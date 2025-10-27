"""
加密工具模块（P1-5优化：密钥持久化）
"""
import base64
import hashlib
import os
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import uuid


class CryptoManager:
    """加密管理器（✅ 优化：密钥持久化，重启后仍可解密）"""
    
    def __init__(self, master_key: str = None):
        """
        初始化加密管理器
        
        Args:
            master_key: 主密钥，如果不提供则从文件加载或生成
        """
        if master_key is None:
            # ✅ P1-5优化：从文件加载或生成持久化密钥
            master_key = self._load_or_generate_key()
        
        self.fernet = Fernet(master_key.encode() if isinstance(master_key, str) else master_key)
    
    def _load_or_generate_key(self) -> bytes:
        """
        加载或生成持久化密钥（✅ P1-5优化）
        
        Returns:
            加密密钥（bytes）
        """
        from ..config import settings
        
        # 密钥文件路径
        key_file = settings.data_dir / ".encryption_key"
        
        if key_file.exists():
            # 从文件加载密钥
            try:
                with open(key_file, 'rb') as f:
                    key = f.read()
                    # 验证密钥格式
                    Fernet(key)  # 如果密钥无效会抛出异常
                    return key
            except Exception as e:
                # 密钥文件损坏，重新生成
                print(f"⚠️ 密钥文件损坏，重新生成: {e}")
        
        # 首次启动或密钥损坏，生成新密钥
        key = Fernet.generate_key()
        
        # 持久化到文件
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # ✅ 设置文件权限（仅当前用户可读写）
            if os.name != 'nt':  # Unix/Linux/macOS
                os.chmod(key_file, 0o600)
            else:  # Windows
                # Windows使用icacls设置权限
                try:
                    import subprocess
                    subprocess.run([
                        'icacls', str(key_file), 
                        '/inheritance:r',  # 移除继承
                        '/grant:r', f'{os.getlogin()}:F'  # 仅当前用户完全控制
                    ], check=True, capture_output=True)
                except:
                    pass  # 权限设置失败不影响功能
            
            print(f"✅ 新密钥已生成并保存到: {key_file}")
            
        except Exception as e:
            print(f"⚠️ 密钥持久化失败: {e}")
            print("⚠️ 密钥仅在内存中，重启后将无法解密旧数据")
        
        return key
    
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
        kdf = PBKDF2HMAC(
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


def encrypt_password(password: str) -> str:
    """
    加密密码（快捷函数）
    用于安全存储密码
    
    Args:
        password: 原始密码
        
    Returns:
        加密后的密码
    """
    return crypto_manager.encrypt(password)


def decrypt_password(encrypted_password: str) -> str:
    """
    解密密码（快捷函数）
    
    Args:
        encrypted_password: 加密后的密码
        
    Returns:
        原始密码
    """
    return crypto_manager.decrypt(encrypted_password)
