"""
增强限流器（P2-2优化：Token Bucket算法）

Token Bucket算法相比Fixed Window的优势：
1. 更灵活：允许短时突发流量
2. 更高效：充分利用API配额
3. 更精确：平滑的流量控制
"""
import asyncio
import time
from typing import Dict
from ..utils.logger import logger


class TokenBucketRateLimiter:
    """
    令牌桶限流器（✅ P2-2优化）
    
    工作原理：
    - 桶有固定容量（capacity）
    - 令牌以恒定速率补充（refill_rate 个/秒）
    - 每次请求消耗1个令牌
    - 令牌不足时等待
    
    优势：
    - Discord: 5条/2秒 = 2.5条/秒（之前：5条/5秒 = 1条/秒）效率提升150%
    - 允许短时突发（桶有余量时）
    - 长期稳定在配额内
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        初始化令牌桶
        
        Args:
            capacity: 桶容量（最多存储多少令牌）
            refill_rate: 令牌补充速率（每秒补充多少个）
        
        Examples:
            # Discord: 5条/2秒
            limiter = TokenBucketRateLimiter(capacity=5, refill_rate=2.5)
            
            # Telegram: 30条/秒
            limiter = TokenBucketRateLimiter(capacity=30, refill_rate=30)
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)  # 初始时桶满
        self.last_refill_time = time.time()
        self._lock = asyncio.Lock()  # 线程安全
    
    async def acquire(self, count: int = 1) -> bool:
        """
        获取令牌（异步，会自动等待）
        
        Args:
            count: 需要的令牌数量
            
        Returns:
            是否成功获取
        """
        async with self._lock:
            # 1. 补充令牌
            now = time.time()
            elapsed = now - self.last_refill_time
            
            # 计算应补充的令牌数
            tokens_to_add = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill_time = now
            
            # 2. 检查令牌是否足够
            if self.tokens >= count:
                # 令牌足够，直接扣除
                self.tokens -= count
                return True
            else:
                # 令牌不足，计算需要等待的时间
                tokens_needed = count - self.tokens
                wait_time = tokens_needed / self.refill_rate
                
                logger.debug(f"限流等待 {wait_time:.2f} 秒")
                
                # 等待令牌补充
                await asyncio.sleep(wait_time)
                
                # 扣除令牌
                self.tokens = 0  # 等待后肯定刚好够用
                self.last_refill_time = time.time()
                
                return True
    
    def try_acquire(self, count: int = 1) -> bool:
        """
        尝试获取令牌（非阻塞）
        
        Args:
            count: 需要的令牌数量
            
        Returns:
            是否成功获取（失败时不等待）
        """
        # 补充令牌
        now = time.time()
        elapsed = now - self.last_refill_time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill_time = now
        
        # 检查令牌
        if self.tokens >= count:
            self.tokens -= count
            return True
        else:
            return False
    
    def get_available_tokens(self) -> float:
        """
        获取当前可用令牌数
        
        Returns:
            可用令牌数（浮点数）
        """
        now = time.time()
        elapsed = now - self.last_refill_time
        tokens_to_add = elapsed * self.refill_rate
        available = min(self.capacity, self.tokens + tokens_to_add)
        return available
    
    def get_wait_time(self, count: int = 1) -> float:
        """
        计算获取指定数量令牌需要等待的时间
        
        Args:
            count: 需要的令牌数量
            
        Returns:
            等待时间（秒）
        """
        available = self.get_available_tokens()
        
        if available >= count:
            return 0.0
        else:
            tokens_needed = count - available
            return tokens_needed / self.refill_rate


class MultiPlatformRateLimiter:
    """
    多平台限流器管理（✅ P2-2优化：使用Token Bucket）
    
    统一管理Discord、Telegram、飞书的限流
    """
    
    def __init__(self):
        """初始化多平台限流器"""
        # ✅ P2-2优化：使用Token Bucket算法
        
        # Discord: 官方限制 5条/2秒，使用保守策略 5条/2.5秒
        self.discord = TokenBucketRateLimiter(
            capacity=5,
            refill_rate=2.0  # 5条/2.5秒 = 2条/秒
        )
        
        # Telegram: 官方限制 30条/秒，保持原样
        self.telegram = TokenBucketRateLimiter(
            capacity=30,
            refill_rate=30.0  # 30条/秒
        )
        
        # 飞书: 官方限制 20条/秒，保持原样
        self.feishu = TokenBucketRateLimiter(
            capacity=20,
            refill_rate=20.0  # 20条/秒
        )
        
        logger.info("✅ 多平台限流器已初始化（Token Bucket算法）")
    
    async def acquire(self, platform: str, count: int = 1) -> bool:
        """
        获取指定平台的令牌
        
        Args:
            platform: 平台名称（discord/telegram/feishu）
            count: 令牌数量
            
        Returns:
            是否成功
        """
        platform = platform.lower()
        
        if platform == 'discord':
            return await self.discord.acquire(count)
        elif platform == 'telegram':
            return await self.telegram.acquire(count)
        elif platform == 'feishu' or platform == 'lark':
            return await self.feishu.acquire(count)
        else:
            logger.warning(f"未知平台: {platform}")
            return True  # 未知平台不限流
    
    def get_stats(self) -> Dict[str, Dict]:
        """
        获取所有平台的限流统计
        
        Returns:
            统计信息字典
        """
        return {
            'discord': {
                'capacity': self.discord.capacity,
                'refill_rate': self.discord.refill_rate,
                'available_tokens': round(self.discord.get_available_tokens(), 2),
                'wait_time': round(self.discord.get_wait_time(), 2)
            },
            'telegram': {
                'capacity': self.telegram.capacity,
                'refill_rate': self.telegram.refill_rate,
                'available_tokens': round(self.telegram.get_available_tokens(), 2),
                'wait_time': round(self.telegram.get_wait_time(), 2)
            },
            'feishu': {
                'capacity': self.feishu.capacity,
                'refill_rate': self.feishu.refill_rate,
                'available_tokens': round(self.feishu.get_available_tokens(), 2),
                'wait_time': round(self.feishu.get_wait_time(), 2)
            }
        }


# 全局实例
rate_limiter = MultiPlatformRateLimiter()
