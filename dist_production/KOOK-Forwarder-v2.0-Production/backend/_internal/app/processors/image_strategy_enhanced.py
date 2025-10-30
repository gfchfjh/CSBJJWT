"""
图片处理智能策略 - ✅ P0-7优化完成: 3步Fallback降级机制
"""
import aiohttp
import asyncio
from typing import Dict, Optional, Tuple
from pathlib import Path
from ..utils.logger import logger
from ..config import settings


class ImageStrategyEnhanced:
    """
    ✅ P0-7优化: 图片处理智能Fallback策略
    
    三步降级机制：
    1. 直传模式：验证原始URL可访问性，成功则直传
    2. 图床模式：原始URL不可用时，下载并上传到本地图床
    3. 本地模式：图床也失败时，保存到本地文件系统等待后续重试
    """
    
    def __init__(self):
        self.stats = {
            "direct_success": 0,      # 直传成功次数
            "imgbed_success": 0,      # 图床成功次数
            "local_fallback": 0,      # 本地降级次数
            "total_failures": 0       # 完全失败次数
        }
        
        logger.info("✅ P0-7: 图片智能Fallback策略已初始化")
    
    async def process_with_smart_fallback(
        self,
        url: str,
        cookies: dict = None,
        referer: str = "https://www.kookapp.cn"
    ) -> Dict[str, any]:
        """
        ✅ P0-7核心: 智能Fallback处理图片
        
        处理流程：
        1️⃣ 尝试验证原始URL → 成功则直传
        2️⃣ 失败则下载并上传到本地图床 → 返回图床URL
        3️⃣ 图床也失败则保存到本地文件 → 等待后续重试
        
        Args:
            url: 图片原始URL
            cookies: Cookie字典（用于下载防盗链图片）
            referer: Referer头
            
        Returns:
            {
                "success": bool,           # 是否成功
                "method": str,             # 使用的方法：direct/imgbed/local
                "original_url": str,       # 原始URL
                "accessible_url": str,     # 可访问的URL（直传或图床）
                "local_path": str,         # 本地路径（降级时）
                "fallback_count": int,     # Fallback次数（0/1/2）
                "error": str               # 错误信息（如果有）
            }
        """
        result = {
            "success": False,
            "method": None,
            "original_url": url,
            "accessible_url": None,
            "local_path": None,
            "fallback_count": 0,
            "error": None
        }
        
        logger.info(f"🖼️ P0-7: 开始智能Fallback处理图片: {url[:50]}...")
        
        # ======= 步骤1: 尝试验证原始URL可访问性 =======
        logger.info("1️⃣ 步骤1: 验证原始URL可访问性...")
        
        is_accessible = await self._test_url_accessibility(url, cookies, referer)
        
        if is_accessible:
            logger.info("✅ 原始URL可直接访问，使用直传模式")
            result["success"] = True
            result["method"] = "direct"
            result["accessible_url"] = url
            result["fallback_count"] = 0
            
            self.stats["direct_success"] += 1
            return result
        
        logger.warning("⚠️ 原始URL不可访问，进入Fallback步骤2")
        result["fallback_count"] += 1
        
        # ======= 步骤2: 下载并上传到本地图床 =======
        logger.info("2️⃣ 步骤2: 下载图片并上传到本地图床...")
        
        # 下载图片
        image_data = await self._download_image_safe(url, cookies, referer)
        
        if image_data:
            # 上传到本地图床
            imgbed_url = await self._upload_to_local_imgbed(image_data, url)
            
            if imgbed_url:
                logger.info("✅ 图床模式成功")
                result["success"] = True
                result["method"] = "imgbed"
                result["accessible_url"] = imgbed_url
                result["fallback_count"] = 1
                
                self.stats["imgbed_success"] += 1
                return result
            else:
                logger.warning("⚠️ 上传到图床失败，进入Fallback步骤3")
                result["fallback_count"] += 1
        else:
            logger.warning("⚠️ 下载图片失败，进入Fallback步骤3")
            result["fallback_count"] += 1
        
        # ======= 步骤3: 保存到本地文件系统 =======
        logger.info("3️⃣ 步骤3: 保存到本地文件系统（等待后续重试）...")
        
        if image_data:
            local_path = await self._save_to_local_file(image_data, url)
            
            if local_path:
                logger.info("⚠️ 本地降级模式（图片已保存）")
                result["success"] = True  # 标记为成功（虽然是降级）
                result["method"] = "local"
                result["local_path"] = local_path
                result["fallback_count"] = 2
                result["error"] = "图片暂存本地，等待后续重试上传"
                
                self.stats["local_fallback"] += 1
                return result
        
        # ======= 全部失败 =======
        logger.error("❌ P0-7: 所有Fallback步骤都失败")
        result["success"] = False
        result["fallback_count"] = 3
        result["error"] = "原始URL不可访问、下载失败、图床失败、本地保存也失败"
        
        self.stats["total_failures"] += 1
        return result
    
    async def _test_url_accessibility(
        self,
        url: str,
        cookies: dict = None,
        referer: str = None,
        timeout: int = 5
    ) -> bool:
        """
        测试URL是否可直接访问
        
        Args:
            url: 图片URL
            cookies: Cookie字典
            referer: Referer头
            timeout: 超时时间（秒）
            
        Returns:
            是否可访问
        """
        try:
            headers = {}
            if referer:
                headers['Referer'] = referer
            if cookies:
                # 构建Cookie头
                cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
                headers['Cookie'] = cookie_str
            
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    allow_redirects=True
                ) as response:
                    # 200-299都认为可访问
                    is_accessible = 200 <= response.status < 300
                    
                    if is_accessible:
                        logger.debug(f"✅ URL可访问: {url[:50]}... (HTTP {response.status})")
                    else:
                        logger.debug(f"❌ URL不可访问: {url[:50]}... (HTTP {response.status})")
                    
                    return is_accessible
        
        except asyncio.TimeoutError:
            logger.debug(f"❌ URL访问超时: {url[:50]}...")
            return False
        except Exception as e:
            logger.debug(f"❌ URL访问失败: {url[:50]}... - {str(e)}")
            return False
    
    async def _download_image_safe(
        self,
        url: str,
        cookies: dict = None,
        referer: str = None,
        max_size_mb: int = 50
    ) -> Optional[bytes]:
        """
        安全地下载图片（带防盗链处理）
        
        Args:
            url: 图片URL
            cookies: Cookie字典
            referer: Referer头
            max_size_mb: 最大文件大小（MB）
            
        Returns:
            图片二进制数据，失败返回None
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            if referer:
                headers['Referer'] = referer
            
            if cookies:
                cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
                headers['Cookie'] = cookie_str
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        logger.warning(f"下载图片失败: HTTP {response.status}")
                        return None
                    
                    # 检查文件大小
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        size_mb = int(content_length) / (1024 * 1024)
                        if size_mb > max_size_mb:
                            logger.warning(f"图片过大: {size_mb:.2f}MB > {max_size_mb}MB")
                            return None
                    
                    # 读取数据
                    image_data = await response.read()
                    
                    logger.info(f"✅ 图片下载成功: {len(image_data) / 1024:.2f}KB")
                    return image_data
        
        except asyncio.TimeoutError:
            logger.error("下载图片超时")
            return None
        except Exception as e:
            logger.error(f"下载图片异常: {str(e)}")
            return None
    
    async def _upload_to_local_imgbed(
        self,
        image_data: bytes,
        original_url: str
    ) -> Optional[str]:
        """
        上传图片到本地图床
        
        Args:
            image_data: 图片二进制数据
            original_url: 原始URL（用于生成文件名）
            
        Returns:
            图床URL，失败返回None
        """
        try:
            from ..processors.image import image_processor
            
            # 生成文件名
            import hashlib
            url_hash = hashlib.md5(original_url.encode()).hexdigest()
            filename = f"{url_hash}.jpg"
            
            # 保存到图床目录
            imgbed_dir = Path(settings.data_dir) / 'images'
            imgbed_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = imgbed_dir / filename
            file_path.write_bytes(image_data)
            
            # 生成图床URL（带Token）
            import secrets
            token = secrets.token_urlsafe(16)
            
            # 保存Token到数据库（有效期2小时）
            from ..queue.redis_client import redis_queue
            await redis_queue.set(
                f"img_token:{filename}",
                token,
                expire=7200  # 2小时
            )
            
            # 构建完整URL
            imgbed_url = f"http://127.0.0.1:{settings.image_server_port}/images/{filename}?token={token}"
            
            logger.info(f"✅ 上传到本地图床成功: {filename}")
            return imgbed_url
        
        except Exception as e:
            logger.error(f"上传到本地图床失败: {str(e)}")
            return None
    
    async def _save_to_local_file(
        self,
        image_data: bytes,
        original_url: str
    ) -> Optional[str]:
        """
        保存图片到本地文件系统（最后的降级方案）
        
        Args:
            image_data: 图片二进制数据
            original_url: 原始URL
            
        Returns:
            本地文件路径，失败返回None
        """
        try:
            # 创建待重试目录
            pending_dir = Path(settings.data_dir) / 'images_pending'
            pending_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            import hashlib
            import time
            url_hash = hashlib.md5(original_url.encode()).hexdigest()
            timestamp = int(time.time())
            filename = f"{timestamp}_{url_hash}.jpg"
            
            file_path = pending_dir / filename
            file_path.write_bytes(image_data)
            
            logger.info(f"⚠️ 图片已保存到本地待重试: {file_path}")
            
            # 记录元数据到Redis（用于后续重试）
            from ..queue.redis_client import redis_queue
            await redis_queue.set(
                f"img_pending:{filename}",
                original_url,
                expire=86400  # 1天
            )
            
            return str(file_path)
        
        except Exception as e:
            logger.error(f"保存到本地文件失败: {str(e)}")
            return None
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            {
                "direct_success": int,
                "imgbed_success": int,
                "local_fallback": int,
                "total_failures": int,
                "total_processed": int,
                "success_rate": float
            }
        """
        total_processed = (
            self.stats["direct_success"] +
            self.stats["imgbed_success"] +
            self.stats["local_fallback"] +
            self.stats["total_failures"]
        )
        
        success_count = (
            self.stats["direct_success"] +
            self.stats["imgbed_success"] +
            self.stats["local_fallback"]
        )
        
        success_rate = (success_count / total_processed * 100) if total_processed > 0 else 0
        
        return {
            **self.stats,
            "total_processed": total_processed,
            "success_rate": round(success_rate, 2)
        }


# 创建全局实例
image_strategy_enhanced = ImageStrategyEnhanced()
