"""
密码重置API
支持通过邮箱验证码重置密码
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from ..database import db
from ..utils.logger import logger
from ..utils.verification_code import verification_manager
from ..utils.email_sender import email_sender
from ..utils.crypto import encrypt_password
import json

router = APIRouter(prefix="/api/password-reset", tags=["auth"])


class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    email: EmailStr = Field(..., description="邮箱地址")


class VerifyCodeRequest(BaseModel):
    """验证验证码请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")


@router.post("/send-code")
async def send_verification_code(request: SendCodeRequest):
    """
    发送密码重置验证码到邮箱
    
    Args:
        request: 包含邮箱地址的请求
        
    Returns:
        操作结果
    """
    try:
        # 检查邮箱是否存在（系统管理员邮箱或KOOK账号邮箱）
        account = db.get_account_by_email(request.email)
        
        # 检查系统配置中是否有管理员邮箱
        admin_email = db.get_system_config('admin_email')
        
        if not account and admin_email != request.email:
            # 为了安全，不透露邮箱是否存在
            logger.warning(f"尝试重置不存在的邮箱密码: {request.email}")
            # 仍然返回成功，防止邮箱枚举攻击
            return {
                "success": True,
                "message": "如果该邮箱已注册，验证码将发送到您的邮箱"
            }
        
        # 生成验证码
        code = verification_manager.generate_code(request.email, purpose='password_reset')
        
        # 构建邮件内容
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 30px; background: white; border: 1px solid #e0e0e0; }}
                .code-box {{ background: #f8f9fa; padding: 20px; border-radius: 5px; 
                            text-align: center; margin: 20px 0; }}
                .code {{ font-size: 32px; font-weight: bold; letter-spacing: 5px; 
                        color: #667eea; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; 
                           padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                h2 {{ margin: 0; font-size: 24px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔐 密码重置验证码</h2>
                </div>
                <div class="content">
                    <p>您好，</p>
                    <p>您正在重置 <strong>KOOK消息转发系统</strong> 的密码。</p>
                    
                    <div class="code-box">
                        <p style="margin: 0; font-size: 14px; color: #666;">您的验证码是：</p>
                        <p class="code">{code}</p>
                    </div>
                    
                    <p>验证码有效期为 <strong>10分钟</strong>，请尽快使用。</p>
                    
                    <div class="warning">
                        <p style="margin: 0;"><strong>⚠️ 安全提示：</strong></p>
                        <ul style="margin: 10px 0 0 0;">
                            <li>如果您未请求密码重置，请忽略此邮件</li>
                            <li>请勿将验证码告知他人</li>
                            <li>系统不会主动索要您的密码或验证码</li>
                        </ul>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">
                        如有疑问，请联系系统管理员。
                    </p>
                </div>
                <div class="footer">
                    <p>来自 <strong>KOOK消息转发系统</strong></p>
                    <p>发送时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 发送邮件
        success = await email_sender.send_email(
            subject="[KOOK转发系统] 密码重置验证码",
            body=html_body,
            to_emails=[request.email],
            html=True
        )
        
        if success:
            logger.info(f"✅ 密码重置验证码已发送到: {request.email}")
            return {
                "success": True,
                "message": "验证码已发送到您的邮箱，请查收（有效期10分钟）"
            }
        else:
            # 验证码发送失败，使验证码失效
            verification_manager.invalidate_code(request.email)
            logger.error(f"❌ 验证码邮件发送失败: {request.email}")
            raise HTTPException(
                status_code=500,
                detail="验证码发送失败，请检查邮件配置或稍后重试"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送验证码异常: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器错误，请稍后重试")


@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest):
    """
    验证验证码是否正确
    
    Args:
        request: 包含邮箱和验证码的请求
        
    Returns:
        验证结果
    """
    try:
        success, message = verification_manager.verify_code(
            request.email,
            request.code,
            purpose='password_reset'
        )
        
        if success:
            # 验证成功，重新生成一个短期令牌用于密码重置
            # 这个令牌只在verify成功后重新生成，防止直接调用reset接口
            reset_token = verification_manager.generate_code(
                request.email,
                purpose='password_reset_confirmed'
            )
            
            return {
                "success": True,
                "message": "验证成功，请在5分钟内完成密码重置",
                "reset_token": reset_token
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证验证码异常: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器错误，请稍后重试")


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    重置密码
    
    Args:
        request: 包含邮箱、验证码和新密码的请求
        
    Returns:
        操作结果
    """
    try:
        # 验证验证码（使用confirmed状态的令牌）
        success, message = verification_manager.verify_code(
            request.email,
            request.code,
            purpose='password_reset_confirmed'
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="验证码无效或已过期，请重新获取验证码"
            )
        
        # 更新密码
        # 1. 检查是否是系统管理员密码
        admin_email = db.get_system_config('admin_email')
        if admin_email == request.email:
            # 更新系统管理员密码
            encrypted_password = encrypt_password(request.new_password)
            db.set_system_config('admin_password', encrypted_password)
            logger.info(f"✅ 系统管理员密码已重置: {request.email}")
        
        # 2. 检查是否是KOOK账号
        account = db.get_account_by_email(request.email)
        if account:
            # 更新KOOK账号密码
            encrypted_password = encrypt_password(request.new_password)
            db.update_account(account['id'], {
                'password_encrypted': encrypted_password
            })
            logger.info(f"✅ KOOK账号密码已重置: {request.email}")
        
        # 发送成功通知邮件
        await email_sender.send_email(
            subject="[KOOK转发系统] 密码重置成功",
            body=f"""
            <p>您好，</p>
            <p>您的密码已成功重置。</p>
            <p>如果这不是您本人的操作，请立即联系系统管理员。</p>
            <p><br>来自 KOOK消息转发系统<br>
            {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            """,
            to_emails=[request.email],
            html=True
        )
        
        return {
            "success": True,
            "message": "密码重置成功，请使用新密码登录"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重置密码异常: {str(e)}")
        raise HTTPException(status_code=500, detail="密码重置失败，请稍后重试")


@router.get("/check-email-config")
async def check_email_config():
    """
    检查邮件配置是否可用
    
    Returns:
        邮件配置状态
    """
    if not email_sender.enabled:
        return {
            "enabled": False,
            "message": "邮件功能未启用，无法使用密码重置功能"
        }
    
    if not email_sender.smtp_server or not email_sender.smtp_user:
        return {
            "enabled": False,
            "message": "邮件配置不完整，请先配置SMTP服务器"
        }
    
    # 测试连接
    success, message = await email_sender.test_connection()
    
    return {
        "enabled": success,
        "message": message if success else "邮件服务器连接失败，请检查配置"
    }
