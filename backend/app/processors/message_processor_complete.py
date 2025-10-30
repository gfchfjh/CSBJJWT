"""
消息处理器 - 完整版
✅ P0-8: 支持所有消息类型
✅ 附件下载和转发
✅ 表情反应处理
✅ 引用消息处理
✅ @提及转换
"""
import aiohttp
import asyncio
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from ..utils.logger import logger


class MessageType:
    """消息类型"""
    TEXT = 1
    IMAGE = 2
    VIDEO = 3
    FILE = 4
    AUDIO = 5
    KMARKDOWN = 9
    CARD = 10


class MessageProcessorComplete:
    """完整的消息处理器"""
    
    def __init__(self):
        self.supported_types = {
            MessageType.TEXT,
            MessageType.IMAGE,
            MessageType.VIDEO,
            MessageType.FILE,
            MessageType.AUDIO,
            MessageType.KMARKDOWN,
            MessageType.CARD
        }
    
    async def process_message(self, message: Dict) -> Dict:
        """
        处理消息（统一入口）
        
        Args:
            message: 原始KOOK消息
            
        Returns:
            处理后的消息（标准化格式）
        """
        msg_type = message.get('type', MessageType.TEXT)
        
        if msg_type not in self.supported_types:
            logger.warning(f"不支持的消息类型: {msg_type}")
            return None
        
        # 基础信息
        processed = {
            'id': message['msg_id'],
            'type': msg_type,
            'content': message.get('content', ''),
            'author': await self._process_author(message.get('author', {})),
            'timestamp': message.get('msg_timestamp', 0),
            'channel_id': message.get('target_id', ''),
            'guild_id': message.get('extra', {}).get('guild_id', ''),
            'attachments': [],
            'embeds': [],
            'mentions': [],
            'quote': None,
            'reactions': []
        }
        
        # 根据类型处理
        if msg_type == MessageType.IMAGE:
            processed['attachments'] = await self._process_image(message)
        
        elif msg_type == MessageType.FILE:
            processed['attachments'] = await self._process_file(message)
        
        elif msg_type == MessageType.VIDEO:
            processed['attachments'] = await self._process_video(message)
        
        elif msg_type in (MessageType.TEXT, MessageType.KMARKDOWN):
            # 处理文本内容
            processed['content'] = await self._process_text_content(message)
            
            # 提取@提及
            processed['mentions'] = await self._extract_mentions(message)
            
            # 处理引用
            processed['quote'] = await self._process_quote(message)
        
        elif msg_type == MessageType.CARD:
            # 卡片消息
            processed['embeds'] = await self._process_card(message)
        
        # 处理表情反应
        if 'extra' in message and 'reaction' in message['extra']:
            processed['reactions'] = await self._process_reactions(message['extra']['reaction'])
        
        return processed
    
    async def _process_author(self, author: Dict) -> Dict:
        """处理作者信息"""
        return {
            'id': author.get('id', ''),
            'username': author.get('username', '未知用户'),
            'nickname': author.get('nickname', author.get('username', '未知用户')),
            'avatar': author.get('avatar', ''),
            'bot': author.get('bot', False),
            'roles': author.get('roles', [])
        }
    
    async def _process_text_content(self, message: Dict) -> str:
        """处理文本内容"""
        content = message.get('content', '')
        
        # 处理KMarkdown格式
        if message.get('type') == MessageType.KMARKDOWN:
            # 转换特殊格式
            content = self._convert_kmarkdown(content)
        
        return content
    
    def _convert_kmarkdown(self, text: str) -> str:
        """转换KMarkdown格式"""
        # (met)用户ID(met) -> @用户
        text = re.sub(r'\(met\)(\d+)\(met\)', r'@\1', text)
        
        # (chn)频道ID(chn) -> #频道
        text = re.sub(r'\(chn\)(\d+)\(chn\)', r'#\1', text)
        
        # (rol)角色ID(rol) -> @角色
        text = re.sub(r'\(rol\)(\d+)\(rol\)', r'@角色\1', text)
        
        # (emj)表情名(emj) -> :表情:
        text = re.sub(r'\(emj\)([^)]+)\(emj\)', r':\1:', text)
        
        return text
    
    async def _extract_mentions(self, message: Dict) -> List[Dict]:
        """提取@提及"""
        mentions = []
        
        # 从extra中获取mention信息
        extra = message.get('extra', {})
        mention_info = extra.get('mention', [])
        
        for user_id in mention_info:
            mentions.append({
                'id': user_id,
                'type': 'user'
            })
        
        # 检查是否@全体成员
        if extra.get('mention_all', False):
            mentions.append({
                'id': 'everyone',
                'type': 'everyone'
            })
        
        # 检查是否@在线成员
        if extra.get('mention_here', False):
            mentions.append({
                'id': 'here',
                'type': 'here'
            })
        
        # 检查角色提及
        mention_roles = extra.get('mention_roles', [])
        for role_id in mention_roles:
            mentions.append({
                'id': role_id,
                'type': 'role'
            })
        
        return mentions
    
    async def _process_quote(self, message: Dict) -> Optional[Dict]:
        """处理引用消息"""
        extra = message.get('extra', {})
        quote = extra.get('quote', None)
        
        if not quote:
            return None
        
        return {
            'id': quote.get('id', ''),
            'type': quote.get('type', MessageType.TEXT),
            'content': quote.get('content', ''),
            'author': await self._process_author(quote.get('author', {})),
            'timestamp': quote.get('create_at', 0)
        }
    
    async def _process_image(self, message: Dict) -> List[Dict]:
        """处理图片消息"""
        attachments = []
        
        # 从content获取图片URL
        image_url = message.get('content', '')
        
        if image_url:
            attachments.append({
                'type': 'image',
                'url': image_url,
                'filename': self._extract_filename(image_url),
                'size': None  # 需要下载后才能知道
            })
        
        # 从attachment获取
        extra = message.get('extra', {})
        attachment = extra.get('attachments', None)
        
        if attachment:
            attachments.append({
                'type': 'image',
                'url': attachment.get('url', ''),
                'filename': attachment.get('name', 'image.jpg'),
                'size': attachment.get('size', 0)
            })
        
        return attachments
    
    async def _process_file(self, message: Dict) -> List[Dict]:
        """处理文件消息"""
        extra = message.get('extra', {})
        attachment = extra.get('attachments', None)
        
        if not attachment:
            return []
        
        return [{
            'type': 'file',
            'url': attachment.get('url', ''),
            'filename': attachment.get('name', 'file'),
            'size': attachment.get('size', 0)
        }]
    
    async def _process_video(self, message: Dict) -> List[Dict]:
        """处理视频消息"""
        extra = message.get('extra', {})
        attachment = extra.get('attachments', None)
        
        if not attachment:
            return []
        
        return [{
            'type': 'video',
            'url': attachment.get('url', ''),
            'filename': attachment.get('name', 'video.mp4'),
            'size': attachment.get('size', 0),
            'duration': attachment.get('duration', 0),
            'width': attachment.get('width', 0),
            'height': attachment.get('height', 0)
        }]
    
    async def _process_card(self, message: Dict) -> List[Dict]:
        """处理卡片消息"""
        import json
        
        try:
            content = message.get('content', '')
            
            if isinstance(content, str):
                cards = json.loads(content)
            else:
                cards = content
            
            embeds = []
            
            for card in cards:
                embed = {
                    'type': card.get('type', 'card'),
                    'theme': card.get('theme', 'primary'),
                    'size': card.get('size', 'lg'),
                    'modules': []
                }
                
                # 处理卡片模块
                modules = card.get('modules', [])
                for module in modules:
                    embed['modules'].append(self._process_card_module(module))
                
                embeds.append(embed)
            
            return embeds
            
        except Exception as e:
            logger.error(f"处理卡片消息失败: {str(e)}")
            return []
    
    def _process_card_module(self, module: Dict) -> Dict:
        """处理卡片模块"""
        module_type = module.get('type', '')
        
        if module_type == 'header':
            return {
                'type': 'header',
                'text': module.get('text', {}).get('content', '')
            }
        
        elif module_type == 'section':
            return {
                'type': 'section',
                'text': module.get('text', {}).get('content', ''),
                'accessory': module.get('accessory', None)
            }
        
        elif module_type == 'image-group':
            return {
                'type': 'image-group',
                'elements': module.get('elements', [])
            }
        
        elif module_type == 'container':
            return {
                'type': 'container',
                'elements': module.get('elements', [])
            }
        
        elif module_type == 'context':
            return {
                'type': 'context',
                'elements': module.get('elements', [])
            }
        
        elif module_type == 'divider':
            return {
                'type': 'divider'
            }
        
        return module
    
    async def _process_reactions(self, reactions: Dict) -> List[Dict]:
        """处理表情反应"""
        result = []
        
        for emoji_id, users in reactions.items():
            result.append({
                'emoji': emoji_id,
                'count': len(users),
                'users': users
            })
        
        return result
    
    def _extract_filename(self, url: str) -> str:
        """从URL提取文件名"""
        from urllib.parse import urlparse, unquote
        
        path = urlparse(url).path
        filename = Path(unquote(path)).name
        
        return filename or 'unknown'
    
    async def download_attachment(
        self, 
        attachment: Dict,
        save_path: Path = None
    ) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        下载附件
        
        Args:
            attachment: 附件信息
            save_path: 保存路径（可选）
            
        Returns:
            (成功标志, 文件路径, 错误信息)
        """
        try:
            url = attachment['url']
            filename = attachment['filename']
            
            if save_path is None:
                from ..config import settings
                save_path = settings.attachment_storage_path
                save_path.mkdir(parents=True, exist_ok=True)
            
            filepath = save_path / filename
            
            # 下载文件
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://www.kookapp.cn/'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=60) as response:
                    if response.status == 200:
                        with open(filepath, 'wb') as f:
                            f.write(await response.read())
                        
                        logger.info(f"附件下载成功: {filename}")
                        return True, filepath, None
                    else:
                        error = f"下载失败，状态码: {response.status}"
                        logger.error(error)
                        return False, None, error
                        
        except Exception as e:
            error = f"下载附件异常: {str(e)}"
            logger.error(error)
            return False, None, error


# 全局实例
message_processor_complete = MessageProcessorComplete()
