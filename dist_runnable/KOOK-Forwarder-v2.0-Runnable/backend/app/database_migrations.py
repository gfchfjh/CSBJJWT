"""
📦 数据库迁移脚本（支持新功能）

为新优化功能添加必要的数据库表：
1. mapping_learning 表（AI映射学习）
2. message_logs_archive 表（日志归档）
3. notification_history 表（通知历史）

作者: KOOK Forwarder Team
版本: 11.0.0
日期: 2025-10-28
"""
import sqlite3
from pathlib import Path
from .config import DB_PATH
from .utils.logger import logger


def migrate_to_v11():
    """迁移到v11.0.0"""
    logger.info("🔄 开始数据库迁移到v11.0.0...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. 创建映射学习表
        logger.info("  📝 创建mapping_learning表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mapping_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kook_channel_id TEXT NOT NULL,
                target_channel_id TEXT NOT NULL,
                use_count INTEGER DEFAULT 0,
                last_used_timestamp REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(kook_channel_id, target_channel_id)
            )
        """)
        
        # 添加索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mapping_learning_kook
            ON mapping_learning(kook_channel_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mapping_learning_target
            ON mapping_learning(target_channel_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mapping_learning_timestamp
            ON mapping_learning(last_used_timestamp DESC)
        """)
        
        # 2. 创建消息日志归档表
        logger.info("  📝 创建message_logs_archive表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_logs_archive (
                id INTEGER PRIMARY KEY,
                kook_message_id TEXT NOT NULL,
                kook_channel_id TEXT NOT NULL,
                content TEXT,
                message_type TEXT,
                sender_name TEXT,
                target_platform TEXT,
                target_channel TEXT,
                status TEXT,
                error_message TEXT,
                latency_ms INTEGER,
                created_at TIMESTAMP,
                archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 添加索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_archive_kook_id
            ON message_logs_archive(kook_message_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_archive_archived
            ON message_logs_archive(archived_at DESC)
        """)
        
        # 3. 创建通知历史表
        logger.info("  📝 创建notification_history表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                clicked INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 添加索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notification_type
            ON notification_history(type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notification_created
            ON notification_history(created_at DESC)
        """)
        
        # 4. 更新系统配置表（添加版本标记）
        cursor.execute("""
            INSERT OR REPLACE INTO system_config (key, value)
            VALUES ('database_version', '11.0.0')
        """)
        
        # 5. 添加首次启动标记字段
        cursor.execute("""
            INSERT OR IGNORE INTO system_config (key, value)
            VALUES ('first_run_completed', 'false')
        """)
        
        # 6. 添加向导完成标记
        cursor.execute("""
            INSERT OR IGNORE INTO system_config (key, value)
            VALUES ('wizard_completed', 'false')
        """)
        
        # 7. 添加免责声明接受标记
        cursor.execute("""
            INSERT OR IGNORE INTO system_config (key, value)
            VALUES ('disclaimer_accepted', 'false')
        """)
        
        conn.commit()
        logger.info("✅ 数据库迁移到v11.0.0完成")
        
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ 数据库迁移失败: {str(e)}")
        return False
    
    finally:
        conn.close()


def check_and_migrate():
    """检查数据库版本并执行必要的迁移"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取当前数据库版本
        cursor.execute("""
            SELECT value FROM system_config WHERE key = 'database_version'
        """)
        
        result = cursor.fetchone()
        current_version = result[0] if result else '10.0.0'
        
        conn.close()
        
        logger.info(f"当前数据库版本: {current_version}")
        
        # 如果版本低于11.0.0，执行迁移
        if current_version < '11.0.0':
            logger.info("检测到旧版本数据库，执行迁移...")
            return migrate_to_v11()
        else:
            logger.info("数据库版本已是最新")
            return True
    
    except Exception as e:
        logger.error(f"检查数据库版本失败: {str(e)}")
        # 如果表不存在，执行完整迁移
        return migrate_to_v11()


# 自动执行迁移
if __name__ == "__main__":
    check_and_migrate()
