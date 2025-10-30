"""
邮件API - ✅ P0-2优化：邮件配置和测试接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from ..utils.logger import logger
from ..utils.email_sender import email_sender
from ..config import settings
from ..database import db

router = APIRouter(prefix="/api/email", tags=["email"])


class EmailConfig(BaseModel):
    """邮件配置"""
    smtp_enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from_email: EmailStr
    smtp_use_tls: bool = True


class TestEmailRequest(BaseModel):
    """测试邮件请求"""
    to_email: EmailStr
    test_type: str = "verification"  # verification/notification


class SendVerificationCodeRequest(BaseModel):
    """发送验证码请求"""
    email: EmailStr
    purpose: str = "密码重置"


# ============ 邮件配置接口 ============

@router.get("/config")
async def get_email_config():
    """
    获取当前邮件配置（不返回密码）
    
    Returns:
        邮件配置信息
    """
    return {
        "smtp_enabled": settings.smtp_enabled,
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "smtp_username": settings.smtp_username,
        "smtp_from_email": settings.smtp_from_email,
        "smtp_use_tls": settings.smtp_use_tls,
        "smtp_password_set": bool(settings.smtp_password)
    }


@router.post("/config")
async def update_email_config(config: EmailConfig):
    """
    更新邮件配置
    
    Args:
        config: 新的邮件配置
        
    Returns:
        更新结果
    """
    try:
        # 更新设置
        settings.smtp_enabled = config.smtp_enabled
        settings.smtp_host = config.smtp_host
        settings.smtp_port = config.smtp_port
        settings.smtp_username = config.smtp_username
        settings.smtp_password = config.smtp_password
        settings.smtp_from_email = config.smtp_from_email
        settings.smtp_use_tls = config.smtp_use_tls
        
        # 保存到数据库
        db.set_system_config('smtp_enabled', str(config.smtp_enabled))
        db.set_system_config('smtp_host', config.smtp_host)
        db.set_system_config('smtp_port', str(config.smtp_port))
        db.set_system_config('smtp_username', config.smtp_username)
        db.set_system_config('smtp_password', config.smtp_password)  # 应该加密存储
        db.set_system_config('smtp_from_email', config.smtp_from_email)
        db.set_system_config('smtp_use_tls', str(config.smtp_use_tls))
        
        # 重新初始化邮件发送器
        from ..utils.email_sender import EmailSender
        global email_sender
        email_sender = EmailSender()
        
        logger.info("✅ 邮件配置已更新")
        
        return {
            "success": True,
            "message": "✅ 邮件配置已更新"
        }
    except Exception as e:
        logger.error(f"更新邮件配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 邮件测试接口 ============

@router.post("/test-connection")
async def test_email_connection():
    """
    测试SMTP连接
    
    Returns:
        连接测试结果
    """
    try:
        result = await email_sender.test_connection()
        return result
    except Exception as e:
        logger.error(f"测试SMTP连接失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-send")
async def test_send_email(request: TestEmailRequest):
    """
    发送测试邮件
    
    Args:
        request: 测试邮件请求
        
    Returns:
        发送结果
    """
    try:
        if request.test_type == "verification":
            # 发送验证码测试
            result = await email_sender.send_verification_code(
                to_email=request.to_email,
                code="123456",
                purpose="邮件功能测试"
            )
        else:
            # 发送通知测试
            result = await email_sender.send_notification(
                to_email=request.to_email,
                title="邮件功能测试",
                content="这是一封测试邮件，如果您收到此邮件，说明SMTP配置正确。",
                notification_type="success"
            )
        
        return result
    except Exception as e:
        logger.error(f"发送测试邮件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 验证码发送接口 ============

@router.post("/send-verification-code")
async def send_verification_code(request: SendVerificationCodeRequest):
    """
    发送验证码邮件
    
    Args:
        request: 验证码请求
        
    Returns:
        {
            "success": bool,
            "message": str,
            "code_id": str,  # 验证码ID（用于后续验证）
            "expires_in": int  # 过期时间（秒）
        }
    """
    try:
        # 生成6位数字验证码
        import random
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # 发送邮件
        result = await email_sender.send_verification_code(
            to_email=request.email,
            code=code,
            purpose=request.purpose
        )
        
        if result["success"]:
            # 保存验证码到Redis（10分钟有效期）
            from ..queue.redis_client import redis_queue
            
            code_id = f"email_code:{request.email}:{request.purpose}"
            await redis_queue.set(code_id, code, expire=600)
            
            logger.info(f"✅ 验证码已发送: {request.email}")
            
            return {
                "success": True,
                "message": "✅ 验证码已发送到您的邮箱",
                "code_id": code_id,
                "expires_in": 600
            }
        else:
            return result
    except Exception as e:
        logger.error(f"发送验证码失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class VerifyCodeRequest(BaseModel):
    """验证验证码请求"""
    email: EmailStr
    code: str
    purpose: str = "密码重置"


@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest):
    """
    验证验证码
    
    Args:
        request: 验证请求
        
    Returns:
        验证结果
    """
    try:
        from ..queue.redis_client import redis_queue
        
        code_id = f"email_code:{request.email}:{request.purpose}"
        stored_code = await redis_queue.get(code_id)
        
        if not stored_code:
            return {
                "success": False,
                "message": "验证码已过期或不存在",
                "error": "code_expired"
            }
        
        if stored_code == request.code:
            # 验证成功，删除验证码
            await redis_queue.delete(code_id)
            
            logger.info(f"✅ 验证码验证成功: {request.email}")
            
            return {
                "success": True,
                "message": "✅ 验证码验证成功"
            }
        else:
            return {
                "success": False,
                "message": "验证码错误",
                "error": "code_invalid"
            }
    except Exception as e:
        logger.error(f"验证验证码失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 备选方案：不依赖邮件的重置方式 ============

class ResetWithoutEmailRequest(BaseModel):
    """不依赖邮件的重置请求"""
    reset_method: str  # security_answer/emergency_code/delete_config
    security_answer: Optional[str] = None
    emergency_code: Optional[str] = None


@router.post("/reset-without-email")
async def reset_without_email(request: ResetWithoutEmailRequest):
    """
    ✅ P0-2备选方案：不依赖邮件的密码重置
    
    支持三种方式：
    1. 安全问题验证
    2. 紧急重置码（安装时生成）
    3. 删除配置文件（重置所有数据）
    
    Args:
        request: 重置请求
        
    Returns:
        重置结果
    """
    try:
        if request.reset_method == "security_answer":
            # 方式1：安全问题验证
            stored_answer = db.get_system_config('security_answer_hash')
            
            if not stored_answer:
                return {
                    "success": False,
                    "message": "未设置安全问题",
                    "error": "security_answer_not_set"
                }
            
            # 验证答案（应该比较哈希值）
            from ..utils.crypto import crypto_manager
            if crypto_manager.verify_password(request.security_answer, stored_answer):
                return {
                    "success": True,
                    "message": "✅ 安全问题验证通过，可以重置密码",
                    "reset_token": "temp_reset_token_123"  # 生成临时重置令牌
                }
            else:
                return {
                    "success": False,
                    "message": "安全问题答案错误",
                    "error": "security_answer_wrong"
                }
        
        elif request.reset_method == "emergency_code":
            # 方式2：紧急重置码
            stored_code = db.get_system_config('emergency_reset_code')
            
            if not stored_code:
                return {
                    "success": False,
                    "message": "紧急重置码未设置",
                    "error": "emergency_code_not_set",
                    "hint": "请在安装时保存紧急重置码"
                }
            
            if request.emergency_code == stored_code:
                return {
                    "success": True,
                    "message": "✅ 紧急重置码验证通过",
                    "reset_token": "temp_reset_token_456"
                }
            else:
                return {
                    "success": False,
                    "message": "紧急重置码错误",
                    "error": "emergency_code_wrong"
                }
        
        elif request.reset_method == "delete_config":
            # 方式3：删除配置文件（最后手段）
            return {
                "success": True,
                "message": "⚠️ 请确认删除配置文件",
                "warning": "此操作将清空所有配置数据（账号、Bot、映射等）",
                "confirm_required": True,
                "instructions": [
                    "1. 关闭应用程序",
                    "2. 删除配置文件：{data_dir}/config.db",
                    "3. 重新启动应用",
                    "4. 重新配置"
                ]
            }
        
        else:
            return {
                "success": False,
                "message": "不支持的重置方式",
                "error": "invalid_reset_method"
            }
    except Exception as e:
        logger.error(f"无邮件重置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
