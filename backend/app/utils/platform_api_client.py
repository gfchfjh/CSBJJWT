"""
目标平台API客户端
用于智能映射时获取真实的频道列表
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from ..utils.logger import logger
from ..config import settings


class DiscordAPIClient:
    """Discord API客户端"""
    
    def __init__(self):
        self.base_url = "https://discord.com/api/v10"
    
    async def get_channels_from_webhook(self, webhook_url: str) -> List[Dict[str, Any]]:
        """
        从Webhook URL获取频道信息
        
        Discord Webhook URL格式：
        https://discord.com/api/webhooks/{server_id}/{webhook_id}/{webhook_token}
        
        Args:
            webhook_url: Webhook URL
            
        Returns:
            频道信息列表 [{'id': str, 'name': str, 'type': str}]
        """
        try:
            logger.info(f"正在获取Discord频道信息: {webhook_url[:50]}...")
            
            # 验证URL格式
            if not webhook_url or 'discord.com/api/webhooks' not in webhook_url:
                logger.error("无效的Discord Webhook URL")
                return []
            
            async with aiohttp.ClientSession() as session:
                async with session.get(webhook_url) as response:
                    if response.status == 200:
                        webhook_data = await response.json()
                        
                        # 提取频道信息
                        channel_info = {
                            'id': webhook_data.get('channel_id', ''),
                            'name': webhook_data.get('name', 'Unknown Channel'),
                            'type': 'webhook',
                            'guild_id': webhook_data.get('guild_id', ''),
                            'guild_name': webhook_data.get('guild_name', '')
                        }
                        
                        logger.info(f"✅ 获取到Discord频道: {channel_info['name']}")
                        return [channel_info]
                    
                    elif response.status == 404:
                        logger.error("Discord Webhook不存在或已删除")
                        return []
                    
                    elif response.status == 401:
                        logger.error("Discord Webhook权限不足")
                        return []
                    
                    else:
                        logger.error(f"获取Discord频道失败: HTTP {response.status}")
                        return []
                        
        except asyncio.TimeoutError:
            logger.error("获取Discord频道超时")
            return []
        except Exception as e:
            logger.error(f"获取Discord频道异常: {str(e)}")
            return []
    
    async def get_guild_channels(self, guild_id: str, bot_token: str) -> List[Dict[str, Any]]:
        """
        获取服务器的所有频道（需要Bot Token）
        
        Args:
            guild_id: 服务器ID
            bot_token: Bot Token
            
        Returns:
            频道列表
        """
        try:
            headers = {
                'Authorization': f'Bot {bot_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/guilds/{guild_id}/channels"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        channels_data = await response.json()
                        
                        # 过滤文本频道
                        text_channels = [
                            {
                                'id': ch['id'],
                                'name': ch['name'],
                                'type': 'text_channel',
                                'position': ch.get('position', 0)
                            }
                            for ch in channels_data
                            if ch.get('type') == 0  # 0 = GUILD_TEXT
                        ]
                        
                        logger.info(f"✅ 获取到{len(text_channels)}个Discord文本频道")
                        return text_channels
                    else:
                        logger.error(f"获取Discord频道列表失败: HTTP {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"获取Discord频道列表异常: {str(e)}")
            return []


class TelegramAPIClient:
    """Telegram API客户端"""
    
    def __init__(self):
        self.base_url = "https://api.telegram.org"
    
    async def get_bot_chats(self, bot_token: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取Bot可访问的群组列表
        
        注意：Telegram Bot无法主动列出所有群组，
        只能从最近的更新记录中提取已添加的群组
        
        Args:
            bot_token: Bot Token
            limit: 获取最近N条更新
            
        Returns:
            群组列表 [{'id': str, 'name': str, 'type': str}]
        """
        try:
            logger.info("正在获取Telegram群组列表...")
            
            if not bot_token:
                logger.error("Telegram Bot Token为空")
                return []
            
            api_url = f"{self.base_url}/bot{bot_token}/getUpdates"
            params = {'limit': limit, 'offset': -limit}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if not data.get('ok'):
                            logger.error(f"Telegram API返回错误: {data.get('description')}")
                            return []
                        
                        # 从更新中提取群组信息
                        chats = {}  # 使用字典去重
                        
                        for update in data.get('result', []):
                            # 从消息中提取
                            if 'message' in update:
                                chat = update['message'].get('chat')
                                if chat and chat.get('type') in ['group', 'supergroup']:
                                    chat_id = str(chat.get('id'))
                                    if chat_id not in chats:
                                        chats[chat_id] = {
                                            'id': chat_id,
                                            'name': chat.get('title', 'Unknown Group'),
                                            'type': chat.get('type'),
                                            'username': chat.get('username', '')
                                        }
                            
                            # 从my_chat_member事件中提取
                            elif 'my_chat_member' in update:
                                chat = update['my_chat_member'].get('chat')
                                if chat and chat.get('type') in ['group', 'supergroup']:
                                    chat_id = str(chat.get('id'))
                                    if chat_id not in chats:
                                        chats[chat_id] = {
                                            'id': chat_id,
                                            'name': chat.get('title', 'Unknown Group'),
                                            'type': chat.get('type'),
                                            'username': chat.get('username', '')
                                        }
                        
                        result = list(chats.values())
                        logger.info(f"✅ 获取到{len(result)}个Telegram群组")
                        
                        if len(result) == 0:
                            logger.warning("提示：Bot需要先被添加到群组，并至少收到一条消息")
                        
                        return result
                    
                    elif response.status == 401:
                        logger.error("Telegram Bot Token无效")
                        return []
                    
                    else:
                        logger.error(f"获取Telegram群组失败: HTTP {response.status}")
                        return []
                        
        except asyncio.TimeoutError:
            logger.error("获取Telegram群组超时")
            return []
        except Exception as e:
            logger.error(f"获取Telegram群组异常: {str(e)}")
            return []
    
    async def get_chat_info(self, bot_token: str, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定群组的信息
        
        Args:
            bot_token: Bot Token
            chat_id: 群组ID
            
        Returns:
            群组信息
        """
        try:
            api_url = f"{self.base_url}/bot{bot_token}/getChat"
            params = {'chat_id': chat_id}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('ok'):
                            chat = data.get('result', {})
                            return {
                                'id': str(chat.get('id')),
                                'name': chat.get('title', 'Unknown'),
                                'type': chat.get('type'),
                                'username': chat.get('username', '')
                            }
                    
                    return None
                    
        except Exception as e:
            logger.error(f"获取Telegram群组信息异常: {str(e)}")
            return None


class FeishuAPIClient:
    """飞书API客户端"""
    
    def __init__(self):
        self.base_url = "https://open.feishu.cn/open-apis"
        self._access_token_cache = {}  # 缓存access_token
    
    async def _get_access_token(self, app_id: str, app_secret: str) -> Optional[str]:
        """
        获取tenant_access_token（带缓存）
        
        Args:
            app_id: 应用ID
            app_secret: 应用Secret
            
        Returns:
            access_token或None
        """
        try:
            # 检查缓存
            cache_key = f"{app_id}:{app_secret}"
            if cache_key in self._access_token_cache:
                token_data = self._access_token_cache[cache_key]
                # 简单的过期检查（实际应该更严格）
                if token_data.get('expires_at', 0) > asyncio.get_event_loop().time():
                    return token_data['token']
            
            # 获取新token
            token_url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            token_payload = {
                "app_id": app_id,
                "app_secret": app_secret
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, json=token_payload) as response:
                    if response.status == 200:
                        token_resp = await response.json()
                        
                        if token_resp.get('code') == 0:
                            access_token = token_resp.get('tenant_access_token')
                            expire = token_resp.get('expire', 7200)
                            
                            # 缓存token（提前5分钟过期）
                            self._access_token_cache[cache_key] = {
                                'token': access_token,
                                'expires_at': asyncio.get_event_loop().time() + expire - 300
                            }
                            
                            return access_token
                        else:
                            logger.error(f"获取飞书token失败: {token_resp.get('msg')}")
                            return None
                    else:
                        logger.error(f"获取飞书token失败: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"获取飞书token异常: {str(e)}")
            return None
    
    async def get_group_chats(self, app_id: str, app_secret: str) -> List[Dict[str, Any]]:
        """
        获取飞书群组列表
        
        Args:
            app_id: 应用ID
            app_secret: 应用Secret
            
        Returns:
            群组列表 [{'id': str, 'name': str, 'type': str}]
        """
        try:
            logger.info("正在获取飞书群组列表...")
            
            if not app_id or not app_secret:
                logger.error("飞书App ID或Secret为空")
                return []
            
            # 获取access_token
            access_token = await self._get_access_token(app_id, app_secret)
            if not access_token:
                return []
            
            # 获取群组列表
            chat_url = f"{self.base_url}/im/v1/chats"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            params = {
                "page_size": 100  # 每页100个
            }
            
            all_chats = []
            page_token = None
            
            async with aiohttp.ClientSession() as session:
                while True:
                    if page_token:
                        params['page_token'] = page_token
                    
                    async with session.get(chat_url, headers=headers, params=params) as response:
                        if response.status == 200:
                            chat_data = await response.json()
                            
                            if chat_data.get('code') == 0:
                                items = chat_data.get('data', {}).get('items', [])
                                
                                for item in items:
                                    # 只获取群组类型的聊天
                                    if item.get('chat_mode') == 'group':
                                        all_chats.append({
                                            'id': item.get('chat_id'),
                                            'name': item.get('name', 'Unknown Group'),
                                            'type': 'group',
                                            'description': item.get('description', '')
                                        })
                                
                                # 检查是否有下一页
                                page_token = chat_data.get('data', {}).get('page_token')
                                if not page_token:
                                    break
                            else:
                                logger.error(f"获取飞书群组失败: {chat_data.get('msg')}")
                                break
                        else:
                            logger.error(f"获取飞书群组失败: HTTP {response.status}")
                            break
                
                logger.info(f"✅ 获取到{len(all_chats)}个飞书群组")
                return all_chats
                
        except Exception as e:
            logger.error(f"获取飞书群组异常: {str(e)}")
            return []
    
    async def get_chat_info(self, app_id: str, app_secret: str, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定群组的信息
        
        Args:
            app_id: 应用ID
            app_secret: 应用Secret
            chat_id: 群组ID
            
        Returns:
            群组信息
        """
        try:
            access_token = await self._get_access_token(app_id, app_secret)
            if not access_token:
                return None
            
            chat_url = f"{self.base_url}/im/v1/chats/{chat_id}"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(chat_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('code') == 0:
                            chat = data.get('data', {})
                            return {
                                'id': chat.get('chat_id'),
                                'name': chat.get('name', 'Unknown'),
                                'type': 'group',
                                'description': chat.get('description', '')
                            }
                    
                    return None
                    
        except Exception as e:
            logger.error(f"获取飞书群组信息异常: {str(e)}")
            return None


# 全局实例
discord_api_client = DiscordAPIClient()
telegram_api_client = TelegramAPIClient()
feishu_api_client = FeishuAPIClient()
