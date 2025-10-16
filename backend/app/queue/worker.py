"""
消息处理Worker
"""
import asyncio
from datetime import datetime
from collections import OrderedDict
from typing import Dict, Any, List, Optional
from ..utils.logger import logger
from ..database import db
from ..processors.filter import message_filter
from ..processors.formatter import formatter
from ..processors.image import image_processor, attachment_processor
from ..forwarders.discord import discord_forwarder
from ..forwarders.telegram import telegram_forwarder
from ..forwarders.feishu import feishu_forwarder
from .redis_client import redis_queue


class LRUCache:
    """简单的LRU缓存，防止无限增长"""
    
    def __init__(self, max_size: int = 10000):
        """
        初始化LRU缓存
        
        Args:
            max_size: 最大缓存大小
        """
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def add(self, key: str):
        """
        添加键到缓存
        
        Args:
            key: 键
        """
        if key in self.cache:
            # 已存在，移到末尾（最近使用）
            self.cache.move_to_end(key)
        else:
            # 新增
            self.cache[key] = True
            # 检查是否超出限制
            if len(self.cache) > self.max_size:
                # 删除最旧的项（最前面的）
                self.cache.popitem(last=False)
    
    def __contains__(self, key: str) -> bool:
        """检查键是否存在"""
        return key in self.cache
    
    def __len__(self) -> int:
        """获取缓存大小"""
        return len(self.cache)


class MessageWorker:
    """消息处理Worker"""
    
    def __init__(self):
        self.is_running = False
        # 使用LRU缓存防止内存泄漏（最多保留10000条消息ID）
        self.processed_messages = LRUCache(max_size=10000)
    
    async def start(self):
        """启动Worker"""
        try:
            logger.info("启动消息处理Worker")
            self.is_running = True
            
            while self.is_running:
                # 从队列取出消息（阻塞5秒）
                message = await redis_queue.dequeue(timeout=5)
                
                if message:
                    await self.process_message(message)
                    
        except Exception as e:
            logger.error(f"Worker运行异常: {str(e)}")
        finally:
            logger.info("消息处理Worker已停止")
    
    async def stop(self):
        """停止Worker"""
        logger.info("停止消息处理Worker")
        self.is_running = False
    
    async def process_message(self, message: Dict[str, Any]):
        """
        处理单条消息
        
        Args:
            message: 消息数据
        """
        start_time = datetime.now()
        message_id = message.get('message_id')
        
        try:
            logger.info(f"开始处理消息: {message_id}")
            
            # 去重检查
            if message_id in self.processed_messages:
                logger.debug(f"消息已处理过，跳过: {message_id}")
                return
            
            # 或者使用Redis去重
            dedup_key = f"processed:{message_id}"
            if await redis_queue.exists(dedup_key):
                logger.debug(f"消息已处理过（Redis），跳过: {message_id}")
                return
            
            # 标记为已处理（保留7天）
            await redis_queue.set(dedup_key, "1", expire=7*24*3600)
            self.processed_messages.add(message_id)
            
            # 应用过滤规则
            should_forward, reason = message_filter.should_forward(message)
            if not should_forward:
                logger.info(f"消息被过滤: {message_id}, 原因: {reason}")
                return
            
            # 查找频道映射
            channel_id = message.get('channel_id')
            mappings = db.get_channel_mappings(channel_id)
            
            if not mappings:
                logger.debug(f"未找到频道映射: {channel_id}")
                return
            
            # 转发到所有映射的目标
            for mapping in mappings:
                await self.forward_to_target(message, mapping)
            
            # 计算延迟
            latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.info(f"消息处理完成: {message_id}, 延迟: {latency_ms}ms")
            
        except Exception as e:
            logger.error(f"处理消息失败: {message_id}, 错误: {str(e)}")
            
            # 记录失败日志
            db.add_message_log(
                kook_message_id=message_id,
                kook_channel_id=message.get('channel_id', ''),
                content=message.get('content', ''),
                message_type=message.get('message_type', 'text'),
                sender_name=message.get('sender_name', ''),
                target_platform='unknown',
                target_channel='unknown',
                status='failed',
                error_message=str(e)
            )
    
    async def process_images(self, image_urls: List[str], 
                            message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        处理消息中的图片（并行处理优化）
        
        Args:
            image_urls: 图片URL列表
            message: 原始消息数据（用于获取Cookie等）
            
        Returns:
            处理后的图片信息列表
        """
        if not image_urls:
            return []
        
        logger.info(f"开始并行处理{len(image_urls)}张图片")
        
        # 创建并行任务
        tasks = [
            self._process_single_image(url)
            for url in image_urls
        ]
        
        # 并行执行（使用gather，return_exceptions=True避免单个失败影响其他）
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        processed_images = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"图片处理失败: {image_urls[i]}, 错误: {result}")
            elif result:
                processed_images.append(result)
        
        logger.info(f"图片处理完成: 成功{len(processed_images)}/{len(image_urls)}张")
        return processed_images
    
    async def _process_single_image(self, url: str) -> Optional[Dict[str, Any]]:
        """
        处理单张图片
        
        Args:
            url: 图片URL
            
        Returns:
            处理后的图片信息
        """
        try:
            logger.debug(f"处理图片: {url}")
            
            # 使用智能策略处理图片
            result = await image_processor.process_image(
                url=url,
                strategy='smart',  # 智能模式：优先直传，失败用图床
                cookies=None,  # TODO: 从消息中获取Cookie
                referer='https://www.kookapp.cn'
            )
            
            if result:
                if isinstance(result, dict):
                    # 智能模式返回dict
                    return result
                else:
                    # 其他模式返回URL字符串
                    return {
                        'original': url,
                        'local': result,
                        'filepath': None
                    }
            else:
                logger.error(f"图片处理返回None: {url}")
                return None
                
        except Exception as e:
            logger.error(f"处理图片异常: {url}, 错误: {str(e)}")
            raise  # 重新抛出让gather捕获
    
    async def process_attachments(self, file_attachments: List[Dict[str, Any]],
                                   message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        处理消息中的附件文件（并行处理优化）
        
        Args:
            file_attachments: 附件列表
            message: 原始消息数据（用于获取Cookie等）
            
        Returns:
            处理后的附件信息列表
        """
        if not file_attachments:
            return []
        
        logger.info(f"开始并行处理{len(file_attachments)}个附件")
        
        # 创建并行任务
        tasks = [
            self._process_single_attachment(attachment)
            for attachment in file_attachments
        ]
        
        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        processed_attachments = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"附件处理失败: {file_attachments[i].get('name')}, 错误: {result}")
            elif result:
                processed_attachments.append(result)
        
        logger.info(f"附件处理完成: 成功{len(processed_attachments)}/{len(file_attachments)}个")
        return processed_attachments
    
    async def _process_single_attachment(self, attachment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理单个附件
        
        Args:
            attachment: 附件信息
            
        Returns:
            处理后的附件信息
        """
        try:
            url = attachment.get('url')
            filename = attachment.get('name', 'unknown')
            file_size_mb = attachment.get('size', 0) / (1024 * 1024)
            
            logger.debug(f"处理附件: {filename} ({file_size_mb:.2f}MB)")
            
            # 检查文件大小（最大50MB）
            if file_size_mb > 50:
                logger.warning(f"附件过大，跳过: {filename} ({file_size_mb:.2f}MB)")
                return None
            
            # 下载附件
            local_path = await attachment_processor.download_attachment(
                url=url,
                filename=filename,
                cookies=None,  # TODO: 从消息中获取Cookie
                referer='https://www.kookapp.cn'
            )
            
            if local_path:
                logger.info(f"✅ 附件下载成功: {filename}")
                return {
                    'original_url': url,
                    'filename': filename,
                    'local_path': local_path,
                    'size': attachment.get('size', 0),
                    'type': attachment.get('type', 'application/octet-stream')
                }
            else:
                logger.error(f"❌ 附件下载失败: {filename}")
                return None
                
        except Exception as e:
            logger.error(f"处理附件异常: {attachment.get('name')}, 错误: {str(e)}")
            raise  # 重新抛出让gather捕获
    
    async def forward_to_target(self, message: Dict[str, Any], 
                               mapping: Dict[str, Any]):
        """
        转发消息到目标平台
        
        Args:
            message: 消息数据
            mapping: 频道映射配置
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
                return
            
            # 准备消息内容
            content = message.get('content', '')
            sender_name = message.get('sender_name', '未知用户')
            message_type = message.get('message_type', 'text')
            image_urls = message.get('image_urls', [])
            file_attachments = message.get('file_attachments', [])
            
            # 提取引用和提及
            quote = message.get('quote')
            mentions = message.get('mentions', [])
            
            # 处理表情反应消息
            if message_type == 'reaction' or message.get('type') == 'reaction':
                reaction_text = formatter.format_reaction(message)
                content = f"💬 表情反应: {reaction_text}"
            
            # 处理图片（如果有）
            processed_images = []
            if image_urls:
                logger.info(f"检测到 {len(image_urls)} 张图片")
                processed_images = await self.process_images(image_urls, message)
            
            # 处理附件（如果有）
            processed_attachments = []
            if file_attachments:
                logger.info(f"检测到 {len(file_attachments)} 个附件")
                processed_attachments = await self.process_attachments(file_attachments, message)
            
            # 格式转换
            if platform == 'discord':
                # 格式化引用
                quote_text = formatter.format_quote(quote, 'discord') if quote else ""
                
                # 格式化提及
                formatted_content = formatter.kmarkdown_to_discord(content)
                formatted_content = formatter.format_mentions(mentions, formatted_content, 'discord')
                
                # 组合最终内容
                formatted_content = f"{quote_text}**{sender_name}**: {formatted_content}"
                
                # 如果有附件，添加到内容中
                if processed_attachments:
                    formatted_content += f"\n\n📎 **附件** ({len(processed_attachments)}个):"
                    for att in processed_attachments:
                        formatted_content += f"\n• {att['filename']}"
                
                webhook_url = bot_config['config'].get('webhook_url')
                
                # 如果有图片，尝试上传
                if processed_images:
                    # Discord支持Embed方式显示图片
                    for img_info in processed_images:
                        # 优先使用原始URL
                        image_url = img_info.get('original') or img_info.get('local')
                        
                        # 使用Embed显示图片
                        success = await discord_forwarder.send_message(
                            webhook_url=webhook_url,
                            content=formatted_content,
                            username=sender_name,
                            embeds=[{
                                'image': {'url': image_url}
                            }]
                        )
                        
                        if not success and img_info.get('local'):
                            # 原始URL失败，尝试本地图床URL
                            logger.info(f"尝试使用本地图床URL: {img_info['local']}")
                            success = await discord_forwarder.send_message(
                                webhook_url=webhook_url,
                                content=formatted_content,
                                username=sender_name,
                                embeds=[{
                                    'image': {'url': img_info['local']}
                                }]
                            )
                else:
                    # 纯文本消息
                    success = await discord_forwarder.send_message(
                        webhook_url=webhook_url,
                        content=formatted_content,
                        username=sender_name
                    )
                
                # 转发附件文件（如果有）
                if processed_attachments and success:
                    for att in processed_attachments:
                        try:
                            att_success = await discord_forwarder.send_with_attachment(
                                webhook_url=webhook_url,
                                content=f"**{sender_name}** 发送了附件:",
                                file_path=att['local_path'],
                                username=sender_name
                            )
                            if not att_success:
                                logger.warning(f"附件发送失败: {att['filename']}")
                        except Exception as e:
                            logger.error(f"发送附件异常: {str(e)}")
                
            elif platform == 'telegram':
                # 格式化引用
                quote_text = formatter.format_quote(quote, 'telegram') if quote else ""
                
                # 格式化提及
                formatted_content = formatter.kmarkdown_to_telegram_html(content)
                formatted_content = formatter.format_mentions(mentions, formatted_content, 'telegram')
                
                # 组合最终内容
                formatted_content = f"{quote_text}<b>{sender_name}</b>: {formatted_content}"
                
                # 如果有附件，添加到内容中
                if processed_attachments:
                    formatted_content += f"\n\n📎 <b>附件</b> ({len(processed_attachments)}个):"
                    for att in processed_attachments:
                        size_mb = att['size'] / (1024 * 1024)
                        formatted_content += f"\n• {att['filename']} ({size_mb:.2f}MB)"
                
                token = bot_config['config'].get('token')
                
                # 如果有图片，发送图片消息
                if processed_images:
                    for img_info in processed_images:
                        # 优先使用原始URL
                        image_url = img_info.get('original') or img_info.get('local')
                        
                        # Telegram发送图片
                        success = await telegram_forwarder.send_photo(
                            token=token,
                            chat_id=target_channel,
                            photo_url=image_url,
                            caption=formatted_content
                        )
                        
                        if not success and img_info.get('local'):
                            # 原始URL失败，尝试本地图床URL
                            logger.info(f"尝试使用本地图床URL: {img_info['local']}")
                            success = await telegram_forwarder.send_photo(
                                token=token,
                                chat_id=target_channel,
                                photo_url=img_info['local'],
                                caption=formatted_content
                            )
                else:
                    # 纯文本消息
                    success = await telegram_forwarder.send_message(
                        token=token,
                        chat_id=target_channel,
                        content=formatted_content
                    )
                
                # 转发附件文件（如果有）
                if processed_attachments and success:
                    for att in processed_attachments:
                        try:
                            att_success = await telegram_forwarder.send_document(
                                token=token,
                                chat_id=target_channel,
                                document_path=att['local_path'],
                                caption=f"📎 {att['filename']}"
                            )
                            if not att_success:
                                logger.warning(f"附件发送失败: {att['filename']}")
                        except Exception as e:
                            logger.error(f"发送附件异常: {str(e)}")
                
            elif platform == 'feishu':
                # 格式化引用
                quote_text = formatter.format_quote(quote, 'feishu') if quote else ""
                
                # 格式化提及
                formatted_content = formatter.kmarkdown_to_feishu_text(content)
                formatted_content = formatter.format_mentions(mentions, formatted_content, 'feishu')
                
                # 组合最终内容
                formatted_content = f"{quote_text}{sender_name}: {formatted_content}"
                
                # 如果有附件，添加到内容中
                if processed_attachments:
                    formatted_content += f"\n\n📎 附件 ({len(processed_attachments)}个):"
                    for att in processed_attachments:
                        size_mb = att['size'] / (1024 * 1024)
                        formatted_content += f"\n• {att['filename']} ({size_mb:.2f}MB)"
                
                app_id = bot_config['config'].get('app_id')
                app_secret = bot_config['config'].get('app_secret')
                
                # 如果有图片，发送图片消息
                if processed_images:
                    # 飞书可以在富文本中显示图片
                    for img_info in processed_images:
                        image_url = img_info.get('original') or img_info.get('local')
                        
                        # 飞书发送图片（使用消息卡片）
                        success = await feishu_forwarder.send_image(
                            app_id=app_id,
                            app_secret=app_secret,
                            chat_id=target_channel,
                            image_url=image_url,
                            caption=formatted_content
                        )
                        
                        if not success and img_info.get('local'):
                            # 原始URL失败，尝试本地图床
                            logger.info(f"尝试使用本地图床URL: {img_info['local']}")
                            success = await feishu_forwarder.send_image(
                                app_id=app_id,
                                app_secret=app_secret,
                                chat_id=target_channel,
                                image_url=img_info['local'],
                                caption=formatted_content
                            )
                else:
                    # 纯文本消息
                    success = await feishu_forwarder.send_message(
                        app_id=app_id,
                        app_secret=app_secret,
                        chat_id=target_channel,
                        content=formatted_content
                    )
                
                # 转发附件文件（如果有）
                if processed_attachments and success:
                    for att in processed_attachments:
                        try:
                            att_success = await feishu_forwarder.send_file(
                                app_id=app_id,
                                app_secret=app_secret,
                                chat_id=target_channel,
                                file_path=att['local_path'],
                                file_name=att['filename']
                            )
                            if not att_success:
                                logger.warning(f"附件发送失败: {att['filename']}")
                        except Exception as e:
                            logger.error(f"发送附件异常: {str(e)}")
                
            else:
                logger.error(f"不支持的平台: {platform}")
                return
            
            # 记录日志
            status = 'success' if success else 'failed'
            log_id = db.add_message_log(
                kook_message_id=message['message_id'],
                kook_channel_id=message['channel_id'],
                content=content,
                message_type=message_type,
                sender_name=sender_name,
                target_platform=platform,
                target_channel=target_channel,
                status=status
            )
            
            if success:
                logger.info(f"消息转发成功: {platform} - {target_channel}")
            else:
                logger.error(f"消息转发失败: {platform} - {target_channel}")
                
                # 添加到失败消息队列，等待重试
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO failed_messages (message_log_id, retry_count)
                        VALUES (?, 0)
                    """, (log_id,))
                    conn.commit()
                
                logger.info(f"消息已添加到重试队列: log_id={log_id}")
                
        except Exception as e:
            logger.error(f"转发消息异常: {str(e)}")


# 创建全局Worker实例
message_worker = MessageWorker()
