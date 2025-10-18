"""
测试消息验证模块
"""
import pytest
from app.processors.message_validator import MessageValidator, message_validator


class TestMessageValidator:
    """测试消息验证器"""
    
    def test_validate_valid_message(self):
        """测试验证有效消息"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '这是一条测试消息',
            'sender_name': '测试用户'
        }
        
        valid, reason, cleaned = message_validator.validate_message(message)
        assert valid is True
        assert reason == ""
        assert 'content' in cleaned
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        message = {
            'message_id': 'msg_123',
            # 缺少 channel_id 和 content
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
        assert '缺少必需字段' in reason
    
    def test_invalid_message_id(self):
        """测试无效消息ID"""
        # 包含非法字符
        message = {
            'message_id': 'msg@#$%',
            'channel_id': 'ch_456',
            'content': '测试'
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
        assert '消息ID格式无效' in reason
    
    def test_message_id_too_long(self):
        """测试消息ID过长"""
        message = {
            'message_id': 'x' * 101,  # 超过100字符
            'channel_id': 'ch_456',
            'content': '测试'
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
    
    def test_content_too_long(self):
        """测试内容过长"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': 'x' * 50001  # 超过50k字符
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
        assert '内容过长' in reason
    
    def test_dangerous_content_xss(self):
        """测试XSS脚本检测"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '<script>alert("xss")</script>'
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
        assert '危险内容' in reason
    
    def test_dangerous_content_javascript(self):
        """测试JavaScript协议检测"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '<a href="javascript:alert()">点击</a>'
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
    
    def test_dangerous_content_event_handler(self):
        """测试事件处理器检测"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '<img src="x" onerror="alert()">'
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
    
    def test_clean_message_whitespace(self):
        """测试清理空白字符"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '   测试消息   \n\n\n\n多余空行   '
        }
        
        valid, _, cleaned = message_validator.validate_message(message)
        assert valid is True
        assert cleaned['content'] == '测试消息\n\n多余空行'
    
    def test_clean_zero_width_chars(self):
        """测试清理零宽字符"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '测试\u200b消息\u200c\u200d'
        }
        
        valid, _, cleaned = message_validator.validate_message(message)
        assert valid is True
        assert '\u200b' not in cleaned['content']
        assert '\u200c' not in cleaned['content']
        assert '\u200d' not in cleaned['content']
    
    def test_clean_sender_name_too_long(self):
        """测试清理过长发送者名称"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '测试',
            'sender_name': 'x' * 60
        }
        
        valid, _, cleaned = message_validator.validate_message(message)
        assert valid is True
        assert len(cleaned['sender_name']) <= 53  # 50 + '...'
    
    def test_validate_image_attachments(self):
        """测试验证图片附件"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '测试',
            'image_urls': [
                'https://example.com/image1.jpg',
                'https://example.com/image2.png'
            ]
        }
        
        valid, _, _ = message_validator.validate_message(message)
        assert valid is True
    
    def test_too_many_image_attachments(self):
        """测试图片数量超限"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '测试',
            'image_urls': ['https://example.com/image.jpg'] * 11  # 超过10个
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
        assert '数量超限' in reason
    
    def test_invalid_url_format(self):
        """测试无效URL格式"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '测试',
            'image_urls': ['not-a-valid-url']
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
        assert '无效的URL格式' in reason
    
    def test_unsupported_protocol(self):
        """测试不支持的协议"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '测试',
            'image_urls': ['ftp://example.com/image.jpg']
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
        assert '不支持的协议' in reason
    
    def test_url_too_long(self):
        """测试URL过长"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '测试',
            'image_urls': ['https://example.com/' + 'x' * 2100]
        }
        
        valid, reason, _ = message_validator.validate_message(message)
        assert valid is False
        assert 'URL过长' in reason
    
    def test_sanitize_discord(self):
        """测试Discord平台清理"""
        content = '测试 @everyone 和 @here 提及'
        cleaned = message_validator.sanitize_for_platform(content, 'discord')
        
        # 应该插入零宽字符，防止真实提及
        assert '@everyone' not in cleaned or '​' in cleaned
    
    def test_sanitize_telegram(self):
        """测试Telegram平台清理"""
        content = '测试 <tag> 和 & 字符 >'
        cleaned = message_validator.sanitize_for_platform(content, 'telegram')
        
        assert '&lt;' in cleaned
        assert '&gt;' in cleaned
        assert '&amp;' in cleaned
    
    def test_check_spam_empty(self):
        """测试检测空消息垃圾"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '   '
        }
        
        is_spam, reason = message_validator.check_spam(message)
        assert is_spam is True
        assert '空消息' in reason
    
    def test_check_spam_excessive_repetition(self):
        """测试检测过多重复字符"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': 'aaaaaaaaaaaaaaaaaaaaaa'
        }
        
        is_spam, reason = message_validator.check_spam(message)
        assert is_spam is True
        assert '重复字符' in reason
    
    def test_check_spam_too_many_urls(self):
        """测试检测过多链接"""
        urls = ' '.join([f'http://example{i}.com' for i in range(15)])
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': urls
        }
        
        is_spam, reason = message_validator.check_spam(message)
        assert is_spam is True
        assert '过多链接' in reason
    
    def test_check_spam_all_caps(self):
        """测试检测全大写消息"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': 'THIS IS ALL CAPS MESSAGE FOR TESTING PURPOSE'
        }
        
        is_spam, reason = message_validator.check_spam(message)
        assert is_spam is True
        assert '大写字母' in reason
    
    def test_normal_message_not_spam(self):
        """测试正常消息不被识别为垃圾"""
        message = {
            'message_id': 'msg_123',
            'channel_id': 'ch_456',
            'content': '这是一条正常的消息，包含合理的内容。'
        }
        
        is_spam, _ = message_validator.check_spam(message)
        assert is_spam is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
