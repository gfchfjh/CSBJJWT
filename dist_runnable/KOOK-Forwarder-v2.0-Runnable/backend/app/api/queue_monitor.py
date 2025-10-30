"""
队列可视化监控API
实时查看Redis队列状态、手动干预队列
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import redis
import json
from datetime import datetime
from ..config import settings
from ..utils.logger import logger

router = APIRouter(prefix="/api/queue", tags=["队列监控"])

# Redis连接
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)


class QueueStats(BaseModel):
    """队列统计"""
    total_size: int
    pending: int
    processing: int
    failed: int
    completed_today: int
    avg_processing_time: float


class QueueMessage(BaseModel):
    """队列消息"""
    id: str
    kook_message_id: str
    channel_name: str
    target_platform: str
    content_preview: str
    status: str
    retry_count: int
    created_at: str
    priority: int


@router.get("/stats", response_model=QueueStats)
async def get_queue_stats():
    """
    获取队列统计信息
    
    实时返回队列状态
    """
    try:
        # 获取各队列大小
        pending = redis_client.llen("queue:pending")
        processing = redis_client.llen("queue:processing")
        failed = redis_client.llen("queue:failed")
        
        # 获取今日完成数
        today = datetime.now().strftime("%Y-%m-%d")
        completed_key = f"stats:completed:{today}"
        completed_today = int(redis_client.get(completed_key) or 0)
        
        # 计算平均处理时间
        avg_time_key = "stats:avg_processing_time"
        avg_time = float(redis_client.get(avg_time_key) or 0.0)
        
        return QueueStats(
            total_size=pending + processing + failed,
            pending=pending,
            processing=processing,
            failed=failed,
            completed_today=completed_today,
            avg_processing_time=avg_time
        )
    
    except Exception as e:
        logger.error(f"获取队列统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages", response_model=List[QueueMessage])
async def get_queue_messages(
    queue_type: str = "pending",
    offset: int = 0,
    limit: int = 50
):
    """
    获取队列消息列表
    
    Args:
        queue_type: 队列类型 (pending/processing/failed)
        offset: 偏移量
        limit: 返回数量
    """
    try:
        queue_key = f"queue:{queue_type}"
        
        # 获取消息ID列表
        message_ids = redis_client.lrange(queue_key, offset, offset + limit - 1)
        
        messages = []
        for msg_id in message_ids:
            # 获取消息详情
            msg_data = redis_client.hgetall(f"message:{msg_id}")
            
            if msg_data:
                messages.append(QueueMessage(
                    id=msg_id,
                    kook_message_id=msg_data.get('kook_message_id', ''),
                    channel_name=msg_data.get('channel_name', ''),
                    target_platform=msg_data.get('target_platform', ''),
                    content_preview=msg_data.get('content', '')[:100],
                    status=queue_type,
                    retry_count=int(msg_data.get('retry_count', 0)),
                    created_at=msg_data.get('created_at', ''),
                    priority=int(msg_data.get('priority', 0))
                ))
        
        return messages
    
    except Exception as e:
        logger.error(f"获取队列消息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retry/{message_id}")
async def retry_message(message_id: str):
    """
    手动重试失败的消息
    """
    try:
        # 从失败队列移除
        redis_client.lrem("queue:failed", 1, message_id)
        
        # 添加到待处理队列
        redis_client.rpush("queue:pending", message_id)
        
        # 重置重试计数
        redis_client.hset(f"message:{message_id}", "retry_count", 0)
        
        logger.info(f"消息 {message_id} 已重新加入队列")
        
        return {"success": True, "message": "消息已重新加入队列"}
    
    except Exception as e:
        logger.error(f"重试消息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/{queue_type}")
async def clear_queue(queue_type: str):
    """
    清空指定队列
    
    Args:
        queue_type: 队列类型 (pending/processing/failed)
    """
    try:
        queue_key = f"queue:{queue_type}"
        
        # 获取所有消息ID
        message_ids = redis_client.lrange(queue_key, 0, -1)
        
        # 删除消息数据
        for msg_id in message_ids:
            redis_client.delete(f"message:{msg_id}")
        
        # 清空队列
        redis_client.delete(queue_key)
        
        logger.warning(f"队列 {queue_type} 已清空，删除了 {len(message_ids)} 条消息")
        
        return {
            "success": True,
            "deleted_count": len(message_ids)
        }
    
    except Exception as e:
        logger.error(f"清空队列失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/priority/{message_id}")
async def set_message_priority(message_id: str, priority: int):
    """
    设置消息优先级
    
    Args:
        message_id: 消息ID
        priority: 优先级 (数字越大优先级越高)
    """
    try:
        redis_client.hset(f"message:{message_id}", "priority", priority)
        
        # TODO: 重新排序队列（按优先级）
        
        return {"success": True, "priority": priority}
    
    except Exception as e:
        logger.error(f"设置优先级失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_queue_health():
    """
    检查队列健康状态
    """
    try:
        # 检查Redis连接
        redis_client.ping()
        
        # 获取队列大小
        stats = await get_queue_stats()
        
        # 判断健康状态
        health_status = "healthy"
        warnings = []
        
        if stats.pending > 1000:
            health_status = "warning"
            warnings.append("待处理队列积压严重")
        
        if stats.failed > 100:
            health_status = "warning"
            warnings.append("失败消息过多")
        
        if stats.processing > 50:
            health_status = "warning"
            warnings.append("处理中消息过多，可能有阻塞")
        
        return {
            "status": health_status,
            "redis_connected": True,
            "warnings": warnings,
            "stats": stats
        }
    
    except Exception as e:
        logger.error(f"队列健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "redis_connected": False,
            "error": str(e)
        }
