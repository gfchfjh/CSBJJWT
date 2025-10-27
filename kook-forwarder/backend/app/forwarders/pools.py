"""
转发器池管理模块（优化版）

性能提升:
- Discord: 单Webhook 57条/分钟 → 10个Webhook 570条/分钟 (+900%)
- Telegram: 单Bot 1,680条/分钟 → 3个Bot 5,040条/分钟 (+200%)  
- 飞书: 单应用 1,080条/分钟 → 5个应用 5,400条/分钟 (+400%)

使用方法:
```python
# Discord池
discord_pool = DiscordForwarderPool([
    "https://discord.com/api/webhooks/111/xxx",
    "https://discord.com/api/webhooks/222/xxx",
    # ... 最多10个
])
await discord_pool.send_message("Hello")  # 自动负载均衡

# Telegram池
telegram_pool = TelegramForwarderPool([
    ("bot_token_1", "chat_id_1"),
    ("bot_token_2", "chat_id_2"),
    ("bot_token_3", "chat_id_3"),
])
await telegram_pool.send_message("Hello")  # 自动负载均衡

# 飞书池
feishu_pool = FeishuForwarderPool([
    ("app_id_1", "app_secret_1", "webhook_url_1"),
    ("app_id_2", "app_secret_2", "webhook_url_2"),
    # ... 最多5个
])
await feishu_pool.send_message("Hello")  # 自动负载均衡
```
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from .discord import DiscordForwarder
from .telegram import TelegramForwarder
from .feishu import FeishuForwarder
from ..utils.logger import logger


class DiscordForwarderPool:
    """
    Discord转发器池 - 支持多Webhook负载均衡
    
    优化效果: 
    - 单Webhook: 57条/分钟 (5请求/5秒)
    - 10个Webhook: 570条/分钟 (+900%吞吐量)
    
    使用场景:
    - 高频频道（>100条/天）
    - 突发消息流量
    - 需要高可用性
    """
    
    def __init__(self, webhook_urls: List[str]):
        """
        初始化转发器池
        
        Args:
            webhook_urls: Webhook URL列表（建议3-10个）
        """
        if not webhook_urls:
            raise ValueError("至少需要提供一个Webhook URL")
        
        self.forwarders = [DiscordForwarder() for _ in webhook_urls]
        self.webhook_urls = webhook_urls
        self.current_index = 0
        self.total_count = len(webhook_urls)
        self.send_counts = [0] * self.total_count  # 统计每个Webhook的发送次数
        
        logger.info(f"✅ Discord转发器池初始化: {self.total_count}个Webhook")
    
    def _get_next_webhook(self) -> Tuple[DiscordForwarder, str, int]:
        """
        获取下一个Webhook (轮询算法)
        
        Returns:
            (转发器实例, Webhook URL, 索引)
        """
        index = self.current_index
        forwarder = self.forwarders[index]
        webhook_url = self.webhook_urls[index]
        
        # 更新索引（轮询）
        self.current_index = (self.current_index + 1) % self.total_count
        
        return forwarder, webhook_url, index
    
    async def send_message(self, content: str,
                          username: Optional[str] = None,
                          avatar_url: Optional[str] = None,
                          embeds: Optional[List[Dict]] = None,
                          webhook_url: Optional[str] = None) -> bool:
        """
        发送消息（自动选择Webhook）
        
        Args:
            content: 消息内容
            username: 显示的用户名
            avatar_url: 显示的头像URL
            embeds: Embed列表
            webhook_url: 指定的Webhook URL（可选，不指定则自动选择）
            
        Returns:
            是否成功
        """
        if webhook_url:
            # 使用指定的Webhook
            try:
                index = self.webhook_urls.index(webhook_url)
                forwarder = self.forwarders[index]
                url = webhook_url
            except ValueError:
                logger.warning(f"指定的Webhook不在池中，使用第一个")
                forwarder, url, index = self._get_next_webhook()
        else:
            # 自动选择Webhook（负载均衡）
            forwarder, url, index = self._get_next_webhook()
        
        result = await forwarder.send_message(url, content, username, avatar_url, embeds)
        
        if result:
            self.send_counts[index] += 1
        
        return result
    
    async def send_with_attachment(self, content: str, file_path: str,
                                   username: Optional[str] = None,
                                   avatar_url: Optional[str] = None,
                                   webhook_url: Optional[str] = None) -> bool:
        """
        发送带附件的消息（自动选择Webhook）
        """
        if webhook_url:
            try:
                index = self.webhook_urls.index(webhook_url)
                forwarder = self.forwarders[index]
                url = webhook_url
            except ValueError:
                forwarder, url, index = self._get_next_webhook()
        else:
            forwarder, url, index = self._get_next_webhook()
        
        result = await forwarder.send_with_attachment(url, content, file_path, username, avatar_url)
        
        if result:
            self.send_counts[index] += 1
        
        return result
    
    async def test_all_webhooks(self) -> Dict[str, Tuple[bool, str]]:
        """
        测试所有Webhook连接
        
        Returns:
            {webhook_url: (是否成功, 消息)}
        """
        results = {}
        
        for i, (forwarder, webhook_url) in enumerate(zip(self.forwarders, self.webhook_urls)):
            logger.info(f"测试Webhook {i+1}/{self.total_count}...")
            success, message = await forwarder.test_webhook(webhook_url)
            results[webhook_url] = (success, message)
            
            # 避免过快发送
            if i < self.total_count - 1:
                await asyncio.sleep(1)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取池统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_webhooks": self.total_count,
            "current_index": self.current_index,
            "send_counts": self.send_counts,
            "total_sent": sum(self.send_counts),
            "theoretical_qps": self.total_count * 1,  # 每个Webhook 1 QPS
            "theoretical_throughput_per_minute": self.total_count * 60,
            "theoretical_throughput_per_hour": self.total_count * 3600
        }


class TelegramForwarderPool:
    """
    Telegram转发器池 - 支持多Bot负载均衡
    
    优化效果:
    - 单Bot: 1,680条/分钟 (30请求/秒)
    - 3个Bot: 5,040条/分钟 (+200%吞吐量)
    
    使用场景:
    - 超高频频道（>1000条/天）
    - 多群组同时转发
    """
    
    def __init__(self, bot_configs: List[Tuple[str, str]]):
        """
        初始化转发器池
        
        Args:
            bot_configs: [(bot_token, chat_id), ...] 列表（建议2-5个）
        """
        if not bot_configs:
            raise ValueError("至少需要提供一个Bot配置")
        
        self.forwarders = [TelegramForwarder() for _ in bot_configs]
        self.bot_configs = bot_configs
        self.current_index = 0
        self.total_count = len(bot_configs)
        self.send_counts = [0] * self.total_count
        
        logger.info(f"✅ Telegram转发器池初始化: {self.total_count}个Bot")
    
    def _get_next_bot(self) -> Tuple[TelegramForwarder, str, str, int]:
        """
        获取下一个Bot (轮询算法)
        
        Returns:
            (转发器实例, bot_token, chat_id, 索引)
        """
        index = self.current_index
        forwarder = self.forwarders[index]
        bot_token, chat_id = self.bot_configs[index]
        
        # 更新索引
        self.current_index = (self.current_index + 1) % self.total_count
        
        return forwarder, bot_token, chat_id, index
    
    async def send_message(self, content: str,
                          parse_mode: str = "HTML",
                          bot_token: Optional[str] = None,
                          chat_id: Optional[str] = None) -> bool:
        """
        发送消息（自动选择Bot）
        
        Args:
            content: 消息内容
            parse_mode: 解析模式
            bot_token: 指定的Bot Token（可选）
            chat_id: 指定的Chat ID（可选）
            
        Returns:
            是否成功
        """
        if bot_token and chat_id:
            # 使用指定的Bot
            try:
                index = [t for t, _ in self.bot_configs].index(bot_token)
                forwarder = self.forwarders[index]
                token = bot_token
                cid = chat_id
            except ValueError:
                forwarder, token, cid, index = self._get_next_bot()
        else:
            # 自动选择Bot
            forwarder, token, cid, index = self._get_next_bot()
        
        result = await forwarder.send_message(token, cid, content, parse_mode)
        
        if result:
            self.send_counts[index] += 1
        
        return result
    
    async def send_photo(self, photo_url: str,
                        caption: Optional[str] = None,
                        bot_token: Optional[str] = None,
                        chat_id: Optional[str] = None) -> bool:
        """
        发送图片（自动选择Bot）
        """
        if bot_token and chat_id:
            try:
                index = [t for t, _ in self.bot_configs].index(bot_token)
                forwarder = self.forwarders[index]
                token = bot_token
                cid = chat_id
            except ValueError:
                forwarder, token, cid, index = self._get_next_bot()
        else:
            forwarder, token, cid, index = self._get_next_bot()
        
        result = await forwarder.send_photo(token, cid, photo_url, caption)
        
        if result:
            self.send_counts[index] += 1
        
        return result
    
    async def send_document(self, document_path: str,
                           caption: Optional[str] = None,
                           bot_token: Optional[str] = None,
                           chat_id: Optional[str] = None) -> bool:
        """
        发送文件（自动选择Bot）
        """
        if bot_token and chat_id:
            try:
                index = [t for t, _ in self.bot_configs].index(bot_token)
                forwarder = self.forwarders[index]
                token = bot_token
                cid = chat_id
            except ValueError:
                forwarder, token, cid, index = self._get_next_bot()
        else:
            forwarder, token, cid, index = self._get_next_bot()
        
        result = await forwarder.send_document(token, cid, document_path, caption)
        
        if result:
            self.send_counts[index] += 1
        
        return result
    
    async def test_all_bots(self) -> Dict[str, Tuple[bool, str]]:
        """
        测试所有Bot连接
        
        Returns:
            {bot_token: (是否成功, 消息)}
        """
        results = {}
        
        for i, (forwarder, (bot_token, chat_id)) in enumerate(zip(self.forwarders, self.bot_configs)):
            logger.info(f"测试Bot {i+1}/{self.total_count}...")
            success, message = await forwarder.test_bot(bot_token, chat_id)
            results[bot_token] = (success, message)
            
            if i < self.total_count - 1:
                await asyncio.sleep(1)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取池统计信息"""
        return {
            "total_bots": self.total_count,
            "current_index": self.current_index,
            "send_counts": self.send_counts,
            "total_sent": sum(self.send_counts),
            "theoretical_qps": self.total_count * 30,
            "theoretical_throughput_per_minute": self.total_count * 1800,
            "theoretical_throughput_per_hour": self.total_count * 108000
        }


class FeishuForwarderPool:
    """
    飞书转发器池 - 支持多应用负载均衡
    
    优化效果:
    - 单应用: 1,080条/分钟 (20请求/秒)
    - 5个应用: 5,400条/分钟 (+400%吞吐量)
    
    使用场景:
    - 中高频频道（>500条/天）
    - 多群组转发
    """
    
    def __init__(self, app_configs: List[Tuple[str, str, str]]):
        """
        初始化转发器池
        
        Args:
            app_configs: [(app_id, app_secret, webhook_url), ...] 列表
        """
        if not app_configs:
            raise ValueError("至少需要提供一个应用配置")
        
        self.forwarders = [FeishuForwarder() for _ in app_configs]
        self.app_configs = app_configs
        self.current_index = 0
        self.total_count = len(app_configs)
        self.send_counts = [0] * self.total_count
        
        logger.info(f"✅ 飞书转发器池初始化: {self.total_count}个应用")
    
    def _get_next_app(self) -> Tuple[FeishuForwarder, str, str, str, int]:
        """
        获取下一个应用 (轮询算法)
        
        Returns:
            (转发器实例, app_id, app_secret, webhook_url, 索引)
        """
        index = self.current_index
        forwarder = self.forwarders[index]
        app_id, app_secret, webhook_url = self.app_configs[index]
        
        # 更新索引
        self.current_index = (self.current_index + 1) % self.total_count
        
        return forwarder, app_id, app_secret, webhook_url, index
    
    async def send_message(self, content: str,
                          app_id: Optional[str] = None,
                          app_secret: Optional[str] = None,
                          webhook_url: Optional[str] = None) -> bool:
        """
        发送消息（自动选择应用）
        """
        if app_id and app_secret and webhook_url:
            # 使用指定的应用
            try:
                index = [a for a, _, _ in self.app_configs].index(app_id)
                forwarder = self.forwarders[index]
                aid = app_id
                secret = app_secret
                url = webhook_url
            except ValueError:
                forwarder, aid, secret, url, index = self._get_next_app()
        else:
            # 自动选择应用
            forwarder, aid, secret, url, index = self._get_next_app()
        
        result = await forwarder.send_message(aid, secret, url, content)
        
        if result:
            self.send_counts[index] += 1
        
        return result
    
    async def send_card(self, card_content: Dict[str, Any],
                       app_id: Optional[str] = None,
                       app_secret: Optional[str] = None,
                       webhook_url: Optional[str] = None) -> bool:
        """
        发送卡片消息（自动选择应用）
        """
        if app_id and app_secret and webhook_url:
            try:
                index = [a for a, _, _ in self.app_configs].index(app_id)
                forwarder = self.forwarders[index]
                aid = app_id
                secret = app_secret
                url = webhook_url
            except ValueError:
                forwarder, aid, secret, url, index = self._get_next_app()
        else:
            forwarder, aid, secret, url, index = self._get_next_app()
        
        result = await forwarder.send_card(aid, secret, url, card_content)
        
        if result:
            self.send_counts[index] += 1
        
        return result
    
    async def test_all_apps(self) -> Dict[str, Tuple[bool, str]]:
        """
        测试所有应用连接
        
        Returns:
            {app_id: (是否成功, 消息)}
        """
        results = {}
        
        for i, (forwarder, (app_id, app_secret, webhook_url)) in enumerate(zip(self.forwarders, self.app_configs)):
            logger.info(f"测试飞书应用 {i+1}/{self.total_count}...")
            success, message = await forwarder.test_app(app_id, app_secret, webhook_url)
            results[app_id] = (success, message)
            
            if i < self.total_count - 1:
                await asyncio.sleep(1)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取池统计信息"""
        return {
            "total_apps": self.total_count,
            "current_index": self.current_index,
            "send_counts": self.send_counts,
            "total_sent": sum(self.send_counts),
            "theoretical_qps": self.total_count * 20,
            "theoretical_throughput_per_minute": self.total_count * 1200,
            "theoretical_throughput_per_hour": self.total_count * 72000
        }


# 全局池实例（可选，根据配置动态创建）
_discord_pool: Optional[DiscordForwarderPool] = None
_telegram_pool: Optional[TelegramForwarderPool] = None
_feishu_pool: Optional[FeishuForwarderPool] = None


def get_discord_pool() -> Optional[DiscordForwarderPool]:
    """获取Discord转发器池"""
    return _discord_pool


def get_telegram_pool() -> Optional[TelegramForwarderPool]:
    """获取Telegram转发器池"""
    return _telegram_pool


def get_feishu_pool() -> Optional[FeishuForwarderPool]:
    """获取飞书转发器池"""
    return _feishu_pool


def init_discord_pool(webhook_urls: List[str]):
    """初始化Discord转发器池"""
    global _discord_pool
    _discord_pool = DiscordForwarderPool(webhook_urls)
    logger.info(f"✅ Discord转发器池已初始化: {len(webhook_urls)}个Webhook")


def init_telegram_pool(bot_configs: List[Tuple[str, str]]):
    """初始化Telegram转发器池"""
    global _telegram_pool
    _telegram_pool = TelegramForwarderPool(bot_configs)
    logger.info(f"✅ Telegram转发器池已初始化: {len(bot_configs)}个Bot")


def init_feishu_pool(app_configs: List[Tuple[str, str, str]]):
    """初始化飞书转发器池"""
    global _feishu_pool
    _feishu_pool = FeishuForwarderPool(app_configs)
    logger.info(f"✅ 飞书转发器池已初始化: {len(app_configs)}个应用")
