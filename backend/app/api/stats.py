"""
统计数据API - 为前端首页提供数据
✅ 新增：今日统计、时间线统计、最近消息
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..database import db
from ..utils.logger import logger
import time

router = APIRouter(prefix="/api/stats", tags=["statistics"])


class TodayStats(BaseModel):
    """今日统计"""
    messages_total: int = 0
    messages_success: int = 0
    messages_failed: int = 0
    messages_pending: int = 0
    success_rate: float = 0.0
    avg_latency: float = 0.0
    active_accounts: int = 0
    active_bots: int = 0
    active_mappings: int = 0


class TimelinePoint(BaseModel):
    """时间线数据点"""
    timestamp: str
    count: int
    success: int
    failed: int


class TimelineStats(BaseModel):
    """时间线统计"""
    range: str
    data: List[TimelinePoint]


class RecentMessage(BaseModel):
    """最近消息"""
    id: int
    content: str
    author: str
    source_channel: str
    target_platform: str
    status: str
    created_at: str
    latency: Optional[float] = None


@router.get("/today", response_model=TodayStats)
async def get_today_stats():
    """获取今日统计数据"""
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        try:
            all_accounts = db.execute("SELECT * FROM accounts").fetchall()
            all_bots = db.execute("SELECT * FROM bots").fetchall()
            all_mappings = db.execute("SELECT * FROM mappings").fetchall()
            
            messages_total = 0
            messages_success = 0
            messages_failed = 0
            messages_pending = 0
            avg_latency = 0.0
            
            try:
                result = db.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                        AVG(CASE WHEN latency IS NOT NULL THEN latency ELSE 0 END) as avg_latency
                    FROM messages
                    WHERE created_at >= ?
                """, (today_start.isoformat(),)).fetchone()
                
                if result:
                    messages_total = result['total'] or 0
                    messages_success = result['success'] or 0
                    messages_failed = result['failed'] or 0
                    messages_pending = result['pending'] or 0
                    avg_latency = result['avg_latency'] or 0.0
            except Exception:
                pass
            
            success_rate = 0.0
            if messages_total > 0:
                success_rate = round((messages_success / messages_total) * 100, 1)
            
            active_accounts = len([a for a in all_accounts if a.get('status') == 'online'])
            active_bots = len([b for b in all_bots if b.get('enabled', True)])
            active_mappings = len([m for m in all_mappings if m.get('enabled', True)])
            
            return TodayStats(
                messages_total=messages_total,
                messages_success=messages_success,
                messages_failed=messages_failed,
                messages_pending=messages_pending,
                success_rate=success_rate,
                avg_latency=round(avg_latency, 1),
                active_accounts=active_accounts,
                active_bots=active_bots,
                active_mappings=active_mappings
            )
            
        except Exception as e:
            logger.warning(f"获取今日统计失败，返回空数据: {str(e)}")
            return TodayStats()
        
    except Exception as e:
        logger.error(f"获取今日统计失败: {str(e)}")
        return TodayStats()


@router.get("/timeline", response_model=TimelineStats)
async def get_timeline_stats(range: str = Query("1h", description="时间范围: 1h, 6h, 24h, 7d, 30d")):
    """获取时间线统计数据"""
    try:
        range_map = {
            "1h": (timedelta(hours=1), 5),
            "6h": (timedelta(hours=6), 30),
            "24h": (timedelta(hours=24), 60),
            "7d": (timedelta(days=7), 360),
            "30d": (timedelta(days=30), 1440)
        }
        
        if range not in range_map:
            range = "1h"
        
        delta, interval_minutes = range_map[range]
        start_time = datetime.now() - delta
        
        data_points = []
        current_time = start_time
        now = datetime.now()
        
        while current_time <= now:
            try:
                next_time = current_time + timedelta(minutes=interval_minutes)
                
                result = db.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                    FROM messages
                    WHERE created_at >= ? AND created_at < ?
                """, (current_time.isoformat(), next_time.isoformat())).fetchone()
                
                count = result['total'] or 0
                success = result['success'] or 0
                failed = result['failed'] or 0
            except Exception:
                count = 0
                success = 0
                failed = 0
            
            data_points.append(TimelinePoint(
                timestamp=current_time.isoformat(),
                count=count,
                success=success,
                failed=failed
            ))
            
            current_time += timedelta(minutes=interval_minutes)
        
        return TimelineStats(range=range, data=data_points)
        
    except Exception as e:
        logger.error(f"获取时间线统计失败: {str(e)}")
        return TimelineStats(range=range, data=[])