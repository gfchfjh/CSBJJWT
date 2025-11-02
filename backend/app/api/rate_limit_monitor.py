"""
✅ P0-5深度优化：限流监控API

功能：
- 实时限流状态查询
- WebSocket推送限流信息
- 队列大小统计
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
import asyncio
from ..utils.rate_limiter import rate_limiter_manager
from ..utils.logger import logger
from ..queue.redis_client import redis_queue

router = APIRouter(prefix="/api/rate-limit", tags=["rate-limit"])


@router.get("/status")
async def get_rate_limit_status():
    """
    获取当前限流状态
    
    Returns:
        各平台的限流状态
    """
    try:
        status = {}
        
        platforms = ['discord', 'telegram', 'feishu']
        
        for platform in platforms:
            try:
                limiter = rate_limiter_manager.get_limiter(
                    platform,
                    calls=5 if platform == 'discord' else 30,
                    period=5 if platform == 'discord' else 1
                )
                
                # 获取限流状态（需要RateLimiter支持get_status方法）
                limiter_status = getattr(limiter, 'get_status', lambda: {
                    'is_limited': False,
                    'queue_size': 0,
                    'wait_time': 0,
                    'progress': 0
                })()
                
                status[platform] = {
                    'is_limited': limiter_status.get('is_limited', False),
                    'queue_size': limiter_status.get('queue_size', 0),
                    'wait_time': limiter_status.get('wait_time', 0),
                    'progress': limiter_status.get('progress', 0)
                }
                
            except Exception as e:
                logger.error(f"获取{platform}限流状态失败: {str(e)}")
                status[platform] = {
                    'is_limited': False,
                    'queue_size': 0,
                    'wait_time': 0,
                    'progress': 0,
                    'error': str(e)
                }
        
        # 获取Redis队列大小
        try:
            queue_size = await redis_queue.size()
        except:
            queue_size = 0
        
        return {
            'platforms': status,
            'total_queue_size': queue_size,
            'timestamp': asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"获取限流状态失败: {str(e)}")
        return {
            'platforms': {},
            'total_queue_size': 0,
            'error': str(e)
        }


# WebSocket连接管理
active_websockets = []


@router.websocket("/ws")
async def rate_limit_websocket(websocket: WebSocket):
    """
    限流状态WebSocket推送
    
    定时推送限流状态（每2秒）
    """
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        logger.info("限流监控WebSocket已连接")
        
        # 定时推送
        while True:
            try:
                # 获取最新状态
                status = await get_rate_limit_status()
                
                # 发送到客户端
                await websocket.send_json({
                    'type': 'rate_limit_status',
                    'data': status
                })
                
                # 等待2秒
                await asyncio.sleep(2)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"限流WebSocket推送失败: {str(e)}")
                await asyncio.sleep(2)
                
    except Exception as e:
        logger.error(f"限流WebSocket异常: {str(e)}")
    finally:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
        logger.info("限流监控WebSocket已断开")
