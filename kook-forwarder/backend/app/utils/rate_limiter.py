"""
限流器模块
"""
import asyncio
from collections import deque
from datetime import datetime, timedelta
from typing import Optional


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, calls: int, period: int):
        """
        初始化限流器
        
        Args:
            calls: 时间段内允许的调用次数
            period: 时间段（秒）
        """
        self.calls = calls
        self.period = period
        self.timestamps = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """获取许可（会阻塞直到可以执行）"""
        async with self.lock:
            now = datetime.now()
            
            # 清理过期的时间戳
            while self.timestamps and self.timestamps[0] < now - timedelta(seconds=self.period):
                self.timestamps.popleft()
            
            # 如果已达上限，计算需要等待的时间
            if len(self.timestamps) >= self.calls:
                sleep_time = (self.timestamps[0] + timedelta(seconds=self.period) - now).total_seconds()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    return await self.acquire()  # 递归重试
            
            # 记录当前时间戳
            self.timestamps.append(now)
    
    def can_acquire(self) -> bool:
        """检查是否可以立即获取许可（不阻塞）"""
        now = datetime.now()
        
        # 清理过期的时间戳
        while self.timestamps and self.timestamps[0] < now - timedelta(seconds=self.period):
            self.timestamps.popleft()
        
        return len(self.timestamps) < self.calls
    
    def get_wait_time(self) -> float:
        """获取需要等待的时间（秒）"""
        if self.can_acquire():
            return 0.0
        
        now = datetime.now()
        if self.timestamps:
            wait_until = self.timestamps[0] + timedelta(seconds=self.period)
            return max(0, (wait_until - now).total_seconds())
        return 0.0


class RateLimiterManager:
    """限流器管理器"""
    
    def __init__(self):
        self.limiters = {}
    
    def get_limiter(self, name: str, calls: int, period: int) -> RateLimiter:
        """
        获取或创建限流器
        
        Args:
            name: 限流器名称
            calls: 时间段内允许的调用次数
            period: 时间段（秒）
            
        Returns:
            限流器实例
        """
        if name not in self.limiters:
            self.limiters[name] = RateLimiter(calls, period)
        return self.limiters[name]


# 创建全局限流器管理器
rate_limiter_manager = RateLimiterManager()
