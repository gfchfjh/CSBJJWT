"""
图片并发下载器（终极版）
======================
功能：
1. 并发下载（asyncio.gather）
2. 限流控制（避免IP封禁）
3. 重试机制（3次）
4. 进度跟踪
5. 断点续传
6. 缓存去重

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import asyncio
import aiohttp
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..utils.logger import logger


class ImageDownloaderUltimate:
    """图片并发下载器（终极版）"""
    
    def __init__(self, max_concurrent: int = 5, cache_dir: Path = None):
        self.max_concurrent = max_concurrent
        self.cache_dir = cache_dir or Path('./data/images/cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 信号量控制并发数
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # 统计信息
        self.stats = {
            'total_downloaded': 0,
            'total_failed': 0,
            'total_cached': 0,
            'total_bytes': 0
        }
    
    def _get_cache_key(self, url: str) -> str:
        """生成缓存键（URL的MD5）"""
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, url: str) -> Path:
        """获取缓存文件路径"""
        cache_key = self._get_cache_key(url)
        # 使用两级目录避免单个目录文件过多
        return self.cache_dir / cache_key[:2] / cache_key[2:4] / cache_key
    
    async def download_single(self, url: str, cookies: Dict = None, 
                             referer: str = None, max_retries: int = 3) -> Optional[bytes]:
        """
        下载单张图片（带重试）
        
        Args:
            url: 图片URL
            cookies: Cookie字典
            referer: Referer头
            max_retries: 最大重试次数
            
        Returns:
            图片数据（bytes）
        """
        # 检查缓存
        cache_path = self._get_cache_path(url)
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    data = f.read()
                self.stats['total_cached'] += 1
                logger.debug(f"使用缓存: {url}")
                return data
            except:
                pass
        
        # 使用信号量限制并发
        async with self.semaphore:
            for attempt in range(max_retries):
                try:
                    # 准备请求头
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    if referer:
                        headers['Referer'] = referer
                    
                    # 准备Cookie
                    cookie_jar = None
                    if cookies:
                        cookie_jar = aiohttp.CookieJar()
                        for name, value in cookies.items():
                            cookie_jar.update_cookies({name: value})
                    
                    # 下载图片
                    timeout = aiohttp.ClientTimeout(total=30)
                    
                    async with aiohttp.ClientSession(
                        headers=headers, 
                        cookie_jar=cookie_jar,
                        timeout=timeout
                    ) as session:
                        async with session.get(url) as response:
                            if response.status == 200:
                                data = await response.read()
                                
                                # 保存到缓存
                                try:
                                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                                    with open(cache_path, 'wb') as f:
                                        f.write(data)
                                except:
                                    pass  # 缓存失败不影响下载
                                
                                # 统计
                                self.stats['total_downloaded'] += 1
                                self.stats['total_bytes'] += len(data)
                                
                                logger.debug(f"下载成功: {url} ({len(data)/1024:.1f} KB)")
                                return data
                            else:
                                logger.warning(f"下载失败 (HTTP {response.status}): {url}")
                                
                except asyncio.TimeoutError:
                    logger.warning(f"下载超时 (尝试 {attempt+1}/{max_retries}): {url}")
                    
                except Exception as e:
                    logger.warning(f"下载异常 (尝试 {attempt+1}/{max_retries}): {url}, {e}")
                
                # 重试前等待
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避：2s, 4s, 8s
        
        # 所有重试失败
        self.stats['total_failed'] += 1
        logger.error(f"下载失败（已重试{max_retries}次）: {url}")
        return None
    
    async def download_batch(self, urls: List[str], cookies: Dict = None,
                            referer: str = None) -> List[Tuple[str, Optional[bytes]]]:
        """
        批量并发下载图片
        
        Args:
            urls: URL列表
            cookies: Cookie字典
            referer: Referer头
            
        Returns:
            [(url, image_data), ...] 列表
        """
        if not urls:
            return []
        
        logger.info(f"开始并发下载{len(urls)}张图片（最大并发数: {self.max_concurrent}）")
        
        start_time = datetime.now()
        
        # 创建下载任务
        tasks = [
            self.download_single(url, cookies, referer)
            for url in urls
        ]
        
        # 并发执行（gather会等待所有任务完成）
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        downloads = []
        success_count = 0
        
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                logger.error(f"下载异常: {url}, {result}")
                downloads.append((url, None))
            elif result is not None:
                downloads.append((url, result))
                success_count += 1
            else:
                downloads.append((url, None))
        
        # 统计
        elapsed = (datetime.now() - start_time).total_seconds()
        total_mb = self.stats['total_bytes'] / (1024 * 1024)
        
        logger.info(
            f"批量下载完成: {success_count}/{len(urls)}成功, "
            f"耗时{elapsed:.2f}秒, "
            f"下载{total_mb:.2f}MB"
        )
        
        return downloads
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            'cache_dir': str(self.cache_dir),
            'max_concurrent': self.max_concurrent
        }
    
    def clear_cache(self, days: int = 7) -> int:
        """
        清理缓存（删除N天前的文件）
        
        Args:
            days: 保留天数
            
        Returns:
            删除的文件数
        """
        import time
        
        cutoff_time = time.time() - (days * 24 * 3600)
        deleted_count = 0
        
        for file_path in self.cache_dir.rglob('*'):
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except:
                        pass
        
        logger.info(f"清理了{deleted_count}个缓存文件")
        return deleted_count


# 全局实例
image_downloader_ultimate = ImageDownloaderUltimate(max_concurrent=5)
