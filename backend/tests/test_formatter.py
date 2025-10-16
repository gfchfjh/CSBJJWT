"""
消息格式转换模块测试
"""
import pytest
from app.processors.formatter import MessageFormatter, formatter


class TestMessageFormatter:
    """MessageFormatter类测试"""
    
    def test_kmarkdown_to_markdown(self):
        """测试KMarkdown到Markdown的转换"""
        # 测试表情转换
        text = "(emj)开心(emj) 今天天气不错"
        result = formatter.kmarkdown_to_markdown(text)
        assert "😊" in result
        assert "今天天气不错" in result
        
        # 测试未知表情
        text = "(emj)未知表情(emj)"
        result = formatter.kmarkdown_to_markdown(text)
        assert ":未知表情:" in result
        
        # 测试空字符串
        result = formatter.kmarkdown_to_markdown("")
        assert result == ""
        
        # 测试None
        result = formatter.kmarkdown_to_markdown(None)
        assert result == ""
    
    def test_kmarkdown_to_discord(self):
        """测试Discord格式转换"""
        text = "**粗体** *斜体* `代码` (emj)赞(emj)"
        result = formatter.kmarkdown_to_discord(text)
        
        assert "**粗体**" in result
        assert "*斜体*" in result
        assert "`代码`" in result
        assert "👍" in result
    
    def test_kmarkdown_to_telegram_html(self):
        """测试Telegram HTML格式转换"""
        text = "**粗体** *斜体* `代码` ~~删除线~~ [链接](https://example.com)"
        result = formatter.kmarkdown_to_telegram_html(text)
        
        assert "<b>粗体</b>" in result
        assert "<i>斜体</i>" in result
        assert "<code>代码</code>" in result
        assert "<s>删除线</s>" in result
        assert '<a href="https://example.com">链接</a>' in result
    
    def test_split_long_message(self):
        """测试超长消息分割"""
        # 测试短消息不分割
        text = "短消息"
        result = formatter.split_long_message(text, 100)
        assert len(result) == 1
        assert result[0] == "短消息"
        
        # 测试长消息分割
        text = "A" * 250
        result = formatter.split_long_message(text, 100)
        assert len(result) == 3
        assert sum(len(msg) for msg in result) == 250
        
        # 测试按行分割
        text = "第一行\n第二行\n第三行"
        result = formatter.split_long_message(text, 10)
        assert len(result) >= 1
    
    def test_format_mention(self):
        """测试@提及格式化"""
        # Discord
        result = formatter.format_mention("123", "用户A", "discord")
        assert "@用户A" in result
        
        # Telegram
        result = formatter.format_mention("456", "用户B", "telegram")
        assert "@用户B" in result
        
        # 飞书
        result = formatter.format_mention("789", "用户C", "feishu")
        assert "@用户C" in result
    
    def test_extract_urls(self):
        """测试URL提取"""
        text = "访问 https://www.kookapp.cn 和 http://example.com"
        urls = formatter.extract_urls(text)
        
        assert len(urls) == 2
        assert "https://www.kookapp.cn" in urls
        assert "http://example.com" in urls
        
        # 测试无URL
        text = "没有链接的文本"
        urls = formatter.extract_urls(text)
        assert len(urls) == 0
    
    def test_format_quote(self):
        """测试引用消息格式化"""
        quote = {
            "author": "张三",
            "content": "原始消息内容"
        }
        
        # Discord格式
        result = formatter.format_quote(quote, "discord")
        assert "> **张三**: 原始消息内容" in result
        
        # Telegram格式
        result = formatter.format_quote(quote, "telegram")
        assert "<blockquote>" in result
        assert "<b>张三</b>" in result
        
        # 飞书格式
        result = formatter.format_quote(quote, "feishu")
        assert "「回复 张三」" in result
        
        # 测试空引用
        result = formatter.format_quote(None, "discord")
        assert result == ""
    
    def test_format_mentions(self):
        """测试@提及格式化"""
        # 测试@全体成员
        mentions = [{"type": "all"}]
        
        # Discord
        content = "大家好 @all"
        result = formatter.format_mentions(mentions, content, "discord")
        assert "@everyone" in result
        
        # Telegram
        content = "通知 @所有人"
        result = formatter.format_mentions(mentions, content, "telegram")
        assert "【@所有人】" in result
        
        # 飞书
        content = "提醒 @all"
        result = formatter.format_mentions(mentions, content, "feishu")
        assert "@所有人" in result
        
        # 测试空提及列表
        result = formatter.format_mentions([], "内容", "discord")
        assert result == "内容"
    
    def test_format_reaction(self):
        """测试表情反应格式化"""
        reaction = {
            "emoji": "❤️",
            "user_id": "12345",
            "action": "add"
        }
        
        result = formatter.format_reaction(reaction)
        assert "❤️" in result
        assert "用户12345" in result
        
        # 测试移除反应
        reaction["action"] = "remove"
        result = formatter.format_reaction(reaction)
        assert "取消" in result
        assert "❤️" in result
    
    def test_create_embed_content(self):
        """测试Discord Embed创建"""
        embed = formatter.create_embed_content(
            title="测试标题",
            content="测试内容",
            author="作者名",
            image_url="https://example.com/image.jpg",
            color=0xFF0000
        )
        
        assert embed["title"] == "测试标题"
        assert embed["description"] == "测试内容"
        assert embed["color"] == 0xFF0000
        assert embed["author"]["name"] == "作者名"
        assert embed["image"]["url"] == "https://example.com/image.jpg"
        
        # 测试最小参数
        embed = formatter.create_embed_content("标题", "内容")
        assert embed["title"] == "标题"
        assert embed["description"] == "内容"
        assert "author" not in embed
        assert "image" not in embed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
