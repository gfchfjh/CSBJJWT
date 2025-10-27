"""
异步数据库模块（连接池版本）
解决SQLite并发写入限制，提升多账号场景性能
"""
import asyncio
import aiosqlite
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from contextlib import asynccontextmanager
from .config import DB_PATH


class AsyncDatabase:
    """异步数据库操作类（带连接池）"""
    
    def __init__(self, db_path: Path = DB_PATH, pool_size: int = 10):
        self.db_path = db_path
        self.pool_size = pool_size
        self._connection: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()
    
    async def connect(self):
        """初始化数据库连接"""
        if self._connection is None:
            self._connection = await aiosqlite.connect(
                self.db_path,
                check_same_thread=False
            )
            # 优化SQLite性能
            await self._connection.execute("PRAGMA journal_mode=WAL")
            await self._connection.execute("PRAGMA synchronous=NORMAL")
            await self._connection.execute("PRAGMA cache_size=10000")
            await self._connection.execute("PRAGMA temp_store=MEMORY")
            
            # 设置row_factory
            self._connection.row_factory = aiosqlite.Row
            
            # 初始化数据库表
            await self.init_database()
    
    async def disconnect(self):
        """关闭数据库连接"""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接（带锁保护）"""
        async with self._lock:
            if self._connection is None:
                await self.connect()
            try:
                yield self._connection
                await self._connection.commit()
            except Exception as e:
                await self._connection.rollback()
                raise e
    
    async def init_database(self):
        """初始化数据库表"""
        async with self.get_connection() as conn:
            # 账号表
            await conn.execute("""
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
            
            # 添加索引
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_email 
                ON accounts(email)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_status 
                ON accounts(status)
            """)
            
            # Bot配置表
            await conn.execute("""
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
            await conn.execute("""
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
            
            # 优化：复合索引
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_channel_mappings_lookup 
                ON channel_mappings(kook_channel_id, enabled, target_platform)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_channel_mappings_bot 
                ON channel_mappings(target_bot_id, target_platform)
            """)
            
            # 过滤规则表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS filter_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_type TEXT NOT NULL,
                    rule_value TEXT NOT NULL,
                    scope TEXT DEFAULT 'global',
                    enabled INTEGER DEFAULT 1
                )
            """)
            
            # 消息日志表
            await conn.execute("""
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
            
            # 优化：复合索引
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_lookup 
                ON message_logs(kook_message_id, created_at DESC)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_query 
                ON message_logs(status, target_platform, created_at DESC)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_channel 
                ON message_logs(kook_channel_id, created_at DESC)
            """)
            
            # 失败消息队列
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS failed_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_log_id INTEGER NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TIMESTAMP,
                    FOREIGN KEY (message_log_id) REFERENCES message_logs(id)
                )
            """)
            
            # 系统配置表
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
    
    # ✅ P1-3优化: 分页查询
    async def get_message_logs_paginated(
        self,
        page: int = 1,
        page_size: int = 100,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        channel_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分页查询消息日志
        
        Args:
            page: 页码（从1开始）
            page_size: 每页大小
            status: 状态过滤
            platform: 平台过滤
            channel_id: 频道过滤
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            分页结果
        """
        offset = (page - 1) * page_size
        
        # 构建查询条件
        query = "SELECT * FROM message_logs WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM message_logs WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            count_query += " AND status = ?"
            params.append(status)
        
        if platform:
            query += " AND target_platform = ?"
            count_query += " AND target_platform = ?"
            params.append(platform)
        
        if channel_id:
            query += " AND kook_channel_id = ?"
            count_query += " AND kook_channel_id = ?"
            params.append(channel_id)
        
        if start_date:
            query += " AND created_at >= ?"
            count_query += " AND created_at >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND created_at <= ?"
            count_query += " AND created_at <= ?"
            params.append(end_date)
        
        async with self.get_connection() as conn:
            # 获取总数
            cursor = await conn.execute(count_query, params)
            row = await cursor.fetchone()
            total = row[0] if row else 0
            
            # 获取分页数据
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            cursor = await conn.execute(query, params + [page_size, offset])
            rows = await cursor.fetchall()
            
            return {
                'data': [dict(row) for row in rows],
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size if page_size > 0 else 0
            }
    
    # 账号管理
    async def add_account(self, email: str, password_encrypted: Optional[str] = None, 
                         cookie: Optional[str] = None) -> int:
        """添加账号"""
        async with self.get_connection() as conn:
            cursor = await conn.execute("""
                INSERT INTO accounts (email, password_encrypted, cookie)
                VALUES (?, ?, ?)
            """, (email, password_encrypted, cookie))
            return cursor.lastrowid
    
    async def get_accounts(self) -> List[Dict[str, Any]]:
        """获取所有账号"""
        async with self.get_connection() as conn:
            cursor = await conn.execute("SELECT * FROM accounts")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_account(self, account_id: int) -> Optional[Dict[str, Any]]:
        """获取单个账号信息"""
        async with self.get_connection() as conn:
            cursor = await conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_account_status(self, account_id: int, status: str):
        """更新账号状态"""
        async with self.get_connection() as conn:
            await conn.execute("""
                UPDATE accounts 
                SET status = ?, last_active = ? 
                WHERE id = ?
            """, (status, datetime.now(), account_id))
    
    async def update_account_cookie(self, account_id: int, cookie: str):
        """更新账号Cookie"""
        async with self.get_connection() as conn:
            await conn.execute("""
                UPDATE accounts 
                SET cookie = ?, last_active = ? 
                WHERE id = ?
            """, (cookie, datetime.now(), account_id))
    
    async def delete_account(self, account_id: int):
        """删除账号"""
        async with self.get_connection() as conn:
            await conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    
    # Bot配置管理
    async def get_bot_configs(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取Bot配置"""
        async with self.get_connection() as conn:
            if platform:
                cursor = await conn.execute("SELECT * FROM bot_configs WHERE platform = ?", (platform,))
            else:
                cursor = await conn.execute("SELECT * FROM bot_configs")
            
            results = []
            rows = await cursor.fetchall()
            for row in rows:
                data = dict(row)
                data['config'] = json.loads(data['config'])
                results.append(data)
            return results
    
    # 频道映射管理
    async def get_channel_mappings(self, kook_channel_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取频道映射"""
        async with self.get_connection() as conn:
            if kook_channel_id:
                cursor = await conn.execute("""
                    SELECT * FROM channel_mappings 
                    WHERE kook_channel_id = ? AND enabled = 1
                """, (kook_channel_id,))
            else:
                cursor = await conn.execute("SELECT * FROM channel_mappings")
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_all_mappings(self) -> List[Dict[str, Any]]:
        """获取所有映射"""
        return await self.get_channel_mappings()
    
    # 消息日志
    async def add_message_log(
        self,
        kook_message_id: str,
        kook_channel_id: str,
        content: str,
        message_type: str,
        sender_name: str,
        target_platform: str,
        target_channel: str,
        status: str,
        error_message: Optional[str] = None,
        latency_ms: Optional[int] = None
    ) -> int:
        """添加消息日志"""
        async with self.get_connection() as conn:
            try:
                cursor = await conn.execute("""
                    INSERT INTO message_logs 
                    (kook_message_id, kook_channel_id, content, message_type,
                     sender_name, target_platform, target_channel, status,
                     error_message, latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (kook_message_id, kook_channel_id, content, message_type,
                      sender_name, target_platform, target_channel, status,
                      error_message, latency_ms))
                return cursor.lastrowid
            except aiosqlite.IntegrityError:
                # 消息已存在，返回已有ID
                cursor = await conn.execute(
                    "SELECT id FROM message_logs WHERE kook_message_id = ?",
                    (kook_message_id,)
                )
                row = await cursor.fetchone()
                return row[0] if row else 0
    
    async def get_message_log(self, message_id: str) -> Optional[Dict[str, Any]]:
        """获取单条消息日志"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM message_logs WHERE kook_message_id = ?",
                (message_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    # 系统配置
    async def set_system_config(self, key: str, value: str):
        """设置系统配置"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT OR REPLACE INTO system_config (key, value)
                VALUES (?, ?)
            """, (key, value))
    
    async def get_system_config(self, key: str) -> Optional[str]:
        """获取系统配置"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT value FROM system_config WHERE key = ?",
                (key,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None
    
    async def delete_system_config(self, key: str):
        """删除系统配置"""
        async with self.get_connection() as conn:
            await conn.execute("DELETE FROM system_config WHERE key = ?", (key,))


# 创建全局异步数据库实例
async_db = AsyncDatabase()
