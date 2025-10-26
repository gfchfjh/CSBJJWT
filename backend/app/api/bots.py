"""
Bot配置API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from ..database import db
from ..forwarders.discord import discord_forwarder
from ..forwarders.telegram import telegram_forwarder
from ..forwarders.feishu import feishu_forwarder


router = APIRouter(prefix="/api/bots", tags=["bots"])


class BotConfigCreate(BaseModel):
    platform: str
    name: str
    config: Dict[str, Any]


class BotConfigResponse(BaseModel):
    id: int
    platform: str
    name: str
    config: Dict[str, Any]
    status: str
    created_at: str


@router.get("/", response_model=List[BotConfigResponse])
async def get_bot_configs(platform: str = None):
    """获取Bot配置列表"""
    configs = db.get_bot_configs(platform)
    return configs


@router.post("/", response_model=BotConfigResponse)
async def add_bot_config(bot: BotConfigCreate):
    """添加Bot配置"""
    # 验证平台
    if bot.platform not in ['discord', 'telegram', 'feishu']:
        raise HTTPException(status_code=400, detail="不支持的平台")
    
    # 添加到数据库
    bot_id = db.add_bot_config(
        platform=bot.platform,
        name=bot.name,
        config=bot.config
    )
    
    # 返回配置信息
    configs = db.get_bot_configs(bot.platform)
    new_config = next((c for c in configs if c['id'] == bot_id), None)
    
    if not new_config:
        raise HTTPException(status_code=500, detail="添加配置失败")
    
    return new_config


@router.delete("/{bot_id}")
async def delete_bot_config(bot_id: int):
    """删除Bot配置"""
    db.delete_bot_config(bot_id)
    return {"message": "配置已删除"}


@router.post("/{bot_id}/test")
async def test_bot_config(bot_id: int):
    """
    ✅ P1-2增强：测试Bot配置（真实发送测试消息）
    """
    import time
    from datetime import datetime
    from ..utils.logger import logger
    
    # 获取配置
    configs = db.get_bot_configs()
    config = next((c for c in configs if c['id'] == bot_id), None)
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    platform = config['platform']
    bot_config = config['config']
    test_message = f"🧪 这是来自 KOOK消息转发系统 的测试消息\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    test_result = {
        "success": False,
        "message": "",
        "details": {},
        "timestamp": int(time.time())
    }
    
    # 测试连接
    if platform == 'discord':
        webhook_url = bot_config.get('webhook_url')
        if not webhook_url:
            raise HTTPException(status_code=400, detail="缺少webhook_url")
        
        # ✅ 真实发送测试消息
        success, message = await discord_forwarder.test_webhook(webhook_url)
        test_result["success"] = success
        test_result["message"] = message if message else ("测试成功！已发送测试消息到Discord" if success else "测试失败")
        test_result["details"] = {
            "platform": "Discord",
            "webhook_url": webhook_url[:50] + "...",
            "message_sent": success
        }
        
    elif platform == 'telegram':
        token = bot_config.get('token')
        chat_id = bot_config.get('chat_id')
        if not token or not chat_id:
            raise HTTPException(status_code=400, detail="缺少token或chat_id")
        
        # ✅ 真实发送测试消息
        success, message = await telegram_forwarder.test_bot(token, chat_id)
        test_result["success"] = success
        test_result["message"] = message if message else ("测试成功！已发送测试消息到Telegram" if success else "测试失败")
        test_result["details"] = {
            "platform": "Telegram",
            "bot_token": token[:10] + "...",
            "chat_id": chat_id,
            "message_sent": success
        }
        
    elif platform == 'feishu':
        app_id = bot_config.get('app_id')
        app_secret = bot_config.get('app_secret')
        chat_id = bot_config.get('chat_id')
        if not app_id or not app_secret or not chat_id:
            raise HTTPException(status_code=400, detail="缺少app_id、app_secret或chat_id")
        
        # ✅ 真实发送测试消息  
        success, message = await feishu_forwarder.test_connection(app_id, app_secret, chat_id)
        test_result["success"] = success
        test_result["message"] = message if message else ("测试成功！已发送测试消息到飞书" if success else "测试失败")
        test_result["details"] = {
            "platform": "飞书",
            "app_id": app_id,
            "chat_id": chat_id,
            "message_sent": success
        }
        
    else:
        raise HTTPException(status_code=400, detail="不支持的平台")
    
    # ✅ 记录测试结果到数据库
    try:
        import json
        db.execute(
            "UPDATE bot_configs SET status = ? WHERE id = ?",
            ("active" if test_result["success"] else "error", bot_id)
        )
        logger.info(f"✅ Bot测试完成 - ID: {bot_id}, 平台: {platform}, 结果: {test_result['success']}")
    except Exception as e:
        logger.error(f"❌ 更新测试结果失败: {str(e)}")
    
    return test_result


@router.get("/telegram/chat-ids")
async def get_telegram_chat_ids(token: str):
    """
    获取Telegram Chat ID列表
    
    通过Bot Token获取最近与Bot交互的所有Chat ID
    """
    if not token:
        raise HTTPException(status_code=400, detail="缺少token参数")
    
    success, chat_ids = await telegram_forwarder.get_chat_ids(token)
    
    if not success:
        raise HTTPException(status_code=500, detail="获取Chat ID失败，请检查Token是否正确")
    
    if not chat_ids:
        return {
            "message": "未找到任何Chat ID。请先在Telegram中向Bot发送一条消息，然后重试。",
            "chat_ids": []
        }
    
    return {
        "message": f"找到 {len(chat_ids)} 个Chat ID",
        "chat_ids": chat_ids
    }
