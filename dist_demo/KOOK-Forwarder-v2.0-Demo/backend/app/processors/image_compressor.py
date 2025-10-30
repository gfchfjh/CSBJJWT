"""
图片压缩模块
从image.py拆分出来，专注于图片压缩逻辑
"""
from PIL import Image
from io import BytesIO
from typing import Tuple
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from ..utils.structured_logger import logger


class ImageCompressor:
    """
    图片压缩器
    
    使用多进程池提升性能，支持智能压缩策略
    """
    
    def __init__(self):
        # 多进程池（CPU核心数-1，至少1个）
        max_workers = max(1, multiprocessing.cpu_count() - 1)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
        logger.info(f"✅ 图片压缩多进程池已启动：{max_workers}个进程")
        
        # 统计信息
        self.stats = {
            'total_processed': 0,
            'total_compressed_mb': 0,
            'total_saved_mb': 0
        }
    
    @staticmethod
    def compress_worker(
        image_data: bytes,
        max_size_mb: float = 10.0,
        quality: int = 85
    ) -> bytes:
        """
        静态压缩方法（用于多进程）
        
        优化策略：
        1. PNG大图自动转JPEG（减少30-50%体积）
        2. 保留小图原格式（避免不必要的损失）
        3. 超大图片自动缩小分辨率
        4. 迭代降低质量直到满足大小要求
        
        Args:
            image_data: 原始图片数据
            max_size_mb: 最大大小（MB）
            quality: 压缩质量（1-100）
            
        Returns:
            压缩后的图片数据
        """
        try:
            # 检查大小
            size_mb = len(image_data) / (1024 * 1024)
            if size_mb <= max_size_mb:
                return image_data
            
            # 打开图片
            img = Image.open(BytesIO(image_data))
            original_format = img.format
            
            # 策略1：PNG大图转JPEG
            should_convert_to_jpeg = (original_format == 'PNG' and size_mb > 2.0)
            
            # 策略2：超大图片缩小分辨率
            max_dimension = 4096
            should_resize = max(img.size) > max_dimension
            
            # 应用转换策略
            if should_convert_to_jpeg or should_resize:
                # 处理透明通道
                if should_convert_to_jpeg and img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # 缩小分辨率
                if should_resize:
                    ratio = max_dimension / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 保存为JPEG
                output = BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                compressed_data = output.getvalue()
                
                compressed_size_mb = len(compressed_data) / (1024 * 1024)
                
                # ✅ 改进：使用迭代而非递归
                while compressed_size_mb > max_size_mb and quality > 50:
                    quality -= 15
                    output = BytesIO()
                    img.save(output, format='JPEG', quality=quality, optimize=True)
                    compressed_data = output.getvalue()
                    compressed_size_mb = len(compressed_data) / (1024 * 1024)
                
                return compressed_data
            
            else:
                # 非PNG或小图，使用原格式优化
                output = BytesIO()
                save_format = original_format if original_format in ('JPEG', 'PNG', 'WEBP') else 'JPEG'
                
                if save_format == 'JPEG':
                    img.save(output, format=save_format, quality=quality, optimize=True)
                elif save_format == 'PNG':
                    img.save(output, format=save_format, optimize=True, compress_level=9)
                else:
                    img.save(output, format=save_format, optimize=True)
                
                compressed_data = output.getvalue()
                compressed_size_mb = len(compressed_data) / (1024 * 1024)
                
                # 如果仍然太大，转JPEG重试
                if compressed_size_mb > max_size_mb:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    output = BytesIO()
                    img.save(output, format='JPEG', quality=quality, optimize=True)
                    return output.getvalue()
                
                return compressed_data
            
        except Exception as e:
            # 压缩失败，返回原图
            logger.error(f"压缩失败，返回原图: {str(e)}")
            return image_data
    
    async def compress(
        self,
        image_data: bytes,
        max_size_mb: float = 10.0,
        quality: int = 85
    ) -> bytes:
        """
        异步压缩图片（使用进程池）
        
        Args:
            image_data: 原始图片数据
            max_size_mb: 最大大小（MB）
            quality: 压缩质量（1-100）
            
        Returns:
            压缩后的图片数据
        """
        size_mb = len(image_data) / (1024 * 1024)
        
        if size_mb <= max_size_mb:
            return image_data
        
        logger.info(f"图片过大({size_mb:.2f}MB)，开始智能压缩...")
        
        # 提交到进程池
        loop = asyncio.get_event_loop()
        compressed_data = await loop.run_in_executor(
            self.process_pool,
            self.compress_worker,
            image_data,
            max_size_mb,
            quality
        )
        
        compressed_size_mb = len(compressed_data) / (1024 * 1024)
        reduction = (1 - compressed_size_mb / size_mb) * 100 if size_mb > 0 else 0
        
        logger.info(f"✅ 智能压缩完成: {size_mb:.2f}MB -> {compressed_size_mb:.2f}MB (减少{reduction:.1f}%)")
        
        # 更新统计
        self.stats['total_processed'] += 1
        self.stats['total_compressed_mb'] += compressed_size_mb
        self.stats['total_saved_mb'] += (size_mb - compressed_size_mb)
        
        return compressed_data
    
    def get_stats(self) -> Dict[str, Any]:
        """获取压缩统计信息"""
        avg_compressed_mb = (
            self.stats['total_compressed_mb'] / self.stats['total_processed']
            if self.stats['total_processed'] > 0 else 0
        )
        avg_saved_mb = (
            self.stats['total_saved_mb'] / self.stats['total_processed']
            if self.stats['total_processed'] > 0 else 0
        )
        
        return {
            'total_processed': self.stats['total_processed'],
            'total_compressed_mb': round(self.stats['total_compressed_mb'], 2),
            'total_saved_mb': round(self.stats['total_saved_mb'], 2),
            'avg_compressed_mb': round(avg_compressed_mb, 2),
            'avg_saved_mb': round(avg_saved_mb, 2),
            'process_pool_workers': self.process_pool._max_workers if hasattr(self.process_pool, '_max_workers') else 0
        }
    
    def shutdown(self):
        """关闭进程池"""
        try:
            self.process_pool.shutdown(wait=True)
            logger.info("图片压缩进程池已关闭")
        except Exception as e:
            logger.error(f"关闭进程池失败: {str(e)}")


# 创建全局压缩器实例
compressor = ImageCompressor()
