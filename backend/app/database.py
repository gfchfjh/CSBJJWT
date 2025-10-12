"""数据库管理模块"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from app.config import settings


class Database:
    """SQLite数据库管理类"""
    
    def __init__(self, db_path: Path = settings.DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # 允许按列名访问
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 账号表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    password_encrypted TEXT,
                    cookie TEXT,
                    status TEXT DEFAULT 'offline',
                    last_active TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Bot配置表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    name TEXT NOT NULL,
                    config TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 频道映射表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channel_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kook_server_id TEXT NOT NULL,
                    kook_channel_id TEXT NOT NULL,
                    kook_channel_name TEXT NOT NULL,
                    target_platform TEXT NOT NULL,
                    target_bot_id INTEGER NOT NULL,
                    target_channel_id TEXT NOT NULL,
                    enabled INTEGER DEFAULT 1,
                    FOREIGN KEY (target_bot_id) REFERENCES bot_configs(id)
                )
            """)
            
            # 过滤规则表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS filter_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_type TEXT NOT NULL,
                    rule_value TEXT NOT NULL,
                    scope TEXT DEFAULT 'global',
                    enabled INTEGER DEFAULT 1
                )
            """)
            
            # 消息日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kook_message_id TEXT NOT NULL UNIQUE,
                    kook_channel_id TEXT NOT NULL,
                    content TEXT,
                    message_type TEXT,
                    sender_name TEXT,
                    target_platform TEXT,
                    target_channel TEXT,
                    status TEXT,
                    error_message TEXT,
                    latency_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 失败消息队列
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS failed_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_log_id INTEGER NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TIMESTAMP,
                    FOREIGN KEY (message_log_id) REFERENCES message_logs(id)
                )
            """)
            
            # 系统配置表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    # 账号管理
    def add_account(self, email: str, password_encrypted: str = None, cookie: str = None) -> int:
        """添加KOOK账号"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accounts (email, password_encrypted, cookie)
                VALUES (?, ?, ?)
            """, (email, password_encrypted, cookie))
            return cursor.lastrowid
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """获取所有账号"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_account_status(self, account_id: int, status: str):
        """更新账号状态"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE accounts 
                SET status = ?, last_active = ?
                WHERE id = ?
            """, (status, datetime.now(), account_id))
    
    # Bot配置管理
    def add_bot_config(self, platform: str, name: str, config: Dict[str, Any]) -> int:
        """添加Bot配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bot_configs (platform, name, config)
                VALUES (?, ?, ?)
            """, (platform, name, json.dumps(config)))
            return cursor.lastrowid
    
    def get_bot_configs(self, platform: str = None) -> List[Dict[str, Any]]:
        """获取Bot配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if platform:
                cursor.execute("SELECT * FROM bot_configs WHERE platform = ?", (platform,))
            else:
                cursor.execute("SELECT * FROM bot_configs")
            
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                data['config'] = json.loads(data['config'])
                results.append(data)
            return results
    
    # 频道映射管理
    def add_channel_mapping(self, kook_server_id: str, kook_channel_id: str, 
                          kook_channel_name: str, target_platform: str, 
                          target_bot_id: int, target_channel_id: str) -> int:
        """添加频道映射"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO channel_mappings 
                (kook_server_id, kook_channel_id, kook_channel_name, 
                 target_platform, target_bot_id, target_channel_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (kook_server_id, kook_channel_id, kook_channel_name,
                  target_platform, target_bot_id, target_channel_id))
            return cursor.lastrowid
    
    def get_channel_mappings(self, kook_channel_id: str = None) -> List[Dict[str, Any]]:
        """获取频道映射"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if kook_channel_id:
                cursor.execute("""
                    SELECT * FROM channel_mappings 
                    WHERE kook_channel_id = ? AND enabled = 1
                """, (kook_channel_id,))
            else:
                cursor.execute("SELECT * FROM channel_mappings WHERE enabled = 1")
            return [dict(row) for row in cursor.fetchall()]
    
    # 消息日志
    def add_message_log(self, kook_message_id: str, kook_channel_id: str,
                       content: str, message_type: str, sender_name: str,
                       target_platform: str, target_channel: str,
                       status: str, error_message: str = None, 
                       latency_ms: int = None) -> int:
        """添加消息日志"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO message_logs 
                (kook_message_id, kook_channel_id, content, message_type, 
                 sender_name, target_platform, target_channel, status, 
                 error_message, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (kook_message_id, kook_channel_id, content, message_type,
                  sender_name, target_platform, target_channel, status,
                  error_message, latency_ms))
            return cursor.lastrowid
    
    def get_message_logs(self, limit: int = 100, status: str = None) -> List[Dict[str, Any]]:
        """获取消息日志"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("""
                    SELECT * FROM message_logs 
                    WHERE status = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (status, limit))
            else:
                cursor.execute("""
                    SELECT * FROM message_logs 
                    ORDER BY created_at DESC LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # 系统配置
    def set_config(self, key: str, value: str):
        """设置系统配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value)
                VALUES (?, ?)
            """, (key, value))
    
    def get_config(self, key: str, default: str = None) -> Optional[str]:
        """获取系统配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_config WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default


# 全局数据库实例
db = Database()
