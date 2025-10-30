#!/usr/bin/env python3
"""
性能测试脚本
✅ P2-6: 性能压力测试
"""
import asyncio
import time
import statistics
from typing import List, Dict
import sys
sys.path.insert(0, '../backend')

from app.utils.message_deduplicator import message_deduplicator
from app.queue.redis_queue_optimized import redis_queue_optimized, QueuePriority
from app.utils.rate_limiter import RateLimiter


class PerformanceTest:
    """性能测试"""
    
    def __init__(self):
        self.results = {}
    
    async def test_message_deduplicator(self, message_count: int = 10000):
        """测试消息去重性能"""
        print(f"\n📊 测试消息去重器（{message_count}条消息）...")
        
        # 预热
        for i in range(100):
            message_deduplicator.is_duplicate(f"warmup_{i}")
        
        # 测试写入
        start_time = time.time()
        
        for i in range(message_count):
            message_deduplicator.is_duplicate(f"message_{i}")
        
        write_time = time.time() - start_time
        write_qps = message_count / write_time
        
        # 测试查询
        start_time = time.time()
        
        for i in range(message_count):
            message_deduplicator.is_duplicate(f"message_{i}")
        
        query_time = time.time() - start_time
        query_qps = message_count / query_time
        
        self.results['deduplicator'] = {
            'message_count': message_count,
            'write_time': f"{write_time:.2f}s",
            'write_qps': f"{write_qps:.0f}/s",
            'query_time': f"{query_time:.2f}s",
            'query_qps': f"{query_qps:.0f}/s"
        }
        
        print(f"✅ 写入性能: {write_qps:.0f} QPS")
        print(f"✅ 查询性能: {query_qps:.0f} QPS")
        
        return write_qps, query_qps
    
    async def test_priority_queue(self, message_count: int = 5000):
        """测试优先级队列性能"""
        print(f"\n📊 测试优先级队列（{message_count}条消息）...")
        
        # 测试入队
        start_time = time.time()
        
        for i in range(message_count):
            priority = [
                QueuePriority.HIGH,
                QueuePriority.NORMAL,
                QueuePriority.LOW
            ][i % 3]
            
            await redis_queue_optimized.enqueue(
                {'id': i, 'content': f'test_{i}'},
                priority
            )
        
        enqueue_time = time.time() - start_time
        enqueue_qps = message_count / enqueue_time
        
        # 测试出队
        start_time = time.time()
        
        for i in range(message_count):
            message = await redis_queue_optimized.dequeue(timeout=1)
            if message:
                await redis_queue_optimized.ack(message)
        
        dequeue_time = time.time() - start_time
        dequeue_qps = message_count / dequeue_time
        
        self.results['priority_queue'] = {
            'message_count': message_count,
            'enqueue_time': f"{enqueue_time:.2f}s",
            'enqueue_qps': f"{enqueue_qps:.0f}/s",
            'dequeue_time': f"{dequeue_time:.2f}s",
            'dequeue_qps': f"{dequeue_qps:.0f}/s"
        }
        
        print(f"✅ 入队性能: {enqueue_qps:.0f} QPS")
        print(f"✅ 出队性能: {dequeue_qps:.0f} QPS")
        
        return enqueue_qps, dequeue_qps
    
    async def test_rate_limiter(self, request_count: int = 1000):
        """测试限流器性能"""
        print(f"\n📊 测试限流器（{request_count}次请求）...")
        
        limiter = RateLimiter(calls=100, period=1)
        
        # 测试限流性能
        start_time = time.time()
        success_count = 0
        
        for i in range(request_count):
            if await limiter.acquire():
                success_count += 1
        
        elapsed_time = time.time() - start_time
        actual_qps = success_count / elapsed_time
        
        self.results['rate_limiter'] = {
            'request_count': request_count,
            'success_count': success_count,
            'elapsed_time': f"{elapsed_time:.2f}s",
            'actual_qps': f"{actual_qps:.0f}/s",
            'limit_qps': '100/s'
        }
        
        print(f"✅ 实际QPS: {actual_qps:.0f}/s（限制: 100/s）")
        print(f"✅ 成功请求: {success_count}/{request_count}")
        
        return actual_qps
    
    async def test_concurrent_performance(self, concurrent_count: int = 100):
        """测试并发性能"""
        print(f"\n📊 测试并发性能（{concurrent_count}个并发）...")
        
        async def mock_task():
            """模拟任务"""
            start = time.time()
            await asyncio.sleep(0.01)  # 模拟IO操作
            return time.time() - start
        
        # 并发执行
        start_time = time.time()
        
        tasks = [mock_task() for _ in range(concurrent_count)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        avg_task_time = statistics.mean(results)
        
        self.results['concurrent'] = {
            'concurrent_count': concurrent_count,
            'total_time': f"{total_time:.2f}s",
            'avg_task_time': f"{avg_task_time*1000:.2f}ms",
            'tasks_per_second': f"{concurrent_count/total_time:.0f}/s"
        }
        
        print(f"✅ 总时间: {total_time:.2f}s")
        print(f"✅ 平均任务时间: {avg_task_time*1000:.2f}ms")
        print(f"✅ 吞吐量: {concurrent_count/total_time:.0f} tasks/s")
        
        return total_time
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("📊 性能测试总结")
        print("="*60)
        
        for test_name, result in self.results.items():
            print(f"\n【{test_name}】")
            for key, value in result.items():
                print(f"  {key}: {value}")
        
        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 KOOK消息转发系统 - 性能测试")
    print("="*60)
    
    tester = PerformanceTest()
    
    try:
        # 运行测试
        await tester.test_message_deduplicator(10000)
        await tester.test_priority_queue(5000)
        await tester.test_rate_limiter(1000)
        await tester.test_concurrent_performance(100)
        
        # 打印总结
        tester.print_summary()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
