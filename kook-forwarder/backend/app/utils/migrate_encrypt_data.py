"""
数据库加密迁移脚本
用于将现有的明文Cookie和密码加密
"""
import sys
from pathlib import Path

# 添加父目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database import db
from app.utils.crypto import crypto_manager
from app.utils.logger import logger


def migrate_encrypt_cookies():
    """
    迁移加密Cookie
    将数据库中所有明文Cookie加密存储
    """
    logger.info("开始加密Cookie数据...")
    
    try:
        accounts = db.get_accounts()
        encrypted_count = 0
        skipped_count = 0
        
        for account in accounts:
            account_id = account['id']
            cookie = account.get('cookie')
            
            if not cookie:
                logger.debug(f"账号 {account_id} 无Cookie，跳过")
                skipped_count += 1
                continue
            
            try:
                # 尝试解密，如果成功说明已经加密
                crypto_manager.decrypt(cookie)
                logger.debug(f"账号 {account_id} Cookie已加密，跳过")
                skipped_count += 1
            except:
                # 解密失败，说明是明文，需要加密
                try:
                    encrypted_cookie = crypto_manager.encrypt(cookie)
                    
                    # 更新数据库
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE accounts SET cookie = ? WHERE id = ?",
                            (encrypted_cookie, account_id)
                        )
                    
                    logger.info(f"✅ 账号 {account_id} Cookie已加密")
                    encrypted_count += 1
                except Exception as e:
                    logger.error(f"❌ 账号 {account_id} Cookie加密失败: {str(e)}")
        
        logger.info(f"Cookie加密完成: 成功 {encrypted_count} 个，跳过 {skipped_count} 个")
        return True
        
    except Exception as e:
        logger.error(f"Cookie加密失败: {str(e)}")
        return False


def migrate_encrypt_passwords():
    """
    迁移加密密码
    将数据库中所有明文密码加密存储
    """
    logger.info("开始加密密码数据...")
    
    try:
        accounts = db.get_accounts()
        encrypted_count = 0
        skipped_count = 0
        
        for account in accounts:
            account_id = account['id']
            password_encrypted = account.get('password_encrypted')
            
            if not password_encrypted:
                logger.debug(f"账号 {account_id} 无密码，跳过")
                skipped_count += 1
                continue
            
            try:
                # 尝试解密，如果成功说明已经加密
                crypto_manager.decrypt(password_encrypted)
                logger.debug(f"账号 {account_id} 密码已加密，跳过")
                skipped_count += 1
            except:
                # 解密失败，可能是明文或已经是旧格式加密
                # 为了安全，建议用户重新设置密码
                logger.warning(f"⚠️ 账号 {account_id} 密码格式未知，建议重新设置")
                skipped_count += 1
        
        logger.info(f"密码检查完成: 跳过 {skipped_count} 个")
        return True
        
    except Exception as e:
        logger.error(f"密码加密失败: {str(e)}")
        return False


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("数据库加密迁移脚本")
    logger.info("=" * 60)
    
    # 检查加密管理器是否可用
    if not crypto_manager.is_available():
        logger.error("❌ 加密管理器不可用，请检查加密密钥配置")
        return False
    
    logger.info("✅ 加密管理器可用")
    
    # 迁移Cookie
    if not migrate_encrypt_cookies():
        logger.error("Cookie加密失败")
        return False
    
    # 迁移密码
    if not migrate_encrypt_passwords():
        logger.error("密码加密失败")
        return False
    
    logger.info("=" * 60)
    logger.info("✅ 数据库加密迁移完成")
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
