"""
图床Token管理器
✅ P0-4深度优化: 为图片URL生成临时访问Token，增强安全性
"""
import secrets
import time
from typing import Optional, Dict
from pathlib import Path
from ..utils.logger import logger


class ImageTokenManager:
    """图床Token管理器"""
    
    def __init__(self, token_expire_hours: int = 2):
        """
        初始化Token管理器
        
        Args:
            token_expire_hours: Token有效期（小时）
        """
        self.token_expire_hours = token_expire_hours
        self.tokens: Dict[str, Dict] = {}  # {token: {"path": Path, "expire_at": timestamp, "image_name": str}}
        
        logger.info(f"✅ 图床Token管理器已初始化（有效期: {token_expire_hours}小时）")
    
    def generate_token(self, image_path: Path, expire_hours: Optional[int] = None) -> str:
        """
        为图片生成临时访问Token
        
        Args:
            image_path: 图片文件路径
            expire_hours: 过期时间（小时），不指定则使用默认值
        
        Returns:
            Token字符串
        """
        # 生成随机Token（URL安全）
        token = secrets.token_urlsafe(32)
        
        # 计算过期时间
        expire_hours = expire_hours or self.token_expire_hours
        expire_at = time.time() + (expire_hours * 3600)
        
        # 存储Token信息
        self.tokens[token] = {
            "path": image_path,
            "expire_at": expire_at,
            "image_name": image_path.name,
            "created_at": time.time()
        }
        
        logger.debug(f"🔐 生成Token: {token[:10]}... → {image_path.name} (有效期: {expire_hours}小时)")
        
        return token
    
    def validate_token(self, token: str, image_name: str) -> Optional[Path]:
        """
        验证Token并返回图片路径
        
        Args:
            token: Token字符串
            image_name: 请求的图片文件名
        
        Returns:
            如果Token有效，返回图片路径；否则返回None
        """
        # 检查Token是否存在
        if token not in self.tokens:
            logger.warning(f"⚠️ Token无效或不存在: {token[:10]}...")
            return None
        
        token_data = self.tokens[token]
        
        # 检查是否过期
        if token_data["expire_at"] < time.time():
            logger.warning(f"⚠️ Token已过期: {token[:10]}... (过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(token_data['expire_at']))})")
            # 删除过期Token
            del self.tokens[token]
            return None
        
        # 检查图片名称是否匹配（防止路径遍历攻击）
        if token_data["image_name"] != image_name:
            logger.error(f"🚨 安全警告: Token对应的图片名称不匹配！Token: {token[:10]}..., 请求: {image_name}, 实际: {token_data['image_name']}")
            return None
        
        # 验证通过，返回图片路径
        image_path = token_data["path"]
        
        # 检查文件是否存在
        if not image_path.exists():
            logger.error(f"❌ 图片文件不存在: {image_path}")
            # 删除无效Token
            del self.tokens[token]
            return None
        
        logger.debug(f"✅ Token验证通过: {token[:10]}... → {image_name}")
        
        return image_path
    
    def revoke_token(self, token: str) -> bool:
        """
        撤销Token
        
        Args:
            token: Token字符串
        
        Returns:
            是否成功撤销
        """
        if token in self.tokens:
            del self.tokens[token]
            logger.info(f"🗑️ Token已撤销: {token[:10]}...")
            return True
        return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        清理所有过期Token
        
        Returns:
            清理的Token数量
        """
        now = time.time()
        expired_tokens = [
            token for token, data in self.tokens.items()
            if data["expire_at"] < now
        ]
        
        for token in expired_tokens:
            del self.tokens[token]
        
        if expired_tokens:
            logger.info(f"🧹 已清理 {len(expired_tokens)} 个过期Token")
        
        return len(expired_tokens)
    
    def get_stats(self) -> Dict:
        """
        获取Token统计信息
        
        Returns:
            统计信息字典
        """
        now = time.time()
        
        valid_tokens = [t for t, d in self.tokens.items() if d["expire_at"] > now]
        expired_tokens = [t for t, d in self.tokens.items() if d["expire_at"] <= now]
        
        # 计算平均剩余时间
        if valid_tokens:
            avg_remaining_seconds = sum(
                self.tokens[t]["expire_at"] - now
                for t in valid_tokens
            ) / len(valid_tokens)
            avg_remaining_hours = avg_remaining_seconds / 3600
        else:
            avg_remaining_hours = 0
        
        return {
            "total_tokens": len(self.tokens),
            "valid_tokens": len(valid_tokens),
            "expired_tokens": len(expired_tokens),
            "avg_remaining_hours": round(avg_remaining_hours, 2),
            "token_expire_hours": self.token_expire_hours
        }
    
    def get_all_tokens(self) -> Dict[str, Dict]:
        """
        获取所有Token信息（用于调试）
        
        Returns:
            Token字典
        """
        now = time.time()
        return {
            token: {
                "image_name": data["image_name"],
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data["created_at"])),
                "expire_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data["expire_at"])),
                "is_expired": data["expire_at"] < now,
                "remaining_seconds": max(0, int(data["expire_at"] - now))
            }
            for token, data in self.tokens.items()
        }


# 创建全局实例
image_token_manager = ImageTokenManager(token_expire_hours=2)
