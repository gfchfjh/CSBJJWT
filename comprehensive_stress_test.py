"""
KOOK消息转发系统 - 全面压力测试
测试所有核心模块的性能、稳定性和并发能力
"""
import asyncio
import aiohttp
import time
import random
import json
import sys
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import statistics

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 测试配置
COMPREHENSIVE_TEST_CONFIG = {
    "api_base_url": "http://127.0.0.1:9527",
    "redis_host": "127.0.0.1",
    "redis_port": 6379,
    
    # 并发测试配置
    "concurrent_levels": [1, 5, 10, 20, 50, 100],
    "max_concurrent": 200,
    
    # 消息测试配置
    "message_batch_sizes": [10, 50, 100, 500, 1000, 5000],
    "test_duration_seconds": 60,
    
    # 格式转换测试
    "formatter_iterations": [1000, 5000, 10000, 50000],
    
    # 图片测试配置
    "image_sizes": [
        (800, 600, "小图"),
        (1920, 1080, "中图"),
        (3840, 2160, "4K图"),
        (7680, 4320, "8K图"),
    ],
    "image_batch_size": 20,
    
    # 数据库测试
    "db_operations": [100, 500, 1000, 5000, 10000],
    
    # 限流测试
    "rate_limits": [
        (5, 5, "Discord限流（5请求/5秒）"),
        (30, 1, "Telegram限流（30请求/1秒）"),
        (20, 1, "飞书限流（20请求/1秒）"),
        (100, 10, "自定义限流（100请求/10秒）"),
    ],
}


class ColorPrinter:
    """彩色输出"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def print_header(text):
        print(f"\n{ColorPrinter.HEADER}{ColorPrinter.BOLD}{'=' * 80}{ColorPrinter.ENDC}")
        print(f"{ColorPrinter.HEADER}{ColorPrinter.BOLD}{text.center(80)}{ColorPrinter.ENDC}")
        print(f"{ColorPrinter.HEADER}{ColorPrinter.BOLD}{'=' * 80}{ColorPrinter.ENDC}\n")
    
    @staticmethod
    def print_success(text):
        print(f"{ColorPrinter.OKGREEN}✅ {text}{ColorPrinter.ENDC}")
    
    @staticmethod
    def print_error(text):
        print(f"{ColorPrinter.FAIL}❌ {text}{ColorPrinter.ENDC}")
    
    @staticmethod
    def print_warning(text):
        print(f"{ColorPrinter.WARNING}⚠️  {text}{ColorPrinter.ENDC}")
    
    @staticmethod
    def print_info(text):
        print(f"{ColorPrinter.OKCYAN}ℹ️  {text}{ColorPrinter.ENDC}")


class ComprehensiveStressTest:
    """全面压力测试类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_base = config["api_base_url"]
        self.session = None
        
        # 统计数据
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "test_results": {},
        }
    
    async def setup(self):
        """初始化测试环境"""
        ColorPrinter.print_header("KOOK消息转发系统 - 全面压力测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"API地址: {self.api_base}")
        print()
        
        # 创建HTTP会话
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # 检查服务状态
        try:
            async with self.session.get(f"{self.api_base}/health") as resp:
                if resp.status == 200:
                    ColorPrinter.print_success("后端服务运行正常")
                else:
                    ColorPrinter.print_error(f"后端服务响应异常 (status={resp.status})")
                    return False
        except Exception as e:
            ColorPrinter.print_error(f"无法连接到后端服务: {e}")
            ColorPrinter.print_info("请先启动后端服务: cd backend && python -m app.main")
            return False
        
        self.stats["start_time"] = datetime.now()
        return True
    
    async def teardown(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
        self.stats["end_time"] = datetime.now()
    
    # ==================== 测试1: API端点压力测试 ====================
    
    async def test_api_stress(self):
        """API端点压力测试"""
        ColorPrinter.print_header("测试1: API端点压力测试")
        
        endpoints = [
            ("GET", "/health", "健康检查"),
            ("GET", "/api/system/status", "系统状态"),
            ("GET", "/api/accounts", "账号列表"),
            ("GET", "/api/bots", "Bot列表"),
            ("GET", "/api/mappings", "映射列表"),
            ("GET", "/api/logs?limit=10", "日志查询"),
            ("GET", "/api/system/stats", "系统统计"),
        ]
        
        results = []
        
        for concurrent in self.config["concurrent_levels"]:
            ColorPrinter.print_info(f"并发度: {concurrent}")
            
            start_time = time.time()
            tasks = []
            
            # 为每个并发请求随机选择端点
            for i in range(concurrent):
                method, endpoint, name = random.choice(endpoints)
                task = self._make_request(method, endpoint)
                tasks.append(task)
            
            # 执行并发请求
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - start_time
            
            # 统计结果
            successful = sum(1 for r in responses if isinstance(r, dict) and r.get("status", 0) < 400)
            failed = concurrent - successful
            
            response_times = [r["response_time"] for r in responses if isinstance(r, dict)]
            avg_time = statistics.mean(response_times) if response_times else 0
            p50_time = statistics.median(response_times) if response_times else 0
            p99_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times, default=0)
            
            qps = concurrent / elapsed if elapsed > 0 else 0
            
            result = {
                "concurrent": concurrent,
                "total": concurrent,
                "successful": successful,
                "failed": failed,
                "qps": round(qps, 2),
                "avg_time_ms": round(avg_time * 1000, 2),
                "p50_time_ms": round(p50_time * 1000, 2),
                "p99_time_ms": round(p99_time * 1000, 2),
                "elapsed": round(elapsed, 2),
            }
            results.append(result)
            
            # 打印结果
            print(f"  ✓ 成功: {successful}/{concurrent}, "
                  f"QPS: {result['qps']}, "
                  f"平均响应: {result['avg_time_ms']}ms, "
                  f"P99: {result['p99_time_ms']}ms")
        
        self.stats["test_results"]["api_stress"] = {
            "test_name": "API端点压力测试",
            "results": results
        }
        
        return results
    
    # ==================== 测试2: 消息格式转换压力测试 ====================
    
    async def test_formatter_stress(self):
        """消息格式转换压力测试"""
        ColorPrinter.print_header("测试2: 消息格式转换压力测试")
        
        try:
            from app.processors.formatter import MessageFormatter
            
            formatter = MessageFormatter()
            
            # 测试文本（包含各种格式）
            test_texts = [
                "**这是粗体** *这是斜体* `这是代码`",
                "(emj)开心(emj) (emj)笑(emj) (emj)爱心(emj) @用户名 @全体成员",
                "这是一段很长的文本" + "测试消息 " * 100,
                "[链接文本](https://example.com) ~~删除线~~ **粗体和*斜体*混合**",
                "中文English混合🎉emoji表情(emj)火(emj)",
            ]
            
            results = []
            
            for iterations in self.config["formatter_iterations"]:
                ColorPrinter.print_info(f"迭代次数: {iterations}")
                
                test_result = {}
                
                # 测试Discord转换
                start = time.time()
                for _ in range(iterations):
                    for text in test_texts:
                        formatter.kmarkdown_to_discord(text)
                discord_time = time.time() - start
                test_result["discord"] = {
                    "iterations": iterations * len(test_texts),
                    "time_seconds": round(discord_time, 3),
                    "ops_per_sec": round((iterations * len(test_texts)) / discord_time, 2)
                }
                
                # 测试Telegram转换
                start = time.time()
                for _ in range(iterations):
                    for text in test_texts:
                        formatter.kmarkdown_to_telegram_html(text)
                telegram_time = time.time() - start
                test_result["telegram"] = {
                    "iterations": iterations * len(test_texts),
                    "time_seconds": round(telegram_time, 3),
                    "ops_per_sec": round((iterations * len(test_texts)) / telegram_time, 2)
                }
                
                # 测试消息分段
                long_text = "测试消息 " * 1000  # 约5000字符
                start = time.time()
                for _ in range(iterations // 10):  # 分段测试较慢，减少迭代
                    formatter.split_long_message(long_text, 2000)
                split_time = time.time() - start
                test_result["split"] = {
                    "iterations": iterations // 10,
                    "time_seconds": round(split_time, 3),
                    "ops_per_sec": round((iterations // 10) / split_time, 2) if split_time > 0 else 0
                }
                
                results.append({
                    "iterations": iterations,
                    **test_result
                })
                
                print(f"  ✓ Discord: {test_result['discord']['ops_per_sec']} ops/s, "
                      f"Telegram: {test_result['telegram']['ops_per_sec']} ops/s, "
                      f"Split: {test_result['split']['ops_per_sec']} ops/s")
            
            self.stats["test_results"]["formatter_stress"] = {
                "test_name": "消息格式转换压力测试",
                "results": results
            }
            
            return results
            
        except Exception as e:
            ColorPrinter.print_error(f"格式转换测试失败: {e}")
            return []
    
    # ==================== 测试3: Redis队列压力测试 ====================
    
    async def test_redis_queue_stress(self):
        """Redis队列压力测试"""
        ColorPrinter.print_header("测试3: Redis队列压力测试")
        
        try:
            import redis.asyncio as aioredis
            
            redis_client = await aioredis.from_url(
                f"redis://{self.config['redis_host']}:{self.config['redis_port']}",
                encoding="utf-8",
                decode_responses=True
            )
            
            # 测试连接
            await redis_client.ping()
            ColorPrinter.print_success("Redis连接成功")
            
            results = []
            
            for batch_size in self.config["message_batch_sizes"]:
                ColorPrinter.print_info(f"批量大小: {batch_size}")
                
                test_queue = f"stress_test_queue_{int(time.time())}"
                
                # 测试入队性能
                messages = [
                    json.dumps({
                        "message_id": f"test_{i}",
                        "content": f"测试消息 {i}",
                        "timestamp": time.time()
                    })
                    for i in range(batch_size)
                ]
                
                start = time.time()
                for msg in messages:
                    await redis_client.rpush(test_queue, msg)
                enqueue_time = time.time() - start
                
                # 测试出队性能
                start = time.time()
                for _ in range(batch_size):
                    await redis_client.lpop(test_queue)
                dequeue_time = time.time() - start
                
                # 测试批量操作
                start = time.time()
                pipe = redis_client.pipeline()
                for msg in messages:
                    pipe.rpush(test_queue, msg)
                await pipe.execute()
                batch_enqueue_time = time.time() - start
                
                # 清理
                await redis_client.delete(test_queue)
                
                result = {
                    "batch_size": batch_size,
                    "enqueue_time": round(enqueue_time, 3),
                    "dequeue_time": round(dequeue_time, 3),
                    "batch_enqueue_time": round(batch_enqueue_time, 3),
                    "enqueue_qps": round(batch_size / enqueue_time, 2),
                    "dequeue_qps": round(batch_size / dequeue_time, 2),
                    "batch_qps": round(batch_size / batch_enqueue_time, 2),
                }
                results.append(result)
                
                print(f"  ✓ 单条入队: {result['enqueue_qps']} msg/s, "
                      f"单条出队: {result['dequeue_qps']} msg/s, "
                      f"批量入队: {result['batch_qps']} msg/s")
            
            await redis_client.close()
            
            self.stats["test_results"]["redis_queue_stress"] = {
                "test_name": "Redis队列压力测试",
                "results": results
            }
            
            return results
            
        except Exception as e:
            ColorPrinter.print_error(f"Redis队列测试失败: {e}")
            return []
    
    # ==================== 测试4: 限流器压力测试 ====================
    
    async def test_rate_limiter_stress(self):
        """限流器压力测试"""
        ColorPrinter.print_header("测试4: 限流器压力测试")
        
        try:
            from app.utils.rate_limiter import RateLimiter
            
            results = []
            
            for calls, period, name in self.config["rate_limits"]:
                ColorPrinter.print_info(f"测试 {name}")
                
                limiter = RateLimiter(calls=calls, period=period)
                
                # 发送 calls * 3 个请求，测试限流效果
                total_requests = calls * 3
                
                start_time = time.time()
                acquire_times = []
                
                for i in range(total_requests):
                    acquire_start = time.time()
                    await limiter.acquire()
                    acquire_time = time.time() - acquire_start
                    acquire_times.append(acquire_time)
                
                total_time = time.time() - start_time
                
                # 理论时间：calls * 3 个请求，每 period 秒 calls 个
                expected_time = period * (total_requests / calls - 1)
                
                result = {
                    "name": name,
                    "calls": calls,
                    "period": period,
                    "total_requests": total_requests,
                    "total_time": round(total_time, 2),
                    "expected_time": round(expected_time, 2),
                    "accuracy": round((1 - abs(total_time - expected_time) / expected_time) * 100, 2) if expected_time > 0 else 100,
                    "avg_acquire_time": round(statistics.mean(acquire_times), 3),
                    "max_acquire_time": round(max(acquire_times), 3),
                }
                results.append(result)
                
                print(f"  ✓ 实际耗时: {result['total_time']}s, "
                      f"预期耗时: {result['expected_time']}s, "
                      f"准确度: {result['accuracy']}%")
            
            self.stats["test_results"]["rate_limiter_stress"] = {
                "test_name": "限流器压力测试",
                "results": results
            }
            
            return results
            
        except Exception as e:
            ColorPrinter.print_error(f"限流器测试失败: {e}")
            return []
    
    # ==================== 测试5: 数据库并发压力测试 ====================
    
    async def test_database_stress(self):
        """数据库并发压力测试"""
        ColorPrinter.print_header("测试5: 数据库并发压力测试")
        
        db_path = Path(__file__).parent / "backend" / "data" / "kook_forwarder.db"
        
        if not db_path.exists():
            ColorPrinter.print_warning("数据库文件不存在，跳过测试")
            return []
        
        results = []
        
        for operations in self.config["db_operations"]:
            ColorPrinter.print_info(f"操作数量: {operations}")
            
            # 测试简单查询
            start = time.time()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            for _ in range(operations):
                cursor.execute("SELECT COUNT(*) FROM message_logs")
                cursor.fetchone()
            
            simple_query_time = time.time() - start
            
            # 测试插入操作
            start = time.time()
            cursor.execute("BEGIN TRANSACTION")
            for i in range(min(operations, 1000)):  # 限制插入数量
                cursor.execute("""
                    INSERT INTO message_logs 
                    (kook_message_id, kook_channel_id, content, message_type, 
                     sender_name, target_platform, target_channel, status, latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"stress_test_{int(time.time())}_{i}",
                    "stress_test_channel",
                    f"压力测试消息 {i}",
                    "text",
                    "压力测试用户",
                    "discord",
                    "test_target",
                    "success",
                    random.randint(100, 2000)
                ))
            cursor.execute("COMMIT")
            insert_time = time.time() - start
            
            # 测试复杂查询
            start = time.time()
            for _ in range(min(operations, 100)):
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
            
            # 清理测试数据
            cursor.execute("DELETE FROM message_logs WHERE kook_channel_id = 'stress_test_channel'")
            conn.commit()
            conn.close()
            
            result = {
                "operations": operations,
                "simple_query_time": round(simple_query_time, 3),
                "simple_query_qps": round(operations / simple_query_time, 2),
                "insert_time": round(insert_time, 3),
                "insert_qps": round(min(operations, 1000) / insert_time, 2),
                "complex_query_time": round(complex_query_time, 3),
                "complex_query_qps": round(min(operations, 100) / complex_query_time, 2) if complex_query_time > 0 else 0,
            }
            results.append(result)
            
            print(f"  ✓ 简单查询: {result['simple_query_qps']} qps, "
                  f"插入: {result['insert_qps']} qps, "
                  f"复杂查询: {result['complex_query_qps']} qps")
        
        self.stats["test_results"]["database_stress"] = {
            "test_name": "数据库并发压力测试",
            "results": results
        }
        
        return results
    
    # ==================== 测试6: 图片处理压力测试 ====================
    
    async def test_image_processing_stress(self):
        """图片处理压力测试"""
        ColorPrinter.print_header("测试6: 图片处理压力测试")
        
        try:
            from PIL import Image
            import io
            
            results = []
            
            for width, height, name in self.config["image_sizes"]:
                ColorPrinter.print_info(f"测试 {name} ({width}x{height})")
                
                # 生成测试图片
                img = Image.new('RGB', (width, height), color=(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                ))
                
                # 测试JPEG压缩
                start = time.time()
                for quality in [95, 85, 75, 60]:
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='JPEG', quality=quality)
                    img_bytes.seek(0)
                jpeg_time = time.time() - start
                
                # 测试PNG压缩
                start = time.time()
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG', optimize=True)
                img_bytes.seek(0)
                png_time = time.time() - start
                
                # 测试缩放
                start = time.time()
                for _ in range(10):
                    img.resize((width // 2, height // 2), Image.Resampling.LANCZOS)
                resize_time = time.time() - start
                
                result = {
                    "name": name,
                    "width": width,
                    "height": height,
                    "jpeg_compress_time": round(jpeg_time, 3),
                    "png_compress_time": round(png_time, 3),
                    "resize_time": round(resize_time / 10, 3),
                }
                results.append(result)
                
                print(f"  ✓ JPEG压缩: {result['jpeg_compress_time']}s, "
                      f"PNG压缩: {result['png_compress_time']}s, "
                      f"缩放: {result['resize_time']}s")
            
            self.stats["test_results"]["image_processing_stress"] = {
                "test_name": "图片处理压力测试",
                "results": results
            }
            
            return results
            
        except Exception as e:
            ColorPrinter.print_error(f"图片处理测试失败: {e}")
            return []
    
    # ==================== 测试7: 端到端集成压力测试 ====================
    
    async def test_end_to_end_stress(self):
        """端到端集成压力测试"""
        ColorPrinter.print_header("测试7: 端到端集成压力测试")
        
        ColorPrinter.print_info("模拟完整消息处理流程")
        
        # 模拟消息数量
        message_counts = [10, 50, 100, 500]
        results = []
        
        for msg_count in message_counts:
            ColorPrinter.print_info(f"消息数量: {msg_count}")
            
            async def process_message(msg_id):
                """模拟完整的消息处理流程"""
                try:
                    # 1. 接收消息（模拟）
                    await asyncio.sleep(0.001)
                    
                    # 2. 格式转换（模拟）
                    from app.processors.formatter import MessageFormatter
                    formatter = MessageFormatter()
                    text = f"**测试消息 {msg_id}** 包含*格式*和`代码`"
                    formatter.kmarkdown_to_discord(text)
                    await asyncio.sleep(0.001)
                    
                    # 3. 限流控制（模拟）
                    await asyncio.sleep(0.002)
                    
                    # 4. 转发（模拟网络请求）
                    await asyncio.sleep(0.01)
                    
                    # 5. 记录日志（模拟）
                    await asyncio.sleep(0.001)
                    
                    return True
                except Exception as e:
                    return False
            
            # 并发处理消息
            start_time = time.time()
            tasks = [process_message(i) for i in range(msg_count)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - start_time
            
            successful = sum(1 for r in responses if r is True)
            throughput = msg_count / elapsed if elapsed > 0 else 0
            
            result = {
                "message_count": msg_count,
                "successful": successful,
                "failed": msg_count - successful,
                "elapsed_time": round(elapsed, 3),
                "throughput": round(throughput, 2),
                "avg_latency_ms": round((elapsed / msg_count) * 1000, 2) if msg_count > 0 else 0,
            }
            results.append(result)
            
            print(f"  ✓ 成功: {successful}/{msg_count}, "
                  f"吞吐量: {result['throughput']} msg/s, "
                  f"平均延迟: {result['avg_latency_ms']}ms")
        
        self.stats["test_results"]["end_to_end_stress"] = {
            "test_name": "端到端集成压力测试",
            "results": results
        }
        
        return results
    
    # ==================== 辅助方法 ====================
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        self.stats["total_requests"] += 1
        start_time = time.time()
        
        try:
            url = f"{self.api_base}{endpoint}"
            async with self.session.request(method, url, **kwargs) as resp:
                response_time = time.time() - start_time
                self.stats["response_times"].append(response_time)
                
                if resp.status < 400:
                    self.stats["successful_requests"] += 1
                else:
                    self.stats["failed_requests"] += 1
                
                return {
                    "status": resp.status,
                    "response_time": response_time,
                }
        except Exception as e:
            response_time = time.time() - start_time
            self.stats["failed_requests"] += 1
            return {
                "status": 0,
                "response_time": response_time,
                "error": str(e)
            }
    
    # ==================== 主测试流程 ====================
    
    async def run_all_tests(self):
        """运行所有压力测试"""
        if not await self.setup():
            return
        
        try:
            # 运行所有测试
            await self.test_api_stress()
            await self.test_formatter_stress()
            await self.test_redis_queue_stress()
            await self.test_rate_limiter_stress()
            await self.test_database_stress()
            await self.test_image_processing_stress()
            await self.test_end_to_end_stress()
            
            # 打印总结
            self.print_summary()
            
        finally:
            await self.teardown()
    
    def print_summary(self):
        """打印测试总结"""
        ColorPrinter.print_header("测试总结")
        
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        print(f"📊 测试总览:")
        print(f"  - 测试时长: {round(duration, 2)}秒")
        print(f"  - 总请求数: {self.stats['total_requests']}")
        print(f"  - 成功请求: {self.stats['successful_requests']}")
        print(f"  - 失败请求: {self.stats['failed_requests']}")
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
            print(f"  - 成功率: {round(success_rate, 2)}%")
        
        if self.stats['response_times']:
            print(f"\n⏱️  响应时间统计:")
            print(f"  - 平均: {round(statistics.mean(self.stats['response_times']) * 1000, 2)}ms")
            print(f"  - 最小: {round(min(self.stats['response_times']) * 1000, 2)}ms")
            print(f"  - 最大: {round(max(self.stats['response_times']) * 1000, 2)}ms")
            print(f"  - 中位数: {round(statistics.median(self.stats['response_times']) * 1000, 2)}ms")
        
        print(f"\n✅ 完成测试模块:")
        for test_name, test_data in self.stats["test_results"].items():
            print(f"  - {test_data.get('test_name', test_name)}")
    
    def save_results(self):
        """保存测试结果"""
        # JSON格式
        report_path = Path(__file__).parent / "comprehensive_stress_test_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False, default=str)
        
        ColorPrinter.print_success(f"详细测试报告已保存至: {report_path}")
        
        # Markdown格式
        self.generate_markdown_report()
    
    def generate_markdown_report(self):
        """生成Markdown测试报告"""
        report_path = Path(__file__).parent / "全面压力测试报告.md"
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# KOOK消息转发系统 - 全面压力测试报告\n\n")
            f.write(f"**测试时间**: {self.stats['start_time']}\n")
            f.write(f"**测试时长**: {(self.stats['end_time'] - self.stats['start_time']).total_seconds():.2f}秒\n\n")
            f.write("---\n\n")
            
            # 测试概览
            f.write("## 📊 测试概览\n\n")
            f.write("| 指标 | 值 |\n")
            f.write("|------|----|\n")
            f.write(f"| 总请求数 | {self.stats['total_requests']} |\n")
            f.write(f"| 成功请求 | {self.stats['successful_requests']} |\n")
            f.write(f"| 失败请求 | {self.stats['failed_requests']} |\n")
            if self.stats['total_requests'] > 0:
                success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
                f.write(f"| 成功率 | {success_rate:.2f}% |\n")
            f.write("\n---\n\n")
            
            # 各测试详细结果
            for test_name, test_data in self.stats["test_results"].items():
                f.write(f"## {test_data.get('test_name', test_name)}\n\n")
                
                if "results" in test_data and test_data["results"]:
                    results = test_data["results"]
                    
                    # 生成表格
                    if isinstance(results[0], dict):
                        keys = list(results[0].keys())
                        f.write("| " + " | ".join(keys) + " |\n")
                        f.write("|" + "|".join(["---"] * len(keys)) + "|\n")
                        
                        for result in results:
                            values = [str(result.get(k, "")) for k in keys]
                            f.write("| " + " | ".join(values) + " |\n")
                
                f.write("\n")
            
            f.write("---\n\n")
            f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        ColorPrinter.print_success(f"Markdown报告已保存至: {report_path}")


async def main():
    """主函数"""
    test_runner = ComprehensiveStressTest(COMPREHENSIVE_TEST_CONFIG)
    
    try:
        await test_runner.run_all_tests()
        test_runner.save_results()
    except KeyboardInterrupt:
        ColorPrinter.print_warning("\n测试被用户中断")
    except Exception as e:
        ColorPrinter.print_error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
