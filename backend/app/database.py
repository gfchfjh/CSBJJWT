"""
数据库模型和操作
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from contextlib import contextmanager
from .config import DB_PATH


class Database:
    """数据库操作类"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute(self, query: str, params: tuple = ()):
        """执行SQL查询（快捷方法）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        
        class CursorWrapper:
            """Cursor包装器，自动关闭连接"""
            def __init__(self, cursor, conn):
                self._cursor = cursor
                self._conn = conn
            
            def fetchone(self):
                try:
                    return self._cursor.fetchone()
                finally:
                    self._conn.close()
            
            def fetchall(self):
                try:
                    return self._cursor.fetchall()
                finally:
                    self._conn.close()
            
            def fetchmany(self, size=None):
                try:
                    return self._cursor.fetchmany(size)
                finally:
                    self._conn.close()
        
        return CursorWrapper(cursor, conn)
    
    def init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 账号表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password_encrypted TEXT,
                    cookie TEXT,
                    status TEXT DEFAULT 'offline',
                    last_active TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 添加索引以提升查询性能
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_email 
                ON accounts(email)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_status 
                ON accounts(status)
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
            
            # 添加频道映射索引（提升映射查询性能）
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_channel_mappings_kook_channel 
                ON channel_mappings(kook_channel_id, enabled)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_channel_mappings_platform 
                ON channel_mappings(target_platform)
            """)
            # v1.7.2新增：复合索引优化联表查询
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mapping_bot_platform 
                ON channel_mappings(target_bot_id, target_platform)
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
            
            # 添加消息日志索引（提升查询和去重性能）
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_kook_id 
                ON message_logs(kook_message_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_status 
                ON message_logs(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_created 
                ON message_logs(created_at DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_channel 
                ON message_logs(kook_channel_id, created_at DESC)
            """)
            # v1.7.2新增：复合索引优化联合查询
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_channel_status 
                ON message_logs(kook_channel_id, status, created_at DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_platform_status 
                ON message_logs(target_platform, status, created_at DESC)
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
    def add_account(self, email: str, password_encrypted: Optional[str] = None, 
                   cookie: Optional[str] = None) -> int:
        """添加账号"""
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
    
    def get_account(self, account_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个账号信息
        
        Args:
            account_id: 账号ID
            
        Returns:
            账号信息字典，不存在返回None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_account_status(self, account_id: int, status: str):
        """更新账号状态"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE accounts 
                SET status = ?, last_active = ? 
                WHERE id = ?
            """, (status, datetime.now(), account_id))
    
    def update_account_cookie(self, account_id: int, cookie: str):
        """
        更新账号Cookie
        
        Args:
            account_id: 账号ID
            cookie: Cookie字符串（JSON格式）
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE accounts 
                SET cookie = ?, last_active = ? 
                WHERE id = ?
            """, (cookie, datetime.now(), account_id))
    
    def delete_account(self, account_id: int):
        """删除账号"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    
    # Bot配置管理
    def add_bot_config(self, platform: str, name: str, config: Dict[str, Any]) -> int:
        """添加Bot配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bot_configs (platform, name, config)
                VALUES (?, ?, ?)
            """, (platform, name, json.dumps(config, ensure_ascii=False)))
            return cursor.lastrowid
    
    def get_bot_configs(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
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
    
    def delete_bot_config(self, bot_id: int):
        """删除Bot配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bot_configs WHERE id = ?", (bot_id,))
    
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
    
    def get_channel_mappings(self, kook_channel_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取频道映射"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if kook_channel_id:
                cursor.execute("""
                    SELECT * FROM channel_mappings 
                    WHERE kook_channel_id = ? AND enabled = 1
                """, (kook_channel_id,))
            else:
                cursor.execute("SELECT * FROM channel_mappings")
            return [dict(row) for row in cursor.fetchall()]
    
    # 消息日志
    def add_message_log(self, kook_message_id: str, kook_channel_id: str,
                       content: str, message_type: str, sender_name: str,
                       target_platform: str, target_channel: str,
                       status: str, error_message: Optional[str] = None,
                       latency_ms: Optional[int] = None) -> int:
        """添加消息日志"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
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
            except sqlite3.IntegrityError:
                # 消息已存在，返回已有ID
                cursor.execute(
                    "SELECT id FROM message_logs WHERE kook_message_id = ?",
                    (kook_message_id,)
                )
                row = cursor.fetchone()
                return row[0] if row else 0
    
    def get_message_logs(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
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
        """设置配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value)
                VALUES (?, ?)
            """, (key, value))
    
    def get_config(self, key: str) -> Optional[str]:
        """获取配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_config WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def delete_config(self, key: str):
        """删除配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM system_config WHERE key = ?", (key,))
    
    # 别名方法（兼容scraper.py中的调用）
    def set_system_config(self, key: str, value: str):
        """设置系统配置（别名）"""
        return self.set_config(key, value)
    
    def get_system_config(self, key: str) -> Optional[str]:
        """获取系统配置（别名）"""
        return self.get_config(key)
    
    def delete_system_config(self, key: str):
        """删除系统配置（别名）"""
        return self.delete_config(key)


# 创建全局数据库实例
db = Database()