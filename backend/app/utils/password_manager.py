"""
主密码管理器
提供密码哈希、验证、Token生成等功能
v17.0.0深度优化：集成增强密码验证器
"""
import hashlib
import secrets
import time
from typing import Optional, Tuple
from ..database import db
from ..utils.logger import logger
from ..utils.password_validator_enhanced import password_validator_enhanced


class PasswordManager:
    """主密码管理器"""
    
    def __init__(self):
        self.token_expire_seconds = 30 * 24 * 3600  # 30天
    
    def hash_password(self, password: str) -> str:
        """
        哈希密码（使用SHA-256）
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def is_password_set(self) -> bool:
        """
        检查是否已设置主密码
        
        Returns:
            是否已设置
        """
        password_hash = db.get_system_config('master_password_hash')
        return password_hash is not None
    
    def set_password(self, password: str) -> bool:
        """
        设置主密码
        
        Args:
            password: 明文密码
            
        Returns:
            是否成功
        """
        try:
            # 验证密码强度
            if not self._validate_password_strength(password):
                logger.error("密码强度不足")
                return False
            
            # 哈希密码
            password_hash = self.hash_password(password)
            
            # 保存到数据库
            db.set_system_config('master_password_hash', password_hash)
            
            logger.info("主密码设置成功")
            return True
            
        except Exception as e:
            logger.error(f"设置主密码失败: {str(e)}")
            return False
    
    def verify_password(self, password: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            
        Returns:
            是否正确
        """
        try:
            # 获取存储的密码哈希
            stored_hash = db.get_system_config('master_password_hash')
            
            if not stored_hash:
                logger.warning("主密码未设置")
                return False
            
            # 计算输入密码的哈希
            input_hash = self.hash_password(password)
            
            # 比较哈希值
            is_valid = input_hash == stored_hash
            
            if is_valid:
                logger.info("密码验证成功")
            else:
                logger.warning("密码验证失败")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"验证密码异常: {str(e)}")
            return False
    
    def change_password(self, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改密码
        
        Args:
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            (是否成功, 消息)
        """
        try:
            # 验证旧密码
            if not self.verify_password(old_password):
                return False, "旧密码错误"
            
            # 验证新密码强度
            if not self._validate_password_strength(new_password):
                # 获取详细的验证结果
                result = password_validator_enhanced.validate(new_password)
                error_msg = "密码强度不足: " + ", ".join(result.issues)
                return False, error_msg
            
            # 检查新旧密码是否相同
            if old_password == new_password:
                return False, "新密码不能与旧密码相同"
            
            # 设置新密码
            if self.set_password(new_password):
                # 清除所有Token，要求重新登录
                self._invalidate_all_tokens()
                return True, "密码修改成功"
            else:
                return False, "密码修改失败"
                
        except Exception as e:
            logger.error(f"修改密码异常: {str(e)}")
            return False, f"修改密码异常: {str(e)}"
    
    def generate_token(self) -> str:
        """
        生成访问Token
        
        Returns:
            Token字符串
        """
        token = secrets.token_urlsafe(32)
        expire_at = int(time.time()) + self.token_expire_seconds
        
        # 保存Token到数据库
        db.set_system_config(f'auth_token_{token}', str(expire_at))
        
        logger.info(f"生成Token: {token[:8]}...，有效期30天")
        return token
    
    def verify_token(self, token: str) -> bool:
        """
        验证Token
        
        Args:
            token: Token字符串
            
        Returns:
            是否有效
        """
        try:
            # 获取Token过期时间
            expire_at_str = db.get_system_config(f'auth_token_{token}')
            
            if not expire_at_str:
                logger.debug(f"Token不存在: {token[:8]}...")
                return False
            
            expire_at = int(expire_at_str)
            
            # 检查是否过期
            if time.time() > expire_at:
                logger.info(f"Token已过期: {token[:8]}...")
                db.delete_system_config(f'auth_token_{token}')
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证Token异常: {str(e)}")
            return False
    
    def invalidate_token(self, token: str):
        """
        使Token失效
        
        Args:
            token: Token字符串
        """
        db.delete_system_config(f'auth_token_{token}')
        logger.info(f"Token已失效: {token[:8]}...")
    
    def _invalidate_all_tokens(self):
        """使所有Token失效"""
        # 获取所有auth_token开头的配置
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM system_config 
                WHERE key LIKE 'auth_token_%'
            """)
            conn.commit()
        logger.info("所有Token已失效")
    
    def _validate_password_strength(self, password: str) -> bool:
        """
        验证密码强度（v17.0.0深度优化：使用增强验证器）
        
        Args:
            password: 密码
            
        Returns:
            是否满足强度要求
        """
        # 使用增强密码验证器
        result = password_validator_enhanced.validate(password)
        
        if not result.is_valid:
            # 记录具体问题
            logger.warning(f"密码强度不足: {', '.join(result.issues)}")
            return False
        
        logger.info(f"密码强度验证通过: 等级={result.level}, 分数={result.score}")
        return True
    
    def reset_password_with_verification(self, verification_code: str, new_password: str) -> Tuple[bool, str]:
        """
        通过验证码重置密码
        
        Args:
            verification_code: 验证码
            new_password: 新密码
            
        Returns:
            (是否成功, 消息)
        """
        try:
            # 验证验证码
            stored_code = db.get_system_config('password_reset_code')
            code_expire = db.get_system_config('password_reset_code_expire')
            
            if not stored_code or not code_expire:
                return False, "验证码不存在或已过期"
            
            if time.time() > float(code_expire):
                db.delete_system_config('password_reset_code')
                db.delete_system_config('password_reset_code_expire')
                return False, "验证码已过期"
            
            if stored_code != verification_code:
                return False, "验证码错误"
            
            # 验证新密码强度
            if not self._validate_password_strength(new_password):
                # 获取详细的验证结果
                result = password_validator_enhanced.validate(new_password)
                error_msg = "密码强度不足: " + ", ".join(result.issues)
                return False, error_msg
            
            # 设置新密码
            if self.set_password(new_password):
                # 清除验证码
                db.delete_system_config('password_reset_code')
                db.delete_system_config('password_reset_code_expire')
                
                # 清除所有Token
                self._invalidate_all_tokens()
                
                return True, "密码重置成功"
            else:
                return False, "密码重置失败"
                
        except Exception as e:
            logger.error(f"重置密码异常: {str(e)}")
            return False, f"重置密码异常: {str(e)}"


# 创建全局实例
password_manager = PasswordManager()
