"""
日志查询API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..database import db


router = APIRouter(prefix="/api/logs", tags=["logs"])


class MessageLogResponse(BaseModel):
    id: int
    kook_message_id: str
    kook_channel_id: str
    content: str
    message_type: str
    sender_name: str
    target_platform: str
    target_channel: str
    status: str
    error_message: Optional[str]
    latency_ms: Optional[int]
    created_at: str


@router.get("/", response_model=List[MessageLogResponse])
async def get_logs(limit: int = 100, status: str = None):
    """获取消息日志"""
    logs = db.get_message_logs(limit, status)
    return logs


@router.get("/stats")
async def get_stats():
    """获取统计信息"""
    # TODO: 实现统计逻辑
    return {
        "total": 0,
        "success": 0,
        "failed": 0,
        "success_rate": 0.0,
        "avg_latency": 0
    }
