"""
KOOK消息转发系统 - 全面压力测试
根据需求文档对所有功能进行压力测试
"""
import asyncio
import aiohttp
import time
import random
import json
import sys
import os
import sqlite3
import psutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 测试配置
TEST_CONFIG = {
    "api_base_url": "http://127.0.0.1:9527",
    "redis_host": "127.0.0.1",
    "redis_port": 6379,
    
    # 压力测试参数
    "concurrent_users": [1, 5, 10, 20, 50, 100],  # 并发用户数
    "test_duration": 30,  # 每个测试持续时间（秒）
    "message_batch_sizes": [10, 50, 100, 500, 1000, 5000],  # 消息批量大小
    "large_message_sizes": [1000, 5000, 10000, 50000],  # 大消息大小（字符）
    "image_sizes": [(800, 600), (1920, 1080), (4096, 3072), (8192, 6144)],  # 图片尺寸
    
    # 限流配置
    "discord_rate": (5, 5),  # 5请求/5秒
    "telegram_rate": (30, 1),  # 30请求/1秒
    "feishu_rate": (20, 1),  # 20请求/1秒
}

# 测试结果存储
test_results = {
    "start_time": None,
    "end_time": None,
    "system_info": {},
    "tests": {},
    "summary": {}
}


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        self.initial_cpu = self.process.cpu_percent()
        self.samples = []
    
    def record_sample(self):
        """记录性能样本"""
        sample = {
            "timestamp": time.time(),
            "memory_mb": self.process.memory_info().rss / 1024 / 1024,
            "cpu_percent": self.process.cpu_percent(),
            "threads": self.process.num_threads(),
            "connections": len(self.process.connections()) if hasattr(self.process, 'connections') else 0
        }
        self.samples.append(sample)
        return sample
    
    def get_stats(self):
        """获取性能统计"""
        if not self.samples:
            return {}
        
        memory_values = [s["memory_mb"] for s in self.samples]
        cpu_values = [s["cpu_percent"] for s in self.samples]
        
        return {
            "memory": {
                "min_mb": min(memory_values),
                "max_mb": max(memory_values),
                "avg_mb": statistics.mean(memory_values),
                "growth_mb": memory_values[-1] - memory_values[0]
            },
            "cpu": {
                "min_percent": min(cpu_values),
                "max_percent": max(cpu_values),
                "avg_percent": statistics.mean(cpu_values)
            },
            "threads": {
                "min": min(s["threads"] for s in self.samples),
                "max": max(s["threads"] for s in self.samples)
            }
        }


class ComprehensiveStressTest:
    """全面压力测试运行器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_base = config["api_base_url"]
        self.session: Optional[aiohttp.ClientSession] = None
        self.monitor = PerformanceMonitor()
        
        # 统计计数器
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.errors = []
    
    async def setup(self):
        """初始化测试环境"""
        print("=" * 100)
        print("KOOK消息转发系统 - 全面压力测试")
        print("=" * 100)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"API地址: {self.api_base}")
        
        # 记录系统信息
        test_results["system_info"] = {
            "platform": sys.platform,
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "total_memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
            "available_memory_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024
        }
        
        print(f"系统: {test_results['system_info']['platform']}")
        print(f"CPU核心: {test_results['system_info']['cpu_count']}")
        print(f"内存: {test_results['system_info']['total_memory_gb']:.2f}GB")
        print("=" * 100)
        print()
        
        # 创建HTTP会话
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # 检查服务是否运行
        try:
            async with self.session.get(f"{self.api_base}/health") as resp:
                if resp.status == 200:
                    print("✅ 后端服务运行正常\n")
                    return True
                else:
                    print(f"❌ 后端服务响应异常 (status={resp.status})\n")
                    return False
        except Exception as e:
            print(f"❌ 无法连接到后端服务: {e}")
            print("请先启动后端服务: cd backend && python -m app.main\n")
            return False
    
    async def teardown(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求并记录性能"""
        self.total_requests += 1
        start_time = time.time()
        
        try:
            url = f"{self.api_base}{endpoint}"
            async with self.session.request(method, url, **kwargs) as resp:
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                
                if resp.status < 400:
                    self.successful_requests += 1
                    status = "success"
                else:
                    self.failed_requests += 1
                    status = "failed"
                
                try:
                    data = await resp.json() if resp.content_type == 'application/json' else None
                except:
                    data = None
                
                return {
                    "status": resp.status,
                    "response_time": response_time,
                    "data": data,
                    "result": status
                }
        except Exception as e:
            response_time = time.time() - start_time
            self.failed_requests += 1
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.errors.append(error_msg)
            
            return {
                "status": 0,
                "response_time": response_time,
                "error": error_msg,
                "result": "error"
            }
    
    # ==================== 测试1: API端点全覆盖测试 ====================
    
    async def test_all_api_endpoints(self) -> Dict[str, Any]:
        """测试1: 测试所有API端点"""
        print("\n" + "=" * 100)
        print("测试1: API端点全覆盖测试")
        print("=" * 100)
        
        endpoints = [
            # 基础端点
            ("GET", "/", "根路径"),
            ("GET", "/health", "健康检查"),
            
            # 账号管理
            ("GET", "/api/accounts", "账号列表"),
            ("GET", "/api/accounts/status", "账号状态"),
            
            # Bot配置
            ("GET", "/api/bots", "Bot列表"),
            ("GET", "/api/bots/platforms", "平台列表"),
            
            # 频道映射
            ("GET", "/api/mappings", "映射列表"),
            ("GET", "/api/mappings/stats", "映射统计"),
            
            # 日志查询
            ("GET", "/api/logs?limit=10", "日志查询"),
            ("GET", "/api/logs/stats", "日志统计"),
            ("GET", "/api/logs/failed", "失败日志"),
            
            # 系统状态
            ("GET", "/api/system/status", "系统状态"),
            ("GET", "/api/system/stats", "系统统计"),
            ("GET", "/api/system/config", "系统配置"),
            
            # 健康检查
            ("GET", "/api/health", "详细健康检查"),
            
            # 更新检查
            ("GET", "/api/updates/check", "检查更新"),
        ]
        
        results = []
        start_time = time.time()
        
        for method, endpoint, name in endpoints:
            print(f"测试 {name:30s} ({method:4s} {endpoint:40s})...", end=" ")
            result = await self.make_request(method, endpoint)
            
            if result["result"] == "success":
                print(f"✅ {result['response_time']*1000:6.2f}ms")
            else:
                print(f"❌ 失败 (status={result['status']})")
            
            results.append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "status": result["result"],
                "response_time": result["response_time"],
                "http_status": result["status"]
            })
        
        elapsed_time = time.time() - start_time
        successful = sum(1 for r in results if r["status"] == "success")
        
        print(f"\n总计: {len(endpoints)}个端点, 成功: {successful}, 失败: {len(endpoints)-successful}, 耗时: {elapsed_time:.2f}s")
        
        return {
            "test_name": "API端点全覆盖测试",
            "total_endpoints": len(endpoints),
            "successful": successful,
            "failed": len(endpoints) - successful,
            "elapsed_time": elapsed_time,
            "results": results
        }
    
    # ==================== 测试2: 并发请求压力测试 ====================
    
    async def test_concurrent_load(self, concurrent: int) -> Dict[str, Any]:
        """测试2: 并发请求压力测试"""
        print(f"\n测试并发度: {concurrent:4d}...", end=" ")
        
        # 记录性能前
        self.monitor.record_sample()
        
        start_time = time.time()
        tasks = []
        
        # 创建并发任务
        endpoints = [
            ("GET", "/api/system/status"),
            ("GET", "/api/accounts"),
            ("GET", "/api/bots"),
            ("GET", "/api/mappings"),
            ("GET", f"/api/logs?limit=10"),
        ]
        
        for i in range(concurrent):
            method, endpoint = random.choice(endpoints)
            tasks.append(self.make_request(method, endpoint))
        
        # 执行并发请求
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed_time = time.time() - start_time
        
        # 统计结果
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("result") == "success")
        failed = concurrent - successful
        
        response_times = [r["response_time"] for r in results if isinstance(r, dict) and "response_time" in r]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            p50 = statistics.median(response_times)
            p90 = statistics.quantiles(response_times, n=10)[8] if len(response_times) > 10 else max_response_time
            p99 = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max_response_time
        else:
            avg_response_time = max_response_time = min_response_time = p50 = p90 = p99 = 0
        
        qps = concurrent / elapsed_time if elapsed_time > 0 else 0
        
        # 记录性能后
        perf_sample = self.monitor.record_sample()
        
        print(f"✅ QPS: {qps:7.2f}, 平均: {avg_response_time*1000:6.2f}ms, P99: {p99*1000:6.2f}ms, 内存: {perf_sample['memory_mb']:.1f}MB")
        
        return {
            "concurrent": concurrent,
            "total_requests": concurrent,
            "successful": successful,
            "failed": failed,
            "elapsed_time": elapsed_time,
            "qps": qps,
            "response_time": {
                "avg": avg_response_time,
                "max": max_response_time,
                "min": min_response_time,
                "p50": p50,
                "p90": p90,
                "p99": p99
            },
            "memory_mb": perf_sample['memory_mb'],
            "cpu_percent": perf_sample['cpu_percent']
        }
    
    # ==================== 测试3: 数据库高负载测试 ====================
    
    async def test_database_stress(self) -> Dict[str, Any]:
        """测试3: 数据库高负载测试"""
        print("\n" + "=" * 100)
        print("测试3: 数据库高负载测试")
        print("=" * 100)
        
        db_path = Path(__file__).parent / "backend" / "data" / "kook_forwarder.db"
        
        if not db_path.exists():
            print("⚠️  数据库文件不存在，创建测试数据库...")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 创建测试表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kook_message_id TEXT NOT NULL UNIQUE,
                    kook_channel_id TEXT NOT NULL,
                    content TEXT,
                    message_type TEXT,
                    sender_name TEXT,
                    target_platform TEXT,
                    target_channel TEXT,
                    status TEXT,
                    latency_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channel_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kook_channel_id TEXT NOT NULL,
                    kook_channel_name TEXT NOT NULL,
                    target_platform TEXT NOT NULL,
                    target_channel TEXT NOT NULL
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ 测试数据库已创建")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        results = {}
        
        # 测试1: 简单查询性能（高频）
        print("\n测试简单查询（10000次）...", end=" ")
        start = time.time()
        for _ in range(10000):
            cursor.execute("SELECT COUNT(*) FROM message_logs")
            cursor.fetchone()
        simple_query_time = time.time() - start
        qps = 10000 / simple_query_time
        print(f"✅ 耗时: {simple_query_time:.3f}s, QPS: {qps:.0f}")
        results["simple_query"] = {"time": simple_query_time, "qps": qps, "iterations": 10000}
        
        # 测试2: 复杂查询性能（JOIN + ORDER BY）
        print("测试复杂查询（1000次）...", end=" ")
        start = time.time()
        for _ in range(1000):
            cursor.execute("""
                SELECT ml.*, cm.kook_channel_name 
                FROM message_logs ml
                LEFT JOIN channel_mappings cm ON ml.kook_channel_id = cm.kook_channel_id
                WHERE ml.status = 'success'
                ORDER BY ml.created_at DESC
                LIMIT 10
            """)
            cursor.fetchall()
        complex_query_time = time.time() - start
        qps = 1000 / complex_query_time
        print(f"✅ 耗时: {complex_query_time:.3f}s, QPS: {qps:.0f}")
        results["complex_query"] = {"time": complex_query_time, "qps": qps, "iterations": 1000}
        
        # 测试3: 批量插入性能
        print("测试批量插入（10000条）...", end=" ")
        start = time.time()
        cursor.execute("BEGIN TRANSACTION")
        for i in range(10000):
            cursor.execute("""
                INSERT OR IGNORE INTO message_logs 
                (kook_message_id, kook_channel_id, content, message_type, sender_name, 
                 target_platform, target_channel, status, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"stress_test_{int(time.time()*1000000)}_{i}",
                "test_channel",
                f"压力测试消息 {i}",
                "text",
                "压力测试",
                "discord",
                "test_target",
                "success",
                random.randint(50, 500)
            ))
        cursor.execute("COMMIT")
        insert_time = time.time() - start
        qps = 10000 / insert_time
        print(f"✅ 耗时: {insert_time:.3f}s, QPS: {qps:.0f}")
        results["batch_insert"] = {"time": insert_time, "qps": qps, "count": 10000}
        
        # 测试4: 并发更新性能
        print("测试批量更新（5000条）...", end=" ")
        start = time.time()
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("""
            UPDATE message_logs 
            SET status = 'retried', latency_ms = latency_ms + 100
            WHERE kook_channel_id = 'test_channel'
            LIMIT 5000
        """)
        cursor.execute("COMMIT")
        update_time = time.time() - start
        qps = 5000 / update_time if update_time > 0 else 0
        print(f"✅ 耗时: {update_time:.3f}s, QPS: {qps:.0f}")
        results["batch_update"] = {"time": update_time, "qps": qps, "count": 5000}
        
        # 测试5: 批量删除性能
        print("测试批量删除（清理测试数据）...", end=" ")
        start = time.time()
        cursor.execute("DELETE FROM message_logs WHERE kook_channel_id = 'test_channel'")
        conn.commit()
        delete_time = time.time() - start
        deleted_rows = cursor.rowcount
        print(f"✅ 耗时: {delete_time:.3f}s, 删除: {deleted_rows}条")
        results["batch_delete"] = {"time": delete_time, "count": deleted_rows}
        
        # 测试6: 数据库大小
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]
        print(f"\n数据库大小: {db_size / 1024 / 1024:.2f}MB")
        results["database_size_mb"] = db_size / 1024 / 1024
        
        conn.close()
        
        return {
            "test_name": "数据库高负载测试",
            "status": "success",
            "results": results
        }
    
    # ==================== 测试4: 消息队列极限测试 ====================
    
    async def test_message_queue_extreme(self) -> Dict[str, Any]:
        """测试4: 消息队列极限测试"""
        print("\n" + "=" * 100)
        print("测试4: 消息队列极限测试")
        print("=" * 100)
        
        try:
            import redis
            r = redis.Redis(
                host=self.config["redis_host"],
                port=self.config["redis_port"],
                decode_responses=True
            )
            
            # 测试连接
            r.ping()
            print("✅ Redis连接成功\n")
            
            queue_results = []
            
            for batch_size in self.config["message_batch_sizes"]:
                print(f"测试批量大小: {batch_size:5d}...", end=" ")
                
                # 测试入队性能
                messages = []
                for i in range(batch_size):
                    message = {
                        "id": f"stress_{int(time.time()*1000000)}_{i}",
                        "type": "text",
                        "content": f"压力测试消息 {i}",
                        "timestamp": time.time()
                    }
                    messages.append(json.dumps(message))
                
                start = time.time()
                pipe = r.pipeline()
                for msg in messages:
                    pipe.lpush("stress_test_queue", msg)
                pipe.execute()
                enqueue_time = time.time() - start
                enqueue_qps = batch_size / enqueue_time
                
                # 测试出队性能
                start = time.time()
                pipe = r.pipeline()
                for _ in range(batch_size):
                    pipe.rpop("stress_test_queue")
                pipe.execute()
                dequeue_time = time.time() - start
                dequeue_qps = batch_size / dequeue_time
                
                print(f"✅ 入队: {enqueue_time:.3f}s ({enqueue_qps:.0f} msg/s), 出队: {dequeue_time:.3f}s ({dequeue_qps:.0f} msg/s)")
                
                queue_results.append({
                    "batch_size": batch_size,
                    "enqueue_time": enqueue_time,
                    "enqueue_qps": enqueue_qps,
                    "dequeue_time": dequeue_time,
                    "dequeue_qps": dequeue_qps,
                    "total_time": enqueue_time + dequeue_time
                })
            
            # 测试队列大小限制
            print("\n测试队列容量...", end=" ")
            queue_name = "stress_capacity_test"
            r.delete(queue_name)
            
            start = time.time()
            for i in range(100000):  # 插入10万条消息
                r.lpush(queue_name, f"msg_{i}")
            capacity_time = time.time() - start
            queue_length = r.llen(queue_name)
            r.delete(queue_name)
            
            print(f"✅ 插入10万条消息耗时: {capacity_time:.3f}s, QPS: {100000/capacity_time:.0f}")
            
            return {
                "test_name": "消息队列极限测试",
                "status": "success",
                "batch_results": queue_results,
                "capacity_test": {
                    "messages": 100000,
                    "time": capacity_time,
                    "qps": 100000 / capacity_time
                }
            }
            
        except Exception as e:
            print(f"❌ Redis测试失败: {e}")
            traceback.print_exc()
            return {"status": "failed", "error": str(e)}
    
    # ==================== 测试5: 限流器压力测试 ====================
    
    async def test_rate_limiter_stress(self) -> Dict[str, Any]:
        """测试5: 限流器压力测试"""
        print("\n" + "=" * 100)
        print("测试5: 限流器压力测试")
        print("=" * 100)
        
        try:
            sys.path.insert(0, str(Path(__file__).parent / "backend"))
            from app.utils.rate_limiter import RateLimiter
            
            results = []
            
            # 测试不同平台的限流配置
            configs = [
                (5, 5, "Discord", "Discord限流（5请求/5秒）"),
                (30, 1, "Telegram", "Telegram限流（30请求/1秒）"),
                (20, 1, "Feishu", "飞书限流（20请求/1秒）"),
                (100, 1, "高负载", "高负载限流（100请求/1秒）"),
            ]
            
            for calls, period, platform, name in configs:
                print(f"\n测试 {name}...")
                limiter = RateLimiter(calls=calls, period=period)
                
                start = time.time()
                acquire_times = []
                
                # 发送calls*3个请求，测试限流效果
                test_requests = calls * 3
                for i in range(test_requests):
                    acquire_start = time.time()
                    await limiter.acquire()
                    acquire_time = time.time() - acquire_start
                    acquire_times.append(acquire_time)
                
                total_time = time.time() - start
                actual_qps = test_requests / total_time
                expected_qps = calls / period
                
                print(f"  发送请求: {test_requests}")
                print(f"  总耗时: {total_time:.3f}s")
                print(f"  实际QPS: {actual_qps:.2f}")
                print(f"  期望QPS: {expected_qps:.2f}")
                print(f"  平均等待: {statistics.mean(acquire_times)*1000:.2f}ms")
                print(f"  最大等待: {max(acquire_times)*1000:.2f}ms")
                
                # 判断限流是否生效
                rate_limit_working = abs(actual_qps - expected_qps) / expected_qps < 0.1  # 误差<10%
                
                results.append({
                    "platform": platform,
                    "name": name,
                    "calls": calls,
                    "period": period,
                    "test_requests": test_requests,
                    "total_time": total_time,
                    "actual_qps": actual_qps,
                    "expected_qps": expected_qps,
                    "avg_acquire_time": statistics.mean(acquire_times),
                    "max_acquire_time": max(acquire_times),
                    "rate_limit_working": rate_limit_working,
                    "status": "✅ 正常" if rate_limit_working else "⚠️ 偏差较大"
                })
            
            return {
                "test_name": "限流器压力测试",
                "status": "success",
                "results": results
            }
            
        except Exception as e:
            print(f"❌ 限流器测试失败: {e}")
            traceback.print_exc()
            return {"status": "failed", "error": str(e)}
    
    # ==================== 测试6: 大消息处理测试 ====================
    
    async def test_large_messages(self) -> Dict[str, Any]:
        """测试6: 大消息处理测试"""
        print("\n" + "=" * 100)
        print("测试6: 大消息处理测试")
        print("=" * 100)
        
        results = []
        
        for size in self.config["large_message_sizes"]:
            print(f"\n测试消息大小: {size:6d} 字符...", end=" ")
            
            # 生成大消息
            large_content = "测试" * (size // 2)
            
            # 测试格式转换性能
            try:
                from app.processors.formatter import kmarkdown_to_discord
                
                start = time.time()
                for _ in range(100):
                    kmarkdown_to_discord(large_content)
                convert_time = time.time() - start
                
                print(f"✅ 100次转换耗时: {convert_time:.3f}s")
                
                results.append({
                    "size_chars": size,
                    "size_bytes": len(large_content.encode('utf-8')),
                    "iterations": 100,
                    "total_time": convert_time,
                    "avg_time_per_convert": convert_time / 100,
                    "status": "success"
                })
            except Exception as e:
                print(f"❌ 失败: {e}")
                results.append({
                    "size_chars": size,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "test_name": "大消息处理测试",
            "status": "success",
            "results": results
        }
    
    # ==================== 测试7: 内存泄漏检测 ====================
    
    async def test_memory_leak(self) -> Dict[str, Any]:
        """测试7: 内存泄漏检测"""
        print("\n" + "=" * 100)
        print("测试7: 内存泄漏检测")
        print("=" * 100)
        
        print("执行长时间压力测试以检测内存泄漏...")
        print("测试时长: 60秒, 采样间隔: 5秒\n")
        
        memory_samples = []
        start_memory = self.monitor.process.memory_info().rss / 1024 / 1024
        
        print(f"初始内存: {start_memory:.2f}MB")
        print(f"{'时间':>10s} {'内存(MB)':>12s} {'增长(MB)':>12s} {'CPU%':>8s}")
        print("-" * 50)
        
        test_duration = 60
        sample_interval = 5
        iterations = 0
        
        start_time = time.time()
        while time.time() - start_time < test_duration:
            # 执行一些请求
            tasks = []
            for _ in range(50):
                endpoint = random.choice([
                    "/api/system/status",
                    "/api/accounts",
                    "/api/logs?limit=10"
                ])
                tasks.append(self.make_request("GET", endpoint))
            
            await asyncio.gather(*tasks, return_exceptions=True)
            iterations += 1
            
            # 记录内存
            current_memory = self.monitor.process.memory_info().rss / 1024 / 1024
            cpu_percent = self.monitor.process.cpu_percent()
            elapsed = time.time() - start_time
            
            memory_samples.append({
                "time": elapsed,
                "memory_mb": current_memory,
                "growth_mb": current_memory - start_memory,
                "cpu_percent": cpu_percent
            })
            
            print(f"{elapsed:>10.1f}s {current_memory:>12.2f} {current_memory - start_memory:>+12.2f} {cpu_percent:>8.1f}")
            
            await asyncio.sleep(sample_interval)
        
        final_memory = memory_samples[-1]["memory_mb"]
        total_growth = final_memory - start_memory
        
        # 分析内存增长趋势
        if len(memory_samples) >= 3:
            # 简单线性回归检测增长趋势
            times = [s["time"] for s in memory_samples]
            memories = [s["memory_mb"] for s in memory_samples]
            
            # 计算平均增长率
            growth_rate = (memories[-1] - memories[0]) / (times[-1] - times[0])
            
            # 判断是否可能存在内存泄漏
            suspected_leak = growth_rate > 1.0  # 每秒增长超过1MB
            
            print(f"\n最终内存: {final_memory:.2f}MB")
            print(f"总增长: {total_growth:+.2f}MB")
            print(f"增长率: {growth_rate:.3f}MB/s")
            print(f"总迭代: {iterations}次")
            
            if suspected_leak:
                print("⚠️  警告: 检测到可能的内存泄漏")
            else:
                print("✅ 内存使用正常")
        
        return {
            "test_name": "内存泄漏检测",
            "status": "success",
            "initial_memory_mb": start_memory,
            "final_memory_mb": final_memory,
            "total_growth_mb": total_growth,
            "growth_rate_mb_per_sec": growth_rate if 'growth_rate' in locals() else 0,
            "test_duration_sec": test_duration,
            "iterations": iterations,
            "suspected_leak": suspected_leak if 'suspected_leak' in locals() else False,
            "samples": memory_samples
        }
    
    # ==================== 测试8: 持续负载测试 ====================
    
    async def test_sustained_load(self) -> Dict[str, Any]:
        """测试8: 持续负载测试"""
        print("\n" + "=" * 100)
        print("测试8: 持续负载测试（持续负载60秒）")
        print("=" * 100)
        
        test_duration = 60
        concurrent_users = 20
        
        print(f"并发用户: {concurrent_users}")
        print(f"测试时长: {test_duration}秒")
        print(f"{'时间':>10s} {'请求数':>10s} {'成功率':>10s} {'平均延迟':>12s} {'QPS':>10s}")
        print("-" * 60)
        
        start_time = time.time()
        total_requests_before = self.total_requests
        samples = []
        
        while time.time() - start_time < test_duration:
            sample_start = time.time()
            requests_before = self.total_requests
            success_before = self.successful_requests
            
            # 发送一批并发请求
            tasks = []
            for _ in range(concurrent_users):
                endpoint = random.choice([
                    "/api/system/status",
                    "/api/accounts",
                    "/api/bots",
                    "/api/mappings",
                    "/api/logs?limit=10"
                ])
                tasks.append(self.make_request("GET", endpoint))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 统计本批次
            sample_time = time.time() - sample_start
            sample_requests = self.total_requests - requests_before
            sample_success = self.successful_requests - success_before
            sample_success_rate = sample_success / sample_requests if sample_requests > 0 else 0
            
            recent_response_times = self.response_times[-(concurrent_users):]
            sample_avg_latency = statistics.mean(recent_response_times) if recent_response_times else 0
            sample_qps = sample_requests / sample_time if sample_time > 0 else 0
            
            elapsed = time.time() - start_time
            samples.append({
                "time": elapsed,
                "requests": sample_requests,
                "success_rate": sample_success_rate,
                "avg_latency": sample_avg_latency,
                "qps": sample_qps
            })
            
            print(f"{elapsed:>10.1f}s {sample_requests:>10d} {sample_success_rate:>9.1%} {sample_avg_latency*1000:>11.2f}ms {sample_qps:>10.1f}")
            
            await asyncio.sleep(1)
        
        total_test_time = time.time() - start_time
        total_test_requests = self.total_requests - total_requests_before
        overall_qps = total_test_requests / total_test_time
        overall_success_rate = sum(s["success_rate"] for s in samples) / len(samples) if samples else 0
        overall_avg_latency = sum(s["avg_latency"] for s in samples) / len(samples) if samples else 0
        
        print(f"\n持续负载测试完成:")
        print(f"  总请求: {total_test_requests}")
        print(f"  平均QPS: {overall_qps:.2f}")
        print(f"  平均成功率: {overall_success_rate:.1%}")
        print(f"  平均延迟: {overall_avg_latency*1000:.2f}ms")
        
        return {
            "test_name": "持续负载测试",
            "status": "success",
            "duration_sec": total_test_time,
            "concurrent_users": concurrent_users,
            "total_requests": total_test_requests,
            "overall_qps": overall_qps,
            "overall_success_rate": overall_success_rate,
            "overall_avg_latency": overall_avg_latency,
            "samples": samples
        }
    
    # ==================== 主测试流程 ====================
    
    async def run_all_tests(self):
        """运行所有压力测试"""
        test_results["start_time"] = datetime.now().isoformat()
        
        # 初始化
        if not await self.setup():
            return False
        
        try:
            # 测试1: API端点全覆盖
            test_results["tests"]["api_endpoints"] = await self.test_all_api_endpoints()
            await asyncio.sleep(2)
            
            # 测试2: 并发请求压力测试
            print("\n" + "=" * 100)
            print("测试2: 并发请求压力测试")
            print("=" * 100)
            
            concurrent_results = []
            for concurrent in self.config["concurrent_users"]:
                result = await self.test_concurrent_load(concurrent)
                concurrent_results.append(result)
                await asyncio.sleep(1)
            
            test_results["tests"]["concurrent_load"] = {
                "test_name": "并发请求压力测试",
                "results": concurrent_results
            }
            
            # 测试3: 数据库高负载测试
            test_results["tests"]["database_stress"] = await self.test_database_stress()
            await asyncio.sleep(2)
            
            # 测试4: 消息队列极限测试
            test_results["tests"]["message_queue_extreme"] = await self.test_message_queue_extreme()
            await asyncio.sleep(2)
            
            # 测试5: 限流器压力测试
            test_results["tests"]["rate_limiter_stress"] = await self.test_rate_limiter_stress()
            await asyncio.sleep(2)
            
            # 测试6: 大消息处理测试
            test_results["tests"]["large_messages"] = await self.test_large_messages()
            await asyncio.sleep(2)
            
            # 测试7: 内存泄漏检测
            test_results["tests"]["memory_leak"] = await self.test_memory_leak()
            await asyncio.sleep(2)
            
            # 测试8: 持续负载测试
            test_results["tests"]["sustained_load"] = await self.test_sustained_load()
            
            # 生成总结
            self.generate_summary()
            
            return True
            
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {e}")
            traceback.print_exc()
            return False
        finally:
            await self.teardown()
            test_results["end_time"] = datetime.now().isoformat()
    
    def generate_summary(self):
        """生成测试总结"""
        print("\n" + "=" * 100)
        print("压力测试总结")
        print("=" * 100)
        
        # 性能统计
        perf_stats = self.monitor.get_stats()
        
        print(f"\n📊 请求统计:")
        print(f"  总请求数: {self.total_requests}")
        print(f"  成功请求: {self.successful_requests}")
        print(f"  失败请求: {self.failed_requests}")
        print(f"  成功率: {self.successful_requests/self.total_requests*100:.2f}%")
        
        if self.response_times:
            print(f"\n⏱️  响应时间:")
            print(f"  平均: {statistics.mean(self.response_times)*1000:.2f}ms")
            print(f"  最小: {min(self.response_times)*1000:.2f}ms")
            print(f"  最大: {max(self.response_times)*1000:.2f}ms")
            
            sorted_times = sorted(self.response_times)
            p50 = sorted_times[len(sorted_times)//2]
            p90 = sorted_times[int(len(sorted_times)*0.9)]
            p95 = sorted_times[int(len(sorted_times)*0.95)]
            p99 = sorted_times[int(len(sorted_times)*0.99)]
            
            print(f"  P50: {p50*1000:.2f}ms")
            print(f"  P90: {p90*1000:.2f}ms")
            print(f"  P95: {p95*1000:.2f}ms")
            print(f"  P99: {p99*1000:.2f}ms")
        
        if perf_stats:
            print(f"\n💻 系统资源:")
            print(f"  内存使用:")
            print(f"    最小: {perf_stats['memory']['min_mb']:.2f}MB")
            print(f"    最大: {perf_stats['memory']['max_mb']:.2f}MB")
            print(f"    平均: {perf_stats['memory']['avg_mb']:.2f}MB")
            print(f"    增长: {perf_stats['memory']['growth_mb']:+.2f}MB")
            
            print(f"  CPU使用:")
            print(f"    最小: {perf_stats['cpu']['min_percent']:.1f}%")
            print(f"    最大: {perf_stats['cpu']['max_percent']:.1f}%")
            print(f"    平均: {perf_stats['cpu']['avg_percent']:.1f}%")
        
        if self.errors:
            print(f"\n⚠️  错误列表 (前10条):")
            for i, error in enumerate(self.errors[:10], 1):
                print(f"  {i}. {error}")
        
        # 保存摘要到结果
        test_results["summary"] = {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            "response_time_stats": {
                "avg_ms": statistics.mean(self.response_times) * 1000 if self.response_times else 0,
                "min_ms": min(self.response_times) * 1000 if self.response_times else 0,
                "max_ms": max(self.response_times) * 1000 if self.response_times else 0,
                "p50_ms": sorted(self.response_times)[len(self.response_times)//2] * 1000 if self.response_times else 0,
                "p90_ms": sorted(self.response_times)[int(len(self.response_times)*0.9)] * 1000 if self.response_times else 0,
                "p99_ms": sorted(self.response_times)[int(len(self.response_times)*0.99)] * 1000 if self.response_times else 0,
            },
            "performance_stats": perf_stats,
            "error_count": len(self.errors)
        }


async def main():
    """主函数"""
    print("正在初始化全面压力测试...")
    
    runner = ComprehensiveStressTest(TEST_CONFIG)
    success = await runner.run_all_tests()
    
    if success:
        # 保存JSON报告
        report_path = Path(__file__).parent / "comprehensive_stress_test_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ JSON报告已保存: {report_path}")
        
        # 生成Markdown报告
        generate_markdown_report(test_results)
        
        print("\n" + "=" * 100)
        print("✅ 全面压力测试完成!")
        print("=" * 100)
        
        return 0
    else:
        print("\n❌ 压力测试失败")
        return 1


def generate_markdown_report(results: Dict[str, Any]):
    """生成详细的Markdown测试报告"""
    report_path = Path(__file__).parent / "压力测试详细报告.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# KOOK消息转发系统 - 全面压力测试报告\n\n")
        f.write(f"**测试开始时间**: {results['start_time']}\n\n")
        f.write(f"**测试结束时间**: {results['end_time']}\n\n")
        f.write("---\n\n")
        
        # 系统信息
        f.write("## 🖥️ 测试环境\n\n")
        f.write("| 项目 | 值 |\n")
        f.write("|------|----|\n")
        for key, value in results["system_info"].items():
            f.write(f"| {key} | {value} |\n")
        f.write("\n---\n\n")
        
        # 测试总结
        if "summary" in results:
            summary = results["summary"]
            f.write("## 📊 测试总结\n\n")
            f.write(f"- **总请求数**: {summary['total_requests']:,}\n")
            f.write(f"- **成功请求**: {summary['successful_requests']:,}\n")
            f.write(f"- **失败请求**: {summary['failed_requests']:,}\n")
            f.write(f"- **成功率**: {summary['success_rate']*100:.2f}%\n\n")
            
            f.write("### 响应时间统计\n\n")
            rt_stats = summary["response_time_stats"]
            f.write("| 指标 | 值 |\n")
            f.write("|------|----|\n")
            f.write(f"| 平均 | {rt_stats['avg_ms']:.2f}ms |\n")
            f.write(f"| 最小 | {rt_stats['min_ms']:.2f}ms |\n")
            f.write(f"| 最大 | {rt_stats['max_ms']:.2f}ms |\n")
            f.write(f"| P50 | {rt_stats['p50_ms']:.2f}ms |\n")
            f.write(f"| P90 | {rt_stats['p90_ms']:.2f}ms |\n")
            f.write(f"| P99 | {rt_stats['p99_ms']:.2f}ms |\n")
            f.write("\n")
            
            if "performance_stats" in summary and summary["performance_stats"]:
                perf = summary["performance_stats"]
                f.write("### 系统资源使用\n\n")
                
                if "memory" in perf:
                    f.write("**内存使用**:\n")
                    f.write(f"- 最小: {perf['memory']['min_mb']:.2f}MB\n")
                    f.write(f"- 最大: {perf['memory']['max_mb']:.2f}MB\n")
                    f.write(f"- 平均: {perf['memory']['avg_mb']:.2f}MB\n")
                    f.write(f"- 增长: {perf['memory']['growth_mb']:+.2f}MB\n\n")
                
                if "cpu" in perf:
                    f.write("**CPU使用**:\n")
                    f.write(f"- 最小: {perf['cpu']['min_percent']:.1f}%\n")
                    f.write(f"- 最大: {perf['cpu']['max_percent']:.1f}%\n")
                    f.write(f"- 平均: {perf['cpu']['avg_percent']:.1f}%\n\n")
        
        f.write("---\n\n")
        
        # 详细测试结果
        f.write("## 📋 详细测试结果\n\n")
        
        for test_name, test_data in results["tests"].items():
            test_title = test_data.get("test_name", test_name)
            f.write(f"### {test_title}\n\n")
            
            if test_data.get("status") == "failed":
                f.write(f"❌ **状态**: 失败\n\n")
                f.write(f"**错误**: {test_data.get('error', 'Unknown')}\n\n")
                continue
            
            f.write(f"✅ **状态**: 成功\n\n")
            
            # 处理不同类型的结果
            if "results" in test_data:
                results_data = test_data["results"]
                
                if isinstance(results_data, list) and results_data:
                    # 表格格式
                    first_item = results_data[0]
                    if isinstance(first_item, dict):
                        keys = list(first_item.keys())
                        
                        # 写表头
                        f.write("| " + " | ".join(keys) + " |\n")
                        f.write("|" + "|".join(["---"] * len(keys)) + "|\n")
                        
                        # 写数据
                        for item in results_data[:20]:  # 限制显示前20行
                            values = []
                            for k in keys:
                                v = item.get(k, "")
                                if isinstance(v, float):
                                    values.append(f"{v:.3f}")
                                else:
                                    values.append(str(v))
                            f.write("| " + " | ".join(values) + " |\n")
                        
                        if len(results_data) > 20:
                            f.write(f"\n*（仅显示前20条，共{len(results_data)}条）*\n")
                
                elif isinstance(results_data, dict):
                    # 键值对格式
                    for key, value in results_data.items():
                        if isinstance(value, dict):
                            f.write(f"\n**{key}**:\n")
                            for k, v in value.items():
                                f.write(f"- {k}: {v}\n")
                        else:
                            f.write(f"- **{key}**: {value}\n")
            
            # 处理其他字段
            for key in ["batch_results", "capacity_test", "samples"]:
                if key in test_data:
                    if key == "samples" and len(test_data[key]) > 10:
                        f.write(f"\n*{key}: {len(test_data[key])}个样本（略）*\n")
                    else:
                        f.write(f"\n**{key}**: {test_data[key]}\n")
            
            f.write("\n")
        
        f.write("---\n\n")
        f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\n*此报告由 KOOK消息转发系统压力测试工具自动生成*\n")
    
    print(f"✅ Markdown报告已保存: {report_path}")


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        sys.exit(1)
