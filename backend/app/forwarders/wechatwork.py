"""
企业微信转发模块
支持企业微信群机器人Webhook
"""
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from ..utils.rate_limiter import rate_limiter_manager
from ..utils.logger import logger
from ..config import settings
from ..processors.formatter import formatter


class WechatWorkForwarder:
    """企业微信消息转发器"""
    
    def __init__(self):
        # 企业微信限流：20请求/分钟
        self.rate_limiter = rate_limiter_manager.get_limiter(
            "wechatwork",
            calls=20,
            period=60
        )
    
    async def send_message(self, webhook_url: str, content: str,
                          mentioned_list: Optional[List[str]] = None,
                          mentioned_mobile_list: Optional[List[str]] = None) -> bool:
        """
        发送文本消息到企业微信
        
        Args:
            webhook_url: 企业微信群机器人Webhook URL
            content: 消息内容
            mentioned_list: @用户列表（userid）
            mentioned_mobile_list: @用户列表（手机号）
            
        Returns:
            是否成功
        """
        try:
            # 应用限流
            await self.rate_limiter.acquire()
            
            # 企业微信单条消息最多2048字节（约680个中文字符）
            max_length = 680
            
            if len(content) > max_length:
                # 超长消息需要分段
                logger.warning(f"企业微信消息超长({len(content)}字符)，自动分段")
                segments = formatter.split_long_message(content, max_length)
                success = True
                
                for i, segment in enumerate(segments):
                    segment_success = await self._send_single_message(
                        webhook_url,
                        f"[{i+1}/{len(segments)}]\n{segment}",
                        mentioned_list if i == 0 else None,  # 仅第一段@用户
                        mentioned_mobile_list if i == 0 else None
                    )
                    
                    if not segment_success:
                        success = False
                        logger.error(f"企业微信分段消息发送失败: {i+1}/{len(segments)}")
                        break
                    
                    if len(segments) > 1:
                        await asyncio.sleep(1)  # 分段间延迟
                
                return success
            else:
                return await self._send_single_message(
                    webhook_url,
                    content,
                    mentioned_list,
                    mentioned_mobile_list
                )
                
        except Exception as e:
            logger.error(f"企业微信发送异常: {str(e)}")
            return False
    
    async def _send_single_message(self, webhook_url: str, content: str,
                                   mentioned_list: Optional[List[str]] = None,
                                   mentioned_mobile_list: Optional[List[str]] = None) -> bool:
        """发送单条消息"""
        try:
            # 构建消息体
            message = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            # 添加@提及
            if mentioned_list or mentioned_mobile_list:
                message["text"]["mentioned_list"] = mentioned_list or []
                message["text"]["mentioned_mobile_list"] = mentioned_mobile_list or []
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    data = await response.json()
                    
                    if data.get('errcode') == 0:
                        logger.info("企业微信消息发送成功")
                        return True
                    else:
                        logger.error(f"企业微信发送失败: {data.get('errmsg')}")
                        return False
                        
        except Exception as e:
            logger.error(f"企业微信发送异常: {str(e)}")
            return False
    
    async def send_markdown(self, webhook_url: str, content: str) -> bool:
        """
        发送Markdown消息到企业微信
        
        Args:
            webhook_url: Webhook URL
            content: Markdown内容
            
        Returns:
            是否成功
        """
        try:
            await self.rate_limiter.acquire()
            
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    data = await response.json()
                    
                    if data.get('errcode') == 0:
                        logger.info("企业微信Markdown消息发送成功")
                        return True
                    else:
                        logger.error(f"企业微信Markdown发送失败: {data.get('errmsg')}")
                        return False
                        
        except Exception as e:
            logger.error(f"企业微信Markdown发送异常: {str(e)}")
            return False
    
    async def send_image(self, webhook_url: str, image_url: str,
                        caption: Optional[str] = None) -> bool:
        """
        发送图片到企业微信
        
        注意：企业微信要求图片必须先转base64或使用media_id
        这里使用图文消息的方式发送
        
        Args:
            webhook_url: Webhook URL
            image_url: 图片URL
            caption: 图片说明
            
        Returns:
            是否成功
        """
        try:
            await self.rate_limiter.acquire()
            
            # 企业微信不支持直接URL，使用图文消息
            message = {
                "msgtype": "news",
                "news": {
                    "articles": [
                        {
                            "title": caption or "图片",
                            "description": caption or "",
                            "url": image_url,
                            "picurl": image_url
                        }
                    ]
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    data = await response.json()
                    
                    if data.get('errcode') == 0:
                        logger.info("企业微信图片消息发送成功")
                        return True
                    else:
                        logger.error(f"企业微信图片发送失败: {data.get('errmsg')}")
                        return False
                        
        except Exception as e:
            logger.error(f"企业微信图片发送异常: {str(e)}")
            return False
    
    async def send_file(self, webhook_url: str, file_url: str,
                       filename: str) -> bool:
        """
        发送文件链接到企业微信
        
        注意：企业微信机器人不直接支持文件，使用图文消息发送链接
        
        Args:
            webhook_url: Webhook URL
            file_url: 文件URL
            filename: 文件名
            
        Returns:
            是否成功
        """
        try:
            await self.rate_limiter.acquire()
            
            message = {
                "msgtype": "news",
                "news": {
                    "articles": [
                        {
                            "title": f"📎 {filename}",
                            "description": "点击下载文件",
                            "url": file_url
                        }
                    ]
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    data = await response.json()
                    
                    if data.get('errcode') == 0:
                        logger.info("企业微信文件链接发送成功")
                        return True
                    else:
                        logger.error(f"企业微信文件发送失败: {data.get('errmsg')}")
                        return False
                        
        except Exception as e:
            logger.error(f"企业微信文件发送异常: {str(e)}")
            return False
    
    async def test_webhook(self, webhook_url: str) -> tuple[bool, str]:
        """
        测试Webhook连接
        
        Args:
            webhook_url: Webhook URL
            
        Returns:
            (是否成功, 消息)
        """
        try:
            message = {
                "msgtype": "text",
                "text": {
                    "content": "✅ KOOK消息转发系统测试消息\n\n如果您看到这条消息，说明企业微信配置成功！"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    data = await response.json()
                    
                    if data.get('errcode') == 0:
                        return True, "测试成功！"
                    else:
                        return False, f"测试失败: {data.get('errmsg', '未知错误')}"
                        
        except asyncio.TimeoutError:
            return False, "测试失败: 连接超时"
        except Exception as e:
            return False, f"测试失败: {str(e)}"


# 创建全局实例
wechatwork_forwarder = WechatWorkForwarder()
