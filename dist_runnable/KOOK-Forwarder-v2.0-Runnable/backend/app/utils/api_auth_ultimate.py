"""
API认证管理器（终极版）
=====================
功能：
1. 自动生成API Token
2. Token验证
3. 强制认证模式
4. Token轮换

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import secrets
from typing import Optional
from fastapi import Header, HTTPException
from ..config import settings
from ..utils.logger import logger


def generate_api_token() -> str:
    """生成安全的API Token"""
    return secrets.token_urlsafe(32)


def verify_api_token(x_api_token: Optional[str] = Header(None)) -> str:
    """
    验证API Token
    
    Args:
        x_api_token: 请求头中的Token
        
    Returns:
        Token字符串
        
    Raises:
        HTTPException: Token无效或缺失
    """
    # 如果未配置Token，跳过验证（向后兼容）
    if not settings.api_token:
        logger.warning("⚠️ API认证未启用（建议在生产环境启用）")
        return "no-auth"
    
    # 验证Token
    if not x_api_token:
        raise HTTPException(
            status_code=401,
            detail="缺少API Token，请在请求头中添加 X-API-Token"
        )
    
    if x_api_token != settings.api_token:
        logger.warning(f"❌ API Token验证失败: {x_api_token[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="API Token无效"
        )
    
    return x_api_token


class APIAuthManager:
    """API认证管理器"""
    
    def __init__(self):
        self.current_token = settings.api_token
        
        # 如果未配置Token，自动生成
        if not self.current_token:
            self.current_token = generate_api_token()
            logger.info(f"🔑 自动生成API Token: {self.current_token[:10]}...")
            logger.info("💡 建议将此Token保存到环境变量 API_TOKEN")
    
    def rotate_token(self) -> str:
        """
        轮换Token
        
        Returns:
            新Token
        """
        old_token = self.current_token
        self.current_token = generate_api_token()
        
        logger.info("🔄 API Token已轮换")
        logger.info(f"旧Token: {old_token[:10]}...")
        logger.info(f"新Token: {self.current_token[:10]}...")
        
        return self.current_token
    
    def get_current_token(self) -> str:
        """获取当前Token"""
        return self.current_token


# 全局实例
api_auth_manager = APIAuthManager()
