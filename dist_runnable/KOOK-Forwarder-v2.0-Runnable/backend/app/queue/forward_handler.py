"""
消息转发处理器
从worker.py拆分出来，专注于平台转发逻辑
"""
import asyncio
from typing import Dict, Any, Optional
from ..utils.structured_logger import logger, log_info, log_error
from ..utils.metrics import metrics
from ..database import db
from ..processors.formatter import formatter
from ..forwarders.discord import discord_forwarder
from ..forwarders.telegram import telegram_forwarder
from ..forwarders.feishu import feishu_forwarder


class ForwardHandler:
    """转发处理器"""
    
    async def forward(self, message: Dict[str, Any], mapping: Dict[str, Any]) -> bool:
        """
        转发消息到目标平台
        
        Args:
            message: 消息数据
            mapping: 频道映射配置
            
        Returns:
            是否成功
        """
        platform = mapping['target_platform']
        target_channel = mapping['target_channel_id']
        bot_id = mapping['target_bot_id']
        
        try:
            # 获取Bot配置
            bot_configs = db.get_bot_configs(platform)
            bot_config = next((b for b in bot_configs if b['id'] == bot_id), None)
            
            if not bot_config:
                log_error("未找到Bot配置", bot_id=bot_id)
                return False
            
            # 准备消息内容
            content = message.get('content', '')
            sender_name = message.get('sender_name', '未知用户')
            message_type = message.get('message_type', 'text')
            
            # 根据平台转发
            if platform == 'discord':
                return await self._forward_to_discord(
                    content, sender_name, message, bot_config, target_channel
                )
            elif platform == 'telegram':
                return await self._forward_to_telegram(
                    content, sender_name, message, bot_config, target_channel
                )
            elif platform == 'feishu':
                return await self._forward_to_feishu(
                    content, sender_name, message, bot_config, target_channel
                )
            else:
                log_error("不支持的平台", platform=platform)
                return False
                
        except Exception as e:
            log_error("转发消息异常",
                     platform=platform,
                     error=str(e))
            metrics.record_error(
                error_type=type(e).__name__,
                module='forward_handler'
            )
            return False
    
    async def _forward_to_discord(
        self,
        content: str,
        sender_name: str,
        message: Dict[str, Any],
        bot_config: Dict[str, Any],
        target_channel: str
    ) -> bool:
        """转发到Discord"""
        try:
            # 格式转换
            formatted_content = formatter.kmarkdown_to_discord(content)
            formatted_content = f"**{sender_name}**: {formatted_content}"
            
            # 处理超长消息
            if len(formatted_content) > 2000:
                segments = formatter.split_long_message(formatted_content, 1950)
                for i, segment in enumerate(segments):
                    success = await discord_forwarder.send_message(
                        webhook_url=bot_config['config']['webhook_url'],
                        content=f"[{i+1}/{len(segments)}] {segment}",
                        username=sender_name
                    )
                    if not success:
                        return False
                    await asyncio.sleep(0.5)
                return True
            else:
                return await discord_forwarder.send_message(
                    webhook_url=bot_config['config']['webhook_url'],
                    content=formatted_content,
                    username=sender_name
                )
        except Exception as e:
            log_error("Discord转发失败", error=str(e))
            return False
    
    async def _forward_to_telegram(
        self,
        content: str,
        sender_name: str,
        message: Dict[str, Any],
        bot_config: Dict[str, Any],
        target_channel: str
    ) -> bool:
        """转发到Telegram"""
        try:
            # 格式转换
            formatted_content = formatter.kmarkdown_to_telegram_html(content)
            formatted_content = f"<b>{sender_name}</b>: {formatted_content}"
            
            # 处理超长消息
            if len(formatted_content) > 4096:
                segments = formatter.split_long_message(formatted_content, 4000)
                for i, segment in enumerate(segments):
                    success = await telegram_forwarder.send_message(
                        token=bot_config['config']['token'],
                        chat_id=target_channel,
                        content=f"[{i+1}/{len(segments)}]\n{segment}"
                    )
                    if not success:
                        return False
                    await asyncio.sleep(0.3)
                return True
            else:
                return await telegram_forwarder.send_message(
                    token=bot_config['config']['token'],
                    chat_id=target_channel,
                    content=formatted_content
                )
        except Exception as e:
            log_error("Telegram转发失败", error=str(e))
            return False
    
    async def _forward_to_feishu(
        self,
        content: str,
        sender_name: str,
        message: Dict[str, Any],
        bot_config: Dict[str, Any],
        target_channel: str
    ) -> bool:
        """转发到飞书"""
        try:
            # 格式转换
            formatted_content = formatter.kmarkdown_to_feishu_text(content)
            formatted_content = f"{sender_name}: {formatted_content}"
            
            # 处理超长消息
            if len(formatted_content) > 5000:
                segments = formatter.split_long_message(formatted_content, 4900)
                for i, segment in enumerate(segments):
                    success = await feishu_forwarder.send_message(
                        app_id=bot_config['config']['app_id'],
                        app_secret=bot_config['config']['app_secret'],
                        chat_id=target_channel,
                        content=f"[{i+1}/{len(segments)}]\n{segment}"
                    )
                    if not success:
                        return False
                    await asyncio.sleep(0.5)
                return True
            else:
                return await feishu_forwarder.send_message(
                    app_id=bot_config['config']['app_id'],
                    app_secret=bot_config['config']['app_secret'],
                    chat_id=target_channel,
                    content=formatted_content
                )
        except Exception as e:
            log_error("飞书转发失败", error=str(e))
            return False
