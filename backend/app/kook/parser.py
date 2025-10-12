"""KOOK消息解析模块"""
import re
from typing import Dict, Any, Optional, List


class KookMessageParser:
    """KOOK消息解析器"""
    
    # Emoji映射表
    EMOJI_MAP = {
        '开心': '😊',
        '难过': '😢',
        '愤怒': '😠',
        '爱心': '❤️',
        '赞': '👍',
        '踩': '👎',
        '笑哭': '😂',
        '惊讶': '😮',
        '思考': '🤔',
        '鼓掌': '👏',
    }
    
    def parse_message(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析KOOK原始消息
        
        Args:
            raw_data: KOOK WebSocket返回的原始消息数据
            
        Returns:
            解析后的标准消息格式
        """
        try:
            msg_type = raw_data.get('type')
            
            if msg_type == 'MESSAGE_CREATE':
                return self._parse_text_message(raw_data)
            elif msg_type == 'MESSAGE_UPDATE':
                return self._parse_message_update(raw_data)
            elif msg_type == 'MESSAGE_REACTION_ADD':
                return self._parse_reaction(raw_data)
            
            return None
            
        except Exception as e:
            from app.utils.logger import logger
            logger.error(f"解析消息失败: {e}")
            return None
    
    def _parse_text_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析文本消息"""
        content = data.get('content', {})
        author = data.get('author', {})
        
        return {
            'message_id': data.get('id'),
            'channel_id': data.get('channel_id'),
            'server_id': data.get('guild_id'),
            'content': content.get('content', ''),
            'message_type': self._detect_message_type(content),
            'sender_id': author.get('id'),
            'sender_name': author.get('username'),
            'sender_avatar': author.get('avatar'),
            'timestamp': data.get('timestamp'),
            'attachments': content.get('attachments', []),
            'embeds': content.get('embeds', []),
            'mentions': content.get('mentions', []),
            'raw_data': data,
        }
    
    def _parse_message_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析消息更新（编辑）"""
        result = self._parse_text_message(data)
        result['is_edit'] = True
        return result
    
    def _parse_reaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析表情反应"""
        return {
            'message_id': data.get('message_id'),
            'channel_id': data.get('channel_id'),
            'message_type': 'reaction',
            'emoji': data.get('emoji', {}).get('name'),
            'user_id': data.get('user_id'),
            'timestamp': data.get('timestamp'),
        }
    
    def _detect_message_type(self, content: Dict[str, Any]) -> str:
        """检测消息类型"""
        attachments = content.get('attachments', [])
        
        if attachments:
            first_attachment = attachments[0]
            content_type = first_attachment.get('content_type', '')
            
            if content_type.startswith('image/'):
                return 'image'
            elif content_type.startswith('video/'):
                return 'video'
            else:
                return 'file'
        
        if content.get('embeds'):
            return 'embed'
        
        return 'text'
    
    def extract_images(self, message: Dict[str, Any]) -> List[str]:
        """提取消息中的图片URL
        
        Args:
            message: 解析后的消息
            
        Returns:
            图片URL列表
        """
        images = []
        
        # 从附件中提取
        for attachment in message.get('attachments', []):
            if attachment.get('content_type', '').startswith('image/'):
                images.append(attachment.get('url'))
        
        # 从embeds中提取
        for embed in message.get('embeds', []):
            if embed.get('type') == 'image':
                images.append(embed.get('url'))
            if embed.get('thumbnail'):
                images.append(embed['thumbnail'].get('url'))
        
        return images
    
    def extract_mentions(self, message: Dict[str, Any]) -> List[str]:
        """提取@提及的用户
        
        Args:
            message: 解析后的消息
            
        Returns:
            被提及用户ID列表
        """
        return [m.get('id') for m in message.get('mentions', [])]


# 全局解析器实例
parser = KookMessageParser()
