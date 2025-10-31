"""
钉钉转发模块
支持钉钉群机器人Webhook
"""
import aiohttp
import asyncio
import hmac
import hashlib
import base64
import time
from urllib.parse import quote_plus
from typing import Dict, Any, Optional, List
from ..utils.rate_limiter import rate_limiter_manager
from ..utils.logger import logger
from ..config import settings
from ..processors.formatter import formatter


class DingTalkForwarder:
    """钉钉消息转发器"""
    
    def __init__(self):
        # 钉钉限流：20请求/分钟
        self.rate_limiter = rate_limiter_manager.get_limiter(
            "dingtalk",
            calls=20,
            period=60
        )
    
    def _generate_sign(self, secret: str) -> tuple[str, str]:
        """
        生成钉钉签名
        
        Args:
            secret: 机器人密钥
            
        Returns:
            (timestamp, sign)
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = quote_plus(base64.b64encode(hmac_code))
        
        return timestamp, sign
    
    async def send_message(self, webhook_url: str, content: str,
                          secret: Optional[str] = None,
                          at_mobiles: Optional[List[str]] = None,
                          at_all: bool = False) -> bool:
        """
        发送文本消息到钉钉
        
        Args:
            webhook_url: 钉钉群机器人Webhook URL
            content: 消息内容
            secret: 机器人密钥（用于签名）
            at_mobiles: @用户手机号列表
            at_all: 是否@所有人
            
        Returns:
            是否成功
        """
        try:
            # 应用限流
            await self.rate_limiter.acquire()
            
            # 钉钉单条消息最多20000字符
            max_length = 20000
            
            if len(content) > max_length:
                # 超长消息需要分段
                logger.warning(f"钉钉消息超长({len(content)}字符)，自动分段")
                segments = formatter.split_long_message(content, 19000)  # 留1000字符余量
                success = True
                
                for i, segment in enumerate(segments):
                    segment_success = await self._send_single_message(
                        webhook_url,
                        f"[{i+1}/{len(segments)}]\n{segment}",
                        secret,
                        at_mobiles if i == 0 else None,  # 仅第一段@用户
                        at_all if i == 0 else False
                    )
                    
                    if not segment_success:
                        success = False
                        logger.error(f"钉钉分段消息发送失败: {i+1}/{len(segments)}")
                        break
                    
                    if len(segments) > 1:
                        await asyncio.sleep(1)  # 分段间延迟
                
                return success
            else:
                return await self._send_single_message(
                    webhook_url,
                    content,
                    secret,
                    at_mobiles,
                    at_all
                )
                
        except Exception as e:
            logger.error(f"钉钉发送异常: {str(e)}")
            return False
    
    async def _send_single_message(self, webhook_url: str, content: str,
                                   secret: Optional[str] = None,
                                   at_mobiles: Optional[List[str]] = None,
                                   at_all: bool = False) -> bool:
        """发送单条消息"""
        try:
            # 如果有密钥，生成签名
            url = webhook_url
            if secret:
                timestamp, sign = self._generate_sign(secret)
                url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
            
            # 构建消息体
            message = {
                "msgtype": "text",
                "text": {
                    "content": content
                },
                "at": {
                    "atMobiles": at_mobiles or [],
                    "isAtAll": at_all
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=message) as response:
                    data = await response.json()
                    
                    if data.get('errcode') == 0:
                        logger.info("钉钉消息发送成功")
                        return True
                    else:
                        logger.error(f"钉钉发送失败: {data.get('errmsg')}")
                        return False
                        
        except Exception as e:
            logger.error(f"钉钉发送异常: {str(e)}")
            return False
    
    async def send_markdown(self, webhook_url: str, title: str, text: str,
                           secret: Optional[str] = None,
                           at_mobiles: Optional[List[str]] = None,
                           at_all: bool = False) -> bool:
        """
        发送Markdown消息到钉钉
        
        Args:
            webhook_url: Webhook URL
            title: 标题
            text: Markdown文本
            secret: 机器人密钥
            at_mobiles: @用户手机号列表
            at_all: 是否@所有人
            
        Returns:
            是否成功
        """
        try:
            await self.rate_limiter.acquire()
            
            # 如果有密钥，生成签名
            url = webhook_url
            if secret:
                timestamp, sign = self._generate_sign(secret)
                url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
            
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": text
                },
                "at": {
                    "atMobiles": at_mobiles or [],
                    "isAtAll": at_all
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=message) as response:
                    data = await response.json()
                    
                    if data.get('errcode') == 0:
                        logger.info("钉钉Markdown消息发送成功")
                        return True
                    else:
                        logger.error(f"钉钉Markdown发送失败: {data.get('errmsg')}")
                        return False
                        
        except Exception as e:
            logger.error(f"钉钉Markdown发送异常: {str(e)}")
            return False
    
    async def send_link(self, webhook_url: str, title: str, text: str,
                       message_url: str, pic_url: Optional[str] = None,
                       secret: Optional[str] = None) -> bool:
        """
        发送链接消息到钉钉
        
        Args:
            webhook_url: Webhook URL
            title: 标题
            text: 文本
            message_url: 点击消息跳转的URL
            pic_url: 图片URL
            secret: 机器人密钥
            
        Returns:
            是否成功
        """
        try:
            await self.rate_limiter.acquire()
            
            # 如果有密钥，生成签名
            url = webhook_url
            if secret:
                timestamp, sign = self._generate_sign(secret)
                url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
            
            message = {
                "msgtype": "link",
                "link": {
                    "title": title,
                    "text": text,
                    "messageUrl": message_url,
                    "picUrl": pic_url or ""
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=message) as response:
                    data = await response.json()
                    
                    if data.get('errcode') == 0:
                        logger.info("钉钉链接消息发送成功")
                        return True
                    else:
                        logger.error(f"钉钉链接发送失败: {data.get('errmsg')}")
                        return False
                        
        except Exception as e:
            logger.error(f"钉钉链接发送异常: {str(e)}")
            return False
    
    async def test_webhook(self, webhook_url: str, secret: Optional[str] = None) -> tuple[bool, str]:
        """
        测试Webhook连接
        
        Args:
            webhook_url: Webhook URL
            secret: 机器人密钥
            
        Returns:
            (是否成功, 消息)
        """
        try:
            success = await self.send_message(
                webhook_url,
                "✅ KOOK消息转发系统测试消息\n\n如果您看到这条消息，说明钉钉配置成功！",
                secret
            )
            
            if success:
                return True, "测试成功！"
            else:
                return False, "测试失败，请检查配置"
                
        except asyncio.TimeoutError:
            return False, "测试失败: 连接超时"
        except Exception as e:
            return False, f"测试失败: {str(e)}"


# 创建全局实例
dingtalk_forwarder = DingTalkForwarder()
