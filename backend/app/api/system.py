"""
系统管理API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..queue.redis_client import redis_queue
from ..queue.worker import message_worker
from ..kook.scraper import scraper_manager
from ..processors.filter import message_filter
from ..config import settings
import asyncio


router = APIRouter(prefix="/api/system", tags=["system"])


class SystemStatus(BaseModel):
    service_running: bool
    redis_connected: bool
    queue_size: int
    active_scrapers: int


@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """获取系统状态"""
    try:
        queue_size = await redis_queue.get_queue_size()
        redis_connected = True
    except:
        queue_size = 0
        redis_connected = False
    
    return {
        "service_running": message_worker.is_running,
        "redis_connected": redis_connected,
        "queue_size": queue_size,
        "active_scrapers": len(scraper_manager.scrapers)
    }


@router.post("/start")
async def start_service():
    """启动服务"""
    if not message_worker.is_running:
        asyncio.create_task(message_worker.start())
    
    return {"message": "服务已启动"}


@router.post("/stop")
async def stop_service():
    """停止服务"""
    await message_worker.stop()
    await scraper_manager.stop_all()
    
    return {"message": "服务已停止"}


@router.get("/config")
async def get_config():
    """获取配置信息"""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "api_port": settings.api_port,
        "image_storage_path": str(settings.image_storage_path),
        "log_level": settings.log_level
    }


@router.get("/filter-rules")
async def get_filter_rules():
    """获取过滤规则"""
    rules = message_filter.get_rules()
    return rules


class FilterRules(BaseModel):
    scope: str = "global"
    channel_id: Optional[str] = None
    keyword_blacklist: List[str] = []
    keyword_whitelist: List[str] = []
    keyword_filter_enabled: bool = False
    user_blacklist: List[Dict[str, str]] = []
    user_whitelist: List[Dict[str, str]] = []
    user_filter_enabled: bool = False
    message_types: List[str] = ["text", "image", "file", "link"]
    only_mention_all: bool = False


@router.post("/filter-rules")
async def save_filter_rules(rules: FilterRules):
    """保存过滤规则"""
    try:
        success = message_filter.save_rules(rules.dict())
        if success:
            return {"message": "过滤规则保存成功"}
        else:
            raise HTTPException(status_code=500, detail="保存失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
