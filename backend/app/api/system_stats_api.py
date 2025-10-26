"""
系统实时统计API（用于托盘菜单）
✅ P1-1优化：托盘菜单5秒自动刷新统计
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timedelta
from ..database import db
from ..queue.redis_client import redis_queue
from ..utils.logger import logger
import time

router = APIRouter(prefix="/api/system", tags=["system"])


class RealtimeStatsResponse(BaseModel):
    """实时统计响应"""
    messages_today: int
    success_count: int
    failed_count: int
    success_rate: float
    avg_latency: float
    queue_size: int
    active_accounts: int
    configured_bots: int
    active_mappings: int
    uptime_seconds: int


# 记录应用启动时间
_app_start_time = time.time()


@router.get("/stats/realtime", response_model=RealtimeStatsResponse)
async def get_realtime_stats():
    """
    获取实时统计信息（专为托盘菜单设计）
    
    Returns:
        实时统计数据
    """
    try:
        # 获取今日零点时间
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 1. 今日消息总数
        messages_today = db.count_messages_since(today_start)
        
        # 2. 今日成功/失败数
        success_count = db.count_messages_by_status('success', since=today_start)
        failed_count = db.count_messages_by_status('failed', since=today_start)
        
        # 3. 成功率
        success_rate = 0.0
        if messages_today > 0:
            success_rate = round((success_count / messages_today) * 100, 1)
        
        # 4. 平均延迟（毫秒）
        avg_latency = db.get_average_latency(since=today_start)
        if avg_latency is None:
            avg_latency = 0.0
        avg_latency = round(avg_latency, 1)
        
        # 5. 队列大小
        queue_size = 0
        try:
            queue_size = await redis_queue.get_queue_size()
        except Exception as e:
            logger.warning(f"获取队列大小失败: {str(e)}")
        
        # 6. 活跃账号数（在线状态）
        active_accounts = len([
            acc for acc in db.get_all_accounts() 
            if acc.get('status') == 'online'
        ])
        
        # 7. 已配置的Bot数
        configured_bots = len(db.get_all_bots())
        
        # 8. 活跃映射数（启用状态）
        active_mappings = len([
            m for m in db.get_all_mappings()
            if m.get('enabled', True)
        ])
        
        # 9. 运行时长（秒）
        uptime_seconds = int(time.time() - _app_start_time)
        
        return RealtimeStatsResponse(
            messages_today=messages_today,
            success_count=success_count,
            failed_count=failed_count,
            success_rate=success_rate,
            avg_latency=avg_latency,
            queue_size=queue_size,
            active_accounts=active_accounts,
            configured_bots=configured_bots,
            active_mappings=active_mappings,
            uptime_seconds=uptime_seconds
        )
        
    except Exception as e:
        logger.error(f"获取实时统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/tray-menu")
async def get_tray_menu_stats():
    """
    获取托盘菜单格式的统计信息（已格式化为文本）
    
    Returns:
        格式化的统计文本
    """
    try:
        stats = await get_realtime_stats()
        
        # 格式化运行时长
        uptime_hours = stats.uptime_seconds // 3600
        uptime_mins = (stats.uptime_seconds % 3600) // 60
        uptime_text = f"{uptime_hours}小时{uptime_mins}分钟"
        
        return {
            "lines": [
                f"📊 实时统计",
                f"──────────────",
                f"今日转发: {stats.messages_today} 条",
                f"成功率: {stats.success_rate}%",
                f"平均延迟: {stats.avg_latency}ms",
                f"队列中: {stats.queue_size} 条",
                f"──────────────",
                f"活跃账号: {stats.active_accounts} 个",
                f"配置Bot: {stats.configured_bots} 个",
                f"映射数: {stats.active_mappings} 个",
                f"──────────────",
                f"运行时长: {uptime_text}"
            ],
            "raw_stats": stats.dict()
        }
        
    except Exception as e:
        logger.error(f"获取托盘菜单统计失败: {str(e)}")
        return {
            "lines": [
                "📊 实时统计",
                "──────────────",
                "数据加载失败",
                "请检查后端服务"
            ],
            "raw_stats": None
        }


@router.get("/stats/summary")
async def get_stats_summary():
    """
    获取统计摘要（更详细的版本）
    
    Returns:
        详细统计摘要
    """
    try:
        stats = await get_realtime_stats()
        
        # 获取最近1小时的统计
        one_hour_ago = datetime.now() - timedelta(hours=1)
        messages_last_hour = db.count_messages_since(one_hour_ago)
        
        # 获取最近失败的消息
        recent_failures = db.get_recent_failed_messages(limit=5)
        
        return {
            "today": {
                "total": stats.messages_today,
                "success": stats.success_count,
                "failed": stats.failed_count,
                "success_rate": stats.success_rate,
                "avg_latency": stats.avg_latency
            },
            "last_hour": {
                "total": messages_last_hour
            },
            "current": {
                "queue_size": stats.queue_size,
                "active_accounts": stats.active_accounts,
                "configured_bots": stats.configured_bots,
                "active_mappings": stats.active_mappings
            },
            "system": {
                "uptime_seconds": stats.uptime_seconds
            },
            "recent_failures": [
                {
                    "id": f.get("id"),
                    "content": f.get("content", "")[:50],
                    "error": f.get("error_message"),
                    "time": f.get("created_at")
                }
                for f in recent_failures
            ]
        }
        
    except Exception as e:
        logger.error(f"获取统计摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
