"""
优化的Redis消息队列
✅ P0-31: Redis持久化、队列优先级、死信队列
"""
import asyncio
import json
from typing import Optional, Dict, List
from datetime import datetime
from ..utils.logger import logger
from ..queue.redis_client import redis_client


class QueuePriority:
    """队列优先级"""
    HIGH = 'high'
    NORMAL = 'normal'
    LOW = 'low'


class RedisQueueOptimized:
    """优化的Redis队列"""
    
    def __init__(self):
        # 优先级队列
        self.queues = {
            QueuePriority.HIGH: 'message_queue:high',
            QueuePriority.NORMAL: 'message_queue:normal',
            QueuePriority.LOW: 'message_queue:low'
        }
        
        # 死信队列
        self.dead_letter_queue = 'message_queue:dead_letter'
        
        # 处理中队列（用于崩溃恢复）
        self.processing_queue = 'message_queue:processing'
        
        # 统计
        self.stats = {
            'total_enqueued': 0,
            'total_dequeued': 0,
            'total_dead_letter': 0,
            'high_priority_count': 0,
            'normal_priority_count': 0,
            'low_priority_count': 0
        }
    
    async def enqueue(
        self,
        message: Dict,
        priority: str = QueuePriority.NORMAL
    ) -> bool:
        """
        入队消息
        
        Args:
            message: 消息数据
            priority: 优先级
            
        Returns:
            是否成功
        """
        try:
            # 添加元数据
            message['_enqueued_at'] = datetime.now().isoformat()
            message['_priority'] = priority
            
            # 序列化
            message_json = json.dumps(message)
            
            # 根据优先级入队
            queue_key = self.queues.get(priority, self.queues[QueuePriority.NORMAL])
            await redis_client.rpush(queue_key, message_json)
            
            # 更新统计
            self.stats['total_enqueued'] += 1
            if priority == QueuePriority.HIGH:
                self.stats['high_priority_count'] += 1
            elif priority == QueuePriority.NORMAL:
                self.stats['normal_priority_count'] += 1
            elif priority == QueuePriority.LOW:
                self.stats['low_priority_count'] += 1
            
            logger.debug(f"消息入队成功，优先级: {priority}")
            
            return True
            
        except Exception as e:
            logger.error(f"消息入队失败: {str(e)}")
            return False
    
    async def dequeue(self, timeout: int = 5) -> Optional[Dict]:
        """
        出队消息（优先级顺序）
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            消息数据
        """
        try:
            # 按优先级顺序尝试出队
            for priority in [QueuePriority.HIGH, QueuePriority.NORMAL, QueuePriority.LOW]:
                queue_key = self.queues[priority]
                
                # 使用BRPOPLPUSH实现原子操作
                # 从队列取出消息，同时放入processing队列
                result = await redis_client.brpoplpush(
                    queue_key,
                    self.processing_queue,
                    timeout
                )
                
                if result:
                    # 反序列化
                    message = json.loads(result)
                    
                    # 添加出队时间
                    message['_dequeued_at'] = datetime.now().isoformat()
                    
                    # 更新统计
                    self.stats['total_dequeued'] += 1
                    
                    logger.debug(f"消息出队成功，优先级: {priority}")
                    
                    return message
            
            # 所有队列都为空
            return None
            
        except Exception as e:
            logger.error(f"消息出队失败: {str(e)}")
            return None
    
    async def ack(self, message: Dict) -> bool:
        """
        确认消息已处理
        
        将消息从processing队列移除
        
        Args:
            message: 消息数据
            
        Returns:
            是否成功
        """
        try:
            message_json = json.dumps(message)
            
            # 从processing队列移除
            removed = await redis_client.lrem(self.processing_queue, 1, message_json)
            
            if removed > 0:
                logger.debug("消息确认成功")
                return True
            else:
                logger.warning("消息未找到，可能已被确认")
                return False
                
        except Exception as e:
            logger.error(f"消息确认失败: {str(e)}")
            return False
    
    async def nack(self, message: Dict, requeue: bool = True) -> bool:
        """
        拒绝消息（处理失败）
        
        Args:
            message: 消息数据
            requeue: 是否重新入队
            
        Returns:
            是否成功
        """
        try:
            message_json = json.dumps(message)
            
            # 从processing队列移除
            await redis_client.lrem(self.processing_queue, 1, message_json)
            
            if requeue:
                # 重新入队
                priority = message.get('_priority', QueuePriority.NORMAL)
                await self.enqueue(message, priority)
                logger.debug("消息重新入队")
            else:
                # 移到死信队列
                await self._move_to_dead_letter(message)
                logger.warning("消息移至死信队列")
            
            return True
            
        except Exception as e:
            logger.error(f"消息拒绝失败: {str(e)}")
            return False
    
    async def _move_to_dead_letter(self, message: Dict):
        """移动消息到死信队列"""
        try:
            # 添加死信元数据
            message['_dead_letter_at'] = datetime.now().isoformat()
            message['_dead_letter_reason'] = '处理失败'
            
            message_json = json.dumps(message)
            
            # 添加到死信队列
            await redis_client.rpush(self.dead_letter_queue, message_json)
            
            # 更新统计
            self.stats['total_dead_letter'] += 1
            
        except Exception as e:
            logger.error(f"移动到死信队列失败: {str(e)}")
    
    async def recover_processing(self):
        """
        恢复处理中的消息
        
        用于服务崩溃后恢复未处理完的消息
        """
        try:
            recovered_count = 0
            
            while True:
                # 从processing队列取出消息
                result = await redis_client.lpop(self.processing_queue)
                
                if not result:
                    break
                
                # 反序列化
                message = json.loads(result)
                
                # 重新入队
                priority = message.get('_priority', QueuePriority.NORMAL)
                await self.enqueue(message, priority)
                
                recovered_count += 1
            
            if recovered_count > 0:
                logger.info(f"恢复了{recovered_count}条未处理的消息")
            
            return recovered_count
            
        except Exception as e:
            logger.error(f"恢复处理中消息失败: {str(e)}")
            return 0
    
    async def get_queue_lengths(self) -> Dict:
        """获取各队列长度"""
        try:
            lengths = {}
            
            for priority, queue_key in self.queues.items():
                length = await redis_client.llen(queue_key)
                lengths[priority] = length
            
            lengths['processing'] = await redis_client.llen(self.processing_queue)
            lengths['dead_letter'] = await redis_client.llen(self.dead_letter_queue)
            lengths['total'] = sum(lengths.values())
            
            return lengths
            
        except Exception as e:
            logger.error(f"获取队列长度失败: {str(e)}")
            return {}
    
    async def get_dead_letter_messages(self, limit: int = 100) -> List[Dict]:
        """获取死信队列消息"""
        try:
            messages = []
            
            # 获取消息（不移除）
            results = await redis_client.lrange(self.dead_letter_queue, 0, limit - 1)
            
            for result in results:
                message = json.loads(result)
                messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"获取死信消息失败: {str(e)}")
            return []
    
    async def requeue_dead_letter(self, message: Dict) -> bool:
        """
        将死信消息重新入队
        
        Args:
            message: 消息数据
            
        Returns:
            是否成功
        """
        try:
            message_json = json.dumps(message)
            
            # 从死信队列移除
            removed = await redis_client.lrem(self.dead_letter_queue, 1, message_json)
            
            if removed > 0:
                # 重新入队
                priority = message.get('_priority', QueuePriority.NORMAL)
                await self.enqueue(message, priority)
                
                logger.info("死信消息重新入队成功")
                return True
            else:
                logger.warning("消息未找到")
                return False
                
        except Exception as e:
            logger.error(f"死信消息重新入队失败: {str(e)}")
            return False
    
    async def clear_dead_letter_queue(self) -> int:
        """清空死信队列"""
        try:
            count = await redis_client.llen(self.dead_letter_queue)
            await redis_client.delete(self.dead_letter_queue)
            
            logger.info(f"已清空死信队列，共{count}条消息")
            
            return count
            
        except Exception as e:
            logger.error(f"清空死信队列失败: {str(e)}")
            return 0
    
    async def clear_all_queues(self):
        """清空所有队列（谨慎使用）"""
        try:
            # 清空优先级队列
            for queue_key in self.queues.values():
                await redis_client.delete(queue_key)
            
            # 清空其他队列
            await redis_client.delete(self.processing_queue)
            await redis_client.delete(self.dead_letter_queue)
            
            logger.warning("所有队列已清空")
            
        except Exception as e:
            logger.error(f"清空队列失败: {str(e)}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats


# 全局实例
redis_queue_optimized = RedisQueueOptimized()
