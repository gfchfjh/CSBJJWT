"""
加密数据迁移工具（P1-5优化）

用于重新加密数据库中的敏感数据
当密钥文件损坏或需要重新生成密钥时使用
"""
from ..database import db
from ..utils.crypto import crypto_manager
from ..utils.logger import logger


def migrate_encrypted_data():
    """
    迁移加密数据
    
    警告：此操作不可逆，请确保已备份数据库
    
    Returns:
        (成功数, 失败数)
    """
    success_count = 0
    failure_count = 0
    
    # 获取所有账号
    accounts = db.get_all_accounts()
    
    logger.info(f"开始迁移 {len(accounts)} 个账号的加密数据...")
    
    for account in accounts:
        account_id = account['id']
        email = account['email']
        
        try:
            # 如果有加密的密码，尝试解密
            if account.get('password_encrypted'):
                try:
                    # 尝试用旧密钥解密
                    password = crypto_manager.decrypt(account['password_encrypted'])
                    
                    # 用新密钥重新加密
                    new_encrypted = crypto_manager.encrypt(password)
                    
                    # 更新数据库
                    db.update_account_password(account_id, new_encrypted)
                    
                    logger.info(f"✅ 账号 {email} 密码已重新加密")
                    success_count += 1
                    
                except Exception as decrypt_error:
                    logger.warning(f"⚠️ 账号 {email} 密码解密失败（可能使用旧密钥）: {decrypt_error}")
                    logger.warning(f"   建议：用户需要重新输入密码")
                    failure_count += 1
            
        except Exception as e:
            logger.error(f"❌ 迁移账号 {email} 失败: {str(e)}")
            failure_count += 1
    
    logger.info(f"迁移完成：成功 {success_count} 个，失败 {failure_count} 个")
    
    return success_count, failure_count


def clear_all_encrypted_data():
    """
    清除所有加密数据
    
    危险操作！仅在密钥完全丢失且无法恢复时使用
    用户需要重新输入所有密码
    """
    logger.warning("⚠️ 开始清除所有加密数据...")
    
    accounts = db.get_all_accounts()
    
    for account in accounts:
        account_id = account['id']
        
        # 清除加密的密码
        db.update_account_password(account_id, None)
    
    logger.info("✅ 所有加密数据已清除，用户需要重新登录")


if __name__ == '__main__':
    # 命令行工具
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python -m backend.app.utils.migrate_encryption migrate   # 迁移加密数据")
        print("  python -m backend.app.utils.migrate_encryption clear     # 清除加密数据（危险）")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'migrate':
        success, failure = migrate_encrypted_data()
        print(f"\n迁移结果：成功 {success} 个，失败 {failure} 个")
        
    elif command == 'clear':
        confirm = input("⚠️ 危险操作！确认清除所有加密数据？(yes/no): ")
        if confirm.lower() == 'yes':
            clear_all_encrypted_data()
            print("\n✅ 已清除所有加密数据")
        else:
            print("已取消")
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
