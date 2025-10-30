"""
验证码WebSocket API
✅ P0-3优化：实时验证码推送（替代数据库轮询）
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json
from ..utils.logger import logger

router = APIRouter(prefix="/ws/captcha", tags=["captcha-websocket"])

# 存储WebSocket连接
# key: account_id, value: Set[WebSocket]
active_connections: Dict[int, Set[WebSocket]] = {}

# 存储待处理的验证码请求
# key: account_id, value: captcha_data
pending_captchas: Dict[int, dict] = {}


class CaptchaWebSocketManager:
    """验证码WebSocket管理器"""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.pending_responses: Dict[int, asyncio.Future] = {}
        logger.info("✅ 验证码WebSocket管理器已初始化")
    
    async def connect(self, account_id: int, websocket: WebSocket):
        """
        连接WebSocket
        
        Args:
            account_id: 账号ID
            websocket: WebSocket连接
        """
        await websocket.accept()
        
        if account_id not in self.active_connections:
            self.active_connections[account_id] = set()
        
        self.active_connections[account_id].add(websocket)
        logger.info(f"✅ 账号 {account_id} 的验证码WebSocket已连接")
        
        # 如果有待处理的验证码，立即发送
        if account_id in pending_captchas:
            await self.send_captcha_request(account_id, pending_captchas[account_id])
    
    def disconnect(self, account_id: int, websocket: WebSocket):
        """
        断开WebSocket
        
        Args:
            account_id: 账号ID
            websocket: WebSocket连接
        """
        if account_id in self.active_connections:
            self.active_connections[account_id].discard(websocket)
            
            # 如果该账号没有活跃连接了，清理
            if not self.active_connections[account_id]:
                del self.active_connections[account_id]
                logger.info(f"账号 {account_id} 的所有验证码WebSocket已断开")
    
    async def send_captcha_request(self, account_id: int, captcha_data: dict):
        """
        发送验证码请求到前端
        
        Args:
            account_id: 账号ID
            captcha_data: 验证码数据（包含image_url等）
        """
        if account_id not in self.active_connections:
            # 没有活跃连接，存储待处理
            pending_captchas[account_id] = captcha_data
            logger.warning(f"账号 {account_id} 没有活跃的验证码WebSocket，已存储待处理")
            return False
        
        # 发送到所有连接
        message = {
            "type": "captcha_required",
            "data": captcha_data
        }
        
        for websocket in self.active_connections[account_id].copy():
            try:
                await websocket.send_json(message)
                logger.info(f"✅ 已向账号 {account_id} 推送验证码请求")
            except Exception as e:
                logger.error(f"发送验证码请求失败: {str(e)}")
                self.disconnect(account_id, websocket)
        
        # 清除待处理的验证码
        if account_id in pending_captchas:
            del pending_captchas[account_id]
        
        return True
    
    async def wait_for_captcha_input(self, account_id: int, timeout: int = 120) -> str:
        """
        等待用户输入验证码
        
        Args:
            account_id: 账号ID
            timeout: 超时时间（秒）
            
        Returns:
            验证码字符串，超时返回None
        """
        # 创建Future等待响应
        future = asyncio.Future()
        self.pending_responses[account_id] = future
        
        try:
            # 等待响应或超时
            captcha_code = await asyncio.wait_for(future, timeout=timeout)
            logger.info(f"✅ 收到账号 {account_id} 的验证码输入: {captcha_code}")
            return captcha_code
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ 账号 {account_id} 验证码输入超时（{timeout}秒）")
            return None
        finally:
            # 清理
            if account_id in self.pending_responses:
                del self.pending_responses[account_id]
    
    def set_captcha_input(self, account_id: int, captcha_code: str):
        """
        设置验证码输入（从WebSocket接收）
        
        Args:
            account_id: 账号ID
            captcha_code: 验证码
        """
        if account_id in self.pending_responses:
            future = self.pending_responses[account_id]
            if not future.done():
                future.set_result(captcha_code)
                logger.info(f"✅ 已接收账号 {account_id} 的验证码: {captcha_code}")
                return True
        
        logger.warning(f"账号 {account_id} 没有等待验证码输入的请求")
        return False


# 创建全局管理器实例
captcha_ws_manager = CaptchaWebSocketManager()


@router.websocket("/{account_id}")
async def captcha_websocket_endpoint(websocket: WebSocket, account_id: int):
    """
    验证码WebSocket端点
    
    Args:
        websocket: WebSocket连接
        account_id: 账号ID
    """
    await captcha_ws_manager.connect(account_id, websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "captcha_input":
                # 收到验证码输入
                captcha_code = data.get("code", "")
                success = captcha_ws_manager.set_captcha_input(account_id, captcha_code)
                
                # 发送确认
                await websocket.send_json({
                    "type": "captcha_received",
                    "success": success,
                    "message": "验证码已接收" if success else "当前没有等待验证码的请求"
                })
            
            elif message_type == "ping":
                # 心跳
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "refresh_captcha":
                # 请求刷新验证码（需要后端重新获取）
                # 这里可以触发后端刷新验证码图片
                await websocket.send_json({
                    "type": "refresh_result",
                    "success": False,
                    "message": "验证码刷新功能待实现"
                })
            
    except WebSocketDisconnect:
        logger.info(f"账号 {account_id} 的验证码WebSocket已断开")
    except Exception as e:
        logger.error(f"验证码WebSocket异常: {str(e)}")
    finally:
        captcha_ws_manager.disconnect(account_id, websocket)


# 导出管理器供其他模块使用
__all__ = ['router', 'captcha_ws_manager']
