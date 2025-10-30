"""
消息去重模块
统一使用Redis实现去重，避免双重缓存浪费内存
"""
from typing import Optional
from ..utils.logger import logger


class MessageDeduplicator:
    """
    消息去重器（基于Redis）
    
    优势：
    - 重启不丢失去重记录
    - 支持分布式部署
    - 内存占用小
    - TTL自动过期
    """
    
    def __init__(self, redis_client, ttl: int = 7 * 24 * 3600):
        """
        初始化去重器
        
        Args:
            redis_client: Redis客户端实例
            ttl: 去重记录保留时间（秒），默认7天
        """
        self.redis = redis_client
        self.ttl = ttl
        self.prefix = "dedup:msg:"
    
    async def is_duplicate(self, message_id: str) -> bool:
        """
        检查消息是否重复
        
        Args:
            message_id: 消息ID
            
        Returns:
            是否重复
        """
        key = f"{self.prefix}{message_id}"
        
        # 检查是否存在
        exists = await self.redis.exists(key)
        
        if exists:
            logger.debug(f"检测到重复消息: {message_id}")
            return True
        
        # 标记为已处理
        await self.redis.set(key, "1", expire=self.ttl)
        return False
    
    async def mark_as_processed(self, message_id: str):
        """
        标记消息为已处理
        
        Args:
            message_id: 消息ID
        """
        key = f"{self.prefix}{message_id}"
        await self.redis.set(key, "1", expire=self.ttl)
    
    async def clear_message(self, message_id: str):
        """
        清除消息的去重记录（用于手动重试）
        
        Args:
            message_id: 消息ID
        """
        key = f"{self.prefix}{message_id}"
        await self.redis.delete(key)
        logger.info(f"已清除消息去重记录: {message_id}")
    
    async def get_stats(self) -> dict:
        """
        获取去重统计信息
        
        Returns:
            统计信息字典
        """
        # 获取所有去重键
        keys = await self.redis.keys(f"{self.prefix}*")
        
        total_deduplicated = len(keys) if keys else 0
        
        return {
            'total_messages_tracked': total_deduplicated,
            'ttl_days': self.ttl / (24 * 3600),
            'memory_efficient': True,
            'distributed_ready': True
        }
    
    async def cleanup_expired(self):
        """
        清理过期的去重记录（Redis自动TTL，此方法仅作兼容）
        """
        # Redis的TTL会自动清理过期键，无需手动清理
        logger.debug("Redis TTL自动清理过期去重记录")
        pass


# 便捷函数
async def create_deduplicator(redis_client) -> MessageDeduplicator:
    """
    创建消息去重器实例
    
    Args:
        redis_client: Redis客户端
        
    Returns:
        去重器实例
    """
    return MessageDeduplicator(redis_client)
