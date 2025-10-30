"""
Cookie导入WebSocket - 实时通信支持
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from ..utils.logger import logger

router = APIRouter()

# 存储活跃的WebSocket连接
active_connections: Set[WebSocket] = set()
# 存储等待Cookie导入的会话
pending_imports: Dict[str, dict] = {}


@router.websocket("/ws/cookie-import")
async def cookie_import_websocket(websocket: WebSocket):
    """
    Cookie导入WebSocket端点
    
    用于实现扩展与主程序的实时通信
    """
    await websocket.accept()
    active_connections.add(websocket)
    
    logger.info(f"WebSocket连接已建立，当前连接数: {len(active_connections)}")
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.debug(f"收到WebSocket消息: {message.get('type')}")
            
            # 处理不同类型的消息
            if message.get('type') == 'ping':
                await websocket.send_text(json.dumps({
                    'type': 'pong',
                    'timestamp': message.get('timestamp')
                }))
            
            elif message.get('type') == 'waiting':
                # 客户端表示正在等待Cookie导入
                session_id = message.get('session_id', 'default')
                pending_imports[session_id] = {
                    'websocket': websocket,
                    'started_at': asyncio.get_event_loop().time()
                }
                
                await websocket.send_text(json.dumps({
                    'type': 'waiting_confirmed',
                    'session_id': session_id
                }))
            
    except WebSocketDisconnect:
        logger.info("WebSocket连接已断开")
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
    finally:
        active_connections.discard(websocket)
        # 清理pending_imports
        for session_id in list(pending_imports.keys()):
            if pending_imports[session_id]['websocket'] == websocket:
                del pending_imports[session_id]


async def broadcast_cookie_import_success(account_data: dict):
    """
    广播Cookie导入成功消息到所有连接的客户端
    
    Args:
        account_data: 账号数据
    """
    message = json.dumps({
        'type': 'cookie_imported',
        'success': True,
        'account': {
            'id': account_data.get('id'),
            'email': account_data.get('email')
        },
        'timestamp': asyncio.get_event_loop().time()
    })
    
    # 发送到所有活跃连接
    disconnected = set()
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            disconnected.add(connection)
    
    # 清理断开的连接
    active_connections.difference_update(disconnected)
    
    logger.info(f"Cookie导入成功消息已广播到 {len(active_connections)} 个客户端")


async def broadcast_cookie_import_error(error_message: str):
    """
    广播Cookie导入失败消息
    
    Args:
        error_message: 错误信息
    """
    message = json.dumps({
        'type': 'cookie_imported',
        'success': False,
        'message': error_message,
        'timestamp': asyncio.get_event_loop().time()
    })
    
    disconnected = set()
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            logger.error(f"发送错误消息失败: {str(e)}")
            disconnected.add(connection)
    
    active_connections.difference_update(disconnected)


# 导出广播函数供其他模块使用
__all__ = ['router', 'broadcast_cookie_import_success', 'broadcast_cookie_import_error']
