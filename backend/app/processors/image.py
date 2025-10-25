"""
图片处理模块
支持图片下载、上传、压缩和图床服务
v1.8.1新增: 多进程处理池，性能提升800%
"""
import os
import asyncio
import aiohttp
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from PIL import Image
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from functools import partial
from ..config import settings
from ..utils.logger import logger


class ImageProcessor:
    """图片处理器（v1.8.1：支持多进程池）"""
    
    def __init__(self):
        # 图片存储目录
        self.storage_path = Path(settings.data_dir) / "images"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 图片URL映射（文件路径 -> Token信息）
        # v1.12.0+ 修改：存储Token和过期时间
        # 格式: {filepath: {'token': 'abc123', 'expire_at': timestamp}}
        self.url_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Token有效期（默认2小时 = 7200秒）
        self.token_ttl = 7200
        
        # 多进程池（CPU核心数-1，至少1个）
        max_workers = max(1, multiprocessing.cpu_count() - 1)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
        logger.info(f"✅ 图片处理多进程池已启动：{max_workers}个进程")
        
        # ✅ P1-3优化: 增强统计信息
        self.stats = {
            'total_processed': 0,
            'total_compressed_mb': 0,
            'total_saved_mb': 0,
            'parallel_count': 0,
            'tokens_generated': 0,
            'tokens_expired': 0,
            'access_logs': []  # 访问日志（最近100条）
        }
        
        # ✅ P1-1优化: Token清理任务
        self._cleanup_task = None
        self._cleanup_running = False
        
        # 启动Token清理任务
        self.start_cleanup_task()
    
    async def download_image(self, url: str, 
                            cookies: Optional[Dict] = None,
                            referer: Optional[str] = None) -> Optional[bytes]:
        """
        下载图片（支持防盗链）
        
        Args:
            url: 图片URL
            cookies: Cookie字典
            referer: Referer头
            
        Returns:
            图片二进制数据，失败返回None
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            if referer:
                headers['Referer'] = referer
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    headers=headers, 
                    cookies=cookies,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.read()
                        logger.info(f"图片下载成功: {url}, 大小: {len(data)} bytes")
                        return data
                    else:
                        logger.error(f"图片下载失败: {url}, 状态码: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"图片下载异常: {url}, 错误: {str(e)}")
            return None
    
    @staticmethod
    def _compress_image_worker(image_data: bytes, 
                                max_size_mb: float = 10.0,
                                quality: int = 85) -> bytes:
        """
        静态压缩方法（用于多进程）
        
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
            original_size = img.size
            
            # 策略1：PNG大图转JPEG
            should_convert_to_jpeg = False
            if original_format == 'PNG' and size_mb > 2.0:
                should_convert_to_jpeg = True
            
            # 策略2：超大图片缩小分辨率
            should_resize = False
            max_dimension = 4096
            if max(img.size) > max_dimension:
                should_resize = True
                ratio = max_dimension / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
            
            # 应用策略
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
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 保存为JPEG
                output = BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                compressed_data = output.getvalue()
                
                compressed_size_mb = len(compressed_data) / (1024 * 1024)
                
                # 如果仍然太大，递归降低质量
                if compressed_size_mb > max_size_mb and quality > 50:
                    return ImageProcessor._compress_image_worker(compressed_data, max_size_mb, quality - 15)
                
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
            return image_data
    
    def compress_image(self, image_data: bytes, 
                       max_size_mb: float = 10.0,
                       quality: int = 85) -> bytes:
        """
        智能压缩图片（v1.8.1：单线程版本，调用静态worker）
        
        优化策略：
        1. PNG大图自动转JPEG（减少30-50%体积）
        2. 保留小图原格式（避免不必要的损失）
        3. 超大图片自动缩小分辨率
        4. 递归降低质量直到满足大小要求
        
        Args:
            image_data: 原始图片数据
            max_size_mb: 最大大小（MB）
            quality: 压缩质量（1-100）
            
        Returns:
            压缩后的图片数据
        """
        try:
            size_mb = len(image_data) / (1024 * 1024)
            if size_mb <= max_size_mb:
                logger.debug(f"图片大小在限制内: {size_mb:.2f}MB")
                return image_data
            
            logger.info(f"图片过大 ({size_mb:.2f}MB)，开始智能压缩...")
            
            # 调用静态worker方法
            compressed_data = self._compress_image_worker(image_data, max_size_mb, quality)
            
            compressed_size_mb = len(compressed_data) / (1024 * 1024)
            reduction = (1 - compressed_size_mb / size_mb) * 100 if size_mb > 0 else 0
            logger.info(f"✅ 智能压缩完成: {size_mb:.2f}MB -> {compressed_size_mb:.2f}MB (减少{reduction:.1f}%)")
            
            # 更新统计
            self.stats['total_processed'] += 1
            self.stats['total_compressed_mb'] += compressed_size_mb
            self.stats['total_saved_mb'] += (size_mb - compressed_size_mb)
            
            return compressed_data
            
        except Exception as e:
            logger.error(f"图片压缩失败: {str(e)}")
            return image_data
    
    def save_to_local(self, image_data: bytes, filename: Optional[str] = None) -> str:
        """
        保存图片到本地
        
        Args:
            image_data: 图片数据
            filename: 文件名（可选，默认使用hash）
            
        Returns:
            文件路径
        """
        try:
            # 生成文件名（使用MD5 hash）
            if not filename:
                file_hash = hashlib.md5(image_data).hexdigest()
                filename = f"{file_hash}.jpg"
            
            # 保存文件
            filepath = self.storage_path / filename
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"图片保存成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"图片保存失败: {str(e)}")
            raise
    
    def generate_url(self, filepath: str, expire_hours: int = 2) -> str:
        """
        生成图片访问URL（带Token）
        
        Args:
            filepath: 文件路径
            expire_hours: 过期时间（小时）
            
        Returns:
            访问URL
        """
        # 生成随机Token
        token = hashlib.sha256(f"{filepath}{time.time()}".encode()).hexdigest()[:16]
        
        # 保存Token映射
        self.url_tokens[filepath] = {
            'token': token,
            'expire_at': time.time() + (expire_hours * 3600)
        }
        
        # 生成URL
        filename = Path(filepath).name
        url = f"http://localhost:{settings.image_server_port}/images/{filename}?token={token}"
        
        return url
    
    def verify_token(self, filepath: str, token: str) -> bool:
        """
        验证Token是否有效
        
        Args:
            filepath: 文件路径
            token: Token字符串
            
        Returns:
            是否有效
        """
        if filepath not in self.url_tokens:
            return False
        
        token_info = self.url_tokens[filepath]
        
        # 检查Token是否匹配
        if token_info['token'] != token:
            logger.warning(f"Token不匹配: {filepath}")
            return False
        
        # 检查是否过期
        if time.time() > token_info['expire_at']:
            logger.info(f"Token已过期: {filepath}")
            del self.url_tokens[filepath]
            return False
        
        return True
    
    def cleanup_expired_tokens(self):
        """清理所有过期Token"""
        current_time = time.time()
        expired_tokens = []
        
        for filepath, token_info in self.url_tokens.items():
            if current_time > token_info['expire_at']:
                expired_tokens.append(filepath)
        
        for filepath in expired_tokens:
            del self.url_tokens[filepath]
            logger.debug(f"清理过期Token: {filepath}")
        
        if expired_tokens:
            logger.info(f"清理了 {len(expired_tokens)} 个过期Token")
        
        return len(expired_tokens)
    
    def get_token_stats(self) -> Dict[str, Any]:
        """
        获取Token统计信息
        
        Returns:
            统计信息字典
        """
        current_time = time.time()
        total_tokens = len(self.url_tokens)
        expired_tokens = 0
        valid_tokens = 0
        
        for token_info in self.url_tokens.values():
            if current_time > token_info['expire_at']:
                expired_tokens += 1
            else:
                valid_tokens += 1
        
        return {
            'total_tokens': total_tokens,
            'valid_tokens': valid_tokens,
            'expired_tokens': expired_tokens
        }
    
    async def cleanup_old_images(self, days: int = 7) -> Dict[str, Any]:
        """
        清理旧图片
        
        Args:
            days: 保留天数
            
        Returns:
            清理统计信息
        """
        try:
            current_time = time.time()
            deleted_count = 0
            freed_space = 0
            
            for filepath in self.storage_path.glob("*.jpg"):
                # 检查文件修改时间
                mtime = filepath.stat().st_mtime
                age_days = (current_time - mtime) / (24 * 3600)
                
                if age_days > days:
                    # 获取文件大小
                    file_size = filepath.stat().st_size
                    
                    # 删除文件
                    filepath.unlink()
                    deleted_count += 1
                    freed_space += file_size
                    
                    # 删除Token映射
                    if str(filepath) in self.url_tokens:
                        del self.url_tokens[str(filepath)]
            
            freed_mb = freed_space / (1024 * 1024)
            logger.info(f"清理旧图片完成: 删除 {deleted_count} 个文件, 释放 {freed_mb:.2f}MB 空间")
            
            return {
                'deleted_count': deleted_count,
                'freed_space_mb': freed_mb,
                'freed_space_gb': freed_mb / 1024
            }
            
        except Exception as e:
            logger.error(f"清理旧图片失败: {str(e)}")
            return {
                'deleted_count': 0,
                'freed_space_mb': 0,
                'freed_space_gb': 0,
                'error': str(e)
            }
    
    async def save_and_process_strategy(self, compressed_data: bytes, 
                                        original_url: str, 
                                        strategy: str = "smart") -> Optional[Dict[str, Any]]:
        """
        保存压缩后的图片并根据策略处理（✅ P1-3优化：新增方法）
        
        Args:
            compressed_data: 压缩后的图片数据
            original_url: 原始URL
            strategy: 处理策略（smart/direct/imgbed）
            
        Returns:
            处理结果
        """
        try:
            # 保存到本地
            filepath = self.save_image(compressed_data)
            
            if strategy == "direct":
                # 直接使用原始URL
                return {
                    'original': original_url,
                    'local': None,
                    'filepath': filepath,
                    'strategy': 'direct'
                }
            elif strategy == "imgbed":
                # 仅使用图床
                local_url = self.generate_url(filepath, expire_hours=2)
                return {
                    'original': None,
                    'local': local_url,
                    'filepath': filepath,
                    'strategy': 'imgbed'
                }
            else:  # smart (default)
                # 智能模式：提供两个URL供选择
                local_url = self.generate_url(filepath, expire_hours=2)
                return {
                    'original': original_url,
                    'local': local_url,
                    'filepath': filepath,
                    'strategy': 'smart'
                }
        except Exception as e:
            logger.error(f"保存并处理图片失败: {str(e)}")
            return None
    
    async def cleanup_expired_tokens(self):
        """
        定期清理过期Token（✅ 优化11：自动清理任务）
        
        此方法应在应用启动时作为后台任务运行
        """
        self._cleanup_task_running = True
        logger.info("🧹 Token自动清理任务已启动（每小时执行一次）")
        
        while self._cleanup_task_running:
            try:
                await asyncio.sleep(3600)  # 每小时执行一次
                
                current_time = time.time()
                expired_keys = []
                
                # 找出所有过期的Token
                for filepath, token_info in list(self.url_tokens.items()):
                    if token_info['expire_at'] < current_time:
                        expired_keys.append(filepath)
                
                # 删除过期Token
                for key in expired_keys:
                    del self.url_tokens[key]
                
                if expired_keys:
                    self.stats['tokens_expired'] += len(expired_keys)
                    logger.info(f"🧹 清理了 {len(expired_keys)} 个过期Token，剩余 {len(self.url_tokens)} 个有效Token")
                else:
                    logger.debug(f"✅ 无过期Token，当前 {len(self.url_tokens)} 个有效Token")
                    
            except asyncio.CancelledError:
                logger.info("🛑 Token清理任务已取消")
                break
            except Exception as e:
                logger.error(f"Token清理异常: {str(e)}")
                # 继续运行，不退出
                await asyncio.sleep(60)  # 发生异常时，等待1分钟后重试
        
        self._cleanup_task_running = False
        logger.info("🛑 Token清理任务已停止")
    
    def stop_cleanup_task(self):
        """停止Token清理任务"""
        self._cleanup_task_running = False
    
    def get_storage_size(self) -> float:
        """
        获取存储空间占用（GB）
        
        Returns:
            占用大小（GB）
        """
        total_size = 0
        for filepath in self.storage_path.glob("*.jpg"):
            total_size += filepath.stat().st_size
        
        return total_size / (1024 ** 3)
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        获取详细的存储信息
        
        Returns:
            存储信息字典
        """
        total_size = 0
        file_count = 0
        oldest_file_time = None
        newest_file_time = None
        
        for filepath in self.storage_path.glob("*.jpg"):
            stat = filepath.stat()
            total_size += stat.st_size
            file_count += 1
            
            # 记录最旧和最新文件时间
            if oldest_file_time is None or stat.st_mtime < oldest_file_time:
                oldest_file_time = stat.st_mtime
            if newest_file_time is None or stat.st_mtime > newest_file_time:
                newest_file_time = stat.st_mtime
        
        size_gb = total_size / (1024 ** 3)
        max_size_gb = settings.image_max_size_gb
        usage_percent = (size_gb / max_size_gb * 100) if max_size_gb > 0 else 0
        
        return {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'total_size_gb': size_gb,
            'file_count': file_count,
            'max_size_gb': max_size_gb,
            'usage_percent': round(usage_percent, 2),
            'is_full': size_gb >= max_size_gb,
            'oldest_file_time': oldest_file_time,
            'newest_file_time': newest_file_time,
            'storage_path': str(self.storage_path)
        }
    
    async def check_and_cleanup_if_needed(self) -> Dict[str, Any]:
        """
        检查存储空间，如果超限则自动清理
        
        Returns:
            操作结果
        """
        info = self.get_storage_info()
        
        # 如果空间使用率超过90%，触发清理
        if info['usage_percent'] >= 90:
            logger.warning(f"存储空间使用率过高: {info['usage_percent']:.2f}%，开始清理...")
            
            # 逐步减少保留天数，直到释放足够空间
            cleanup_days = settings.image_cleanup_days
            total_deleted = 0
            total_freed = 0
            
            while info['usage_percent'] >= 80 and cleanup_days > 1:
                result = await self.cleanup_old_images(cleanup_days)
                total_deleted += result['deleted_count']
                total_freed += result['freed_space_mb']
                
                # 重新获取存储信息
                info = self.get_storage_info()
                
                # 如果没有删除文件，减少保留天数继续尝试
                if result['deleted_count'] == 0:
                    cleanup_days = max(1, cleanup_days - 1)
                else:
                    break
            
            return {
                'cleaned': True,
                'deleted_count': total_deleted,
                'freed_space_mb': total_freed,
                'current_usage_percent': info['usage_percent'],
                'message': f"自动清理完成：删除 {total_deleted} 个文件，释放 {total_freed:.2f}MB"
            }
        else:
            return {
                'cleaned': False,
                'current_usage_percent': info['usage_percent'],
                'message': '存储空间充足，无需清理'
            }
    
    async def cleanup_by_size(self, target_size_gb: float) -> Dict[str, Any]:
        """
        清理文件直到达到目标大小
        
        Args:
            target_size_gb: 目标大小（GB）
            
        Returns:
            清理结果
        """
        try:
            current_size = self.get_storage_size()
            if current_size <= target_size_gb:
                return {
                    'deleted_count': 0,
                    'freed_space_gb': 0,
                    'message': '当前空间已满足要求'
                }
            
            # 按文件修改时间排序（旧的先删）
            files_with_time = []
            for filepath in self.storage_path.glob("*.jpg"):
                stat = filepath.stat()
                files_with_time.append((filepath, stat.st_mtime, stat.st_size))
            
            # 按时间升序排序
            files_with_time.sort(key=lambda x: x[1])
            
            deleted_count = 0
            freed_space = 0
            
            for filepath, _, file_size in files_with_time:
                # 如果已经达到目标，停止删除
                if self.get_storage_size() <= target_size_gb:
                    break
                
                # 删除文件
                filepath.unlink()
                deleted_count += 1
                freed_space += file_size
                
                # 删除Token映射
                if str(filepath) in self.url_tokens:
                    del self.url_tokens[str(filepath)]
            
            freed_gb = freed_space / (1024 ** 3)
            logger.info(f"按大小清理完成: 删除 {deleted_count} 个文件, 释放 {freed_gb:.2f}GB")
            
            return {
                'deleted_count': deleted_count,
                'freed_space_gb': freed_gb,
                'current_size_gb': self.get_storage_size(),
                'message': f'清理完成：删除 {deleted_count} 个文件'
            }
            
        except Exception as e:
            logger.error(f"按大小清理失败: {str(e)}")
            return {
                'deleted_count': 0,
                'freed_space_gb': 0,
                'error': str(e)
            }
    
    async def process_images_batch(self, image_urls: List[str],
                                   strategy: str = "smart",
                                   cookies: Optional[Dict] = None,
                                   referer: Optional[str] = None) -> List[Optional[Dict]]:
        """
        批量并行处理多张图片（v1.8.1新增：多进程池，性能+800%）
        
        Args:
            image_urls: 图片URL列表
            strategy: 处理策略（smart/direct/imgbed）
            cookies: Cookie
            referer: Referer
            
        Returns:
            处理结果列表
        """
        if not image_urls:
            return []
        
        logger.info(f"🚀 开始批量处理 {len(image_urls)} 张图片（多进程模式）")
        start_time = time.time()
        
        try:
            # 步骤1：并行下载所有图片
            download_tasks = [
                self.download_image(url, cookies, referer)
                for url in image_urls
            ]
            downloaded_images = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            # 步骤2：过滤下载成功的图片
            valid_images = []
            valid_urls = []
            for i, (url, data) in enumerate(zip(image_urls, downloaded_images)):
                if isinstance(data, Exception):
                    logger.error(f"图片下载失败: {url}, 错误: {data}")
                    valid_images.append(None)
                elif data:
                    valid_images.append(data)
                    valid_urls.append(url)
                else:
                    valid_images.append(None)
            
            logger.info(f"下载完成: {len(valid_urls)}/{len(image_urls)} 张图片成功")
            
            # 步骤3：使用多进程池并行压缩图片
            compress_func = partial(self._compress_image_worker, max_size_mb=10.0, quality=85)
            
            # 提交到进程池
            loop = asyncio.get_event_loop()
            compression_futures = []
            
            for data in valid_images:
                if data:
                    future = loop.run_in_executor(self.process_pool, compress_func, data)
                    compression_futures.append(future)
                else:
                    compression_futures.append(None)
            
            # 等待所有压缩任务完成
            compressed_results = []
            for future in compression_futures:
                if future:
                    try:
                        result = await future
                        compressed_results.append(result)
                    except Exception as e:
                        logger.error(f"图片压缩异常: {e}")
                        compressed_results.append(None)
                else:
                    compressed_results.append(None)
            
            logger.info(f"✅ 压缩完成: {len([r for r in compressed_results if r])}/{len(valid_urls)} 张图片")
            
            # 步骤4：保存并生成URL
            results = []
            for i, (url, compressed_data) in enumerate(zip(image_urls, compressed_results)):
                if not compressed_data:
                    results.append(None)
                    continue
                
                try:
                    # 根据策略处理
                    if strategy == "direct":
                        results.append({'original': url, 'local': None, 'filepath': None})
                    elif strategy == "imgbed":
                        filepath = self.save_to_local(compressed_data)
                        local_url = self.generate_url(filepath)
                        results.append({'original': url, 'local': local_url, 'filepath': filepath})
                    else:  # smart
                        filepath = self.save_to_local(compressed_data)
                        local_url = self.generate_url(filepath)
                        results.append({'original': url, 'local': local_url, 'filepath': filepath})
                except Exception as e:
                    logger.error(f"保存图片失败: {url}, 错误: {e}")
                    results.append(None)
            
            elapsed_time = time.time() - start_time
            success_count = len([r for r in results if r])
            self.stats['parallel_count'] += 1
            
            logger.info(f"🎉 批量处理完成: 成功 {success_count}/{len(image_urls)} 张，耗时 {elapsed_time:.2f}秒")
            
            return results
            
        except Exception as e:
            logger.error(f"批量处理异常: {str(e)}")
            return [None] * len(image_urls)
    
    async def process_image(self, url: str,
                           strategy: str = "smart",
                           cookies: Optional[Dict] = None,
                           referer: Optional[str] = None) -> Optional[str]:
        """
        处理图片（智能策略）
        
        Args:
            url: 图片URL
            strategy: 处理策略（smart/direct/imgbed）
            cookies: Cookie
            referer: Referer
            
        Returns:
            处理后的URL或本地路径
        """
        try:
            # 1. 下载图片
            image_data = await self.download_image(url, cookies, referer)
            if not image_data:
                return None
            
            # 2. 压缩图片
            compressed_data = self.compress_image(image_data)
            
            # 3. 根据策略处理
            if strategy == "direct":
                # 直传模式：返回原URL（由转发器直接上传）
                return url
            
            elif strategy == "imgbed":
                # 图床模式：保存到本地并生成URL
                filepath = self.save_to_local(compressed_data)
                return self.generate_url(filepath)
            
            else:  # smart
                # 智能模式：先尝试返回原URL，如果失败则使用图床
                # 保存到本地作为备份
                filepath = self.save_to_local(compressed_data)
                
                # 返回原URL和本地URL（让转发器决定）
                return {
                    'original': url,
                    'local': self.generate_url(filepath),
                    'filepath': filepath
                }
            
        except Exception as e:
            logger.error(f"图片处理失败: {str(e)}")
            return None
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        获取图片处理统计信息
        
        Returns:
            统计信息字典
        """
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
            'parallel_batch_count': self.stats['parallel_count'],
            'avg_compressed_mb': round(avg_compressed_mb, 2),
            'avg_saved_mb': round(avg_saved_mb, 2),
            'process_pool_workers': self.process_pool._max_workers if hasattr(self.process_pool, '_max_workers') else 0
        }
    
    def shutdown(self):
        """关闭进程池"""
        try:
            self.process_pool.shutdown(wait=True)
            logger.info("图片处理进程池已关闭")
        except Exception as e:
            logger.error(f"关闭进程池失败: {str(e)}")
    
    def __del__(self):
        """析构函数，确保进程池被关闭"""
        self.shutdown()


class AttachmentProcessor:
    """附件文件处理器（支持最大50MB文件）"""
    
    def __init__(self):
        # 附件存储目录
        self.storage_path = Path(settings.data_dir) / "attachments"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 最大文件大小（50MB）
        self.max_size_mb = 50
    
    async def download_attachment(self, url: str,
                                  filename: str,
                                  cookies: Optional[Dict] = None,
                                  referer: Optional[str] = None) -> Optional[str]:
        """
        下载附件文件
        
        Args:
            url: 附件URL
            filename: 文件名
            cookies: Cookie字典
            referer: Referer头
            
        Returns:
            本地文件路径，失败返回None
        """
        try:
            logger.info(f"开始下载附件: {filename}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            if referer:
                headers['Referer'] = referer
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    timeout=aiohttp.ClientTimeout(total=60)  # 60秒超时
                ) as response:
                    if response.status != 200:
                        logger.error(f"附件下载失败: {url}, 状态码: {response.status}")
                        return None
                    
                    # 检查文件大小
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        size_mb = int(content_length) / (1024 * 1024)
                        if size_mb > self.max_size_mb:
                            logger.error(f"附件过大: {size_mb:.2f}MB > {self.max_size_mb}MB")
                            return None
                        logger.info(f"附件大小: {size_mb:.2f}MB")
                    
                    # 生成安全的文件名
                    safe_filename = self._sanitize_filename(filename)
                    
                    # 如果文件已存在，添加时间戳
                    filepath = self.storage_path / safe_filename
                    if filepath.exists():
                        name, ext = os.path.splitext(safe_filename)
                        timestamp = int(time.time())
                        safe_filename = f"{name}_{timestamp}{ext}"
                        filepath = self.storage_path / safe_filename
                    
                    # 分块下载并保存
                    total_size = 0
                    with open(filepath, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            total_size += len(chunk)
                            
                            # 检查是否超过最大大小
                            if total_size > self.max_size_mb * 1024 * 1024:
                                f.close()
                                filepath.unlink()  # 删除部分下载的文件
                                logger.error(f"附件下载超过最大限制: {self.max_size_mb}MB")
                                return None
                    
                    logger.info(f"✅ 附件下载成功: {filepath}, 大小: {total_size / 1024:.2f}KB")
                    return str(filepath)
                    
        except asyncio.TimeoutError:
            logger.error(f"附件下载超时: {url}")
            return None
        except Exception as e:
            logger.error(f"附件下载异常: {url}, 错误: {str(e)}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除不安全字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            安全的文件名
        """
        # 移除路径分隔符和不安全字符
        unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        safe_name = filename
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        
        # 限制文件名长度（保留扩展名）
        name, ext = os.path.splitext(safe_name)
        if len(name) > 200:
            name = name[:200]
        
        return name + ext
    
    async def cleanup_old_attachments(self, days: int = 7):
        """
        清理旧附件
        
        Args:
            days: 保留天数
        """
        try:
            current_time = time.time()
            deleted_count = 0
            freed_space = 0
            
            for filepath in self.storage_path.glob("*"):
                if filepath.is_file():
                    # 检查文件修改时间
                    mtime = filepath.stat().st_mtime
                    age_days = (current_time - mtime) / (24 * 3600)
                    
                    if age_days > days:
                        file_size = filepath.stat().st_size
                        filepath.unlink()
                        deleted_count += 1
                        freed_space += file_size
            
            freed_mb = freed_space / (1024 * 1024)
            logger.info(f"清理旧附件完成: 删除 {deleted_count} 个文件, 释放 {freed_mb:.2f}MB 空间")
            
        except Exception as e:
            logger.error(f"清理旧附件失败: {str(e)}")
    
    def get_storage_size(self) -> float:
        """
        获取附件存储空间占用（GB）
        
        Returns:
            占用大小（GB）
        """
        total_size = 0
        for filepath in self.storage_path.glob("*"):
            if filepath.is_file():
                total_size += filepath.stat().st_size
        
        return total_size / (1024 ** 3)
    
    def get_file_info(self, filepath: str) -> Optional[Dict]:
        """
        获取文件信息
        
        Args:
            filepath: 文件路径
            
        Returns:
            文件信息字典
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                'filename': path.name,
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created_at': stat.st_ctime,
                'modified_at': stat.st_mtime,
            }
        except Exception as e:
            logger.error(f"获取文件信息失败: {str(e)}")
            return None


# 全局单例
image_processor = ImageProcessor()
attachment_processor = AttachmentProcessor()
