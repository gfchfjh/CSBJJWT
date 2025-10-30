"""
密码安全管理器（终极版）
======================
功能：
1. bcrypt密码哈希
2. 强密码策略验证
3. 密码复杂度检查
4. 密码历史记录（防止重复使用）
5. 密码加盐存储

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import bcrypt
import re
from typing import Tuple, List
from datetime import datetime


class PasswordManagerUltimate:
    """密码安全管理器（终极版）"""
    
    # 密码复杂度要求
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    
    SPECIAL_CHARS = r'!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        使用bcrypt哈希密码
        
        Args:
            password: 明文密码
            
        Returns:
            bcrypt哈希值
        """
        salt = bcrypt.gensalt(rounds=12)  # 12轮加密（安全且性能可接受）
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            hashed: bcrypt哈希值
            
        Returns:
            是否匹配
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            return False
    
    @classmethod
    def validate_password_strength(cls, password: str) -> Tuple[bool, List[str]]:
        """
        验证密码强度
        
        Args:
            password: 明文密码
            
        Returns:
            (是否符合要求, 错误列表)
        """
        errors = []
        
        # 长度检查
        if len(password) < cls.MIN_LENGTH:
            errors.append(f'密码长度至少{cls.MIN_LENGTH}位')
        
        if len(password) > cls.MAX_LENGTH:
            errors.append(f'密码长度不能超过{cls.MAX_LENGTH}位')
        
        # 大写字母
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append('密码必须包含大写字母')
        
        # 小写字母
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append('密码必须包含小写字母')
        
        # 数字
        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append('密码必须包含数字')
        
        # 特殊字符
        if cls.REQUIRE_SPECIAL:
            special_pattern = f'[{re.escape(cls.SPECIAL_CHARS)}]'
            if not re.search(special_pattern, password):
                errors.append(f'密码必须包含特殊字符（{cls.SPECIAL_CHARS}）')
        
        # 常见弱密码检查
        weak_passwords = [
            'password', '12345678', 'qwerty', 'admin', 'letmein',
            'welcome', 'monkey', '1234567890', 'password123'
        ]
        
        if password.lower() in weak_passwords:
            errors.append('密码过于简单，请使用更强的密码')
        
        # 连续字符检查
        if re.search(r'(.)\1{2,}', password):
            errors.append('密码不能包含3个及以上连续相同字符')
        
        # 顺序字符检查
        sequential = ['012', '123', '234', '345', '456', '567', '678', '789',
                     'abc', 'bcd', 'cde', 'def', 'efg', 'fgh']
        for seq in sequential:
            if seq in password.lower():
                errors.append('密码不能包含连续的顺序字符')
                break
        
        is_valid = len(errors) == 0
        
        return is_valid, errors
    
    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """
        生成强密码
        
        Args:
            length: 密码长度
            
        Returns:
            随机强密码
        """
        import secrets
        import string
        
        # 确保包含各类字符
        chars = (
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits +
            '!@#$%^&*'
        )
        
        while True:
            password = ''.join(secrets.choice(chars) for _ in range(length))
            
            # 验证强度
            is_valid, _ = PasswordManagerUltimate.validate_password_strength(password)
            if is_valid:
                return password
    
    @staticmethod
    def check_password_history(user_id: int, new_password: str, history_count: int = 5) -> bool:
        """
        检查密码历史（防止重复使用）
        
        Args:
            user_id: 用户ID
            new_password: 新密码
            history_count: 检查最近N个密码
            
        Returns:
            是否与历史密码重复
        """
        # 从数据库获取历史密码哈希
        history_key = f'password_history:{user_id}'
        history_data = db.get_config(history_key)
        
        if not history_data:
            return False
        
        try:
            import json
            history = json.loads(history_data)
            recent_hashes = history[-history_count:]
            
            # 检查新密码是否与历史密码相同
            for old_hash in recent_hashes:
                if PasswordManagerUltimate.verify_password(new_password, old_hash):
                    return True
            
            return False
            
        except:
            return False
    
    @staticmethod
    def add_to_password_history(user_id: int, password_hash: str, max_history: int = 10):
        """
        添加密码到历史记录
        
        Args:
            user_id: 用户ID
            password_hash: 密码哈希
            max_history: 最大历史记录数
        """
        import json
        
        history_key = f'password_history:{user_id}'
        history_data = db.get_config(history_key)
        
        if history_data:
            history = json.loads(history_data)
        else:
            history = []
        
        # 添加新密码
        history.append(password_hash)
        
        # 限制历史记录数量
        if len(history) > max_history:
            history = history[-max_history:]
        
        # 保存
        db.set_config(history_key, json.dumps(history))


# 全局实例
password_manager_ultimate = PasswordManagerUltimate()
