"""
KOOK消息解析器 - 完整支持所有消息类型
✨ P0-1优化: 新增表情反应、回复引用、链接预览、附件文件支持
"""
import re
import aiohttp
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from ..utils.logger import logger


@dataclass
class ReactionMessage:
    """表情反应消息"""
    emoji: str
    users: List[str]
    count: int
    message_id: str


@dataclass
class QuoteMessage:
    """回复引用消息"""
    quoted_message_id: str
    quoted_content: str
    quoted_author: str
    quoted_author_id: str
    current_content: str
    current_author: str


@dataclass
class LinkPreview:
    """链接预览"""
    url: str
    title: Optional[str]
    description: Optional[str]
    image: Optional[str]
    site_name: Optional[str]


@dataclass
class Attachment:
    """文件附件"""
    filename: str
    size: int  # bytes
    url: str
    file_type: str
    mime_type: Optional[str]


class FileSizeExceeded(Exception):
    """文件大小超限异常"""
    pass


class KookMessageParser:
    """KOOK消息解析器 - 完整版"""
    
    # 最大文件大小 50MB
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    # KOOK表情代码到emoji的映射
    KOOK_EMOJI_MAP = {
        "[开心]": "😊",
        "[笑]": "😄",
        "[大笑]": "😆",
        "[哈哈]": "😂",
        "[笑哭]": "😂",
        "[害羞]": "😳",
        "[爱心]": "❤️",
        "[心碎]": "💔",
        "[赞]": "👍",
        "[踩]": "👎",
        "[加油]": "💪",
        "[握手]": "🤝",
        "[鼓掌]": "👏",
        "[OK]": "👌",
        "[耶]": "✌️",
        "[祈祷]": "🙏",
        "[哭]": "😭",
        "[哭泣]": "😢",
        "[伤心]": "😞",
        "[生气]": "😠",
        "[愤怒]": "😤",
        "[惊讶]": "😲",
        "[震惊]": "😱",
        "[疑问]": "❓",
        "[感叹]": "❗",
        "[火]": "🔥",
        "[闪电]": "⚡",
        "[星星]": "⭐",
        "[月亮]": "🌙",
        "[太阳]": "☀️",
        "[彩虹]": "🌈",
        "[花]": "🌸",
    }
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建aiohttp会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def parse_message_type(self, msg: Dict) -> str:
        """
        判断消息类型
        
        Returns:
            text / image / file / card / reaction / system
        """
        msg_type = msg.get("type", 1)
        
        # KOOK消息类型映射
        # 1: 文本消息
        # 2: 图片消息
        # 3: 视频消息
        # 4: 文件消息
        # 8: 音频消息
        # 9: KMarkdown
        # 10: 卡片消息
        
        if msg_type == 1:
            return "text"
        elif msg_type == 2:
            return "image"
        elif msg_type in [3, 4, 8]:
            return "file"
        elif msg_type == 10:
            return "card"
        elif msg_type == 9:
            # KMarkdown可能包含文本、图片、链接
            content = msg.get("content", "")
            if self._has_image_markdown(content):
                return "image"
            elif self._has_link(content):
                return "link"
            return "text"
        else:
            return "text"
    
    def _has_image_markdown(self, content: str) -> bool:
        """检查是否包含图片Markdown"""
        return bool(re.search(r'!\[.*?\]\(.*?\)', content))
    
    def _has_link(self, content: str) -> bool:
        """检查是否包含链接"""
        return bool(re.search(r'https?://\S+', content))
    
    def parse_reactions(self, msg: Dict) -> List[ReactionMessage]:
        """
        解析表情反应
        
        KOOK表情反应格式:
        {
            "reactions": [
                {
                    "emoji": {"id": "xxx", "name": "开心"},
                    "count": 2,
                    "me": false,
                    "users": ["user1", "user2"]
                }
            ]
        }
        
        Returns:
            ReactionMessage列表
        """
        reactions = msg.get("reactions", [])
        result = []
        
        for reaction in reactions:
            emoji_data = reaction.get("emoji", {})
            emoji_name = emoji_data.get("name", "")
            
            # 转换KOOK表情代码为emoji
            emoji = self.KOOK_EMOJI_MAP.get(f"[{emoji_name}]", emoji_name)
            
            users = reaction.get("users", [])
            count = reaction.get("count", 0)
            message_id = msg.get("msg_id", "")
            
            result.append(ReactionMessage(
                emoji=emoji,
                users=users,
                count=count,
                message_id=message_id
            ))
        
        return result
    
    def parse_quote(self, msg: Dict) -> Optional[QuoteMessage]:
        """
        解析回复引用
        
        KOOK回复格式:
        {
            "quote": {
                "id": "quoted_msg_id",
                "type": 1,
                "content": "被引用的消息内容",
                "create_at": 1234567890,
                "author": {
                    "id": "user_id",
                    "username": "用户名",
                    "avatar": "avatar_url"
                }
            },
            "content": "当前回复内容"
        }
        
        Returns:
            QuoteMessage对象或None
        """
        quote_data = msg.get("quote")
        if not quote_data:
            return None
        
        try:
            quoted_author = quote_data.get("author", {})
            current_author_data = msg.get("author", {})
            
            return QuoteMessage(
                quoted_message_id=quote_data.get("id", ""),
                quoted_content=quote_data.get("content", ""),
                quoted_author=quoted_author.get("username", "未知用户"),
                quoted_author_id=quoted_author.get("id", ""),
                current_content=msg.get("content", ""),
                current_author=current_author_data.get("username", "未知用户")
            )
        except Exception as e:
            logger.error(f"解析引用消息失败: {e}")
            return None
    
    async def parse_link_preview(self, url: str) -> Optional[LinkPreview]:
        """
        解析链接预览（获取Open Graph元数据）
        
        Args:
            url: 要解析的URL
        
        Returns:
            LinkPreview对象或None
        """
        try:
            session = await self._get_session()
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                
                # 解析Open Graph标签
                title = self._extract_og_tag(html, "og:title") or self._extract_title_tag(html)
                description = self._extract_og_tag(html, "og:description")
                image = self._extract_og_tag(html, "og:image")
                site_name = self._extract_og_tag(html, "og:site_name")
                
                if not title:
                    # 如果没有找到标题，使用URL
                    title = url
                
                return LinkPreview(
                    url=url,
                    title=title,
                    description=description,
                    image=image,
                    site_name=site_name
                )
                
        except asyncio.TimeoutError:
            logger.warning(f"链接预览超时: {url}")
            return None
        except Exception as e:
            logger.error(f"解析链接预览失败 {url}: {e}")
            return None
    
    def _extract_og_tag(self, html: str, property_name: str) -> Optional[str]:
        """提取Open Graph标签"""
        pattern = f'<meta\\s+property=["\']?{property_name}["\']?\\s+content=["\']([^"\']+)["\']'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # 尝试反向匹配（content在前）
        pattern = f'<meta\\s+content=["\']([^"\']+)["\']\\s+property=["\']?{property_name}["\']?'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_title_tag(self, html: str) -> Optional[str]:
        """提取<title>标签"""
        match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
        return match.group(1) if match else None
    
    def parse_attachment(self, msg: Dict) -> Optional[Attachment]:
        """
        解析文件附件
        
        KOOK附件格式:
        {
            "type": 4,  # 文件消息
            "attachments": {
                "type": "file",
                "url": "https://...",
                "name": "文件名.pdf",
                "file_type": "application/pdf",
                "size": 1024000  # bytes
            }
        }
        
        Returns:
            Attachment对象或None
        
        Raises:
            FileSizeExceeded: 文件超过50MB
        """
        attachment_data = msg.get("attachments")
        if not attachment_data:
            # 尝试从content中提取（某些情况下附件信息在content中）
            content = msg.get("content", "")
            if content.startswith("http"):
                # 简单的文件URL
                return Attachment(
                    filename=content.split("/")[-1],
                    size=0,  # 未知大小
                    url=content,
                    file_type="unknown",
                    mime_type=None
                )
            return None
        
        try:
            filename = attachment_data.get("name", "unknown")
            size = attachment_data.get("size", 0)
            url = attachment_data.get("url", "")
            file_type = attachment_data.get("file_type", "unknown")
            mime_type = attachment_data.get("type")
            
            # 检查文件大小限制
            if size > self.MAX_FILE_SIZE:
                raise FileSizeExceeded(
                    f"文件 {filename} 大小 {size/1024/1024:.2f}MB 超过50MB限制"
                )
            
            return Attachment(
                filename=filename,
                size=size,
                url=url,
                file_type=file_type,
                mime_type=mime_type
            )
            
        except FileSizeExceeded:
            raise
        except Exception as e:
            logger.error(f"解析附件失败: {e}")
            return None
    
    def parse_mentions(self, msg: Dict) -> List[Dict]:
        """
        解析@提及
        
        KOOK @提及格式:
        {
            "mention": ["user_id_1", "user_id_2"],
            "mention_all": false,
            "mention_roles": ["role_id_1"],
            "mention_here": false
        }
        
        Returns:
            [
                {"type": "user", "user_id": "xxx", "username": "xxx"},
                {"type": "role", "role_id": "xxx", "role_name": "xxx"},
                {"type": "all"},
                {"type": "here"}
            ]
        """
        mentions = []
        
        # @用户
        mention_users = msg.get("mention", [])
        for user_id in mention_users:
            # 尝试从消息内容中提取用户名
            username = self._extract_username_from_mention(msg.get("content", ""), user_id)
            mentions.append({
                "type": "user",
                "user_id": user_id,
                "username": username or f"用户{user_id[:6]}"
            })
        
        # @角色
        mention_roles = msg.get("mention_roles", [])
        for role_id in mention_roles:
            mentions.append({
                "type": "role",
                "role_id": role_id,
                "role_name": f"角色{role_id[:6]}"
            })
        
        # @全体成员
        if msg.get("mention_all", False):
            mentions.append({"type": "all"})
        
        # @在线成员
        if msg.get("mention_here", False):
            mentions.append({"type": "here"})
        
        return mentions
    
    def _extract_username_from_mention(self, content: str, user_id: str) -> Optional[str]:
        """从消息内容中提取@用户名"""
        # KOOK @格式: @用户名 或 (met)user_id(met)
        pattern = f'\\(met\\){user_id}\\(met\\)@([^\\s]+)'
        match = re.search(pattern, content)
        return match.group(1) if match else None
    
    def parse_images(self, msg: Dict) -> List[str]:
        """
        解析图片URL列表
        
        支持多种格式:
        1. type=2 图片消息
        2. KMarkdown中的图片
        3. attachments中的图片
        
        Returns:
            图片URL列表
        """
        images = []
        
        # 方式1: 图片消息类型
        if msg.get("type") == 2:
            content = msg.get("content", "")
            if content.startswith("http"):
                images.append(content)
        
        # 方式2: KMarkdown图片语法 ![alt](url)
        content = msg.get("content", "")
        markdown_images = re.findall(r'!\[.*?\]\((https?://[^\)]+)\)', content)
        images.extend(markdown_images)
        
        # 方式3: attachments
        attachments = msg.get("attachments", {})
        if attachments and attachments.get("type") == "image":
            url = attachments.get("url")
            if url:
                images.append(url)
        
        return list(set(images))  # 去重
    
    async def parse_complete_message(self, msg: Dict) -> Dict[str, Any]:
        """
        完整解析消息（一次性解析所有内容）
        
        Returns:
            {
                "message_id": "...",
                "type": "text/image/file/...",
                "content": "原始内容",
                "author": {...},
                "reactions": [ReactionMessage, ...],
                "quote": QuoteMessage or None,
                "link_preview": LinkPreview or None,
                "attachment": Attachment or None,
                "images": ["url1", "url2"],
                "mentions": [{...}, ...],
                "timestamp": 1234567890,
                "channel_id": "...",
                "guild_id": "..."
            }
        """
        result = {
            "message_id": msg.get("msg_id", ""),
            "type": self.parse_message_type(msg),
            "content": msg.get("content", ""),
            "author": msg.get("author", {}),
            "timestamp": msg.get("msg_timestamp", 0),
            "channel_id": msg.get("target_id", ""),
            "guild_id": msg.get("guild_id", ""),
        }
        
        # 解析表情反应
        result["reactions"] = self.parse_reactions(msg)
        
        # 解析回复引用
        result["quote"] = self.parse_quote(msg)
        
        # 解析图片
        result["images"] = self.parse_images(msg)
        
        # 解析@提及
        result["mentions"] = self.parse_mentions(msg)
        
        # 解析附件
        try:
            result["attachment"] = self.parse_attachment(msg)
        except FileSizeExceeded as e:
            logger.warning(str(e))
            result["attachment"] = None
            result["attachment_error"] = str(e)
        
        # 解析链接预览（异步，可能较慢）
        links = re.findall(r'https?://\S+', result["content"])
        if links:
            # 只解析第一个链接
            result["link_preview"] = await self.parse_link_preview(links[0])
        else:
            result["link_preview"] = None
        
        return result


# 全局实例
message_parser = KookMessageParser()
