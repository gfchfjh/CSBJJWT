"""
✅ P2-3新增：完整的异步数据库模块（使用 aiosqlite）
相比同步版本的优势：
1. 不阻塞事件循环
2. 提升并发性能
3. 与FastAPI异步框架完美配合
"""
import aiosqlite
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from contextlib import asynccontextmanager
from .config import DB_PATH
from .utils.logger import logger


class AsyncDatabase:
    """异步数据库操作类"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._connection = None
    
    async def connect(self):
        """建立数据库连接"""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self.init_database()
        logger.info(f"✅ 异步数据库已连接: {self.db_path}")
    
    async def close(self):
        """关闭数据库连接"""
        if self._connection:
            await self._connection.close()
            logger.info("✅ 数据库连接已关闭")
    
    @asynccontextmanager
    async def transaction(self):
        """事务上下文管理器"""
        async with self._connection as conn:
            try:
                await conn.execute("BEGIN")
                yield conn
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                logger.error(f"数据库事务回滚: {str(e)}")
                raise
    
    async def init_database(self):
        """
        初始化数据库表
        """
        async with self._connection.cursor() as cursor:
            # 账号表
            await cursor.execute("""
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
            
            # 索引
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_email 
                ON accounts(email)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_status 
                ON accounts(status)
            """)
            
            # Bot配置表
            await cursor.execute("""
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
            await cursor.execute("""
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
            
            # 索引
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_channel_mappings_kook_channel 
                ON channel_mappings(kook_channel_id, enabled)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_channel_mappings_platform 
                ON channel_mappings(target_platform)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mapping_bot_platform 
                ON channel_mappings(target_bot_id, target_platform)
            """)
            
            # 过滤规则表
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS filter_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_type TEXT NOT NULL,
                    rule_value TEXT NOT NULL,
                    scope TEXT DEFAULT 'global',
                    enabled INTEGER DEFAULT 1
                )
            """)
            
            # 消息日志表
            await cursor.execute("""
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
            
            # 索引
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_kook_id 
                ON message_logs(kook_message_id)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_status 
                ON message_logs(status)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_created 
                ON message_logs(created_at DESC)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_channel 
                ON message_logs(kook_channel_id, created_at DESC)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_platform_status 
                ON message_logs(target_platform, status)
            """)
            
            # 失败消息队列
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS failed_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_log_id INTEGER NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TIMESTAMP,
                    FOREIGN KEY (message_log_id) REFERENCES message_logs(id)
                )
            """)
            
            # 系统配置表
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            await self._connection.commit()
            logger.info("✅ 数据库表初始化完成")
    
    # ============ 账号管理 ============
    
    async def add_account(self, email: str, password: Optional[str] = None, 
                         cookie: Optional[str] = None) -> int:
        """添加账号"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO accounts (email, password_encrypted, cookie) VALUES (?, ?, ?)",
                (email, password, cookie)
            )
            await self._connection.commit()
            return cursor.lastrowid
    
    async def get_accounts(self, status: Optional[str] = None) -> List[Dict]:
        """获取账号列表"""
        async with self._connection.cursor() as cursor:
            if status:
                await cursor.execute(
                    "SELECT * FROM accounts WHERE status = ? ORDER BY created_at DESC",
                    (status,)
                )
            else:
                await cursor.execute("SELECT * FROM accounts ORDER BY created_at DESC")
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_account(self, account_id: int) -> Optional[Dict]:
        """获取单个账号"""
        async with self._connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_account_status(self, account_id: int, status: str):
        """更新账号状态"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE accounts SET status = ?, last_active = ? WHERE id = ?",
                (status, datetime.now(), account_id)
            )
            await self._connection.commit()
    
    async def delete_account(self, account_id: int):
        """删除账号"""
        async with self._connection.cursor() as cursor:
            await cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            await self._connection.commit()
    
    # ============ Bot配置管理 ============
    
    async def add_bot_config(self, platform: str, name: str, config: Dict) -> int:
        """添加Bot配置"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO bot_configs (platform, name, config) VALUES (?, ?, ?)",
                (platform, name, json.dumps(config))
            )
            await self._connection.commit()
            return cursor.lastrowid
    
    async def get_bot_configs(self, platform: Optional[str] = None) -> List[Dict]:
        """获取Bot配置列表"""
        async with self._connection.cursor() as cursor:
            if platform:
                await cursor.execute(
                    "SELECT * FROM bot_configs WHERE platform = ? ORDER BY created_at DESC",
                    (platform,)
                )
            else:
                await cursor.execute("SELECT * FROM bot_configs ORDER BY created_at DESC")
            
            rows = await cursor.fetchall()
            result = []
            for row in rows:
                bot = dict(row)
                bot['config'] = json.loads(bot['config'])
                result.append(bot)
            return result
    
    async def get_bot_config(self, bot_id: int) -> Optional[Dict]:
        """获取单个Bot配置"""
        async with self._connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM bot_configs WHERE id = ?", (bot_id,))
            row = await cursor.fetchone()
            if row:
                bot = dict(row)
                bot['config'] = json.loads(bot['config'])
                return bot
            return None
    
    async def update_bot_config(self, bot_id: int, config: Dict):
        """更新Bot配置"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE bot_configs SET config = ? WHERE id = ?",
                (json.dumps(config), bot_id)
            )
            await self._connection.commit()
    
    async def delete_bot_config(self, bot_id: int):
        """删除Bot配置"""
        async with self._connection.cursor() as cursor:
            await cursor.execute("DELETE FROM bot_configs WHERE id = ?", (bot_id,))
            await self._connection.commit()
    
    # ============ 频道映射管理 ============
    
    async def add_mapping(self, kook_server_id: str, kook_channel_id: str,
                         kook_channel_name: str, target_platform: str,
                         target_bot_id: int, target_channel_id: str) -> int:
        """添加频道映射"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                """INSERT INTO channel_mappings 
                (kook_server_id, kook_channel_id, kook_channel_name, 
                 target_platform, target_bot_id, target_channel_id)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (kook_server_id, kook_channel_id, kook_channel_name,
                 target_platform, target_bot_id, target_channel_id)
            )
            await self._connection.commit()
            return cursor.lastrowid
    
    async def get_mappings(self, enabled_only: bool = False) -> List[Dict]:
        """获取频道映射列表"""
        async with self._connection.cursor() as cursor:
            if enabled_only:
                await cursor.execute(
                    "SELECT * FROM channel_mappings WHERE enabled = 1"
                )
            else:
                await cursor.execute("SELECT * FROM channel_mappings")
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_mappings_by_channel(self, kook_channel_id: str) -> List[Dict]:
        """根据KOOK频道ID获取映射"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM channel_mappings WHERE kook_channel_id = ? AND enabled = 1",
                (kook_channel_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def delete_mapping(self, mapping_id: int):
        """删除频道映射"""
        async with self._connection.cursor() as cursor:
            await cursor.execute("DELETE FROM channel_mappings WHERE id = ?", (mapping_id,))
            await self._connection.commit()
    
    # ============ 消息日志管理 ============
    
    async def add_message_log(self, kook_message_id: str, kook_channel_id: str,
                             content: str, message_type: str, sender_name: str,
                             target_platform: str, target_channel: str,
                             status: str, latency_ms: Optional[int] = None,
                             error_message: Optional[str] = None) -> int:
        """添加消息日志"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                """INSERT INTO message_logs 
                (kook_message_id, kook_channel_id, content, message_type, sender_name,
                 target_platform, target_channel, status, latency_ms, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (kook_message_id, kook_channel_id, content, message_type, sender_name,
                 target_platform, target_channel, status, latency_ms, error_message)
            )
            await self._connection.commit()
            return cursor.lastrowid
    
    async def get_message_logs(self, status: Optional[str] = None,
                               platform: Optional[str] = None,
                               limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取消息日志"""
        async with self._connection.cursor() as cursor:
            query = "SELECT * FROM message_logs WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if platform:
                query += " AND target_platform = ?"
                params.append(platform)
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            await cursor.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_message_stats(self) -> Dict[str, Any]:
        """获取消息统计"""
        async with self._connection.cursor() as cursor:
            # 今日消息数
            await cursor.execute(
                "SELECT COUNT(*) as total FROM message_logs WHERE DATE(created_at) = DATE('now')"
            )
            total = (await cursor.fetchone())['total']
            
            # 成功数
            await cursor.execute(
                """SELECT COUNT(*) as success FROM message_logs 
                WHERE DATE(created_at) = DATE('now') AND status = 'success'"""
            )
            success = (await cursor.fetchone())['success']
            
            # 平均延迟
            await cursor.execute(
                """SELECT AVG(latency_ms) as avg_latency FROM message_logs 
                WHERE DATE(created_at) = DATE('now') AND status = 'success'"""
            )
            avg_latency = (await cursor.fetchone())['avg_latency'] or 0
            
            success_rate = (success / total * 100) if total > 0 else 0
            
            return {
                "total": total,
                "success": success,
                "success_rate": round(success_rate, 1),
                "avg_latency": round(avg_latency, 0),
                "failed": total - success
            }
    
    async def check_message_exists(self, kook_message_id: str) -> bool:
        """检查消息是否已存在（去重）"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(
                "SELECT 1 FROM message_logs WHERE kook_message_id = ?",
                (kook_message_id,)
            )
            return await cursor.fetchone() is not None
    
    # ============ 通用方法 ============
    
    async def execute(self, query: str, params: tuple = ()):
        """执行SQL语句"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, params)
            await self._connection.commit()
            return cursor
    
    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """查询单条记录"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, params)
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """查询多条记录"""
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


# 全局异步数据库实例
async_db = AsyncDatabase()
