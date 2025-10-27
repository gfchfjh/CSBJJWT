"""
图片处理模块 v2.0 - 性能优化版
版本: v6.0.0
作者: KOOK Forwarder Team

性能优化:
1. 多进程处理池（处理大图片）
2. 智能格式转换（HEIC/WebP/AVIF → JPG）
3. 自适应压缩策略
4. LRU Token缓存（替代周期清理）
5. 异步下载优化

目标性能:
- <500KB: <200ms
- 500KB-2MB: <500ms
- 2MB-5MB: <1s
- >5MB: <2s
"""

import os
import asyncio
import aiohttp
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing
from functools import lru_cache
from collections import OrderedDict
from threading import Lock
from ..config import settings
from ..utils.logger import logger


class LRUTokenCache:
    """LRU Token缓存（替代周期清理，性能更优）"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 7200):
        """
        初始化LRU缓存
        
        Args:
            max_size: 最大缓存数量
            ttl: Token有效期（秒）
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.lock = Lock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0
        }
    
    def get(self, key: str) -> Optional[Dict]:
        """获取Token（自动检查过期）"""
        with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            # 检查是否过期
            token_data = self.cache[key]
            if time.time() > token_data['expire_at']:
                # 已过期，删除
                del self.cache[key]
                self.stats['expirations'] += 1
                self.stats['misses'] += 1
                return None
            
            # 命中，移到末尾（LRU）
            self.cache.move_to_end(key)
            self.stats['hits'] += 1
            return token_data
    
    def set(self, key: str, token: str):
        """设置Token"""
        with self.lock:
            # 检查是否需要淘汰
            if len(self.cache) >= self.max_size:
                # 删除最久未使用的
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
            
            # 添加新Token
            self.cache[key] = {
                'token': token,
                'expire_at': time.time() + self.ttl,
                'created_at': time.time()
            }
            
            # 移到末尾
            self.cache.move_to_end(key)
    
    def remove(self, key: str):
        """删除Token"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear_expired(self) -> int:
        """清理过期Token（可选，手动调用）"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, data in self.cache.items()
                if current_time > data['expire_at']
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            self.stats['expirations'] += len(expired_keys)
            return len(expired_keys)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                **self.stats,
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': f"{hit_rate:.2%}",
                'fill_rate': f"{len(self.cache) / self.max_size:.2%}"
            }


class ImageProcessorV2:
    """
    图片处理器 v2.0 - 性能优化版
    
    优化点:
    1. 多进程处理大图片（>2MB）
    2. 线程池处理小图片（<2MB）
    3. 智能格式转换
    4. LRU Token缓存
    5. 异步下载优化
    """
    
    def __init__(self):
        # 图片存储目录
        self.storage_path = Path(settings.data_dir) / "images"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # LRU Token缓存（替代dict + 周期清理）
        self.token_cache = LRUTokenCache(max_size=1000, ttl=7200)
        
        # 多进程池（处理大图片，CPU密集型）
        max_workers = max(1, multiprocessing.cpu_count() - 1)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
        logger.info(f"✅ 图片处理多进程池：{max_workers}个进程")
        
        # 线程池（处理小图片和I/O）
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers * 2)
        logger.info(f"✅ 图片处理线程池：{max_workers * 2}个线程")
        
        # 统计信息
        self.stats = {
            'total_processed': 0,
            'total_downloads': 0,
            'total_compressed_mb': 0.0,
            'total_saved_mb': 0.0,
            'process_pool_used': 0,
            'thread_pool_used': 0,
            'format_conversions': 0,
            'avg_process_time_ms': 0.0
        }
        
        # 支持的输入格式
        self.supported_input_formats = {
            'JPEG', 'JPG', 'PNG', 'GIF', 'BMP', 'TIFF', 'WEBP',
            'HEIC', 'HEIF', 'AVIF', 'ICO'
        }
        
        # 平台推荐输出格式
        self.platform_formats = {
            'discord': 'WEBP',   # Discord支持WebP，体积小
            'telegram': 'JPEG',  # Telegram推荐JPEG
            'feishu': 'JPEG'     # 飞书推荐JPEG
        }
    
    async def download_image(self, url: str, 
                            cookies: Optional[Dict] = None,
                            referer: Optional[str] = None,
                            timeout: int = 30) -> Optional[bytes]:
        """
        下载图片（优化版，支持重试和防盗链）
        
        Args:
            url: 图片URL
            cookies: Cookie字典
            referer: Referer头
            timeout: 超时时间（秒）
            
        Returns:
            图片二进制数据，失败返回None
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
                
                if referer:
                    headers['Referer'] = referer
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url, 
                        headers=headers, 
                        cookies=cookies,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.read()
                            size_mb = len(data) / (1024 * 1024)
                            logger.info(f"✅ 图片下载成功: {url[:50]}... (大小: {size_mb:.2f}MB, 尝试: {attempt + 1}/{max_retries})")
                            
                            self.stats['total_downloads'] += 1
                            return data
                        else:
                            logger.warning(f"图片下载失败: HTTP {response.status} (尝试: {attempt + 1}/{max_retries})")
                            
            except asyncio.TimeoutError:
                logger.warning(f"图片下载超时: {url[:50]}... (尝试: {attempt + 1}/{max_retries})")
            except Exception as e:
                logger.error(f"图片下载异常: {str(e)} (尝试: {attempt + 1}/{max_retries})")
            
            # 重试前等待
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避: 1s, 2s, 4s
        
        logger.error(f"图片下载最终失败（{max_retries}次尝试）: {url[:50]}...")
        return None
    
    @staticmethod
    def _detect_format(image_data: bytes) -> Optional[str]:
        """
        检测图片格式（通过魔术字节）
        
        Args:
            image_data: 图片二进制数据
            
        Returns:
            格式名称（JPEG/PNG/WEBP/HEIC等）或None
        """
        if not image_data or len(image_data) < 12:
            return None
        
        # 检查魔术字节
        magic_bytes = image_data[:12]
        
        # JPEG
        if magic_bytes[:3] == b'\xff\xd8\xff':
            return 'JPEG'
        
        # PNG
        if magic_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            return 'PNG'
        
        # GIF
        if magic_bytes[:6] in (b'GIF87a', b'GIF89a'):
            return 'GIF'
        
        # WEBP
        if magic_bytes[:4] == b'RIFF' and magic_bytes[8:12] == b'WEBP':
            return 'WEBP'
        
        # BMP
        if magic_bytes[:2] == b'BM':
            return 'BMP'
        
        # HEIC/HEIF
        if b'ftyp' in magic_bytes and (b'heic' in magic_bytes or b'heif' in magic_bytes):
            return 'HEIC'
        
        # AVIF
        if b'ftyp' in magic_bytes and b'avif' in magic_bytes:
            return 'AVIF'
        
        return None
    
    @staticmethod
    def _compress_image_worker(image_data: bytes, 
                                max_size_mb: float = 10.0,
                                quality: int = 85,
                                target_format: str = 'JPEG') -> Tuple[bytes, Dict]:
        """
        静态压缩方法（用于多进程）
        
        Args:
            image_data: 原始图片数据
            max_size_mb: 最大大小（MB）
            quality: 压缩质量（1-100）
            target_format: 目标格式
            
        Returns:
            (压缩后的图片数据, 统计信息)
        """
        start_time = time.time()
        stats = {
            'original_size_mb': len(image_data) / (1024 * 1024),
            'original_format': None,
            'target_format': target_format,
            'compressed_size_mb': 0,
            'compression_ratio': 0,
            'format_converted': False,
            'resized': False,
            'process_time_ms': 0
        }
        
        try:
            # 检查原始大小
            original_size_mb = len(image_data) / (1024 * 1024)
            
            # 如果已经足够小，直接返回
            if original_size_mb <= max_size_mb and target_format == 'JPEG':
                # 仍然打开验证是否有效
                try:
                    img = Image.open(BytesIO(image_data))
                    stats['original_format'] = img.format
                    img.verify()
                    
                    stats['compressed_size_mb'] = original_size_mb
                    stats['compression_ratio'] = 1.0
                    stats['process_time_ms'] = (time.time() - start_time) * 1000
                    
                    return image_data, stats
                except:
                    pass  # 无效图片，继续处理
            
            # 打开图片
            img = Image.open(BytesIO(image_data))
            original_format = img.format
            original_size = img.size
            stats['original_format'] = original_format
            
            # 策略1：格式转换
            # HEIC/HEIF/AVIF/PNG → JPEG（如果需要）
            should_convert_format = False
            if target_format and original_format != target_format:
                if original_format in ('HEIC', 'HEIF', 'AVIF'):
                    # 现代格式转换为通用格式
                    should_convert_format = True
                    stats['format_converted'] = True
                elif original_format == 'PNG' and target_format == 'JPEG' and original_size_mb > 2.0:
                    # 大PNG转JPEG可显著减小
                    should_convert_format = True
                    stats['format_converted'] = True
            
            # 策略2：缩小分辨率（超大图片）
            should_resize = False
            max_dimension = 4096  # 最大边长
            new_size = original_size
            
            if max(original_size) > max_dimension:
                should_resize = True
                ratio = max_dimension / max(original_size)
                new_size = tuple(int(dim * ratio) for dim in original_size)
                stats['resized'] = True
            
            # 应用转换
            if should_convert_format or should_resize or original_size_mb > max_size_mb:
                # 处理透明通道（转JPEG时）
                if target_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
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
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 保存为目标格式
                output = BytesIO()
                
                if target_format == 'JPEG':
                    img.save(output, format='JPEG', quality=quality, optimize=True, progressive=True)
                elif target_format == 'WEBP':
                    img.save(output, format='WEBP', quality=quality, method=6)
                elif target_format == 'PNG':
                    img.save(output, format='PNG', optimize=True, compress_level=9)
                else:
                    img.save(output, format=target_format, optimize=True)
                
                compressed_data = output.getvalue()
                compressed_size_mb = len(compressed_data) / (1024 * 1024)
                
                # 如果仍然太大且质量足够高，递归降低质量
                if compressed_size_mb > max_size_mb and quality > 60:
                    logger.debug(f"图片仍然过大({compressed_size_mb:.2f}MB)，降低质量重试...")
                    return ImageProcessorV2._compress_image_worker(
                        compressed_data, max_size_mb, quality - 10, target_format
                    )
                
                # 统计
                stats['compressed_size_mb'] = compressed_size_mb
                stats['compression_ratio'] = compressed_size_mb / original_size_mb if original_size_mb > 0 else 1.0
                stats['process_time_ms'] = (time.time() - start_time) * 1000
                
                return compressed_data, stats
            else:
                # 不需要处理，返回原图
                stats['compressed_size_mb'] = original_size_mb
                stats['compression_ratio'] = 1.0
                stats['process_time_ms'] = (time.time() - start_time) * 1000
                
                return image_data, stats
            
        except Exception as e:
            logger.error(f"图片压缩失败: {str(e)}")
            stats['error'] = str(e)
            stats['process_time_ms'] = (time.time() - start_time) * 1000
            # 压缩失败，返回原图
            return image_data, stats
    
    async def compress_image(self, image_data: bytes, 
                            max_size_mb: float = None,
                            quality: int = None,
                            target_platform: str = 'discord') -> Tuple[bytes, Dict]:
        """
        压缩图片（智能选择多进程或线程）
        
        Args:
            image_data: 原始图片数据
            max_size_mb: 最大大小（MB）
            quality: 压缩质量（1-100）
            target_platform: 目标平台
            
        Returns:
            (压缩后的图片数据, 统计信息)
        """
        if max_size_mb is None:
            max_size_mb = settings.image_max_size_mb
        if quality is None:
            quality = settings.image_compression_quality
        
        # 确定目标格式
        target_format = self.platform_formats.get(target_platform, 'JPEG')
        
        # 原始大小
        size_mb = len(image_data) / (1024 * 1024)
        
        # 智能选择处理方式
        if size_mb > 2.0:
            # 大图片：使用多进程（CPU密集型）
            logger.debug(f"使用多进程处理大图片({size_mb:.2f}MB)...")
            self.stats['process_pool_used'] += 1
            
            loop = asyncio.get_event_loop()
            compressed_data, compress_stats = await loop.run_in_executor(
                self.process_pool,
                self._compress_image_worker,
                image_data,
                max_size_mb,
                quality,
                target_format
            )
        else:
            # 小图片：使用线程池（I/O密集型）
            logger.debug(f"使用线程池处理小图片({size_mb:.2f}MB)...")
            self.stats['thread_pool_used'] += 1
            
            loop = asyncio.get_event_loop()
            compressed_data, compress_stats = await loop.run_in_executor(
                self.thread_pool,
                self._compress_image_worker,
                image_data,
                max_size_mb,
                quality,
                target_format
            )
        
        # 更新统计
        self.stats['total_processed'] += 1
        self.stats['total_compressed_mb'] += compress_stats['compressed_size_mb']
        self.stats['total_saved_mb'] += (compress_stats['original_size_mb'] - compress_stats['compressed_size_mb'])
        
        if compress_stats.get('format_converted'):
            self.stats['format_conversions'] += 1
        
        # 更新平均处理时间
        total_time = self.stats.get('total_process_time_ms', 0) + compress_stats['process_time_ms']
        self.stats['total_process_time_ms'] = total_time
        self.stats['avg_process_time_ms'] = total_time / self.stats['total_processed']
        
        logger.debug(f"图片处理完成: {compress_stats['process_time_ms']:.0f}ms, "
                    f"压缩率: {compress_stats['compression_ratio']:.2%}")
        
        return compressed_data, compress_stats
    
    async def save_image(self, image_data: bytes, 
                        original_filename: Optional[str] = None) -> Tuple[str, str]:
        """
        保存图片到本地并生成Token URL
        
        Args:
            image_data: 图片数据
            original_filename: 原始文件名
            
        Returns:
            (本地文件路径, Token URL)
        """
        # 生成文件名（使用SHA256哈希）
        file_hash = hashlib.sha256(image_data).hexdigest()
        
        # 检测格式
        detected_format = self._detect_format(image_data)
        file_ext = detected_format.lower() if detected_format else 'jpg'
        
        filename = f"{file_hash}.{file_ext}"
        filepath = self.storage_path / filename
        
        # 保存文件（如果不存在）
        if not filepath.exists():
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(image_data)
            logger.debug(f"图片已保存: {filepath}")
        else:
            logger.debug(f"图片已存在: {filepath}")
        
        # 生成Token
        token = self._generate_token(str(filepath))
        
        # 缓存Token（LRU缓存，自动过期）
        self.token_cache.set(str(filepath), token)
        
        # 生成URL
        url = f"http://127.0.0.1:{settings.image_server_port}/images/{filename}?token={token}"
        
        return str(filepath), url
    
    def _generate_token(self, filepath: str) -> str:
        """生成访问Token"""
        import secrets
        timestamp = str(int(time.time()))
        random_str = secrets.token_urlsafe(16)
        data = f"{filepath}:{timestamp}:{random_str}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def verify_token(self, filepath: str, token: str) -> bool:
        """
        验证Token（使用LRU缓存）
        
        Args:
            filepath: 文件路径
            token: Token字符串
            
        Returns:
            是否有效
        """
        cached_token_data = self.token_cache.get(filepath)
        
        if cached_token_data:
            return cached_token_data['token'] == token
        
        return False
    
    def get_stats(self) -> Dict:
        """获取处理统计"""
        cache_stats = self.token_cache.get_stats()
        
        return {
            **self.stats,
            'token_cache': cache_stats
        }
    
    def cleanup(self):
        """清理资源"""
        logger.info("关闭图片处理器...")
        
        # 关闭进程池
        self.process_pool.shutdown(wait=False)
        
        # 关闭线程池
        self.thread_pool.shutdown(wait=False)
        
        logger.info("✅ 图片处理器已关闭")


# 需要导入aiofiles
try:
    import aiofiles
except ImportError:
    logger.warning("⚠️  aiofiles未安装，文件操作将使用同步方式")
    # 提供同步fallback
    import aiofiles
    class aiofiles:
        @staticmethod
        def open(path, mode):
            return open(path, mode)


# 全局实例
image_processor_v2 = ImageProcessorV2()
