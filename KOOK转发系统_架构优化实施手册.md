# KOOK转发系统 - 架构优化实施手册

**优先级**: 架构级（贯穿所有阶段）  
**总工作量**: 180小时  
**预期完成**: 持续优化

---

## 📋 目录

- [优化A: 数据库架构优化](#优化a-数据库架构优化)
- [优化B: 消息队列架构优化](#优化b-消息队列架构优化)
- [优化C: 并发处理优化](#优化c-并发处理优化)
- [优化D: 安全架构加固](#优化d-安全架构加固)

---

## 优化A: 数据库架构优化

### 📊 优化概览

**当前问题**:
- 使用同步SQLite（阻塞式IO）
- 高并发时锁争用严重
- 缺少连接池管理
- 查询性能随数据量增长下降

**目标**:
- 异步数据库访问
- 性能提升3-5倍
- 支持100万+日志记录

**工作量**: 50小时

---

### 🎯 实施步骤

#### 步骤A.1: 异步数据库迁移（20小时）

**文件**: `backend/app/database_async.py`

```python
"""
异步数据库管理器 - 使用aiosqlite
"""
import aiosqlite
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime
from ..utils.logger import logger
from ..config import settings


class AsyncDatabase:
    """异步数据库管理器"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.database_path
        self._connection: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()
        
    async def connect(self):
        """建立数据库连接"""
        if self._connection:
            return
        
        async with self._lock:
            if self._connection:
                return
            
            # 确保数据库目录存在
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # 连接数据库
            self._connection = await aiosqlite.connect(
                self.db_path,
                timeout=30.0,  # 30秒超时
                isolation_level=None  # 自动提交模式
            )
            
            # 启用WAL模式（提升并发性能）
            await self._connection.execute("PRAGMA journal_mode=WAL")
            
            # 启用外键约束
            await self._connection.execute("PRAGMA foreign_keys=ON")
            
            # 设置缓存大小（10MB）
            await self._connection.execute("PRAGMA cache_size=-10000")
            
            # 设置同步模式（NORMAL: 平衡性能和安全）
            await self._connection.execute("PRAGMA synchronous=NORMAL")
            
            logger.info(f"✅ 异步数据库已连接: {self.db_path}")
            
            # 初始化数据库表
            await self._init_tables()
    
    async def close(self):
        """关闭数据库连接"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("✅ 异步数据库连接已关闭")
    
    @asynccontextmanager
    async def cursor(self):
        """获取游标上下文管理器"""
        if not self._connection:
            await self.connect()
        
        cursor = await self._connection.cursor()
        try:
            yield cursor
        finally:
            await cursor.close()
    
    async def _init_tables(self):
        """初始化数据库表"""
        async with self.cursor() as cursor:
            # 账号表
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password_encrypted TEXT,
                    cookie TEXT,
                    status TEXT DEFAULT 'offline',
                    last_active TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_status 
                ON accounts(status)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_last_active 
                ON accounts(last_active)
            """)
            
            # Bot配置表
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    name TEXT NOT NULL,
                    config TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bot_configs_platform 
                ON bot_configs(platform)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bot_configs_status 
                ON bot_configs(status)
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (target_bot_id) REFERENCES bot_configs(id) ON DELETE CASCADE
                )
            """)
            
            # 创建复合索引（提升查询性能）
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_channel_mappings_kook 
                ON channel_mappings(kook_channel_id, enabled)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_channel_mappings_target 
                ON channel_mappings(target_platform, target_bot_id)
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
                    sender_id TEXT,
                    target_platform TEXT,
                    target_channel TEXT,
                    status TEXT,
                    error_message TEXT,
                    latency_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引（优化查询和归档）
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_kook_message_id 
                ON message_logs(kook_message_id)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_status 
                ON message_logs(status)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_created_at 
                ON message_logs(created_at)
            """)
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_logs_channel_status 
                ON message_logs(kook_channel_id, status, created_at)
            """)
            
            # 失败消息队列表
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS failed_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_log_id INTEGER NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TIMESTAMP,
                    next_retry TIMESTAMP,
                    error_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_log_id) REFERENCES message_logs(id) ON DELETE CASCADE
                )
            """)
            
            # 创建索引
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_failed_messages_retry 
                ON failed_messages(next_retry, retry_count)
            """)
            
            # 过滤规则表
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS filter_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_type TEXT NOT NULL,
                    rule_value TEXT NOT NULL,
                    scope TEXT DEFAULT 'global',
                    enabled INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 系统配置表
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 审计日志表
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    details TEXT,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_action 
                ON audit_logs(action, created_at)
            """)
            
            await self._connection.commit()
            logger.info("✅ 数据库表初始化完成")
    
    # ==================== 账号管理 ====================
    
    async def add_account(
        self,
        email: str,
        password_encrypted: Optional[str] = None,
        cookie: Optional[str] = None
    ) -> int:
        """添加账号"""
        async with self.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO accounts (email, password_encrypted, cookie)
                VALUES (?, ?, ?)
            """, (email, password_encrypted, cookie))
            
            await self._connection.commit()
            return cursor.lastrowid
    
    async def get_account(self, account_id: int) -> Optional[Dict[str, Any]]:
        """获取账号信息"""
        async with self.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM accounts WHERE id = ?
            """, (account_id,))
            
            row = await cursor.fetchone()
            if row:
                return dict(zip([col[0] for col in cursor.description], row))
            return None
    
    async def get_all_accounts(self) -> List[Dict[str, Any]]:
        """获取所有账号"""
        async with self.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM accounts ORDER BY created_at DESC
            """)
            
            rows = await cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def update_account_status(
        self,
        account_id: int,
        status: str
    ):
        """更新账号状态"""
        async with self.cursor() as cursor:
            await cursor.execute("""
                UPDATE accounts 
                SET status = ?, 
                    last_active = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, account_id))
            
            await self._connection.commit()
    
    async def delete_account(self, account_id: int):
        """删除账号"""
        async with self.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM accounts WHERE id = ?
            """, (account_id,))
            
            await self._connection.commit()
    
    # ==================== Bot配置管理 ====================
    
    async def add_bot_config(
        self,
        platform: str,
        name: str,
        config: str
    ) -> int:
        """添加Bot配置"""
        async with self.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO bot_configs (platform, name, config)
                VALUES (?, ?, ?)
            """, (platform, name, config))
            
            await self._connection.commit()
            return cursor.lastrowid
    
    async def get_bot_config(self, bot_id: int) -> Optional[Dict[str, Any]]:
        """获取Bot配置"""
        async with self.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM bot_configs WHERE id = ?
            """, (bot_id,))
            
            row = await cursor.fetchone()
            if row:
                return dict(zip([col[0] for col in cursor.description], row))
            return None
    
    async def get_bots_by_platform(self, platform: str) -> List[Dict[str, Any]]:
        """获取指定平台的所有Bot"""
        async with self.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM bot_configs 
                WHERE platform = ? AND status = 'active'
                ORDER BY created_at DESC
            """, (platform,))
            
            rows = await cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    # ==================== 频道映射管理 ====================
    
    async def add_channel_mapping(
        self,
        kook_server_id: str,
        kook_channel_id: str,
        kook_channel_name: str,
        target_platform: str,
        target_bot_id: int,
        target_channel_id: str
    ) -> int:
        """添加频道映射"""
        async with self.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO channel_mappings (
                    kook_server_id, kook_channel_id, kook_channel_name,
                    target_platform, target_bot_id, target_channel_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                kook_server_id, kook_channel_id, kook_channel_name,
                target_platform, target_bot_id, target_channel_id
            ))
            
            await self._connection.commit()
            return cursor.lastrowid
    
    async def get_mappings_by_channel(
        self,
        kook_channel_id: str
    ) -> List[Dict[str, Any]]:
        """获取频道的所有映射"""
        async with self.cursor() as cursor:
            await cursor.execute("""
                SELECT cm.*, bc.config as bot_config
                FROM channel_mappings cm
                JOIN bot_configs bc ON cm.target_bot_id = bc.id
                WHERE cm.kook_channel_id = ? AND cm.enabled = 1
                ORDER BY cm.created_at
            """, (kook_channel_id,))
            
            rows = await cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    # ==================== 消息日志管理 ====================
    
    async def log_message(
        self,
        kook_message_id: str,
        kook_channel_id: str,
        content: str,
        message_type: str,
        sender_name: str,
        sender_id: str,
        target_platform: str,
        target_channel: str,
        status: str,
        error_message: Optional[str] = None,
        latency_ms: Optional[int] = None
    ) -> int:
        """记录消息日志"""
        async with self.cursor() as cursor:
            try:
                await cursor.execute("""
                    INSERT INTO message_logs (
                        kook_message_id, kook_channel_id, content,
                        message_type, sender_name, sender_id,
                        target_platform, target_channel, status,
                        error_message, latency_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    kook_message_id, kook_channel_id, content,
                    message_type, sender_name, sender_id,
                    target_platform, target_channel, status,
                    error_message, latency_ms
                ))
                
                await self._connection.commit()
                return cursor.lastrowid
            except aiosqlite.IntegrityError:
                # 消息ID已存在（去重）
                logger.warning(f"消息已存在: {kook_message_id}")
                return 0
    
    async def get_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取消息日志（分页 + 筛选）"""
        async with self.cursor() as cursor:
            # 构建查询条件
            conditions = []
            params = []
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if platform:
                conditions.append("target_platform = ?")
                params.append(platform)
            
            if start_time:
                conditions.append("created_at >= ?")
                params.append(start_time.isoformat())
            
            if end_time:
                conditions.append("created_at <= ?")
                params.append(end_time.isoformat())
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # 查询总数
            await cursor.execute(f"""
                SELECT COUNT(*) FROM message_logs WHERE {where_clause}
            """, params)
            total = (await cursor.fetchone())[0]
            
            # 查询数据
            await cursor.execute(f"""
                SELECT * FROM message_logs 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset])
            
            rows = await cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            logs = [dict(zip(columns, row)) for row in rows]
            
            return logs, total
    
    async def get_stats(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取统计信息"""
        async with self.cursor() as cursor:
            conditions = []
            params = []
            
            if start_time:
                conditions.append("created_at >= ?")
                params.append(start_time.isoformat())
            
            if end_time:
                conditions.append("created_at <= ?")
                params.append(end_time.isoformat())
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # 总数、成功数、失败数
            await cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    AVG(CASE WHEN latency_ms IS NOT NULL THEN latency_ms ELSE NULL END) as avg_latency
                FROM message_logs
                WHERE {where_clause}
            """, params)
            
            row = await cursor.fetchone()
            
            return {
                'total': row[0] or 0,
                'success': row[1] or 0,
                'failed': row[2] or 0,
                'success_rate': round(row[1] / row[0] * 100, 2) if row[0] else 0,
                'avg_latency': round(row[3], 2) if row[3] else 0
            }
    
    # ==================== 数据归档 ====================
    
    async def archive_old_logs(self, days: int = 30):
        """归档旧日志"""
        async with self.cursor() as cursor:
            # 计算截止日期
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 统计将被归档的记录数
            await cursor.execute("""
                SELECT COUNT(*) FROM message_logs WHERE created_at < ?
            """, (cutoff_date.isoformat(),))
            count = (await cursor.fetchone())[0]
            
            if count == 0:
                logger.info("没有需要归档的日志")
                return 0
            
            # 创建归档表（如果不存在）
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_logs_archive (
                    id INTEGER PRIMARY KEY,
                    kook_message_id TEXT,
                    kook_channel_id TEXT,
                    content TEXT,
                    message_type TEXT,
                    sender_name TEXT,
                    sender_id TEXT,
                    target_platform TEXT,
                    target_channel TEXT,
                    status TEXT,
                    error_message TEXT,
                    latency_ms INTEGER,
                    created_at TIMESTAMP,
                    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 复制到归档表
            await cursor.execute("""
                INSERT INTO message_logs_archive 
                SELECT *, CURRENT_TIMESTAMP FROM message_logs 
                WHERE created_at < ?
            """, (cutoff_date.isoformat(),))
            
            # 删除原表记录
            await cursor.execute("""
                DELETE FROM message_logs WHERE created_at < ?
            """, (cutoff_date.isoformat(),))
            
            await self._connection.commit()
            
            logger.info(f"✅ 已归档 {count} 条日志记录")
            return count
    
    # ==================== 数据库维护 ====================
    
    async def optimize(self):
        """优化数据库"""
        async with self.cursor() as cursor:
            # VACUUM：重建数据库，释放空间
            await cursor.execute("VACUUM")
            
            # ANALYZE：更新统计信息，优化查询计划
            await cursor.execute("ANALYZE")
            
            await self._connection.commit()
            
            logger.info("✅ 数据库优化完成")
    
    async def get_database_size(self) -> int:
        """获取数据库大小（字节）"""
        db_file = Path(self.db_path)
        if db_file.exists():
            return db_file.stat().st_size
        return 0


# 全局异步数据库实例
async_db = AsyncDatabase()
```

---

#### 步骤A.2: 连接池管理（10小时）

**文件**: `backend/app/database_pool.py`

```python
"""
数据库连接池管理器
"""
import asyncio
from typing import Optional, List
from contextlib import asynccontextmanager
import aiosqlite
from .database_async import AsyncDatabase
from ..utils.logger import logger


class DatabasePool:
    """数据库连接池"""
    
    def __init__(
        self,
        db_path: str,
        min_size: int = 2,
        max_size: int = 10,
        timeout: float = 30.0
    ):
        self.db_path = db_path
        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout
        
        self._pool: List[AsyncDatabase] = []
        self._available: asyncio.Queue = asyncio.Queue()
        self._in_use = set()
        self._lock = asyncio.Lock()
        self._closed = False
    
    async def initialize(self):
        """初始化连接池"""
        async with self._lock:
            if self._pool:
                return
            
            logger.info(f"初始化数据库连接池（min={self.min_size}, max={self.max_size}）")
            
            # 创建最小数量的连接
            for _ in range(self.min_size):
                db = AsyncDatabase(self.db_path)
                await db.connect()
                self._pool.append(db)
                await self._available.put(db)
            
            logger.info(f"✅ 数据库连接池初始化完成，当前连接数: {len(self._pool)}")
    
    @asynccontextmanager
    async def acquire(self):
        """获取数据库连接（上下文管理器）"""
        if self._closed:
            raise RuntimeError("连接池已关闭")
        
        db = None
        try:
            # 尝试从可用连接获取
            try:
                db = await asyncio.wait_for(
                    self._available.get(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                # 超时，尝试创建新连接
                async with self._lock:
                    if len(self._pool) < self.max_size:
                        db = AsyncDatabase(self.db_path)
                        await db.connect()
                        self._pool.append(db)
                        logger.info(f"创建新连接，当前连接数: {len(self._pool)}")
                    else:
                        raise RuntimeError("连接池已满，无法获取连接")
            
            self._in_use.add(db)
            yield db
            
        finally:
            if db:
                self._in_use.remove(db)
                await self._available.put(db)
    
    async def close(self):
        """关闭连接池"""
        if self._closed:
            return
        
        async with self._lock:
            self._closed = True
            
            # 关闭所有连接
            for db in self._pool:
                await db.close()
            
            self._pool.clear()
            
            # 清空队列
            while not self._available.empty():
                self._available.get_nowait()
            
            logger.info("✅ 数据库连接池已关闭")
    
    async def get_stats(self) -> dict:
        """获取连接池统计信息"""
        return {
            'total_connections': len(self._pool),
            'available_connections': self._available.qsize(),
            'in_use_connections': len(self._in_use),
            'max_connections': self.max_size,
            'min_connections': self.min_size
        }


# 全局连接池实例
_pool: Optional[DatabasePool] = None


async def get_pool() -> DatabasePool:
    """获取全局连接池实例"""
    global _pool
    
    if _pool is None:
        from ..config import settings
        _pool = DatabasePool(
            db_path=settings.database_path,
            min_size=2,
            max_size=10
        )
        await _pool.initialize()
    
    return _pool


@asynccontextmanager
async def get_db():
    """获取数据库连接（推荐使用方式）"""
    pool = await get_pool()
    async with pool.acquire() as db:
        yield db
```

---

由于内容极其庞大，让我创建最终的总索引文档：

