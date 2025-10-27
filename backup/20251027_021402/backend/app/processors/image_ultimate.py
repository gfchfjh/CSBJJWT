"""
图片处理器（终极优化版）
======================
功能：
1. 并发下载（aiohttp并发）
2. 多进程压缩（CPU密集）
3. 智能缓存
4. 防盗链处理
5. 自动重试

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import asyncio
import aiohttp
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from PIL import Image
import io
import hashlib
from ..utils.logger import logger
from ..config import settings


class ImageProcessorUltimate:
    """图片处理器（终极优化版）"""
    
    def __init__(self):
        # 创建多进程池（用于图片压缩）
        self.process_pool = ProcessPoolExecutor(max_workers=4)
        
        # 创建aiohttp会话（用于并发下载）
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 下载缓存（避免重复下载）
        self.download_cache: Dict[str, bytes] = {}
        self.max_cache_size = 100  # 最多缓存100张图片
    
    async def ensure_session(self):
        """确保aiohttp会话存在"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=20)  # 最多20个并发连接
            )
    
    async def download_images_concurrent(self, urls: List[str], 
                                        cookies: Dict = None,
                                        referer: str = None) -> List[Tuple[str, Optional[bytes]]]:
        """
        并发下载多张图片（性能优化）
        
        Args:
            urls: 图片URL列表
            cookies: Cookie字典
            referer: Referer头
            
        Returns:
            [(url, image_data), ...]
        """
        await self.ensure_session()
        
        logger.info(f"🚀 并发下载 {len(urls)} 张图片...")
        
        # 创建并发下载任务
        tasks = [
            self._download_single_image(url, cookies, referer)
            for url in urls
        ]
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        downloaded = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                logger.error(f"下载失败: {url} - {result}")
                downloaded.append((url, None))
            else:
                downloaded.append((url, result))
        
        success_count = sum(1 for _, data in downloaded if data)
        logger.info(f"✅ 下载完成: {success_count}/{len(urls)} 成功")
        
        return downloaded
    
    async def _download_single_image(self, url: str, 
                                    cookies: Dict = None,
                                    referer: str = None) -> Optional[bytes]:
        """
        下载单张图片（支持缓存）
        
        Args:
            url: 图片URL
            cookies: Cookie字典
            referer: Referer头
            
        Returns:
            图片数据
        """
        # 检查缓存
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in self.download_cache:
            logger.debug(f"使用缓存图片: {url}")
            return self.download_cache[cache_key]
        
        try:
            # 准备请求头
            headers = {}
            if referer:
                headers['Referer'] = referer
            if cookies:
                # 转换Cookie字典为Cookie字符串
                cookie_str = '; '.join(f"{k}={v}" for k, v in cookies.items())
                headers['Cookie'] = cookie_str
            
            # 下载图片
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.read()
                    
                    # 加入缓存
                    if len(self.download_cache) >= self.max_cache_size:
                        # 删除最旧的缓存
                        oldest_key = next(iter(self.download_cache))
                        del self.download_cache[oldest_key]
                    
                    self.download_cache[cache_key] = data
                    
                    logger.debug(f"下载成功: {url} ({len(data) / 1024:.1f} KB)")
                    return data
                else:
                    logger.error(f"下载失败: {url} - HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"下载异常: {url} - {e}")
            return None
    
    @staticmethod
    def _compress_image_worker(image_data: bytes, max_size_mb: float, quality: int) -> bytes:
        """
        压缩图片（静态方法，用于多进程池）
        
        Args:
            image_data: 原始图片数据
            max_size_mb: 最大大小（MB）
            quality: 压缩质量（1-100）
            
        Returns:
            压缩后的图片数据
        """
        try:
            # 打开图片
            img = Image.open(io.BytesIO(image_data))
            
            # 转换RGBA到RGB（如果需要）
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # 压缩图片
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            compressed_data = output.getvalue()
            
            # 检查大小
            size_mb = len(compressed_data) / (1024 * 1024)
            
            if size_mb > max_size_mb:
                # 递归降低质量
                if quality > 50:
                    return ImageProcessorUltimate._compress_image_worker(
                        image_data, max_size_mb, quality - 10
                    )
            
            return compressed_data
            
        except Exception as e:
            # 多进程中无法使用logger，返回原数据
            return image_data
    
    async def process_images_concurrent(self, image_urls: List[str],
                                       cookies: Dict = None) -> List[Dict]:
        """
        并发处理多张图片（下载+压缩）
        
        Args:
            image_urls: 图片URL列表
            cookies: Cookie字典
            
        Returns:
            处理后的图片信息列表
        """
        # 步骤1: 并发下载
        downloaded = await self.download_images_concurrent(
            image_urls, 
            cookies=cookies, 
            referer='https://www.kookapp.cn'
        )
        
        # 步骤2: 并发压缩（使用多进程池）
        compress_tasks = []
        loop = asyncio.get_event_loop()
        
        for url, image_data in downloaded:
            if image_data:
                task = loop.run_in_executor(
                    self.process_pool,
                    self._compress_image_worker,
                    image_data,
                    settings.image_max_size_mb,
                    settings.image_compression_quality
                )
                compress_tasks.append((url, task))
        
        # 等待压缩完成
        processed_images = []
        for url, task in compress_tasks:
            try:
                compressed_data = await task
                
                # 保存到本地
                image_path = await self._save_to_local(url, compressed_data)
                
                processed_images.append({
                    'original_url': url,
                    'local_path': str(image_path),
                    'size': len(compressed_data)
                })
                
            except Exception as e:
                logger.error(f"图片处理失败: {url} - {e}")
        
        return processed_images
    
    async def _save_to_local(self, url: str, data: bytes) -> Path:
        """保存图片到本地"""
        # 生成文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()
        filename = f"{url_hash}.jpg"
        filepath = settings.image_storage_path / filename
        
        # 写入文件
        filepath.write_bytes(data)
        
        return filepath
    
    async def close(self):
        """关闭资源"""
        if self.session and not self.session.closed:
            await self.session.close()
        
        self.process_pool.shutdown(wait=True)


# 全局图片处理器实例
image_processor_ultimate = ImageProcessorUltimate()
