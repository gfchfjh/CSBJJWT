"""限流工具模块"""
import asyncio
from collections import deque
from datetime import datetime, timedelta
from typing import Dict


class RateLimiter:
    """限流器"""
    
    def __init__(self, calls: int, period: int):
        """初始化限流器
        
        Args:
            calls: 时间窗口内允许的最大调用次数
            period: 时间窗口（秒）
        """
        self.calls = calls
        self.period = period
        self.timestamps = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """获取令牌（等待直到可以执行）"""
        async with self._lock:
            now = datetime.now()
            
            # 清理过期时间戳
            while self.timestamps and self.timestamps[0] < now - timedelta(seconds=self.period):
                self.timestamps.popleft()
            
            # 如果达到限制，需要等待
            if len(self.timestamps) >= self.calls:
                sleep_time = (self.timestamps[0] + timedelta(seconds=self.period) - now).total_seconds()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    return await self.acquire()
            
            # 记录时间戳
            self.timestamps.append(now)
    
    def get_remaining(self) -> int:
        """获取剩余可用次数"""
        now = datetime.now()
        # 清理过期时间戳
        while self.timestamps and self.timestamps[0] < now - timedelta(seconds=self.period):
            self.timestamps.popleft()
        return max(0, self.calls - len(self.timestamps))


class RateLimiterManager:
    """限流器管理器"""
    
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}
    
    def get_limiter(self, key: str, calls: int, period: int) -> RateLimiter:
        """获取或创建限流器"""
        if key not in self.limiters:
            self.limiters[key] = RateLimiter(calls, period)
        return self.limiters[key]


# 全局限流器管理器
rate_limiter_manager = RateLimiterManager()
