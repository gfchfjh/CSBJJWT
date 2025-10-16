"""
认证相关API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..utils.auth import generate_api_token
from ..utils.crypto import verify_password, hash_password
from ..database import db
from ..utils.logger import logger
from ..config import settings


router = APIRouter(prefix="/api/auth", tags=["认证"])


class TokenResponse(BaseModel):
    """Token响应"""
    token: str
    message: str


@router.get("/generate-token", response_model=TokenResponse)
async def generate_new_token():
    """
    生成新的API Token（仅开发环境）
    
    Returns:
        新生成的Token
    """
    if not settings.debug:
        raise HTTPException(status_code=403, detail="仅开发环境可用")
    
    new_token = generate_api_token()
    logger.info(f"生成新Token: {new_token[:10]}...")
    
    return TokenResponse(
        token=new_token,
        message=f"请将以下内容添加到.env文件：\nAPI_TOKEN={new_token}"
    )


@router.get("/check")
async def check_auth_status():
    """
    检查认证状态
    
    Returns:
        认证配置信息
    """
    return {
        "enabled": bool(settings.api_token),
        "token_header": settings.api_token_header,
        "message": "API认证已启用" if settings.api_token else "API认证未启用（建议启用）"
    }


class PasswordVerifyRequest(BaseModel):
    """密码验证请求"""
    password: str


class PasswordVerifyResponse(BaseModel):
    """密码验证响应"""
    success: bool
    message: str


@router.post("/verify-password", response_model=PasswordVerifyResponse)
async def verify_app_password(request: PasswordVerifyRequest):
    """
    验证应用密码
    
    Args:
        request: 密码验证请求
        
    Returns:
        验证结果
    """
    # 检查是否启用密码保护
    if not settings.require_password:
        return PasswordVerifyResponse(
            success=False,
            message="密码保护未启用"
        )
    
    try:
        # 从数据库获取密码哈希
        password_hash = db.get_system_config('app_password_hash')
        
        if not password_hash:
            # 首次设置密码
            logger.info("首次设置应用密码")
            hashed = hash_password(request.password)
            db.set_system_config('app_password_hash', hashed)
            return PasswordVerifyResponse(
                success=True,
                message="密码已设置"
            )
        
        # 验证密码
        if verify_password(request.password, password_hash):
            logger.info("应用密码验证成功")
            return PasswordVerifyResponse(
                success=True,
                message="密码正确"
            )
        else:
            logger.warning("应用密码验证失败")
            return PasswordVerifyResponse(
                success=False,
                message="密码错误"
            )
            
    except Exception as e:
        logger.error(f"密码验证异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str


@router.post("/change-password")
async def change_app_password(request: PasswordChangeRequest):
    """
    修改应用密码
    
    Args:
        request: 修改密码请求
        
    Returns:
        修改结果
    """
    try:
        # 验证旧密码
        password_hash = db.get_system_config('app_password_hash')
        
        if not password_hash:
            raise HTTPException(status_code=404, detail="未设置密码")
        
        if not verify_password(request.old_password, password_hash):
            raise HTTPException(status_code=401, detail="旧密码错误")
        
        # 设置新密码
        new_hash = hash_password(request.new_password)
        db.set_system_config('app_password_hash', new_hash)
        
        logger.info("应用密码已修改")
        return {"success": True, "message": "密码修改成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/password-exists")
async def check_password_exists():
    """
    检查应用密码是否已设置
    
    Returns:
        密码存在状态
    """
    password_hash = db.get_system_config('app_password_hash')
    return {
        "exists": bool(password_hash),
        "message": "密码已设置" if password_hash else "未设置密码"
    }


class PasswordSetRequest(BaseModel):
    """设置密码请求"""
    password: str


@router.post("/set-password")
async def set_app_password(request: PasswordSetRequest):
    """
    设置应用密码（首次使用）
    
    Args:
        request: 密码设置请求
        
    Returns:
        设置结果
    """
    try:
        # 检查是否已设置
        password_hash = db.get_system_config('app_password_hash')
        if password_hash:
            raise HTTPException(status_code=400, detail="密码已设置，请使用修改密码功能")
        
        # 验证密码长度
        if len(request.password) < 6 or len(request.password) > 20:
            raise HTTPException(status_code=400, detail="密码长度必须在6-20位之间")
        
        # 设置密码
        hashed = hash_password(request.password)
        db.set_system_config('app_password_hash', hashed)
        
        logger.info("应用密码已设置")
        return {"success": True, "message": "密码设置成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置密码异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-password")
async def reset_app_password():
    """
    重置应用密码（危险操作，将清空所有配置）
    
    Returns:
        重置结果
    """
    try:
        # 删除密码哈希
        db.delete_system_config('app_password_hash')
        
        # 清空其他敏感配置（可选）
        # 注意：这里可以根据需要决定是否清空其他数据
        logger.warning("应用密码已重置！")
        
        return {
            "success": True,
            "message": "密码已重置，请重新设置"
        }
        
    except Exception as e:
        logger.error(f"重置密码异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
