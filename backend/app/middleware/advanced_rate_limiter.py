"""
高级限流器
✅ P1-8: API限流增强（令牌桶、滑动窗口）
"""
import asyncio
import time
from typing import Dict, Optional
from collections import deque
from dataclasses import dataclass
from ..utils.logger import logger


@dataclass
class RateLimitRule:
    """限流规则"""
    calls: int          # 允许的调用次数
    period: int         # 时间窗口（秒）
    burst: int = 0      # 突发容量（令牌桶）


class TokenBucket:
    """令牌桶算法"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        初始化令牌桶
        
        Args:
            capacity: 桶容量
            refill_rate: 令牌填充速率（个/秒）
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """
        获取令牌
        
        Args:
            tokens: 需要的令牌数
            
        Returns:
            是否成功获取
        """
        async with self.lock:
            # 填充令牌
            now = time.time()
            elapsed = now - self.last_refill
            new_tokens = elapsed * self.refill_rate
            
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now
            
            # 检查是否有足够令牌
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                return False
    
    def get_tokens(self) -> float:
        """获取当前令牌数"""
        return self.tokens


class SlidingWindowCounter:
    """滑动窗口计数器"""
    
    def __init__(self, window_size: int, max_requests: int):
        """
        初始化滑动窗口
        
        Args:
            window_size: 窗口大小（秒）
            max_requests: 最大请求数
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def allow_request(self) -> bool:
        """
        检查是否允许请求
        
        Returns:
            是否允许
        """
        async with self.lock:
            now = time.time()
            
            # 移除过期请求
            while self.requests and self.requests[0] < now - self.window_size:
                self.requests.popleft()
            
            # 检查请求数
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            else:
                return False
    
    def get_request_count(self) -> int:
        """获取当前窗口内的请求数"""
        now = time.time()
        
        # 移除过期请求
        while self.requests and self.requests[0] < now - self.window_size:
            self.requests.popleft()
        
        return len(self.requests)


class LeakyBucket:
    """漏桶算法"""
    
    def __init__(self, capacity: int, leak_rate: float):
        """
        初始化漏桶
        
        Args:
            capacity: 桶容量
            leak_rate: 漏水速率（个/秒）
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water = 0
        self.last_leak = time.time()
        self.lock = asyncio.Lock()
    
    async def add_water(self, amount: int = 1) -> bool:
        """
        添加水（请求）
        
        Args:
            amount: 水量
            
        Returns:
            是否成功添加
        """
        async with self.lock:
            # 漏水
            now = time.time()
            elapsed = now - self.last_leak
            leaked = elapsed * self.leak_rate
            
            self.water = max(0, self.water - leaked)
            self.last_leak = now
            
            # 检查容量
            if self.water + amount <= self.capacity:
                self.water += amount
                return True
            else:
                return False
    
    def get_water_level(self) -> float:
        """获取当前水位"""
        return self.water


class AdvancedRateLimiter:
    """高级限流器"""
    
    def __init__(self):
        self.limiters: Dict[str, any] = {}
        
        # 统计
        self.stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'rejected_requests': 0
        }
    
    def create_token_bucket(
        self,
        key: str,
        capacity: int,
        refill_rate: float
    ):
        """创建令牌桶限流器"""
        self.limiters[key] = TokenBucket(capacity, refill_rate)
        logger.info(f"令牌桶限流器已创建: {key}")
    
    def create_sliding_window(
        self,
        key: str,
        window_size: int,
        max_requests: int
    ):
        """创建滑动窗口限流器"""
        self.limiters[key] = SlidingWindowCounter(window_size, max_requests)
        logger.info(f"滑动窗口限流器已创建: {key}")
    
    def create_leaky_bucket(
        self,
        key: str,
        capacity: int,
        leak_rate: float
    ):
        """创建漏桶限流器"""
        self.limiters[key] = LeakyBucket(capacity, leak_rate)
        logger.info(f"漏桶限流器已创建: {key}")
    
    async def check_limit(self, key: str, tokens: int = 1) -> bool:
        """
        检查限流
        
        Args:
            key: 限流器键
            tokens: 需要的令牌数/水量
            
        Returns:
            是否允许请求
        """
        if key not in self.limiters:
            # 未配置限流器，默认允许
            return True
        
        self.stats['total_requests'] += 1
        
        limiter = self.limiters[key]
        
        # 根据限流器类型调用不同方法
        if isinstance(limiter, TokenBucket):
            allowed = await limiter.acquire(tokens)
        elif isinstance(limiter, SlidingWindowCounter):
            allowed = await limiter.allow_request()
        elif isinstance(limiter, LeakyBucket):
            allowed = await limiter.add_water(tokens)
        else:
            allowed = True
        
        if allowed:
            self.stats['allowed_requests'] += 1
        else:
            self.stats['rejected_requests'] += 1
            logger.warning(f"请求被限流: {key}")
        
        return allowed
    
    async def wait_for_token(self, key: str, timeout: Optional[float] = None):
        """
        等待直到获取令牌
        
        Args:
            key: 限流器键
            timeout: 超时时间（秒）
        """
        start_time = time.time()
        
        while True:
            if await self.check_limit(key):
                return True
            
            # 检查超时
            if timeout and (time.time() - start_time) >= timeout:
                return False
            
            # 短暂等待
            await asyncio.sleep(0.1)
    
    def get_limiter_status(self, key: str) -> Dict:
        """获取限流器状态"""
        if key not in self.limiters:
            return {'error': 'Limiter not found'}
        
        limiter = self.limiters[key]
        
        if isinstance(limiter, TokenBucket):
            return {
                'type': 'token_bucket',
                'tokens': limiter.get_tokens(),
                'capacity': limiter.capacity,
                'refill_rate': limiter.refill_rate
            }
        elif isinstance(limiter, SlidingWindowCounter):
            return {
                'type': 'sliding_window',
                'request_count': limiter.get_request_count(),
                'max_requests': limiter.max_requests,
                'window_size': limiter.window_size
            }
        elif isinstance(limiter, LeakyBucket):
            return {
                'type': 'leaky_bucket',
                'water_level': limiter.get_water_level(),
                'capacity': limiter.capacity,
                'leak_rate': limiter.leak_rate
            }
        else:
            return {'error': 'Unknown limiter type'}
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'rejection_rate': (
                self.stats['rejected_requests'] / self.stats['total_requests'] * 100
                if self.stats['total_requests'] > 0 else 0
            )
        }


# 全局限流器
advanced_rate_limiter = AdvancedRateLimiter()


# 便捷函数
async def check_api_limit(api_name: str) -> bool:
    """检查API限流"""
    return await advanced_rate_limiter.check_limit(f'api:{api_name}')


async def check_user_limit(user_id: str, action: str) -> bool:
    """检查用户操作限流"""
    return await advanced_rate_limiter.check_limit(f'user:{user_id}:{action}')
