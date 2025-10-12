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
    
    async def send_with_attachment(self, webhook_url: str, content: str,
                                   file_path: str,
                                   username: Optional[str] = None,
                                   avatar_url: Optional[str] = None) -> bool:
        """
        发送带附件的消息
        
        Args:
            webhook_url: Webhook URL
            content: 消息内容
            file_path: 文件路径
            username: 显示的用户名
            avatar_url: 显示的头像URL
            
        Returns:
            是否成功
        """
        try:
            await self.rate_limiter.acquire()
            
            webhook = DiscordWebhook(
                url=webhook_url,
                content=content,
                username=username or "KOOK消息转发",
                avatar_url=avatar_url
            )
            
            with open(file_path, "rb") as f:
                webhook.add_file(file=f.read(), filename=file_path.split('/')[-1])
            
            response = webhook.execute()
            
            if response.status_code not in [200, 204]:
                logger.error(f"Discord文件发送失败: {response.status_code}")
                return False
            
            logger.info(f"Discord文件发送成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Discord文件发送异常: {str(e)}")
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


# 创建全局实例
discord_forwarder = DiscordForwarder()
