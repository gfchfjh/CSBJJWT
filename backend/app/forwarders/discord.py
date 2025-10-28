"""
Discord转发模块
"""
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from discord_webhook import DiscordWebhook, DiscordEmbed
from ..utils.rate_limiter import rate_limiter_manager
from ..utils.logger import logger
from ..config import settings
from ..processors.formatter import formatter


class DiscordForwarder:
    """Discord消息转发器"""
    
    def __init__(self):
        self.rate_limiter = rate_limiter_manager.get_limiter(
            "discord",
            settings.discord_rate_limit_calls,
            settings.discord_rate_limit_period
        )
    
    async def send_message(self, webhook_url: str, content: str,
                          username: Optional[str] = None,
                          avatar_url: Optional[str] = None,
                          embeds: Optional[List[Dict]] = None) -> bool:
        """
        发送消息到Discord
        
        Args:
            webhook_url: Webhook URL
            content: 消息内容
            username: 显示的用户名
            avatar_url: 显示的头像URL
            embeds: Embed列表
            
        Returns:
            是否成功
        """
        try:
            # 应用限流
            await self.rate_limiter.acquire()
            
            # Discord单条消息最多2000字符
            messages = formatter.split_long_message(content, 2000)
            
            for msg in messages:
                webhook = DiscordWebhook(
                    url=webhook_url,
                    content=msg,
                    username=username or "KOOK消息转发",
                    avatar_url=avatar_url
                )
                
                # 添加Embed（仅第一条消息）
                if embeds and msg == messages[0]:
                    for embed_data in embeds:
                        embed = DiscordEmbed(**embed_data)
                        webhook.add_embed(embed)
                
                response = webhook.execute()
                
                if response.status_code not in [200, 204]:
                    logger.error(f"Discord发送失败: {response.status_code} - {response.text}")
                    return False
                
                # 如果有多条消息，稍微延迟一下
                if len(messages) > 1:
                    await asyncio.sleep(0.5)
            
            logger.info(f"Discord消息发送成功: {len(messages)}条")
            return True
            
        except Exception as e:
            logger.error(f"Discord发送异常: {str(e)}")
            return False
    
    async def send_image_direct(self, webhook_url: str, 
                               image_url: str,
                               content: str = "",
                               username: Optional[str] = None,
                               avatar_url: Optional[str] = None) -> bool:
        """
        发送图片消息（直接上传模式）
        
        Args:
            webhook_url: Webhook URL
            image_url: 图片URL
            content: 附带文本
            username: 显示的用户名
            avatar_url: 显示的头像URL
            
        Returns:
            是否成功
        """
        try:
            await self.rate_limiter.acquire()
            
            # 下载图片
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        logger.error(f"下载图片失败: {resp.status}")
                        return False
                    
                    image_data = await resp.read()
            
            # 使用Webhook上传图片
            webhook = DiscordWebhook(
                url=webhook_url,
                content=content,
                username=username or "KOOK消息转发",
                avatar_url=avatar_url
            )
            
            # 从URL提取文件名
            filename = image_url.split('/')[-1].split('?')[0]
            if not filename or '.' not in filename:
                filename = 'image.jpg'
            
            webhook.add_file(file=image_data, filename=filename)
            
            response = webhook.execute()
            
            if response.status_code not in [200, 204]:
                logger.error(f"Discord图片上传失败: {response.status_code}")
                return False
            
            logger.info(f"Discord图片上传成功（直传模式）")
            return True
            
        except Exception as e:
            logger.error(f"Discord图片直传异常: {str(e)}")
            return False
    
    async def send_with_attachment(self, webhook_url: str, content: str,
                                   file_path: str,
                                   username: Optional[str] = None,
                                   avatar_url: Optional[str] = None) -> bool:
        """
        发送带附件的消息（增强版 - 支持重试）
        
        Args:
            webhook_url: Webhook URL
            content: 消息内容
            file_path: 文件路径
            username: 显示的用户名
            avatar_url: 显示的头像URL
            
        Returns:
            是否成功
        """
        max_retries = 3
        retry_delay = 5  # 秒
        
        for attempt in range(max_retries):
            try:
                await self.rate_limiter.acquire()
                
                webhook = DiscordWebhook(
                    url=webhook_url,
                    content=content,
                    username=username or "KOOK消息转发",
                    avatar_url=avatar_url
                )
                
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    filename = file_path.split('/')[-1]
                    webhook.add_file(file=file_data, filename=filename)
                
                response = webhook.execute()
                
                if response.status_code in [200, 204]:
                    logger.info(f"Discord文件发送成功: {file_path}")
                    return True
                elif response.status_code == 429:
                    # 限流，等待后重试
                    retry_after = int(response.headers.get('Retry-After', retry_delay))
                    logger.warning(f"Discord API限流，等待{retry_after}秒后重试...")
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    logger.error(f"Discord文件发送失败: {response.status_code} - {response.text}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                    return False
                    
            except FileNotFoundError:
                logger.error(f"文件不存在: {file_path}")
                return False
            except Exception as e:
                logger.error(f"Discord文件发送异常: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                return False
        
        return False
    
    async def test_webhook(self, webhook_url: str) -> tuple[bool, str]:
        """
        测试Webhook连接
        
        Args:
            webhook_url: Webhook URL
            
        Returns:
            (是否成功, 消息)
        """
        try:
            webhook = DiscordWebhook(
                url=webhook_url,
                content="✅ KOOK消息转发系统测试消息\n\n如果您看到这条消息，说明Webhook配置成功！"
            )
            
            response = webhook.execute()
            
            if response.status_code in [200, 204]:
                return True, "测试成功！"
            else:
                return False, f"测试失败: HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"测试失败: {str(e)}"


class DiscordForwarderPool:
    """
    Discord转发器池 - 支持多Webhook负载均衡
    
    优化效果: 
    - 单Webhook: 57条/分钟 (5请求/5秒)
    - 10个Webhook: 570条/分钟 (+900%吞吐量)
    """
    
    def __init__(self, webhook_urls: List[str]):
        """
        初始化转发器池
        
        Args:
            webhook_urls: Webhook URL列表
        """
        if not webhook_urls:
            raise ValueError("至少需要提供一个Webhook URL")
        
        self.forwarders = [DiscordForwarder() for _ in webhook_urls]
        self.webhook_urls = webhook_urls
        self.current_index = 0
        self.total_count = len(webhook_urls)
        
        logger.info(f"Discord转发器池初始化完成: {self.total_count}个Webhook")
    
    def _get_next_webhook(self) -> tuple[DiscordForwarder, str]:
        """
        获取下一个Webhook (轮询算法)
        
        Returns:
            (转发器实例, Webhook URL)
        """
        forwarder = self.forwarders[self.current_index]
        webhook_url = self.webhook_urls[self.current_index]
        
        # 更新索引（轮询）
        self.current_index = (self.current_index + 1) % self.total_count
        
        return forwarder, webhook_url
    
    async def send_message(self, content: str,
                          username: Optional[str] = None,
                          avatar_url: Optional[str] = None,
                          embeds: Optional[List[Dict]] = None,
                          webhook_url: Optional[str] = None) -> bool:
        """
        发送消息（自动选择Webhook）
        
        Args:
            content: 消息内容
            username: 显示的用户名
            avatar_url: 显示的头像URL
            embeds: Embed列表
            webhook_url: 指定的Webhook URL（可选，不指定则自动选择）
            
        Returns:
            是否成功
        """
        if webhook_url:
            # 使用指定的Webhook
            forwarder = self.forwarders[0]
            url = webhook_url
        else:
            # 自动选择Webhook（负载均衡）
            forwarder, url = self._get_next_webhook()
        
        return await forwarder.send_message(
            url, content, username, avatar_url, embeds
        )
    
    async def send_with_attachment(self, content: str, file_path: str,
                                   username: Optional[str] = None,
                                   avatar_url: Optional[str] = None,
                                   webhook_url: Optional[str] = None) -> bool:
        """
        发送带附件的消息（自动选择Webhook）
        
        Args:
            content: 消息内容
            file_path: 文件路径
            username: 显示的用户名
            avatar_url: 显示的头像URL
            webhook_url: 指定的Webhook URL（可选）
            
        Returns:
            是否成功
        """
        if webhook_url:
            forwarder = self.forwarders[0]
            url = webhook_url
        else:
            forwarder, url = self._get_next_webhook()
        
        return await forwarder.send_with_attachment(
            url, content, file_path, username, avatar_url
        )
    
    async def test_all_webhooks(self) -> Dict[str, tuple[bool, str]]:
        """
        测试所有Webhook连接
        
        Returns:
            {webhook_url: (是否成功, 消息)}
        """
        results = {}
        
        for i, (forwarder, webhook_url) in enumerate(zip(self.forwarders, self.webhook_urls)):
            logger.info(f"测试Webhook {i+1}/{self.total_count}...")
            success, message = await forwarder.test_webhook(webhook_url)
            results[webhook_url] = (success, message)
            
            # 避免过快发送
            if i < self.total_count - 1:
                await asyncio.sleep(1)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取池统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_webhooks": self.total_count,
            "current_index": self.current_index,
            "theoretical_qps": self.total_count * 1,  # 每个Webhook 1 QPS
            "theoretical_throughput": self.total_count * 60  # 每分钟吞吐量
        }


# 创建全局实例
discord_forwarder = DiscordForwarder()
