"""
消息格式转换模块
"""
import re
from typing import Dict


# emoji映射表（KMarkdown表情名到Unicode）
# 已扩充至100+个常用表情
EMOJI_MAP = {
    # 笑脸和情感
    "开心": "😊",
    "笑": "😄",
    "大笑": "😆",
    "哈哈": "😂",
    "笑哭": "😂",
    "微笑": "🙂",
    "眨眼": "😉",
    "傻笑": "😁",
    "坏笑": "😏",
    "害羞": "😳",
    "脸红": "😊",
    
    # 负面情绪
    "哭": "😭",
    "哭泣": "😢",
    "伤心": "😞",
    "失望": "😔",
    "担心": "😟",
    "怒": "😡",
    "生气": "😠",
    "愤怒": "😤",
    "郁闷": "😒",
    "无语": "😑",
    "鄙视": "😒",
    
    # 其他表情
    "惊讶": "😲",
    "震惊": "😱",
    "害怕": "😨",
    "冷汗": "😰",
    "疲惫": "😫",
    "困": "😴",
    "睡觉": "😴",
    "口罩": "😷",
    "病": "🤒",
    "晕": "😵",
    "眩晕": "💫",
    
    # 爱心和手势
    "爱心": "❤️",
    "心": "💗",
    "心碎": "💔",
    "赞": "👍",
    "好的": "👌",
    "握手": "🤝",
    "鼓掌": "👏",
    "拳头": "✊",
    "踩": "👎",
    "耶": "✌️",
    "比心": "🤟",
    "加油": "💪",
    "祈祷": "🙏",
    
    # 符号
    "疑问": "❓",
    "问号": "❓",
    "感叹": "❗",
    "叹号": "❗",
    "警告": "⚠️",
    "禁止": "🚫",
    "对": "✅",
    "错": "❌",
    "勾": "✔️",
    
    # 自然和天气
    "火": "🔥",
    "水": "💧",
    "闪电": "⚡",
    "太阳": "☀️",
    "月亮": "🌙",
    "星星": "⭐",
    "云": "☁️",
    "雨": "🌧️",
    "雪": "❄️",
    "彩虹": "🌈",
    "花": "🌸",
    "玫瑰": "🌹",
    "树": "🌳",
    
    # 动物
    "猫": "🐱",
    "狗": "🐶",
    "熊": "🐻",
    "兔子": "🐰",
    "猴子": "🐵",
    "猪": "🐷",
    "牛": "🐮",
    "鸡": "🐔",
    "鸟": "🐦",
    "鱼": "🐟",
    "龙": "🐉",
    
    # 食物
    "蛋糕": "🎂",
    "生日": "🎂",
    "汉堡": "🍔",
    "披萨": "🍕",
    "咖啡": "☕",
    "茶": "🍵",
    "啤酒": "🍺",
    "干杯": "🍻",
    "苹果": "🍎",
    "香蕉": "🍌",
    "西瓜": "🍉",
    "冰淇淋": "🍦",
    
    # 活动和物品
    "钱": "💰",
    "钱袋": "💰",
    "红包": "🧧",
    "礼物": "🎁",
    "庆祝": "🎉",
    "彩带": "🎊",
    "气球": "🎈",
    "音乐": "🎵",
    "游戏": "🎮",
    "足球": "⚽",
    "篮球": "🏀",
    "奖杯": "🏆",
    "勋章": "🎖️",
    
    # 交通和旅行
    "车": "🚗",
    "飞机": "✈️",
    "火车": "🚄",
    "火箭": "🚀",
    "自行车": "🚲",
    "地铁": "🚇",
    
    # 建筑和地点
    "家": "🏠",
    "学校": "🏫",
    "医院": "🏥",
    "银行": "🏦",
    "酒店": "🏨",
    
    # 办公和学习
    "书": "📚",
    "笔记本": "📓",
    "电脑": "💻",
    "手机": "📱",
    "电话": "📞",
    "邮件": "📧",
    "信封": "✉️",
    "日历": "📅",
    "时钟": "🕐",
    "闹钟": "⏰",
    "灯泡": "💡",
    "想法": "💡",
    "放大镜": "🔍",
    "搜索": "🔍",
    "钥匙": "🔑",
    "锁": "🔒",
    "解锁": "🔓",
    
    # 数字和箭头
    "一": "1️⃣",
    "二": "2️⃣",
    "三": "3️⃣",
    "上": "⬆️",
    "下": "⬇️",
    "左": "⬅️",
    "右": "➡️",
    "返回": "🔙",
    "刷新": "🔄",
    "循环": "🔁",
    
    # 其他常用
    "新": "🆕",
    "热": "🔥",
    "顶": "🔝",
    "酷": "🆒",
    "免费": "🆓",
    "OK": "🆗",
    "666": "👍",
}


class MessageFormatter:
    """消息格式转换器"""
    
    @staticmethod
    def kmarkdown_to_markdown(text: str) -> str:
        """
        将KMarkdown转换为标准Markdown
        
        Args:
            text: KMarkdown文本
            
        Returns:
            Markdown文本
        """
        if not text:
            return ""
        
        # 转换表情 (emj)表情名(emj) → emoji
        text = re.sub(
            r'\(emj\)(\w+)\(emj\)',
            lambda m: EMOJI_MAP.get(m.group(1), f":{m.group(1)}:"),
            text
        )
        
        # KMarkdown和Markdown的基本格式是兼容的
        # **粗体** 保持不变
        # *斜体* 保持不变
        # `代码` 保持不变
        # ~~删除线~~ 保持不变
        
        return text
    
    @staticmethod
    def kmarkdown_to_discord(text: str) -> str:
        """
        将KMarkdown转换为Discord格式
        
        Args:
            text: KMarkdown文本
            
        Returns:
            Discord格式文本
        """
        # Discord支持标准Markdown
        return MessageFormatter.kmarkdown_to_markdown(text)
    
    @staticmethod
    def kmarkdown_to_telegram_html(text: str) -> str:
        """
        将KMarkdown转换为Telegram HTML格式
        
        Args:
            text: KMarkdown文本
            
        Returns:
            Telegram HTML格式文本
        """
        if not text:
            return ""
        
        # 转换表情
        text = re.sub(
            r'\(emj\)(\w+)\(emj\)',
            lambda m: EMOJI_MAP.get(m.group(1), f":{m.group(1)}:"),
            text
        )
        
        # 转换为HTML格式
        # **粗体** → <b>粗体</b>
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        
        # *斜体* → <i>斜体</i>
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        
        # `代码` → <code>代码</code>
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        
        # ~~删除线~~ → <s>删除线</s>
        text = re.sub(r'~~(.+?)~~', r'<s>\1</s>', text)
        
        # [链接文本](URL) → <a href="URL">链接文本</a>
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        
        return text
    
    @staticmethod
    def kmarkdown_to_feishu_text(text: str) -> str:
        """
        将KMarkdown转换为飞书富文本格式
        
        Args:
            text: KMarkdown文本
            
        Returns:
            飞书文本格式
        """
        # 飞书支持Markdown，但需要特殊处理
        return MessageFormatter.kmarkdown_to_markdown(text)
    
    @staticmethod
    def split_long_message(text: str, max_length: int) -> list:
        """
        分割超长消息
        
        Args:
            text: 原始文本
            max_length: 单条消息最大长度
            
        Returns:
            分割后的消息列表
        """
        if len(text) <= max_length:
            return [text]
        
        messages = []
        current = ""
        
        # 按行分割，尽量保持完整性
        lines = text.split('\n')
        
        for line in lines:
            if len(current) + len(line) + 1 <= max_length:
                current += line + '\n'
            else:
                if current:
                    messages.append(current.rstrip())
                    current = ""
                
                # 如果单行就超长，强制分割
                if len(line) > max_length:
                    for i in range(0, len(line), max_length):
                        messages.append(line[i:i + max_length])
                else:
                    current = line + '\n'
        
        if current:
            messages.append(current.rstrip())
        
        return messages
    
    @staticmethod
    def format_mention(user_id: str, username: str, platform: str) -> str:
        """
        格式化@提及
        
        Args:
            user_id: 用户ID
            username: 用户名
            platform: 目标平台
            
        Returns:
            格式化后的提及文本
        """
        if platform == "discord":
            return f"@{username}"
        elif platform == "telegram":
            return f"@{username}"
        elif platform == "feishu":
            return f"@{username}"
        else:
            return f"@{username}"
    
    @staticmethod
    def extract_urls(text: str) -> list:
        """
        提取文本中的URL
        
        Args:
            text: 文本内容
            
        Returns:
            URL列表
        """
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def format_quote(quote: Dict, platform: str) -> str:
        """
        格式化引用消息
        
        Args:
            quote: 引用信息字典
            platform: 目标平台
            
        Returns:
            格式化后的引用文本
        """
        if not quote:
            return ""
        
        author = quote.get('author', '未知用户')
        content = quote.get('content', '')
        
        if platform == "discord":
            # Discord使用 > 引用格式
            return f"> **{author}**: {content}\n"
        elif platform == "telegram":
            # Telegram使用HTML格式
            return f"<blockquote><b>{author}</b>: {content}</blockquote>\n"
        elif platform == "feishu":
            # 飞书使用文本格式
            return f"「回复 {author}」: {content}\n"
        else:
            return f"「回复 {author}」: {content}\n"
    
    @staticmethod
    def format_mentions(mentions: list, content: str, platform: str) -> str:
        """
        格式化@提及
        
        Args:
            mentions: 提及列表
            content: 原始内容
            platform: 目标平台
            
        Returns:
            格式化后的内容
        """
        if not mentions:
            return content
        
        # 处理@全体成员
        for mention in mentions:
            if mention.get('type') == 'all':
                if platform == "discord":
                    content = content.replace('@all', '@everyone')
                    content = content.replace('@所有人', '@everyone')
                elif platform == "telegram":
                    # Telegram没有@所有人功能，用文本代替
                    content = content.replace('@all', '【@所有人】')
                    content = content.replace('@所有人', '【@所有人】')
                elif platform == "feishu":
                    content = content.replace('@all', '@所有人')
        
        return content
    
    @staticmethod
    def format_reaction(reaction: Dict) -> str:
        """
        格式化表情反应为文本
        
        Args:
            reaction: 表情反应信息
            
        Returns:
            格式化文本
        """
        emoji = reaction.get('emoji', '❤️')
        user_id = reaction.get('user_id', '')
        action = reaction.get('action', 'add')
        
        if action == 'add':
            return f"{emoji} 用户{user_id}"
        else:
            return f"取消 {emoji} 用户{user_id}"
    
    @staticmethod
    def create_embed_content(title: str, content: str, 
                           author: str = None, 
                           image_url: str = None,
                           color: int = 0x5865F2) -> Dict:
        """
        创建Discord Embed格式内容
        
        Args:
            title: 标题
            content: 内容
            author: 作者名
            image_url: 图片URL
            color: 颜色（十六进制）
            
        Returns:
            Embed字典
        """
        embed = {
            "title": title,
            "description": content,
            "color": color,
        }
        
        if author:
            embed["author"] = {"name": author}
        
        if image_url:
            embed["image"] = {"url": image_url}
        
        return embed


# 创建全局格式化器实例
formatter = MessageFormatter()
