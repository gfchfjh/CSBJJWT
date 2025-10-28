"""
WebSocket连接管理器
实现智能断线重连、心跳检测、连接池管理
"""
import asyncio
import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """连接状态枚举"""
    DISCONNECTED = "disconnected"  # 未连接
    CONNECTING = "connecting"      # 连接中
    CONNECTED = "connected"        # 已连接
    RECONNECTING = "reconnecting"  # 重连中
    FAILED = "failed"              # 连接失败


class ReconnectStrategy:
    """重连策略"""
    
    def __init__(
        self,
        max_retries: int = 10,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        初始化重连策略
        
        Args:
            max_retries: 最大重试次数（0表示无限重试）
            initial_delay: 初始延迟（秒）
            max_delay: 最大延迟（秒）
            exponential_base: 指数退避基数
            jitter: 是否添加随机抖动（防止雪崩）
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_count = 0
    
    def get_delay(self) -> float:
        """
        计算下次重试的延迟时间
        
        Returns:
            float: 延迟秒数
        """
        # 指数退避
        delay = min(
            self.initial_delay * (self.exponential_base ** self.retry_count),
            self.max_delay
        )
        
        # 添加随机抖动（±25%）
        if self.jitter:
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def should_retry(self) -> bool:
        """
        判断是否应该继续重试
        
        Returns:
            bool: 应该重试返回True
        """
        if self.max_retries == 0:  # 无限重试
            return True
        return self.retry_count < self.max_retries
    
    def increment(self):
        """增加重试次数"""
        self.retry_count += 1
    
    def reset(self):
        """重置重试计数"""
        self.retry_count = 0


class WebSocketManager:
    """
    WebSocket连接管理器
    
    功能：
    - 自动重连
    - 心跳检测
    - 连接状态监控
    - 消息队列
    """
    
    def __init__(
        self,
        connect_func: Callable,
        on_message: Optional[Callable] = None,
        on_connect: Optional[Callable] = None,
        on_disconnect: Optional[Callable] = None,
        heartbeat_interval: float = 30.0,
        heartbeat_timeout: float = 10.0,
        reconnect_strategy: Optional[ReconnectStrategy] = None
    ):
        """
        初始化WebSocket管理器
        
        Args:
            connect_func: 连接函数（异步），返回WebSocket对象
            on_message: 消息处理函数（异步）
            on_connect: 连接成功回调（异步）
            on_disconnect: 断开连接回调（异步）
            heartbeat_interval: 心跳间隔（秒）
            heartbeat_timeout: 心跳超时（秒）
            reconnect_strategy: 重连策略
        """
        self.connect_func = connect_func
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        
        self.reconnect_strategy = reconnect_strategy or ReconnectStrategy()
        
        self.ws: Optional[Any] = None
        self.state = ConnectionState.DISCONNECTED
        self.last_heartbeat = None
        self.last_message_time = None
        
        self._running = False
        self._reconnect_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._message_task: Optional[asyncio.Task] = None
        
        self._stats = {
            'connected_at': None,
            'total_messages': 0,
            'total_reconnects': 0,
            'last_error': None
        }
    
    async def start(self):
        """启动WebSocket连接"""
        if self._running:
            logger.warning("WebSocket管理器已在运行")
            return
        
        self._running = True
        logger.info("启动WebSocket管理器")
        
        # 开始连接
        await self._connect()
    
    async def stop(self):
        """停止WebSocket连接"""
        logger.info("停止WebSocket管理器")
        self._running = False
        
        # 取消所有任务
        if self._reconnect_task:
            self._reconnect_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._message_task:
            self._message_task.cancel()
        
        # 关闭连接
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.error(f"关闭WebSocket异常: {e}")
        
        self.state = ConnectionState.DISCONNECTED
    
    async def _connect(self):
        """内部连接方法"""
        if self.state == ConnectionState.CONNECTING:
            logger.debug("正在连接中，跳过")
            return
        
        self.state = ConnectionState.CONNECTING
        logger.info("正在建立WebSocket连接...")
        
        try:
            # 调用用户提供的连接函数
            self.ws = await self.connect_func()
            
            if self.ws:
                self.state = ConnectionState.CONNECTED
                self._stats['connected_at'] = datetime.now()
                self.last_heartbeat = datetime.now()
                self.last_message_time = datetime.now()
                
                # 重置重连策略
                self.reconnect_strategy.reset()
                
                logger.info("✅ WebSocket连接成功")
                
                # 触发连接成功回调
                if self.on_connect:
                    await self.on_connect()
                
                # 启动心跳任务
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
                # 启动消息接收任务
                if self.on_message:
                    self._message_task = asyncio.create_task(self._message_loop())
                
            else:
                raise Exception("连接函数返回None")
                
        except Exception as e:
            logger.error(f"❌ WebSocket连接失败: {e}")
            self._stats['last_error'] = str(e)
            self.state = ConnectionState.FAILED
            
            # 触发断开回调
            if self.on_disconnect:
                await self.on_disconnect(str(e))
            
            # 尝试重连
            if self._running:
                await self._schedule_reconnect()
    
    async def _schedule_reconnect(self):
        """调度重连"""
        if not self.reconnect_strategy.should_retry():
            logger.error(f"❌ 达到最大重试次数 ({self.reconnect_strategy.max_retries})，放弃重连")
            self.state = ConnectionState.FAILED
            return
        
        delay = self.reconnect_strategy.get_delay()
        self.reconnect_strategy.increment()
        self._stats['total_reconnects'] += 1
        
        logger.info(
            f"🔄 将在 {delay:.1f} 秒后重连 "
            f"(第 {self.reconnect_strategy.retry_count}/{self.reconnect_strategy.max_retries} 次)"
        )
        
        self.state = ConnectionState.RECONNECTING
        
        # 延迟后重连
        await asyncio.sleep(delay)
        
        if self._running:
            await self._connect()
    
    async def _heartbeat_loop(self):
        """心跳检测循环"""
        logger.debug("心跳任务启动")
        
        try:
            while self._running and self.state == ConnectionState.CONNECTED:
                await asyncio.sleep(self.heartbeat_interval)
                
                # 检查是否超时
                if self.last_message_time:
                    elapsed = (datetime.now() - self.last_message_time).total_seconds()
                    
                    if elapsed > (self.heartbeat_interval + self.heartbeat_timeout):
                        logger.warning(f"⚠️ 心跳超时 ({elapsed:.1f}秒)，触发重连")
                        await self._handle_disconnect("心跳超时")
                        break
                
                # 发送心跳（如果WebSocket支持ping）
                try:
                    if hasattr(self.ws, 'ping'):
                        await self.ws.ping()
                        self.last_heartbeat = datetime.now()
                        logger.debug("💓 心跳发送成功")
                except Exception as e:
                    logger.error(f"心跳发送失败: {e}")
                    await self._handle_disconnect(f"心跳失败: {e}")
                    break
                    
        except asyncio.CancelledError:
            logger.debug("心跳任务被取消")
        except Exception as e:
            logger.error(f"心跳任务异常: {e}")
    
    async def _message_loop(self):
        """消息接收循环"""
        logger.debug("消息接收任务启动")
        
        try:
            while self._running and self.state == ConnectionState.CONNECTED:
                try:
                    # 接收消息
                    message = await self.ws.recv()
                    
                    self.last_message_time = datetime.now()
                    self._stats['total_messages'] += 1
                    
                    # 处理消息
                    if self.on_message:
                        await self.on_message(message)
                        
                except asyncio.TimeoutError:
                    logger.debug("消息接收超时，继续等待")
                    continue
                except Exception as e:
                    logger.error(f"消息接收异常: {e}")
                    await self._handle_disconnect(f"消息接收异常: {e}")
                    break
                    
        except asyncio.CancelledError:
            logger.debug("消息接收任务被取消")
        except Exception as e:
            logger.error(f"消息接收任务异常: {e}")
    
    async def _handle_disconnect(self, reason: str):
        """处理断开连接"""
        logger.warning(f"🔌 WebSocket断开: {reason}")
        
        self.state = ConnectionState.DISCONNECTED
        self._stats['last_error'] = reason
        
        # 关闭连接
        if self.ws:
            try:
                await self.ws.close()
            except:
                pass
            self.ws = None
        
        # 触发断开回调
        if self.on_disconnect:
            try:
                await self.on_disconnect(reason)
            except Exception as e:
                logger.error(f"断开回调异常: {e}")
        
        # 重连
        if self._running:
            await self._schedule_reconnect()
    
    def get_state(self) -> ConnectionState:
        """获取当前连接状态"""
        return self.state
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = None
        if self._stats['connected_at']:
            uptime = (datetime.now() - self._stats['connected_at']).total_seconds()
        
        return {
            'state': self.state.value,
            'uptime': uptime,
            'total_messages': self._stats['total_messages'],
            'total_reconnects': self._stats['total_reconnects'],
            'last_error': self._stats['last_error'],
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'last_message': self.last_message_time.isoformat() if self.last_message_time else None,
            'retry_count': self.reconnect_strategy.retry_count,
            'max_retries': self.reconnect_strategy.max_retries
        }
