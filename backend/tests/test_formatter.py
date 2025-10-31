"""
消息格式转换器测试
"""
import pytest
from app.processors.formatter import formatter


class TestFormatter:
    """格式转换器测试类"""
    
    def test_kmarkdown_to_discord(self):
        """测试KMarkdown转Discord格式"""
        # 测试粗体
        assert formatter.kmarkdown_to_discord("**粗体**") == "**粗体**"
        
        # 测试斜体
        assert formatter.kmarkdown_to_discord("*斜体*") == "*斜体*"
        
        # 测试代码
        assert formatter.kmarkdown_to_discord("`代码`") == "`代码`"
        
        # 测试emoji
        text = formatter.kmarkdown_to_discord("(emj)开心(emj)")
        assert "😊" in text or "开心" in text
    
    def test_kmarkdown_to_telegram_html(self):
        """测试KMarkdown转Telegram HTML"""
        # 测试粗体
        assert formatter.kmarkdown_to_telegram_html("**粗体**") == "<b>粗体</b>"
        
        # 测试斜体
        assert formatter.kmarkdown_to_telegram_html("*斜体*") == "<i>斜体</i>"
        
        # 测试代码
        assert formatter.kmarkdown_to_telegram_html("`代码`") == "<code>代码</code>"
    
    def test_split_long_message(self):
        """测试长消息分割"""
        # 短消息不分割
        short_msg = "测试" * 100
        result = formatter.split_long_message(short_msg, 2000)
        assert len(result) == 1
        
        # 长消息分割
        long_msg = "测试" * 2000
        result = formatter.split_long_message(long_msg, 2000)
        assert len(result) > 1
        assert all(len(msg) <= 2000 for msg in result)
    
    def test_escape_markdown(self):
        """测试Markdown转义"""
        text = formatter.escape_markdown("测试_下划线_和*星号*")
        assert "\\_" in text or "_" not in text
    
    def test_format_user_mention(self):
        """测试@用户转换"""
        result = formatter.format_user_mention("张三", "123456")
        assert "张三" in result
    
    def test_format_channel_link(self):
        """测试频道链接格式化"""
        result = formatter.format_channel_link("公告频道", "789")
        assert "公告频道" in result


class TestEmojiMapping:
    """Emoji映射测试"""
    
    def test_emoji_map_exists(self):
        """测试emoji映射表存在"""
        from app.processors.formatter import EMOJI_MAP
        assert len(EMOJI_MAP) > 0
    
    def test_common_emojis(self):
        """测试常用emoji"""
        from app.processors.formatter import EMOJI_MAP
        assert "开心" in EMOJI_MAP
        assert "笑" in EMOJI_MAP
        assert "哭" in EMOJI_MAP
        assert "赞" in EMOJI_MAP


class TestPerformance:
    """性能测试"""
    
    def test_format_performance(self):
        """测试格式转换性能"""
        import time
        
        text = "测试消息**粗体***斜体*`代码`" * 100
        
        start = time.time()
        for _ in range(1000):
            formatter.kmarkdown_to_discord(text)
        end = time.time()
        
        # 1000次转换应在1秒内完成
        assert (end - start) < 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
