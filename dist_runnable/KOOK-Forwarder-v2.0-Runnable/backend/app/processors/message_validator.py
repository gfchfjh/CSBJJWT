"""
消息验证模块
用于验证消息内容的合法性和安全性
"""
import re
from typing import Dict, Any, Tuple, List, Optional
from ..utils.logger import logger


class MessageValidator:
    """消息验证器"""
    
    def __init__(self):
        # 危险模式列表（防止注入攻击）
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS脚本
            r'javascript:',  # JavaScript协议
            r'on\w+\s*=',  # 事件处理器
            r'eval\s*\(',  # eval函数
            r'expression\s*\(',  # CSS expression
        ]
        
        # 敏感信息模式（防止泄露）
        self.sensitive_patterns = {
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'phone': r'\b1[3-9]\d{9}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'id_card': r'\b\d{17}[\dXx]\b',
            'password_like': r'(?i)(password|passwd|pwd|密码)[:\s=]+[\S]+',
        }
        
        # URL模式
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
    
    def validate_message(self, message: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        验证消息完整性和安全性
        
        Args:
            message: 消息数据
            
        Returns:
            (是否有效, 错误信息, 清理后的消息)
        """
        try:
            # 1. 验证必需字段
            required_fields = ['message_id', 'channel_id', 'content']
            for field in required_fields:
                if field not in message:
                    return False, f"缺少必需字段: {field}", message
            
            # 2. 验证消息ID格式
            if not self._validate_message_id(message['message_id']):
                return False, "消息ID格式无效", message
            
            # 3. 验证内容长度
            content = message.get('content', '')
            if len(content) > 50000:  # 最大50k字符
                return False, f"消息内容过长: {len(content)}字符", message
            
            # 4. 安全检查
            is_safe, reason = self._check_security(content)
            if not is_safe:
                logger.warning(f"消息安全检查失败: {reason}")
                return False, f"安全检查失败: {reason}", message
            
            # 5. 清理内容
            cleaned_message = self._clean_message(message.copy())
            
            # 6. 验证附件
            if 'image_urls' in message:
                valid, reason = self._validate_attachments(message['image_urls'], 'image')
                if not valid:
                    return False, reason, cleaned_message
            
            if 'file_attachments' in message:
                valid, reason = self._validate_attachments(
                    [att.get('url') for att in message['file_attachments']], 
                    'file'
                )
                if not valid:
                    return False, reason, cleaned_message
            
            return True, "", cleaned_message
            
        except Exception as e:
            logger.error(f"消息验证异常: {str(e)}")
            return False, f"验证异常: {str(e)}", message
    
    def _validate_message_id(self, message_id: str) -> bool:
        """验证消息ID格式"""
        if not message_id:
            return False
        
        # 消息ID应该是字母数字组合，长度合理
        if len(message_id) > 100:
            return False
        
        # 允许字母、数字、下划线、横线
        if not re.match(r'^[a-zA-Z0-9_-]+$', message_id):
            return False
        
        return True
    
    def _check_security(self, content: str) -> Tuple[bool, str]:
        """
        安全检查
        
        Args:
            content: 消息内容
            
        Returns:
            (是否安全, 原因)
        """
        if not content:
            return True, ""
        
        # 检查危险模式
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False, f"检测到潜在危险内容: {pattern}"
        
        # 检查敏感信息（仅警告，不阻止）
        for info_type, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                logger.warning(f"消息包含敏感信息类型: {info_type}, 数量: {len(matches)}")
        
        return True, ""
    
    def _clean_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理消息内容
        
        Args:
            message: 原始消息
            
        Returns:
            清理后的消息
        """
        # 清理内容中的空白字符
        if 'content' in message:
            content = message['content']
            
            # 移除连续的空白行（保留最多2个换行）
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            # 移除行首行尾空白
            content = '\n'.join(line.strip() for line in content.split('\n'))
            
            # 移除零宽字符（可能用于隐藏内容）
            zero_width_chars = [
                '\u200b',  # Zero Width Space
                '\u200c',  # Zero Width Non-Joiner
                '\u200d',  # Zero Width Joiner
                '\ufeff',  # Zero Width No-Break Space
            ]
            for char in zero_width_chars:
                content = content.replace(char, '')
            
            message['content'] = content.strip()
        
        # 验证发送者名称
        if 'sender_name' in message:
            sender = message['sender_name']
            # 限制长度
            if len(sender) > 50:
                message['sender_name'] = sender[:50] + '...'
            # 移除控制字符
            message['sender_name'] = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', message['sender_name'])
        
        return message
    
    def _validate_attachments(self, urls: List[str], 
                             attachment_type: str) -> Tuple[bool, str]:
        """
        验证附件URL
        
        Args:
            urls: URL列表
            attachment_type: 附件类型（image/file）
            
        Returns:
            (是否有效, 错误信息)
        """
        if not urls:
            return True, ""
        
        # 限制附件数量
        max_count = 10 if attachment_type == 'image' else 5
        if len(urls) > max_count:
            return False, f"{attachment_type}数量超限: {len(urls)} > {max_count}"
        
        # 验证每个URL
        for url in urls:
            if not url:
                continue
            
            # 验证URL格式
            if not self.url_pattern.match(url):
                return False, f"无效的URL格式: {url[:50]}"
            
            # 检查URL长度
            if len(url) > 2048:
                return False, f"URL过长: {len(url)}字符"
            
            # 验证协议（仅允许http/https）
            if not url.startswith(('http://', 'https://')):
                return False, f"不支持的协议: {url[:50]}"
        
        return True, ""
    
    def sanitize_for_platform(self, content: str, platform: str) -> str:
        """
        为特定平台清理内容
        
        Args:
            content: 原始内容
            platform: 目标平台（discord/telegram/feishu）
            
        Returns:
            清理后的内容
        """
        if not content:
            return ""
        
        if platform == 'discord':
            # Discord允许Markdown，但限制某些字符
            # 转义@everyone和@here（防止意外提及）
            content = content.replace('@everyone', '@​everyone')
            content = content.replace('@here', '@​here')
            
        elif platform == 'telegram':
            # Telegram HTML模式，需要转义特殊字符
            html_chars = {
                '<': '&lt;',
                '>': '&gt;',
                '&': '&amp;',
            }
            for char, escape in html_chars.items():
                content = content.replace(char, escape)
            
        elif platform == 'feishu':
            # 飞书需要转义某些特殊字符
            pass
        
        return content
    
    def check_spam(self, message: Dict[str, Any]) -> Tuple[bool, str]:
        """
        检查是否为垃圾消息
        
        Args:
            message: 消息数据
            
        Returns:
            (是否为垃圾消息, 原因)
        """
        content = message.get('content', '')
        
        # 空消息
        if not content.strip() and not message.get('image_urls') and not message.get('file_attachments'):
            return True, "空消息"
        
        # 过多重复字符
        if self._has_excessive_repetition(content):
            return True, "包含过多重复字符"
        
        # 过多链接
        urls = self.url_pattern.findall(content)
        if len(urls) > 10:
            return True, f"包含过多链接: {len(urls)}个"
        
        # 全大写（超过80%）
        if len(content) > 20:
            upper_ratio = sum(1 for c in content if c.isupper()) / len(content)
            if upper_ratio > 0.8:
                return True, "过多大写字母"
        
        return False, ""
    
    def _has_excessive_repetition(self, text: str, threshold: int = 10) -> bool:
        """检查是否有过多重复字符"""
        if len(text) < threshold:
            return False
        
        # 检查单个字符重复
        for char in set(text):
            if text.count(char) > threshold and char not in ' \n\t':
                return True
        
        # 检查短字符串重复
        for length in [2, 3]:
            for i in range(len(text) - length):
                substr = text[i:i+length]
                count = text.count(substr)
                if count > threshold // length:
                    return True
        
        return False


# 创建全局验证器实例
message_validator = MessageValidator()
