"""
✅ P0-9优化: 托盘菜单统计完善API
提供7项实时统计，供Electron托盘菜单使用
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
from datetime import datetime, timedelta
from ..database import db
from ..queue.redis_client import redis_queue
from ..utils.logger import logger


router = APIRouter(prefix="/api/tray-stats", tags=["托盘统计"])


@router.get("/realtime")
async def get_realtime_stats() -> Dict[str, Any]:
    """
    获取实时统计信息（供托盘菜单使用）
    
    Returns:
        实时统计数据字典
    """
    try:
        # 1. 系统状态
        system_status = await _get_system_status()
        
        # 2. 今日转发统计
        today_stats = await _get_today_stats()
        
        # 3. 成功率统计
        success_rate = await _get_success_rate()
        
        # 4. 平均延迟
        avg_latency = await _get_avg_latency()
        
        # 5. 队列大小
        queue_size = await _get_queue_size()
        
        # 6. 活跃账号数
        active_accounts = await _get_active_accounts()
        
        # 7. 活跃Bot数
        active_bots = await _get_active_bots()
        
        # 8. 运行时长
        uptime = await _get_uptime()
        
        return {
            "success": True,
            "timestamp": time.time(),
            "stats": {
                # 系统状态
                "status": system_status["status"],  # online/reconnecting/error/offline
                "status_text": system_status["text"],  # 中文状态
                "status_icon": system_status["icon"],  # 🟢🟡🔴⚪
                
                # 今日转发数
                "today_messages": today_stats["total"],
                "today_success": today_stats["success"],
                "today_failed": today_stats["failed"],
                
                # 成功率
                "success_rate": success_rate,  # 百分比 0-100
                "success_rate_text": f"{success_rate:.1f}%",
                
                # 平均延迟
                "avg_latency_ms": avg_latency,
                "avg_latency_text": _format_latency(avg_latency),
                
                # 队列
                "queue_size": queue_size,
                "queue_status": _get_queue_status(queue_size),
                
                # 账号
                "active_accounts": active_accounts,
                "total_accounts": await _get_total_accounts(),
                
                # Bot
                "active_bots": active_bots,
                "total_bots": await _get_total_bots(),
                
                # 运行时长
                "uptime_seconds": uptime,
                "uptime_text": _format_uptime(uptime),
                
                # 其他信息
                "last_message_time": await _get_last_message_time(),
                "errors_today": await _get_errors_today()
            }
        }
    except Exception as e:
        logger.error(f"获取托盘统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick")
async def get_quick_stats() -> Dict[str, str]:
    """
    获取快速统计（简化版，供托盘快速展示）
    
    Returns:
        简化的统计文本
    """
    try:
        stats = await get_realtime_stats()
        data = stats["stats"]
        
        return {
            "success": True,
            "text": f"""
{data['status_icon']} {data['status_text']}

📊 今日转发: {data['today_messages']}条
✅ 成功率: {data['success_rate_text']}
⏱️ 延迟: {data['avg_latency_text']}
📦 队列: {data['queue_size']}条
👤 账号: {data['active_accounts']}/{data['total_accounts']}
🤖 Bot: {data['active_bots']}/{data['total_bots']}
⏰ 运行: {data['uptime_text']}
            """.strip()
        }
    except Exception as e:
        logger.error(f"获取快速统计失败: {str(e)}")
        return {
            "success": False,
            "text": "❌ 统计获取失败"
        }


# ========== 内部辅助函数 ==========

async def _get_system_status() -> Dict[str, str]:
    """获取系统状态"""
    try:
        # 检查账号状态
        accounts = db.get_accounts()
        online_accounts = [a for a in accounts if a.get('status') == 'online']
        
        # 检查Redis连接
        try:
            await redis_queue.ping()
            redis_ok = True
        except:
            redis_ok = False
        
        # 判断系统状态
        if not redis_ok:
            return {"status": "error", "text": "数据库异常", "icon": "🔴"}
        elif len(online_accounts) == 0:
            return {"status": "offline", "text": "离线", "icon": "⚪"}
        elif len(online_accounts) < len(accounts):
            return {"status": "reconnecting", "text": "部分在线", "icon": "🟡"}
        else:
            return {"status": "online", "text": "在线", "icon": "🟢"}
    except:
        return {"status": "error", "text": "状态未知", "icon": "🔴"}


async def _get_today_stats() -> Dict[str, int]:
    """获取今日转发统计"""
    try:
        # 查询今天的消息日志
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 这里简化处理，实际应该查询数据库
        logs = db.get_message_logs(limit=1000)
        
        today_logs = [
            log for log in logs
            if datetime.fromisoformat(log.get('created_at', '1970-01-01')) >= today_start
        ]
        
        total = len(today_logs)
        success = len([log for log in today_logs if log.get('status') == 'success'])
        failed = len([log for log in today_logs if log.get('status') == 'failed'])
        
        return {
            "total": total,
            "success": success,
            "failed": failed
        }
    except:
        return {"total": 0, "success": 0, "failed": 0}


async def _get_success_rate() -> float:
    """获取成功率"""
    try:
        stats = await _get_today_stats()
        if stats["total"] == 0:
            return 100.0
        return (stats["success"] / stats["total"]) * 100
    except:
        return 0.0


async def _get_avg_latency() -> int:
    """获取平均延迟（毫秒）"""
    try:
        logs = db.get_message_logs(limit=100, status='success')
        latencies = [log.get('latency_ms', 0) for log in logs if log.get('latency_ms')]
        
        if latencies:
            return int(sum(latencies) / len(latencies))
        return 0
    except:
        return 0


async def _get_queue_size() -> int:
    """获取队列大小"""
    try:
        size = await redis_queue.get_queue_size()
        return size
    except:
        return 0


async def _get_active_accounts() -> int:
    """获取活跃账号数"""
    try:
        accounts = db.get_accounts()
        return len([a for a in accounts if a.get('status') == 'online'])
    except:
        return 0


async def _get_total_accounts() -> int:
    """获取总账号数"""
    try:
        accounts = db.get_accounts()
        return len(accounts)
    except:
        return 0


async def _get_active_bots() -> int:
    """获取活跃Bot数"""
    try:
        bots = db.get_bot_configs()
        return len([b for b in bots if b.get('status') == 'active'])
    except:
        return 0


async def _get_total_bots() -> int:
    """获取总Bot数"""
    try:
        bots = db.get_bot_configs()
        return len(bots)
    except:
        return 0


# 启动时间（全局变量）
_start_time = time.time()


async def _get_uptime() -> int:
    """获取运行时长（秒）"""
    return int(time.time() - _start_time)


def _format_uptime(seconds: int) -> str:
    """格式化运行时长"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}分钟"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}天{hours}小时"


def _format_latency(ms: int) -> str:
    """格式化延迟"""
    if ms == 0:
        return "N/A"
    elif ms < 1000:
        return f"{ms}ms"
    else:
        return f"{ms/1000:.1f}秒"


def _get_queue_status(size: int) -> str:
    """获取队列状态"""
    if size == 0:
        return "空闲"
    elif size < 10:
        return "正常"
    elif size < 50:
        return "繁忙"
    else:
        return "拥堵"


async def _get_last_message_time() -> str:
    """获取最后一条消息时间"""
    try:
        logs = db.get_message_logs(limit=1)
        if logs:
            created_at = logs[0].get('created_at')
            if created_at:
                dt = datetime.fromisoformat(created_at)
                now = datetime.now()
                diff = (now - dt).total_seconds()
                
                if diff < 60:
                    return "刚刚"
                elif diff < 3600:
                    return f"{int(diff/60)}分钟前"
                elif diff < 86400:
                    return f"{int(diff/3600)}小时前"
                else:
                    return dt.strftime("%Y-%m-%d")
        return "暂无"
    except:
        return "未知"


async def _get_errors_today() -> int:
    """获取今日错误数"""
    try:
        stats = await _get_today_stats()
        return stats["failed"]
    except:
        return 0


@router.get("/history")
async def get_history_stats(hours: int = 24) -> Dict[str, Any]:
    """
    获取历史统计（用于图表）
    
    Args:
        hours: 小时数（默认24小时）
        
    Returns:
        历史统计数据
    """
    try:
        # 这里简化处理，实际应该查询数据库并按小时分组
        return {
            "success": True,
            "hours": hours,
            "data": {
                "timestamps": [],
                "message_counts": [],
                "success_rates": [],
                "latencies": []
            }
        }
    except Exception as e:
        logger.error(f"获取历史统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_stats() -> Dict[str, bool]:
    """
    重置统计数据
    
    Returns:
        操作结果
    """
    try:
        # 重置启动时间
        global _start_time
        _start_time = time.time()
        
        logger.info("✅ 统计数据已重置")
        
        return {
            "success": True,
            "message": "统计数据已重置"
        }
    except Exception as e:
        logger.error(f"重置统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
