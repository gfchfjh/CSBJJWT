"""
失败消息重试Worker
自动处理失败的消息，实现重试机制
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from ..utils.logger import logger
from ..database import db
from ..processors.filter import message_filter
from ..processors.formatter import formatter
from ..processors.image import image_processor
from ..forwarders.discord import discord_forwarder
from ..forwarders.telegram import telegram_forwarder
from ..forwarders.feishu import feishu_forwarder
from ..config import settings


class RetryWorker:
    """失败消息重试Worker"""
    
    def __init__(self):
        self.is_running = False
        self.retry_interval = settings.message_retry_interval  # 重试间隔（秒）
        self.max_retries = settings.message_retry_max  # 最大重试次数
    
    async def start(self):
        """启动重试Worker"""
        try:
            logger.info("启动失败消息重试Worker")
            self.is_running = True
            
            while self.is_running:
                # 每隔一段时间检查失败消息
                await asyncio.sleep(self.retry_interval)
                
                await self.process_failed_messages()
                
        except Exception as e:
            logger.error(f"重试Worker运行异常: {str(e)}")
        finally:
            logger.info("失败消息重试Worker已停止")
    
    async def stop(self):
        """停止重试Worker"""
        logger.info("停止失败消息重试Worker")
        self.is_running = False
    
    async def process_failed_messages(self):
        """处理失败的消息"""
        try:
            # 从数据库获取失败的消息
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 查询需要重试的消息（失败且重试次数未达上限）
                cursor.execute("""
                    SELECT fm.*, ml.*
                    FROM failed_messages fm
                    JOIN message_logs ml ON fm.message_log_id = ml.id
                    WHERE fm.retry_count < ?
                    AND (fm.last_retry IS NULL 
                         OR datetime(fm.last_retry, '+' || ? || ' seconds') <= datetime('now'))
                    ORDER BY fm.last_retry ASC
                    LIMIT 10
                """, (self.max_retries, self.retry_interval))
                
                failed_messages = [dict(row) for row in cursor.fetchall()]
            
            if not failed_messages:
                return
            
            logger.info(f"发现 {len(failed_messages)} 条失败消息，开始重试")
            
            for msg_data in failed_messages:
                await self.retry_message(msg_data)
                
        except Exception as e:
            logger.error(f"处理失败消息异常: {str(e)}")
    
    async def retry_message(self, msg_data: Dict[str, Any]):
        """
        重试单条消息
        
        Args:
            msg_data: 消息数据（包含failed_messages和message_logs的字段）
        """
        message_log_id = msg_data.get("message_log_id")
        retry_count = msg_data.get("retry_count", 0)
        
        try:
            logger.info(f"重试消息: id={message_log_id}, 第{retry_count + 1}次重试")
            
            # 重构消息数据
            message = {
                "message_id": msg_data.get("kook_message_id"),
                "channel_id": msg_data.get("kook_channel_id"),
                "content": msg_data.get("content"),
                "message_type": msg_data.get("message_type"),
                "sender_name": msg_data.get("sender_name"),
            }
            
            # 获取目标平台和频道
            target_platform = msg_data.get("target_platform")
            target_channel = msg_data.get("target_channel")
            
            # 查找映射配置
            mappings = db.get_channel_mappings(message["channel_id"])
            
            # 找到对应的映射
            mapping = None
            for m in mappings:
                if m["target_platform"] == target_platform and m["target_channel_id"] == target_channel:
                    mapping = m
                    break
            
            if not mapping:
                logger.error(f"未找到映射配置: platform={target_platform}, channel={target_channel}")
                await self.mark_retry_failed(message_log_id, retry_count, "映射配置不存在")
                return
            
            # 尝试重新转发
            success = await self.forward_message(message, mapping)
            
            if success:
                # 重试成功，更新状态
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # 更新消息日志状态
                    cursor.execute("""
                        UPDATE message_logs
                        SET status = 'success', error_message = NULL
                        WHERE id = ?
                    """, (message_log_id,))
                    
                    # 删除失败消息记录
                    cursor.execute("""
                        DELETE FROM failed_messages
                        WHERE message_log_id = ?
                    """, (message_log_id,))
                    
                    conn.commit()
                
                logger.info(f"消息重试成功: id={message_log_id}")
            else:
                # 重试失败，更新重试次数
                await self.mark_retry_failed(message_log_id, retry_count, "转发失败")
                
        except Exception as e:
            logger.error(f"重试消息异常: id={message_log_id}, 错误: {str(e)}")
            await self.mark_retry_failed(message_log_id, retry_count, str(e))
    
    async def mark_retry_failed(self, message_log_id: int, retry_count: int, error: str):
        """
        标记重试失败
        
        Args:
            message_log_id: 消息日志ID
            retry_count: 当前重试次数
            error: 错误信息
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                new_retry_count = retry_count + 1
                
                # 更新失败消息记录
                cursor.execute("""
                    UPDATE failed_messages
                    SET retry_count = ?, last_retry = ?
                    WHERE message_log_id = ?
                """, (new_retry_count, datetime.now(), message_log_id))
                
                # 更新消息日志
                cursor.execute("""
                    UPDATE message_logs
                    SET error_message = ?
                    WHERE id = ?
                """, (f"重试{new_retry_count}次失败: {error}", message_log_id))
                
                conn.commit()
            
            if new_retry_count >= self.max_retries:
                logger.warning(f"消息已达最大重试次数: id={message_log_id}")
            else:
                logger.info(f"消息重试失败，将在{self.retry_interval}秒后再次重试")
                
        except Exception as e:
            logger.error(f"更新重试状态失败: {str(e)}")
    
    async def forward_message(self, message: Dict[str, Any], mapping: Dict[str, Any]) -> bool:
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
                logger.error(f"未找到Bot配置: {bot_id}")
                return False
            
            # 准备消息内容
            content = message.get('content', '')
            sender_name = message.get('sender_name', '未知用户')
            
            # 格式转换和转发
            if platform == 'discord':
                formatted_content = formatter.kmarkdown_to_discord(content)
                formatted_content = f"**{sender_name}**: {formatted_content}"
                
                webhook_url = bot_config['config'].get('webhook_url')
                
                success = await discord_forwarder.send_message(
                    webhook_url=webhook_url,
                    content=formatted_content,
                    username=sender_name
                )
                
            elif platform == 'telegram':
                formatted_content = formatter.kmarkdown_to_telegram_html(content)
                formatted_content = f"<b>{sender_name}</b>: {formatted_content}"
                
                token = bot_config['config'].get('token')
                
                success = await telegram_forwarder.send_message(
                    token=token,
                    chat_id=target_channel,
                    content=formatted_content
                )
                
            elif platform == 'feishu':
                formatted_content = formatter.kmarkdown_to_feishu_text(content)
                formatted_content = f"{sender_name}: {formatted_content}"
                
                app_id = bot_config['config'].get('app_id')
                app_secret = bot_config['config'].get('app_secret')
                
                success = await feishu_forwarder.send_message(
                    app_id=app_id,
                    app_secret=app_secret,
                    chat_id=target_channel,
                    content=formatted_content
                )
                
            else:
                logger.error(f"不支持的平台: {platform}")
                return False
            
            return success
            
        except Exception as e:
            logger.error(f"转发消息异常: {str(e)}")
            return False


# 创建全局重试Worker实例
retry_worker = RetryWorker()
