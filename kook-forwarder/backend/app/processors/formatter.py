"""
消息格式转换模块（✨ P0-3优化：完整支持链接预览、回复引用、表情反应格式化）
"""
import re
from typing import Dict, List, Optional


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
        智能分割超长消息
        
        优先级：
        1. 段落边界（双换行）
        2. 句子边界（。！？）
        3. 子句边界（，；：）
        4. 单词边界（空格）
        5. 强制字符截断
        
        Args:
            text: 原始文本
            max_length: 单条消息最大长度
            
        Returns:
            分割后的消息列表
        """
        if len(text) <= max_length:
            return [text]
        
        messages = []
        
        # 首先尝试按段落分割（双换行）
        paragraphs = re.split(r'\n\n+', text)
        current = ""
        
        for para in paragraphs:
            # 如果当前累积内容+段落不超长，继续累积
            if len(current) + len(para) + 2 <= max_length:
                if current:
                    current += '\n\n' + para
                else:
                    current = para
            else:
                # 保存当前累积内容
                if current:
                    messages.append(current)
                    current = ""
                
                # 如果单个段落就超长，需要进一步分割
                if len(para) > max_length:
                    # 尝试按句子分割
                    sentences = MessageFormatter._split_by_sentences(para, max_length)
                    for i, sent in enumerate(sentences):
                        if i < len(sentences) - 1:
                            messages.append(sent)
                        else:
                            current = sent
                else:
                    current = para
        
        if current:
            messages.append(current)
        
        return messages
    
    @staticmethod
    def _split_by_sentences(text: str, max_length: int) -> list:
        """
        按句子边界分割文本
        
        Args:
            text: 待分割文本
            max_length: 最大长度
            
        Returns:
            分割后的文本列表
        """
        if len(text) <= max_length:
            return [text]
        
        # 句子边界正则：。！？后面可选空格
        sentence_pattern = r'([。！？!?]+\s*)'
        parts = re.split(sentence_pattern, text)
        
        # 重新组合（分隔符要和前一句合并）
        sentences = []
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                sentences.append(parts[i] + parts[i + 1])
            else:
                sentences.append(parts[i])
        
        # 按句子累积
        result = []
        current = ""
        
        for sent in sentences:
            if len(current) + len(sent) <= max_length:
                current += sent
            else:
                if current:
                    result.append(current)
                    current = ""
                
                # 如果单个句子就超长，按子句分割
                if len(sent) > max_length:
                    sub_parts = MessageFormatter._split_by_clauses(sent, max_length)
                    result.extend(sub_parts[:-1])
                    if sub_parts:
                        current = sub_parts[-1]
                else:
                    current = sent
        
        if current:
            result.append(current)
        
        return result
    
    @staticmethod
    def _split_by_clauses(text: str, max_length: int) -> list:
        """
        按子句边界分割文本（逗号、分号等）
        
        Args:
            text: 待分割文本
            max_length: 最大长度
            
        Returns:
            分割后的文本列表
        """
        if len(text) <= max_length:
            return [text]
        
        # 子句边界正则
        clause_pattern = r'([，,；;：:]+\s*)'
        parts = re.split(clause_pattern, text)
        
        # 重新组合
        clauses = []
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                clauses.append(parts[i] + parts[i + 1])
            else:
                clauses.append(parts[i])
        
        # 按子句累积
        result = []
        current = ""
        
        for clause in clauses:
            if len(current) + len(clause) <= max_length:
                current += clause
            else:
                if current:
                    result.append(current)
                    current = ""
                
                # 如果单个子句就超长，按单词分割
                if len(clause) > max_length:
                    word_parts = MessageFormatter._split_by_words(clause, max_length)
                    result.extend(word_parts[:-1])
                    if word_parts:
                        current = word_parts[-1]
                else:
                    current = clause
        
        if current:
            result.append(current)
        
        return result
    
    @staticmethod
    def _split_by_words(text: str, max_length: int) -> list:
        """
        按单词边界分割文本
        
        Args:
            text: 待分割文本
            max_length: 最大长度
            
        Returns:
            分割后的文本列表
        """
        if len(text) <= max_length:
            return [text]
        
        # 按空格分割单词
        words = text.split()
        
        result = []
        current = ""
        
        for word in words:
            if len(current) + len(word) + 1 <= max_length:
                current += (" " if current else "") + word
            else:
                if current:
                    result.append(current)
                    current = ""
                
                # 如果单个单词就超长，强制截断
                if len(word) > max_length:
                    for i in range(0, len(word), max_length):
                        chunk = word[i:i + max_length]
                        if i + max_length < len(word):
                            result.append(chunk)
                        else:
                            current = chunk
                else:
                    current = word
        
        if current:
            result.append(current)
        
        return result
    
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
    
    @staticmethod
    def format_quote_message(quote: Optional[Dict], current_content: str, platform: str) -> str:
        """
        格式化回复引用消息（✨ P0-3新增）
        
        Args:
            quote: 引用消息对象 {"message_id": "xxx", "author": "用户A", "content": "原始消息"}
            current_content: 当前回复内容
            platform: 目标平台 (discord/telegram/feishu)
        
        Returns:
            格式化后的完整消息
        """
        if not quote:
            return current_content
        
        author = quote.get('author', '未知用户')
        content = quote.get('content', '')
        
        # 限制引用内容长度
        if len(content) > 100:
            content = content[:100] + '...'
        
        if platform == "discord":
            # Discord格式: > 引用内容（带竖线）
            quoted_text = '\n'.join(f"> {line}" for line in content.split('\n'))
            return f"{quoted_text}\n> **—— {author}**\n\n{current_content}"
        
        elif platform == "telegram":
            # Telegram格式: HTML引用块
            return f"""<blockquote>
<b>{author}</b>: {content}
</blockquote>

{current_content}"""
        
        elif platform == "feishu":
            # 飞书格式: 文本引用
            return f"""【引用 {author}】
{content}
────────
{current_content}"""
        
        return current_content
    
    @staticmethod
    def format_link_preview(link_preview: Optional[Dict], platform: str) -> Optional[Dict]:
        """
        格式化链接预览（✨ P0-3新增）
        
        Args:
            link_preview: {"url": "...", "title": "...", "description": "...", "image": "..."}
            platform: 目标平台
        
        Returns:
            平台特定的链接卡片格式
        """
        if not link_preview:
            return None
        
        url = link_preview.get('url', '')
        title = link_preview.get('title', url)
        description = link_preview.get('description', '')
        image = link_preview.get('image')
        
        if platform == "discord":
            # Discord Embed卡片
            embed = {
                "title": title,
                "url": url,
                "color": 0x3498db,  # 蓝色
            }
            
            if description:
                # 限制描述长度
                if len(description) > 200:
                    description = description[:200] + '...'
                embed["description"] = description
            
            if image:
                embed["thumbnail"] = {"url": image}
            
            return embed
        
        elif platform == "telegram":
            # Telegram: 使用HTML格式
            html = f"""<b>🔗 {title}</b>"""
            if description:
                if len(description) > 200:
                    description = description[:200] + '...'
                html += f"\n{description}"
            html += f"\n\n<a href=\"{url}\">{url}</a>"
            return {"html": html, "url": url}
        
        elif platform == "feishu":
            # 飞书: 消息卡片
            card = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": f"🔗 {title}"
                        }
                    },
                    "elements": []
                }
            }
            
            if description:
                if len(description) > 200:
                    description = description[:200] + '...'
                card["card"]["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": description
                    }
                })
            
            card["card"]["elements"].append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "查看链接"
                    },
                    "url": url,
                    "type": "primary"
                }]
            })
            
            return card
        
        return None
    
    @staticmethod
    def format_reactions(reactions: List[Dict], platform: str) -> str:
        """
        格式化表情反应聚合（✨ P0-3新增）
        
        Args:
            reactions: [{"emoji": "❤️", "users": ["用户A", "用户B"], "count": 2}, ...]
            platform: 目标平台
        
        Returns:
            格式化后的反应文本
        """
        if not reactions:
            return ""
        
        # 聚合显示: ❤️ 用户A、用户B (2) | 👍 用户C (1)
        reaction_texts = []
        
        for reaction in reactions:
            emoji = reaction.get("emoji", "❓")
            users = reaction.get("users", [])
            count = reaction.get("count", 0)
            
            if not users:
                continue
            
            # 最多显示3个用户名
            user_text = "、".join(users[:3])
            if count > len(users):
                user_text += f" 等{count}人"
            elif count > 3:
                user_text = "、".join(users[:3]) + f" 等{count}人"
            
            reaction_texts.append(f"{emoji} {user_text} ({count})")
        
        if not reaction_texts:
            return ""
        
        # 根据平台格式化
        if platform == "discord":
            return "\n\n💬 **反应**: " + " | ".join(reaction_texts)
        elif platform == "telegram":
            return "\n\n💬 <b>反应</b>: " + " | ".join(reaction_texts)
        elif platform == "feishu":
            return "\n\n💬 反应: " + " | ".join(reaction_texts)
        
        return "\n\n💬 反应: " + " | ".join(reaction_texts)
    
    @staticmethod
    def format_mentions(content: str, mentions: List[Dict], platform: str) -> str:
        """
        格式化@提及（✨ P0-3增强）
        
        Args:
            content: 原始消息内容
            mentions: [{"type": "user", "user_id": "123", "username": "用户A"}, ...]
            platform: 目标平台
        
        Returns:
            格式化后的消息
        """
        if not mentions:
            return content
        
        for mention in mentions:
            mention_type = mention.get('type')
            
            if mention_type == 'user':
                username = mention.get('username', '未知用户')
                user_id = mention.get('user_id', '')
                
                # KOOK提及格式: (met)user_id(met) 或 @username
                kook_mention_pattern1 = f"(met){user_id}(met)"
                kook_mention_pattern2 = f"@{username}"
                
                if platform == "discord":
                    # Discord: 加粗用户名（无法实现真实@）
                    target_mention = f"**@{username}**"
                elif platform == "telegram":
                    # Telegram: HTML加粗
                    target_mention = f"<b>@{username}</b>"
                elif platform == "feishu":
                    # 飞书: 加粗显示（需要用户ID映射才能真实@）
                    target_mention = f"**@{username}**"
                else:
                    target_mention = f"@{username}"
                
                # 替换两种格式
                content = content.replace(kook_mention_pattern1, target_mention)
                content = content.replace(kook_mention_pattern2, target_mention)
            
            elif mention_type == 'all':
                # @全体成员
                if platform == "discord":
                    content = content.replace("(met)all(met)", "@everyone")
                    content = content.replace("@全体成员", "@everyone")
                elif platform == "telegram":
                    content = content.replace("(met)all(met)", "[@all]")
                    content = content.replace("@全体成员", "[@all]")
                elif platform == "feishu":
                    content = content.replace("(met)all(met)", "@所有人")
                    content = content.replace("@全体成员", "@所有人")
            
            elif mention_type == 'here':
                # @在线成员
                if platform == "discord":
                    content = content.replace("(met)here(met)", "@here")
                elif platform == "telegram":
                    content = content.replace("(met)here(met)", "[@online]")
                elif platform == "feishu":
                    content = content.replace("(met)here(met)", "@在线成员")
            
            elif mention_type == 'role':
                # @角色
                role_name = mention.get('role_name', '角色')
                content = content.replace(f"(rol){mention.get('role_id', '')}(rol)", f"@{role_name}")
        
        return content


# 创建全局格式化器实例
formatter = MessageFormatter()
