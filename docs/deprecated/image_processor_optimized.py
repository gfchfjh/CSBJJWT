"""
图片处理优化模块
优化项：
1. 并发下载（aiohttp批量下载）
2. WebP格式支持（体积减少30-50%）
3. 多进程压缩（利用多核CPU）
4. 智能缓存（相同URL不重复下载）
"""
import asyncio
import aiohttp
from typing import List, Dict, Optional
from pathlib import Path
import hashlib
import time
from concurrent.futures import ProcessPoolExecutor
from PIL import Image
import io
from ..utils.logger import logger


class ImageProcessorOptimized:
    """优化的图片处理器"""
    
    def __init__(self):
        self.cache_dir = Path.home() / 'KookForwarder' / 'data' / 'image_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 图片缓存（内存缓存，避免重复下载）
        self.url_cache = {}  # {url_hash: local_path}
        
        # 进程池（用于CPU密集型的图片压缩）
        self.process_pool = ProcessPoolExecutor(max_workers=4)
        
        # 统计信息
        self.stats = {
            'downloads': 0,
            'cache_hits': 0,
            'compressions': 0,
            'webp_conversions': 0,
            'total_saved_bytes': 0
        }
    
    async def download_images_concurrent(self, urls: List[str], 
                                        cookies: Optional[Dict] = None,
                                        max_concurrent: int = 10) -> List[Dict]:
        """
        并发下载多个图片
        
        Args:
            urls: 图片URL列表
            cookies: Cookie字典（用于防盗链）
            max_concurrent: 最大并发数
            
        Returns:
            [
                {
                    'url': 'https://...',
                    'local_path': '/path/to/image.jpg',
                    'size': 12345,
                    'format': 'JPEG',
                    'cached': False
                },
                ...
            ]
        """
        if not urls:
            return []
        
        logger.info(f"开始并发下载 {len(urls)} 张图片...")
        start_time = time.time()
        
        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_one(url):
            async with semaphore:
                return await self._download_single_image(url, cookies)
        
        # 并发下载所有图片
        results = await asyncio.gather(*[download_one(url) for url in urls], 
                                       return_exceptions=True)
        
        # 处理结果
        successful_downloads = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"下载失败: {str(result)}")
            elif result:
                successful_downloads.append(result)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ 完成下载 {len(successful_downloads)}/{len(urls)} 张图片，耗时 {elapsed:.2f}秒")
        
        return successful_downloads
    
    async def _download_single_image(self, url: str, 
                                     cookies: Optional[Dict] = None) -> Optional[Dict]:
        """下载单张图片"""
        try:
            # 检查缓存
            url_hash = hashlib.md5(url.encode()).hexdigest()
            
            if url_hash in self.url_cache:
                cached_path = self.url_cache[url_hash]
                if Path(cached_path).exists():
                    self.stats['cache_hits'] += 1
                    logger.debug(f"使用缓存: {url}")
                    
                    return {
                        'url': url,
                        'local_path': cached_path,
                        'size': Path(cached_path).stat().st_size,
                        'format': self._get_image_format(cached_path),
                        'cached': True
                    }
            
            # 下载图片
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.kookapp.cn/'
            }
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers, cookies=cookies) as resp:
                    if resp.status != 200:
                        logger.error(f"下载失败: HTTP {resp.status}")
                        return None
                    
                    content = await resp.read()
                    
                    # 保存到缓存目录
                    ext = self._guess_extension_from_content(content)
                    local_path = self.cache_dir / f"{url_hash}{ext}"
                    
                    local_path.write_bytes(content)
                    
                    # 更新缓存
                    self.url_cache[url_hash] = str(local_path)
                    self.stats['downloads'] += 1
                    
                    logger.debug(f"下载成功: {url} -> {local_path}")
                    
                    return {
                        'url': url,
                        'local_path': str(local_path),
                        'size': len(content),
                        'format': self._get_image_format(str(local_path)),
                        'cached': False
                    }
                    
        except Exception as e:
            logger.error(f"下载图片失败 {url}: {str(e)}")
            return None
    
    async def compress_images_concurrent(self, image_paths: List[str],
                                        max_size_kb: int = 5120,
                                        quality: int = 85,
                                        use_webp: bool = True) -> List[Dict]:
        """
        并发压缩多张图片
        
        Args:
            image_paths: 图片路径列表
            max_size_kb: 最大文件大小（KB）
            quality: 压缩质量 (1-100)
            use_webp: 是否转换为WebP格式（体积减少30-50%）
            
        Returns:
            [
                {
                    'original_path': '/path/to/original.jpg',
                    'compressed_path': '/path/to/compressed.webp',
                    'original_size': 1024000,
                    'compressed_size': 512000,
                    'compression_ratio': 0.5
                },
                ...
            ]
        """
        if not image_paths:
            return []
        
        logger.info(f"开始并发压缩 {len(image_paths)} 张图片...")
        start_time = time.time()
        
        # 使用进程池并发压缩（CPU密集型任务）
        loop = asyncio.get_event_loop()
        
        tasks = [
            loop.run_in_executor(
                self.process_pool,
                self._compress_single_image,
                path, max_size_kb, quality, use_webp
            )
            for path in image_paths
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        successful_compressions = []
        total_saved = 0
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"压缩失败: {str(result)}")
            elif result:
                successful_compressions.append(result)
                total_saved += result['original_size'] - result['compressed_size']
        
        self.stats['compressions'] += len(successful_compressions)
        self.stats['total_saved_bytes'] += total_saved
        
        elapsed = time.time() - start_time
        logger.info(f"✅ 完成压缩 {len(successful_compressions)}/{len(image_paths)} 张图片，"
                   f"节省 {total_saved / 1024:.1f}KB，耗时 {elapsed:.2f}秒")
        
        return successful_compressions
    
    @staticmethod
    def _compress_single_image(image_path: str, max_size_kb: int, 
                               quality: int, use_webp: bool) -> Optional[Dict]:
        """
        压缩单张图片（在独立进程中执行）
        
        注意：此方法在子进程中运行，不能使用logger等非pickle对象
        """
        try:
            from PIL import Image
            import os
            
            original_path = Path(image_path)
            original_size = original_path.stat().st_size
            
            # 打开图片
            with Image.open(original_path) as img:
                # 转换RGBA为RGB（WebP需要）
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 确定输出格式和路径
                if use_webp:
                    ext = '.webp'
                    save_format = 'WEBP'
                else:
                    ext = '.jpg'
                    save_format = 'JPEG'
                
                compressed_path = original_path.with_suffix(ext)
                
                # 如果原图已经很小，直接保存
                if original_size <= max_size_kb * 1024:
                    img.save(compressed_path, format=save_format, 
                            quality=quality, optimize=True)
                else:
                    # 需要压缩：先缩小尺寸，再调整质量
                    current_quality = quality
                    current_img = img.copy()
                    
                    # 最多尝试5次
                    for attempt in range(5):
                        # 保存到内存
                        buffer = io.BytesIO()
                        current_img.save(buffer, format=save_format, 
                                       quality=current_quality, optimize=True)
                        size = len(buffer.getvalue())
                        
                        if size <= max_size_kb * 1024 or current_quality <= 50:
                            # 满足要求，保存到文件
                            with open(compressed_path, 'wb') as f:
                                f.write(buffer.getvalue())
                            break
                        
                        # 降低质量继续尝试
                        current_quality -= 10
                        
                        # 如果质量已经很低，尝试缩小尺寸
                        if current_quality < 60 and attempt == 2:
                            new_size = (int(current_img.width * 0.8), 
                                      int(current_img.height * 0.8))
                            current_img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                compressed_size = compressed_path.stat().st_size
                
                return {
                    'original_path': str(original_path),
                    'compressed_path': str(compressed_path),
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': compressed_size / original_size,
                    'format': save_format
                }
                
        except Exception as e:
            # 在子进程中无法使用logger，打印到控制台
            print(f"压缩图片失败 {image_path}: {str(e)}")
            return None
    
    def _guess_extension_from_content(self, content: bytes) -> str:
        """从文件内容猜测扩展名"""
        # 检查文件头
        if content[:2] == b'\xff\xd8':
            return '.jpg'
        elif content[:8] == b'\x89PNG\r\n\x1a\n':
            return '.png'
        elif content[:6] in [b'GIF87a', b'GIF89a']:
            return '.gif'
        elif content[:4] == b'RIFF' and content[8:12] == b'WEBP':
            return '.webp'
        else:
            return '.jpg'  # 默认
    
    def _get_image_format(self, path: str) -> str:
        """获取图片格式"""
        try:
            with Image.open(path) as img:
                return img.format
        except:
            return 'UNKNOWN'
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'cache_size': len(self.url_cache),
            'cache_dir_size_mb': sum(f.stat().st_size for f in self.cache_dir.glob('*')) / (1024 * 1024)
        }
    
    def clear_cache(self):
        """清空缓存"""
        for file in self.cache_dir.glob('*'):
            try:
                file.unlink()
            except Exception as e:
                logger.error(f"删除缓存文件失败 {file}: {str(e)}")
        
        self.url_cache.clear()
        logger.info("✅ 图片缓存已清空")
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'process_pool'):
            self.process_pool.shutdown(wait=False)


# 创建全局实例
image_processor_optimized = ImageProcessorOptimized()
