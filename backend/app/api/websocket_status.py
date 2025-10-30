"""
WebSocket状态广播
✅ P0-32: 实时状态推送、多客户端同步、断线重连
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set, List
import asyncio
import json
from datetime import datetime
from ..utils.logger import logger

router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接
        self.active_connections: Dict[str, Set[WebSocket]] = {
            'status': set(),       # 系统状态
            'logs': set(),         # 实时日志
            'performance': set(),  # 性能指标
            'accounts': set()      # 账号状态
        }
        
        # 连接统计
        self.stats = {
            'total_connections': 0,
            'current_connections': 0,
            'disconnections': 0
        }
        
        # 广播任务
        self.broadcast_task = None
        self._running = False
    
    async def connect(self, websocket: WebSocket, channel: str = 'status'):
        """连接WebSocket"""
        await websocket.accept()
        
        if channel not in self.active_connections:
            channel = 'status'
        
        self.active_connections[channel].add(websocket)
        
        self.stats['total_connections'] += 1
        self.stats['current_connections'] = self._get_total_connections()
        
        logger.info(f"WebSocket连接: channel={channel}, 当前连接数={self.stats['current_connections']}")
        
        # 发送欢迎消息
        await self.send_personal(websocket, {
            'type': 'connected',
            'channel': channel,
            'message': '连接成功',
            'timestamp': datetime.now().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket, channel: str = 'status'):
        """断开WebSocket"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
        
        self.stats['disconnections'] += 1
        self.stats['current_connections'] = self._get_total_connections()
        
        logger.info(f"WebSocket断开: channel={channel}, 当前连接数={self.stats['current_connections']}")
    
    async def send_personal(self, websocket: WebSocket, data: dict):
        """发送个人消息"""
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"发送个人消息失败: {str(e)}")
    
    async def broadcast(self, channel: str, data: dict):
        """广播消息到指定频道"""
        if channel not in self.active_connections:
            return
        
        # 添加时间戳
        data['timestamp'] = datetime.now().isoformat()
        
        # 断开的连接列表
        disconnected = []
        
        # 广播
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"广播消息失败: {str(e)}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.active_connections[channel].discard(connection)
    
    async def broadcast_all(self, data: dict):
        """广播消息到所有频道"""
        for channel in self.active_connections.keys():
            await self.broadcast(channel, data.copy())
    
    def _get_total_connections(self) -> int:
        """获取总连接数"""
        return sum(len(conns) for conns in self.active_connections.values())
    
    async def start_broadcast_loop(self):
        """启动定时广播循环"""
        self._running = True
        self.broadcast_task = asyncio.create_task(self._broadcast_loop())
        logger.info("WebSocket广播循环已启动")
    
    async def stop_broadcast_loop(self):
        """停止广播循环"""
        self._running = False
        if self.broadcast_task:
            self.broadcast_task.cancel()
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass
        logger.info("WebSocket广播循环已停止")
    
    async def _broadcast_loop(self):
        """广播循环"""
        try:
            while self._running:
                # 每5秒广播一次系统状态
                await self._broadcast_system_status()
                await asyncio.sleep(5)
                
        except asyncio.CancelledError:
            logger.info("广播循环已取消")
        except Exception as e:
            logger.error(f"广播循环异常: {str(e)}")
    
    async def _broadcast_system_status(self):
        """广播系统状态"""
        from ..core.multi_account_manager import multi_account_manager
        from ..queue.redis_queue_optimized import redis_queue_optimized
        
        try:
            # 获取账号状态
            account_stats = multi_account_manager.get_stats()
            
            # 获取队列状态
            queue_lengths = await redis_queue_optimized.get_queue_lengths()
            
            # 广播状态
            await self.broadcast('status', {
                'type': 'system_status',
                'accounts': account_stats,
                'queue': queue_lengths
            })
            
        except Exception as e:
            logger.error(f"广播系统状态失败: {str(e)}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'channels': {
                channel: len(conns)
                for channel, conns in self.active_connections.items()
            }
        }


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/status")
async def websocket_status(websocket: WebSocket):
    """系统状态WebSocket"""
    await manager.connect(websocket, 'status')
    
    try:
        while True:
            # 接收消息（保持连接）
            data = await websocket.receive_text()
            
            # 处理心跳
            if data == 'ping':
                await manager.send_personal(websocket, {'type': 'pong'})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'status')
    except Exception as e:
        logger.error(f"WebSocket异常: {str(e)}")
        manager.disconnect(websocket, 'status')


@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    """实时日志WebSocket"""
    await manager.connect(websocket, 'logs')
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == 'ping':
                await manager.send_personal(websocket, {'type': 'pong'})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'logs')
    except Exception as e:
        logger.error(f"WebSocket异常: {str(e)}")
        manager.disconnect(websocket, 'logs')


@router.websocket("/performance")
async def websocket_performance(websocket: WebSocket):
    """性能指标WebSocket"""
    await manager.connect(websocket, 'performance')
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == 'ping':
                await manager.send_personal(websocket, {'type': 'pong'})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'performance')
    except Exception as e:
        logger.error(f"WebSocket异常: {str(e)}")
        manager.disconnect(websocket, 'performance')


@router.websocket("/accounts")
async def websocket_accounts(websocket: WebSocket):
    """账号状态WebSocket"""
    await manager.connect(websocket, 'accounts')
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == 'ping':
                await manager.send_personal(websocket, {'type': 'pong'})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, 'accounts')
    except Exception as e:
        logger.error(f"WebSocket异常: {str(e)}")
        manager.disconnect(websocket, 'accounts')


# 便捷广播函数
async def broadcast_log(log_data: dict):
    """广播日志"""
    await manager.broadcast('logs', {
        'type': 'log',
        'data': log_data
    })


async def broadcast_account_status(account_id: int, status: dict):
    """广播账号状态"""
    await manager.broadcast('accounts', {
        'type': 'account_status',
        'account_id': account_id,
        'status': status
    })


async def broadcast_performance_metric(metric_data: dict):
    """广播性能指标"""
    await manager.broadcast('performance', {
        'type': 'performance_metric',
        'data': metric_data
    })


async def broadcast_system_alert(alert_data: dict):
    """广播系统告警"""
    await manager.broadcast_all({
        'type': 'system_alert',
        'data': alert_data
    })
