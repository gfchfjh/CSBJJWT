"""
Cookie存储验证脚本
检查数据库中Cookie的存储情况
"""
import sqlite3
import json
from pathlib import Path
import sys

DB_PATH = Path.home() / "Documents" / "KookForwarder" / "data" / "config.db"

def verify_cookies():
    """验证Cookie存储"""
    
    print("=" * 60)
    print("Cookie存储验证")
    print("=" * 60)
    
    if not DB_PATH.exists():
        print("❌ 数据库文件不存在")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查询所有账号（注意：数据库列名是cookie，不是cookies）
        cursor.execute("SELECT id, email, cookie, status FROM accounts")
        accounts = cursor.fetchall()
        
        if not accounts:
            print("⚠️  数据库中没有账号")
            print("ℹ️  请先在前端添加账号进行测试")
            return True
        
        print(f"\n📋 账号列表 (共 {len(accounts)} 个账号):")
        print("-" * 60)
        
        for i, (account_id, email, cookie, status) in enumerate(accounts, 1):
            print(f"\n[{i}] 账号ID: {account_id}")
            print(f"    邮箱: {email}")
            print(f"    状态: {status}")
            
            # 解析Cookie
            if cookie:
                # 尝试解密Cookie（如果已加密）
                try:
                    from backend.app.utils.crypto import crypto_manager
                    decrypted_cookie = crypto_manager.decrypt(cookie)
                    cookie_to_parse = decrypted_cookie
                    print(f"    🔐 Cookie已解密")
                except:
                    # 如果解密失败，可能是未加密的Cookie
                    cookie_to_parse = cookie
                
                try:
                    cookie_data = json.loads(cookie_to_parse)
                    if isinstance(cookie_data, list):
                        print(f"    ✅ Cookie已存储 ({len(cookie_data)} 个Cookie)")
                    else:
                        print(f"    ✅ Cookie已存储")
                    
                    # 显示Cookie大小
                    cookie_size = len(cookie)
                    print(f"    📊 Cookie大小: {cookie_size} 字符")
                    
                except json.JSONDecodeError:
                    print(f"    ⚠️  Cookie格式可能不是JSON")
                    print(f"    📊 Cookie大小: {len(cookie)} 字符")
            else:
                print(f"    ⚠️  Cookie为空")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Cookie存储验证完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_cookies()
    sys.exit(0 if success else 1)
