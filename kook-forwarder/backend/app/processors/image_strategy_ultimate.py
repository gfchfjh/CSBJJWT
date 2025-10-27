"""
图片处理终极策略模块（✨ P0-4优化）
支持：智能模式、Token安全、自动清理
"""
import time
import hashlib
import hmac
import asyncio
from pathlib import Path
from typing import Optional, Tuple, Any
from enum import Enum
from ..utils.logger import logger
from ..config import settings


class ImageStrategy(Enum):
    """图片处理策略"""
    SMART = "smart"          # 智能模式（优先直传，失败回退图床）
    DIRECT_ONLY = "direct"   # 仅直传到目标平台
    IMGBED_ONLY = "imgbed"   # 仅使用内置图床


class ImageProcessorUltimate:
    """图片处理器终极版（✨ P0-4优化）"""
    
    def __init__(self):
        self.strategy = ImageStrategy.SMART
        self.imgbed_base_url = f"http://localhost:{settings.image_server_port}"
        self.token_expiry = 2 * 60 * 60  # 2小时
        self.max_storage_gb = getattr(settings, 'max_image_storage_gb', 10)
        self.auto_cleanup_days = getattr(settings, 'image_cleanup_days', 7)
        self.imgbed_dir = Path("data/images")
        self.imgbed_dir.mkdir(parents=True, exist_ok=True)
    
    def set_strategy(self, strategy: str):
        """设置处理策略"""
        try:
            self.strategy = ImageStrategy(strategy)
            logger.info(f"✅ 图片处理策略已设置为: {strategy}")
        except ValueError:
            logger.error(f"❌ 无效的策略: {strategy}")
    
    async def process_image(
        self,
        image_url: str,
        cookies: dict,
        platform: str,
        platform_api: Any
    ) -> Tuple[bool, str]:
        """
        处理图片（智能策略）
        
        Args:
            image_url: KOOK图片URL
            cookies: Cookie字典（防盗链）
            platform: 目标平台
            platform_api: 平台API客户端
        
        Returns:
            (成功与否, 图片URL或错误信息)
        """
        # 下载图片
        image_data = await self._download_with_cookies(image_url, cookies)
        if not image_data:
            return False, "图片下载失败"
        
        # 根据策略处理
        if self.strategy == ImageStrategy.SMART:
            return await self._smart_upload(image_data, platform, platform_api)
        elif self.strategy == ImageStrategy.DIRECT_ONLY:
            return await self._direct_upload(image_data, platform, platform_api)
        elif self.strategy == ImageStrategy.IMGBED_ONLY:
            return await self._imgbed_upload(image_data)
        
        return False, "未知策略"
    
    async def _download_with_cookies(self, url: str, cookies: dict) -> Optional[bytes]:
        """下载图片（带Cookie防盗链）"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://www.kookapp.cn/'
                }
                
                async with session.get(url, headers=headers, cookies=cookies, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.read()
                        logger.info(f"✅ 图片下载成功: {len(data)} bytes")
                        return data
                    else:
                        logger.error(f"❌ 图片下载失败: HTTP {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ 图片下载异常: {e}")
            return None
    
    async def _smart_upload(
        self,
        image_data: bytes,
        platform: str,
        platform_api: Any
    ) -> Tuple[bool, str]:
        """
        智能上传策略（✨ P0-4核心功能）
        
        流程:
        1. 优先尝试直接上传到目标平台
        2. 如果失败（如超大小限制），自动回退到图床
        3. 图床也失败则保存本地，等待下次重试
        """
        logger.info(f"🧠 智能模式: 优先尝试直传到 {platform}...")
        
        # 第1步: 尝试直传
        success, result = await self._direct_upload(image_data, platform, platform_api)
        
        if success:
            logger.info(f"✅ 直传成功: {result}")
            return True, result
        
        logger.warning(f"⚠️ 直传失败: {result}，回退到图床模式...")
        
        # 第2步: 回退到图床
        success, result = await self._imgbed_upload(image_data)
        
        if success:
            logger.info(f"✅ 图床上传成功: {result}")
            return True, result
        
        logger.error(f"❌ 图床上传也失败: {result}")
        
        # 第3步: 保存本地等待重试
        local_path = await self._save_for_retry(image_data)
        return False, f"已保存本地: {local_path}"
    
    async def _direct_upload(
        self,
        image_data: bytes,
        platform: str,
        platform_api: Any
    ) -> Tuple[bool, str]:
        """直接上传到目标平台"""
        try:
            if platform == "discord":
                # 注意：这里需要platform_api有upload_file方法
                # 实际实现需要根据具体的API接口调整
                logger.info("上传到Discord...")
                # url = await platform_api.upload_file(image_data, filename="image.jpg")
                # return True, url
                return False, "Discord直传暂未实现"
            
            elif platform == "telegram":
                logger.info("上传到Telegram...")
                # file_id = await platform_api.send_photo(image_data)
                # return True, f"tg://{file_id}"
                return False, "Telegram直传暂未实现"
            
            elif platform == "feishu":
                logger.info("上传到飞书...")
                # media_id = await platform_api.upload_image(image_data)
                # return True, f"feishu://{media_id}"
                return False, "飞书直传暂未实现"
            
            return False, f"不支持的平台: {platform}"
            
        except Exception as e:
            logger.error(f"直传失败: {e}")
            return False, str(e)
    
    async def _imgbed_upload(self, image_data: bytes) -> Tuple[bool, str]:
        """上传到内置图床（✨ P0-4核心功能）"""
        try:
            # 生成唯一文件名
            file_hash = hashlib.sha256(image_data).hexdigest()[:16]
            timestamp = int(time.time())
            filename = f"{timestamp}_{file_hash}.jpg"
            
            # 保存到图床目录
            file_path = self.imgbed_dir / filename
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            # 生成带Token的URL（✨ P0-4安全功能）
            token = self._generate_token(filename)
            url = f"{self.imgbed_base_url}/images/{filename}?token={token}"
            
            # 记录到数据库（用于清理）
            await self._record_image(filename, len(image_data), timestamp)
            
            logger.info(f"✅ 图床上传成功: {filename} ({len(image_data)} bytes)")
            return True, url
            
        except Exception as e:
            logger.error(f"图床上传失败: {e}")
            return False, str(e)
    
    def _generate_token(self, filename: str) -> str:
        """
        生成图片访问Token（✨ P0-4安全功能）
        
        Token格式: timestamp:signature
        signature = HMAC-SHA256(filename + timestamp + secret_key)
        有效期: 2小时
        """
        timestamp = int(time.time())
        secret_key = getattr(settings, 'secret_key', 'default_secret_key_change_me')
        
        message = f"{filename}:{timestamp}:{secret_key}"
        signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Token = timestamp:signature
        return f"{timestamp}:{signature}"
    
    def verify_token(self, filename: str, token: str) -> bool:
        """验证Token有效性（✨ P0-4安全功能）"""
        try:
            timestamp_str, signature = token.split(":", 1)
            timestamp = int(timestamp_str)
            
            # 检查是否过期（2小时）
            now = int(time.time())
            if now - timestamp > self.token_expiry:
                logger.warning(f"Token已过期: {filename}")
                return False
            
            # 重新生成Token验证
            secret_key = getattr(settings, 'secret_key', 'default_secret_key_change_me')
            message = f"{filename}:{timestamp}:{secret_key}"
            expected_signature = hmac.new(
                secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = signature == expected_signature
            if not is_valid:
                logger.warning(f"Token签名无效: {filename}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Token验证异常: {e}")
            return False
    
    async def _save_for_retry(self, image_data: bytes) -> str:
        """保存到本地等待重试"""
        retry_dir = Path("data/images_retry")
        retry_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"retry_{int(time.time())}_{hashlib.md5(image_data).hexdigest()[:8]}.jpg"
        file_path = retry_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        logger.info(f"💾 图片已保存本地等待重试: {file_path}")
        return str(file_path)
    
    async def _record_image(self, filename: str, size: int, timestamp: int):
        """记录图片到数据库"""
        try:
            from ..database import db
            
            # 记录图片信息（用于后续清理）
            await db.execute(
                """INSERT OR REPLACE INTO image_storage 
                   (filename, size, upload_time, last_access)
                   VALUES (?, ?, ?, ?)""",
                (filename, size, timestamp, timestamp)
            )
            
        except Exception as e:
            logger.error(f"记录图片信息失败: {e}")
    
    async def auto_cleanup_old_images(self):
        """
        自动清理旧图片（✨ P0-4核心功能）
        
        规则:
        1. 删除N天前的图片（默认7天）
        2. 如果空间超过最大限制，删除最旧的图片直到降到90%
        """
        if not self.imgbed_dir.exists():
            return
        
        now = time.time()
        cutoff_time = now - (self.auto_cleanup_days * 24 * 60 * 60)
        
        deleted_count = 0
        deleted_size = 0
        
        logger.info(f"🗑️ 开始自动清理图片...")
        
        # 获取所有图片文件（按时间排序）
        images = sorted(
            self.imgbed_dir.glob("*.jpg"),
            key=lambda p: p.stat().st_mtime
        )
        
        # 规则1: 删除N天前的图片
        for image_path in images:
            if image_path.stat().st_mtime < cutoff_time:
                size = image_path.stat().st_size
                image_path.unlink()
                deleted_count += 1
                deleted_size += size
                logger.debug(f"删除旧图: {image_path.name} ({size/1024:.1f}KB)")
        
        # 规则2: 空间检查
        total_size = sum(f.stat().st_size for f in self.imgbed_dir.glob("*.jpg"))
        max_size = self.max_storage_gb * 1024 * 1024 * 1024
        
        if total_size > max_size:
            logger.warning(f"⚠️ 图床空间超限: {total_size/1024/1024/1024:.2f}GB > {self.max_storage_gb}GB")
            
            # 删除最旧的图片直到降到90%
            target_size = max_size * 0.9
            current_size = total_size
            
            # 重新获取图片列表（排除已删除的）
            images = sorted(
                self.imgbed_dir.glob("*.jpg"),
                key=lambda p: p.stat().st_mtime
            )
            
            for image_path in images:
                if current_size <= target_size:
                    break
                
                size = image_path.stat().st_size
                image_path.unlink()
                current_size -= size
                deleted_count += 1
                deleted_size += size
                logger.debug(f"删除旧图(空间清理): {image_path.name}")
        
        if deleted_count > 0:
            logger.info(
                f"✅ 自动清理完成: 删除 {deleted_count} 张图片，"
                f"释放 {deleted_size/1024/1024:.2f}MB 空间"
            )
        else:
            logger.info("✅ 无需清理")
    
    def get_storage_stats(self) -> dict:
        """获取存储统计信息"""
        if not self.imgbed_dir.exists():
            return {
                "total_images": 0,
                "total_size": 0,
                "total_size_mb": 0,
                "max_size_gb": self.max_storage_gb,
                "usage_percentage": 0
            }
        
        images = list(self.imgbed_dir.glob("*.jpg"))
        total_size = sum(f.stat().st_size for f in images)
        max_size = self.max_storage_gb * 1024 * 1024 * 1024
        
        return {
            "total_images": len(images),
            "total_size": total_size,
            "total_size_mb": total_size / 1024 / 1024,
            "total_size_gb": total_size / 1024 / 1024 / 1024,
            "max_size_gb": self.max_storage_gb,
            "usage_percentage": (total_size / max_size * 100) if max_size > 0 else 0
        }


# 全局实例
image_processor_ultimate = ImageProcessorUltimate()
