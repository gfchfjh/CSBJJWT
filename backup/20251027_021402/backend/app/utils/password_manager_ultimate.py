"""
密码安全管理器（终极版）
======================
使用bcrypt进行密码哈希，替代简单AES加密

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import bcrypt
from typing import Optional
from .logger import logger


class PasswordManagerUltimate:
    """密码管理器（使用bcrypt）"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        哈希密码（bcrypt）
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        try:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"密码哈希失败: {e}")
            raise
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            hashed: 哈希密码
            
        Returns:
            是否匹配
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            (是否通过, 错误信息)
        """
        if len(password) < 8:
            return False, "密码至少需要8个字符"
        
        if len(password) > 128:
            return False, "密码不能超过128个字符"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "密码必须包含大写字母、小写字母和数字"
        
        return True, ""


password_manager = PasswordManagerUltimate()
