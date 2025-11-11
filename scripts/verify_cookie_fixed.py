"""
Cookie存储验证脚本 - 修复版
"""
import sqlite3
import json
from pathlib import Path
import sys

DB_PATH = Path.home() / "Documents" / "KookForwarder" / "data" / "config.db"

def verify_cookies():
    print("=" * 60)
    print("Cookie存储验证")
    print("=" * 60)
    
    if not DB_PATH.exists():
        print("❌ 数据库文件不存在")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 正确的列名是cookie，不是cookies
        cursor.execute("SELECT id, email, cookie, status FROM accounts")
        accounts = cursor.fetchall()
        
        if not accounts:
            print("⚠️  数据库中没有账号")
            return True
        
        print(f"\n📋 账号列表 (共 {len(accounts)} 个账号):")
        print("-" * 60)
        
        for i, (account_id, email, cookie, status) in enumerate(accounts, 1):
            print(f"\n[{i}] 账号ID: {account_id}")
            print(f"    邮箱: {email}")
            print(f"    状态: {status}")
            
            if cookie:
                # 尝试解密
                try:
                    import sys
                    sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
                    from app.utils.crypto import crypto_manager
                    decrypted = crypto_manager.decrypt(cookie)
                    cookie_data = json.loads(decrypted)
                    print(f"    🔐 Cookie已解密")
                    if isinstance(cookie_data, list):
                        print(f"    ✅ Cookie已存储 ({len(cookie_data)} 个Cookie)")
                    else:
                        print(f"    ✅ Cookie已存储")
                except:
                    # 未加密或解密失败
                    try:
                        cookie_data = json.loads(cookie)
                        if isinstance(cookie_data, list):
                            print(f"    ✅ Cookie已存储 ({len(cookie_data)} 个Cookie)")
                        else:
                            print(f"    ✅ Cookie已存储")
                    except:
                        print(f"    ⚠️  Cookie格式异常")
                
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
