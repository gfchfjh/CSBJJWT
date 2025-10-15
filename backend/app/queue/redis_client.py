"""
Redis队列客户端
"""
import redis.asyncio as aioredis
import json
from typing import Optional, Dict, Any
from ..utils.logger import logger
from ..config import settings


class RedisQueue:
    """Redis消息队列"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.queue_name = "kook_messages"
    
    async def connect(self):
        """连接Redis"""
        try:
            self.redis = await aioredis.from_url(
                f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
                password=settings.redis_password,
                encoding="utf-8",
                decode_responses=True
            )
            
            # 测试连接
            await self.redis.ping()
            logger.info("Redis连接成功")
            
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            raise
    
    async def disconnect(self):
        """断开连接"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis连接已关闭")
    
    async def enqueue(self, message: Dict[str, Any]) -> bool:
        """
        将消息加入队列
        
        Args:
            message: 消息数据
            
        Returns:
            是否成功
        """
        try:
            message_json = json.dumps(message, ensure_ascii=False)
            await self.redis.rpush(self.queue_name, message_json)
            logger.debug(f"消息已入队: {message.get('message_id')}")
            return True
            
        except Exception as e:
            logger.error(f"消息入队失败: {str(e)}")
            return False
    
    async def dequeue(self, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """
        从队列取出消息
        
        Args:
            timeout: 超时时间（秒），0表示立即返回
            
        Returns:
            消息数据，如果队列为空返回None
        """
        try:
            if timeout > 0:
                # 阻塞式取出
                result = await self.redis.blpop(self.queue_name, timeout)
                if result:
                    _, message_json = result
                    message = json.loads(message_json)
                    return message
            else:
                # 非阻塞式取出
                message_json = await self.redis.lpop(self.queue_name)
                if message_json:
                    message = json.loads(message_json)
                    return message
            
            return None
            
        except Exception as e:
            logger.error(f"消息出队失败: {str(e)}")
            return None
    
    async def get_queue_size(self) -> int:
        """获取队列大小"""
        try:
            return await self.redis.llen(self.queue_name)
        except Exception as e:
            logger.error(f"获取队列大小失败: {str(e)}")
            return 0
    
    async def clear_queue(self):
        """清空队列"""
        try:
            await self.redis.delete(self.queue_name)
            logger.info("队列已清空")
        except Exception as e:
            logger.error(f"清空队列失败: {str(e)}")
    
    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """设置键值"""
        try:
            await self.redis.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"设置键值失败: {str(e)}")
    
    async def get(self, key: str) -> Optional[str]:
        """获取键值"""
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"获取键值失败: {str(e)}")
            return None
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"检查键存在失败: {str(e)}")
            return False
    
    async def add_to_set(self, set_name: str, value: str):
        """添加到集合"""
        try:
            await self.redis.sadd(set_name, value)
        except Exception as e:
            logger.error(f"添加到集合失败: {str(e)}")
    
    async def is_in_set(self, set_name: str, value: str) -> bool:
        """检查值是否在集合中"""
        try:
            return await self.redis.sismember(set_name, value)
        except Exception as e:
            logger.error(f"检查集合成员失败: {str(e)}")
            return False


# 创建全局Redis队列实例
redis_queue = RedisQueue()
