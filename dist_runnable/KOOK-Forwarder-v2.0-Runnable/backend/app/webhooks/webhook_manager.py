"""
Webhook管理系统
✅ P1-9: Webhook回调支持
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime
from ..utils.logger import logger


class WebhookEvent:
    """Webhook事件类型"""
    MESSAGE_RECEIVED = 'message.received'
    MESSAGE_FORWARDED = 'message.forwarded'
    MESSAGE_FAILED = 'message.failed'
    ACCOUNT_ONLINE = 'account.online'
    ACCOUNT_OFFLINE = 'account.offline'
    SYSTEM_ALERT = 'system.alert'


class WebhookManager:
    """Webhook管理器"""
    
    def __init__(self):
        self.webhooks: Dict[str, List[str]] = {}  # event -> urls
        self.retry_config = {
            'max_retries': 3,
            'timeout': 10,
            'backoff_factor': 2
        }
        
        # 统计
        self.stats = {
            'total_sent': 0,
            'success': 0,
            'failed': 0
        }
    
    def register_webhook(self, event: str, url: str):
        """
        注册Webhook
        
        Args:
            event: 事件类型
            url: Webhook URL
        """
        if event not in self.webhooks:
            self.webhooks[event] = []
        
        if url not in self.webhooks[event]:
            self.webhooks[event].append(url)
            logger.info(f"Webhook已注册: {event} -> {url}")
    
    def unregister_webhook(self, event: str, url: str):
        """取消注册Webhook"""
        if event in self.webhooks:
            if url in self.webhooks[event]:
                self.webhooks[event].remove(url)
                logger.info(f"Webhook已取消: {event} -> {url}")
    
    async def trigger(self, event: str, payload: Dict):
        """
        触发Webhook
        
        Args:
            event: 事件类型
            payload: 数据载荷
        """
        if event not in self.webhooks:
            return
        
        urls = self.webhooks[event]
        
        if not urls:
            return
        
        # 添加元数据
        webhook_data = {
            'event': event,
            'timestamp': datetime.now().isoformat(),
            'data': payload
        }
        
        # 异步发送到所有URL
        tasks = [
            self._send_webhook(url, webhook_data)
            for url in urls
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_webhook(self, url: str, data: Dict):
        """发送Webhook请求"""
        self.stats['total_sent'] += 1
        
        for attempt in range(self.retry_config['max_retries']):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        json=data,
                        timeout=self.retry_config['timeout']
                    ) as response:
                        if response.status == 200:
                            self.stats['success'] += 1
                            logger.debug(f"Webhook发送成功: {url}")
                            return
                        else:
                            logger.warning(f"Webhook响应异常: {url}, 状态码: {response.status}")
                            
            except Exception as e:
                logger.error(f"Webhook发送失败 (尝试{attempt + 1}/{self.retry_config['max_retries']}): {url}, 错误: {str(e)}")
                
                # 如果不是最后一次尝试，等待后重试
                if attempt < self.retry_config['max_retries'] - 1:
                    wait_time = self.retry_config['backoff_factor'] ** attempt
                    await asyncio.sleep(wait_time)
        
        # 所有重试都失败
        self.stats['failed'] += 1
        logger.error(f"Webhook发送最终失败: {url}")
    
    def get_webhooks(self, event: Optional[str] = None) -> Dict:
        """获取Webhook列表"""
        if event:
            return {event: self.webhooks.get(event, [])}
        else:
            return self.webhooks.copy()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'success_rate': (
                self.stats['success'] / self.stats['total_sent'] * 100
                if self.stats['total_sent'] > 0 else 0
            )
        }


# 全局实例
webhook_manager = WebhookManager()


# 便捷函数
async def trigger_webhook(event: str, payload: Dict):
    """触发Webhook"""
    await webhook_manager.trigger(event, payload)
