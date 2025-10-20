"""
验证码生成和验证模块
用于邮箱验证、密码重置等场景
v1.9.1 优化：使用Redis存储验证码，支持分布式部署
"""
import secrets
import string
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from .logger import logger
import redis


class VerificationCodeManager:
    """验证码管理器（使用Redis存储）"""
    
    def __init__(self):
        # 尝试连接Redis，失败则使用内存存储
        try:
            self.redis_client = redis.Redis(
                host='127.0.0.1',
                port=6379,
                db=1,  # 使用db1存储验证码
                decode_responses=True
            )
            # 测试连接
            self.redis_client.ping()
            self.use_redis = True
            logger.info("✅ 验证码管理器使用Redis存储")
        except Exception as e:
            logger.warning(f"Redis连接失败，使用内存存储: {str(e)}")
            self.use_redis = False
            # 内存存储：{email: {'code': str, 'expires_at': datetime, 'purpose': str}}
            self.codes: Dict[str, Dict] = {}
        
        # 验证码有效期（分钟）
        self.code_expiry_minutes = 10
        
        # 短期确认令牌有效期（分钟）- 用于verify后到reset之间的时间窗口
        self.confirm_token_expiry_minutes = 5
        
        # 验证码长度
        self.code_length = 6
    
    def generate_code(self, email: str, purpose: str = 'password_reset') -> str:
        """
        生成验证码
        
        Args:
            email: 邮箱地址
            purpose: 用途（password_reset/email_verify/password_reset_confirmed等）
            
        Returns:
            验证码
        """
        # 生成6位数字验证码
        code = ''.join(secrets.choice(string.digits) for _ in range(self.code_length))
        
        # 根据用途设置不同的过期时间
        if purpose == 'password_reset_confirmed':
            expiry_minutes = self.confirm_token_expiry_minutes
        else:
            expiry_minutes = self.code_expiry_minutes
        
        # 设置过期时间
        expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
        
        data = {
            'code': code,
            'expires_at': expires_at.isoformat(),
            'purpose': purpose,
            'attempts': 0  # 验证尝试次数
        }
        
        # 存储验证码
        if self.use_redis:
            # 使用Redis存储，自动过期
            key = f"verification:{email}:{purpose}"
            self.redis_client.setex(
                name=key,
                time=expiry_minutes * 60,  # 秒
                value=json.dumps(data)
            )
        else:
            # 使用内存存储
            data['expires_at'] = expires_at
            self.codes[f"{email}:{purpose}"] = data
        
        logger.info(f"已为 {email} 生成验证码（用途：{purpose}，有效期：{expiry_minutes}分钟）")
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
        key = f"{email}:{purpose}"
        
        # 获取存储的验证码
        if self.use_redis:
            redis_key = f"verification:{email}:{purpose}"
            stored_json = self.redis_client.get(redis_key)
            if not stored_json:
                return False, "验证码不存在或已过期，请重新获取"
            stored = json.loads(stored_json)
            stored['expires_at'] = datetime.fromisoformat(stored['expires_at'])
        else:
            # 使用内存存储
            if key not in self.codes:
                return False, "验证码不存在或已过期，请重新获取"
            stored = self.codes[key]
        
        # 检查用途是否匹配
        if stored['purpose'] != purpose:
            return False, "验证码用途不匹配"
        
        # 检查是否过期
        if datetime.now() > stored['expires_at']:
            self.invalidate_code(email, purpose)
            return False, "验证码已过期，请重新获取"
        
        # 检查尝试次数（防止暴力破解）
        if stored['attempts'] >= 5:
            self.invalidate_code(email, purpose)
            return False, "验证次数过多，验证码已失效，请重新获取"
        
        # 验证码错误，增加尝试次数
        if stored['code'] != code:
            stored['attempts'] += 1
            
            # 更新尝试次数
            if self.use_redis:
                redis_key = f"verification:{email}:{purpose}"
                stored['expires_at'] = stored['expires_at'].isoformat()
                self.redis_client.setex(
                    name=redis_key,
                    time=int((datetime.fromisoformat(stored['expires_at']) - datetime.now()).total_seconds()),
                    value=json.dumps(stored)
                )
            else:
                self.codes[key] = stored
            
            remaining = 5 - stored['attempts']
            return False, f"验证码错误，还剩 {remaining} 次尝试机会"
        
        # 验证成功，删除验证码
        self.invalidate_code(email, purpose)
        logger.info(f"✅ 验证码验证成功: {email} ({purpose})")
        return True, "验证成功"
    
    def invalidate_code(self, email: str, purpose: str = None):
        """
        使验证码失效
        
        Args:
            email: 邮箱地址
            purpose: 用途（可选，不指定则删除所有用途）
        """
        if self.use_redis:
            if purpose:
                # 删除指定用途
                redis_key = f"verification:{email}:{purpose}"
                self.redis_client.delete(redis_key)
            else:
                # 删除所有用途
                pattern = f"verification:{email}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
        else:
            # 内存存储
            if purpose:
                key = f"{email}:{purpose}"
                if key in self.codes:
                    del self.codes[key]
            else:
                # 删除所有相关验证码
                keys_to_delete = [k for k in self.codes.keys() if k.startswith(f"{email}:")]
                for k in keys_to_delete:
                    del self.codes[k]
        
        logger.info(f"已使验证码失效: {email}" + (f" ({purpose})" if purpose else ""))
    
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
