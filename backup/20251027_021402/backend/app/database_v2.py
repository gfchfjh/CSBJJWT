"""
数据库模块 v2.0 - 性能优化版
版本: v6.0.0
作者: KOOK Forwarder Team

优化点:
1. 完整的索引策略
2. 查询优化（LIMIT + OFFSET）
3. 连接池优化
4. 批量操作支持
5. 异步操作（aiosqlite）
6. 事务优化

性能目标:
- 查询<100ms（1000条记录）
- 插入<50ms（单条）
- 批量插入<200ms（100条）
"""

import sqlite3
import aiosqlite
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from contextlib import asynccontextmanager
from ..config import DB_PATH
from ..utils.logger import logger


class DatabaseV2:
    """数据库操作类 v2.0 - 性能优化版"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._connection_pool = None
        self.init_database()
        
        # 统计信息
        self.stats = {
            'queries': 0,
            'inserts': 0,
            'updates': 0,
            'deletes': 0,
            'total_query_time_ms': 0.0,
            'avg_query_time_ms': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    @asynccontextmanager
    async def get_async_connection(self):
        """获取异步数据库连接"""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        try:
            yield conn
            await conn.commit()
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await conn.close()
    
    def init_database(self):
        """初始化数据库表（同步方式，启动时调用一次）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 启用WAL模式（提升并发性能）
            cursor.execute("PRAGMA journal_mode=WAL")
            
            # 优化设置
            cursor.execute("PRAGMA synchronous=NORMAL")  # 平衡性能和安全
            cursor.execute("PRAGMA cache_size=10000")    # 增大缓存
            cursor.execute("PRAGMA temp_store=MEMORY")   # 临时表在内存
            
            # 账号表
            cursor.execute("""
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
            
            # 账号表索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_email ON accounts(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_last_active ON accounts(last_active DESC)")
            
            # Bot配置表
            cursor.execute("""
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
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bots_platform ON bot_configs(platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bots_status ON bot_configs(status)")
            
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (target_bot_id) REFERENCES bot_configs(id) ON DELETE CASCADE
                )
            """)
            
            # 频道映射索引（关键性能优化）
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mappings_kook_channel ON channel_mappings(kook_channel_id, enabled)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mappings_platform ON channel_mappings(target_platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mappings_bot ON channel_mappings(target_bot_id, enabled)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mappings_server ON channel_mappings(kook_server_id)")
            
            # 复合索引（优化联表查询）
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mappings_compound 
                ON channel_mappings(kook_channel_id, target_platform, enabled)
            """)
            
            # 过滤规则表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS filter_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_type TEXT NOT NULL,
                    rule_value TEXT NOT NULL,
                    scope TEXT DEFAULT 'global',
                    enabled INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_filter_type ON filter_rules(rule_type, enabled)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_filter_scope ON filter_rules(scope, enabled)")
            
            # 消息日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kook_message_id TEXT NOT NULL UNIQUE,
                    kook_channel_id TEXT NOT NULL,
                    kook_server_id TEXT,
                    content TEXT,
                    message_type TEXT,
                    sender_id TEXT,
                    sender_name TEXT,
                    target_platform TEXT,
                    target_channel TEXT,
                    target_bot_id INTEGER,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    latency_ms INTEGER,
                    retry_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 消息日志索引（关键性能优化）
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_logs_message_id ON message_logs(kook_message_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_status ON message_logs(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_created ON message_logs(created_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_channel ON message_logs(kook_channel_id, created_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_platform ON message_logs(target_platform, created_at DESC)")
            
            # 复合索引（优化复杂查询）
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_channel_status 
                ON message_logs(kook_channel_id, status, created_at DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_platform_status 
                ON message_logs(target_platform, status, created_at DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_sender 
                ON message_logs(sender_id, created_at DESC)
            """)
            
            # 失败消息队列
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS failed_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_log_id INTEGER NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TIMESTAMP,
                    next_retry TIMESTAMP,
                    error_type TEXT,
                    FOREIGN KEY (message_log_id) REFERENCES message_logs(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_failed_retry ON failed_messages(next_retry)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_failed_count ON failed_messages(retry_count)")
            
            # 系统配置表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 图片Token缓存表（可选，如果需要持久化）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS image_tokens (
                    filepath TEXT PRIMARY KEY,
                    token TEXT NOT NULL,
                    expire_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_expire ON image_tokens(expire_at)")
            
            conn.commit()
            logger.info("✅ 数据库表初始化完成")
            
            # 分析表以优化查询计划
            cursor.execute("ANALYZE")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # ========== 异步查询方法 ==========
    
    async def get_message_logs(self, 
                               limit: int = 100,
                               offset: int = 0,
                               status: Optional[str] = None,
                               channel_id: Optional[str] = None,
                               platform: Optional[str] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Tuple[List[Dict], int]:
        """
        获取消息日志（优化版，支持分页和过滤）
        
        Args:
            limit: 每页数量
            offset: 偏移量
            status: 状态过滤
            channel_id: 频道ID过滤
            platform: 平台过滤
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            (日志列表, 总数)
        """
        import time as time_module
        start_time = time_module.time()
        
        async with self.get_async_connection() as conn:
            # 构建查询
            where_clauses = []
            params = []
            
            if status:
                where_clauses.append("status = ?")
                params.append(status)
            
            if channel_id:
                where_clauses.append("kook_channel_id = ?")
                params.append(channel_id)
            
            if platform:
                where_clauses.append("target_platform = ?")
                params.append(platform)
            
            if start_date:
                where_clauses.append("created_at >= ?")
                params.append(start_date.isoformat())
            
            if end_date:
                where_clauses.append("created_at <= ?")
                params.append(end_date.isoformat())
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # 查询总数（使用覆盖索引）
            count_sql = f"SELECT COUNT(*) FROM message_logs WHERE {where_sql}"
            cursor = await conn.execute(count_sql, params)
            row = await cursor.fetchone()
            total = row[0] if row else 0
            
            # 查询数据（使用索引优化）
            query_sql = f"""
                SELECT * FROM message_logs 
                WHERE {where_sql}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            cursor = await conn.execute(query_sql, params)
            rows = await cursor.fetchall()
            logs = [dict(row) for row in rows]
            
            # 统计
            query_time = (time_module.time() - start_time) * 1000
            self.stats['queries'] += 1
            self.stats['total_query_time_ms'] += query_time
            self.stats['avg_query_time_ms'] = self.stats['total_query_time_ms'] / self.stats['queries']
            
            logger.debug(f"查询日志耗时: {query_time:.2f}ms, 结果: {len(logs)}条/{total}总数")
            
            return logs, total
    
    async def add_message_log_batch(self, messages: List[Dict]) -> int:
        """
        批量添加消息日志（性能优化）
        
        Args:
            messages: 消息列表
            
        Returns:
            成功插入的数量
        """
        if not messages:
            return 0
        
        import time as time_module
        start_time = time_module.time()
        
        async with self.get_async_connection() as conn:
            # 使用事务批量插入
            cursor = await conn.cursor()
            
            insert_sql = """
                INSERT OR IGNORE INTO message_logs 
                (kook_message_id, kook_channel_id, kook_server_id, content, 
                 message_type, sender_id, sender_name, target_platform, 
                 target_channel, target_bot_id, status, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = []
            for msg in messages:
                values.append((
                    msg.get('kook_message_id'),
                    msg.get('kook_channel_id'),
                    msg.get('kook_server_id'),
                    msg.get('content'),
                    msg.get('message_type', 'text'),
                    msg.get('sender_id'),
                    msg.get('sender_name'),
                    msg.get('target_platform'),
                    msg.get('target_channel'),
                    msg.get('target_bot_id'),
                    msg.get('status', 'pending'),
                    msg.get('latency_ms', 0)
                ))
            
            await cursor.executemany(insert_sql, values)
            inserted = cursor.rowcount
            
            insert_time = (time_module.time() - start_time) * 1000
            self.stats['inserts'] += inserted
            
            logger.debug(f"批量插入{inserted}条日志耗时: {insert_time:.2f}ms")
            
            return inserted
    
    async def cleanup_old_logs(self, days: int = 7) -> int:
        """
        清理旧日志（性能优化）
        
        Args:
            days: 保留天数
            
        Returns:
            删除的记录数
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        async with self.get_async_connection() as conn:
            cursor = await conn.execute(
                "DELETE FROM message_logs WHERE created_at < ? AND status = 'success'",
                (cutoff_date,)
            )
            deleted = cursor.rowcount
            
            # 清理孤立的失败消息记录
            await conn.execute("""
                DELETE FROM failed_messages 
                WHERE message_log_id NOT IN (SELECT id FROM message_logs)
            """)
            
            # VACUUM（回收空间，可选）
            if deleted > 1000:
                logger.info("执行VACUUM回收空间...")
                await conn.execute("VACUUM")
            
            self.stats['deletes'] += deleted
            
            logger.info(f"✅ 清理了{deleted}条旧日志")
            return deleted
    
    async def get_stats_summary(self, hours: int = 24) -> Dict:
        """
        获取统计摘要（优化查询）
        
        Args:
            hours: 统计最近N小时
            
        Returns:
            统计信息
        """
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        async with self.get_async_connection() as conn:
            # 使用单个查询获取所有统计（减少数据库访问）
            query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                    AVG(CASE WHEN latency_ms > 0 THEN latency_ms ELSE NULL END) as avg_latency,
                    MAX(latency_ms) as max_latency,
                    MIN(CASE WHEN latency_ms > 0 THEN latency_ms ELSE NULL END) as min_latency,
                    COUNT(DISTINCT kook_channel_id) as channel_count,
                    COUNT(DISTINCT target_platform) as platform_count
                FROM message_logs
                WHERE created_at >= ?
            """
            
            cursor = await conn.execute(query, (start_time,))
            row = await cursor.fetchone()
            
            if row:
                total = row[0] or 0
                success = row[1] or 0
                
                return {
                    'total': total,
                    'success': success,
                    'failed': row[2] or 0,
                    'pending': row[3] or 0,
                    'success_rate': (success / total * 100) if total > 0 else 0,
                    'avg_latency_ms': round(row[4] or 0, 2),
                    'max_latency_ms': row[5] or 0,
                    'min_latency_ms': row[6] or 0,
                    'channel_count': row[7] or 0,
                    'platform_count': row[8] or 0,
                    'hours': hours
                }
            
            return {}
    
    def get_performance_stats(self) -> Dict:
        """获取数据库性能统计"""
        return {
            **self.stats,
            'db_size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
        }


# 全局实例
db_v2 = DatabaseV2()
