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
    """测试Bot配置"""
    # 获取配置
    configs = db.get_bot_configs()
    config = next((c for c in configs if c['id'] == bot_id), None)
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    platform = config['platform']
    bot_config = config['config']
    
    # 测试连接
    if platform == 'discord':
        webhook_url = bot_config.get('webhook_url')
        if not webhook_url:
            raise HTTPException(status_code=400, detail="缺少webhook_url")
        
        success, message = await discord_forwarder.test_webhook(webhook_url)
        
    elif platform == 'telegram':
        token = bot_config.get('token')
        chat_id = bot_config.get('chat_id')
        if not token or not chat_id:
            raise HTTPException(status_code=400, detail="缺少token或chat_id")
        
        success, message = await telegram_forwarder.test_bot(token, chat_id)
        
    elif platform == 'feishu':
        app_id = bot_config.get('app_id')
        app_secret = bot_config.get('app_secret')
        chat_id = bot_config.get('chat_id')
        if not app_id or not app_secret or not chat_id:
            raise HTTPException(status_code=400, detail="缺少app_id、app_secret或chat_id")
        
        success, message = await feishu_forwarder.test_connection(app_id, app_secret, chat_id)
        
    else:
        raise HTTPException(status_code=400, detail="不支持的平台")
    
    return {"success": success, "message": message}


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
