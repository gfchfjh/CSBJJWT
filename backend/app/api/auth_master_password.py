"""
主密码认证API
✅ P0-8优化：主密码管理接口
"""
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from ..utils.master_password import master_password_manager
from ..utils.logger import logger


router = APIRouter(prefix="/api/auth", tags=["auth"])


class SetMasterPasswordRequest(BaseModel):
    """设置主密码请求"""
    password: str


class UnlockRequest(BaseModel):
    """解锁请求"""
    password: str
    remember_days: int = 0  # 0表示24小时


class ChangeMasterPasswordRequest(BaseModel):
    """修改主密码请求"""
    old_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    email: str
    verification_code: str


@router.post("/set-master-password")
async def set_master_password(request: SetMasterPasswordRequest):
    """
    设置主密码（仅在未设置时可用）
    """
    # 检查是否已设置
    if master_password_manager.is_password_set():
        raise HTTPException(
            status_code=400,
            detail="主密码已设置，请使用修改密码接口"
        )
    
    success, message = master_password_manager.set_password(request.password)
    
    if success:
        return {
            "success": True,
            "message": message
        }
    else:
        raise HTTPException(status_code=400, detail=message)


@router.post("/unlock")
async def unlock(request: UnlockRequest, response: Response):
    """
    解锁应用
    
    Returns:
        Token（也会设置到Cookie）
    """
    token = master_password_manager.unlock(
        request.password,
        request.remember_days
    )
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="密码错误"
        )
    
    # 设置Cookie
    max_age = request.remember_days * 86400 if request.remember_days > 0 else 86400
    response.set_cookie(
        key="master_token",
        value=token,
        max_age=max_age,
        httponly=True,
        secure=False,  # 本地开发时用False，生产环境应该用True
        samesite="lax"
    )
    
    return {
        "success": True,
        "token": token,
        "message": "解锁成功"
    }


@router.post("/logout")
async def logout(response: Response, token: Optional[str] = None):
    """
    登出（撤销Token）
    """
    if token:
        master_password_manager.revoke_token(token)
    
    # 清除Cookie
    response.delete_cookie("master_token")
    
    return {
        "success": True,
        "message": "已登出"
    }


@router.post("/change-master-password")
async def change_master_password(request: ChangeMasterPasswordRequest):
    """
    修改主密码
    """
    success, message = master_password_manager.change_password(
        request.old_password,
        request.new_password
    )
    
    if success:
        # 撤销所有Token，要求重新登录
        master_password_manager.revoke_all_tokens()
        
        return {
            "success": True,
            "message": "密码已修改，请重新登录"
        }
    else:
        raise HTTPException(status_code=400, detail=message)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    通过邮箱验证重置密码
    """
    success, message = master_password_manager.reset_password_with_email(
        request.email,
        request.verification_code
    )
    
    if success:
        return {
            "success": True,
            "temporary_password": message,
            "message": "密码已重置，请使用临时密码登录并尽快修改"
        }
    else:
        raise HTTPException(status_code=400, detail=message)


@router.get("/master-password-status")
async def get_master_password_status():
    """
    获取主密码状态
    """
    stats = master_password_manager.get_stats()
    
    return {
        "password_set": stats["password_set"],
        "active_sessions": stats["active_tokens"]
    }


@router.delete("/delete-master-password")
async def delete_master_password(password: str):
    """
    删除主密码（危险操作！）
    """
    # 验证密码
    if not master_password_manager.verify_password(password):
        raise HTTPException(status_code=401, detail="密码错误")
    
    success = master_password_manager.delete_password()
    
    if success:
        return {
            "success": True,
            "message": "主密码已删除"
        }
    else:
        raise HTTPException(status_code=500, detail="删除失败")
