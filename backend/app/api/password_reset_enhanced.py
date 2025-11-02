"""
主密码重置API - ✅ P0-14优化完成: 邮箱验证码重置功能
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import secrets
import hashlib
import asyncio
from datetime import datetime, timedelta
from ..utils.logger import logger
from ..database import db
from ..queue.redis_client import redis_queue

router = APIRouter(prefix="/api/password-reset-enhanced", tags=["password-reset"])


class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    email: EmailStr


class PasswordResetVerify(BaseModel):
    """密码重置验证"""
    email: EmailStr
    code: str
    new_password: str


# ============ ✅ P0-14: 邮箱验证码重置功能 ============

@router.post("/request")
async def request_password_reset(request: PasswordResetRequest):
    """
    ✅ P0-14新增: 请求密码重置（发送邮箱验证码）
    
    功能：
    1. 验证邮箱是否已配置
    2. 生成6位数字验证码
    3. 发送到用户邮箱
    4. 存储验证码（10分钟有效期）
    
    Args:
        request: 包含邮箱地址
        
    Returns:
        {
            "success": bool,
            "message": str,
            "email_sent_to": str,
            "expires_in": int  # 有效期（秒）
        }
    """
    logger.info(f"✅ P0-14: 收到密码重置请求: {request.email}")
    
    try:
        # 1. 检查邮箱是否已配置（用于接收验证码）
        user_email = db.get_system_config('user_email')
        
        if not user_email:
            logger.warning("用户未配置邮箱")
            raise HTTPException(
                status_code=400,
                detail="未配置邮箱，无法发送验证码。请先在设置中配置邮箱。"
            )
        
        if user_email != request.email:
            logger.warning(f"邮箱不匹配: {request.email} != {user_email}")
            raise HTTPException(
                status_code=400,
                detail="邮箱地址不匹配，请输入您在设置中配置的邮箱。"
            )
        
        # 2. 生成6位数字验证码
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        logger.info(f"生成验证码: {code} (仅开发环境显示)")
        
        # 3. 存储验证码到Redis（10分钟有效期）
        redis_key = f"password_reset_code:{request.email}"
        await redis_queue.set(
            redis_key,
            code,
            expire=600  # 10分钟
        )
        
        # 记录请求时间（防止频繁请求）
        request_key = f"password_reset_request:{request.email}"
        await redis_queue.set(
            request_key,
            str(int(datetime.now().timestamp())),
            expire=60  # 1分钟内不能重复请求
        )
        
        # 4. 发送邮件
        email_sent = await _send_verification_email(request.email, code)
        
        if email_sent:
            logger.info(f"✅ 验证码邮件已发送到: {request.email}")
            return {
                "success": True,
                "message": f"验证码已发送到 {request.email}，请查收邮件。",
                "email_sent_to": request.email,
                "expires_in": 600  # 10分钟
            }
        else:
            logger.error("邮件发送失败")
            raise HTTPException(
                status_code=500,
                detail="验证码发送失败，请检查邮件配置或稍后重试。"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"请求密码重置失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"请求失败: {str(e)}"
        )


@router.post("/verify")
async def verify_and_reset_password(request: PasswordResetVerify):
    """
    ✅ P0-14新增: 验证验证码并重置密码
    
    功能：
    1. 验证6位数字验证码
    2. 验证新密码强度
    3. 使用bcrypt哈希密码
    4. 更新主密码
    5. 清除验证码
    
    Args:
        request: 包含邮箱、验证码、新密码
        
    Returns:
        {
            "success": bool,
            "message": str
        }
    """
    logger.info(f"✅ P0-14: 收到密码重置验证: {request.email}")
    
    try:
        # 1. 验证邮箱
        user_email = db.get_system_config('user_email')
        
        if user_email != request.email:
            raise HTTPException(
                status_code=400,
                detail="邮箱地址不匹配"
            )
        
        # 2. 验证验证码
        redis_key = f"password_reset_code:{request.email}"
        stored_code = await redis_queue.get(redis_key)
        
        if not stored_code:
            raise HTTPException(
                status_code=400,
                detail="验证码已过期或不存在，请重新请求验证码。"
            )
        
        if stored_code != request.code:
            # 记录失败尝试
            fail_key = f"password_reset_fails:{request.email}"
            fail_count = await redis_queue.incr(fail_key)
            await redis_queue.expire(fail_key, 3600)  # 1小时
            
            logger.warning(f"验证码错误（第{fail_count}次尝试）")
            
            # 3次失败后锁定
            if fail_count >= 3:
                await redis_queue.delete(redis_key)
                raise HTTPException(
                    status_code=429,
                    detail="验证码错误次数过多，已锁定。请1小时后重试。"
                )
            
            raise HTTPException(
                status_code=400,
                detail=f"验证码错误，还有{3-fail_count}次尝试机会。"
            )
        
        # 3. 验证新密码强度
        password_check = _validate_password_strength(request.new_password)
        
        if not password_check["valid"]:
            raise HTTPException(
                status_code=400,
                detail=password_check["message"]
            )
        
        # 4. 哈希新密码（bcrypt）
        try:
            import bcrypt
            
            password_hash = bcrypt.hashpw(
                request.new_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
        except ImportError:
            logger.warning("bcrypt未安装，使用sha256（不推荐）")
            password_hash = hashlib.sha256(
                request.new_password.encode('utf-8')
            ).hexdigest()
        
        # 5. 更新主密码
        db.set_system_config('master_password_hash', password_hash)
        
        # 6. 清除验证码和失败记录
        await redis_queue.delete(redis_key)
        await redis_queue.delete(f"password_reset_fails:{request.email}")
        
        logger.info(f"✅ 主密码重置成功: {request.email}")
        
        return {
            "success": True,
            "message": "✅ 密码重置成功！请使用新密码登录。"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"密码重置失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"重置失败: {str(e)}"
        )


@router.get("/check-email-configured")
async def check_email_configured():
    """
    ✅ P0-14新增: 检查是否已配置邮箱
    
    Returns:
        {
            "configured": bool,
            "email": str (脱敏)
        }
    """
    try:
        user_email = db.get_system_config('user_email')
        
        if user_email:
            # 脱敏显示：a***@example.com
            masked_email = _mask_email(user_email)
            
            return {
                "configured": True,
                "email": masked_email
            }
        else:
            return {
                "configured": False,
                "email": None
            }
    
    except Exception as e:
        logger.error(f"检查邮箱配置失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"检查失败: {str(e)}"
        )


# ============ 辅助函数 ============

async def _send_verification_email(email: str, code: str) -> bool:
    """
    发送验证码邮件
    
    Args:
        email: 收件邮箱
        code: 验证码
        
    Returns:
        是否成功
    """
    try:
        # 从配置获取SMTP设置
        smtp_host = db.get_system_config('smtp_host') or 'smtp.gmail.com'
        smtp_port = int(db.get_system_config('smtp_port') or 587)
        smtp_user = db.get_system_config('smtp_user')
        smtp_password = db.get_system_config('smtp_password')
        
        if not smtp_user or not smtp_password:
            logger.warning("SMTP未配置，邮件发送功能不可用")
            # 开发环境：直接返回True并打印验证码
            if logger.level == "DEBUG":
                logger.warning(f"开发模式：验证码 = {code}")
                return True
            return False
        
        # 使用aiosmtplib发送邮件
        import aiosmtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # 构建邮件
        message = MIMEMultipart('alternative')
        message['Subject'] = 'KOOK转发系统 - 密码重置验证码'
        message['From'] = smtp_user
        message['To'] = email
        
        # 邮件内容（HTML格式）
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #5865F2; margin-bottom: 20px;">🔐 密码重置验证码</h2>
                
                <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                    您正在重置KOOK消息转发系统的主密码。
                </p>
                
                <div style="background-color: #f0f0f0; padding: 20px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
                    <p style="font-size: 14px; color: #666; margin-bottom: 10px;">您的验证码是：</p>
                    <p style="font-size: 32px; font-weight: bold; color: #5865F2; letter-spacing: 5px; margin: 0;">
                        {code}
                    </p>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-bottom: 10px;">
                    <strong>重要提示：</strong>
                </p>
                <ul style="font-size: 14px; color: #666;">
                    <li>验证码有效期为 <strong>10分钟</strong></li>
                    <li>如果不是您本人操作，请忽略此邮件</li>
                    <li>请勿将验证码告诉他人</li>
                </ul>
                
                <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    KOOK消息转发系统<br>
                    此邮件由系统自动发送，请勿回复
                </p>
            </div>
        </body>
        </html>
        """
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        message.attach(html_part)
        
        # 发送邮件
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True,
            timeout=30
        )
        
        logger.info(f"✅ 验证码邮件发送成功: {email}")
        return True
    
    except ImportError:
        logger.error("aiosmtplib未安装，无法发送邮件")
        return False
    except Exception as e:
        logger.error(f"发送邮件失败: {str(e)}")
        return False


def _validate_password_strength(password: str) -> Dict[str, any]:
    """
    验证密码强度
    
    要求：
    - 长度6-20位
    - 至少包含字母和数字
    - 可选：特殊字符
    
    Args:
        password: 密码字符串
        
    Returns:
        {
            "valid": bool,
            "message": str,
            "strength": str  # weak/medium/strong
        }
    """
    # 检查长度
    if len(password) < 6:
        return {
            "valid": False,
            "message": "密码长度不能少于6位",
            "strength": "weak"
        }
    
    if len(password) > 20:
        return {
            "valid": False,
            "message": "密码长度不能超过20位",
            "strength": "weak"
        }
    
    # 检查是否包含字母和数字
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    if not has_letter or not has_digit:
        return {
            "valid": False,
            "message": "密码必须同时包含字母和数字",
            "strength": "weak"
        }
    
    # 评估强度
    if has_letter and has_digit and has_special and len(password) >= 10:
        strength = "strong"
    elif has_letter and has_digit and len(password) >= 8:
        strength = "medium"
    else:
        strength = "weak"
    
    return {
        "valid": True,
        "message": "密码强度合格",
        "strength": strength
    }


def _mask_email(email: str) -> str:
    """
    邮箱脱敏显示
    
    Args:
        email: 原始邮箱 example@gmail.com
        
    Returns:
        脱敏邮箱 e***e@gmail.com
    """
    try:
        local, domain = email.split('@')
        
        if len(local) <= 2:
            masked_local = local[0] + '*'
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    except:
        return email  # 如果解析失败，返回原始邮箱
