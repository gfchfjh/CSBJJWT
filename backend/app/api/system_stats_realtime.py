"""
系统实时统计API - P1-5深度优化
提供5秒刷新的实时统计数据
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
import time
from ..database import db
from ..queue.redis_client import redis_queue
from ..utils.logger import logger

router = APIRouter(prefix="/api/system", tags=["系统统计"])


class SystemStats(BaseModel):
    """系统统计数据"""
    total_forwarded: int = 0          # 转发总数
    success_rate: float = 0.0          # 成功率（0-1）
    queue_size: int = 0                # 当前队列大小
    status: str = "stopped"            # 状态：running/stopped/error
    active_scrapers: int = 0           # 活跃抓取器数量
    active_bots: int = 0               # 活跃Bot数量
    last_message_time: str = ""        # 最后一条消息时间
    uptime_seconds: int = 0            # 运行时长（秒）


class DetailedStats(BaseModel):
    """详细统计（包含趋势）"""
    current: SystemStats
    hourly: Dict[str, int] = {}        # 每小时统计
    daily: Dict[str, int] = {}         # 每日统计
    platform_breakdown: Dict[str, Dict[str, Any]] = {}  # 平台分解


# 系统启动时间（用于计算uptime）
system_start_time = time.time()


@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """
    获取系统实时统计
    
    返回：
    - total_forwarded: 转发总数
    - success_rate: 成功率
    - queue_size: 队列大小
    - status: 运行状态
    - active_scrapers: 活跃抓取器
    - active_bots: 活跃Bot
    """
    try:
        # 1. 从数据库获取转发总数
        total_result = db.execute("""
            SELECT COUNT(*) as total 
            FROM message_logs 
            WHERE created_at > datetime('now', '-7 days')
        """).fetchone()
        
        total_forwarded = total_result['total'] if total_result else 0
        
        # 2. 计算成功率
        success_result = db.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count
            FROM message_logs
            WHERE created_at > datetime('now', '-24 hours')
        """).fetchone()
        
        if success_result and success_result['total'] > 0:
            success_rate = success_result['success_count'] / success_result['total']
        else:
            success_rate = 0.0
        
        # 3. 获取队列大小
        try:
            queue_size = await redis_queue.get_queue_size()
        except Exception as e:
            logger.error(f"获取队列大小失败: {e}")
            queue_size = 0
        
        # 4. 检查系统状态
        status = await check_system_status()
        
        # 5. 统计活跃抓取器
        active_scrapers_result = db.execute("""
            SELECT COUNT(*) as count 
            FROM accounts 
            WHERE status = 'online'
        """).fetchone()
        
        active_scrapers = active_scrapers_result['count'] if active_scrapers_result else 0
        
        # 6. 统计活跃Bot
        active_bots_result = db.execute("""
            SELECT COUNT(DISTINCT platform) as count
            FROM (
                SELECT 'discord' as platform FROM bot_configs WHERE platform = 'discord' AND status = 'active'
                UNION ALL
                SELECT 'telegram' as platform FROM bot_configs WHERE platform = 'telegram' AND status = 'active'
                UNION ALL
                SELECT 'feishu' as platform FROM bot_configs WHERE platform = 'feishu' AND status = 'active'
            )
        """).fetchone()
        
        active_bots = active_bots_result['count'] if active_bots_result else 0
        
        # 7. 最后一条消息时间
        last_message_result = db.execute("""
            SELECT created_at 
            FROM message_logs 
            ORDER BY created_at DESC 
            LIMIT 1
        """).fetchone()
        
        last_message_time = last_message_result['created_at'] if last_message_result else ""
        
        # 8. 运行时长
        uptime_seconds = int(time.time() - system_start_time)
        
        return SystemStats(
            total_forwarded=total_forwarded,
            success_rate=round(success_rate, 3),
            queue_size=queue_size,
            status=status,
            active_scrapers=active_scrapers,
            active_bots=active_bots,
            last_message_time=last_message_time,
            uptime_seconds=uptime_seconds
        )
        
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}", exc_info=True)
        
        # 返回默认数据（避免崩溃）
        return SystemStats(
            status="error",
            total_forwarded=0,
            success_rate=0.0,
            queue_size=0
        )


@router.get("/stats/detailed", response_model=DetailedStats)
async def get_detailed_stats():
    """
    获取详细统计（包含趋势数据）
    """
    try:
        # 1. 获取当前统计
        current = await get_system_stats()
        
        # 2. 每小时统计（最近24小时）
        hourly_result = db.execute("""
            SELECT 
                strftime('%H', created_at) as hour,
                COUNT(*) as count
            FROM message_logs
            WHERE created_at > datetime('now', '-24 hours')
            GROUP BY hour
            ORDER BY hour
        """).fetchall()
        
        hourly = {row['hour']: row['count'] for row in hourly_result}
        
        # 3. 每日统计（最近7天）
        daily_result = db.execute("""
            SELECT 
                date(created_at) as day,
                COUNT(*) as count
            FROM message_logs
            WHERE created_at > datetime('now', '-7 days')
            GROUP BY day
            ORDER BY day
        """).fetchall()
        
        daily = {row['day']: row['count'] for row in daily_result}
        
        # 4. 平台分解统计
        platform_result = db.execute("""
            SELECT 
                target_platform as platform,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(latency_ms) as avg_latency
            FROM message_logs
            WHERE created_at > datetime('now', '-24 hours')
            GROUP BY target_platform
        """).fetchall()
        
        platform_breakdown = {}
        for row in platform_result:
            platform = row['platform']
            platform_breakdown[platform] = {
                'total': row['total'],
                'success': row['success'],
                'failed': row['failed'],
                'success_rate': row['success'] / row['total'] if row['total'] > 0 else 0,
                'avg_latency_ms': round(row['avg_latency'] or 0, 2)
            }
        
        return DetailedStats(
            current=current,
            hourly=hourly,
            daily=daily,
            platform_breakdown=platform_breakdown
        )
        
    except Exception as e:
        logger.error(f"获取详细统计失败: {e}", exc_info=True)
        return DetailedStats(current=SystemStats())


async def check_system_status() -> str:
    """
    检查系统状态
    
    返回: running/stopped/error
    """
    try:
        # 检查Redis连接
        try:
            if redis_queue.redis:
                await redis_queue.redis.ping()
                redis_ok = True
            else:
                redis_ok = False
        except:
            redis_ok = False
        
        if not redis_ok:
            return "error"
        
        # 检查是否有活跃的抓取器
        active_count = db.execute("""
            SELECT COUNT(*) as count 
            FROM accounts 
            WHERE status = 'online'
        """).fetchone()
        
        if active_count and active_count['count'] > 0:
            return "running"
        else:
            return "stopped"
            
    except Exception as e:
        logger.error(f"检查系统状态失败: {e}")
        return "error"


@router.post("/start")
async def start_system():
    """启动系统（启动所有抓取器）"""
    try:
        from ..kook.scraper import scraper_manager
        
        await scraper_manager.start_all()
        
        return {"message": "系统已启动"}
    except Exception as e:
        logger.error(f"启动系统失败: {e}")
        return {"error": str(e)}


@router.post("/stop")
async def stop_system():
    """停止系统（停止所有抓取器）"""
    try:
        from ..kook.scraper import scraper_manager
        
        await scraper_manager.stop_all()
        
        return {"message": "系统已停止"}
    except Exception as e:
        logger.error(f"停止系统失败: {e}")
        return {"error": str(e)}


@router.post("/restart")
async def restart_system():
    """重启系统"""
    try:
        from ..kook.scraper import scraper_manager
        
        # 停止所有
        await scraper_manager.stop_all()
        
        # 等待3秒
        import asyncio
        await asyncio.sleep(3)
        
        # 重新启动
        await scraper_manager.start_all()
        
        return {"message": "系统已重启"}
    except Exception as e:
        logger.error(f"重启系统失败: {e}")
        return {"error": str(e)}
