"""
系统状态WebSocket推送
✅ P0-6优化: 实时推送账号和服务状态
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set, Dict, Any
import asyncio
import json
from datetime import datetime
from ..database import db
from ..utils.logger import logger


router = APIRouter()

# 存储所有WebSocket连接
active_connections: Set[WebSocket] = set()

# 状态缓存
status_cache = {
    'accounts': [],
    'services': {},
    'statistics': {},
    'last_update': None
}


class SystemStatusManager:
    """系统状态管理器"""
    
    def __init__(self):
        self.update_interval = 1  # 更新间隔（秒）
        self.update_task = None
    
    async def connect(self, websocket: WebSocket):
        """新客户端连接"""
        await websocket.accept()
        active_connections.add(websocket)
        logger.info(f"WebSocket客户端已连接，当前连接数: {len(active_connections)}")
        
        # 立即发送当前状态
        try:
            current_status = await self.get_current_status()
            await websocket.send_json(current_status)
        except Exception as e:
            logger.error(f"发送初始状态失败: {str(e)}")
    
    def disconnect(self, websocket: WebSocket):
        """客户端断开连接"""
        active_connections.discard(websocket)
        logger.info(f"WebSocket客户端已断开，当前连接数: {len(active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """广播消息到所有客户端"""
        if not active_connections:
            return
        
        disconnected = set()
        
        for connection in active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: {str(e)}")
                disconnected.add(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            active_connections.discard(conn)
    
    async def start_auto_update(self):
        """启动自动更新任务"""
        if self.update_task is not None:
            return
        
        self.update_task = asyncio.create_task(self._auto_update_loop())
        logger.info("✅ 系统状态自动更新已启动")
    
    async def stop_auto_update(self):
        """停止自动更新任务"""
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
            self.update_task = None
            logger.info("⏹️ 系统状态自动更新已停止")
    
    async def _auto_update_loop(self):
        """自动更新循环"""
        while True:
            try:
                if active_connections:
                    status = await self.get_current_status()
                    await self.broadcast(status)
                
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"自动更新异常: {str(e)}")
                await asyncio.sleep(5)
    
    async def get_current_status(self) -> Dict[str, Any]:
        """获取当前系统状态"""
        try:
            # 获取账号状态
            accounts = await self.get_accounts_status()
            
            # 获取服务状态
            services = await self.get_services_status()
            
            # 获取统计信息
            statistics = await self.get_statistics()
            
            status = {
                'type': 'status_update',
                'timestamp': datetime.now().isoformat(),
                'accounts': accounts,
                'services': services,
                'statistics': statistics
            }
            
            # 更新缓存
            global status_cache
            status_cache = status.copy()
            status_cache['last_update'] = datetime.now()
            
            return status
            
        except Exception as e:
            logger.error(f"获取系统状态失败: {str(e)}")
            return {
                'type': 'error',
                'message': f"获取状态失败: {str(e)}"
            }
    
    async def get_accounts_status(self) -> list:
        """获取所有账号状态"""
        try:
            accounts = await db.get_all_accounts()
            
            result = []
            for acc in accounts:
                result.append({
                    'id': acc['id'],
                    'email': acc['email'],
                    'status': acc.get('status', 'offline'),  # online/offline/reconnecting
                    'last_active': acc.get('last_active', ''),
                    'reconnect_count': acc.get('reconnect_count', 0),
                    'error_message': acc.get('error_message', '')
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取账号状态失败: {str(e)}")
            return []
    
    async def get_services_status(self) -> Dict:
        """获取服务状态"""
        services = {
            'backend': 'online',
            'redis': await self._check_redis(),
            'queue': await self._get_queue_status()
        }
        
        return services
    
    async def _check_redis(self) -> Dict:
        """检查Redis状态"""
        try:
            from ..queue.redis_client import redis_queue
            
            # 尝试ping Redis
            result = redis_queue.redis_client.ping()
            
            if result:
                # 获取Redis信息
                info = redis_queue.redis_client.info()
                
                return {
                    'status': 'online',
                    'version': info.get('redis_version', 'unknown'),
                    'memory_used': info.get('used_memory_human', 'unknown'),
                    'uptime_seconds': info.get('uptime_in_seconds', 0)
                }
            else:
                return {
                    'status': 'offline',
                    'message': 'Redis未响应'
                }
                
        except Exception as e:
            return {
                'status': 'offline',
                'message': str(e)
            }
    
    async def _get_queue_status(self) -> Dict:
        """获取队列状态"""
        try:
            from ..queue.redis_client import redis_queue
            
            # 获取队列大小
            queue_size = await redis_queue.get_queue_size()
            
            # 获取处理中的消息数
            processing = await redis_queue.get_processing_count()
            
            return {
                'size': queue_size,
                'processing': processing,
                'status': 'normal' if queue_size < 100 else 'high_load'
            }
            
        except Exception as e:
            logger.error(f"获取队列状态失败: {str(e)}")
            return {
                'size': 0,
                'processing': 0,
                'status': 'unknown'
            }
    
    async def get_statistics(self) -> Dict:
        """获取实时统计"""
        try:
            # 获取今日统计
            today_stats = await db.get_today_statistics()
            
            return {
                'today': {
                    'total_messages': today_stats.get('total', 0),
                    'success': today_stats.get('success', 0),
                    'failed': today_stats.get('failed', 0),
                    'success_rate': today_stats.get('success_rate', 0),
                    'avg_latency': today_stats.get('avg_latency', 0)
                },
                'realtime': {
                    'messages_per_minute': await self._get_messages_per_minute(),
                    'active_bots': await self._get_active_bots_count()
                }
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {
                'today': {},
                'realtime': {}
            }
    
    async def _get_messages_per_minute(self) -> int:
        """获取每分钟消息数"""
        try:
            # 查询最近1分钟的消息数
            count = await db.count_messages_in_last_minutes(1)
            return count
        except:
            return 0
    
    async def _get_active_bots_count(self) -> int:
        """获取活跃Bot数量"""
        try:
            bots = await db.get_all_bots()
            active = [b for b in bots if b.get('status') == 'active']
            return len(active)
        except:
            return 0
    
    async def broadcast_account_status(self, account_id: int, status: str, message: str = ''):
        """广播账号状态变化"""
        update = {
            'type': 'account_status_change',
            'timestamp': datetime.now().isoformat(),
            'account_id': account_id,
            'status': status,
            'message': message
        }
        
        await self.broadcast(update)
    
    async def broadcast_notification(self, title: str, message: str, type: str = 'info'):
        """广播通知消息"""
        notification = {
            'type': 'notification',
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'message': message,
            'notification_type': type  # info/success/warning/error
        }
        
        await self.broadcast(notification)


# 全局实例
status_manager = SystemStatusManager()


@router.websocket("/ws/system-status")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点：系统状态推送"""
    await status_manager.connect(websocket)
    
    try:
        while True:
            # 等待客户端消息（用于保持连接）
            data = await websocket.receive_text()
            
            # 处理客户端请求
            try:
                request = json.loads(data)
                
                if request.get('action') == 'get_status':
                    # 客户端请求刷新状态
                    status = await status_manager.get_current_status()
                    await websocket.send_json(status)
                    
                elif request.get('action') == 'reconnect_account':
                    # 客户端请求重连账号
                    account_id = request.get('account_id')
                    # 触发重连逻辑
                    await websocket.send_json({
                        'type': 'command_received',
                        'action': 'reconnect_account',
                        'account_id': account_id
                    })
                    
            except json.JSONDecodeError:
                logger.warning(f"收到无效的JSON数据: {data}")
                
    except WebSocketDisconnect:
        status_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket异常: {str(e)}")
        status_manager.disconnect(websocket)


@router.on_event("startup")
async def startup_event():
    """启动时自动开始状态推送"""
    await status_manager.start_auto_update()


@router.on_event("shutdown")
async def shutdown_event():
    """关闭时停止状态推送"""
    await status_manager.stop_auto_update()
