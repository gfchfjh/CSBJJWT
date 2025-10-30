"""
消息转发器 - 增强版
✅ P0-9: 转发逻辑增强
✅ Discord伪装原始发送者
✅ 错误处理和重试机制
✅ 限流保护
✅ 多平台统一接口
"""
import aiohttp
import asyncio
from typing import Dict, Optional, Tuple
from abc import ABC, abstractmethod
from ..utils.logger import logger
from ..utils.rate_limiter import RateLimiter


class ForwarderBase(ABC):
    """转发器基类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.rate_limiter = self._init_rate_limiter()
        
        # 统计
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'rate_limited': 0
        }
    
    @abstractmethod
    def _init_rate_limiter(self) -> RateLimiter:
        """初始化限流器"""
        pass
    
    @abstractmethod
    async def send_message(
        self, 
        message: Dict,
        impersonate: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        发送消息
        
        Args:
            message: 标准化的消息
            impersonate: 是否伪装原始发送者
            
        Returns:
            (成功标志, 消息ID, 错误信息)
        """
        pass
    
    async def forward_with_retry(
        self,
        message: Dict,
        max_retries: int = 3,
        impersonate: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        转发消息（带重试）
        
        Args:
            message: 消息
            max_retries: 最大重试次数
            impersonate: 是否伪装
            
        Returns:
            (成功标志, 消息ID, 错误信息)
        """
        self.stats['total'] += 1
        
        for attempt in range(max_retries):
            try:
                # 等待限流
                await self.rate_limiter.acquire()
                
                # 发送消息
                success, msg_id, error = await self.send_message(message, impersonate)
                
                if success:
                    self.stats['success'] += 1
                    return True, msg_id, None
                
                # 失败，判断是否需要重试
                if self._should_retry(error):
                    wait_time = self._calculate_backoff(attempt)
                    logger.warning(
                        f"发送失败（第{attempt + 1}次），{wait_time}秒后重试: {error}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # 不可重试的错误
                    logger.error(f"发送失败（不可重试）: {error}")
                    self.stats['failed'] += 1
                    return False, None, error
                    
            except Exception as e:
                logger.error(f"转发异常: {str(e)}")
                
                if attempt < max_retries - 1:
                    wait_time = self._calculate_backoff(attempt)
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    self.stats['failed'] += 1
                    return False, None, str(e)
        
        # 重试次数耗尽
        self.stats['failed'] += 1
        return False, None, f"重试{max_retries}次后仍失败"
    
    def _should_retry(self, error: Optional[str]) -> bool:
        """判断错误是否可重试"""
        if not error:
            return False
        
        # 可重试的错误类型
        retryable_errors = [
            'timeout',
            'connection',
            'rate limit',
            '429',
            'too many requests',
            'temporary',
            'server error',
            '500',
            '502',
            '503',
            '504'
        ]
        
        error_lower = error.lower()
        
        for retryable in retryable_errors:
            if retryable in error_lower:
                return True
        
        return False
    
    def _calculate_backoff(self, attempt: int) -> float:
        """计算指数退避时间"""
        base_wait = 2  # 基础等待时间（秒）
        return base_wait * (2 ** attempt)  # 2, 4, 8, 16...
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        success_rate = 0
        if self.stats['total'] > 0:
            success_rate = self.stats['success'] / self.stats['total'] * 100
        
        return {
            **self.stats,
            'success_rate': f"{success_rate:.1f}%"
        }


class DiscordForwarderEnhanced(ForwarderBase):
    """Discord转发器 - 增强版"""
    
    def _init_rate_limiter(self) -> RateLimiter:
        # Discord限制：每5秒5条消息
        return RateLimiter(calls=5, period=5)
    
    async def send_message(
        self, 
        message: Dict,
        impersonate: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        发送消息到Discord
        
        Args:
            message: 标准化消息
            impersonate: 是否伪装原始发送者（使用username和avatar_url）
        """
        try:
            webhook_url = self.config.get('webhook_url')
            
            if not webhook_url:
                return False, None, "未配置Webhook URL"
            
            # 构建Discord消息
            payload = self._build_discord_payload(message, impersonate)
            
            # 发送
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 204:
                        # Discord Webhook成功返回204
                        return True, None, None
                    elif response.status == 429:
                        # 速率限制
                        retry_after = (await response.json()).get('retry_after', 1)
                        self.stats['rate_limited'] += 1
                        return False, None, f"Rate limited, retry after {retry_after}s"
                    else:
                        error_text = await response.text()
                        return False, None, f"HTTP {response.status}: {error_text}"
                        
        except Exception as e:
            return False, None, str(e)
    
    def _build_discord_payload(self, message: Dict, impersonate: bool) -> Dict:
        """构建Discord消息载荷"""
        payload = {}
        
        if impersonate:
            # 伪装原始发送者
            author = message.get('author', {})
            payload['username'] = author.get('nickname', author.get('username', '未知用户'))
            payload['avatar_url'] = author.get('avatar', '')
        
        # 文本内容
        content = message.get('content', '')
        
        # 处理@提及
        for mention in message.get('mentions', []):
            if mention['type'] == 'everyone':
                content += '\n@everyone'
            # Discord的@需要实际的用户ID，这里简化处理
        
        # 处理引用
        quote = message.get('quote', None)
        if quote:
            quote_text = f"> {quote.get('content', '')}\n"
            content = quote_text + content
        
        payload['content'] = content
        
        # 附件
        embeds = []
        for attachment in message.get('attachments', []):
            if attachment['type'] == 'image':
                embed = {
                    'image': {
                        'url': attachment['url']
                    }
                }
                embeds.append(embed)
        
        if embeds:
            payload['embeds'] = embeds
        
        # 卡片消息转换为Embed
        for embed_data in message.get('embeds', []):
            embed = self._convert_card_to_embed(embed_data)
            if embed:
                embeds.append(embed)
        
        if embeds:
            payload['embeds'] = embeds
        
        return payload
    
    def _convert_card_to_embed(self, card: Dict) -> Optional[Dict]:
        """将KOOK卡片转换为Discord Embed"""
        embed = {
            'color': self._get_theme_color(card.get('theme', 'primary'))
        }
        
        for module in card.get('modules', []):
            module_type = module.get('type')
            
            if module_type == 'header':
                embed['title'] = module.get('text', '')
            
            elif module_type == 'section':
                if 'description' not in embed:
                    embed['description'] = ''
                embed['description'] += module.get('text', '') + '\n'
        
        return embed if embed.get('title') or embed.get('description') else None
    
    def _get_theme_color(self, theme: str) -> int:
        """获取主题颜色"""
        colors = {
            'primary': 0x3498db,
            'success': 0x2ecc71,
            'warning': 0xf39c12,
            'danger': 0xe74c3c,
            'info': 0x9b59b6,
            'secondary': 0x95a5a6
        }
        return colors.get(theme, 0x3498db)


class TelegramForwarderEnhanced(ForwarderBase):
    """Telegram转发器 - 增强版"""
    
    def _init_rate_limiter(self) -> RateLimiter:
        # Telegram限制：每秒30条消息
        return RateLimiter(calls=30, period=1)
    
    async def send_message(
        self, 
        message: Dict,
        impersonate: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """发送消息到Telegram"""
        try:
            bot_token = self.config.get('bot_token')
            chat_id = self.config.get('chat_id')
            
            if not bot_token or not chat_id:
                return False, None, "未配置Bot Token或Chat ID"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # 构建消息
            payload = self._build_telegram_payload(message, impersonate)
            payload['chat_id'] = chat_id
            
            # 发送
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=30) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        message_id = result.get('result', {}).get('message_id')
                        return True, str(message_id), None
                    else:
                        error = result.get('description', 'Unknown error')
                        return False, None, error
                        
        except Exception as e:
            return False, None, str(e)
    
    def _build_telegram_payload(self, message: Dict, impersonate: bool) -> Dict:
        """构建Telegram消息载荷"""
        # Telegram HTML格式
        text = message.get('content', '')
        
        # 伪装发送者（在消息前加发送者信息）
        if impersonate:
            author = message.get('author', {})
            username = author.get('nickname', author.get('username', '未知用户'))
            text = f"<b>{username}</b>:\n{text}"
        
        # 处理引用
        quote = message.get('quote', None)
        if quote:
            quote_author = quote.get('author', {}).get('username', '未知用户')
            quote_content = quote.get('content', '')
            text = f"<i>回复 {quote_author}: {quote_content}</i>\n\n{text}"
        
        payload = {
            'text': text,
            'parse_mode': 'HTML'
        }
        
        return payload


class FeishuForwarderEnhanced(ForwarderBase):
    """飞书转发器 - 增强版"""
    
    def _init_rate_limiter(self) -> RateLimiter:
        # 飞书限制：每秒20条消息
        return RateLimiter(calls=20, period=1)
    
    async def send_message(
        self, 
        message: Dict,
        impersonate: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """发送消息到飞书"""
        try:
            webhook_url = self.config.get('webhook_url')
            
            if not webhook_url:
                return False, None, "未配置Webhook URL"
            
            # 构建飞书消息
            payload = self._build_feishu_payload(message, impersonate)
            
            # 发送
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=30
                ) as response:
                    result = await response.json()
                    
                    if result.get('code') == 0:
                        return True, None, None
                    else:
                        error = result.get('msg', 'Unknown error')
                        return False, None, error
                        
        except Exception as e:
            return False, None, str(e)
    
    def _build_feishu_payload(self, message: Dict, impersonate: bool) -> Dict:
        """构建飞书消息载荷"""
        content = message.get('content', '')
        
        if impersonate:
            author = message.get('author', {})
            username = author.get('nickname', author.get('username', '未知用户'))
            content = f"**{username}**:\n{content}"
        
        payload = {
            'msg_type': 'text',
            'content': {
                'text': content
            }
        }
        
        return payload


# 工厂函数
def create_forwarder(platform: str, config: Dict) -> ForwarderBase:
    """创建转发器实例"""
    forwarders = {
        'discord': DiscordForwarderEnhanced,
        'telegram': TelegramForwarderEnhanced,
        'feishu': FeishuForwarderEnhanced
    }
    
    forwarder_class = forwarders.get(platform)
    
    if not forwarder_class:
        raise ValueError(f"不支持的平台: {platform}")
    
    return forwarder_class(config)
