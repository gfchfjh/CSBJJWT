"""
速率限制器
用于forwarder_enhanced.py等模块
"""
import asyncio
from collections import deque
from datetime import datetime, timedelta


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, calls: int, period: int):
        """
        初始化限流器
        
        Args:
            calls: 时间窗口内允许的最大调用次数
            period: 时间窗口（秒）
        """
        self.calls = calls
        self.period = period
        self.timestamps = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """获取许可（阻塞直到可以执行）"""
        async with self.lock:
            now = datetime.now()
            
            # 清理过期的时间戳
            while self.timestamps and self.timestamps[0] < now - timedelta(seconds=self.period):
                self.timestamps.popleft()
            
            # 检查是否超限
            if len(self.timestamps) >= self.calls:
                # 计算需要等待的时间
                oldest = self.timestamps[0]
                wait_until = oldest + timedelta(seconds=self.period)
                wait_time = (wait_until - now).total_seconds()
                
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    return await self.acquire()
            
            # 记录时间戳
            self.timestamps.append(now)
    
    def try_acquire(self) -> bool:
        """尝试获取许可（非阻塞）"""
        now = datetime.now()
        
        # 清理过期的时间戳
        while self.timestamps and self.timestamps[0] < now - timedelta(seconds=self.period):
            self.timestamps.popleft()
        
        # 检查是否超限
        if len(self.timestamps) >= self.calls:
            return False
        
        # 记录时间戳
        self.timestamps.append(now)
        return True



class RateLimiterManager:
    def __init__(self):
        self.limiters = {}
    
    def get_limiter(self, name: str, calls: int, period: int):
        if name not in self.limiters:
            self.limiters[name] = RateLimiter(calls, period)
        return self.limiters[name]

rate_limiter_manager = RateLimiterManager()
