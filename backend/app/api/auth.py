"""
认证相关API
包括登录、登出、修改密码等
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional
from ..utils.password_manager import password_manager
from ..utils.logger import logger

router = APIRouter(prefix="/auth", tags=["认证"])


class SetPasswordRequest(BaseModel):
    """设置密码请求"""
    password: str = Field(..., min_length=6, max_length=20, description="密码（6-20位）")


class LoginRequest(BaseModel):
    """登录请求"""
    password: str = Field(..., description="密码")
    remember: bool = Field(False, description="记住密码（30天）")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码（6-20位）")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    verification_code: str = Field(..., description="验证码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码（6-20位）")


@router.get("/status")
async def get_auth_status():
    """
    获取认证状态
    
    Returns:
        是否已设置密码
    """
    return {
        "password_set": password_manager.is_password_set()
    }


@router.post("/setup")
async def setup_password(request: SetPasswordRequest):
    """
    首次设置密码
    
    Args:
        request: 设置密码请求
        
    Returns:
        设置结果
    """
    try:
        # 检查是否已设置密码
        if password_manager.is_password_set():
            raise HTTPException(status_code=400, detail="密码已设置，请使用修改密码功能")
        
        # 设置密码
        if password_manager.set_password(request.password):
            logger.info("首次设置密码成功")
            return {
                "success": True,
                "message": "密码设置成功"
            }
        else:
            raise HTTPException(status_code=500, detail="密码设置失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置密码异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(request: LoginRequest):
    """
    登录验证
    
    Args:
        request: 登录请求
        
    Returns:
        Token
    """
    try:
        # 验证密码
        if not password_manager.verify_password(request.password):
            raise HTTPException(status_code=401, detail="密码错误")
        
        # 生成Token
        token = password_manager.generate_token()
        
        logger.info("登录成功")
        return {
            "success": True,
            "message": "登录成功",
            "token": token,
            "remember": request.remember
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """
    登出
    
    Args:
        authorization: Authorization头（Bearer token）
    """
    try:
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:]
            password_manager.invalidate_token(token)
        
        logger.info("登出成功")
        return {
            "success": True,
            "message": "登出成功"
        }
        
    except Exception as e:
        logger.error(f"登出异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-token")
async def verify_token(authorization: Optional[str] = Header(None)):
    """
    验证Token
    
    Args:
        authorization: Authorization头（Bearer token）
        
    Returns:
        验证结果
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="未提供Token")
        
        token = authorization[7:]
        
        if password_manager.verify_token(token):
            return {
                "valid": True,
                "message": "Token有效"
            }
        else:
            raise HTTPException(status_code=401, detail="Token无效或已过期")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证Token异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    authorization: Optional[str] = Header(None)
):
    """
    修改密码
    
    Args:
        request: 修改密码请求
        authorization: Authorization头（Bearer token）
        
    Returns:
        修改结果
    """
    try:
        # 验证Token
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="未登录")
        
        token = authorization[7:]
        if not password_manager.verify_token(token):
            raise HTTPException(status_code=401, detail="Token无效或已过期")
        
        # 修改密码
        success, message = password_manager.change_password(
            request.old_password,
            request.new_password
        )
        
        if success:
            logger.info("密码修改成功")
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    重置密码（通过验证码）
    
    Args:
        request: 重置密码请求
        
    Returns:
        重置结果
    """
    try:
        success, message = password_manager.reset_password_with_verification(
            request.verification_code,
            request.new_password
        )
        
        if success:
            logger.info("密码重置成功")
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重置密码异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
