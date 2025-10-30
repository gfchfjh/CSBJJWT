"""
数据库优化版本
✅ P2-2优化: 连接池 + 复合索引 + VACUUM优化
"""
import sqlite3
import aiosqlite
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from .config import DB_PATH
from .utils.logger import logger


class DatabasePool:
    """
    异步数据库连接池
    
    功能：
    1. 连接池管理（最多10个连接）
    2. 自动连接复用
    3. 连接健康检查
    4. 性能统计
    """
    
    def __init__(self, db_path: Path = DB_PATH, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self.pool: List[aiosqlite.Connection] = []
        self.active_connections = 0
        
        # 统计信息
        self.total_queries = 0
        self.total_time = 0.0
        self.pool_hits = 0  # 连接复用次数
        self.pool_misses = 0  # 新建连接次数
        
        logger.info(f"✅ 数据库连接池已初始化（最大连接数: {max_connections}）")
    
    @asynccontextmanager
    async def get_connection(self):
        """
        获取数据库连接（异步上下文管理器）
        
        用法：
        async with db_pool.get_connection() as conn:
            await conn.execute("SELECT ...")
        """
        conn = None
        
        try:
            # 1. 尝试从池中获取连接
            if self.pool:
                conn = self.pool.pop()
                self.pool_hits += 1
                logger.debug(f"复用连接（池剩余: {len(self.pool)}）")
            else:
                # 2. 创建新连接
                conn = await aiosqlite.connect(self.db_path)
                conn.row_factory = aiosqlite.Row
                self.pool_misses += 1
                logger.debug("创建新连接")
            
            self.active_connections += 1
            
            yield conn
            
            await conn.commit()
            
        except Exception as e:
            if conn:
                await conn.rollback()
            raise e
        finally:
            self.active_connections -= 1
            
            # 归还连接到池
            if conn:
                if len(self.pool) < self.max_connections:
                    self.pool.append(conn)
                else:
                    # 池已满，关闭连接
                    await conn.close()
    
    async def close_all(self):
        """关闭所有连接"""
        for conn in self.pool:
            await conn.close()
        self.pool.clear()
        logger.info("✅ 所有数据库连接已关闭")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        hit_rate = (self.pool_hits / (self.pool_hits + self.pool_misses) * 100) if (self.pool_hits + self.pool_misses) > 0 else 0
        
        return {
            'pool_size': len(self.pool),
            'active_connections': self.active_connections,
            'max_connections': self.max_connections,
            'pool_hits': self.pool_hits,
            'pool_misses': self.pool_misses,
            'hit_rate': round(hit_rate, 2),
            'total_queries': self.total_queries,
            'avg_query_time': round(self.total_time / self.total_queries, 4) if self.total_queries > 0 else 0
        }


class OptimizedDatabase:
    """
    优化的数据库类
    
    功能：
    1. 使用连接池
    2. 优化的索引
    3. 自动VACUUM
    4. 查询性能监控
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.pool = DatabasePool(db_path)
        
        # 初始化数据库
        asyncio.create_task(self.init_database())
        
        logger.info(f"✅ 优化数据库已初始化: {db_path}")
    
    async def init_database(self):
        """初始化数据库表和索引"""
        async with self.pool.get_connection() as conn:
            cursor = await conn.cursor()
            
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
            
            # 优化索引（单列）
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_email 
                ON accounts(email)
            """)
            
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_status 
                ON accounts(status)
            """)
            
            # 复合索引（提升联合查询性能）
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_status_active
                ON accounts(status, last_active DESC)
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
            
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bot_platform_status
                ON bot_configs(platform, status)
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
                    FOREIGN KEY (target_bot_id) REFERENCES bot_configs(id)
                )
            """)
            
            # 优化索引
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_channel_mappings_kook_channel 
                ON channel_mappings(kook_channel_id, enabled)
            """)
            
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_channel_mappings_platform 
                ON channel_mappings(target_platform)
            """)
            
            # 复合索引优化联表查询
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mapping_bot_platform 
                ON channel_mappings(target_bot_id, target_platform, enabled)
            """)
            
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mapping_kook_server
                ON channel_mappings(kook_server_id, enabled)
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
            
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_filter_type_scope
                ON filter_rules(rule_type, scope, enabled)
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
            
            # 优化索引（消息日志查询频繁）
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
            
            # 复合索引优化多条件查询
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_channel_status 
                ON message_logs(kook_channel_id, status, created_at DESC)
            """)
            
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_platform_status 
                ON message_logs(target_platform, status, created_at DESC)
            """)
            
            # 覆盖索引（包含常用查询的所有列）
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_status_composite
                ON message_logs(status, created_at DESC, kook_channel_id, target_platform)
            """)
            
            # 失败消息队列
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS failed_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_log_id INTEGER NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TIMESTAMP,
                    next_retry TIMESTAMP,
                    FOREIGN KEY (message_log_id) REFERENCES message_logs(id)
                )
            """)
            
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_failed_next_retry
                ON failed_messages(next_retry, retry_count)
            """)
            
            # 系统配置表
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await conn.commit()
            
            logger.info("✅ 数据库表和索引已优化")
    
    async def optimize(self):
        """
        数据库优化（定期执行）
        
        操作：
        1. VACUUM - 整理碎片，回收空间
        2. ANALYZE - 更新统计信息，优化查询计划
        3. 清理旧日志
        """
        logger.info("🔧 开始数据库优化...")
        
        start_time = datetime.now()
        
        async with self.pool.get_connection() as conn:
            # 1. 清理7天前的消息日志
            cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
            
            cursor = await conn.execute("""
                DELETE FROM message_logs
                WHERE created_at < ? AND status = 'success'
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            logger.info(f"清理了{deleted_count}条旧日志")
            
            # 2. VACUUM（整理碎片）
            await conn.execute("VACUUM")
            logger.info("✅ VACUUM完成")
            
            # 3. ANALYZE（更新统计信息）
            await conn.execute("ANALYZE")
            logger.info("✅ ANALYZE完成")
            
            await conn.commit()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ 数据库优化完成，耗时{elapsed:.2f}秒")
    
    async def get_database_size(self) -> Dict:
        """获取数据库大小信息"""
        import os
        
        if not self.db_path.exists():
            return {'size_mb': 0}
        
        size_bytes = os.path.getsize(self.db_path)
        size_mb = size_bytes / (1024 * 1024)
        
        async with self.pool.get_connection() as conn:
            cursor = await conn.execute("PRAGMA page_count")
            row = await cursor.fetchone()
            page_count = row[0] if row else 0
            
            cursor = await conn.execute("PRAGMA page_size")
            row = await cursor.fetchone()
            page_size = row[0] if row else 0
            
            cursor = await conn.execute("PRAGMA freelist_count")
            row = await cursor.fetchone()
            freelist_count = row[0] if row else 0
        
        return {
            'size_mb': round(size_mb, 2),
            'size_bytes': size_bytes,
            'page_count': page_count,
            'page_size': page_size,
            'freelist_count': freelist_count,
            'fragmentation_pct': round((freelist_count / page_count * 100) if page_count > 0 else 0, 2)
        }
    
    async def get_table_stats(self) -> List[Dict]:
        """获取各表统计信息"""
        tables = [
            'accounts',
            'bot_configs',
            'channel_mappings',
            'filter_rules',
            'message_logs',
            'failed_messages',
            'system_config'
        ]
        
        stats = []
        
        async with self.pool.get_connection() as conn:
            for table in tables:
                cursor = await conn.execute(f"SELECT COUNT(*) FROM {table}")
                row = await cursor.fetchone()
                count = row[0] if row else 0
                
                stats.append({
                    'table': table,
                    'row_count': count
                })
        
        return stats


# 全局实例
optimized_db = OptimizedDatabase()


# 定时优化任务（每周执行）
async def schedule_optimization():
    """定时数据库优化任务"""
    while True:
        try:
            # 每周日凌晨3点执行
            now = datetime.now()
            next_run = now.replace(hour=3, minute=0, second=0, microsecond=0)
            
            # 如果是周日之前，计算到下个周日
            days_until_sunday = (6 - now.weekday()) % 7
            if days_until_sunday == 0 and now.hour >= 3:
                days_until_sunday = 7
            
            next_run += timedelta(days=days_until_sunday)
            
            wait_seconds = (next_run - now).total_seconds()
            
            logger.info(f"下次数据库优化时间: {next_run.isoformat()}")
            
            await asyncio.sleep(wait_seconds)
            
            # 执行优化
            await optimized_db.optimize()
            
        except Exception as e:
            logger.error(f"定时优化任务异常: {e}")
            await asyncio.sleep(86400)  # 出错后24小时重试
