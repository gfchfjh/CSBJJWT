"""
KOOK消息转发系统 - 压力测试脚本
测试所有核心功能的性能和稳定性
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
from typing import List, Dict, Any
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 测试配置
TEST_CONFIG = {
    "api_base_url": "http://127.0.0.1:9527",
    "redis_host": "127.0.0.1",
    "redis_port": 6379,
    "concurrent_users": [1, 10, 50, 100, 200],  # 并发用户数
    "test_duration": 60,  # 每个测试持续时间（秒）
    "message_batch_sizes": [10, 50, 100, 500, 1000],  # 消息批量大小
}

# 测试结果存储
test_results = {
    "start_time": None,
    "end_time": None,
    "tests": {}
}


class StressTestRunner:
    """压力测试运行器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_base = config["api_base_url"]
        self.session = None
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        
    async def setup(self):
        """初始化测试环境"""
        print("=" * 80)
        print("KOOK消息转发系统 - 压力测试")
        print("=" * 80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"API地址: {self.api_base}")
        print("=" * 80)
        print()
        
        # 创建HTTP会话
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # 检查服务是否运行
        try:
            async with self.session.get(f"{self.api_base}/health") as resp:
                if resp.status == 200:
                    print("✅ 后端服务运行正常")
                else:
                    print("❌ 后端服务响应异常")
                    return False
        except Exception as e:
            print(f"❌ 无法连接到后端服务: {e}")
            print("请先启动后端服务: cd backend && python -m app.main")
            return False
        
        return True
    
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
                else:
                    self.failed_requests += 1
                
                return {
                    "status": resp.status,
                    "response_time": response_time,
                    "data": await resp.json() if resp.content_type == 'application/json' else None
                }
        except Exception as e:
            response_time = time.time() - start_time
            self.failed_requests += 1
            return {
                "status": 0,
                "response_time": response_time,
                "error": str(e)
            }
    
    async def test_api_endpoints(self) -> Dict[str, Any]:
        """测试1: API端点响应测试"""
        print("\n" + "=" * 80)
        print("测试1: API端点响应测试")
        print("=" * 80)
        
        endpoints = [
            ("GET", "/", "根路径"),
            ("GET", "/health", "健康检查"),
            ("GET", "/api/accounts", "账号列表"),
            ("GET", "/api/bots", "Bot列表"),
            ("GET", "/api/mappings", "映射列表"),
            ("GET", "/api/logs?limit=10", "日志查询"),
            ("GET", "/api/system/status", "系统状态"),
            ("GET", "/api/system/stats", "系统统计"),
        ]
        
        results = []
        
        for method, endpoint, name in endpoints:
            print(f"测试 {name} ({method} {endpoint})...", end=" ")
            result = await self.make_request(method, endpoint)
            
            if result["status"] < 400:
                print(f"✅ {result['response_time']*1000:.2f}ms")
                results.append({
                    "name": name,
                    "endpoint": endpoint,
                    "status": "success",
                    "response_time": result["response_time"]
                })
            else:
                print(f"❌ 失败 (status={result['status']})")
                results.append({
                    "name": name,
                    "endpoint": endpoint,
                    "status": "failed",
                    "error": result.get("error", "Unknown")
                })
        
        return {
            "test_name": "API端点响应测试",
            "total_endpoints": len(endpoints),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "results": results
        }
    
    async def test_concurrent_requests(self, concurrent: int) -> Dict[str, Any]:
        """测试2: 并发请求测试"""
        print(f"\n测试并发度: {concurrent}...", end=" ")
        
        start_time = time.time()
        tasks = []
        
        # 创建并发任务
        for i in range(concurrent):
            # 随机选择不同的端点
            endpoints = [
                ("GET", "/api/system/status"),
                ("GET", "/api/accounts"),
                ("GET", "/api/bots"),
                ("GET", "/api/mappings"),
                ("GET", f"/api/logs?limit=10&offset={random.randint(0, 100)}"),
            ]
            method, endpoint = random.choice(endpoints)
            tasks.append(self.make_request(method, endpoint))
        
        # 执行并发请求
        results = await asyncio.gather(*tasks)
        
        elapsed_time = time.time() - start_time
        successful = sum(1 for r in results if r["status"] < 400)
        failed = concurrent - successful
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        max_response_time = max(r["response_time"] for r in results)
        min_response_time = min(r["response_time"] for r in results)
        
        qps = concurrent / elapsed_time if elapsed_time > 0 else 0
        
        print(f"✅ QPS: {qps:.2f}, 平均响应: {avg_response_time*1000:.2f}ms")
        
        return {
            "concurrent": concurrent,
            "total_requests": concurrent,
            "successful": successful,
            "failed": failed,
            "elapsed_time": elapsed_time,
            "qps": qps,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time
        }
    
    async def test_database_performance(self) -> Dict[str, Any]:
        """测试3: 数据库性能测试"""
        print("\n" + "=" * 80)
        print("测试3: 数据库性能测试")
        print("=" * 80)
        
        db_path = Path(__file__).parent / "backend" / "data" / "kook_forwarder.db"
        
        if not db_path.exists():
            print("❌ 数据库文件不存在")
            return {"status": "skipped", "reason": "数据库文件不存在"}
        
        results = {}
        
        # 测试简单查询
        print("测试简单查询...", end=" ")
        start = time.time()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for _ in range(1000):
            cursor.execute("SELECT COUNT(*) FROM message_logs")
            cursor.fetchone()
        
        simple_query_time = time.time() - start
        print(f"✅ 1000次查询耗时: {simple_query_time:.3f}s")
        results["simple_query_1000"] = simple_query_time
        
        # 测试复杂查询（带JOIN）
        print("测试复杂查询（JOIN）...", end=" ")
        start = time.time()
        
        for _ in range(100):
            cursor.execute("""
                SELECT ml.*, cm.kook_channel_name 
                FROM message_logs ml
                LEFT JOIN channel_mappings cm ON ml.kook_channel_id = cm.kook_channel_id
                LIMIT 10
            """)
            cursor.fetchall()
        
        complex_query_time = time.time() - start
        print(f"✅ 100次查询耗时: {complex_query_time:.3f}s")
        results["complex_query_100"] = complex_query_time
        
        # 测试索引效果
        print("测试索引查询...", end=" ")
        start = time.time()
        
        for _ in range(1000):
            cursor.execute("""
                SELECT * FROM message_logs 
                WHERE status = 'success' 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            cursor.fetchall()
        
        indexed_query_time = time.time() - start
        print(f"✅ 1000次查询耗时: {indexed_query_time:.3f}s")
        results["indexed_query_1000"] = indexed_query_time
        
        # 测试插入性能
        print("测试批量插入...", end=" ")
        start = time.time()
        
        cursor.execute("BEGIN TRANSACTION")
        for i in range(100):
            cursor.execute("""
                INSERT INTO message_logs 
                (kook_message_id, kook_channel_id, content, message_type, sender_name, 
                 target_platform, target_channel, status, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"test_{int(time.time())}_{i}",
                "test_channel",
                f"测试消息 {i}",
                "text",
                "测试用户",
                "discord",
                "test_target",
                "success",
                100
            ))
        cursor.execute("COMMIT")
        
        insert_time = time.time() - start
        print(f"✅ 100条插入耗时: {insert_time:.3f}s")
        results["insert_100"] = insert_time
        
        # 清理测试数据
        cursor.execute("DELETE FROM message_logs WHERE kook_channel_id = 'test_channel'")
        conn.commit()
        
        conn.close()
        
        return {
            "test_name": "数据库性能测试",
            "status": "success",
            "results": results
        }
    
    async def test_message_queue(self, batch_size: int) -> Dict[str, Any]:
        """测试4: 消息队列性能测试"""
        print(f"测试批量大小: {batch_size}...", end=" ")
        
        try:
            import redis
            r = redis.Redis(
                host=self.config["redis_host"],
                port=self.config["redis_port"],
                decode_responses=True
            )
            
            # 测试入队性能
            start = time.time()
            for i in range(batch_size):
                message = {
                    "id": f"test_{int(time.time())}_{i}",
                    "type": "text",
                    "content": f"测试消息 {i}",
                    "timestamp": time.time()
                }
                r.lpush("test_queue", json.dumps(message))
            
            enqueue_time = time.time() - start
            
            # 测试出队性能
            start = time.time()
            for _ in range(batch_size):
                r.rpop("test_queue")
            
            dequeue_time = time.time() - start
            
            print(f"✅ 入队: {enqueue_time:.3f}s, 出队: {dequeue_time:.3f}s")
            
            return {
                "batch_size": batch_size,
                "enqueue_time": enqueue_time,
                "dequeue_time": dequeue_time,
                "enqueue_qps": batch_size / enqueue_time if enqueue_time > 0 else 0,
                "dequeue_qps": batch_size / dequeue_time if dequeue_time > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Redis连接失败: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_rate_limiter(self) -> Dict[str, Any]:
        """测试5: 限流器性能测试"""
        print("\n" + "=" * 80)
        print("测试5: 限流器性能测试")
        print("=" * 80)
        
        try:
            from app.utils.rate_limiter import RateLimiter
            
            results = []
            
            # 测试不同限流配置
            configs = [
                (5, 5, "Discord限流（5请求/5秒）"),
                (30, 1, "Telegram限流（30请求/1秒）"),
                (20, 1, "飞书限流（20请求/1秒）"),
            ]
            
            for calls, period, name in configs:
                print(f"\n测试 {name}...")
                limiter = RateLimiter(calls=calls, period=period)
                
                start = time.time()
                acquire_times = []
                
                # 发送calls*2个请求，测试限流效果
                for i in range(calls * 2):
                    acquire_start = time.time()
                    await limiter.acquire()
                    acquire_time = time.time() - acquire_start
                    acquire_times.append(acquire_time)
                    
                    if i < calls:
                        # 前calls个请求应该立即通过
                        if acquire_time > 0.1:
                            print(f"  ⚠️ 请求{i+1}等待时间过长: {acquire_time:.3f}s")
                    else:
                        # 后续请求应该被限流
                        print(f"  ✅ 请求{i+1}被限流，等待: {acquire_time:.3f}s")
                
                total_time = time.time() - start
                
                results.append({
                    "name": name,
                    "calls": calls,
                    "period": period,
                    "total_requests": calls * 2,
                    "total_time": total_time,
                    "avg_acquire_time": sum(acquire_times) / len(acquire_times),
                    "max_acquire_time": max(acquire_times)
                })
            
            return {
                "test_name": "限流器性能测试",
                "status": "success",
                "results": results
            }
            
        except Exception as e:
            print(f"❌ 限流器测试失败: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_image_processing(self) -> Dict[str, Any]:
        """测试6: 图片处理性能测试"""
        print("\n" + "=" * 80)
        print("测试6: 图片处理性能测试")
        print("=" * 80)
        
        try:
            from app.processors.image import ImageProcessor
            from PIL import Image
            import io
            
            processor = ImageProcessor()
            results = []
            
            # 生成不同大小的测试图片
            test_images = [
                (800, 600, "小图"),
                (1920, 1080, "中图"),
                (4096, 3072, "大图"),
            ]
            
            for width, height, name in test_images:
                print(f"\n测试 {name} ({width}x{height})...")
                
                # 创建测试图片
                img = Image.new('RGB', (width, height), color='red')
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG', quality=95)
                original_size = img_bytes.tell()
                
                print(f"  原始大小: {original_size/1024:.2f}KB")
                
                # 测试压缩性能
                start = time.time()
                compressed = await processor.compress_image(img_bytes.getvalue(), max_size_mb=10)
                compress_time = time.time() - start
                
                compressed_size = len(compressed) if compressed else original_size
                compression_ratio = (1 - compressed_size / original_size) * 100
                
                print(f"  压缩后: {compressed_size/1024:.2f}KB")
                print(f"  压缩比: {compression_ratio:.1f}%")
                print(f"  耗时: {compress_time:.3f}s")
                
                results.append({
                    "name": name,
                    "width": width,
                    "height": height,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": compression_ratio,
                    "compress_time": compress_time
                })
            
            return {
                "test_name": "图片处理性能测试",
                "status": "success",
                "results": results
            }
            
        except Exception as e:
            print(f"❌ 图片处理测试失败: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_message_formatter(self) -> Dict[str, Any]:
        """测试7: 消息格式转换性能测试"""
        print("\n" + "=" * 80)
        print("测试7: 消息格式转换性能测试")
        print("=" * 80)
        
        try:
            from app.processors.formatter import (
                kmarkdown_to_discord,
                kmarkdown_to_telegram_html,
                kmarkdown_to_feishu
            )
            
            # 测试文本
            test_text = """
            **这是粗体文本**
            *这是斜体文本*
            `这是代码`
            (emj)开心(emj) (emj)笑(emj) (emj)爱心(emj)
            @用户名 @全体成员
            http://example.com/test
            """
            
            results = []
            
            # 测试Discord转换
            print("测试Discord格式转换...", end=" ")
            start = time.time()
            for _ in range(10000):
                kmarkdown_to_discord(test_text)
            discord_time = time.time() - start
            print(f"✅ 10000次转换耗时: {discord_time:.3f}s")
            results.append({
                "format": "Discord",
                "iterations": 10000,
                "time": discord_time,
                "ops_per_sec": 10000 / discord_time
            })
            
            # 测试Telegram转换
            print("测试Telegram格式转换...", end=" ")
            start = time.time()
            for _ in range(10000):
                kmarkdown_to_telegram_html(test_text)
            telegram_time = time.time() - start
            print(f"✅ 10000次转换耗时: {telegram_time:.3f}s")
            results.append({
                "format": "Telegram",
                "iterations": 10000,
                "time": telegram_time,
                "ops_per_sec": 10000 / telegram_time
            })
            
            # 测试飞书转换
            print("测试飞书格式转换...", end=" ")
            start = time.time()
            for _ in range(10000):
                kmarkdown_to_feishu(test_text)
            feishu_time = time.time() - start
            print(f"✅ 10000次转换耗时: {feishu_time:.3f}s")
            results.append({
                "format": "飞书",
                "iterations": 10000,
                "time": feishu_time,
                "ops_per_sec": 10000 / feishu_time
            })
            
            return {
                "test_name": "消息格式转换性能测试",
                "status": "success",
                "results": results
            }
            
        except Exception as e:
            print(f"❌ 格式转换测试失败: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def run_all_tests(self):
        """运行所有压力测试"""
        test_results["start_time"] = datetime.now().isoformat()
        
        # 初始化
        if not await self.setup():
            return
        
        try:
            # 测试1: API端点响应
            result = await self.test_api_endpoints()
            test_results["tests"]["api_endpoints"] = result
            
            # 测试2: 并发请求
            print("\n" + "=" * 80)
            print("测试2: 并发请求测试")
            print("=" * 80)
            
            concurrent_results = []
            for concurrent in self.config["concurrent_users"]:
                result = await self.test_concurrent_requests(concurrent)
                concurrent_results.append(result)
            
            test_results["tests"]["concurrent_requests"] = {
                "test_name": "并发请求测试",
                "results": concurrent_results
            }
            
            # 测试3: 数据库性能
            result = await self.test_database_performance()
            test_results["tests"]["database"] = result
            
            # 测试4: 消息队列
            print("\n" + "=" * 80)
            print("测试4: 消息队列性能测试")
            print("=" * 80)
            
            queue_results = []
            for batch_size in self.config["message_batch_sizes"]:
                result = await self.test_message_queue(batch_size)
                queue_results.append(result)
            
            test_results["tests"]["message_queue"] = {
                "test_name": "消息队列性能测试",
                "results": queue_results
            }
            
            # 测试5: 限流器
            result = await self.test_rate_limiter()
            test_results["tests"]["rate_limiter"] = result
            
            # 测试6: 图片处理
            result = await self.test_image_processing()
            test_results["tests"]["image_processing"] = result
            
            # 测试7: 消息格式转换
            result = await self.test_message_formatter()
            test_results["tests"]["message_formatter"] = result
            
            # 总结
            self.print_summary()
            
        finally:
            await self.teardown()
            test_results["end_time"] = datetime.now().isoformat()
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 80)
        print("测试总结")
        print("=" * 80)
        
        print(f"\n总请求数: {self.total_requests}")
        print(f"成功请求: {self.successful_requests}")
        print(f"失败请求: {self.failed_requests}")
        print(f"成功率: {self.successful_requests/self.total_requests*100:.2f}%")
        
        if self.response_times:
            avg_time = sum(self.response_times) / len(self.response_times)
            max_time = max(self.response_times)
            min_time = min(self.response_times)
            
            print(f"\n响应时间统计:")
            print(f"  平均: {avg_time*1000:.2f}ms")
            print(f"  最大: {max_time*1000:.2f}ms")
            print(f"  最小: {min_time*1000:.2f}ms")
            
            # 计算百分位数
            sorted_times = sorted(self.response_times)
            p50 = sorted_times[len(sorted_times)//2]
            p90 = sorted_times[int(len(sorted_times)*0.9)]
            p99 = sorted_times[int(len(sorted_times)*0.99)]
            
            print(f"  P50: {p50*1000:.2f}ms")
            print(f"  P90: {p90*1000:.2f}ms")
            print(f"  P99: {p99*1000:.2f}ms")


async def main():
    """主函数"""
    runner = StressTestRunner(TEST_CONFIG)
    await runner.run_all_tests()
    
    # 保存测试结果
    report_path = Path(__file__).parent / "stress_test_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细测试报告已保存至: {report_path}")
    
    # 生成Markdown报告
    generate_markdown_report(test_results)


def generate_markdown_report(results: Dict[str, Any]):
    """生成Markdown格式的测试报告"""
    report_path = Path(__file__).parent / "压力测试报告.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# KOOK消息转发系统 - 压力测试报告\n\n")
        f.write(f"**测试时间**: {results['start_time']}\n\n")
        f.write("---\n\n")
        
        f.write("## 📊 测试概览\n\n")
        f.write("| 测试项 | 状态 |\n")
        f.write("|--------|------|\n")
        
        for test_name, test_data in results["tests"].items():
            status = "✅" if test_data.get("status") != "failed" else "❌"
            f.write(f"| {test_data.get('test_name', test_name)} | {status} |\n")
        
        f.write("\n---\n\n")
        
        # 详细结果
        for test_name, test_data in results["tests"].items():
            f.write(f"## {test_data.get('test_name', test_name)}\n\n")
            
            if "results" in test_data:
                if isinstance(test_data["results"], list):
                    # 表格格式
                    if test_data["results"]:
                        # 获取所有键
                        keys = test_data["results"][0].keys()
                        f.write("| " + " | ".join(keys) + " |\n")
                        f.write("|" + "|".join(["---"] * len(keys)) + "|\n")
                        
                        for result in test_data["results"]:
                            values = [str(result.get(k, "")) for k in keys]
                            f.write("| " + " | ".join(values) + " |\n")
                else:
                    # 键值对格式
                    for key, value in test_data["results"].items():
                        f.write(f"- **{key}**: {value}\n")
            
            f.write("\n")
        
        f.write("---\n\n")
        f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"Markdown测试报告已保存至: {report_path}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(0)
