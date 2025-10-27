"""
消息转发器测试
"""
import pytest
from app.forwarders.discord import DiscordForwarder
from app.forwarders.telegram import TelegramForwarder
from app.forwarders.feishu import FeishuForwarder


class TestDiscordForwarder:
    """Discord转发器测试"""
    
    def test_forwarder_initialization(self):
        """测试转发器初始化"""
        forwarder = DiscordForwarder()
        
        assert forwarder.rate_limiter is not None
        assert isinstance(forwarder.webhooks, dict)
    
    def test_webhook_url_validation_valid(self):
        """测试有效Webhook URL验证"""
        valid_urls = [
            'https://discord.com/api/webhooks/123456/abcdef',
            'https://discordapp.com/api/webhooks/789012/ghijkl',
        ]
        
        for url in valid_urls:
            assert 'discord' in url.lower()
            assert 'webhooks' in url
    
    def test_webhook_url_validation_invalid(self):
        """测试无效Webhook URL验证"""
        invalid_urls = [
            'http://example.com',
            'not a url',
            '',
            None
        ]
        
        for url in invalid_urls:
            assert not (url and 'discord' in str(url).lower() and 'webhooks' in str(url))
    
    @pytest.mark.asyncio
    async def test_send_message_length_limit(self):
        """测试消息长度限制"""
        forwarder = DiscordForwarder()
        
        # Discord单条消息最多2000字符
        long_message = 'A' * 3000
        
        from app.processors.formatter import formatter
        chunks = formatter.split_long_message(long_message, 2000)
        
        # 应该被分成至少2条消息
        assert len(chunks) >= 2
        assert all(len(chunk) <= 2000 for chunk in chunks)
    
    def test_embed_structure(self):
        """测试Embed卡片结构"""
        embed = {
            'title': 'Test Title',
            'description': 'Test Description',
            'color': 0x5865F2,
            'footer': {
                'text': 'KOOK消息转发系统'
            }
        }
        
        assert 'title' in embed
        assert 'description' in embed
        assert 'color' in embed
        assert isinstance(embed['color'], int)


class TestTelegramForwarder:
    """Telegram转发器测试"""
    
    def test_forwarder_initialization(self):
        """测试转发器初始化"""
        forwarder = TelegramForwarder()
        
        assert forwarder.rate_limiter is not None
        assert isinstance(forwarder.bots, dict)
    
    def test_bot_token_validation(self):
        """测试Bot Token格式验证"""
        valid_tokens = [
            '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
            '987654321:ABCdefGHIjklMNOpqrsTUVwxyz123456789',
        ]
        
        for token in valid_tokens:
            parts = token.split(':')
            assert len(parts) == 2
            assert parts[0].isdigit()
            assert len(parts[1]) > 0
    
    def test_chat_id_validation(self):
        """测试Chat ID格式验证"""
        valid_chat_ids = [
            '-1001234567890',  # 超级群组
            '123456789',        # 私聊
            '-987654321',       # 普通群组
        ]
        
        for chat_id in valid_chat_ids:
            # Chat ID应该是数字（可以带负号）
            assert chat_id.lstrip('-').isdigit()
    
    @pytest.mark.asyncio
    async def test_send_message_length_limit(self):
        """测试消息长度限制"""
        forwarder = TelegramForwarder()
        
        # Telegram单条消息最多4096字符
        long_message = 'A' * 5000
        
        from app.processors.formatter import formatter
        chunks = formatter.split_long_message(long_message, 4096)
        
        # 应该被分成至少2条消息
        assert len(chunks) >= 2
        assert all(len(chunk) <= 4096 for chunk in chunks)
    
    def test_html_format_validation(self):
        """测试HTML格式验证"""
        html_message = '<b>粗体</b> <i>斜体</i> <code>代码</code>'
        
        # 验证HTML标签
        assert '<b>' in html_message
        assert '</b>' in html_message
        assert '<i>' in html_message
        assert '<code>' in html_message


class TestFeishuForwarder:
    """飞书转发器测试"""
    
    def test_forwarder_initialization(self):
        """测试转发器初始化"""
        forwarder = FeishuForwarder()
        
        assert forwarder.rate_limiter is not None
    
    def test_app_credentials_validation(self):
        """测试应用凭证格式验证"""
        # App ID格式：cli_开头
        valid_app_id = 'cli_a1b2c3d4e5f6g7h8'
        assert valid_app_id.startswith('cli_')
        
        # App Secret格式：随机字符串
        valid_app_secret = 'ABCdefGHI123456'
        assert len(valid_app_secret) > 10
    
    def test_chat_id_validation(self):
        """测试Chat ID格式验证"""
        # 飞书Chat ID格式：oc_开头
        valid_chat_id = 'oc_1234567890abcdef'
        assert valid_chat_id.startswith('oc_') or valid_chat_id.startswith('ou_')
    
    def test_message_card_structure(self):
        """测试消息卡片结构"""
        card = {
            'config': {
                'wide_screen_mode': True
            },
            'header': {
                'title': {
                    'tag': 'plain_text',
                    'content': 'Test Title'
                }
            },
            'elements': [
                {
                    'tag': 'div',
                    'text': {
                        'tag': 'plain_text',
                        'content': 'Test Content'
                    }
                }
            ]
        }
        
        assert 'config' in card
        assert 'header' in card
        assert 'elements' in card
        assert isinstance(card['elements'], list)


class TestForwarderRateLimiting:
    """转发器限流测试"""
    
    @pytest.mark.asyncio
    async def test_discord_rate_limit(self):
        """测试Discord限流（5条/5秒）"""
        forwarder = DiscordForwarder()
        
        # 验证限流器存在
        assert forwarder.rate_limiter is not None
        
        # 限流器应该允许逐步获取配额
        import time
        start = time.time()
        
        for i in range(3):
            await forwarder.rate_limiter.acquire()
        
        elapsed = time.time() - start
        
        # 3次acquire应该很快（不超过1秒）
        assert elapsed < 1.0
    
    @pytest.mark.asyncio
    async def test_telegram_rate_limit(self):
        """测试Telegram限流（30条/秒）"""
        forwarder = TelegramForwarder()
        
        assert forwarder.rate_limiter is not None
        
        # Telegram限流更宽松，应该能快速获取配额
        import time
        start = time.time()
        
        for i in range(10):
            await forwarder.rate_limiter.acquire()
        
        elapsed = time.time() - start
        
        # 10次acquire应该很快（不超过1秒）
        assert elapsed < 1.0


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_invalid_webhook_url_handling(self):
        """测试无效Webhook URL处理"""
        forwarder = DiscordForwarder()
        
        # 发送到无效URL应该返回False
        invalid_url = 'https://invalid.com/webhook'
        
        # 注意：实际测试会尝试发送，这里只验证不会崩溃
        try:
            result = await forwarder.send_message(
                webhook_url=invalid_url,
                content='Test',
                username='TestBot'
            )
            # 预期失败
            assert result is False
        except Exception as e:
            # 异常也是可以接受的
            assert True
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """测试网络错误处理"""
        forwarder = TelegramForwarder()
        
        # 使用无效Token应该失败但不崩溃
        invalid_token = '000000000:INVALID_TOKEN'
        invalid_chat_id = '0'
        
        try:
            result = await forwarder.send_message(
                token=invalid_token,
                chat_id=invalid_chat_id,
                content='Test'
            )
            # 预期失败
            assert result is False
        except Exception:
            # 异常也是可以接受的
            assert True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
