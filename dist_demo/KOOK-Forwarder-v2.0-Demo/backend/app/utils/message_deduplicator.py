"""
消息去重器
✅ P0-20: 防止重复转发相同消息
"""
import hashlib
import time
from typing import Optional, Set
from collections import deque
from ..utils.logger import logger


class MessageDeduplicator:
    """消息去重器"""
    
    def __init__(self, max_size: int = 10000, ttl: int = 7 * 24 * 3600):
        """
        初始化去重器
        
        Args:
            max_size: 最大缓存消息数
            ttl: 消息ID过期时间（秒），默认7天
        """
        self.max_size = max_size
        self.ttl = ttl
        
        # 使用集合存储消息ID（快速查找）
        self.message_ids: Set[str] = set()
        
        # 使用队列存储消息ID和时间戳（FIFO清理）
        self.message_queue = deque()
        
        # 统计
        self.stats = {
            'total_checked': 0,
            'duplicates_found': 0,
            'unique_messages': 0
        }
    
    def is_duplicate(self, message_id: str) -> bool:
        """
        检查消息是否重复
        
        Args:
            message_id: 消息ID
            
        Returns:
            True表示重复，False表示唯一
        """
        self.stats['total_checked'] += 1
        
        # 清理过期消息
        self._cleanup_expired()
        
        # 检查是否已存在
        if message_id in self.message_ids:
            self.stats['duplicates_found'] += 1
            logger.debug(f"发现重复消息: {message_id}")
            return True
        
        # 添加到缓存
        self._add_message(message_id)
        self.stats['unique_messages'] += 1
        
        return False
    
    def check_message(self, message: dict) -> bool:
        """
        检查消息对象是否重复
        
        Args:
            message: 消息对象
            
        Returns:
            True表示重复，False表示唯一
        """
        # 从消息中提取ID
        message_id = self._extract_message_id(message)
        
        if not message_id:
            # 如果没有ID，生成内容哈希
            message_id = self._generate_content_hash(message)
        
        return self.is_duplicate(message_id)
    
    def _add_message(self, message_id: str):
        """添加消息ID到缓存"""
        current_time = time.time()
        
        # 添加到集合
        self.message_ids.add(message_id)
        
        # 添加到队列
        self.message_queue.append((message_id, current_time))
        
        # 检查是否超过最大容量
        if len(self.message_ids) > self.max_size:
            self._remove_oldest()
    
    def _remove_oldest(self):
        """移除最旧的消息"""
        if self.message_queue:
            message_id, _ = self.message_queue.popleft()
            self.message_ids.discard(message_id)
    
    def _cleanup_expired(self):
        """清理过期消息"""
        current_time = time.time()
        
        # 从队列头部移除过期消息
        while self.message_queue:
            message_id, timestamp = self.message_queue[0]
            
            if current_time - timestamp > self.ttl:
                self.message_queue.popleft()
                self.message_ids.discard(message_id)
            else:
                # 队列是有序的，后面的都没过期
                break
    
    def _extract_message_id(self, message: dict) -> Optional[str]:
        """从消息中提取ID"""
        # 尝试多个可能的ID字段
        for field in ['msg_id', 'message_id', 'id', 'msgId']:
            if field in message:
                return str(message[field])
        
        return None
    
    def _generate_content_hash(self, message: dict) -> str:
        """
        根据消息内容生成哈希
        
        用于没有ID的消息
        """
        # 提取关键字段
        key_fields = [
            str(message.get('content', '')),
            str(message.get('author', {}).get('id', '')),
            str(message.get('channel_id', '')),
            str(message.get('timestamp', ''))
        ]
        
        # 生成哈希
        content = '|'.join(key_fields)
        return hashlib.md5(content.encode()).hexdigest()
    
    def clear(self):
        """清空缓存"""
        self.message_ids.clear()
        self.message_queue.clear()
        logger.info("消息去重缓存已清空")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            'cache_size': len(self.message_ids),
            'max_size': self.max_size,
            'usage_percent': len(self.message_ids) / self.max_size * 100
        }


# 全局实例
message_deduplicator = MessageDeduplicator()
