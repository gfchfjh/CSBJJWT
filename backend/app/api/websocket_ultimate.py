"""
WebSocket实时推送API（终极版）
============================
功能：
1. 实时统计数据推送
2. 实时日志推送
3. 系统状态推送
4. 连接管理
5. 心跳保持

作者：KOOK Forwarder Team
日期：2025-10-25
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Set
import asyncio
import json
from datetime import datetime
from ..utils.logger import logger


router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 不同类型的连接
        self.stats_connections: Set[WebSocket] = set()
        self.logs_connections: Set[WebSocket] = set()
        self.status_connections: Set[WebSocket] = set()
        
        # 心跳任务
        self.heartbeat_task = None
        
    async def connect(self, websocket: WebSocket, connection_type: str):
        """连接WebSocket"""
        await websocket.accept()
        
        if connection_type == 'stats':
            self.stats_connections.add(websocket)
            logger.info(f"新统计连接 (总计: {len(self.stats_connections)})")
        elif connection_type == 'logs':
            self.logs_connections.add(websocket)
            logger.info(f"新日志连接 (总计: {len(self.logs_connections)})")
        elif connection_type == 'status':
            self.status_connections.add(websocket)
            logger.info(f"新状态连接 (总计: {len(self.status_connections)})")
        
        # 启动心跳任务（如果还未启动）
        if not self.heartbeat_task:
            self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
    
    def disconnect(self, websocket: WebSocket, connection_type: str):
        """断开WebSocket"""
        if connection_type == 'stats':
            self.stats_connections.discard(websocket)
            logger.info(f"统计连接断开 (剩余: {len(self.stats_connections)})")
        elif connection_type == 'logs':
            self.logs_connections.discard(websocket)
            logger.info(f"日志连接断开 (剩余: {len(self.logs_connections)})")
        elif connection_type == 'status':
            self.status_connections.discard(websocket)
            logger.info(f"状态连接断开 (剩余: {len(self.status_connections)})")
    
    async def broadcast_stats(self, data: dict):
        """广播统计数据"""
        await self._broadcast(self.stats_connections, data)
    
    async def broadcast_log(self, data: dict):
        """广播日志"""
        await self._broadcast(self.logs_connections, data)
    
    async def broadcast_status(self, data: dict):
        """广播状态"""
        await self._broadcast(self.status_connections, data)
    
    async def _broadcast(self, connections: Set[WebSocket], data: dict):
        """广播数据到所有连接"""
        if not connections:
            return
        
        message = json.dumps(data, ensure_ascii=False)
        dead_connections = set()
        
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"发送WebSocket消息失败: {e}")
                dead_connections.add(connection)
        
        # 移除死连接
        for connection in dead_connections:
            connections.discard(connection)
    
    async def heartbeat_loop(self):
        """心跳循环（每30秒）"""
        while True:
            try:
                await asyncio.sleep(30)
                
                # 发送心跳到所有连接
                heartbeat = {
                    'type': 'heartbeat',
                    'timestamp': datetime.now().isoformat()
                }
                
                await self._broadcast(self.stats_connections, heartbeat)
                await self._broadcast(self.logs_connections, heartbeat)
                await self._broadcast(self.status_connections, heartbeat)
                
            except Exception as e:
                logger.error(f"心跳循环异常: {e}")


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/stats")
async def websocket_stats(websocket: WebSocket):
    """实时统计数据WebSocket"""
    await manager.connect(websocket, 'stats')
    
    try:
        # 立即发送当前统计数据
        from ..database import db
        
        stats = {
            'type': 'stats',
            'data': {
                'total_messages': len(db.get_message_logs(limit=100000)),
                'success_count': len(db.get_message_logs(limit=100000, status='success')),
                'failed_count': len(db.get_message_logs(limit=100000, status='failed')),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        await websocket.send_text(json.dumps(stats, ensure_ascii=False))
        
        # 保持连接
        while True:
            # 等待客户端消息（用于检测连接状态）
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'stats')
    except Exception as e:
        logger.error(f"WebSocket异常: {e}")
        manager.disconnect(websocket, 'stats')


@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    """实时日志WebSocket"""
    await manager.connect(websocket, 'logs')
    
    try:
        # 保持连接
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'logs')
    except Exception as e:
        logger.error(f"WebSocket异常: {e}")
        manager.disconnect(websocket, 'logs')


@router.websocket("/status")
async def websocket_status(websocket: WebSocket):
    """实时系统状态WebSocket"""
    await manager.connect(websocket, 'status')
    
    try:
        # 立即发送当前状态
        import psutil
        
        status = {
            'type': 'status',
            'data': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        await websocket.send_text(json.dumps(status, ensure_ascii=False))
        
        # 保持连接
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'status')
    except Exception as e:
        logger.error(f"WebSocket异常: {e}")
        manager.disconnect(websocket, 'status')


# 导出管理器供其他模块使用
__all__ = ['manager', 'router']
