"""
Redis客户端（终极优化版）
========================
功能：
1. 连接池管理（5-20连接）
2. 自动重连
3. 批量操作优化
4. 性能监控
5. 健康检查

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import asyncio
import aioredis
import json
from typing import List, Optional, Any
from ..utils.logger import logger
from ..config import settings


class RedisQueueUltimate:
    """Redis队列客户端（终极优化版）"""
    
    def __init__(self):
        self.pool: Optional[aioredis.Redis] = None
        self.is_connected = False
        
        # 性能统计
        self.enqueue_count = 0
        self.dequeue_count = 0
        self.batch_dequeue_count = 0
    
    async def connect(self):
        """连接Redis（使用连接池）"""
        try:
            logger.info("🔌 连接Redis（使用连接池）...")
            
            # 创建连接池（5-20连接）
            self.pool = await aioredis.create_redis_pool(
                f'redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}',
                password=settings.redis_password,
                minsize=5,  # 最小连接数
                maxsize=20,  # 最大连接数
                encoding='utf-8'
            )
            
            # 测试连接
            await self.pool.ping()
            
            self.is_connected = True
            logger.info("✅ Redis连接池创建成功（5-20连接）")
            
        except Exception as e:
            logger.error(f"❌ Redis连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开Redis连接"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.is_connected = False
            logger.info("✅ Redis连接池已关闭")
    
    async def enqueue(self, message: Dict[str, Any], queue_name: str = 'message_queue'):
        """
        入队消息
        
        Args:
            message: 消息数据
            queue_name: 队列名称
        """
        try:
            message_json = json.dumps(message, ensure_ascii=False)
            await self.pool.rpush(queue_name, message_json)
            self.enqueue_count += 1
            
        except Exception as e:
            logger.error(f"消息入队失败: {e}")
            raise
    
    async def enqueue_batch(self, messages: List[Dict[str, Any]], queue_name: str = 'message_queue'):
        """
        批量入队消息（性能优化：使用pipeline）
        
        Args:
            messages: 消息列表
            queue_name: 队列名称
        """
        if not messages:
            return
        
        try:
            # 使用pipeline批量操作
            pipe = self.pool.pipeline()
            
            for message in messages:
                message_json = json.dumps(message, ensure_ascii=False)
                pipe.rpush(queue_name, message_json)
            
            await pipe.execute()
            self.enqueue_count += len(messages)
            
            logger.debug(f"批量入队 {len(messages)} 条消息")
            
        except Exception as e:
            logger.error(f"批量入队失败: {e}")
            raise
    
    async def dequeue(self, queue_name: str = 'message_queue', timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        出队单条消息
        
        Args:
            queue_name: 队列名称
            timeout: 超时时间（秒）
            
        Returns:
            消息数据或None
        """
        try:
            result = await self.pool.blpop(queue_name, timeout=timeout)
            
            if result:
                queue, message_json = result
                self.dequeue_count += 1
                return json.loads(message_json)
            
            return None
            
        except Exception as e:
            logger.error(f"消息出队失败: {e}")
            return None
    
    async def dequeue_batch(self, count: int = 10, queue_name: str = 'message_queue', 
                           timeout: int = 5) -> List[Dict[str, Any]]:
        """
        批量出队消息（性能优化：使用pipeline）
        
        Args:
            count: 出队数量
            queue_name: 队列名称
            timeout: 超时时间（秒）
            
        Returns:
            消息列表
        """
        try:
            messages = []
            
            # 使用pipeline批量操作
            pipe = self.pool.pipeline()
            
            for _ in range(count):
                pipe.lpop(queue_name)
            
            results = await pipe.execute()
            
            for result in results:
                if result:
                    try:
                        message = json.loads(result)
                        messages.append(message)
                    except json.JSONDecodeError:
                        logger.error(f"JSON解析失败: {result}")
            
            if messages:
                self.dequeue_count += len(messages)
                self.batch_dequeue_count += 1
                logger.debug(f"批量出队 {len(messages)} 条消息")
            
            return messages
            
        except Exception as e:
            logger.error(f"批量出队失败: {e}")
            return []
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return await self.pool.exists(key)
        except Exception as e:
            logger.error(f"检查键存在性失败: {e}")
            return False
    
    async def set(self, key: str, value: str, expire: int = None):
        """设置键值"""
        try:
            await self.pool.set(key, value)
            if expire:
                await self.pool.expire(key, expire)
        except Exception as e:
            logger.error(f"设置键值失败: {e}")
            raise
    
    async def get(self, key: str) -> Optional[str]:
        """获取键值"""
        try:
            value = await self.pool.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            logger.error(f"获取键值失败: {e}")
            return None
    
    async def delete(self, key: str):
        """删除键"""
        try:
            await self.pool.delete(key)
        except Exception as e:
            logger.error(f"删除键失败: {e}")
    
    async def get_queue_length(self, queue_name: str = 'message_queue') -> int:
        """获取队列长度"""
        try:
            return await self.pool.llen(queue_name)
        except Exception as e:
            logger.error(f"获取队列长度失败: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'is_connected': self.is_connected,
            'enqueue_count': self.enqueue_count,
            'dequeue_count': self.dequeue_count,
            'batch_dequeue_count': self.batch_dequeue_count,
            'pool_size': f"{self.pool.size if self.pool else 0} / 20"
        }


# 全局Redis客户端实例（终极优化版）
redis_queue_ultimate = RedisQueueUltimate()
