"""
日志查询API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
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
    """
    获取今日统计信息
    
    Returns:
        总消息数、成功数、失败数、成功率、平均延迟
    """
    # 获取所有日志（简化实现，实际应按日期查询）
    logs = db.get_message_logs(limit=10000)
    
    # 计算今日数据
    today = datetime.now().date()
    today_logs = [log for log in logs if 
                  datetime.fromisoformat(log['created_at']).date() == today]
    
    total = len(today_logs)
    success = len([log for log in today_logs if log['status'] == 'success'])
    failed = len([log for log in today_logs if log['status'] == 'failed'])
    
    # 计算成功率
    success_rate = round((success / total * 100) if total > 0 else 0, 1)
    
    # 计算平均延迟
    latencies = [log['latency_ms'] for log in today_logs 
                 if log['latency_ms'] is not None]
    avg_latency = round(sum(latencies) / len(latencies)) if latencies else 0
    
    return {
        "total": total,
        "success": success,
        "failed": failed,
        "success_rate": success_rate,
        "avg_latency": avg_latency
    }


@router.get("/stats/trend")
async def get_stats_trend(hours: int = 24) -> Dict[str, Any]:
    """
    获取消息转发量趋势数据（按小时统计）
    
    Args:
        hours: 统计最近N小时的数据（默认24小时）
        
    Returns:
        小时列表和对应的消息数量
    """
    logs = db.get_message_logs(limit=100000)
    
    # 准备时间范围
    now = datetime.now()
    hour_labels = []
    hour_counts = []
    
    for i in range(hours - 1, -1, -1):
        hour_time = now - timedelta(hours=i)
        hour_label = hour_time.strftime('%H:00')
        
        # 统计该小时内的消息数
        hour_start = hour_time.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        
        count = len([log for log in logs if 
                    hour_start <= datetime.fromisoformat(log['created_at']) < hour_end])
        
        hour_labels.append(hour_label)
        hour_counts.append(count)
    
    return {
        "hours": hour_labels,
        "counts": hour_counts
    }


@router.get("/stats/platforms")
async def get_stats_by_platform() -> Dict[str, Any]:
    """
    获取各平台的消息分布统计
    
    Returns:
        各平台名称和对应的消息数量
    """
    logs = db.get_message_logs(limit=10000)
    
    # 统计今日数据
    today = datetime.now().date()
    today_logs = [log for log in logs if 
                  datetime.fromisoformat(log['created_at']).date() == today]
    
    # 按平台统计
    platform_counts = {}
    for log in today_logs:
        platform = log.get('target_platform', 'unknown')
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    # 格式化输出
    platforms = []
    counts = []
    
    # 确保三个主要平台都有数据
    for platform in ['discord', 'telegram', 'feishu']:
        display_name = {
            'discord': 'Discord',
            'telegram': 'Telegram',
            'feishu': '飞书'
        }.get(platform, platform)
        
        platforms.append(display_name)
        counts.append(platform_counts.get(platform, 0))
    
    return {
        "platforms": platforms,
        "counts": counts
    }
