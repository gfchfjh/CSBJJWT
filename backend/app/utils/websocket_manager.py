"""
WebSocket连接管理器
✅ P1-3优化: 指数退避 + 心跳检测 + 智能重连
"""
import asyncio
import random
import time
from datetime import datetime
from typing import Optional, Callable, Any
from enum import Enum
from ..utils.logger import logger


class ConnectionStatus(Enum):
    """连接状态枚举"""
    DISCONNECTED = "disconnected"      # 未连接
    CONNECTING = "connecting"          # 连接中
    CONNECTED = "connected"            # 已连接
    RECONNECTING = "reconnecting"      # 重连中
    FAILED = "failed"                  # 连接失败


class WebSocketManager:
    """
    WebSocket连接管理器
    
    功能：
    1. 指数退避重连（最多10次）
    2. 心跳检测（30秒间隔）
    3. 自动重连
    4. 连接状态管理
    5. 随机抖动（防止雪崩）
    """
    
    def __init__(
        self,
        url: str,
        max_retries: int = 10,
        heartbeat_interval: int = 30,
        heartbeat_timeout: int = 10
    ):
        """
        初始化WebSocket管理器
        
        Args:
            url: WebSocket URL
            max_retries: 最大重试次数
            heartbeat_interval: 心跳间隔（秒）
            heartbeat_timeout: 心跳超时时间（秒）
        """
        self.url = url
        self.max_retries = max_retries
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        
        # 连接状态
        self.status = ConnectionStatus.DISCONNECTED
        self.retry_count = 0
        
        # WebSocket对象（由子类实现）
        self.ws = None
        
        # 心跳任务
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.last_heartbeat: Optional[datetime] = None
        self.last_pong: Optional[datetime] = None
        
        # 回调函数
        self.on_connect: Optional[Callable] = None
        self.on_disconnect: Optional[Callable] = None
        self.on_message: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # 统计信息
        self.total_reconnects = 0
        self.total_messages = 0
        self.connected_at: Optional[datetime] = None
        self.last_error: Optional[str] = None
        
        logger.info(f"✅ WebSocket管理器已初始化: {url}")
    
    async def connect(self) -> bool:
        """
        连接WebSocket（带智能重连）
        
        Returns:
            是否连接成功
        """
        while self.retry_count < self.max_retries:
            try:
                self.status = ConnectionStatus.CONNECTING if self.retry_count == 0 else ConnectionStatus.RECONNECTING
                
                logger.info(f"{'连接' if self.retry_count == 0 else '重连'}WebSocket... (第{self.retry_count + 1}次)")
                
                # 实际连接逻辑（由子类实现）
                await self._do_connect()
                
                # 连接成功
                self.status = ConnectionStatus.CONNECTED
                self.retry_count = 0  # 重置计数
                self.connected_at = datetime.now()
                
                logger.info(f"✅ WebSocket连接成功: {self.url}")
                
                # 启动心跳
                self._start_heartbeat()
                
                # 回调
                if self.on_connect:
                    await self.on_connect()
                
                return True
                
            except Exception as e:
                self.retry_count += 1
                self.last_error = str(e)
                
                if self.retry_count >= self.max_retries:
                    # 达到最大重试次数
                    self.status = ConnectionStatus.FAILED
                    logger.error(f"❌ WebSocket连接失败，已达最大重试次数({self.max_retries}): {e}")
                    
                    if self.on_error:
                        await self.on_error(e)
                    
                    return False
                
                # 计算退避延迟（指数退避 + 随机抖动）
                delay = self._calculate_backoff_delay()
                
                logger.warning(
                    f"⚠️ 连接失败（{self.retry_count}/{self.max_retries}），"
                    f"{delay:.1f}秒后重试: {e}"
                )
                
                await asyncio.sleep(delay)
        
        return False
    
    def _calculate_backoff_delay(self) -> float:
        """
        计算指数退避延迟
        
        公式：delay = min(2^retry_count, max_delay) + random_jitter
        
        Returns:
            延迟时间（秒）
        """
        # 基础延迟：2的指数
        base_delay = 2 ** self.retry_count
        
        # 最大延迟：60秒
        max_delay = 60
        
        # 限制最大值
        delay = min(base_delay, max_delay)
        
        # 添加随机抖动（±10%），防止雪崩效应
        jitter = random.uniform(-delay * 0.1, delay * 0.1)
        
        return delay + jitter
    
    async def _do_connect(self):
        """
        实际连接逻辑（由子类实现）
        
        子类需要：
        1. 创建WebSocket连接
        2. 设置self.ws
        """
        raise NotImplementedError("子类必须实现_do_connect方法")
    
    def _start_heartbeat(self):
        """启动心跳检测"""
        if self.heartbeat_task is None or self.heartbeat_task.done():
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info(f"✅ 心跳检测已启动（间隔{self.heartbeat_interval}秒）")
    
    def _stop_heartbeat(self):
        """停止心跳检测"""
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()
            logger.info("心跳检测已停止")
    
    async def _heartbeat_loop(self):
        """心跳检测循环"""
        while self.status == ConnectionStatus.CONNECTED:
            try:
                # 发送ping
                await self._send_ping()
                self.last_heartbeat = datetime.now()
                
                logger.debug(f"💓 心跳ping发送: {self.last_heartbeat.isoformat()}")
                
                # 等待心跳间隔
                await asyncio.sleep(self.heartbeat_interval)
                
                # 检查是否超时（没有收到pong）
                if self.last_heartbeat and self.last_pong:
                    elapsed = (datetime.now() - self.last_pong).seconds
                    
                    if elapsed > self.heartbeat_timeout:
                        logger.warning(f"⚠️ 心跳超时（{elapsed}秒无响应），触发重连...")
                        await self.reconnect()
                        break
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳检测异常: {e}")
                await self.reconnect()
                break
    
    async def _send_ping(self):
        """
        发送ping（由子类实现）
        
        对于Playwright的WebSocket，可能需要发送特定格式的消息
        """
        if self.ws:
            try:
                # 这里的实现取决于WebSocket类型
                # 如果是标准WebSocket，可以使用ws.ping()
                # 如果是自定义协议，可能需要发送特定消息
                await self.ws.ping()
            except Exception as e:
                logger.error(f"发送ping失败: {e}")
    
    def on_pong_received(self):
        """收到pong响应时调用"""
        self.last_pong = datetime.now()
        logger.debug(f"💓 心跳pong收到: {self.last_pong.isoformat()}")
    
    async def reconnect(self):
        """重新连接"""
        logger.info("🔄 开始重连...")
        
        self.total_reconnects += 1
        
        # 断开现有连接
        await self.disconnect(is_reconnect=True)
        
        # 重新连接
        success = await self.connect()
        
        if success:
            logger.info(f"✅ 重连成功（总重连次数: {self.total_reconnects}）")
        else:
            logger.error("❌ 重连失败")
    
    async def disconnect(self, is_reconnect: bool = False):
        """
        断开连接
        
        Args:
            is_reconnect: 是否为重连操作（如果是，不重置retry_count）
        """
        logger.info("断开WebSocket连接...")
        
        # 停止心跳
        self._stop_heartbeat()
        
        # 关闭WebSocket
        if self.ws:
            try:
                await self._do_disconnect()
            except Exception as e:
                logger.error(f"关闭WebSocket异常: {e}")
            finally:
                self.ws = None
        
        # 更新状态
        if not is_reconnect:
            self.status = ConnectionStatus.DISCONNECTED
            self.retry_count = 0
        
        # 回调
        if self.on_disconnect and not is_reconnect:
            await self.on_disconnect()
        
        logger.info("✅ WebSocket已断开")
    
    async def _do_disconnect(self):
        """实际断开逻辑（由子类实现）"""
        if self.ws:
            await self.ws.close()
    
    async def send_message(self, message: Any):
        """
        发送消息
        
        Args:
            message: 要发送的消息
        """
        if self.status != ConnectionStatus.CONNECTED:
            raise ConnectionError("WebSocket未连接")
        
        try:
            await self._do_send(message)
            self.total_messages += 1
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            raise
    
    async def _do_send(self, message: Any):
        """实际发送逻辑（由子类实现）"""
        if self.ws:
            await self.ws.send(message)
    
    def get_stats(self) -> dict:
        """
        获取统计信息
        
        Returns:
            统计数据字典
        """
        uptime = None
        if self.connected_at:
            uptime = (datetime.now() - self.connected_at).seconds
        
        return {
            'status': self.status.value,
            'url': self.url,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'total_reconnects': self.total_reconnects,
            'total_messages': self.total_messages,
            'connected_at': self.connected_at.isoformat() if self.connected_at else None,
            'uptime_seconds': uptime,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'last_pong': self.last_pong.isoformat() if self.last_pong else None,
            'last_error': self.last_error
        }
    
    def is_connected(self) -> bool:
        """是否已连接"""
        return self.status == ConnectionStatus.CONNECTED
    
    def set_callbacks(
        self,
        on_connect: Optional[Callable] = None,
        on_disconnect: Optional[Callable] = None,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ):
        """
        设置回调函数
        
        Args:
            on_connect: 连接成功回调
            on_disconnect: 断开连接回调
            on_message: 收到消息回调
            on_error: 错误回调
        """
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_message = on_message
        self.on_error = on_error


class PlaywrightWebSocketManager(WebSocketManager):
    """
    Playwright WebSocket管理器
    
    专门用于管理Playwright页面中的WebSocket连接
    """
    
    def __init__(
        self,
        page,
        ws_url_pattern: str = None,
        **kwargs
    ):
        """
        初始化
        
        Args:
            page: Playwright页面对象
            ws_url_pattern: WebSocket URL匹配模式（用于识别目标WS）
            **kwargs: 传递给父类的参数
        """
        super().__init__(url=ws_url_pattern or "unknown", **kwargs)
        self.page = page
        self.ws_url_pattern = ws_url_pattern
        self.target_ws = None  # 目标WebSocket对象
    
    async def _do_connect(self):
        """实现Playwright的连接逻辑"""
        # 对于Playwright，WebSocket是由页面自动创建的
        # 我们只需要等待WebSocket出现
        
        # 监听WebSocket事件
        self.page.on('websocket', self._on_websocket_created)
        
        # 等待WebSocket连接（最多10秒）
        try:
            await asyncio.wait_for(
                self._wait_for_websocket(),
                timeout=10
            )
        except asyncio.TimeoutError:
            raise ConnectionError("等待WebSocket连接超时")
    
    async def _wait_for_websocket(self):
        """等待WebSocket连接建立"""
        while self.target_ws is None:
            await asyncio.sleep(0.1)
    
    def _on_websocket_created(self, ws):
        """WebSocket创建时的回调"""
        # 检查URL是否匹配
        if self.ws_url_pattern and self.ws_url_pattern not in ws.url:
            return
        
        logger.info(f"✅ 检测到WebSocket: {ws.url}")
        
        self.target_ws = ws
        self.ws = ws
        
        # 监听WebSocket事件
        ws.on('close', lambda: self._on_ws_close())
        ws.on('framereceived', lambda frame: self._on_frame_received(frame))
    
    def _on_ws_close(self):
        """WebSocket关闭时的回调"""
        logger.warning("⚠️ WebSocket已关闭")
        
        if self.status == ConnectionStatus.CONNECTED:
            # 触发重连
            asyncio.create_task(self.reconnect())
    
    def _on_frame_received(self, frame):
        """收到WebSocket帧时的回调"""
        # 处理pong帧
        if frame.is_pong:
            self.on_pong_received()
        
        # 调用消息回调
        if self.on_message:
            asyncio.create_task(self.on_message(frame.payload))
    
    async def _send_ping(self):
        """发送ping（Playwright WebSocket）"""
        # Playwright的WebSocket可能不支持直接ping
        # 可以通过发送特定消息来实现心跳
        pass
    
    async def _do_disconnect(self):
        """Playwright WebSocket断开"""
        # Playwright的WebSocket由页面管理，我们只需要清空引用
        self.target_ws = None


# 使用示例
if __name__ == "__main__":
    async def main():
        # 标准WebSocket示例
        ws_manager = WebSocketManager("wss://example.com/ws")
        
        # 设置回调
        ws_manager.set_callbacks(
            on_connect=lambda: print("已连接"),
            on_disconnect=lambda: print("已断开"),
            on_message=lambda msg: print(f"收到消息: {msg}"),
            on_error=lambda err: print(f"错误: {err}")
        )
        
        # 连接
        await ws_manager.connect()
        
        # 保持运行
        while ws_manager.is_connected():
            await asyncio.sleep(1)
    
    asyncio.run(main())
