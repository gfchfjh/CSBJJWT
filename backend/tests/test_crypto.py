"""
加密工具模块测试
"""
import pytest
from app.utils.crypto import CryptoManager, crypto_manager, hash_password, verify_password


class TestCryptoManager:
    """CryptoManager类测试"""
    
    def test_encrypt_decrypt(self):
        """测试加密和解密"""
        crypto = CryptoManager()
        
        # 测试普通文本
        plaintext = "这是一个测试密码123!@#"
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert encrypted != plaintext  # 加密后应该不同
        assert decrypted == plaintext  # 解密后应该相同
        
        # 测试空字符串
        assert crypto.encrypt("") == ""
        assert crypto.decrypt("") == ""
        
        # 测试中文
        plaintext = "中文密码测试"
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        assert decrypted == plaintext
    
    def test_decrypt_invalid_data(self):
        """测试解密无效数据"""
        crypto = CryptoManager()
        
        with pytest.raises(ValueError):
            crypto.decrypt("invalid_encrypted_data")
    
    def test_hash_password(self):
        """测试密码哈希"""
        password = "MySecurePassword123"
        hashed = CryptoManager.hash_password(password)
        
        # 哈希后应该不同
        assert hashed != password
        
        # 哈希长度应该固定（SHA256 = 64位十六进制）
        assert len(hashed) == 64
        
        # 相同密码应该产生相同哈希
        hashed2 = CryptoManager.hash_password(password)
        assert hashed == hashed2
        
        # 不同密码应该产生不同哈希
        hashed3 = CryptoManager.hash_password("DifferentPassword")
        assert hashed != hashed3
    
    def test_verify_password(self):
        """测试密码验证"""
        password = "TestPassword456"
        hashed = CryptoManager.hash_password(password)
        
        # 正确密码应该验证通过
        assert CryptoManager.verify_password(password, hashed) == True
        
        # 错误密码应该验证失败
        assert CryptoManager.verify_password("WrongPassword", hashed) == False
        
        # 空密码
        assert CryptoManager.verify_password("", hashed) == False


class TestGlobalCryptoFunctions:
    """测试全局加密函数"""
    
    def test_hash_password_function(self):
        """测试hash_password快捷函数"""
        password = "GlobalTestPassword"
        hashed = hash_password(password)
        
        assert len(hashed) == 64
        assert hashed != password
    
    def test_verify_password_function(self):
        """测试verify_password快捷函数"""
        password = "VerifyTest123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True
        assert verify_password("wrong", hashed) == False


class TestEncryptionConsistency:
    """测试加密一致性"""
    
    def test_encrypt_decrypt_multiple_times(self):
        """测试多次加密解密"""
        crypto = CryptoManager()
        original = "重复测试文本"
        
        # 多次加密解密
        for i in range(5):
            encrypted = crypto.encrypt(original)
            decrypted = crypto.decrypt(encrypted)
            assert decrypted == original
    
    def test_encrypt_special_characters(self):
        """测试特殊字符加密"""
        crypto = CryptoManager()
        
        special_texts = [
            "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "中文🎉emoji混合",
            "多行\n文本\t测试",
            "空格   多个空格",
        ]
        
        for text in special_texts:
            encrypted = crypto.encrypt(text)
            decrypted = crypto.decrypt(encrypted)
            assert decrypted == text, f"Failed for: {text}"
    
    def test_global_crypto_manager(self):
        """测试全局加密管理器实例"""
        text = "全局实例测试"
        encrypted = crypto_manager.encrypt(text)
        decrypted = crypto_manager.decrypt(encrypted)
        
        assert decrypted == text


class TestPasswordSecurity:
    """测试密码安全性"""
    
    def test_password_hash_uniqueness(self):
        """测试密码哈希唯一性"""
        passwords = [
            "password1",
            "password2",
            "Password1",  # 大小写敏感
            "password 1", # 空格敏感
        ]
        
        hashes = [hash_password(pwd) for pwd in passwords]
        
        # 所有哈希应该不同
        assert len(set(hashes)) == len(passwords)
    
    def test_common_passwords(self):
        """测试常见密码哈希"""
        common_passwords = [
            "123456",
            "password",
            "admin",
            "letmein",
        ]
        
        for pwd in common_passwords:
            hashed = hash_password(pwd)
            assert verify_password(pwd, hashed)
            assert not verify_password(pwd + "x", hashed)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
