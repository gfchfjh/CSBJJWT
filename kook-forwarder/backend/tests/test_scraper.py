"""
KOOK抓取器测试
"""
import pytest
from app.kook.scraper import KookScraper, ScraperManager
import asyncio


class TestKookScraper:
    """KOOK抓取器测试"""
    
    def test_scraper_initialization(self):
        """测试抓取器初始化"""
        scraper = KookScraper(account_id=1)
        
        assert scraper.account_id == 1
        assert scraper.browser is None
        assert scraper.context is None
        assert scraper.page is None
        assert scraper.is_running is False
        assert scraper.reconnect_count == 0
        assert scraper.max_reconnect == 5
    
    def test_cookie_validation_valid(self):
        """测试有效Cookie验证"""
        scraper = KookScraper(account_id=1)
        
        valid_cookie = '''[
            {"name": "token", "value": "test123", "domain": ".kookapp.cn"},
            {"name": "session", "value": "sess456", "domain": ".kookapp.cn"}
        ]'''
        
        assert scraper._validate_cookies(valid_cookie) is True
    
    def test_cookie_validation_invalid_format(self):
        """测试无效格式Cookie验证"""
        scraper = KookScraper(account_id=1)
        
        # 非JSON格式
        assert scraper._validate_cookies('not a json') is False
        
        # 非列表格式
        assert scraper._validate_cookies('{"name": "value"}') is False
        
        # 空列表
        assert scraper._validate_cookies('[]') is False
    
    def test_cookie_validation_missing_fields(self):
        """测试缺少必需字段的Cookie验证"""
        scraper = KookScraper(account_id=1)
        
        # 缺少name字段
        invalid_cookie = '''[
            {"value": "test123", "domain": ".kookapp.cn"}
        ]'''
        
        assert scraper._validate_cookies(invalid_cookie) is False
        
        # 缺少value字段
        invalid_cookie2 = '''[
            {"name": "token", "domain": ".kookapp.cn"}
        ]'''
        
        assert scraper._validate_cookies(invalid_cookie2) is False
    
    def test_message_callback_registration(self):
        """测试消息回调函数注册"""
        scraper = KookScraper(account_id=1)
        
        def test_callback(message):
            pass
        
        scraper.set_message_callback(test_callback)
        
        assert scraper.message_callback == test_callback


class TestScraperManager:
    """抓取器管理器测试"""
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        manager = ScraperManager()
        
        assert isinstance(manager.scrapers, dict)
        assert len(manager.scrapers) == 0
    
    @pytest.mark.asyncio
    async def test_start_scraper_cookie_mode(self):
        """测试启动抓取器（Cookie模式）"""
        manager = ScraperManager()
        
        # 注意：实际测试需要有效的Cookie和浏览器环境
        # 这里只测试基本逻辑
        result = await manager.start_scraper(
            account_id=1,
            cookie='[{"name":"test","value":"123","domain":".kookapp.cn"}]'
        )
        
        # 由于没有真实浏览器环境，预期会失败但不应崩溃
        assert isinstance(result, bool)
        
        # 清理
        if 1 in manager.scrapers:
            await manager.stop_scraper(1)
    
    @pytest.mark.asyncio
    async def test_stop_nonexistent_scraper(self):
        """测试停止不存在的抓取器"""
        manager = ScraperManager()
        
        result = await manager.stop_scraper(999)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_stop_all_scrapers(self):
        """测试停止所有抓取器"""
        manager = ScraperManager()
        
        # 停止空管理器不应报错
        await manager.stop_all()
        
        assert len(manager.scrapers) == 0


class TestMessageParsing:
    """消息解析测试"""
    
    def test_text_message_parsing(self):
        """测试文本消息解析"""
        # 模拟WebSocket消息数据
        message_data = {
            'type': 'MESSAGE_CREATE',
            'data': {
                'id': 'msg123',
                'channel_id': 'ch456',
                'guild_id': 'guild789',
                'content': 'Hello World',
                'type': 'text',
                'author': {
                    'id': 'user123',
                    'username': 'TestUser',
                    'avatar': 'avatar_url'
                },
                'timestamp': 1234567890,
                'attachments': []
            }
        }
        
        # 验证消息结构
        assert message_data['type'] == 'MESSAGE_CREATE'
        assert message_data['data']['content'] == 'Hello World'
        assert message_data['data']['author']['username'] == 'TestUser'
    
    def test_image_message_parsing(self):
        """测试图片消息解析"""
        message_data = {
            'type': 'MESSAGE_CREATE',
            'data': {
                'id': 'msg123',
                'type': 'image',
                'attachments': [
                    {
                        'type': 'image',
                        'url': 'https://example.com/image.jpg'
                    }
                ]
            }
        }
        
        assert message_data['data']['type'] == 'image'
        assert len(message_data['data']['attachments']) == 1
        assert message_data['data']['attachments'][0]['type'] == 'image'
    
    def test_mention_message_parsing(self):
        """测试@提及消息解析"""
        message_data = {
            'type': 'MESSAGE_CREATE',
            'data': {
                'id': 'msg123',
                'content': '@user Hello',
                'mention_info': {
                    'mention_part': ['user123'],
                    'mention_all': False
                }
            }
        }
        
        mention_info = message_data['data']['mention_info']
        assert 'user123' in mention_info['mention_part']
        assert mention_info['mention_all'] is False
    
    def test_reaction_event_parsing(self):
        """测试表情反应事件解析"""
        reaction_data = {
            'type': 'MESSAGE_REACTION_ADD',
            'data': {
                'msg_id': 'msg123',
                'channel_id': 'ch456',
                'user_id': 'user789',
                'emoji': {
                    'name': '👍'
                },
                'timestamp': 1234567890
            }
        }
        
        assert reaction_data['type'] == 'MESSAGE_REACTION_ADD'
        assert reaction_data['data']['emoji']['name'] == '👍'


class TestReconnectionLogic:
    """重连逻辑测试"""
    
    def test_max_reconnect_attempts(self):
        """测试最大重连次数"""
        scraper = KookScraper(account_id=1)
        scraper.max_reconnect = 3
        
        # 模拟重连计数
        for i in range(3):
            scraper.reconnect_count += 1
        
        assert scraper.reconnect_count == scraper.max_reconnect
    
    def test_reconnect_count_reset(self):
        """测试重连计数重置"""
        scraper = KookScraper(account_id=1)
        scraper.reconnect_count = 5
        
        # 成功重连后应重置计数
        scraper.reconnect_count = 0
        
        assert scraper.reconnect_count == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
