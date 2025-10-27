"""
认证系统（终极版）
================
功能：
1. 强制API认证
2. Token自动生成
3. Token过期检查
4. 多Token支持
5. Token刷新机制

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from ..database import db
from ..utils.logger import logger


class AuthManagerUltimate:
    """认证管理器（终极版）"""
    
    def __init__(self):
        self.tokens_cache = {}  # {token_hash: {'user_id': ..., 'expires': ...}}
        
    def generate_token(self, user_id: str = 'default', expires_days: int = 30) -> str:
        """
        生成API Token
        
        Args:
            user_id: 用户ID
            expires_days: 有效天数
            
        Returns:
            Token字符串
        """
        # 生成随机Token（32字节）
        token = secrets.token_urlsafe(32)
        
        # 计算过期时间
        expires_at = datetime.now() + timedelta(days=expires_days)
        
        # 保存到数据库
        token_hash = self._hash_token(token)
        
        db.set_config(f'api_token:{token_hash}', json.dumps({
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat(),
            'last_used': None
        }))
        
        logger.info(f"生成新Token: {token[:10]}... (有效期: {expires_days}天)")
        
        return token
    
    def _hash_token(self, token: str) -> str:
        """Token哈希（用于安全存储）"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        验证Token
        
        Args:
            token: Token字符串
            
        Returns:
            (是否有效, 错误消息)
        """
        if not token:
            return False, "Token为空"
        
        token_hash = self._hash_token(token)
        
        # 从数据库加载
        token_data = db.get_config(f'api_token:{token_hash}')
        
        if not token_data:
            return False, "Token无效"
        
        try:
            import json
            data = json.loads(token_data)
            
            # 检查过期
            expires_at = datetime.fromisoformat(data['expires_at'])
            if datetime.now() > expires_at:
                return False, "Token已过期"
            
            # 更新最后使用时间
            data['last_used'] = datetime.now().isoformat()
            db.set_config(f'api_token:{token_hash}', json.dumps(data))
            
            return True, None
            
        except Exception as e:
            logger.error(f"Token验证异常: {e}")
            return False, "Token验证失败"
    
    def revoke_token(self, token: str) -> bool:
        """撤销Token"""
        token_hash = self._hash_token(token)
        db.delete_config(f'api_token:{token_hash}')
        logger.info(f"已撤销Token: {token[:10]}...")
        return True
    
    def list_tokens(self) -> List[Dict]:
        """列出所有Token"""
        import json
        tokens = []
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM system_config WHERE key LIKE 'api_token:%'")
            
            for row in cursor.fetchall():
                try:
                    data = json.loads(row['value'])
                    token_hash = row['key'].replace('api_token:', '')
                    
                    tokens.append({
                        'token_hash': token_hash[:16] + '...',
                        'user_id': data.get('user_id'),
                        'created_at': data.get('created_at'),
                        'expires_at': data.get('expires_at'),
                        'last_used': data.get('last_used')
                    })
                except:
                    pass
        
        return tokens


# 全局认证管理器
auth_manager_ultimate = AuthManagerUltimate()


# 默认生成一个Token（首次启动）
def ensure_default_token():
    """确保存在默认Token"""
    default_token_key = 'default_api_token'
    
    existing_token = db.get_config(default_token_key)
    
    if not existing_token:
        token = auth_manager_ultimate.generate_token(user_id='system', expires_days=365)
        db.set_config(default_token_key, token)
        
        logger.info("=" * 60)
        logger.info("🔐 已生成默认API Token（请妥善保管）")
        logger.info(f"Token: {token}")
        logger.info("请在前端配置中设置此Token，或设置环境变量：")
        logger.info(f"export API_TOKEN={token}")
        logger.info("=" * 60)
        
        return token
    else:
        logger.info(f"✅ 使用已有Token: {existing_token[:10]}...")
        return existing_token
