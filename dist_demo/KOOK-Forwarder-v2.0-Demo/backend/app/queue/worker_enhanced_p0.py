"""
消息处理Worker增强补丁
✅ P0优化集成：整合所有P0级新功能到Worker
"""
from typing import Dict, Any
from ..utils.logger import logger
from ..processors.file_processor import file_processor
from ..processors.reaction_aggregator import reaction_aggregator
from ..processors.image_strategy import image_strategy
from ..utils.message_deduplicator import message_deduplicator
from ..utils.message_backup import message_backup
from ..database import db


class WorkerP0Enhancements:
    """Worker P0增强功能集"""
    
    @staticmethod
    async def check_and_skip_duplicate(message: Dict[str, Any]) -> bool:
        """
        ✅ P0-9: 检查消息是否重复
        
        Returns:
            True if duplicate (should skip)
        """
        message_id = message.get('message_id')
        if not message_id:
            return False
        
        # 检查是否重复
        if message_deduplicator.is_duplicate(message_id):
            logger.debug(f"消息重复，跳过: {message_id}")
            return True
        
        return False
    
    @staticmethod
    async def mark_message_processed(message: Dict[str, Any]):
        """
        ✅ P0-9: 标记消息已处理
        """
        message_id = message.get('message_id')
        if message_id:
            message_deduplicator.mark_as_processed(
                message_id,
                source="kook",
                channel_id=message.get('channel_id', '')
            )
    
    @staticmethod
    async def backup_message(message: Dict[str, Any]):
        """
        ✅ P0-10: 备份消息（用于崩溃恢复）
        """
        try:
            message_backup.save_message(message)
        except Exception as e:
            logger.error(f"备份消息失败: {str(e)}")
    
    @staticmethod
    async def remove_from_backup(message: Dict[str, Any]):
        """
        ✅ P0-10: 从备份中移除已处理的消息
        """
        try:
            message_id = message.get('message_id')
            if message_id:
                message_backup.remove_message(message_id)
        except Exception as e:
            logger.error(f"移除备份失败: {str(e)}")
    
    @staticmethod
    async def handle_reaction(message: Dict[str, Any]) -> bool:
        """
        ✅ P0-5: 处理表情反应
        
        Returns:
            True if handled successfully
        """
        try:
            action = message.get('action', 'add')
            message_id = message.get('message_id')
            emoji = message.get('emoji', '')
            user_id = message.get('user_id', '')
            
            # 需要获取用户名（从数据库或API）
            user_name = message.get('user_name', f'User_{user_id[:6]}')
            
            if action == 'add':
                reaction_aggregator.add_reaction(
                    message_id,
                    emoji,
                    user_id,
                    user_name
                )
            elif action == 'remove':
                reaction_aggregator.remove_reaction(
                    message_id,
                    emoji,
                    user_id
                )
            
            # 检查是否应该发送更新
            if reaction_aggregator.should_send_update(message_id):
                await WorkerP0Enhancements.send_reaction_update(message_id)
            
            return True
        except Exception as e:
            logger.error(f"处理表情反应失败: {str(e)}")
            return False
    
    @staticmethod
    async def send_reaction_update(message_id: str):
        """
        ✅ P0-5: 发送表情反应更新
        """
        try:
            # 获取原始消息的映射信息
            log = db.get_message_log(message_id)
            if not log:
                logger.warning(f"未找到消息日志: {message_id}")
                return
            
            # 获取映射配置
            mappings = db.get_mappings_by_channel(log['kook_channel_id'])
            
            for mapping in mappings:
                if not mapping.get('enabled'):
                    continue
                
                platform = mapping['target_platform']
                
                # 格式化表情反应
                reaction_text = reaction_aggregator.format_reactions(message_id, platform)
                
                if not reaction_text:
                    continue
                
                # 发送到对应平台
                bot_config = db.get_bot_config(mapping['target_bot_id'])
                if not bot_config:
                    continue
                
                await WorkerP0Enhancements._send_to_platform(
                    platform,
                    bot_config,
                    reaction_text,
                    mapping
                )
            
        except Exception as e:
            logger.error(f"发送表情反应更新失败: {str(e)}")
    
    @staticmethod
    async def process_file_attachments(message: Dict[str, Any], mapping: Dict, bot_config: Dict) -> bool:
        """
        ✅ P0-4: 处理文件附件
        
        Returns:
            True if processed successfully
        """
        file_attachments = message.get('file_attachments', [])
        
        if not file_attachments:
            return True
        
        logger.info(f"开始处理 {len(file_attachments)} 个文件附件")
        
        cookies = message.get('cookies', {})
        platform = mapping['target_platform']
        
        for file_att in file_attachments:
            try:
                # 验证文件类型
                if not file_processor.validate_file_type(file_att['name']):
                    logger.warning(f"跳过不允许的文件类型: {file_att['name']}")
                    continue
                
                # 下载文件
                file_data = await file_processor.download_file(
                    file_att['url'],
                    cookies,
                    referer="https://www.kookapp.cn"
                )
                
                if not file_data:
                    logger.error(f"文件下载失败: {file_att['name']}")
                    continue
                
                # 保存临时文件
                temp_file = await file_processor.save_temp_file(
                    file_data['data'],
                    file_data['filename']
                )
                
                if not temp_file:
                    logger.error(f"保存临时文件失败: {file_att['name']}")
                    continue
                
                # 发送到目标平台
                success = await WorkerP0Enhancements._send_file_to_platform(
                    platform,
                    bot_config,
                    temp_file,
                    file_data,
                    message.get('sender_name', 'KOOK用户')
                )
                
                # 清理临时文件
                file_processor.cleanup_temp_file(temp_file)
                
                if success:
                    logger.info(f"文件转发成功: {file_att['name']}")
                else:
                    logger.error(f"文件转发失败: {file_att['name']}")
                
            except Exception as e:
                logger.error(f"处理文件附件异常: {file_att.get('name', 'unknown')}, {str(e)}")
        
        return True
    
    @staticmethod
    async def process_images_with_strategy(image_urls: List[str], cookies: Dict, 
                                          platform: str) -> List[str]:
        """
        ✅ P0-6: 使用策略处理图片
        
        Returns:
            处理后的图片URL列表
        """
        result_urls = []
        
        for image_url in image_urls:
            try:
                processed_url = await image_strategy.process_image(
                    image_url,
                    cookies,
                    platform
                )
                
                if processed_url:
                    result_urls.append(processed_url)
                else:
                    logger.warning(f"图片处理失败: {image_url}")
            except Exception as e:
                logger.error(f"图片处理异常: {image_url}, {str(e)}")
        
        return result_urls
    
    @staticmethod
    async def _send_to_platform(platform: str, bot_config: Dict, 
                                content: str, mapping: Dict) -> bool:
        """发送消息到目标平台"""
        try:
            config = bot_config.get('config', {})
            
            if platform == 'discord':
                webhook_url = config.get('webhook_url')
                return await discord_forwarder.send_message(
                    webhook_url,
                    content
                )
            elif platform == 'telegram':
                token = config.get('token')
                chat_id = config.get('chat_id')
                return await telegram_forwarder.send_message(
                    token,
                    chat_id,
                    content
                )
            elif platform == 'feishu':
                # TODO: 实现飞书发送
                return False
            else:
                return False
        except Exception as e:
            logger.error(f"发送到{platform}失败: {str(e)}")
            return False
    
    @staticmethod
    async def _send_file_to_platform(platform: str, bot_config: Dict,
                                     file_path, file_data: Dict,
                                     sender_name: str) -> bool:
        """发送文件到目标平台"""
        try:
            config = bot_config.get('config', {})
            
            if platform == 'discord':
                webhook_url = config.get('webhook_url')
                return await discord_forwarder.send_with_attachment(
                    webhook_url,
                    f"📎 文件来自 {sender_name}",
                    str(file_path),
                    username=sender_name
                )
            elif platform == 'telegram':
                token = config.get('token')
                chat_id = config.get('chat_id')
                return await telegram_forwarder.send_file(
                    token,
                    chat_id,
                    str(file_path),
                    caption=f"📎 文件来自 {sender_name}"
                )
            elif platform == 'feishu':
                # TODO: 实现飞书文件发送
                return False
            else:
                return False
        except Exception as e:
            logger.error(f"发送文件到{platform}失败: {str(e)}")
            return False
    
    @staticmethod
    async def restore_pending_messages():
        """
        ✅ P0-10: 恢复崩溃前未发送的消息
        """
        try:
            pending = message_backup.load_pending_messages()
            
            if not pending:
                return
            
            logger.info(f"开始恢复 {len(pending)} 条未发送消息...")
            
            restored_count = 0
            for msg in pending:
                try:
                    # 重新入队
                    await redis_queue.enqueue(msg)
                    restored_count += 1
                except Exception as e:
                    logger.error(f"恢复消息失败: {msg.get('message_id')}, {str(e)}")
            
            logger.info(f"✅ 成功恢复 {restored_count}/{len(pending)} 条消息")
            
        except Exception as e:
            logger.error(f"恢复消息异常: {str(e)}")


# 创建全局增强功能实例
worker_p0_enhancements = WorkerP0Enhancements()
