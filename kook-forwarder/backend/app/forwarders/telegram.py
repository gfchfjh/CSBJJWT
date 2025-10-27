"""
Telegram转发模块
"""
import asyncio
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from ..utils.rate_limiter import rate_limiter_manager
from ..utils.logger import logger
from ..config import settings
from ..processors.formatter import formatter


class TelegramForwarder:
    """Telegram消息转发器"""
    
    def __init__(self):
        self.rate_limiter = rate_limiter_manager.get_limiter(
            "telegram",
            settings.telegram_rate_limit_calls,
            settings.telegram_rate_limit_period
        )
        self.bots = {}  # 缓存Bot实例
    
    def get_bot(self, token: str) -> Bot:
        """获取Bot实例"""
        if token not in self.bots:
            self.bots[token] = Bot(token=token)
        return self.bots[token]
    
    async def send_message(self, token: str, chat_id: str, content: str,
                          parse_mode: str = "HTML") -> bool:
        """
        发送消息到Telegram
        
        Args:
            token: Bot Token
            chat_id: 聊天ID
            content: 消息内容
            parse_mode: 解析模式（HTML/Markdown）
            
        Returns:
            是否成功
        """
        try:
            # 应用限流
            await self.rate_limiter.acquire()
            
            bot = self.get_bot(token)
            
            # 转换为HTML格式
            if parse_mode == "HTML":
                content = formatter.kmarkdown_to_telegram_html(content)
            
            # Telegram单条消息最多4096字符
            messages = formatter.split_long_message(content, 4096)
            
            for msg in messages:
                await bot.send_message(
                    chat_id=chat_id,
                    text=msg,
                    parse_mode=parse_mode
                )
                
                # 如果有多条消息，稍微延迟一下
                if len(messages) > 1:
                    await asyncio.sleep(0.3)
            
            logger.info(f"Telegram消息发送成功: {len(messages)}条")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram发送失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Telegram发送异常: {str(e)}")
            return False
    
    async def send_photo(self, token: str, chat_id: str, photo_url: str,
                        caption: Optional[str] = None) -> bool:
        """
        发送图片到Telegram
        
        Args:
            token: Bot Token
            chat_id: 聊天ID
            photo_url: 图片URL或文件路径
            caption: 图片说明
            
        Returns:
            是否成功
        """
        try:
            await self.rate_limiter.acquire()
            
            bot = self.get_bot(token)
            
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption=caption
            )
            
            logger.info(f"Telegram图片发送成功")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram图片发送失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Telegram图片发送异常: {str(e)}")
            return False
    
    async def send_document(self, token: str, chat_id: str, document_path: str,
                           caption: Optional[str] = None) -> bool:
        """
        发送文件到Telegram
        
        Args:
            token: Bot Token
            chat_id: 聊天ID
            document_path: 文件路径
            caption: 文件说明
            
        Returns:
            是否成功
        """
        try:
            await self.rate_limiter.acquire()
            
            bot = self.get_bot(token)
            
            with open(document_path, 'rb') as f:
                await bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption=caption
                )
            
            logger.info(f"Telegram文件发送成功: {document_path}")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram文件发送失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Telegram文件发送异常: {str(e)}")
            return False
    
    async def test_bot(self, token: str, chat_id: str) -> tuple[bool, str]:
        """
        测试Bot连接
        
        Args:
            token: Bot Token
            chat_id: 聊天ID
            
        Returns:
            (是否成功, 消息)
        """
        try:
            bot = self.get_bot(token)
            
            # 获取Bot信息
            bot_info = await bot.get_me()
            
            # 发送测试消息
            await bot.send_message(
                chat_id=chat_id,
                text="✅ KOOK消息转发系统测试消息\n\n如果您看到这条消息，说明Bot配置成功！",
                parse_mode="HTML"
            )
            
            return True, f"测试成功！Bot名称: @{bot_info.username}"
            
        except TelegramError as e:
            return False, f"测试失败: {str(e)}"
        except Exception as e:
            return False, f"测试失败: {str(e)}"
    
    async def get_chat_ids(self, token: str) -> tuple[bool, list]:
        """
        获取可用的Chat ID列表
        
        通过getUpdates API获取最近与Bot交互的所有Chat ID
        
        Args:
            token: Bot Token
            
        Returns:
            (是否成功, Chat ID列表)
        """
        try:
            bot = self.get_bot(token)
            
            # 获取Bot信息（验证Token有效性）
            try:
                bot_info = await bot.get_me()
                logger.info(f"获取Chat ID - Bot: @{bot_info.username}")
            except TelegramError as e:
                return False, []
            
            # 获取最近的更新
            updates = await bot.get_updates(limit=100)
            
            if not updates:
                logger.warning("未找到任何更新，请先向Bot发送一条消息")
                return True, []
            
            # 提取所有唯一的Chat ID
            chat_ids = set()
            chat_info = []
            
            for update in updates:
                if update.message:
                    chat = update.message.chat
                    chat_id = str(chat.id)
                    
                    if chat_id not in [c['id'] for c in chat_info]:
                        info = {
                            'id': chat_id,
                            'type': chat.type,
                            'title': chat.title if chat.title else f"{chat.first_name or ''} {chat.last_name or ''}".strip(),
                            'username': chat.username
                        }
                        chat_info.append(info)
                        chat_ids.add(chat_id)
            
            logger.info(f"找到 {len(chat_ids)} 个Chat ID")
            return True, chat_info
            
        except TelegramError as e:
            logger.error(f"获取Chat ID失败: {str(e)}")
            return False, []
        except Exception as e:
            logger.error(f"获取Chat ID异常: {str(e)}")
            return False, []


# 创建全局实例
telegram_forwarder = TelegramForwarder()
