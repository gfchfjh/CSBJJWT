"""
WebSocket API
提供实时通信功能：验证码处理、系统状态推送等
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json
from ..utils.logger import logger
from ..database import db

router = APIRouter()

# 存储所有活跃的WebSocket连接
active_connections: Set[WebSocket] = set()


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "system": set(),  # 系统状态推送
            "captcha": set(),  # 验证码处理
            "logs": set(),     # 日志推送
        }
    
    async def connect(self, websocket: WebSocket, channel: str = "system"):
        """连接客户端"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket客户端连接: channel={channel}, total={len(self.active_connections[channel])}")
    
    def disconnect(self, websocket: WebSocket, channel: str = "system"):
        """断开客户端"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            logger.info(f"WebSocket客户端断开: channel={channel}, total={len(self.active_connections[channel])}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {str(e)}")
    
    async def broadcast(self, message: dict, channel: str = "system"):
        """广播消息到指定频道"""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败: {str(e)}")
                disconnected.add(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.active_connections[channel].discard(connection)


# 创建全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/system")
async def websocket_system(websocket: WebSocket):
    """
    系统状态WebSocket
    用于推送系统状态、统计数据等
    """
    await manager.connect(websocket, "system")
    try:
        while True:
            # 等待客户端消息（心跳）
            data = await websocket.receive_text()
            
            # 响应心跳
            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "system")
    except Exception as e:
        logger.error(f"WebSocket系统频道异常: {str(e)}")
        manager.disconnect(websocket, "system")


@router.websocket("/ws/captcha")
async def websocket_captcha(websocket: WebSocket):
    """
    验证码处理WebSocket
    用于实时推送验证码请求和接收用户输入
    """
    await manager.connect(websocket, "captcha")
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
            
            elif message_type == "captcha_input":
                # 用户提交验证码
                account_id = data.get("account_id")
                captcha_code = data.get("code")
                
                if account_id and captcha_code:
                    # 存储到数据库，让scraper读取
                    db.set_system_config(
                        f"captcha_input_{account_id}",
                        json.dumps({
                            "code": captcha_code,
                            "timestamp": asyncio.get_event_loop().time()
                        })
                    )
                    
                    await manager.send_personal_message({
                        "type": "captcha_received",
                        "account_id": account_id,
                        "status": "success"
                    }, websocket)
                    
                    logger.info(f"收到验证码输入: account_id={account_id}")
            
            elif message_type == "check_captcha":
                # 检查是否有验证码请求
                account_id = data.get("account_id")
                
                if account_id:
                    captcha_data = db.get_system_config(f"captcha_required_{account_id}")
                    
                    if captcha_data:
                        try:
                            captcha_info = json.loads(captcha_data)
                            await manager.send_personal_message({
                                "type": "captcha_required",
                                "account_id": account_id,
                                "image_url": captcha_info.get("image_url"),
                                "timestamp": captcha_info.get("timestamp")
                            }, websocket)
                        except:
                            pass
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, "captcha")
    except Exception as e:
        logger.error(f"WebSocket验证码频道异常: {str(e)}")
        manager.disconnect(websocket, "captcha")


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    日志推送WebSocket
    用于实时推送消息转发日志
    """
    await manager.connect(websocket, "logs")
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, "logs")
    except Exception as e:
        logger.error(f"WebSocket日志频道异常: {str(e)}")
        manager.disconnect(websocket, "logs")


# 工具函数：供其他模块调用

async def push_captcha_request(account_id: int, image_url: str):
    """
    推送验证码请求到前端
    
    Args:
        account_id: 账号ID
        image_url: 验证码图片URL
    """
    await manager.broadcast({
        "type": "captcha_required",
        "account_id": account_id,
        "image_url": image_url,
        "timestamp": asyncio.get_event_loop().time()
    }, "captcha")


async def push_log_message(log_data: dict):
    """
    推送日志消息到前端
    
    Args:
        log_data: 日志数据
    """
    await manager.broadcast({
        "type": "log_message",
        "data": log_data
    }, "logs")


async def push_system_status(status_data: dict):
    """
    推送系统状态到前端
    
    Args:
        status_data: 状态数据
    """
    await manager.broadcast({
        "type": "system_status",
        "data": status_data
    }, "system")


async def push_account_status(account_id: int, status: str):
    """
    推送账号状态变化
    
    Args:
        account_id: 账号ID
        status: 状态（online/offline）
    """
    await manager.broadcast({
        "type": "account_status",
        "account_id": account_id,
        "status": status
    }, "system")
