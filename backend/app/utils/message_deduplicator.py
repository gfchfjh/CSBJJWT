"""
消息去重模块
实现消息ID持久化存储，防止重启后重复转发
"""
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Set, Optional
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class MessageDeduplicator:
    """
    消息去重器
    
    使用SQLite持久化存储已处理的消息ID
    支持自动清理过期数据
    """
    
    def __init__(self, db_path: str = "data/message_dedup.db", retention_days: int = 7):
        """
        初始化去重器
        
        Args:
            db_path: 数据库文件路径
            retention_days: 消息ID保留天数（默认7天）
        """
        self.db_path = Path(db_path)
        self.retention_days = retention_days
        self._lock = threading.Lock()
        self._memory_cache: Set[str] = set()
        
        # 确保数据目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        # 加载最近的消息ID到内存缓存
        self._load_recent_to_cache()
        
        logger.info(f"消息去重器初始化完成，数据库: {self.db_path}, 保留{retention_days}天")
    
    def _init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_messages (
                    message_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT DEFAULT 'kook'
                )
            ''')
            
            # 创建索引加速查询
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_processed_at 
                ON processed_messages(processed_at)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_channel_id 
                ON processed_messages(channel_id)
            ''')
            
            conn.commit()
            logger.debug("数据库表初始化完成")
    
    def _load_recent_to_cache(self, hours: int = 24):
        """
        加载最近N小时的消息ID到内存缓存
        
        Args:
            hours: 加载最近多少小时的数据
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT message_id FROM processed_messages WHERE processed_at >= ?',
                (cutoff_time,)
            )
            
            self._memory_cache = {row[0] for row in cursor.fetchall()}
            logger.info(f"已加载 {len(self._memory_cache)} 条最近{hours}小时的消息ID到缓存")
    
    def is_processed(self, message_id: str) -> bool:
        """
        检查消息是否已处理
        
        Args:
            message_id: 消息ID
            
        Returns:
            bool: 已处理返回True，否则返回False
        """
        # 先检查内存缓存（快速路径）
        if message_id in self._memory_cache:
            return True
        
        # 检查数据库（慢速路径）
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT 1 FROM processed_messages WHERE message_id = ? LIMIT 1',
                (message_id,)
            )
            exists = cursor.fetchone() is not None
            
            # 如果数据库中存在但缓存中没有，更新缓存
            if exists:
                self._memory_cache.add(message_id)
            
            return exists
    
    def mark_processed(self, message_id: str, channel_id: str, source: str = 'kook'):
        """
        标记消息为已处理
        
        Args:
            message_id: 消息ID
            channel_id: 频道ID
            source: 消息来源（默认kook）
        """
        with self._lock:
            try:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        '''
                        INSERT OR IGNORE INTO processed_messages 
                        (message_id, channel_id, source, processed_at)
                        VALUES (?, ?, ?, ?)
                        ''',
                        (message_id, channel_id, source, datetime.now())
                    )
                    conn.commit()
                
                # 更新内存缓存
                self._memory_cache.add(message_id)
                
            except Exception as e:
                logger.error(f"标记消息失败: {e}")
    
    def cleanup_old_messages(self) -> int:
        """
        清理过期的消息记录
        
        Returns:
            int: 清理的记录数
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        with self._lock:
            try:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'DELETE FROM processed_messages WHERE processed_at < ?',
                        (cutoff_date,)
                    )
                    deleted_count = cursor.rowcount
                    conn.commit()
                
                # 重新加载缓存
                self._load_recent_to_cache()
                
                logger.info(f"清理了 {deleted_count} 条过期消息记录（{self.retention_days}天前）")
                return deleted_count
                
            except Exception as e:
                logger.error(f"清理过期消息失败: {e}")
                return 0
    
    def get_stats(self) -> dict:
        """
        获取统计信息
        
        Returns:
            dict: 包含统计信息的字典
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # 总记录数
            cursor.execute('SELECT COUNT(*) FROM processed_messages')
            total = cursor.fetchone()[0]
            
            # 最近24小时
            yesterday = datetime.now() - timedelta(hours=24)
            cursor.execute(
                'SELECT COUNT(*) FROM processed_messages WHERE processed_at >= ?',
                (yesterday,)
            )
            last_24h = cursor.fetchone()[0]
            
            # 最近7天
            week_ago = datetime.now() - timedelta(days=7)
            cursor.execute(
                'SELECT COUNT(*) FROM processed_messages WHERE processed_at >= ?',
                (week_ago,)
            )
            last_7d = cursor.fetchone()[0]
            
            # 最早和最晚记录
            cursor.execute('SELECT MIN(processed_at), MAX(processed_at) FROM processed_messages')
            oldest, newest = cursor.fetchone()
            
            return {
                'total_messages': total,
                'cache_size': len(self._memory_cache),
                'last_24h': last_24h,
                'last_7d': last_7d,
                'oldest_record': oldest,
                'newest_record': newest,
                'retention_days': self.retention_days,
                'database_path': str(self.db_path)
            }
    
    def reset(self):
        """清空所有去重记录（谨慎使用）"""
        with self._lock:
            try:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM processed_messages')
                    conn.commit()
                
                self._memory_cache.clear()
                logger.warning("已清空所有去重记录")
                
            except Exception as e:
                logger.error(f"重置去重记录失败: {e}")


# 全局实例
_deduplicator_instance: Optional[MessageDeduplicator] = None


def get_deduplicator() -> MessageDeduplicator:
    """
    获取全局去重器实例（单例模式）
    
    Returns:
        MessageDeduplicator: 去重器实例
    """
    global _deduplicator_instance
    if _deduplicator_instance is None:
        _deduplicator_instance = MessageDeduplicator()
    return _deduplicator_instance
