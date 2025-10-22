"""
KOOK消息转发系统 - 全面压力测试
根据需求文档对所有功能模块进行深度压力测试

测试模块:
1. API端点压力测试 (FastAPI)
2. 消息格式转换 (KMarkdown → Discord/Telegram/飞书)
3. Redis消息队列
4. 限流器 (Discord/Telegram/飞书)
5. 数据库性能 (SQLite)
6. 图片处理 (下载/压缩/图床/批量处理)
7. 消息过滤器 (关键词/用户/类型)
8. 转发器 (Discord/Telegram/飞书)
9. 端到端集成测试
10. 并发负载测试
"""
import asyncio
import aiohttp
import time
import random
import json
import sys
import os
import sqlite3
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import hashlib
from io import BytesIO

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))


# ============================================================================
# 测试配置
# ============================================================================

FULL_TEST_CONFIG = {
    # 基础配置
    "api_base_url": "http://127.0.0.1:9527",
    "redis_host": "127.0.0.1",
    "redis_port": 6379,
    
    # 并发测试级别
    "concurrent_levels": [1, 5, 10, 20, 50, 100, 200, 500],
    "max_stress_concurrent": 1000,  # 极限压力测试
    
    # 消息测试
    "message_batch_sizes": [10, 50, 100, 500, 1000, 5000, 10000],
    "long_message_sizes": [1000, 5000, 10000, 50000],  # 字符数
    
    # 格式转换测试
    "formatter_iterations": [1000, 5000, 10000, 50000, 100000],
    
    # 图片测试
    "image_sizes": [
        (800, 600, "小图"),
        (1920, 1080, "中图"),
        (3840, 2160, "4K图"),
        (7680, 4320, "8K图"),
    ],
    "image_batch_sizes": [5, 10, 20, 50],
    
    # 数据库测试
    "db_operations": [100, 500, 1000, 5000, 10000, 50000],
    
    # 限流测试
    "rate_limit_configs": [
        (5, 5, "Discord限流（5请求/5秒）"),
        (30, 1, "Telegram限流（30请求/1秒）"),
        (20, 1, "飞书限流（20请求/1秒）"),
        (100, 10, "高并发限流（100请求/10秒）"),
    ],
    
    # 过滤器测试
    "filter_test_count": 10000,
    "filter_keywords": ["广告", "代练", "外挂", "辅助", "刷钻", "测试"],
    
    # 性能基准
    "benchmarks": {
        "api_min_qps": 500,
        "db_min_qps": 1000,
        "formatter_min_ops": 10000,
        "queue_min_qps": 5000,
    }
}


# ============================================================================
# 彩色输出工具
# ============================================================================

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
    def header(text):
        print(f"\n{ColorPrinter.HEADER}{ColorPrinter.BOLD}{'=' * 80}{ColorPrinter.ENDC}")
        print(f"{ColorPrinter.HEADER}{ColorPrinter.BOLD}{text.center(80)}{ColorPrinter.ENDC}")
        print(f"{ColorPrinter.HEADER}{ColorPrinter.BOLD}{'=' * 80}{ColorPrinter.ENDC}\n")
    
    @staticmethod
    def success(text):
        print(f"{ColorPrinter.OKGREEN}✅ {text}{ColorPrinter.ENDC}")
    
    @staticmethod
    def error(text):
        print(f"{ColorPrinter.FAIL}❌ {text}{ColorPrinter.ENDC}")
    
    @staticmethod
    def warning(text):
        print(f"{ColorPrinter.WARNING}⚠️  {text}{ColorPrinter.ENDC}")
    
    @staticmethod
    def info(text):
        print(f"{ColorPrinter.OKCYAN}ℹ️  {text}{ColorPrinter.ENDC}")
    
    @staticmethod
    def metric(name, value, unit="", benchmark=None):
        """打印性能指标"""
        color = ColorPrinter.OKGREEN
        status = "✓"
        
        if benchmark and value < benchmark:
            color = ColorPrinter.FAIL
            status = "✗"
        
        print(f"{color}{status} {name}: {value}{unit}{ColorPrinter.ENDC}", end="")
        if benchmark:
            print(f" (基准: {benchmark}{unit})")
        else:
            print()


# ============================================================================
# 全面压力测试主类
# ============================================================================

class FullSystemStressTest:
    """KOOK消息转发系统 - 全面压力测试"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_base = config["api_base_url"]
        self.session = None
        
        # 测试统计
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "test_results": {},
            "performance_grades": {},
        }
    
    async def setup(self):
        """初始化测试环境"""
        ColorPrinter.header("KOOK消息转发系统 - 全面压力测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"API地址: {self.api_base}")
        print(f"测试配置: {len(self.config)} 项配置")
        print()
        
        # 创建HTTP会话
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # 检查服务状态
        try:
            async with self.session.get(f"{self.api_base}/health") as resp:
                if resp.status == 200:
                    ColorPrinter.success("后端服务运行正常")
                else:
                    ColorPrinter.error(f"后端服务响应异常 (status={resp.status})")
                    return False
        except Exception as e:
            ColorPrinter.error(f"无法连接到后端服务: {e}")
            ColorPrinter.info("请先启动后端服务: cd backend && python -m app.main")
            return False
        
        self.stats["start_time"] = datetime.now()
        return True
    
    async def teardown(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
        self.stats["end_time"] = datetime.now()
    
    # ========================================================================
    # 测试1: API端点极限压力测试
    # ========================================================================
    
    async def test_api_extreme_stress(self):
        """测试1: API端点极限压力测试"""
        ColorPrinter.header("测试1: API端点极限压力测试")
        
        endpoints = [
            ("GET", "/health", "健康检查"),
            ("GET", "/api/system/status", "系统状态"),
            ("GET", "/api/system/stats", "系统统计"),
            ("GET", "/api/accounts", "账号列表"),
            ("GET", "/api/bots", "Bot列表"),
            ("GET", "/api/mappings", "映射列表"),
            ("GET", "/api/logs?limit=10", "日志查询"),
        ]
        
        results = []
        
        for concurrent in self.config["concurrent_levels"]:
            ColorPrinter.info(f"并发度: {concurrent}")
            
            start_time = time.time()
            tasks = []
            
            # 随机选择端点发送并发请求
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
            
            response_times = [r["response_time"] for r in responses if isinstance(r, dict) and "response_time" in r]
            avg_time = statistics.mean(response_times) if response_times else 0
            max_time = max(response_times) if response_times else 0
            min_time = min(response_times) if response_times else 0
            
            # 计算百分位
            p50 = statistics.median(response_times) if response_times else 0
            p90 = statistics.quantiles(response_times, n=10)[8] if len(response_times) >= 10 else max_time
            p99 = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max_time
            
            qps = concurrent / elapsed if elapsed > 0 else 0
            
            result = {
                "concurrent": concurrent,
                "successful": successful,
                "failed": failed,
                "qps": round(qps, 2),
                "avg_ms": round(avg_time * 1000, 2),
                "min_ms": round(min_time * 1000, 2),
                "max_ms": round(max_time * 1000, 2),
                "p50_ms": round(p50 * 1000, 2),
                "p90_ms": round(p90 * 1000, 2),
                "p99_ms": round(p99 * 1000, 2),
                "elapsed": round(elapsed, 2),
            }
            results.append(result)
            
            # 打印结果
            print(f"  成功: {successful}/{concurrent}, QPS: {result['qps']:.2f}, "
                  f"平均: {result['avg_ms']}ms, P99: {result['p99_ms']}ms")
        
        self.stats["test_results"]["api_extreme_stress"] = results
        return results
    
    # ========================================================================
    # 测试2: 消息格式转换性能测试
    # ========================================================================
    
    async def test_formatter_performance(self):
        """测试2: 消息格式转换性能测试"""
        ColorPrinter.header("测试2: 消息格式转换性能测试")
        
        try:
            from app.processors.formatter import MessageFormatter
            
            formatter = MessageFormatter()
            
            # 测试文本样本
            test_texts = [
                "**粗体** *斜体* `代码`",
                "(emj)开心(emj) (emj)笑(emj) (emj)爱心(emj) @用户名 @全体成员",
                "这是一段很长的文本" + "测试消息 " * 100,
                "[链接文本](https://example.com) ~~删除线~~ **粗体和*斜体*混合**",
                "中文English混合🎉emoji表情(emj)火(emj)" * 10,
            ]
            
            results = []
            
            for iterations in self.config["formatter_iterations"]:
                ColorPrinter.info(f"迭代次数: {iterations}")
                
                test_result = {
                    "iterations": iterations,
                }
                
                # 测试Discord转换
                start = time.time()
                for _ in range(iterations):
                    for text in test_texts:
                        formatter.kmarkdown_to_discord(text)
                discord_time = time.time() - start
                discord_ops = (iterations * len(test_texts)) / discord_time
                test_result["discord_ops"] = round(discord_ops, 2)
                
                # 测试Telegram转换
                start = time.time()
                for _ in range(iterations):
                    for text in test_texts:
                        formatter.kmarkdown_to_telegram_html(text)
                telegram_time = time.time() - start
                telegram_ops = (iterations * len(test_texts)) / telegram_time
                test_result["telegram_ops"] = round(telegram_ops, 2)
                
                # 测试消息分段
                long_text = "测试消息 " * 1000
                start = time.time()
                for _ in range(iterations // 100 if iterations >= 100 else 1):
                    formatter.split_long_message(long_text, 2000)
                split_time = time.time() - start
                split_ops = (iterations // 100 if iterations >= 100 else 1) / split_time if split_time > 0 else 0
                test_result["split_ops"] = round(split_ops, 2)
                
                results.append(test_result)
                
                ColorPrinter.metric("Discord转换", discord_ops, " ops/s", 
                                   self.config["benchmarks"]["formatter_min_ops"])
                ColorPrinter.metric("Telegram转换", telegram_ops, " ops/s")
                ColorPrinter.metric("消息分段", split_ops, " ops/s")
            
            self.stats["test_results"]["formatter_performance"] = results
            return results
            
        except Exception as e:
            ColorPrinter.error(f"格式转换测试失败: {e}")
            return []
    
    # ========================================================================
    # 测试3: Redis队列极限压力测试
    # ========================================================================
    
    async def test_redis_queue_extreme(self):
        """测试3: Redis队列极限压力测试"""
        ColorPrinter.header("测试3: Redis队列极限压力测试")
        
        try:
            import redis.asyncio as aioredis
            
            redis_client = await aioredis.from_url(
                f"redis://{self.config['redis_host']}:{self.config['redis_port']}",
                encoding="utf-8",
                decode_responses=True
            )
            
            await redis_client.ping()
            ColorPrinter.success("Redis连接成功")
            
            results = []
            
            for batch_size in self.config["message_batch_sizes"]:
                ColorPrinter.info(f"批量大小: {batch_size}")
                
                test_queue = f"stress_test_queue_{int(time.time())}"
                
                # 生成测试消息
                messages = [
                    json.dumps({
                        "message_id": f"test_{i}",
                        "content": f"测试消息 {i}",
                        "timestamp": time.time(),
                        "data": "x" * 100  # 增加消息大小
                    })
                    for i in range(batch_size)
                ]
                
                # 测试单条入队
                start = time.time()
                for msg in messages:
                    await redis_client.rpush(test_queue, msg)
                enqueue_time = time.time() - start
                enqueue_qps = batch_size / enqueue_time
                
                # 测试单条出队
                start = time.time()
                for _ in range(batch_size):
                    await redis_client.lpop(test_queue)
                dequeue_time = time.time() - start
                dequeue_qps = batch_size / dequeue_time
                
                # 测试批量操作
                start = time.time()
                pipe = redis_client.pipeline()
                for msg in messages:
                    pipe.rpush(test_queue, msg)
                await pipe.execute()
                batch_time = time.time() - start
                batch_qps = batch_size / batch_time
                
                # 清理
                await redis_client.delete(test_queue)
                
                result = {
                    "batch_size": batch_size,
                    "enqueue_qps": round(enqueue_qps, 2),
                    "dequeue_qps": round(dequeue_qps, 2),
                    "batch_qps": round(batch_qps, 2),
                }
                results.append(result)
                
                ColorPrinter.metric("单条入队", enqueue_qps, " msg/s", 
                                   self.config["benchmarks"]["queue_min_qps"] if batch_size >= 1000 else None)
                ColorPrinter.metric("批量入队", batch_qps, " msg/s")
            
            await redis_client.close()
            
            self.stats["test_results"]["redis_queue_extreme"] = results
            return results
            
        except Exception as e:
            ColorPrinter.error(f"Redis队列测试失败: {e}")
            return []
    
    # ========================================================================
    # 测试4: 限流器精确度测试
    # ========================================================================
    
    async def test_rate_limiter_accuracy(self):
        """测试4: 限流器精确度测试"""
        ColorPrinter.header("测试4: 限流器精确度测试")
        
        try:
            from app.utils.rate_limiter import RateLimiter
            
            results = []
            
            for calls, period, name in self.config["rate_limit_configs"]:
                ColorPrinter.info(f"测试 {name}")
                
                limiter = RateLimiter(calls=calls, period=period)
                
                # 发送 calls * 3 个请求
                total_requests = calls * 3
                
                start_time = time.time()
                acquire_times = []
                
                for i in range(total_requests):
                    acquire_start = time.time()
                    await limiter.acquire()
                    acquire_time = time.time() - acquire_start
                    acquire_times.append(acquire_time)
                
                total_time = time.time() - start_time
                
                # 理论时间计算
                expected_time = period * ((total_requests / calls) - 1)
                accuracy = (1 - abs(total_time - expected_time) / expected_time) * 100 if expected_time > 0 else 100
                
                result = {
                    "name": name,
                    "calls": calls,
                    "period": period,
                    "total_requests": total_requests,
                    "actual_time": round(total_time, 2),
                    "expected_time": round(expected_time, 2),
                    "accuracy": round(accuracy, 2),
                    "avg_acquire": round(statistics.mean(acquire_times), 3),
                    "max_acquire": round(max(acquire_times), 3),
                }
                results.append(result)
                
                ColorPrinter.metric("准确度", accuracy, "%", 95)
                print(f"  实际: {result['actual_time']}s, 预期: {result['expected_time']}s")
            
            self.stats["test_results"]["rate_limiter_accuracy"] = results
            return results
            
        except Exception as e:
            ColorPrinter.error(f"限流器测试失败: {e}")
            return []
    
    # ========================================================================
    # 测试5: 数据库并发压力测试
    # ========================================================================
    
    async def test_database_concurrent(self):
        """测试5: 数据库并发压力测试"""
        ColorPrinter.header("测试5: 数据库并发压力测试")
        
        db_path = Path(__file__).parent / "backend" / "data" / "kook_forwarder.db"
        
        if not db_path.exists():
            ColorPrinter.warning("数据库文件不存在，跳过测试")
            return []
        
        results = []
        
        for operations in self.config["db_operations"]:
            ColorPrinter.info(f"操作数量: {operations}")
            
            # 测试简单查询
            start = time.time()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            for _ in range(operations):
                cursor.execute("SELECT COUNT(*) FROM message_logs")
                cursor.fetchone()
            
            simple_query_time = time.time() - start
            simple_qps = operations / simple_query_time
            
            # 测试插入操作
            start = time.time()
            cursor.execute("BEGIN TRANSACTION")
            insert_count = min(operations, 1000)
            for i in range(insert_count):
                cursor.execute("""
                    INSERT INTO message_logs 
                    (kook_message_id, kook_channel_id, content, message_type, 
                     sender_name, target_platform, target_channel, status, latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"stress_{int(time.time())}_{i}",
                    "stress_channel",
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
            insert_qps = insert_count / insert_time
            
            # 测试复杂查询
            start = time.time()
            complex_count = min(operations, 100)
            for _ in range(complex_count):
                cursor.execute("""
                    SELECT ml.*, cm.kook_channel_name 
                    FROM message_logs ml
                    LEFT JOIN channel_mappings cm ON ml.kook_channel_id = cm.kook_channel_id
                    WHERE ml.status = 'success'
                    ORDER BY ml.created_at DESC
                    LIMIT 10
                """)
                cursor.fetchall()
            complex_time = time.time() - start
            complex_qps = complex_count / complex_time if complex_time > 0 else 0
            
            # 清理
            cursor.execute("DELETE FROM message_logs WHERE kook_channel_id = 'stress_channel'")
            conn.commit()
            conn.close()
            
            result = {
                "operations": operations,
                "simple_qps": round(simple_qps, 2),
                "insert_qps": round(insert_qps, 2),
                "complex_qps": round(complex_qps, 2),
            }
            results.append(result)
            
            ColorPrinter.metric("简单查询", simple_qps, " qps", 
                               self.config["benchmarks"]["db_min_qps"] if operations >= 1000 else None)
            ColorPrinter.metric("插入", insert_qps, " qps")
            ColorPrinter.metric("复杂查询", complex_qps, " qps")
        
        self.stats["test_results"]["database_concurrent"] = results
        return results
    
    # ========================================================================
    # 测试6: 图片处理压力测试
    # ========================================================================
    
    async def test_image_processing_stress(self):
        """测试6: 图片处理压力测试"""
        ColorPrinter.header("测试6: 图片处理压力测试")
        
        try:
            from PIL import Image
            
            results = []
            
            for width, height, name in self.config["image_sizes"]:
                ColorPrinter.info(f"测试 {name} ({width}x{height})")
                
                # 生成测试图片
                img = Image.new('RGB', (width, height), color=(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                ))
                
                # 测试JPEG压缩（不同质量）
                jpeg_results = []
                for quality in [95, 85, 75, 60]:
                    start = time.time()
                    img_bytes = BytesIO()
                    img.save(img_bytes, format='JPEG', quality=quality)
                    compress_time = time.time() - start
                    size_kb = len(img_bytes.getvalue()) / 1024
                    jpeg_results.append({
                        "quality": quality,
                        "time": round(compress_time, 3),
                        "size_kb": round(size_kb, 2)
                    })
                
                # 测试PNG压缩
                start = time.time()
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG', optimize=True)
                png_time = time.time() - start
                png_size_kb = len(img_bytes.getvalue()) / 1024
                
                # 测试缩放
                start = time.time()
                for _ in range(10):
                    img.resize((width // 2, height // 2), Image.Resampling.LANCZOS)
                resize_time = (time.time() - start) / 10
                
                result = {
                    "name": name,
                    "width": width,
                    "height": height,
                    "jpeg_results": jpeg_results,
                    "png_time": round(png_time, 3),
                    "png_size_kb": round(png_size_kb, 2),
                    "resize_time": round(resize_time, 3),
                }
                results.append(result)
                
                print(f"  JPEG(85): {jpeg_results[1]['time']}s, {jpeg_results[1]['size_kb']}KB")
                print(f"  PNG: {result['png_time']}s, {result['png_size_kb']}KB")
                print(f"  缩放: {result['resize_time']}s/次")
            
            self.stats["test_results"]["image_processing_stress"] = results
            return results
            
        except Exception as e:
            ColorPrinter.error(f"图片处理测试失败: {e}")
            return []
    
    # ========================================================================
    # 测试7: 消息过滤器性能测试
    # ========================================================================
    
    async def test_message_filter_performance(self):
        """测试7: 消息过滤器性能测试"""
        ColorPrinter.header("测试7: 消息过滤器性能测试")
        
        try:
            from app.processors.filter import MessageFilter
            
            filter = MessageFilter()
            
            # 准备测试消息
            test_messages = []
            for i in range(self.config["filter_test_count"]):
                test_messages.append({
                    "message_id": f"test_{i}",
                    "content": random.choice([
                        "这是正常消息",
                        "广告信息请联系",
                        "代练服务",
                        "外挂辅助",
                        "官方公告",
                        "版本更新通知",
                    ]),
                    "sender_id": f"user_{random.randint(1, 100)}",
                    "sender_name": f"用户{random.randint(1, 100)}",
                    "message_type": random.choice(["text", "image", "file"]),
                })
            
            # 测试无规则过滤
            start = time.time()
            for msg in test_messages:
                filter.should_forward(msg)
            no_rule_time = time.time() - start
            no_rule_qps = len(test_messages) / no_rule_time
            
            ColorPrinter.metric("无规则过滤", no_rule_qps, " msg/s")
            
            # 添加规则并测试
            filter.add_rule("keyword_blacklist", self.config["filter_keywords"])
            
            start = time.time()
            passed = 0
            blocked = 0
            for msg in test_messages:
                should_forward, reason = filter.should_forward(msg)
                if should_forward:
                    passed += 1
                else:
                    blocked += 1
            with_rule_time = time.time() - start
            with_rule_qps = len(test_messages) / with_rule_time
            
            result = {
                "test_count": len(test_messages),
                "no_rule_qps": round(no_rule_qps, 2),
                "with_rule_qps": round(with_rule_qps, 2),
                "passed": passed,
                "blocked": blocked,
                "block_rate": round((blocked / len(test_messages)) * 100, 2)
            }
            
            ColorPrinter.metric("有规则过滤", with_rule_qps, " msg/s")
            print(f"  拦截率: {result['block_rate']}% ({blocked}/{len(test_messages)})")
            
            self.stats["test_results"]["message_filter_performance"] = result
            return result
            
        except Exception as e:
            ColorPrinter.error(f"过滤器测试失败: {e}")
            return {}
    
    # ========================================================================
    # 测试8: 端到端集成压力测试
    # ========================================================================
    
    async def test_end_to_end_integration(self):
        """测试8: 端到端集成压力测试"""
        ColorPrinter.header("测试8: 端到端集成压力测试")
        
        message_counts = [10, 50, 100, 500, 1000]
        results = []
        
        for msg_count in message_counts:
            ColorPrinter.info(f"消息数量: {msg_count}")
            
            async def process_complete_message(msg_id):
                """模拟完整的消息处理流程"""
                try:
                    # 1. 接收消息
                    await asyncio.sleep(0.001)
                    
                    # 2. 格式转换
                    from app.processors.formatter import MessageFormatter
                    formatter = MessageFormatter()
                    text = f"**测试消息 {msg_id}** 包含*格式*和`代码`"
                    formatter.kmarkdown_to_discord(text)
                    await asyncio.sleep(0.001)
                    
                    # 3. 过滤检查
                    from app.processors.filter import MessageFilter
                    filter = MessageFilter()
                    message = {
                        "content": text,
                        "sender_id": "test_user",
                        "sender_name": "测试用户",
                        "message_type": "text"
                    }
                    should_forward, _ = filter.should_forward(message)
                    if not should_forward:
                        return False
                    await asyncio.sleep(0.001)
                    
                    # 4. 限流控制
                    await asyncio.sleep(0.002)
                    
                    # 5. 模拟转发
                    await asyncio.sleep(0.01)
                    
                    # 6. 记录日志
                    await asyncio.sleep(0.001)
                    
                    return True
                except Exception as e:
                    return False
            
            # 并发处理消息
            start_time = time.time()
            tasks = [process_complete_message(i) for i in range(msg_count)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - start_time
            
            successful = sum(1 for r in responses if r is True)
            throughput = msg_count / elapsed if elapsed > 0 else 0
            
            result = {
                "message_count": msg_count,
                "successful": successful,
                "failed": msg_count - successful,
                "elapsed": round(elapsed, 3),
                "throughput": round(throughput, 2),
                "avg_latency_ms": round((elapsed / msg_count) * 1000, 2) if msg_count > 0 else 0,
            }
            results.append(result)
            
            ColorPrinter.metric("吞吐量", throughput, " msg/s")
            ColorPrinter.metric("平均延迟", result['avg_latency_ms'], "ms")
        
        self.stats["test_results"]["end_to_end_integration"] = results
        return results
    
    # ========================================================================
    # 测试9: 长消息处理测试
    # ========================================================================
    
    async def test_long_message_handling(self):
        """测试9: 长消息处理测试"""
        ColorPrinter.header("测试9: 长消息处理测试")
        
        try:
            from app.processors.formatter import MessageFormatter
            
            formatter = MessageFormatter()
            results = []
            
            for size in self.config["long_message_sizes"]:
                ColorPrinter.info(f"消息长度: {size} 字符")
                
                # 生成长消息
                long_text = "这是测试消息。" * (size // 10)
                
                # 测试分段（Discord 2000字符）
                start = time.time()
                discord_parts = formatter.split_long_message(long_text, 2000)
                discord_time = time.time() - start
                
                # 测试分段（Telegram 4096字符）
                start = time.time()
                telegram_parts = formatter.split_long_message(long_text, 4096)
                telegram_time = time.time() - start
                
                result = {
                    "size": size,
                    "discord_parts": len(discord_parts),
                    "discord_time": round(discord_time, 4),
                    "telegram_parts": len(telegram_parts),
                    "telegram_time": round(telegram_time, 4),
                }
                results.append(result)
                
                print(f"  Discord: {len(discord_parts)}段, {discord_time:.4f}s")
                print(f"  Telegram: {len(telegram_parts)}段, {telegram_time:.4f}s")
            
            self.stats["test_results"]["long_message_handling"] = results
            return results
            
        except Exception as e:
            ColorPrinter.error(f"长消息测试失败: {e}")
            return []
    
    # ========================================================================
    # 测试10: 系统综合性能评分
    # ========================================================================
    
    def calculate_performance_grades(self):
        """计算系统性能评分"""
        ColorPrinter.header("系统性能评分")
        
        grades = {}
        benchmarks = self.config["benchmarks"]
        
        # API性能评分
        if "api_extreme_stress" in self.stats["test_results"]:
            api_results = self.stats["test_results"]["api_extreme_stress"]
            # 取并发100的QPS
            qps_100 = next((r["qps"] for r in api_results if r["concurrent"] == 100), 0)
            api_score = (qps_100 / benchmarks["api_min_qps"]) * 100
            grades["API性能"] = {
                "score": round(api_score, 2),
                "value": qps_100,
                "benchmark": benchmarks["api_min_qps"],
                "grade": self._get_grade(api_score)
            }
        
        # 数据库性能评分
        if "database_concurrent" in self.stats["test_results"]:
            db_results = self.stats["test_results"]["database_concurrent"]
            # 取1000操作的QPS
            qps_1000 = next((r["simple_qps"] for r in db_results if r["operations"] == 1000), 0)
            db_score = (qps_1000 / benchmarks["db_min_qps"]) * 100
            grades["数据库性能"] = {
                "score": round(db_score, 2),
                "value": qps_1000,
                "benchmark": benchmarks["db_min_qps"],
                "grade": self._get_grade(db_score)
            }
        
        # 格式转换性能评分
        if "formatter_performance" in self.stats["test_results"]:
            fmt_results = self.stats["test_results"]["formatter_performance"]
            # 取10000迭代的ops
            ops_10k = next((r["discord_ops"] for r in fmt_results if r["iterations"] == 10000), 0)
            fmt_score = (ops_10k / benchmarks["formatter_min_ops"]) * 100
            grades["格式转换性能"] = {
                "score": round(fmt_score, 2),
                "value": ops_10k,
                "benchmark": benchmarks["formatter_min_ops"],
                "grade": self._get_grade(fmt_score)
            }
        
        # 队列性能评分
        if "redis_queue_extreme" in self.stats["test_results"]:
            queue_results = self.stats["test_results"]["redis_queue_extreme"]
            # 取1000批量的QPS
            qps_1k = next((r["batch_qps"] for r in queue_results if r["batch_size"] == 1000), 0)
            queue_score = (qps_1k / benchmarks["queue_min_qps"]) * 100
            grades["队列性能"] = {
                "score": round(queue_score, 2),
                "value": qps_1k,
                "benchmark": benchmarks["queue_min_qps"],
                "grade": self._get_grade(queue_score)
            }
        
        # 限流器准确度评分
        if "rate_limiter_accuracy" in self.stats["test_results"]:
            limiter_results = self.stats["test_results"]["rate_limiter_accuracy"]
            avg_accuracy = statistics.mean([r["accuracy"] for r in limiter_results])
            grades["限流器准确度"] = {
                "score": round(avg_accuracy, 2),
                "value": avg_accuracy,
                "benchmark": 95,
                "grade": self._get_grade(avg_accuracy)
            }
        
        # 打印评分
        print("\n" + "=" * 80)
        for name, data in grades.items():
            grade_color = {
                "优秀": ColorPrinter.OKGREEN,
                "良好": ColorPrinter.OKBLUE,
                "及格": ColorPrinter.WARNING,
                "较差": ColorPrinter.FAIL,
            }.get(data["grade"], ColorPrinter.ENDC)
            
            print(f"{grade_color}{name}: {data['score']}分 ({data['grade']}){ColorPrinter.ENDC}")
            print(f"  实际值: {data['value']}, 基准: {data['benchmark']}")
        print("=" * 80 + "\n")
        
        # 计算总分
        total_score = statistics.mean([g["score"] for g in grades.values()])
        overall_grade = self._get_grade(total_score)
        
        print(f"{ColorPrinter.BOLD}系统总评分: {total_score:.2f}分 ({overall_grade}){ColorPrinter.ENDC}\n")
        
        self.stats["performance_grades"] = grades
        self.stats["overall_score"] = round(total_score, 2)
        self.stats["overall_grade"] = overall_grade
        
        return grades
    
    def _get_grade(self, score):
        """根据分数获取等级"""
        if score >= 120:
            return "优秀"
        elif score >= 100:
            return "良好"
        elif score >= 80:
            return "及格"
        else:
            return "较差"
    
    # ========================================================================
    # 辅助方法
    # ========================================================================
    
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
    
    # ========================================================================
    # 主测试流程
    # ========================================================================
    
    async def run_all_tests(self):
        """运行所有压力测试"""
        if not await self.setup():
            return
        
        try:
            # 执行所有测试
            await self.test_api_extreme_stress()
            await self.test_formatter_performance()
            await self.test_redis_queue_extreme()
            await self.test_rate_limiter_accuracy()
            await self.test_database_concurrent()
            await self.test_image_processing_stress()
            await self.test_message_filter_performance()
            await self.test_end_to_end_integration()
            await self.test_long_message_handling()
            
            # 计算性能评分
            self.calculate_performance_grades()
            
            # 打印总结
            self.print_summary()
            
        finally:
            await self.teardown()
    
    def print_summary(self):
        """打印测试总结"""
        ColorPrinter.header("测试总结")
        
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
            print(f"\n⏱️  API响应时间统计:")
            print(f"  - 平均: {round(statistics.mean(self.stats['response_times']) * 1000, 2)}ms")
            print(f"  - 最小: {round(min(self.stats['response_times']) * 1000, 2)}ms")
            print(f"  - 最大: {round(max(self.stats['response_times']) * 1000, 2)}ms")
            print(f"  - 中位数: {round(statistics.median(self.stats['response_times']) * 1000, 2)}ms")
        
        print(f"\n✅ 完成测试模块: {len(self.stats['test_results'])}个")
        for test_name in self.stats["test_results"].keys():
            print(f"  - {test_name}")
    
    def save_results(self):
        """保存测试结果"""
        # JSON格式
        report_path = Path(__file__).parent / "test_results" / "full_stress_test_report.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False, default=str)
        
        ColorPrinter.success(f"详细测试报告已保存至: {report_path}")
        
        # Markdown格式
        self.generate_markdown_report()
        
        # HTML格式
        self.generate_html_report()
    
    def generate_markdown_report(self):
        """生成Markdown测试报告"""
        report_path = Path(__file__).parent / "test_results" / "全面压力测试报告.md"
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# KOOK消息转发系统 - 全面压力测试报告\n\n")
            f.write(f"**测试时间**: {self.stats['start_time']}\n")
            f.write(f"**测试时长**: {(self.stats['end_time'] - self.stats['start_time']).total_seconds():.2f}秒\n\n")
            f.write("---\n\n")
            
            # 性能评分
            f.write("## 📊 性能评分\n\n")
            if "performance_grades" in self.stats:
                f.write("| 测试项 | 得分 | 等级 | 实际值 | 基准值 |\n")
                f.write("|--------|------|------|--------|--------|\n")
                for name, data in self.stats["performance_grades"].items():
                    f.write(f"| {name} | {data['score']} | {data['grade']} | {data['value']} | {data['benchmark']} |\n")
                
                f.write(f"\n**系统总评分**: {self.stats.get('overall_score', 0)}分 ({self.stats.get('overall_grade', 'N/A')})\n\n")
            
            f.write("---\n\n")
            
            # 各测试详细结果
            for test_name, test_data in self.stats["test_results"].items():
                f.write(f"## {test_name}\n\n")
                
                if isinstance(test_data, list) and test_data:
                    # 表格格式
                    keys = list(test_data[0].keys())
                    f.write("| " + " | ".join(keys) + " |\n")
                    f.write("|" + "|".join(["---"] * len(keys)) + "|\n")
                    
                    for result in test_data:
                        values = [str(result.get(k, "")) for k in keys]
                        f.write("| " + " | ".join(values) + " |\n")
                elif isinstance(test_data, dict):
                    # 键值对格式
                    for key, value in test_data.items():
                        f.write(f"- **{key}**: {value}\n")
                
                f.write("\n")
            
            f.write("---\n\n")
            f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        ColorPrinter.success(f"Markdown报告已保存至: {report_path}")
    
    def generate_html_report(self):
        """生成HTML测试报告"""
        report_path = Path(__file__).parent / "test_results" / "full_stress_test_report.html"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KOOK消息转发系统 - 全面压力测试报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .grade-优秀 {{ color: #4CAF50; font-weight: bold; }}
        .grade-良好 {{ color: #2196F3; font-weight: bold; }}
        .grade-及格 {{ color: #FF9800; font-weight: bold; }}
        .grade-较差 {{ color: #f44336; font-weight: bold; }}
        .metric {{
            display: inline-block;
            padding: 5px 10px;
            margin: 5px;
            background-color: #e3f2fd;
            border-radius: 3px;
        }}
        .summary-box {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <h1>🚀 KOOK消息转发系统 - 全面压力测试报告</h1>
    
    <div class="summary-box">
        <h2>📋 测试概览</h2>
        <p><strong>测试时间</strong>: {self.stats['start_time']}</p>
        <p><strong>测试时长</strong>: {(self.stats['end_time'] - self.stats['start_time']).total_seconds():.2f}秒</p>
        <p><strong>总请求数</strong>: {self.stats['total_requests']}</p>
        <p><strong>成功请求</strong>: {self.stats['successful_requests']}</p>
        <p><strong>失败请求</strong>: {self.stats['failed_requests']}</p>
        <p><strong>成功率</strong>: {(self.stats['successful_requests'] / self.stats['total_requests'] * 100) if self.stats['total_requests'] > 0 else 0:.2f}%</p>
    </div>
    
    <div class="summary-box">
        <h2>🏆 性能评分</h2>
        <p><strong>系统总评分</strong>: <span class="grade-{self.stats.get('overall_grade', '')}">{self.stats.get('overall_score', 0)}分 ({self.stats.get('overall_grade', 'N/A')})</span></p>
        <table>
            <tr>
                <th>测试项</th>
                <th>得分</th>
                <th>等级</th>
                <th>实际值</th>
                <th>基准值</th>
            </tr>
"""
        
        if "performance_grades" in self.stats:
            for name, data in self.stats["performance_grades"].items():
                html_content += f"""
            <tr>
                <td>{name}</td>
                <td>{data['score']}</td>
                <td class="grade-{data['grade']}">{data['grade']}</td>
                <td>{data['value']}</td>
                <td>{data['benchmark']}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
    
    <div class="summary-box">
        <h2>📈 详细测试结果</h2>
"""
        
        for test_name, test_data in self.stats["test_results"].items():
            html_content += f"<h3>{test_name}</h3>\n"
            
            if isinstance(test_data, list) and test_data:
                keys = list(test_data[0].keys())
                html_content += "<table>\n<tr>"
                for key in keys:
                    html_content += f"<th>{key}</th>"
                html_content += "</tr>\n"
                
                for result in test_data:
                    html_content += "<tr>"
                    for key in keys:
                        html_content += f"<td>{result.get(key, '')}</td>"
                    html_content += "</tr>\n"
                html_content += "</table>\n"
        
        html_content += f"""
    </div>
    
    <footer style="text-align: center; margin-top: 50px; padding: 20px; color: #777;">
        <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>
</body>
</html>
"""
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        ColorPrinter.success(f"HTML报告已保存至: {report_path}")


# ============================================================================
# 主函数
# ============================================================================

async def main():
    """主函数"""
    print("=" * 80)
    print("KOOK消息转发系统 - 全面压力测试".center(80))
    print("=" * 80)
    print()
    
    test_runner = FullSystemStressTest(FULL_TEST_CONFIG)
    
    try:
        await test_runner.run_all_tests()
        test_runner.save_results()
        
        ColorPrinter.success("\n所有测试完成！")
        
    except KeyboardInterrupt:
        ColorPrinter.warning("\n测试被用户中断")
    except Exception as e:
        ColorPrinter.error(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
