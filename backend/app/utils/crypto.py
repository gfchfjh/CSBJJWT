"""加密工具模块"""
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class CryptoUtil:
    """加密工具类"""
    
    def __init__(self, master_key: str = None):
        """初始化加密工具
        
        Args:
            master_key: 主密钥，如果不提供则使用设备ID生成
        """
        if master_key is None:
            master_key = self._get_device_id()
        
        self.cipher = self._create_cipher(master_key)
    
    def _get_device_id(self) -> str:
        """获取设备唯一ID"""
        import platform
        import uuid
        
        # 组合多个设备信息生成唯一ID
        device_info = f"{platform.node()}-{platform.machine()}-{uuid.getnode()}"
        return hashlib.sha256(device_info.encode()).hexdigest()
    
    def _create_cipher(self, master_key: str) -> Fernet:
        """创建加密器"""
        # 使用PBKDF2派生密钥
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'kook-forwarder-salt',  # 在生产环境应使用随机salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        return Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """加密文本
        
        Args:
            plaintext: 明文
            
        Returns:
            加密后的文本（Base64编码）
        """
        encrypted = self.cipher.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """解密文本
        
        Args:
            ciphertext: 密文（Base64编码）
            
        Returns:
            解密后的明文
        """
        encrypted = base64.urlsafe_b64decode(ciphertext.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()


# 全局加密工具实例
crypto = CryptoUtil()
