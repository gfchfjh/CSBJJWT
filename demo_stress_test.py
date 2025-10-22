"""
压力测试演示 - 无需后端服务即可运行
展示测试框架的功能和生成测试报告
"""
import asyncio
import time
import json
import random
import statistics
from pathlib import Path
from datetime import datetime


class DemoStressTest:
    """演示版压力测试"""
    
    def __init__(self):
        self.results = {}
        self.stats = {
            "start_time": datetime.now(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
        }
    
    def print_header(self, text):
        """打印标题"""
        print("\n" + "=" * 80)
        print(f"  {text}")
        print("=" * 80 + "\n")
    
    def print_success(self, text):
        """打印成功信息"""
        print(f"✅ {text}")
    
    def print_info(self, text):
        """打印信息"""
        print(f"ℹ️  {text}")
    
    # ==================== 测试1: 消息格式转换性能 ====================
    
    async def test_message_formatting(self):
        """测试消息格式转换性能"""
        self.print_header("测试1: 消息格式转换性能")
        self.stats["total_tests"] += 1
        
        try:
            # 模拟格式转换
            test_texts = [
                "**粗体** *斜体* `代码`",
                "这是一条很长的消息" + "测试 " * 100,
                "@用户名 @全体成员 http://example.com",
            ]
            
            results = []
            
            for iterations in [1000, 5000, 10000]:
                self.print_info(f"迭代次数: {iterations}")
                
                # 模拟Discord转换
                start = time.time()
                for _ in range(iterations):
                    for text in test_texts:
                        # 模拟转换操作
                        converted = text.replace("**", "").replace("*", "").replace("`", "")
                duration = time.time() - start
                
                ops_per_sec = (iterations * len(test_texts)) / duration
                results.append({
                    "iterations": iterations,
                    "duration_seconds": round(duration, 3),
                    "ops_per_second": round(ops_per_sec, 2),
                })
                
                print(f"  ✓ 耗时: {duration:.3f}s, 性能: {ops_per_sec:.2f} ops/s")
            
            self.results["message_formatting"] = results
            self.stats["passed_tests"] += 1
            self.print_success("消息格式转换测试完成")
            
        except Exception as e:
            self.stats["failed_tests"] += 1
            print(f"❌ 测试失败: {e}")
    
    # ==================== 测试2: 并发处理能力 ====================
    
    async def test_concurrent_processing(self):
        """测试并发处理能力"""
        self.print_header("测试2: 并发处理能力")
        self.stats["total_tests"] += 1
        
        try:
            results = []
            
            for concurrent in [10, 50, 100, 200]:
                self.print_info(f"并发数: {concurrent}")
                
                async def process_message(msg_id):
                    """模拟消息处理"""
                    # 模拟各种操作
                    await asyncio.sleep(0.01)  # 格式转换
                    await asyncio.sleep(0.005)  # 过滤
                    await asyncio.sleep(0.015)  # 转发
                    return True
                
                # 并发处理
                start = time.time()
                tasks = [process_message(i) for i in range(concurrent)]
                responses = await asyncio.gather(*tasks)
                duration = time.time() - start
                
                successful = sum(1 for r in responses if r)
                throughput = concurrent / duration
                
                results.append({
                    "concurrent": concurrent,
                    "successful": successful,
                    "duration_seconds": round(duration, 3),
                    "throughput": round(throughput, 2),
                })
                
                print(f"  ✓ 成功: {successful}/{concurrent}, "
                      f"吞吐量: {throughput:.2f} msg/s")
            
            self.results["concurrent_processing"] = results
            self.stats["passed_tests"] += 1
            self.print_success("并发处理测试完成")
            
        except Exception as e:
            self.stats["failed_tests"] += 1
            print(f"❌ 测试失败: {e}")
    
    # ==================== 测试3: 内存队列性能 ====================
    
    async def test_queue_performance(self):
        """测试队列性能"""
        self.print_header("测试3: 内存队列性能")
        self.stats["total_tests"] += 1
        
        try:
            from collections import deque
            
            results = []
            
            for batch_size in [100, 500, 1000, 5000]:
                self.print_info(f"批量大小: {batch_size}")
                
                queue = deque()
                
                # 测试入队
                start = time.time()
                for i in range(batch_size):
                    queue.append({
                        "id": f"msg_{i}",
                        "content": f"测试消息 {i}",
                        "timestamp": time.time()
                    })
                enqueue_time = time.time() - start
                
                # 测试出队
                start = time.time()
                while queue:
                    queue.popleft()
                dequeue_time = time.time() - start
                
                results.append({
                    "batch_size": batch_size,
                    "enqueue_time": round(enqueue_time, 3),
                    "dequeue_time": round(dequeue_time, 3),
                    "enqueue_qps": round(batch_size / enqueue_time, 2),
                    "dequeue_qps": round(batch_size / dequeue_time, 2),
                })
                
                print(f"  ✓ 入队: {batch_size/enqueue_time:.2f} msg/s, "
                      f"出队: {batch_size/dequeue_time:.2f} msg/s")
            
            self.results["queue_performance"] = results
            self.stats["passed_tests"] += 1
            self.print_success("队列性能测试完成")
            
        except Exception as e:
            self.stats["failed_tests"] += 1
            print(f"❌ 测试失败: {e}")
    
    # ==================== 测试4: 限流器准确性 ====================
    
    async def test_rate_limiter(self):
        """测试限流器准确性"""
        self.print_header("测试4: 限流器准确性")
        self.stats["total_tests"] += 1
        
        try:
            from collections import deque
            from datetime import timedelta
            
            class SimpleLimiter:
                def __init__(self, calls, period):
                    self.calls = calls
                    self.period = period
                    self.timestamps = deque()
                
                async def acquire(self):
                    now = datetime.now()
                    
                    # 清理过期时间戳
                    while self.timestamps and self.timestamps[0] < now - timedelta(seconds=self.period):
                        self.timestamps.popleft()
                    
                    # 限流
                    if len(self.timestamps) >= self.calls:
                        sleep_time = (self.timestamps[0] + timedelta(seconds=self.period) - now).total_seconds()
                        if sleep_time > 0:
                            await asyncio.sleep(sleep_time)
                            return await self.acquire()
                    
                    self.timestamps.append(now)
            
            results = []
            
            configs = [
                (5, 1, "5请求/秒"),
                (10, 1, "10请求/秒"),
                (20, 2, "20请求/2秒"),
            ]
            
            for calls, period, name in configs:
                self.print_info(f"测试 {name}")
                
                limiter = SimpleLimiter(calls, period)
                
                # 发送 calls * 2 个请求
                total_requests = calls * 2
                
                start = time.time()
                for _ in range(total_requests):
                    await limiter.acquire()
                duration = time.time() - start
                
                # 理论时间
                expected_time = period * (total_requests / calls - 1)
                accuracy = (1 - abs(duration - expected_time) / expected_time) * 100 if expected_time > 0 else 100
                
                results.append({
                    "config": name,
                    "requests": total_requests,
                    "actual_time": round(duration, 2),
                    "expected_time": round(expected_time, 2),
                    "accuracy": round(accuracy, 2),
                })
                
                print(f"  ✓ 实际: {duration:.2f}s, 预期: {expected_time:.2f}s, "
                      f"准确度: {accuracy:.2f}%")
            
            self.results["rate_limiter"] = results
            self.stats["passed_tests"] += 1
            self.print_success("限流器测试完成")
            
        except Exception as e:
            self.stats["failed_tests"] += 1
            print(f"❌ 测试失败: {e}")
    
    # ==================== 测试5: 数据序列化性能 ====================
    
    async def test_serialization(self):
        """测试数据序列化性能"""
        self.print_header("测试5: 数据序列化性能")
        self.stats["total_tests"] += 1
        
        try:
            # 生成测试数据
            test_data = [
                {
                    "message_id": f"test_{i}",
                    "channel_id": f"channel_{i % 100}",
                    "content": f"这是测试消息 {i}，包含一些中文内容" * 5,
                    "sender": {"id": f"user_{i}", "name": f"用户{i}"},
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "platform": "discord",
                        "priority": random.choice(["high", "medium", "low"]),
                        "tags": [f"tag_{j}" for j in range(5)],
                    }
                }
                for i in range(1000)
            ]
            
            results = []
            
            # JSON序列化
            start = time.time()
            for data in test_data:
                json.dumps(data, ensure_ascii=False)
            json_serialize_time = time.time() - start
            
            # JSON反序列化
            json_strings = [json.dumps(data, ensure_ascii=False) for data in test_data]
            start = time.time()
            for json_str in json_strings:
                json.loads(json_str)
            json_deserialize_time = time.time() - start
            
            results.append({
                "format": "JSON",
                "operations": 1000,
                "serialize_time": round(json_serialize_time, 3),
                "deserialize_time": round(json_deserialize_time, 3),
                "serialize_qps": round(1000 / json_serialize_time, 2),
                "deserialize_qps": round(1000 / json_deserialize_time, 2),
            })
            
            self.print_info("JSON序列化测试")
            print(f"  ✓ 序列化: {1000/json_serialize_time:.2f} ops/s")
            print(f"  ✓ 反序列化: {1000/json_deserialize_time:.2f} ops/s")
            
            self.results["serialization"] = results
            self.stats["passed_tests"] += 1
            self.print_success("序列化性能测试完成")
            
        except Exception as e:
            self.stats["failed_tests"] += 1
            print(f"❌ 测试失败: {e}")
    
    # ==================== 测试6: 过滤器性能 ====================
    
    async def test_filter_performance(self):
        """测试过滤器性能"""
        self.print_header("测试6: 过滤器性能")
        self.stats["total_tests"] += 1
        
        try:
            # 准备测试数据
            blacklist_keywords = ["广告", "代练", "外挂", "刷钻", "辅助"]
            test_messages = []
            
            # 1000条正常消息
            for i in range(1000):
                test_messages.append({
                    "id": f"normal_{i}",
                    "content": f"这是正常消息 {i}",
                })
            
            # 500条包含黑名单关键词
            for i in range(500):
                keyword = random.choice(blacklist_keywords)
                test_messages.append({
                    "id": f"blocked_{i}",
                    "content": f"这是{keyword}消息",
                })
            
            random.shuffle(test_messages)
            
            # 测试过滤性能
            start = time.time()
            passed = 0
            for msg in test_messages:
                content = msg.get("content", "")
                if not any(kw in content for kw in blacklist_keywords):
                    passed += 1
            filter_time = time.time() - start
            
            result = {
                "total_messages": len(test_messages),
                "passed": passed,
                "blocked": len(test_messages) - passed,
                "filter_time": round(filter_time, 3),
                "filter_qps": round(len(test_messages) / filter_time, 2),
            }
            
            self.print_info(f"处理: {len(test_messages)}条消息")
            print(f"  ✓ 通过: {passed}条, 拦截: {len(test_messages) - passed}条")
            print(f"  ✓ 性能: {result['filter_qps']:.2f} msg/s")
            
            self.results["filter_performance"] = result
            self.stats["passed_tests"] += 1
            self.print_success("过滤器测试完成")
            
        except Exception as e:
            self.stats["failed_tests"] += 1
            print(f"❌ 测试失败: {e}")
    
    # ==================== 主测试流程 ====================
    
    async def run_all_tests(self):
        """运行所有测试"""
        self.print_header("KOOK消息转发系统 - 压力测试演示")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"说明: 这是演示版本,无需后端服务即可运行\n")
        
        # 运行所有测试
        await self.test_message_formatting()
        await self.test_concurrent_processing()
        await self.test_queue_performance()
        await self.test_rate_limiter()
        await self.test_serialization()
        await self.test_filter_performance()
        
        # 打印总结
        self.print_summary()
        
        # 保存报告
        self.save_report()
    
    def print_summary(self):
        """打印测试总结"""
        self.print_header("测试总结")
        
        duration = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        print(f"总耗时: {duration:.2f}秒")
        print(f"总测试数: {self.stats['total_tests']}")
        print(f"通过: {self.stats['passed_tests']}")
        print(f"失败: {self.stats['failed_tests']}")
        
        if self.stats['total_tests'] > 0:
            success_rate = (self.stats['passed_tests'] / self.stats['total_tests']) * 100
            print(f"成功率: {success_rate:.2f}%")
        
        print("\n完成的测试模块:")
        for test_name in self.results.keys():
            print(f"  ✅ {test_name}")
    
    def save_report(self):
        """保存测试报告"""
        # 创建目录
        Path("test_results").mkdir(exist_ok=True)
        
        # JSON报告
        report_data = {
            "test_time": self.stats["start_time"].isoformat(),
            "duration_seconds": (datetime.now() - self.stats["start_time"]).total_seconds(),
            "stats": self.stats,
            "results": self.results,
        }
        
        json_path = Path("test_results/demo_stress_test_report.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.print_success(f"JSON报告已保存: {json_path}")
        
        # Markdown报告
        md_path = Path("test_results/演示压力测试报告.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# KOOK消息转发系统 - 压力测试演示报告\n\n")
            f.write(f"**测试时间**: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 📊 测试概览\n\n")
            f.write("| 指标 | 值 |\n")
            f.write("|------|----|\n")
            f.write(f"| 总测试数 | {self.stats['total_tests']} |\n")
            f.write(f"| 通过测试 | {self.stats['passed_tests']} |\n")
            f.write(f"| 失败测试 | {self.stats['failed_tests']} |\n")
            
            success_rate = (self.stats['passed_tests'] / self.stats['total_tests']) * 100 if self.stats['total_tests'] > 0 else 0
            f.write(f"| 成功率 | {success_rate:.2f}% |\n")
            f.write("\n---\n\n")
            
            # 各测试详细结果
            for test_name, test_results in self.results.items():
                f.write(f"## {test_name}\n\n")
                
                if isinstance(test_results, list) and test_results:
                    # 表格格式
                    keys = list(test_results[0].keys())
                    f.write("| " + " | ".join(keys) + " |\n")
                    f.write("|" + "|".join(["---"] * len(keys)) + "|\n")
                    
                    for result in test_results:
                        values = [str(result.get(k, "")) for k in keys]
                        f.write("| " + " | ".join(values) + " |\n")
                    f.write("\n")
                elif isinstance(test_results, dict):
                    for key, value in test_results.items():
                        f.write(f"- **{key}**: {value}\n")
                    f.write("\n")
        
        self.print_success(f"Markdown报告已保存: {md_path}")


async def main():
    """主函数"""
    tester = DemoStressTest()
    
    try:
        await tester.run_all_tests()
        print("\n✅ 演示测试完成！")
        print("\n💡 提示: 这是演示版本，展示了测试框架的功能")
        print("   要运行完整测试，请启动后端服务和Redis，然后运行:")
        print("   - ./run_all_stress_tests.sh (Linux/macOS)")
        print("   - run_all_stress_tests.bat (Windows)")
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
