"""
限流器测试
"""
import pytest
import asyncio
from app.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """限流器测试类"""
    
    @pytest.mark.asyncio
    async def test_basic_rate_limiting(self):
        """测试基本限流功能"""
        limiter = RateLimiter(calls=5, period=1)
        
        # 前5次应该立即通过
        for i in range(5):
            await limiter.acquire()
        
        # 第6次应该被限流
        import time
        start = time.time()
        await limiter.acquire()
        elapsed = time.time() - start
        
        # 应该等待约1秒
        assert elapsed >= 0.9
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求"""
        limiter = RateLimiter(calls=10, period=1)
        
        async def make_request():
            await limiter.acquire()
            return True
        
        # 创建20个并发请求
        tasks = [make_request() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        
        # 所有请求都应该成功
        assert all(results)
    
    def test_try_acquire(self):
        """测试非阻塞获取"""
        limiter = RateLimiter(calls=2, period=1)
        
        # 前2次应该成功
        assert limiter.try_acquire() == True
        assert limiter.try_acquire() == True
        
        # 第3次应该失败
        assert limiter.try_acquire() == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
