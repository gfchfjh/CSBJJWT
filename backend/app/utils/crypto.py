"""
加密工具模块
"""
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import uuid


class CryptoManager:
    """加密管理器"""
    
    def __init__(self, master_key: str = None):
        """
        初始化加密管理器
        
        Args:
            master_key: 主密钥，如果不提供则基于设备ID生成
        """
        if master_key is None:
            # 基于设备唯一ID生成密钥
            device_id = self._get_device_id()
            master_key = self._derive_key_from_device_id(device_id)
        
        self.fernet = Fernet(master_key.encode() if isinstance(master_key, str) else master_key)
    
    def _get_device_id(self) -> str:
        """获取设备唯一ID"""
        try:
            # 尝试使用MAC地址
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                           for i in range(0, 8*6, 8)][::-1])
            return hashlib.sha256(mac.encode()).hexdigest()
        except:
            # fallback到随机生成
            return str(uuid.uuid4())
    
    def _derive_key_from_device_id(self, device_id: str) -> bytes:
        """从设备ID派生密钥"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'kook_forwarder_salt',  # 固定盐值
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(device_id.encode()))
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密文本
        
        Args:
            plaintext: 明文
            
        Returns:
            加密后的密文（Base64编码）
        """
        if not plaintext:
            return ""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密文本
        
        Args:
            ciphertext: 密文（Base64编码）
            
        Returns:
            解密后的明文
        """
        if not ciphertext:
            return ""
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self.fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希
        
        Args:
            password: 原始密码
            
        Returns:
            哈希后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        验证密码
        
        Args:
            password: 原始密码
            hashed: 哈希后的密码
            
        Returns:
            是否匹配
        """
        return CryptoManager.hash_password(password) == hashed


# 创建全局加密管理器实例
crypto_manager = CryptoManager()


# 导出快捷函数
def hash_password(password: str) -> str:
    """
    对密码进行哈希（快捷函数）
    
    Args:
        password: 原始密码
        
    Returns:
        哈希后的密码
    """
    return CryptoManager.hash_password(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    验证密码（快捷函数）
    
    Args:
        password: 原始密码
        hashed: 哈希后的密码
        
    Returns:
        是否匹配
    """
    return CryptoManager.verify_password(password, hashed)
