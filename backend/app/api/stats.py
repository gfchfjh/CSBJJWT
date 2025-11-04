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
    """
    获取今日统计数据
    
    Returns:
        今日消息统计、成功率、延迟等
    """
    try:
        # 获取今日零点时间
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 使用 try-except 处理可能不存在的数据库方法
        try:
            # 1. 今日消息统计
            all_accounts = db.execute("SELECT * FROM accounts").fetchall()
            all_bots = db.execute("SELECT * FROM bots").fetchall()
            all_mappings = db.execute("SELECT * FROM mappings").fetchall()
            
            # 简单统计（如果没有消息表，返回模拟数据）
            messages_total = 0
            messages_success = 0
            messages_failed = 0
            messages_pending = 0
            avg_latency = 0.0
            
            # 尝试从日志或消息表获取统计
            try:
                # 检查是否有messages表
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
                # messages表不存在，使用默认值
                pass
            
            # 计算成功率
            success_rate = 0.0
            if messages_total > 0:
                success_rate = round((messages_success / messages_total) * 100, 1)
            
            # 活跃统计
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
            # 返回空数据而不是错误
            return TodayStats(
                messages_total=0,
                messages_success=0,
                messages_failed=0,
                messages_pending=0,
                success_rate=0.0,
                avg_latency=0.0,
                active_accounts=0,
                active_bots=0,
                active_mappings=0
            )
        
    except Exception as e:
        logger.error(f"获取今日统计失败: {str(e)}")
        # 返回空数据而不是抛出异常
        return TodayStats()


@router.get("/timeline", response_model=TimelineStats)
async def get_timeline_stats(range: str = Query("1h", description="时间范围: 1h, 6h, 24h, 7d, 30d")):
    """
    获取时间线统计数据
    
    Args:
        range: 时间范围 (1h, 6h, 24h, 7d, 30d)
        
    Returns:
        时间线数据点列表
    """
    try:
        # 解析时间范围
        range_map = {
            "1h": (timedelta(hours=1), 5),    # 1小时，5分钟间隔
            "6h": (timedelta(hours=6), 30),   # 6小时，30分钟间隔
            "24h": (timedelta(hours=24), 60), # 24小时，1小时间隔
            "7d": (timedelta(days=7), 360),   # 7天，6小时间隔
            "30d": (timedelta(days=30), 1440) # 30天，24小时间隔
        }
        
        if range not in range_map:
            range = "1h"
        
        delta, interval_minutes = range_map[range]
        start_time = datetime.now() - delta
        
        # 生成时间点
        data_points = []
        current_time = start_time
        now = datetime.now()
        
        while current_time <= now:
            # 尝试从数据库获取该时间段的消息数
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
                # messages表不存在，使用模拟数据
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
        
        return TimelineStats(
            range=range,
            data=data_points
        )
        
    except Exception as e:
        logger.error(f"获取时间线统计失败: {str(e)}")
        # 返回空数据
        return TimelineStats(range=range, data=[])


@router.get("/recent", response_model=List[RecentMessage])
async def get_recent_messages(limit: int = Query(10, ge=1, le=100)):
    """
    获取最近的消息列表
    
    Args:
        limit: 返回数量限制 (1-100)
        
    Returns:
        最近消息列表
    """
    try:
        # 尝试从数据库获取最近消息
        try:
            rows = db.execute("""
                SELECT 
                    id,
                    content,
                    author_name as author,
                    source_channel_name as source_channel,
                    target_platform,
                    status,
                    created_at,
                    latency
                FROM messages
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            
            messages = []
            for row in rows:
                messages.append(RecentMessage(
                    id=row['id'],
                    content=row['content'][:100] + ('...' if len(row['content']) > 100 else ''),
                    author=row['author'] or 'Unknown',
                    source_channel=row['source_channel'] or 'Unknown',
                    target_platform=row['target_platform'] or 'Unknown',
                    status=row['status'] or 'pending',
                    created_at=row['created_at'],
                    latency=row['latency']
                ))
            
            return messages
            
        except Exception as e:
            logger.warning(f"messages表不存在或查询失败: {str(e)}")
            # 返回空列表
            return []
        
    except Exception as e:
        logger.error(f"获取最近消息失败: {str(e)}")
        return []
