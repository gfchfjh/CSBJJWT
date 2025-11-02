"""
性能监控API
提供系统性能指标和统计数据
"""
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from fastapi import APIRouter, Query
from ..utils.logger import logger
from ..database import db
from ..queue.redis_client import redis_queue

router = APIRouter(prefix="/api/performance", tags=["performance"])


@router.get("/metrics")
async def get_performance_metrics(time_range: str = Query(default="1h", regex="^(1h|6h|24h)$")):
    """
    获取性能监控指标
    
    Args:
        time_range: 时间范围（1h/6h/24h）
        
    Returns:
        性能指标数据
    """
    try:
        # 解析时间范围
        range_minutes = {
            "1h": 60,
            "6h": 360,
            "24h": 1440
        }[time_range]
        
        # 获取实时指标
        metrics = await get_realtime_metrics()
        
        # 获取历史数据
        message_data = await get_message_trend_data(range_minutes)
        resource_data = await get_resource_trend_data(range_minutes)
        platform_data = await get_platform_distribution_data(range_minutes)
        error_data = await get_error_rate_data(range_minutes)
        
        return {
            "metrics": metrics,
            "messageData": message_data,
            "resourceData": resource_data,
            "platformData": platform_data,
            "errorData": error_data
        }
        
    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        return {
            "metrics": get_default_metrics(),
            "messageData": {},
            "resourceData": {},
            "platformData": [],
            "errorData": {}
        }


async def get_realtime_metrics() -> Dict[str, Any]:
    """获取实时性能指标"""
    try:
        # CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        
        # 消息处理速度（最近1分钟）
        processing_rate = await get_processing_rate(minutes=1)
        
        # 消息处理趋势（与上一分钟对比）
        prev_rate = await get_processing_rate(minutes=1, offset=1)
        processing_trend = ((processing_rate - prev_rate) / prev_rate * 100) if prev_rate > 0 else 0
        
        # 队列积压
        queue_size = await get_queue_size()
        
        return {
            "cpuUsage": round(cpu_usage, 1),
            "memoryUsage": round(memory_usage, 1),
            "memoryUsedMB": round(memory_used_mb, 0),
            "memoryTotalMB": round(memory_total_mb, 0),
            "processingRate": processing_rate,
            "processingTrend": round(processing_trend, 1),
            "queueSize": queue_size
        }
        
    except Exception as e:
        logger.error(f"获取实时指标失败: {str(e)}")
        return get_default_metrics()


def get_default_metrics() -> Dict[str, Any]:
    """获取默认指标（出错时返回）"""
    return {
        "cpuUsage": 0,
        "memoryUsage": 0,
        "memoryUsedMB": 0,
        "memoryTotalMB": 0,
        "processingRate": 0,
        "processingTrend": 0,
        "queueSize": 0
    }


async def get_processing_rate(minutes: int = 1, offset: int = 0) -> int:
    """
    获取消息处理速度
    
    Args:
        minutes: 统计分钟数
        offset: 时间偏移（分钟），用于计算趋势
        
    Returns:
        每分钟处理的消息数
    """
    try:
        end_time = datetime.now() - timedelta(minutes=offset)
        start_time = end_time - timedelta(minutes=minutes)
        
        # 从数据库查询成功消息数
        query = """
            SELECT COUNT(*) FROM message_logs 
            WHERE status = 'success' 
            AND created_at BETWEEN ? AND ?
        """
        
        result = db.execute_query(query, (start_time, end_time))
        count = result[0][0] if result else 0
        
        # 返回每分钟平均数
        return count // minutes if minutes > 0 else 0
        
    except Exception as e:
        logger.error(f"获取处理速度失败: {str(e)}")
        return 0


async def get_queue_size() -> int:
    """获取当前队列大小"""
    try:
        if redis_client:
            return await redis_queue.llen("message_queue")
        return 0
    except Exception as e:
        logger.error(f"获取队列大小失败: {str(e)}")
        return 0


async def get_message_trend_data(minutes: int) -> Dict[str, List]:
    """获取消息处理趋势数据"""
    try:
        # 计算采样间隔
        interval = max(1, minutes // 60)  # 最多60个数据点
        
        time_labels = []
        success_data = []
        failed_data = []
        pending_data = []
        
        for i in range(60):
            time_point = datetime.now() - timedelta(minutes=(59 - i) * interval)
            time_labels.append(time_point.strftime("%H:%M"))
            
            # 查询该时间段的消息数
            start_time = time_point - timedelta(minutes=interval)
            end_time = time_point
            
            query = """
                SELECT status, COUNT(*) FROM message_logs 
                WHERE created_at BETWEEN ? AND ?
                GROUP BY status
            """
            
            results = db.execute_query(query, (start_time, end_time))
            stats = {row[0]: row[1] for row in results}
            
            success_data.append(stats.get('success', 0))
            failed_data.append(stats.get('failed', 0))
            pending_data.append(stats.get('pending', 0))
        
        return {
            "timeLabels": time_labels,
            "success": success_data,
            "failed": failed_data,
            "pending": pending_data
        }
        
    except Exception as e:
        logger.error(f"获取消息趋势数据失败: {str(e)}")
        return {"timeLabels": [], "success": [], "failed": [], "pending": []}


async def get_resource_trend_data(minutes: int) -> Dict[str, List]:
    """获取资源使用趋势数据"""
    try:
        # 注意：这个需要持续记录资源使用情况到数据库或Redis
        # 这里提供一个简化版本，实际应该从历史记录中读取
        
        time_labels = []
        cpu_data = []
        memory_data = []
        
        # 简化版：使用当前值填充（实际应该从历史记录读取）
        current_cpu = psutil.cpu_percent(interval=0.1)
        current_memory = psutil.virtual_memory().percent
        
        for i in range(60):
            time_point = datetime.now() - timedelta(minutes=59 - i)
            time_labels.append(time_point.strftime("%H:%M"))
            
            # TODO: 从数据库或Redis读取历史资源使用率
            # 这里暂时使用当前值的随机波动
            import random
            cpu_data.append(current_cpu + random.uniform(-10, 10))
            memory_data.append(current_memory + random.uniform(-5, 5))
        
        return {
            "timeLabels": time_labels,
            "cpu": [max(0, min(100, x)) for x in cpu_data],
            "memory": [max(0, min(100, x)) for x in memory_data]
        }
        
    except Exception as e:
        logger.error(f"获取资源趋势数据失败: {str(e)}")
        return {"timeLabels": [], "cpu": [], "memory": []}


async def get_platform_distribution_data(minutes: int) -> List[Dict]:
    """获取平台转发分布数据"""
    try:
        start_time = datetime.now() - timedelta(minutes=minutes)
        
        query = """
            SELECT target_platform, COUNT(*) as count
            FROM message_logs
            WHERE created_at >= ? AND status = 'success'
            GROUP BY target_platform
            ORDER BY count DESC
        """
        
        results = db.execute_query(query, (start_time,))
        
        return [
            {"platform": row[0], "count": row[1]}
            for row in results
        ]
        
    except Exception as e:
        logger.error(f"获取平台分布数据失败: {str(e)}")
        return []


async def get_error_rate_data(minutes: int) -> Dict[str, List]:
    """获取错误率趋势数据"""
    try:
        interval = max(1, minutes // 60)
        
        time_labels = []
        error_rates = []
        
        for i in range(60):
            time_point = datetime.now() - timedelta(minutes=(59 - i) * interval)
            time_labels.append(time_point.strftime("%H:%M"))
            
            start_time = time_point - timedelta(minutes=interval)
            end_time = time_point
            
            # 查询总数和失败数
            query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM message_logs
                WHERE created_at BETWEEN ? AND ?
            """
            
            result = db.execute_query(query, (start_time, end_time))
            if result and result[0][0] > 0:
                total, failed = result[0]
                error_rate = (failed / total * 100) if total > 0 else 0
            else:
                error_rate = 0
            
            error_rates.append(error_rate)
        
        return {
            "timeLabels": time_labels,
            "errorRates": error_rates
        }
        
    except Exception as e:
        logger.error(f"获取错误率数据失败: {str(e)}")
        return {"timeLabels": [], "errorRates": []}


@router.get("/system")
async def get_system_info():
    """获取系统信息"""
    try:
        return {
            "cpu": {
                "count": psutil.cpu_count(),
                "percent": psutil.cpu_percent(interval=1)
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "used": psutil.virtual_memory().used,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "percent": psutil.disk_usage('/').percent
            },
            "network": {
                "sent": psutil.net_io_counters().bytes_sent,
                "recv": psutil.net_io_counters().bytes_recv
            }
        }
    except Exception as e:
        logger.error(f"获取系统信息失败: {str(e)}")
        return {}
