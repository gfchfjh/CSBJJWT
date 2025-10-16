"""
限流器模块测试
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from app.utils.rate_limiter import RateLimiter, RateLimiterManager


class TestRateLimiter:
    """RateLimiter类测试"""
    
    @pytest.mark.asyncio
    async def test_basic_rate_limit(self):
        """测试基本限流功能"""
        # 创建限流器：每5秒最多3次调用
        limiter = RateLimiter(calls=3, period=5)
        
        # 前3次应该立即通过
        start_time = datetime.now()
        for i in range(3):
            await limiter.acquire()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        assert elapsed < 1  # 应该很快完成
        
        # 第4次应该被限流
        start_time = datetime.now()
        await limiter.acquire()
        elapsed = (datetime.now() - start_time).total_seconds()
        assert elapsed >= 4  # 应该等待至少4秒
    
    @pytest.mark.asyncio
    async def test_can_acquire(self):
        """测试检查是否可以立即获取许可"""
        limiter = RateLimiter(calls=2, period=5)
        
        # 初始应该可以获取
        assert limiter.can_acquire() == True
        
        # 获取2次后不能再获取
        await limiter.acquire()
        await limiter.acquire()
        assert limiter.can_acquire() == False
        
        # 等待5秒后应该可以获取
        await asyncio.sleep(5)
        assert limiter.can_acquire() == True
    
    @pytest.mark.asyncio
    async def test_get_wait_time(self):
        """测试获取等待时间"""
        limiter = RateLimiter(calls=1, period=5)
        
        # 初始等待时间为0
        assert limiter.get_wait_time() == 0.0
        
        # 获取许可后需要等待
        await limiter.acquire()
        wait_time = limiter.get_wait_time()
        assert wait_time > 0
        assert wait_time <= 5
    
    @pytest.mark.asyncio
    async def test_concurrent_acquire(self):
        """测试并发获取许可"""
        limiter = RateLimiter(calls=5, period=5)
        
        # 并发请求10次
        tasks = [limiter.acquire() for _ in range(10)]
        
        start_time = datetime.now()
        await asyncio.gather(*tasks)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # 前5次立即通过，后5次需要等待约5秒
        assert elapsed >= 4  # 至少等待4秒
        assert elapsed < 7   # 不应该超过7秒


class TestRateLimiterManager:
    """RateLimiterManager类测试"""
    
    def test_get_limiter(self):
        """测试获取或创建限流器"""
        manager = RateLimiterManager()
        
        # 第一次获取，应该创建新的
        limiter1 = manager.get_limiter("test", calls=5, period=10)
        assert limiter1 is not None
        assert limiter1.calls == 5
        assert limiter1.period == 10
        
        # 第二次获取同名限流器，应该返回已有的
        limiter2 = manager.get_limiter("test", calls=10, period=20)
        assert limiter1 is limiter2
        
        # 获取不同名字的限流器
        limiter3 = manager.get_limiter("test2", calls=3, period=5)
        assert limiter3 is not limiter1
    
    @pytest.mark.asyncio
    async def test_multiple_limiters(self):
        """测试多个限流器独立工作"""
        manager = RateLimiterManager()
        
        limiter_a = manager.get_limiter("api_a", calls=2, period=5)
        limiter_b = manager.get_limiter("api_b", calls=3, period=5)
        
        # A限流器：2次请求
        await limiter_a.acquire()
        await limiter_a.acquire()
        assert limiter_a.can_acquire() == False
        
        # B限流器：3次请求
        await limiter_b.acquire()
        await limiter_b.acquire()
        await limiter_b.acquire()
        assert limiter_b.can_acquire() == False
        
        # 两个限流器相互独立
        assert len(limiter_a.timestamps) == 2
        assert len(limiter_b.timestamps) == 3


@pytest.mark.asyncio
async def test_discord_rate_limit_simulation():
    """模拟Discord限流：每5秒最多5条"""
    limiter = RateLimiter(calls=5, period=5)
    
    # 模拟发送10条消息
    send_times = []
    
    for i in range(10):
        await limiter.acquire()
        send_times.append(datetime.now())
    
    # 前5条应该很快发送
    first_batch_duration = (send_times[4] - send_times[0]).total_seconds()
    assert first_batch_duration < 1
    
    # 后5条应该等待约5秒
    second_batch_duration = (send_times[9] - send_times[4]).total_seconds()
    assert second_batch_duration >= 4


@pytest.mark.asyncio
async def test_telegram_rate_limit_simulation():
    """模拟Telegram限流：每秒最多30条"""
    limiter = RateLimiter(calls=30, period=1)
    
    # 模拟发送50条消息
    start_time = datetime.now()
    
    for i in range(50):
        await limiter.acquire()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    # 前30条立即发送，后20条需要等待约0.67秒
    assert elapsed >= 0.6  # 至少等待0.6秒
    assert elapsed < 2     # 不应该超过2秒


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
