"""
图片处理模块
支持图片下载、上传、压缩和图床服务
"""
import os
import asyncio
import aiohttp
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image
from io import BytesIO
from ..config import settings
from ..utils.logger import logger


class ImageProcessor:
    """图片处理器"""
    
    def __init__(self):
        # 图片存储目录
        self.storage_path = Path(settings.data_dir) / "images"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 图片URL映射（文件路径 -> Token）
        self.url_tokens: Dict[str, str] = {}
    
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
    
    def compress_image(self, image_data: bytes, 
                       max_size_mb: float = 10.0,
                       quality: int = 85) -> bytes:
        """
        压缩图片
        
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
            
            # 转换为RGB（如果是RGBA）
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            # 压缩
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            compressed_data = output.getvalue()
            
            # 检查压缩后大小
            compressed_size_mb = len(compressed_data) / (1024 * 1024)
            logger.info(f"图片压缩: {size_mb:.2f}MB -> {compressed_size_mb:.2f}MB")
            
            # 如果仍然太大，递归降低质量
            if compressed_size_mb > max_size_mb and quality > 50:
                return self.compress_image(image_data, max_size_mb, quality - 10)
            
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
