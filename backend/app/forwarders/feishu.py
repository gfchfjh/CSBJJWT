"""
飞书转发模块
"""
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from ..utils.rate_limiter import rate_limiter_manager
from ..utils.logger import logger
from ..config import settings
from ..processors.formatter import formatter


class FeishuForwarder:
    """飞书消息转发器"""
    
    def __init__(self):
        self.rate_limiter = rate_limiter_manager.get_limiter(
            "feishu",
            settings.feishu_rate_limit_calls,
            settings.feishu_rate_limit_period
        )
        self.access_tokens = {}  # 缓存access_token
    
    async def get_access_token(self, app_id: str, app_secret: str) -> Optional[str]:
        """
        获取飞书访问令牌
        
        Args:
            app_id: App ID
            app_secret: App Secret
            
        Returns:
            访问令牌
        """
        # 检查缓存
        cache_key = f"{app_id}:{app_secret}"
        if cache_key in self.access_tokens:
            return self.access_tokens[cache_key]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                    json={
                        "app_id": app_id,
                        "app_secret": app_secret
                    }
                ) as response:
                    data = await response.json()
                    
                    if data.get("code") == 0:
                        token = data.get("tenant_access_token")
                        self.access_tokens[cache_key] = token
                        return token
                    else:
                        logger.error(f"获取飞书令牌失败: {data}")
                        return None
                        
        except Exception as e:
            logger.error(f"获取飞书令牌异常: {str(e)}")
            return None
    
    async def send_message(self, app_id: str, app_secret: str, 
                          chat_id: str, content: str,
                          msg_type: str = "text") -> bool:
        """
        发送消息到飞书
        
        Args:
            app_id: App ID
            app_secret: App Secret
            chat_id: 群聊ID
            content: 消息内容
            msg_type: 消息类型（text/post）
            
        Returns:
            是否成功
        """
        try:
            # 应用限流
            await self.rate_limiter.acquire()
            
            # 获取访问令牌
            access_token = await self.get_access_token(app_id, app_secret)
            if not access_token:
                return False
            
            # 构建消息体
            if msg_type == "text":
                message = {
                    "msg_type": "text",
                    "content": {
                        "text": content
                    }
                }
            else:
                # 富文本格式
                message = {
                    "msg_type": "post",
                    "content": {
                        "post": {
                            "zh_cn": {
                                "title": "KOOK消息",
                                "content": [[{"tag": "text", "text": content}]]
                            }
                        }
                    }
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://open.feishu.cn/open-apis/im/v1/messages",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "receive_id": chat_id,
                        "receive_id_type": "chat_id",
                        **message
                    }
                ) as response:
                    data = await response.json()
                    
                    if data.get("code") == 0:
                        logger.info("飞书消息发送成功")
                        return True
                    else:
                        logger.error(f"飞书消息发送失败: {data}")
                        return False
                        
        except Exception as e:
            logger.error(f"飞书发送异常: {str(e)}")
            return False
    
    async def send_card(self, app_id: str, app_secret: str,
                       chat_id: str, card_content: Dict[str, Any]) -> bool:
        """
        发送消息卡片到飞书
        
        Args:
            app_id: App ID
            app_secret: App Secret
            chat_id: 群聊ID
            card_content: 卡片内容
            
        Returns:
            是否成功
        """
        try:
            await self.rate_limiter.acquire()
            
            access_token = await self.get_access_token(app_id, app_secret)
            if not access_token:
                return False
            
            message = {
                "msg_type": "interactive",
                "content": card_content
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://open.feishu.cn/open-apis/im/v1/messages",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "receive_id": chat_id,
                        "receive_id_type": "chat_id",
                        **message
                    }
                ) as response:
                    data = await response.json()
                    
                    if data.get("code") == 0:
                        logger.info("飞书卡片发送成功")
                        return True
                    else:
                        logger.error(f"飞书卡片发送失败: {data}")
                        return False
                        
        except Exception as e:
            logger.error(f"飞书卡片发送异常: {str(e)}")
            return False
    
    async def test_connection(self, app_id: str, app_secret: str, 
                             chat_id: str) -> tuple[bool, str]:
        """
        测试连接
        
        Args:
            app_id: App ID
            app_secret: App Secret
            chat_id: 群聊ID
            
        Returns:
            (是否成功, 消息)
        """
        try:
            # 测试获取令牌
            access_token = await self.get_access_token(app_id, app_secret)
            if not access_token:
                return False, "获取访问令牌失败，请检查App ID和App Secret"
            
            # 发送测试消息
            success = await self.send_message(
                app_id, app_secret, chat_id,
                "✅ KOOK消息转发系统测试消息\n\n如果您看到这条消息，说明飞书配置成功！"
            )
            
            if success:
                return True, "测试成功！"
            else:
                return False, "发送测试消息失败，请检查群聊ID"
                
        except Exception as e:
            return False, f"测试失败: {str(e)}"


# 创建全局实例
feishu_forwarder = FeishuForwarder()
