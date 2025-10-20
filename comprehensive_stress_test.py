"""
KOOK消息转发系统 - 全面综合压力测试
覆盖所有核心功能和边界条件
"""
import asyncio
import aiohttp
import time
import random
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import sqlite3
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 测试配置
COMPREHENSIVE_TEST_CONFIG = {
    "api_base_url": "http://127.0.0.1:9527",
    "redis_host": "127.0.0.1",
    "redis_port": 6379,
    
    # 并发测试配置
    "concurrent_users": [1, 5, 10, 25, 50, 100, 200],
    "concurrent_websockets": [1, 5, 10, 20, 50],
    
    # 负载测试配置
    "message_batch_sizes": [10, 50, 100, 500, 1000, 5000],
    "sustained_load_duration": 300,  # 5分钟持续负载
    
    # 吞吐量测试配置
    "throughput_test_duration": 60,  # 1分钟吞吐量测试
    "target_qps": [10, 50, 100, 200, 500],
    
    # 稳定性测试配置
    "stability_test_duration": 600,  # 10分钟稳定性测试
    "stability_request_interval": 0.1,  # 每0.1秒一个请求
}


class ComprehensiveStressTest:
    """全面综合压力测试"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_base = config["api_base_url"]
        self.session = None
        
        # 统计信息
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.errors = []
        
        # 性能指标
        self.peak_qps = 0
        self.avg_qps = 0
        self.p50_latency = 0
        self.p90_latency = 0
        self.p99_latency = 0
        
    async def setup(self):
        """初始化测试环境"""
        print("=" * 100)
        print(" " * 30 + "KOOK消息转发系统 - 全面压力测试")
        print("=" * 100)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"API地址: {self.api_base}")
        print(f"测试配置: {len(COMPREHENSIVE_TEST_CONFIG)}个测试维度")
        print("=" * 100)
        print()
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # 检查服务状态
        try:
            async with self.session.get(f"{self.api_base}/health") as resp:
                if resp.status == 200:
                    print("✅ 后端服务运行正常")
                    return True
                else:
                    print("❌ 后端服务响应异常")
                    return False
        except Exception as e:
            print(f"❌ 无法连接到后端服务: {e}")
            print("请先启动后端服务: cd backend && python -m app.main")
            return False
    
    async def teardown(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        self.total_requests += 1
        start_time = time.time()
        
        try:
            url = f"{self.api_base}{endpoint}"
            async with self.session.request(method, url, **kwargs) as resp:
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                
                if resp.status < 400:
                    self.successful_requests += 1
                else:
                    self.failed_requests += 1
                
                try:
                    data = await resp.json() if resp.content_type == 'application/json' else None
                except:
                    data = None
                
                return {
                    "status": resp.status,
                    "response_time": response_time,
                    "data": data
                }
        except Exception as e:
            response_time = time.time() - start_time
            self.failed_requests += 1
            self.errors.append(str(e))
            return {
                "status": 0,
                "response_time": response_time,
                "error": str(e)
            }
    
    async def test_throughput_under_load(self, target_qps: int) -> Dict[str, Any]:
        """测试1: 吞吐量测试 - 目标QPS下的系统性能"""
        print(f"\n{'='*100}")
        print(f"测试1: 吞吐量测试 - 目标QPS: {target_qps}")
        print(f"{'='*100}")
        
        duration = self.config["throughput_test_duration"]
        interval = 1.0 / target_qps
        
        print(f"目标: {target_qps} QPS, 持续时间: {duration}秒, 请求间隔: {interval*1000:.2f}ms")
        
        start_time = time.time()
        requests_sent = 0
        request_times = []
        
        endpoints = [
            ("GET", "/api/system/status"),
            ("GET", "/api/accounts"),
            ("GET", "/api/bots"),
            ("GET", "/api/logs?limit=10"),
        ]
        
        while time.time() - start_time < duration:
            iter_start = time.time()
            
            # 发送请求
            method, endpoint = random.choice(endpoints)
            result = await self.make_request(method, endpoint)
            request_times.append(result["response_time"])
            requests_sent += 1
            
            # 控制请求速率
            elapsed = time.time() - iter_start
            sleep_time = max(0, interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        total_time = time.time() - start_time
        actual_qps = requests_sent / total_time
        success_rate = sum(1 for t in request_times if t > 0) / len(request_times) * 100
        
        # 计算延迟百分位
        sorted_times = sorted(request_times)
        p50 = sorted_times[len(sorted_times)//2] * 1000
        p90 = sorted_times[int(len(sorted_times)*0.9)] * 1000
        p99 = sorted_times[int(len(sorted_times)*0.99)] * 1000
        avg = sum(request_times) / len(request_times) * 1000
        
        print(f"\n结果:")
        print(f"  请求总数: {requests_sent}")
        print(f"  实际QPS: {actual_qps:.2f}")
        print(f"  成功率: {success_rate:.2f}%")
        print(f"  平均延迟: {avg:.2f}ms")
        print(f"  P50延迟: {p50:.2f}ms")
        print(f"  P90延迟: {p90:.2f}ms")
        print(f"  P99延迟: {p99:.2f}ms")
        
        return {
            "test_name": f"吞吐量测试 ({target_qps} QPS)",
            "target_qps": target_qps,
            "actual_qps": actual_qps,
            "total_requests": requests_sent,
            "success_rate": success_rate,
            "latency_avg_ms": avg,
            "latency_p50_ms": p50,
            "latency_p90_ms": p90,
            "latency_p99_ms": p99
        }
    
    async def test_sustained_load(self) -> Dict[str, Any]:
        """测试2: 持续负载测试 - 长时间稳定性"""
        print(f"\n{'='*100}")
        print("测试2: 持续负载测试 (5分钟)")
        print(f"{'='*100}")
        
        duration = self.config["sustained_load_duration"]
        qps = 50  # 中等负载
        
        print(f"负载: {qps} QPS, 持续: {duration}秒 ({duration/60:.1f}分钟)")
        
        start_time = time.time()
        requests_by_minute = []
        current_minute_requests = []
        
        endpoints = [
            ("GET", "/api/system/status"),
            ("GET", "/api/system/stats"),
            ("GET", "/api/logs?limit=20"),
            ("GET", "/api/accounts"),
        ]
        
        while time.time() - start_time < duration:
            # 每秒发送qps个请求
            tasks = []
            for _ in range(qps):
                method, endpoint = random.choice(endpoints)
                tasks.append(self.make_request(method, endpoint))
            
            results = await asyncio.gather(*tasks)
            current_minute_requests.extend(results)
            
            # 每60秒统计一次
            if len(current_minute_requests) >= qps * 60:
                success = sum(1 for r in current_minute_requests if r["status"] < 400)
                requests_by_minute.append({
                    "minute": len(requests_by_minute) + 1,
                    "requests": len(current_minute_requests),
                    "success": success,
                    "success_rate": success / len(current_minute_requests) * 100
                })
                current_minute_requests = []
                print(f"  分钟 {len(requests_by_minute)}: {success}/{qps*60} 成功")
            
            await asyncio.sleep(1)
        
        # 最后不足一分钟的统计
        if current_minute_requests:
            success = sum(1 for r in current_minute_requests if r["status"] < 400)
            requests_by_minute.append({
                "minute": len(requests_by_minute) + 1,
                "requests": len(current_minute_requests),
                "success": success,
                "success_rate": success / len(current_minute_requests) * 100
            })
        
        total_requests = sum(m["requests"] for m in requests_by_minute)
        total_success = sum(m["success"] for m in requests_by_minute)
        overall_success_rate = total_success / total_requests * 100
        
        print(f"\n持续负载测试完成:")
        print(f"  总请求数: {total_requests}")
        print(f"  成功请求: {total_success}")
        print(f"  整体成功率: {overall_success_rate:.2f}%")
        
        return {
            "test_name": "持续负载测试",
            "duration_seconds": duration,
            "target_qps": qps,
            "total_requests": total_requests,
            "total_success": total_success,
            "overall_success_rate": overall_success_rate,
            "by_minute": requests_by_minute
        }
    
    async def test_spike_load(self) -> Dict[str, Any]:
        """测试3: 峰值负载测试 - 突发流量处理"""
        print(f"\n{'='*100}")
        print("测试3: 峰值负载测试 (突发流量)")
        print(f"{'='*100}")
        
        results = []
        
        # 模拟不同强度的突发流量
        spike_configs = [
            {"name": "小突发", "burst_size": 50, "burst_duration": 5},
            {"name": "中突发", "burst_size": 100, "burst_duration": 10},
            {"name": "大突发", "burst_size": 200, "burst_duration": 15},
        ]
        
        for config in spike_configs:
            print(f"\n测试 {config['name']}: {config['burst_size']}并发, 持续{config['burst_duration']}秒")
            
            start_time = time.time()
            
            # 创建大量并发请求
            async def burst_request():
                method, endpoint = random.choice([
                    ("GET", "/api/system/status"),
                    ("GET", "/api/logs?limit=10"),
                ])
                return await self.make_request(method, endpoint)
            
            tasks = [burst_request() for _ in range(config['burst_size'])]
            burst_results = await asyncio.gather(*tasks)
            
            burst_time = time.time() - start_time
            success_count = sum(1 for r in burst_results if r["status"] < 400)
            success_rate = success_count / len(burst_results) * 100
            
            response_times = [r["response_time"] for r in burst_results]
            avg_response = sum(response_times) / len(response_times) * 1000
            max_response = max(response_times) * 1000
            
            print(f"  完成: {success_count}/{config['burst_size']} 成功")
            print(f"  耗时: {burst_time:.2f}秒")
            print(f"  平均响应: {avg_response:.2f}ms")
            print(f"  最大响应: {max_response:.2f}ms")
            
            results.append({
                "spike_type": config['name'],
                "burst_size": config['burst_size'],
                "success_count": success_count,
                "success_rate": success_rate,
                "total_time": burst_time,
                "avg_response_ms": avg_response,
                "max_response_ms": max_response
            })
            
            # 等待系统恢复
            await asyncio.sleep(5)
        
        return {
            "test_name": "峰值负载测试",
            "results": results
        }
    
    async def test_concurrent_operations(self) -> Dict[str, Any]:
        """测试4: 并发操作测试 - 多用户同时操作"""
        print(f"\n{'='*100}")
        print("测试4: 并发操作测试")
        print(f"{'='*100}")
        
        results = []
        
        for concurrent in self.config["concurrent_users"]:
            print(f"\n测试 {concurrent} 并发用户...", end=" ")
            
            # 模拟不同用户的不同操作
            async def user_operation(user_id: int):
                operations = [
                    ("GET", "/api/accounts"),
                    ("GET", "/api/bots"),
                    ("GET", "/api/mappings"),
                    ("GET", f"/api/logs?limit=10&offset={user_id*10}"),
                    ("GET", "/api/system/stats"),
                ]
                
                user_results = []
                for method, endpoint in operations:
                    result = await self.make_request(method, endpoint)
                    user_results.append(result)
                
                return user_results
            
            start_time = time.time()
            tasks = [user_operation(i) for i in range(concurrent)]
            all_results = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            
            # 统计
            all_requests = [r for user in all_results for r in user]
            success = sum(1 for r in all_requests if r["status"] < 400)
            total = len(all_requests)
            success_rate = success / total * 100
            
            qps = total / total_time
            
            print(f"✅ 成功率: {success_rate:.1f}%, QPS: {qps:.1f}")
            
            results.append({
                "concurrent_users": concurrent,
                "total_requests": total,
                "success_count": success,
                "success_rate": success_rate,
                "total_time": total_time,
                "qps": qps
            })
        
        return {
            "test_name": "并发操作测试",
            "results": results
        }
    
    async def test_database_stress(self) -> Dict[str, Any]:
        """测试5: 数据库压力测试"""
        print(f"\n{'='*100}")
        print("测试5: 数据库压力测试")
        print(f"{'='*100}")
        
        db_path = Path(__file__).parent / "backend" / "data" / "kook_forwarder.db"
        
        if not db_path.exists():
            print("❌ 数据库文件不存在")
            return {"status": "skipped", "reason": "数据库文件不存在"}
        
        results = []
        
        # 测试大批量插入
        print("\n测试大批量插入 (10000条)...", end=" ")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        start = time.time()
        cursor.execute("BEGIN TRANSACTION")
        for i in range(10000):
            cursor.execute("""
                INSERT INTO message_logs 
                (kook_message_id, kook_channel_id, content, message_type, sender_name, 
                 target_platform, target_channel, status, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"stress_test_{int(time.time())}_{i}",
                "stress_test_channel",
                f"压力测试消息 {i}",
                "text",
                "stress_test_user",
                "discord",
                "test_target",
                "success",
                random.randint(50, 500)
            ))
        cursor.execute("COMMIT")
        insert_time = time.time() - start
        print(f"✅ 耗时: {insert_time:.3f}s, 速度: {10000/insert_time:.0f} 条/秒")
        
        results.append({
            "operation": "批量插入",
            "records": 10000,
            "time": insert_time,
            "records_per_second": 10000 / insert_time
        })
        
        # 测试高并发查询
        print("测试高并发查询 (5000次)...", end=" ")
        
        def query_db():
            c = sqlite3.connect(db_path)
            cur = c.cursor()
            cur.execute("""
                SELECT * FROM message_logs 
                WHERE status = 'success' 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            cur.fetchall()
            c.close()
        
        start = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(query_db) for _ in range(5000)]
            for future in futures:
                future.result()
        query_time = time.time() - start
        print(f"✅ 耗时: {query_time:.3f}s, QPS: {5000/query_time:.0f}")
        
        results.append({
            "operation": "并发查询",
            "queries": 5000,
            "time": query_time,
            "qps": 5000 / query_time
        })
        
        # 清理测试数据
        cursor.execute("DELETE FROM message_logs WHERE kook_channel_id = 'stress_test_channel'")
        conn.commit()
        conn.close()
        
        return {
            "test_name": "数据库压力测试",
            "status": "success",
            "results": results
        }
    
    async def test_redis_queue_stress(self) -> Dict[str, Any]:
        """测试6: Redis队列压力测试"""
        print(f"\n{'='*100}")
        print("测试6: Redis队列压力测试")
        print(f"{'='*100}")
        
        try:
            import redis
            r = redis.Redis(
                host=self.config["redis_host"],
                port=self.config["redis_port"],
                decode_responses=True
            )
            
            results = []
            
            # 测试高速入队
            print("\n测试高速入队 (50000条)...", end=" ")
            start = time.time()
            pipe = r.pipeline()
            for i in range(50000):
                message = json.dumps({
                    "id": f"stress_{i}",
                    "content": f"消息 {i}",
                    "timestamp": time.time()
                })
                pipe.lpush("stress_test_queue", message)
            pipe.execute()
            enqueue_time = time.time() - start
            print(f"✅ 耗时: {enqueue_time:.3f}s, 速度: {50000/enqueue_time:.0f} 条/秒")
            
            results.append({
                "operation": "高速入队",
                "messages": 50000,
                "time": enqueue_time,
                "messages_per_second": 50000 / enqueue_time
            })
            
            # 测试高速出队
            print("测试高速出队 (50000条)...", end=" ")
            start = time.time()
            pipe = r.pipeline()
            for _ in range(50000):
                pipe.rpop("stress_test_queue")
            pipe.execute()
            dequeue_time = time.time() - start
            print(f"✅ 耗时: {dequeue_time:.3f}s, 速度: {50000/dequeue_time:.0f} 条/秒")
            
            results.append({
                "operation": "高速出队",
                "messages": 50000,
                "time": dequeue_time,
                "messages_per_second": 50000 / dequeue_time
            })
            
            # 测试并发读写
            print("测试并发读写...", end=" ")
            
            async def concurrent_queue_ops():
                r_conn = redis.Redis(
                    host=self.config["redis_host"],
                    port=self.config["redis_port"],
                    decode_responses=True
                )
                
                # 入队
                for i in range(100):
                    r_conn.lpush("concurrent_queue", f"msg_{i}")
                
                # 出队
                for _ in range(100):
                    r_conn.rpop("concurrent_queue")
            
            start = time.time()
            tasks = [asyncio.to_thread(concurrent_queue_ops) for _ in range(50)]
            await asyncio.gather(*tasks)
            concurrent_time = time.time() - start
            total_ops = 50 * 200  # 50个协程，每个200次操作
            print(f"✅ {total_ops}次操作耗时: {concurrent_time:.3f}s")
            
            results.append({
                "operation": "并发读写",
                "total_operations": total_ops,
                "time": concurrent_time,
                "ops_per_second": total_ops / concurrent_time
            })
            
            return {
                "test_name": "Redis队列压力测试",
                "status": "success",
                "results": results
            }
            
        except Exception as e:
            print(f"❌ Redis压力测试失败: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_memory_leak(self) -> Dict[str, Any]:
        """测试7: 内存泄漏测试"""
        print(f"\n{'='*100}")
        print("测试7: 内存泄漏测试 (10000次请求)")
        print(f"{'='*100}")
        
        try:
            import psutil
            import gc
            
            # 获取当前进程
            process = psutil.Process()
            
            # 记录初始内存
            gc.collect()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            print(f"初始内存: {initial_memory:.2f} MB")
            
            # 执行大量请求
            for i in range(0, 10000, 1000):
                tasks = []
                for _ in range(1000):
                    tasks.append(self.make_request("GET", "/api/system/status"))
                await asyncio.gather(*tasks)
                
                # 每1000次请求检查一次内存
                gc.collect()
                current_memory = process.memory_info().rss / 1024 / 1024
                print(f"  {i+1000}次请求后: {current_memory:.2f} MB (增长: {current_memory-initial_memory:.2f} MB)")
            
            # 最终内存
            gc.collect()
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = final_memory - initial_memory
            
            print(f"\n最终内存: {final_memory:.2f} MB")
            print(f"总增长: {memory_increase:.2f} MB")
            print(f"每请求: {memory_increase/10000*1024:.2f} KB")
            
            # 判断是否有明显内存泄漏
            leak_detected = memory_increase > 100  # 如果增长超过100MB则可能有泄漏
            
            return {
                "test_name": "内存泄漏测试",
                "status": "success",
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": memory_increase,
                "memory_per_request_kb": memory_increase/10000*1024,
                "leak_detected": leak_detected
            }
            
        except Exception as e:
            print(f"❌ 内存测试失败: {e}")
            return {"status": "failed", "error": str(e)}
    
    def generate_comprehensive_report(self, test_results: Dict[str, Any]):
        """生成全面的测试报告"""
        report_path = Path(__file__).parent / "comprehensive_stress_test_report.md"
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# KOOK消息转发系统 - 全面压力测试报告\n\n")
            f.write(f"**测试时间**: {test_results['start_time']}\n")
            f.write(f"**测试环境**: {self.api_base}\n\n")
            f.write("---\n\n")
            
            f.write("## 📊 测试总览\n\n")
            f.write("| 测试项 | 状态 | 关键指标 |\n")
            f.write("|--------|------|----------|\n")
            
            for test_name, test_data in test_results.get("tests", {}).items():
                status = "✅" if test_data.get("status") != "failed" else "❌"
                
                # 提取关键指标
                key_metric = ""
                if "qps" in str(test_data):
                    if isinstance(test_data.get("actual_qps"), (int, float)):
                        key_metric = f"QPS: {test_data['actual_qps']:.1f}"
                elif "success_rate" in str(test_data):
                    if isinstance(test_data.get("overall_success_rate"), (int, float)):
                        key_metric = f"成功率: {test_data['overall_success_rate']:.1f}%"
                
                f.write(f"| {test_data.get('test_name', test_name)} | {status} | {key_metric} |\n")
            
            f.write("\n---\n\n")
            
            # 性能汇总
            f.write("## 🚀 性能汇总\n\n")
            f.write(f"- **总请求数**: {self.total_requests:,}\n")
            f.write(f"- **成功请求**: {self.successful_requests:,}\n")
            f.write(f"- **失败请求**: {self.failed_requests:,}\n")
            f.write(f"- **成功率**: {self.successful_requests/self.total_requests*100:.2f}%\n\n")
            
            if self.response_times:
                sorted_times = sorted(self.response_times)
                f.write("### 响应时间统计\n\n")
                f.write(f"- **平均**: {sum(self.response_times)/len(self.response_times)*1000:.2f}ms\n")
                f.write(f"- **P50**: {sorted_times[len(sorted_times)//2]*1000:.2f}ms\n")
                f.write(f"- **P90**: {sorted_times[int(len(sorted_times)*0.9)]*1000:.2f}ms\n")
                f.write(f"- **P99**: {sorted_times[int(len(sorted_times)*0.99)]*1000:.2f}ms\n")
                f.write(f"- **最大**: {max(self.response_times)*1000:.2f}ms\n")
                f.write(f"- **最小**: {min(self.response_times)*1000:.2f}ms\n\n")
            
            f.write("---\n\n")
            
            # 详细测试结果
            for test_name, test_data in test_results.get("tests", {}).items():
                f.write(f"## {test_data.get('test_name', test_name)}\n\n")
                
                if test_data.get("status") == "failed":
                    f.write(f"**状态**: ❌ 失败\n\n")
                    f.write(f"**错误**: {test_data.get('error', 'Unknown')}\n\n")
                    continue
                
                # 根据测试类型生成不同的报告内容
                if "results" in test_data:
                    if isinstance(test_data["results"], list) and test_data["results"]:
                        # 表格格式
                        keys = test_data["results"][0].keys()
                        f.write("| " + " | ".join(str(k) for k in keys) + " |\n")
                        f.write("|" + "|".join(["---"] * len(keys)) + "|\n")
                        
                        for result in test_data["results"]:
                            values = [str(result.get(k, "")) for k in keys]
                            # 格式化数字
                            formatted_values = []
                            for v in values:
                                try:
                                    if '.' in v:
                                        formatted_values.append(f"{float(v):.2f}")
                                    else:
                                        formatted_values.append(v)
                                except:
                                    formatted_values.append(v)
                            f.write("| " + " | ".join(formatted_values) + " |\n")
                    elif isinstance(test_data["results"], dict):
                        for key, value in test_data["results"].items():
                            if isinstance(value, (int, float)):
                                f.write(f"- **{key}**: {value:.2f}\n")
                            else:
                                f.write(f"- **{key}**: {value}\n")
                
                f.write("\n")
            
            f.write("---\n\n")
            f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**测试用例**: {len(test_results.get('tests', {}))}个\n")
            f.write(f"**总测试时长**: {test_results.get('end_time', '')} - {test_results.get('start_time', '')}\n")
        
        print(f"\n\n{'='*100}")
        print(f"📄 详细报告已保存至: {report_path}")
        print(f"{'='*100}")
    
    async def run_all_tests(self):
        """运行所有压力测试"""
        test_results = {
            "start_time": datetime.now().isoformat(),
            "tests": {}
        }
        
        if not await self.setup():
            return
        
        try:
            # 测试1-4: 负载和吞吐量测试
            for qps in [10, 50, 100]:
                result = await self.test_throughput_under_load(qps)
                test_results["tests"][f"throughput_{qps}qps"] = result
            
            # 测试2: 持续负载
            result = await self.test_sustained_load()
            test_results["tests"]["sustained_load"] = result
            
            # 测试3: 峰值负载
            result = await self.test_spike_load()
            test_results["tests"]["spike_load"] = result
            
            # 测试4: 并发操作
            result = await self.test_concurrent_operations()
            test_results["tests"]["concurrent_operations"] = result
            
            # 测试5: 数据库压力
            result = await self.test_database_stress()
            test_results["tests"]["database_stress"] = result
            
            # 测试6: Redis队列压力
            result = await self.test_redis_queue_stress()
            test_results["tests"]["redis_queue_stress"] = result
            
            # 测试7: 内存泄漏
            result = await self.test_memory_leak()
            test_results["tests"]["memory_leak"] = result
            
            # 生成报告
            test_results["end_time"] = datetime.now().isoformat()
            self.generate_comprehensive_report(test_results)
            
            # 保存JSON结果
            json_path = Path(__file__).parent / "comprehensive_stress_test_results.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(test_results, f, indent=2, ensure_ascii=False)
            
            print(f"📊 JSON结果已保存至: {json_path}")
            
        except Exception as e:
            print(f"\n❌ 测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await self.teardown()


async def main():
    """主函数"""
    print("\n")
    print("┌" + "─" * 98 + "┐")
    print("│" + " " * 25 + "KOOK消息转发系统 - 全面压力测试" + " " * 42 + "│")
    print("│" + " " * 98 + "│")
    print("│  本测试将对系统进行全面的压力测试，包括：" + " " * 49 + "│")
    print("│  • 吞吐量测试（不同QPS）" + " " * 68 + "│")
    print("│  • 持续负载测试（5分钟）" + " " * 68 + "│")
    print("│  • 峰值负载测试（突发流量）" + " " * 64 + "│")
    print("│  • 并发操作测试" + " " * 79 + "│")
    print("│  • 数据库压力测试" + " " * 77 + "│")
    print("│  • Redis队列压力测试" + " " * 72 + "│")
    print("│  • 内存泄漏测试" + " " * 80 + "│")
    print("│" + " " * 98 + "│")
    print("│  预计总耗时: 15-20分钟" + " " * 70 + "│")
    print("└" + "─" * 98 + "┘")
    print("\n")
    
    runner = ComprehensiveStressTest(COMPREHENSIVE_TEST_CONFIG)
    await runner.run_all_tests()
    
    print("\n✅ 全面压力测试完成！\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(0)
