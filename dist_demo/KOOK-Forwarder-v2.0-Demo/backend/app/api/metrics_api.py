"""
Prometheus指标API端点
"""
from fastapi import APIRouter, Response
from ..utils.metrics import get_metrics, metrics, MetricsCollector
from ..config import settings

router = APIRouter(prefix="/api/metrics", tags=["监控"])


@router.get("/prometheus")
async def prometheus_metrics():
    """
    Prometheus指标端点
    
    返回Prometheus文本格式的所有指标数据
    用于Prometheus服务器抓取
    """
    # 设置应用信息
    MetricsCollector.set_app_info(
        version=settings.app_version,
        environment='production' if not settings.debug else 'development'
    )
    
    metrics_data = get_metrics()
    
    return Response(
        content=metrics_data,
        media_type="text/plain; charset=utf-8"
    )


@router.get("/stats")
async def get_stats():
    """
    获取JSON格式的统计信息（用于前端展示）
    
    Returns:
        统计信息字典
    """
    from ..queue.redis_client import redis_queue
    from ..database import db
    
    # 获取队列大小
    try:
        queue_len = await redis_queue.get_queue_length()
    except:
        queue_len = 0
    
    # 获取账号统计
    accounts = db.get_accounts()
    active_account_count = len([a for a in accounts if a.get('status') == 'online'])
    
    # 获取Bot统计
    all_bots = db.get_bot_configs()
    bot_stats = {}
    for platform in ['discord', 'telegram', 'feishu']:
        bot_stats[platform] = len([b for b in all_bots if b.get('platform') == platform])
    
    return {
        'queue_size': queue_len,
        'active_accounts': active_account_count,
        'total_accounts': len(accounts),
        'active_bots': bot_stats,
        'version': settings.app_version
    }
