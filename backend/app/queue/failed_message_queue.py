"""
失败消息重试队列
✅ P0-21: 失败消息自动重试机制
"""
import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from ..utils.logger import logger


@dataclass
class FailedMessage:
    """失败消息"""
    id: str
    message: dict
    error: str
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    last_retry: Optional[float] = None
    next_retry: Optional[float] = None
    

class FailedMessageQueue:
    """失败消息队列"""
    
    def __init__(self, max_retries: int = 3, base_delay: int = 60):
        """
        初始化队列
        
        Args:
            max_retries: 最大重试次数
            base_delay: 基础重试延迟（秒）
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        
        # 失败消息队列
        self.queue: Dict[str, FailedMessage] = {}
        
        # 重试任务
        self.retry_task: Optional[asyncio.Task] = None
        self._running = False
        
        # 统计
        self.stats = {
            'total_failed': 0,
            'total_retried': 0,
            'retry_success': 0,
            'retry_failed': 0,
            'abandoned': 0
        }
        
        # 消息处理器（由外部设置）
        self.message_handler = None
    
    async def start(self):
        """启动重试任务"""
        if self._running:
            return
        
        self._running = True
        self.retry_task = asyncio.create_task(self._retry_loop())
        logger.info("失败消息队列已启动")
    
    async def stop(self):
        """停止重试任务"""
        self._running = False
        
        if self.retry_task:
            self.retry_task.cancel()
            try:
                await self.retry_task
            except asyncio.CancelledError:
                pass
        
        logger.info("失败消息队列已停止")
    
    def add(self, message_id: str, message: dict, error: str):
        """
        添加失败消息到队列
        
        Args:
            message_id: 消息ID
            message: 消息数据
            error: 错误信息
        """
        # 检查是否已存在
        if message_id in self.queue:
            failed_msg = self.queue[message_id]
            failed_msg.retry_count += 1
            failed_msg.error = error
            
            # 检查是否超过最大重试次数
            if failed_msg.retry_count >= self.max_retries:
                logger.warning(f"消息{message_id}超过最大重试次数({self.max_retries})，放弃重试")
                self.stats['abandoned'] += 1
                del self.queue[message_id]
                return
        else:
            # 创建新的失败消息
            failed_msg = FailedMessage(
                id=message_id,
                message=message,
                error=error,
                max_retries=self.max_retries
            )
            self.queue[message_id] = failed_msg
        
        # 计算下次重试时间（指数退避）
        delay = self._calculate_delay(failed_msg.retry_count)
        failed_msg.next_retry = time.time() + delay
        
        self.stats['total_failed'] += 1
        
        logger.info(
            f"消息{message_id}加入失败队列，"
            f"重试次数: {failed_msg.retry_count}/{self.max_retries}，"
            f"下次重试: {delay}秒后"
        )
    
    def remove(self, message_id: str):
        """从队列中移除消息"""
        if message_id in self.queue:
            del self.queue[message_id]
            logger.debug(f"消息{message_id}已从失败队列移除")
    
    def get(self, message_id: str) -> Optional[FailedMessage]:
        """获取失败消息"""
        return self.queue.get(message_id)
    
    def get_all(self) -> List[FailedMessage]:
        """获取所有失败消息"""
        return list(self.queue.values())
    
    def get_pending_retry(self) -> List[FailedMessage]:
        """获取等待重试的消息"""
        current_time = time.time()
        return [
            msg for msg in self.queue.values()
            if msg.next_retry and msg.next_retry <= current_time
        ]
    
    async def _retry_loop(self):
        """重试循环"""
        try:
            while self._running:
                # 获取待重试的消息
                pending = self.get_pending_retry()
                
                if pending:
                    logger.info(f"发现{len(pending)}条待重试消息")
                    
                    # 并发重试（最多10条）
                    batch = pending[:10]
                    tasks = [self._retry_message(msg) for msg in batch]
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # 每10秒检查一次
                await asyncio.sleep(10)
                
        except asyncio.CancelledError:
            logger.info("重试循环已取消")
            raise
        except Exception as e:
            logger.error(f"重试循环异常: {str(e)}")
    
    async def _retry_message(self, failed_msg: FailedMessage):
        """重试单条消息"""
        try:
            logger.info(f"开始重试消息{failed_msg.id}（第{failed_msg.retry_count + 1}次）")
            
            # 更新重试时间
            failed_msg.last_retry = time.time()
            failed_msg.next_retry = None
            
            self.stats['total_retried'] += 1
            
            # 调用消息处理器
            if not self.message_handler:
                logger.error("未设置消息处理器，无法重试")
                return
            
            success = await self.message_handler(failed_msg.message)
            
            if success:
                # 重试成功，从队列移除
                self.remove(failed_msg.id)
                self.stats['retry_success'] += 1
                logger.info(f"消息{failed_msg.id}重试成功")
            else:
                # 重试失败，重新加入队列
                failed_msg.retry_count += 1
                
                if failed_msg.retry_count >= self.max_retries:
                    # 超过最大重试次数
                    self.remove(failed_msg.id)
                    self.stats['abandoned'] += 1
                    logger.warning(f"消息{failed_msg.id}超过最大重试次数，已放弃")
                else:
                    # 计算下次重试时间
                    delay = self._calculate_delay(failed_msg.retry_count)
                    failed_msg.next_retry = time.time() + delay
                    self.stats['retry_failed'] += 1
                    logger.warning(f"消息{failed_msg.id}重试失败，{delay}秒后再试")
            
        except Exception as e:
            logger.error(f"重试消息{failed_msg.id}时异常: {str(e)}")
            
            # 异常也算重试失败
            failed_msg.retry_count += 1
            if failed_msg.retry_count < self.max_retries:
                delay = self._calculate_delay(failed_msg.retry_count)
                failed_msg.next_retry = time.time() + delay
    
    def _calculate_delay(self, retry_count: int) -> int:
        """
        计算重试延迟（指数退避）
        
        Args:
            retry_count: 当前重试次数
            
        Returns:
            延迟秒数
        """
        # 指数退避：base_delay * 2^retry_count
        # 例如：60s, 120s, 240s, 480s...
        delay = self.base_delay * (2 ** retry_count)
        
        # 最大延迟1小时
        max_delay = 3600
        return min(delay, max_delay)
    
    def clear(self):
        """清空队列"""
        self.queue.clear()
        logger.info("失败消息队列已清空")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            'queue_size': len(self.queue),
            'pending_retry': len(self.get_pending_retry())
        }
    
    def set_message_handler(self, handler):
        """设置消息处理器"""
        self.message_handler = handler
        logger.info("消息处理器已设置")


# 全局实例
failed_message_queue = FailedMessageQueue()
