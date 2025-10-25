"""
主密码管理器
✅ P0-8优化：实现主密码保护功能
"""
import secrets
import time
from pathlib import Path
from typing import Optional, Tuple
import bcrypt
from ..config import settings
from ..utils.logger import logger


class MasterPasswordManager:
    """主密码管理器"""
    
    def __init__(self):
        self.password_file = Path(settings.data_dir) / ".master_password"
        self.unlock_tokens: dict = {}  # {token: expire_time}
        self.token_ttl = 86400  # 24小时
        
        logger.info("✅ 主密码管理器已初始化")
    
    def is_password_set(self) -> bool:
        """
        检查是否已设置主密码
        
        Returns:
            True if password is set
        """
        return self.password_file.exists()
    
    def set_password(self, password: str) -> Tuple[bool, str]:
        """
        设置主密码
        
        Args:
            password: 新密码
            
        Returns:
            (成功与否, 消息)
        """
        try:
            # 验证密码强度
            if len(password) < 6:
                return False, "密码长度至少6位"
            
            if len(password) > 20:
                return False, "密码长度不能超过20位"
            
            # 检查密码强度（至少包含数字和字母）
            has_digit = any(c.isdigit() for c in password)
            has_alpha = any(c.isalpha() for c in password)
            
            if not (has_digit and has_alpha):
                logger.warning("密码强度较弱，但仍允许设置")
            
            # 使用bcrypt哈希密码
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # 保存到文件
            self.password_file.parent.mkdir(parents=True, exist_ok=True)
            self.password_file.write_bytes(hashed)
            
            # 设置文件权限（仅所有者可读写）
            try:
                import os
                if os.name != 'nt':  # 非Windows系统
                    import stat
                    os.chmod(self.password_file, stat.S_IRUSR | stat.S_IWUSR)
            except Exception as e:
                logger.warning(f"设置文件权限失败: {str(e)}")
            
            logger.info("✅ 主密码已设置")
            return True, "主密码设置成功"
            
        except Exception as e:
            logger.error(f"设置主密码失败: {str(e)}")
            return False, f"设置失败: {str(e)}"
    
    def verify_password(self, password: str) -> bool:
        """
        验证主密码
        
        Args:
            password: 待验证的密码
            
        Returns:
            True if password is correct
        """
        if not self.is_password_set():
            # 未设置密码时，任何密码都通过
            return True
        
        try:
            stored_hash = self.password_file.read_bytes()
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        except Exception as e:
            logger.error(f"验证主密码失败: {str(e)}")
            return False
    
    def change_password(self, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改主密码
        
        Args:
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            (成功与否, 消息)
        """
        # 验证旧密码
        if not self.verify_password(old_password):
            return False, "旧密码错误"
        
        # 设置新密码
        return self.set_password(new_password)
    
    def unlock(self, password: str, remember_days: int = 0) -> Optional[str]:
        """
        解锁应用（返回临时Token）
        
        Args:
            password: 密码
            remember_days: 记住天数（0=24小时）
            
        Returns:
            Token字符串，失败返回None
        """
        if not self.verify_password(password):
            logger.warning("主密码验证失败")
            return None
        
        # 生成Token
        token = secrets.token_urlsafe(32)
        
        # 计算过期时间
        if remember_days > 0:
            ttl = remember_days * 86400
        else:
            ttl = self.token_ttl
        
        expire_time = time.time() + ttl
        self.unlock_tokens[token] = expire_time
        
        logger.info(f"✅ 应用已解锁（Token有效期: {ttl/3600:.1f}小时）")
        return token
    
    def is_unlocked(self, token: Optional[str]) -> bool:
        """
        检查是否已解锁
        
        Args:
            token: 解锁Token
            
        Returns:
            True if unlocked
        """
        # 如果未设置密码，总是返回True
        if not self.is_password_set():
            return True
        
        if not token:
            return False
        
        if token not in self.unlock_tokens:
            return False
        
        # 检查是否过期
        expire_time = self.unlock_tokens[token]
        if time.time() > expire_time:
            # Token已过期，删除
            del self.unlock_tokens[token]
            logger.info("Token已过期")
            return False
        
        return True
    
    def revoke_token(self, token: str):
        """
        撤销Token（登出）
        
        Args:
            token: 解锁Token
        """
        if token in self.unlock_tokens:
            del self.unlock_tokens[token]
            logger.info("Token已撤销（用户登出）")
    
    def revoke_all_tokens(self):
        """撤销所有Token（强制所有用户重新登录）"""
        count = len(self.unlock_tokens)
        self.unlock_tokens.clear()
        logger.info(f"已撤销所有Token（{count}个）")
    
    def reset_password_with_email(self, email: str, verification_code: str) -> Tuple[bool, str]:
        """
        通过邮箱验证重置密码
        
        Args:
            email: 邮箱地址
            verification_code: 验证码
            
        Returns:
            (成功与否, 消息或新临时密码)
        """
        # TODO: 实现邮箱验证逻辑
        # 这里是简化实现
        
        logger.warning("密码重置功能尚未完全实现")
        
        # 生成临时密码
        temp_password = secrets.token_urlsafe(12)
        
        # 设置临时密码
        success, msg = self.set_password(temp_password)
        
        if success:
            return True, f"临时密码: {temp_password}（请尽快修改）"
        else:
            return False, msg
    
    def delete_password(self):
        """
        删除主密码（慎用！）
        """
        try:
            if self.password_file.exists():
                self.password_file.unlink()
                logger.info("⚠️ 主密码已删除")
                
                # 撤销所有Token
                self.revoke_all_tokens()
                
                return True
        except Exception as e:
            logger.error(f"删除主密码失败: {str(e)}")
            return False
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        active_tokens = 0
        expired_tokens = 0
        current_time = time.time()
        
        for expire_time in self.unlock_tokens.values():
            if current_time > expire_time:
                expired_tokens += 1
            else:
                active_tokens += 1
        
        return {
            "password_set": self.is_password_set(),
            "active_tokens": active_tokens,
            "expired_tokens": expired_tokens,
            "total_tokens": len(self.unlock_tokens)
        }
    
    def cleanup_expired_tokens(self):
        """清理过期的Token"""
        current_time = time.time()
        expired = [
            token for token, expire_time in self.unlock_tokens.items()
            if current_time > expire_time
        ]
        
        for token in expired:
            del self.unlock_tokens[token]
        
        if expired:
            logger.info(f"清理了 {len(expired)} 个过期Token")


# 创建全局实例
master_password_manager = MasterPasswordManager()
