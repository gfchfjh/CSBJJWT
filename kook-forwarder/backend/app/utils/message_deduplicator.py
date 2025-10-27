"""
消息去重器
✅ P0-9优化：防止消息重复转发
"""
from collections import deque
import time
import sqlite3
from pathlib import Path
from typing import Set
from ..config import settings
from ..utils.logger import logger


class MessageDeduplicator:
    """消息去重器"""
    
    def __init__(self):
        self.db_path = Path(settings.data_dir) / "message_ids.db"
        self._init_db()
        
        # 内存缓存（最近10000条消息ID）
        self.recent_ids: deque = deque(maxlen=10000)
        self._load_recent_ids()
        
        logger.info("✅ 消息去重器已初始化")
    
    def _init_db(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_messages (
                    message_id TEXT PRIMARY KEY,
                    processed_at INTEGER NOT NULL,
                    source TEXT,
                    channel_id TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_processed_at ON processed_messages(processed_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_channel_id ON processed_messages(channel_id)")
            conn.commit()
            conn.close()
            logger.info("✅ 消息去重数据库已初始化")
        except Exception as e:
            logger.error(f"初始化消息去重数据库失败: {str(e)}")
    
    def _load_recent_ids(self):
        """加载最近的消息ID到内存"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute("""
                SELECT message_id FROM processed_messages
                ORDER BY processed_at DESC
                LIMIT 10000
            """)
            for row in cursor:
                self.recent_ids.append(row[0])
            conn.close()
            logger.info(f"加载了 {len(self.recent_ids)} 条最近消息ID到内存")
        except Exception as e:
            logger.error(f"加载消息ID失败: {str(e)}")
    
    def is_duplicate(self, message_id: str) -> bool:
        """
        检查消息是否已处理
        
        Args:
            message_id: 消息ID
            
        Returns:
            True if duplicate, False if new
        """
        # 先检查内存缓存（O(1)平均时间）
        if message_id in self.recent_ids:
            logger.debug(f"消息重复（内存缓存）: {message_id}")
            return True
        
        # 再检查数据库
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute(
                "SELECT 1 FROM processed_messages WHERE message_id = ? LIMIT 1",
                (message_id,)
            )
            exists = cursor.fetchone() is not None
            conn.close()
            
            if exists:
                logger.debug(f"消息重复（数据库）: {message_id}")
                # 同步到内存缓存
                self.recent_ids.append(message_id)
            
            return exists
        except Exception as e:
            logger.error(f"检查消息去重失败: {str(e)}")
            # 发生错误时，保守处理：假设不重复
            return False
    
    def mark_as_processed(self, message_id: str, source: str = "kook", channel_id: str = ""):
        """
        标记消息已处理
        
        Args:
            message_id: 消息ID
            source: 来源（kook/discord/telegram等）
            channel_id: 频道ID
        """
        try:
            now = int(time.time())
            
            # 添加到内存缓存
            if message_id not in self.recent_ids:
                self.recent_ids.append(message_id)
            
            # 添加到数据库
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                "INSERT OR IGNORE INTO processed_messages (message_id, processed_at, source, channel_id) VALUES (?, ?, ?, ?)",
                (message_id, now, source, channel_id)
            )
            conn.commit()
            conn.close()
            
            logger.debug(f"消息已标记为已处理: {message_id}")
        except Exception as e:
            logger.error(f"标记消息失败: {str(e)}")
    
    def cleanup_old_records(self, days: int = 7):
        """
        清理N天前的记录
        
        Args:
            days: 保留天数（默认7天）
        """
        try:
            cutoff_time = int(time.time()) - (days * 86400)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute(
                "DELETE FROM processed_messages WHERE processed_at < ?",
                (cutoff_time,)
            )
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"清理了 {deleted_count} 条 {days}天前的消息记录")
            
            return deleted_count
        except Exception as e:
            logger.error(f"清理旧消息记录失败: {str(e)}")
            return 0
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            
            # 总记录数
            cursor = conn.execute("SELECT COUNT(*) FROM processed_messages")
            total = cursor.fetchone()[0]
            
            # 今天的记录数
            today_start = int(time.time() / 86400) * 86400
            cursor = conn.execute(
                "SELECT COUNT(*) FROM processed_messages WHERE processed_at >= ?",
                (today_start,)
            )
            today = cursor.fetchone()[0]
            
            # 按来源统计
            cursor = conn.execute("""
                SELECT source, COUNT(*) 
                FROM processed_messages 
                GROUP BY source
            """)
            by_source = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "total": total,
                "today": today,
                "in_memory": len(self.recent_ids),
                "by_source": by_source
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {}


# 创建全局实例
message_deduplicator = MessageDeduplicator()
