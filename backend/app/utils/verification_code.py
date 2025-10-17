"""
验证码生成和验证模块
用于邮箱验证、密码重置等场景
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
from .logger import logger


class VerificationCodeManager:
    """验证码管理器"""
    
    def __init__(self):
        # 存储验证码：{email: {'code': str, 'expires_at': datetime, 'purpose': str}}
        self.codes: Dict[str, Dict] = {}
        
        # 验证码有效期（分钟）
        self.code_expiry_minutes = 10
        
        # 验证码长度
        self.code_length = 6
    
    def generate_code(self, email: str, purpose: str = 'password_reset') -> str:
        """
        生成验证码
        
        Args:
            email: 邮箱地址
            purpose: 用途（password_reset/email_verify等）
            
        Returns:
            验证码
        """
        # 生成6位数字验证码
        code = ''.join(secrets.choice(string.digits) for _ in range(self.code_length))
        
        # 设置过期时间
        expires_at = datetime.now() + timedelta(minutes=self.code_expiry_minutes)
        
        # 存储验证码
        self.codes[email] = {
            'code': code,
            'expires_at': expires_at,
            'purpose': purpose,
            'attempts': 0  # 验证尝试次数
        }
        
        logger.info(f"已为 {email} 生成验证码（用途：{purpose}）")
        return code
    
    def verify_code(self, email: str, code: str, purpose: str = 'password_reset') -> tuple[bool, str]:
        """
        验证验证码
        
        Args:
            email: 邮箱地址
            code: 验证码
            purpose: 用途
            
        Returns:
            (是否验证成功, 错误消息)
        """
        # 检查验证码是否存在
        if email not in self.codes:
            return False, "验证码不存在或已过期，请重新获取"
        
        stored = self.codes[email]
        
        # 检查用途是否匹配
        if stored['purpose'] != purpose:
            return False, "验证码用途不匹配"
        
        # 检查是否过期
        if datetime.now() > stored['expires_at']:
            del self.codes[email]
            return False, "验证码已过期，请重新获取"
        
        # 检查尝试次数（防止暴力破解）
        if stored['attempts'] >= 5:
            del self.codes[email]
            return False, "验证次数过多，验证码已失效，请重新获取"
        
        # 验证码错误，增加尝试次数
        if stored['code'] != code:
            stored['attempts'] += 1
            remaining = 5 - stored['attempts']
            return False, f"验证码错误，还剩 {remaining} 次尝试机会"
        
        # 验证成功，删除验证码
        del self.codes[email]
        logger.info(f"✅ 验证码验证成功: {email}")
        return True, "验证成功"
    
    def invalidate_code(self, email: str):
        """
        使验证码失效
        
        Args:
            email: 邮箱地址
        """
        if email in self.codes:
            del self.codes[email]
            logger.info(f"已使验证码失效: {email}")
    
    def is_code_valid(self, email: str) -> bool:
        """
        检查验证码是否有效
        
        Args:
            email: 邮箱地址
            
        Returns:
            是否有效
        """
        if email not in self.codes:
            return False
        
        stored = self.codes[email]
        return datetime.now() <= stored['expires_at']
    
    def get_remaining_time(self, email: str) -> Optional[int]:
        """
        获取验证码剩余有效时间（秒）
        
        Args:
            email: 邮箱地址
            
        Returns:
            剩余秒数，不存在返回None
        """
        if not self.is_code_valid(email):
            return None
        
        stored = self.codes[email]
        remaining = (stored['expires_at'] - datetime.now()).total_seconds()
        return int(remaining)
    
    def cleanup_expired(self):
        """清理过期的验证码"""
        now = datetime.now()
        expired_emails = [
            email for email, data in self.codes.items()
            if now > data['expires_at']
        ]
        
        for email in expired_emails:
            del self.codes[email]
        
        if expired_emails:
            logger.info(f"已清理 {len(expired_emails)} 个过期验证码")


# 创建全局验证码管理器
verification_manager = VerificationCodeManager()
