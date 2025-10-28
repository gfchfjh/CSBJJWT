"""
消息去重器 - 持久化实现
✅ P1-1优化: 内存+数据库双重去重，重启不丢失
"""
import sqlite3
import asyncio
from pathlib import Path
from typing import Set, Optional, Dict
from datetime import datetime, timedelta
from ..config import settings
from ..utils.logger import logger


class MessageDeduplicator:
    """
    消息去重器
    
    功能：
    1. 内存缓存（快速查询，加载最近24小时）
    2. SQLite持久化（重启不丢失）
    3. 自动清理（保留7天数据）
    4. 统计信息
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (settings.data_dir / 'message_dedup.db')
        self.memory_cache: Set[str] = set()  # 内存缓存
        self.cache_hits = 0  # 缓存命中次数
        self.cache_misses = 0  # 缓存未命中次数
        
        # 初始化数据库
        self.init_database()
        
        # 加载最近24小时的消息ID到内存
        self.load_recent_to_cache()
        
        logger.info(f"✅ 消息去重器已初始化，缓存了{len(self.memory_cache)}条消息ID")
    
    def init_database(self):
        """初始化去重数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建去重表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_dedup (
                    message_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    server_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seen_count INTEGER DEFAULT 1
                )
            """)
            
            # 创建索引优化查询
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_dedup_channel_time
                ON message_dedup(channel_id, created_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_dedup_created_time
                ON message_dedup(created_at DESC)
            """)
            
            # 统计表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dedup_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_messages INTEGER DEFAULT 0,
                    duplicate_messages INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 初始化统计
            cursor.execute("""
                INSERT OR IGNORE INTO dedup_stats (id, total_messages, duplicate_messages)
                VALUES (1, 0, 0)
            """)
            
            conn.commit()
            
        logger.info(f"✅ 去重数据库已初始化: {self.db_path}")
    
    def load_recent_to_cache(self, hours: int = 24):
        """
        加载最近N小时的消息ID到内存缓存
        
        Args:
            hours: 加载多少小时内的数据，默认24小时
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT message_id FROM message_dedup
                WHERE created_at > ?
            """, (cutoff_time,))
            
            rows = cursor.fetchall()
            
            self.memory_cache = {row[0] for row in rows}
            
            logger.info(f"✅ 加载了{len(self.memory_cache)}条消息ID到内存缓存（最近{hours}小时）")
    
    async def is_duplicate(self, message_id: str) -> bool:
        """
        检查消息是否重复
        
        Args:
            message_id: 消息ID
            
        Returns:
            True=重复, False=新消息
        """
        # 1. 快速内存查询（优先）
        if message_id in self.memory_cache:
            self.cache_hits += 1
            return True
        
        # 2. 数据库查询（缓存未命中）
        self.cache_misses += 1
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 1 FROM message_dedup
                WHERE message_id = ?
            """, (message_id,))
            
            result = cursor.fetchone()
            
            if result:
                # 补充到缓存
                self.memory_cache.add(message_id)
                return True
            
            return False
    
    async def mark_as_seen(
        self,
        message_id: str,
        channel_id: str,
        server_id: Optional[str] = None
    ):
        """
        标记消息为已处理
        
        Args:
            message_id: 消息ID
            channel_id: 频道ID
            server_id: 服务器ID（可选）
        """
        # 1. 添加到内存缓存
        self.memory_cache.add(message_id)
        
        # 2. 持久化到数据库
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 插入或增加计数
            cursor.execute("""
                INSERT INTO message_dedup (message_id, channel_id, server_id, seen_count)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(message_id) DO UPDATE SET
                    seen_count = seen_count + 1,
                    created_at = CURRENT_TIMESTAMP
            """, (message_id, channel_id, server_id))
            
            # 更新统计
            cursor.execute("""
                UPDATE dedup_stats
                SET total_messages = total_messages + 1,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = 1
            """)
            
            conn.commit()
    
    async def cleanup_old_messages(self, days: int = 7):
        """
        清理旧消息（定时任务）
        
        Args:
            days: 保留多少天的数据，默认7天
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 删除旧数据
            cursor.execute("""
                DELETE FROM message_dedup
                WHERE created_at < ?
            """, (cutoff_time,))
            
            deleted_count = cursor.rowcount
            
            conn.commit()
            
            logger.info(f"🧹 清理了{deleted_count}条{days}天前的消息记录")
        
        # 重建缓存（释放内存）
        self.load_recent_to_cache()
        
        # 执行VACUUM优化数据库
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM")
            logger.info("✅ 数据库已优化（VACUUM）")
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计数据字典
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 总体统计
            cursor.execute("""
                SELECT total_messages, duplicate_messages, last_updated
                FROM dedup_stats WHERE id = 1
            """)
            
            stats_row = cursor.fetchone()
            
            # 数据库消息数
            cursor.execute("SELECT COUNT(*) FROM message_dedup")
            db_count = cursor.fetchone()[0]
            
            # 最新消息时间
            cursor.execute("""
                SELECT MAX(created_at) FROM message_dedup
            """)
            last_message = cursor.fetchone()[0]
            
            # 缓存命中率
            total_queries = self.cache_hits + self.cache_misses
            cache_hit_rate = (self.cache_hits / total_queries * 100) if total_queries > 0 else 0
            
            return {
                'memory_cache_size': len(self.memory_cache),
                'database_records': db_count,
                'total_messages_processed': stats_row[0] if stats_row else 0,
                'duplicate_messages': stats_row[1] if stats_row else 0,
                'last_updated': stats_row[2] if stats_row else None,
                'last_message_time': last_message,
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'cache_hit_rate': round(cache_hit_rate, 2)
            }
    
    async def get_channel_stats(self, channel_id: str) -> Dict:
        """
        获取特定频道的统计
        
        Args:
            channel_id: 频道ID
            
        Returns:
            频道统计数据
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 频道消息数
            cursor.execute("""
                SELECT COUNT(*) FROM message_dedup
                WHERE channel_id = ?
            """, (channel_id,))
            
            total_count = cursor.fetchone()[0]
            
            # 最近消息
            cursor.execute("""
                SELECT MAX(created_at) FROM message_dedup
                WHERE channel_id = ?
            """, (channel_id,))
            
            last_message = cursor.fetchone()[0]
            
            # 最近24小时消息数
            cutoff_24h = (datetime.now() - timedelta(hours=24)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM message_dedup
                WHERE channel_id = ? AND created_at > ?
            """, (channel_id, cutoff_24h))
            
            count_24h = cursor.fetchone()[0]
            
            return {
                'channel_id': channel_id,
                'total_messages': total_count,
                'messages_24h': count_24h,
                'last_message_time': last_message
            }
    
    async def reset(self):
        """重置去重器（清空所有数据）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM message_dedup")
            cursor.execute("""
                UPDATE dedup_stats
                SET total_messages = 0, duplicate_messages = 0
                WHERE id = 1
            """)
            
            conn.commit()
        
        # 清空缓存
        self.memory_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.warning("⚠️ 去重器已重置，所有数据已清空")


# 全局实例
message_deduplicator = MessageDeduplicator()


# 定时清理任务（每天凌晨3点）
async def schedule_cleanup():
    """定时清理任务"""
    while True:
        try:
            # 计算距离下次清理的时间
            now = datetime.now()
            next_cleanup = now.replace(hour=3, minute=0, second=0, microsecond=0)
            
            if next_cleanup <= now:
                next_cleanup += timedelta(days=1)
            
            wait_seconds = (next_cleanup - now).total_seconds()
            
            logger.info(f"下次清理时间: {next_cleanup.isoformat()}")
            
            await asyncio.sleep(wait_seconds)
            
            # 执行清理
            await message_deduplicator.cleanup_old_messages()
            
        except Exception as e:
            logger.error(f"定时清理任务异常: {e}")
            await asyncio.sleep(3600)  # 出错后1小时重试
