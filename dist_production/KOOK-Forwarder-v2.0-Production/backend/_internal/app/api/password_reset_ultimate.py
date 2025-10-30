"""
✅ P0-7优化: 主密码重置完整系统（邮箱验证码）
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Dict, Any
import random
import string
import time
import hashlib
from ..database import db
from ..utils.crypto import crypto_manager
from ..utils.logger import logger


router = APIRouter(prefix="/auth", tags=["主密码认证"])

# 存储验证码（实际应该用Redis，这里简化用内存）
_verification_codes: Dict[str, Dict[str, Any]] = {}
# 存储设备令牌
_device_tokens: Dict[str, Dict[str, Any]] = {}


class SendResetCodeRequest(BaseModel):
    email: EmailStr


class VerifyResetCodeRequest(BaseModel):
    email: EmailStr
    code: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class VerifyMasterPasswordRequest(BaseModel):
    password: str


class VerifyDeviceTokenRequest(BaseModel):
    device_token: str


@router.post("/send-reset-code")
async def send_reset_code(request: SendResetCodeRequest) -> Dict:
    """
    发送密码重置验证码到邮箱
    
    Args:
        request: 包含邮箱
        
    Returns:
        发送结果
    """
    try:
        email = request.email
        
        # 检查该邮箱是否已注册
        # TODO: 实际应该检查system_config表中的admin_email
        
        # 生成6位验证码
        code = ''.join(random.choices(string.digits, k=6))
        
        # 存储验证码（5分钟有效）
        _verification_codes[email] = {
            'code': code,
            'expire_at': time.time() + 300,  # 5分钟
            'attempts': 0
        }
        
        # 发送邮件
        try:
            await send_email(
                to=email,
                subject='KOOK消息转发系统 - 密码重置验证码',
                body=f"""
                <h2>密码重置验证码</h2>
                <p>您正在重置KOOK消息转发系统的主密码。</p>
                <p>您的验证码是：<strong style="font-size: 24px; color: #409EFF;">{code}</strong></p>
                <p>验证码有效期为5分钟。</p>
                <p>如果这不是您的操作，请忽略此邮件。</p>
                <hr>
                <p style="color: #909399; font-size: 12px;">KOOK消息转发系统</p>
                """
            )
            
            logger.info(f"✅ 验证码已发送到: {email}")
            
            return {
                'success': True,
                'message': '验证码已发送，请查收邮件',
                'expire_seconds': 300
            }
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            
            # 邮件发送失败时，在日志中显示验证码（仅开发环境）
            logger.warning(f"开发模式：验证码为 {code}")
            
            return {
                'success': True,
                'message': '邮件服务暂时不可用，请查看应用日志获取验证码',
                'code_in_log': True
            }
    
    except Exception as e:
        logger.error(f"发送验证码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-reset-code")
async def verify_reset_code(request: VerifyResetCodeRequest) -> Dict:
    """
    验证重置验证码
    
    Args:
        request: 包含邮箱和验证码
        
    Returns:
        验证结果
    """
    try:
        email = request.email
        code = request.code
        
        # 检查验证码是否存在
        if email not in _verification_codes:
            raise HTTPException(status_code=400, detail='验证码不存在或已过期')
        
        code_data = _verification_codes[email]
        
        # 检查是否过期
        if time.time() > code_data['expire_at']:
            del _verification_codes[email]
            raise HTTPException(status_code=400, detail='验证码已过期')
        
        # 检查尝试次数
        if code_data['attempts'] >= 5:
            del _verification_codes[email]
            raise HTTPException(status_code=400, detail='验证码尝试次数过多，请重新发送')
        
        # 验证验证码
        if code != code_data['code']:
            code_data['attempts'] += 1
            raise HTTPException(status_code=400, detail=f'验证码错误（剩余{5 - code_data["attempts"]}次机会）')
        
        # 验证成功
        logger.info(f"✅ 验证码验证成功: {email}")
        
        return {
            'success': True,
            'message': '验证成功'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证验证码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-master-password")
async def reset_master_password(request: ResetPasswordRequest) -> Dict:
    """
    重置主密码
    
    Args:
        request: 包含邮箱、验证码、新密码
        
    Returns:
        重置结果
    """
    try:
        email = request.email
        code = request.code
        new_password = request.new_password
        
        # 再次验证验证码
        if email not in _verification_codes:
            raise HTTPException(status_code=400, detail='验证码不存在或已过期')
        
        code_data = _verification_codes[email]
        
        if time.time() > code_data['expire_at']:
            del _verification_codes[email]
            raise HTTPException(status_code=400, detail='验证码已过期')
        
        if code != code_data['code']:
            raise HTTPException(status_code=400, detail='验证码错误')
        
        # 验证新密码
        if len(new_password) < 6 or len(new_password) > 20:
            raise HTTPException(status_code=400, detail='密码长度必须为6-20位')
        
        # 加密新密码
        password_hash = crypto_manager.hash_password(new_password)
        
        # 保存到数据库
        db.set_config('master_password_hash', password_hash)
        db.set_config('master_password_updated_at', str(time.time()))
        
        # 清除验证码
        del _verification_codes[email]
        
        # 清除所有设备令牌（强制重新登录）
        _device_tokens.clear()
        
        logger.info(f"✅ 主密码已重置: {email}")
        
        return {
            'success': True,
            'message': '密码重置成功'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重置密码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-master-password")
async def verify_master_password(request: VerifyMasterPasswordRequest) -> Dict:
    """
    验证主密码
    
    Args:
        request: 包含密码
        
    Returns:
        验证结果，包含Token和设备令牌
    """
    try:
        password = request.password
        
        # 获取存储的密码哈希
        password_hash = db.get_config('master_password_hash')
        
        if not password_hash:
            raise HTTPException(status_code=400, detail='未设置主密码')
        
        # 验证密码
        if not crypto_manager.verify_password(password, password_hash):
            logger.warning(f"主密码验证失败")
            raise HTTPException(status_code=401, detail='密码错误')
        
        # 生成会话Token（30分钟有效）
        token = generate_token()
        token_expire = int(time.time() + 1800) * 1000  # 30分钟，毫秒
        
        # 生成设备令牌（30天有效）
        device_token = generate_device_token()
        _device_tokens[device_token] = {
            'created_at': time.time(),
            'expire_at': time.time() + (30 * 24 * 60 * 60)  # 30天
        }
        
        logger.info(f"✅ 主密码验证成功")
        
        return {
            'success': True,
            'token': token,
            'expire_at': token_expire,
            'device_token': device_token
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证主密码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-device-token")
async def verify_device_token(request: VerifyDeviceTokenRequest) -> Dict:
    """
    验证设备令牌（用于记住30天）
    
    Args:
        request: 包含设备令牌
        
    Returns:
        验证结果
    """
    try:
        device_token = request.device_token
        
        # 检查设备令牌是否存在
        if device_token not in _device_tokens:
            raise HTTPException(status_code=401, detail='设备令牌无效')
        
        token_data = _device_tokens[device_token]
        
        # 检查是否过期
        if time.time() > token_data['expire_at']:
            del _device_tokens[device_token]
            raise HTTPException(status_code=401, detail='设备令牌已过期')
        
        # 验证成功，生成新的会话Token
        token = generate_token()
        token_expire = int(time.time() + 1800) * 1000  # 30分钟
        
        logger.info(f"✅ 设备令牌验证成功（自动解锁）")
        
        return {
            'success': True,
            'token': token,
            'expire_at': token_expire
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证设备令牌失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 辅助函数 ==========

def generate_token() -> str:
    """生成随机Token"""
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    return hashlib.sha256(random_str.encode()).hexdigest()


def generate_device_token() -> str:
    """生成设备令牌"""
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    return hashlib.sha256(random_str.encode()).hexdigest()


async def send_email(to: str, subject: str, body: str):
    """
    发送邮件（简化版，实际应该使用SMTP）
    
    Args:
        to: 收件人
        subject: 主题
        body: 内容（HTML）
    """
    try:
        from ..config import settings
        
        if not settings.smtp_enabled:
            raise Exception('SMTP未配置')
        
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # 创建邮件
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = settings.smtp_from_email or settings.smtp_username
        message['To'] = to
        
        # 添加HTML内容
        html_part = MIMEText(body, 'html', 'utf-8')
        message.attach(html_part)
        
        # 发送邮件
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            
            server.send_message(message)
        
        logger.info(f"✅ 邮件已发送到: {to}")
    
    except Exception as e:
        logger.error(f"发送邮件失败: {str(e)}")
        raise


@router.get("/status")
async def get_auth_status() -> Dict:
    """
    获取认证状态
    
    Returns:
        是否已设置密码
    """
    password_hash = db.get_config('master_password_hash')
    
    return {
        'password_set': password_hash is not None,
        'require_password': True
    }
