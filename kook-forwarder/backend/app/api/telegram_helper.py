"""
Telegram辅助工具API
提供Telegram配置辅助功能，如自动获取Chat ID
v1.15.0 新增
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from ..utils.logger import logger

router = APIRouter(prefix="/api/telegram-helper", tags=["Telegram Helper"])


class BotTokenRequest(BaseModel):
    """Bot Token请求模型"""
    bot_token: str


class ChatInfo(BaseModel):
    """群组信息模型"""
    chat_id: int
    chat_title: str
    chat_type: str
    member_count: Optional[int] = None


class AutoGetChatIDResponse(BaseModel):
    """自动获取Chat ID响应"""
    success: bool
    message: str
    chats: List[ChatInfo] = []
    timeout_seconds: int = 30


@router.post("/get-chat-id", response_model=AutoGetChatIDResponse)
async def auto_get_chat_id(request: BotTokenRequest):
    """
    自动获取Chat ID
    
    流程：
    1. 用户将Bot添加到目标群组
    2. 在群组中发送任意消息
    3. 调用此API
    4. API轮询getUpdates获取最新消息
    5. 返回所有包含此Bot的群组的Chat ID
    
    Args:
        request: 包含bot_token的请求
        
    Returns:
        AutoGetChatIDResponse: 包含找到的群组列表
    """
    try:
        logger.info(f"开始自动获取Chat ID，Token: {request.bot_token[:10]}...")
        
        # 创建Bot实例
        bot = Bot(token=request.bot_token)
        
        # 验证Token
        try:
            bot_info = await bot.get_me()
            logger.info(f"Bot验证成功: @{bot_info.username}")
        except TelegramError as e:
            logger.error(f"Bot Token验证失败: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Bot Token无效: {str(e)}"
            )
        
        # 轮询获取更新
        found_chats = []
        timeout = 30  # 30秒超时
        poll_interval = 2  # 每2秒轮询一次
        max_attempts = timeout // poll_interval
        
        logger.info(f"开始轮询更新（最多{max_attempts}次，每{poll_interval}秒）...")
        
        offset = None
        for attempt in range(max_attempts):
            try:
                # 获取更新
                updates = await bot.get_updates(
                    offset=offset,
                    timeout=poll_interval,
                    allowed_updates=["message", "channel_post"]
                )
                
                if updates:
                    logger.info(f"收到{len(updates)}条更新")
                    
                    # 处理每个更新
                    for update in updates:
                        # 更新offset
                        offset = update.update_id + 1
                        
                        # 获取聊天信息
                        chat = None
                        if update.message:
                            chat = update.message.chat
                        elif update.channel_post:
                            chat = update.channel_post.chat
                        
                        if chat and chat.type in ['group', 'supergroup', 'channel']:
                            # 检查是否已添加
                            if not any(c.chat_id == chat.id for c in found_chats):
                                # 获取成员数（如果可能）
                                member_count = None
                                try:
                                    if chat.type in ['group', 'supergroup']:
                                        chat_full = await bot.get_chat(chat.id)
                                        member_count = await bot.get_chat_member_count(chat.id)
                                except Exception:
                                    pass
                                
                                chat_info = ChatInfo(
                                    chat_id=chat.id,
                                    chat_title=chat.title or "未命名群组",
                                    chat_type=chat.type,
                                    member_count=member_count
                                )
                                found_chats.append(chat_info)
                                logger.info(f"找到群组: {chat_info.chat_title} (ID: {chat_info.chat_id})")
                else:
                    logger.debug(f"第{attempt+1}次轮询：无新消息")
                
                # 如果已找到群组，可以提前返回
                if found_chats:
                    logger.info(f"成功找到{len(found_chats)}个群组")
                    return AutoGetChatIDResponse(
                        success=True,
                        message=f"成功找到{len(found_chats)}个群组",
                        chats=found_chats,
                        timeout_seconds=timeout
                    )
                
                # 等待下一次轮询
                if attempt < max_attempts - 1:
                    await asyncio.sleep(poll_interval)
                    
            except TelegramError as e:
                logger.error(f"获取更新失败: {e}")
                if "unauthorized" in str(e).lower():
                    raise HTTPException(
                        status_code=401,
                        detail="Bot未被授权，请确保Bot已添加到群组"
                    )
        
        # 超时未找到群组
        if not found_chats:
            logger.warning("轮询超时，未找到任何群组")
            return AutoGetChatIDResponse(
                success=False,
                message=f"超时（{timeout}秒）未找到群组。请确保：\n"
                       "1. Bot已添加到目标群组\n"
                       "2. 在群组中发送了至少一条消息\n"
                       "3. Bot有权限读取消息",
                chats=[],
                timeout_seconds=timeout
            )
        
        return AutoGetChatIDResponse(
            success=True,
            message=f"成功找到{len(found_chats)}个群组",
            chats=found_chats,
            timeout_seconds=timeout
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"自动获取Chat ID失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"获取Chat ID失败: {str(e)}"
        )


@router.post("/test-connection")
async def test_telegram_connection(request: BotTokenRequest):
    """
    测试Telegram Bot连接
    
    Args:
        request: 包含bot_token的请求
        
    Returns:
        dict: Bot信息
    """
    try:
        bot = Bot(token=request.bot_token)
        bot_info = await bot.get_me()
        
        return {
            "success": True,
            "bot_info": {
                "id": bot_info.id,
                "username": bot_info.username,
                "first_name": bot_info.first_name,
                "can_join_groups": bot_info.can_join_groups,
                "can_read_all_group_messages": bot_info.can_read_all_group_messages,
            }
        }
    except TelegramError as e:
        raise HTTPException(
            status_code=400,
            detail=f"连接失败: {str(e)}"
        )
