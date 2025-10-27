"""
API认证工具
"""
import secrets
from fastapi import Header, HTTPException, status
from typing import Optional
from ..config import settings
from .logger import logger


def generate_api_token() -> str:
    """
    生成随机API Token
    
    Returns:
        64字符的随机Token
    """
    return secrets.token_urlsafe(48)


async def verify_api_token(x_api_token: Optional[str] = Header(None)) -> str:
    """
    验证API Token（FastAPI依赖注入）
    
    Args:
        x_api_token: 请求头中的Token
        
    Returns:
        Token字符串（验证通过）
        
    Raises:
        HTTPException: Token无效或缺失
    """
    # 如果未配置API Token，则不启用认证
    if not settings.api_token:
        logger.debug("API认证未启用（未配置API_TOKEN）")
        return "no-auth"
    
    # 检查Token是否提供
    if not x_api_token:
        logger.warning("API请求缺少Token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证Token
    if x_api_token != settings.api_token:
        logger.warning(f"API Token验证失败: {x_api_token[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug("API Token验证通过")
    return x_api_token


async def optional_api_token(x_api_token: Optional[str] = Header(None)) -> Optional[str]:
    """
    可选的API Token验证（不强制要求）
    
    Args:
        x_api_token: 请求头中的Token
        
    Returns:
        Token字符串或None
    """
    # 如果未配置API Token，直接返回
    if not settings.api_token:
        return None
    
    # 如果提供了Token，则验证
    if x_api_token:
        if x_api_token != settings.api_token:
            logger.warning(f"可选API Token验证失败: {x_api_token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.debug("可选API Token验证通过")
        return x_api_token
    
    return None
