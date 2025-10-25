"""
表情反应聚合器增强版 - ✅ P0-6优化完成: 3秒批量发送机制
"""
import asyncio
import time
from typing import Dict, List, Optional
from collections import defaultdict
from ..utils.logger import logger
from .reaction_aggregator import ReactionAggregator


class ReactionAggregatorEnhanced(ReactionAggregator):
    """
    ✅ P0-6优化: 增强版表情反应聚合器
    
    新功能：
    1. 异步3秒批量发送
    2. 自动清理过期反应
    3. 智能合并相同消息的反应
    4. 支持实时更新和延迟更新
    """
    
    def __init__(self):
        super().__init__()
        
        # 待发送队列（message_id -> 发送任务）
        self.pending_tasks: Dict[str, asyncio.Task] = {}
        
        # 配置
        self.batch_delay = 3.0  # 3秒延迟批量发送
        self.auto_cleanup_enabled = True
        self.cleanup_interval = 300  # 5分钟自动清理一次
        
        # 统计信息
        self.stats = {
            "total_reactions_received": 0,
            "total_reactions_sent": 0,
            "batches_sent": 0,
            "auto_cleaned": 0
        }
        
        logger.info("✅ P0-6: 增强版表情反应聚合器已初始化（3秒批量发送）")
    
    async def add_reaction_async(
        self,
        message_id: str,
        emoji: str,
        user_id: str,
        user_name: str,
        timestamp: Optional[int] = None,
        callback = None
    ):
        """
        ✅ P0-6新增: 异步添加表情反应（3秒后自动批量发送）
        
        Args:
            message_id: 消息ID
            emoji: 表情符号
            user_id: 用户ID
            user_name: 用户名
            timestamp: 时间戳
            callback: 发送回调函数 async def callback(message_id, formatted_text)
        """
        # 调用父类方法添加反应
        self.add_reaction(message_id, emoji, user_id, user_name, timestamp)
        
        # 统计
        self.stats["total_reactions_received"] += 1
        
        # 如果已有待发送任务，取消它
        if message_id in self.pending_tasks:
            self.pending_tasks[message_id].cancel()
            logger.debug(f"取消旧的发送任务: {message_id}")
        
        # 创建新的3秒延迟发送任务
        task = asyncio.create_task(
            self._delayed_send(message_id, callback)
        )
        self.pending_tasks[message_id] = task
        
        logger.debug(f"创建3秒延迟发送任务: {message_id}")
    
    async def remove_reaction_async(
        self,
        message_id: str,
        emoji: str,
        user_id: str,
        callback = None
    ):
        """
        ✅ P0-6新增: 异步移除表情反应（3秒后更新）
        
        Args:
            message_id: 消息ID
            emoji: 表情符号
            user_id: 用户ID
            callback: 发送回调函数
        """
        # 调用父类方法移除反应
        self.remove_reaction(message_id, emoji, user_id)
        
        # 取消旧任务
        if message_id in self.pending_tasks:
            self.pending_tasks[message_id].cancel()
        
        # 创建新的延迟发送任务（更新反应）
        task = asyncio.create_task(
            self._delayed_send(message_id, callback)
        )
        self.pending_tasks[message_id] = task
    
    async def _delayed_send(self, message_id: str, callback):
        """
        ✅ P0-6核心: 3秒延迟发送机制
        
        Args:
            message_id: 消息ID
            callback: 发送回调函数
        """
        try:
            # 等待3秒
            await asyncio.sleep(self.batch_delay)
            
            # 3秒后，发送汇总的反应
            if callback:
                # 格式化反应文本
                formatted_text = self.format_reactions(message_id, platform="discord")
                
                if formatted_text:
                    logger.info(f"✅ P0-6: 3秒后批量发送表情反应: {message_id}")
                    
                    # 调用回调函数发送
                    await callback(message_id, formatted_text)
                    
                    # 统计
                    self.stats["total_reactions_sent"] += 1
                    self.stats["batches_sent"] += 1
                else:
                    logger.debug(f"消息 {message_id} 没有反应，跳过发送")
            
            # 发送完成，从待发送队列中移除
            if message_id in self.pending_tasks:
                del self.pending_tasks[message_id]
        
        except asyncio.CancelledError:
            logger.debug(f"延迟发送任务被取消: {message_id}")
        except Exception as e:
            logger.error(f"延迟发送失败: {message_id}, 错误: {str(e)}")
    
    async def start_auto_cleanup_task(self):
        """
        ✅ P0-6新增: 启动自动清理任务
        
        定期清理过期的反应记录（释放内存）
        """
        if not self.auto_cleanup_enabled:
            return
        
        logger.info("✅ P0-6: 启动表情反应自动清理任务")
        
        while True:
            try:
                # 等待清理间隔
                await asyncio.sleep(self.cleanup_interval)
                
                # 清理1小时前的旧记录
                self.cleanup_old_messages(max_age_seconds=3600)
                
                self.stats["auto_cleaned"] += 1
                
                logger.info(
                    f"✅ P0-6: 自动清理完成，"
                    f"当前记录数: {len(self.reactions)}，"
                    f"待发送任务: {len(self.pending_tasks)}"
                )
                
            except asyncio.CancelledError:
                logger.info("自动清理任务已停止")
                break
            except Exception as e:
                logger.error(f"自动清理异常: {str(e)}")
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            {
                "total_reactions_received": int,  # 接收的反应总数
                "total_reactions_sent": int,      # 发送的反应总数
                "batches_sent": int,              # 发送的批次总数
                "auto_cleaned": int,              # 自动清理次数
                "pending_messages": int,          # 待发送消息数
                "total_messages": int             # 总消息数
            }
        """
        return {
            **self.stats,
            "pending_messages": len(self.pending_tasks),
            "total_messages": len(self.reactions)
        }
    
    async def force_send_all(self, callback):
        """
        ✅ P0-6新增: 强制立即发送所有待发送的反应
        
        Args:
            callback: 发送回调函数
        """
        logger.info(f"强制发送所有待发送反应，共 {len(self.pending_tasks)} 条")
        
        # 取消所有延迟任务
        for task in self.pending_tasks.values():
            task.cancel()
        
        self.pending_tasks.clear()
        
        # 立即发送所有反应
        for message_id in list(self.reactions.keys()):
            formatted_text = self.format_reactions(message_id, platform="discord")
            
            if formatted_text and callback:
                await callback(message_id, formatted_text)
                self.stats["total_reactions_sent"] += 1
    
    def format_reactions_multi_platform(
        self,
        message_id: str,
        platforms: List[str]
    ) -> Dict[str, str]:
        """
        ✅ P0-6新增: 为多个平台同时格式化反应
        
        Args:
            message_id: 消息ID
            platforms: 平台列表 ['discord', 'telegram', 'feishu']
            
        Returns:
            {
                'discord': '格式化文本',
                'telegram': '格式化文本',
                'feishu': '格式化文本'
            }
        """
        result = {}
        
        for platform in platforms:
            formatted = self.format_reactions(message_id, platform=platform)
            if formatted:
                result[platform] = formatted
        
        return result
    
    async def send_to_multiple_platforms(
        self,
        message_id: str,
        platform_callbacks: Dict[str, callable]
    ):
        """
        ✅ P0-6新增: 同时发送到多个平台
        
        Args:
            message_id: 消息ID
            platform_callbacks: {
                'discord': async def callback(msg_id, text),
                'telegram': async def callback(msg_id, text),
                ...
            }
        """
        # 为每个平台格式化
        platforms = list(platform_callbacks.keys())
        formatted_texts = self.format_reactions_multi_platform(message_id, platforms)
        
        # 并行发送到所有平台
        tasks = []
        for platform, callback in platform_callbacks.items():
            if platform in formatted_texts:
                task = callback(message_id, formatted_texts[platform])
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(f"✅ P0-6: 表情反应已发送到 {len(tasks)} 个平台")


# 创建全局增强实例
reaction_aggregator_enhanced = ReactionAggregatorEnhanced()
