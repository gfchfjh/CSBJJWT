"""
数据库完整性检查脚本
检查数据库文件、表结构、索引和数据完整性
"""
import sqlite3
import sys
from pathlib import Path

# 数据库路径
DB_PATH = Path.home() / "Documents" / "KookForwarder" / "data" / "config.db"

def check_database():
    """检查数据库完整性"""
    
    print("=" * 60)
    print("数据库完整性检查")
    print("=" * 60)
    
    # 检查数据库文件是否存在
    if not DB_PATH.exists():
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        print("⚠️  系统首次启动时会自动创建")
        return False
    
    print(f"✅ 数据库文件存在: {DB_PATH}")
    print(f"📊 文件大小: {DB_PATH.stat().st_size / 1024:.2f} KB\n")
    
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"📋 数据库表列表 (共 {len(tables)} 个表):")
        print("-" * 60)
        
        required_tables = [
            'accounts',
            'bot_configs',
            'channel_mappings',
            'filter_rules',
            'message_logs',
            'failed_messages',
            'system_settings',
            'disclaimer_agreements'
        ]
        
        existing_tables = [table[0] for table in tables]
        
        for i, table in enumerate(existing_tables, 1):
            # 获取表的行数
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            status = "✅" if table in required_tables else "ℹ️"
            print(f"{status} [{i:2d}] {table:<30} - {count:>6} 行")
        
        # 检查缺失的表
        missing_tables = set(required_tables) - set(existing_tables)
        if missing_tables:
            print(f"\n⚠️  缺失的关键表: {', '.join(missing_tables)}")
            print("   系统首次启动时会自动创建这些表")
        else:
            print("\n✅ 所有关键表都存在")
        
        # 检查索引
        print("\n" + "=" * 60)
        print("📊 数据库索引检查")
        print("-" * 60)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        print(f"✅ 共有 {len(indexes)} 个索引")
        
        # 数据库完整性检查
        print("\n" + "=" * 60)
        print("🔍 数据库完整性验证")
        print("-" * 60)
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result[0] == 'ok':
            print("✅ 数据库完整性检查通过")
        else:
            print(f"❌ 数据库完整性检查失败: {result[0]}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ 数据库检查完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 检查过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)
