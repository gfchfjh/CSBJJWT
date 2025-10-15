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
            return False
        
        # 检查是否过期
        if time.time() > token_info['expire_at']:
            del self.url_tokens[filepath]
            return False
        
        return True
    
    async def cleanup_old_images(self, days: int = 7):
        """
        清理旧图片
        
        Args:
            days: 保留天数
        """
        try:
            current_time = time.time()
            deleted_count = 0
            
            for filepath in self.storage_path.glob("*.jpg"):
                # 检查文件修改时间
                mtime = filepath.stat().st_mtime
                age_days = (current_time - mtime) / (24 * 3600)
                
                if age_days > days:
                    filepath.unlink()
                    deleted_count += 1
                    
                    # 删除Token映射
                    if str(filepath) in self.url_tokens:
                        del self.url_tokens[str(filepath)]
            
            logger.info(f"清理旧图片完成: 删除 {deleted_count} 个文件")
            
        except Exception as e:
            logger.error(f"清理旧图片失败: {str(e)}")
    
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


# 全局单例
image_processor = ImageProcessor()
