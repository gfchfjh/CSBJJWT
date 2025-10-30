"""
消息处理器核心模块
从worker.py拆分出来，专注于消息处理逻辑
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..utils.structured_logger import logger, log_info, log_error
from ..utils.deduplication import MessageDeduplicator
from ..utils.metrics import metrics, async_measure_time
from ..database import db
from .filter import message_filter
from .formatter import formatter


class MessageProcessor:
    """消息处理器"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        # 使用统一的Redis去重机制
        self.deduplicator = MessageDeduplicator(redis_client)
    
    async def process_message(self, message: Dict[str, Any]) -> bool:
        """
        处理单条消息
        
        Args:
            message: 消息数据
            
        Returns:
            是否成功
        """
        start_time = datetime.now()
        message_id = message.get('message_id', 'unknown')
        
        try:
            log_info("开始处理消息", message_id=message_id)
            
            # ✅ P0-7优化: 使用统一的Redis去重
            if await self.deduplicator.is_duplicate(message_id):
                log_info("消息已处理过，跳过", message_id=message_id)
                return True  # 重复消息不算失败
            
            # 应用过滤规则
            should_forward, reason = message_filter.should_forward(message)
            if not should_forward:
                log_info("消息被过滤", message_id=message_id, reason=reason)
                return True  # 被过滤也不算失败
            
            # 查找频道映射
            channel_id = message.get('channel_id')
            mappings = db.get_channel_mappings(channel_id)
            
            if not mappings:
                log_info("未找到频道映射", channel_id=channel_id)
                return True
            
            # 转发到所有映射的目标
            success_count = 0
            for mapping in mappings:
                try:
                    # 使用异步上下文管理器记录耗时
                    async with async_measure_time(mapping['target_platform'], 'forward'):
                        success = await self._forward_to_target(message, mapping)
                        if success:
                            success_count += 1
                            # 记录成功指标
                            metrics.record_message_processed(
                                platform=mapping['target_platform'],
                                status='success',
                                message_type=message.get('message_type', 'text')
                            )
                        else:
                            # 记录失败指标
                            metrics.record_message_processed(
                                platform=mapping['target_platform'],
                                status='failed',
                                message_type=message.get('message_type', 'text')
                            )
                except Exception as e:
                    log_error("转发消息异常", 
                             platform=mapping['target_platform'],
                             error=str(e))
                    metrics.record_error(
                        error_type=type(e).__name__,
                        module='message_processor'
                    )
            
            # 计算延迟
            latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            log_info("消息处理完成", 
                    message_id=message_id,
                    success_count=success_count,
                    total_mappings=len(mappings),
                    latency_ms=latency_ms)
            
            return success_count > 0
            
        except Exception as e:
            log_error("处理消息失败", message_id=message_id, error=str(e))
            metrics.record_error(
                error_type=type(e).__name__,
                module='message_processor'
            )
            return False
    
    async def _forward_to_target(self, message: Dict[str, Any], 
                                 mapping: Dict[str, Any]) -> bool:
        """
        转发消息到目标平台（简化版，实际实现在worker.py）
        
        Args:
            message: 消息数据
            mapping: 频道映射配置
            
        Returns:
            是否成功
        """
        # 此方法将在worker.py中完整实现
        # 这里仅作为接口定义
        platform = mapping['target_platform']
        target_channel = mapping['target_channel_id']
        
        log_info("转发消息",
                platform=platform,
                target_channel=target_channel,
                message_id=message.get('message_id'))
        
        # 实际转发逻辑由ForwardHandler处理
        from ..queue.forward_handler import ForwardHandler
        handler = ForwardHandler()
        return await handler.forward(message, mapping)


class BatchMessageProcessor:
    """批量消息处理器"""
    
    def __init__(self, redis_client, batch_size: int = 10):
        self.processor = MessageProcessor(redis_client)
        self.batch_size = batch_size
    
    async def process_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量处理消息
        
        Args:
            messages: 消息列表
            
        Returns:
            处理结果统计
        """
        if not messages:
            return {'total': 0, 'success': 0, 'failed': 0}
        
        log_info("开始批量处理", batch_size=len(messages))
        
        # 并行处理所有消息
        results = await asyncio.gather(
            *[self.processor.process_message(msg) for msg in messages],
            return_exceptions=True
        )
        
        # 统计结果
        success_count = sum(1 for r in results if r is True)
        failed_count = len(results) - success_count
        
        log_info("批量处理完成",
                total=len(messages),
                success=success_count,
                failed=failed_count)
        
        return {
            'total': len(messages),
            'success': success_count,
            'failed': failed_count,
            'success_rate': success_count / len(messages) if len(messages) > 0 else 0
        }
