"""
KOOK消息转发系统 - 模块独立压力测试
不依赖后端服务运行,直接测试各个核心模块的性能

测试模块:
1. 消息格式转换器 (MessageFormatter)
2. 限流器 (RateLimiter)
3. 图片处理器 (ImageProcessor) 
4. 消息过滤器 (MessageFilter)
5. 数据库操作 (Database)
6. Redis队列 (如果Redis可用)
"""
import asyncio
import time
import random
import json
import sys
import os
import sqlite3
import statistics
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from io import BytesIO

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))


# ============================================================================
# 彩色输出
# ============================================================================

class ColorPrinter:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def header(text):
        print(f"\n{ColorPrinter.BOLD}{'=' * 80}{ColorPrinter.ENDC}")
        print(f"{ColorPrinter.BOLD}{text.center(80)}{ColorPrinter.ENDC}")
        print(f"{ColorPrinter.BOLD}{'=' * 80}{ColorPrinter.ENDC}\n")
    
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
        print(f"ℹ️  {text}")


# ============================================================================
# 测试主类
# ============================================================================

class ModuleStressTest:
    """模块独立压力测试"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
    
    async def run_all_tests(self):
        """运行所有测试"""
        ColorPrinter.header("KOOK消息转发系统 - 模块独立压力测试")
        print(f"测试时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 执行各项测试
        await self.test_formatter()
        await self.test_rate_limiter()
        await self.test_image_processor()
        await self.test_message_filter()
        await self.test_database()
        await self.test_redis_queue()
        
        # 生成报告
        self.generate_report()
    
    async def test_formatter(self):
        """测试1: 消息格式转换器"""
        ColorPrinter.header("测试1: 消息格式转换器性能测试")
        
        try:
            from app.processors.formatter import MessageFormatter
            
            formatter = MessageFormatter()
            
            # 测试文本样本
            test_texts = [
                "**粗体** *斜体* `代码`",
                "(emj)开心(emj) (emj)笑(emj) (emj)爱心(emj) @用户名",
                "这是一段长文本" + "测试 " * 100,
                "[链接](https://example.com) ~~删除线~~",
            ]
            
            results = {}
            
            # 测试Discord转换
            iterations = 10000
            start = time.time()
            for _ in range(iterations):
                for text in test_texts:
                    formatter.kmarkdown_to_discord(text)
            discord_time = time.time() - start
            discord_ops = (iterations * len(test_texts)) / discord_time
            results["discord_ops_per_sec"] = round(discord_ops, 2)
            
            # 测试Telegram转换
            start = time.time()
            for _ in range(iterations):
                for text in test_texts:
                    formatter.kmarkdown_to_telegram_html(text)
            telegram_time = time.time() - start
            telegram_ops = (iterations * len(test_texts)) / telegram_time
            results["telegram_ops_per_sec"] = round(telegram_ops, 2)
            
            # 测试消息分段
            long_text = "测试消息 " * 1000  # ~5000字符
            start = time.time()
            for _ in range(1000):
                formatter.split_long_message(long_text, 2000)
            split_time = time.time() - start
            split_ops = 1000 / split_time
            results["split_ops_per_sec"] = round(split_ops, 2)
            
            ColorPrinter.success(f"Discord转换: {results['discord_ops_per_sec']} ops/s")
            ColorPrinter.success(f"Telegram转换: {results['telegram_ops_per_sec']} ops/s")
            ColorPrinter.success(f"消息分段: {results['split_ops_per_sec']} ops/s")
            
            self.results["formatter"] = results
            
        except Exception as e:
            ColorPrinter.error(f"格式转换测试失败: {e}")
            self.results["formatter"] = {"error": str(e)}
    
    async def test_rate_limiter(self):
        """测试2: 限流器"""
        ColorPrinter.header("测试2: 限流器精确度测试")
        
        try:
            from app.utils.rate_limiter import RateLimiter
            
            test_configs = [
                (5, 5, "Discord限流（5请求/5秒）"),
                (30, 1, "Telegram限流（30请求/1秒）"),
                (20, 1, "飞书限流（20请求/1秒）"),
            ]
            
            results = []
            
            for calls, period, name in test_configs:
                ColorPrinter.info(f"测试 {name}")
                
                limiter = RateLimiter(calls=calls, period=period)
                
                # 发送 calls * 2 个请求
                total_requests = calls * 2
                
                start_time = time.time()
                for i in range(total_requests):
                    await limiter.acquire()
                total_time = time.time() - start_time
                
                # 理论时间
                expected_time = period * ((total_requests / calls) - 1)
                accuracy = (1 - abs(total_time - expected_time) / expected_time) * 100 if expected_time > 0 else 100
                
                result = {
                    "name": name,
                    "actual_time": round(total_time, 2),
                    "expected_time": round(expected_time, 2),
                    "accuracy": round(accuracy, 2),
                }
                results.append(result)
                
                ColorPrinter.success(f"准确度: {accuracy:.2f}% (实际: {total_time:.2f}s, 预期: {expected_time:.2f}s)")
            
            self.results["rate_limiter"] = results
            
        except Exception as e:
            ColorPrinter.error(f"限流器测试失败: {e}")
            self.results["rate_limiter"] = {"error": str(e)}
    
    async def test_image_processor(self):
        """测试3: 图片处理器"""
        ColorPrinter.header("测试3: 图片处理性能测试")
        
        try:
            from PIL import Image
            
            test_sizes = [
                (800, 600, "小图"),
                (1920, 1080, "中图"),
                (3840, 2160, "4K图"),
            ]
            
            results = []
            
            for width, height, name in test_sizes:
                ColorPrinter.info(f"测试 {name} ({width}x{height})")
                
                # 生成测试图片
                img = Image.new('RGB', (width, height), color=(255, 0, 0))
                
                # 测试JPEG压缩
                start = time.time()
                img_bytes = BytesIO()
                img.save(img_bytes, format='JPEG', quality=85, optimize=True)
                jpeg_time = time.time() - start
                jpeg_size_kb = len(img_bytes.getvalue()) / 1024
                
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
                    "jpeg_time_s": round(jpeg_time, 3),
                    "jpeg_size_kb": round(jpeg_size_kb, 2),
                    "png_time_s": round(png_time, 3),
                    "png_size_kb": round(png_size_kb, 2),
                    "resize_time_s": round(resize_time, 3),
                }
                results.append(result)
                
                ColorPrinter.success(f"JPEG: {jpeg_time:.3f}s ({jpeg_size_kb:.2f}KB)")
                ColorPrinter.success(f"PNG: {png_time:.3f}s ({png_size_kb:.2f}KB)")
                ColorPrinter.success(f"缩放: {resize_time:.3f}s/次")
            
            self.results["image_processor"] = results
            
        except Exception as e:
            ColorPrinter.error(f"图片处理测试失败: {e}")
            self.results["image_processor"] = {"error": str(e)}
    
    async def test_message_filter(self):
        """测试4: 消息过滤器"""
        ColorPrinter.header("测试4: 消息过滤器性能测试")
        
        try:
            from app.processors.filter import MessageFilter
            
            filter = MessageFilter()
            
            # 生成测试消息
            test_count = 10000
            test_messages = []
            for i in range(test_count):
                test_messages.append({
                    "message_id": f"test_{i}",
                    "content": random.choice([
                        "这是正常消息",
                        "广告信息",
                        "代练服务",
                        "官方公告",
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
            no_rule_qps = test_count / no_rule_time
            
            # 添加规则
            filter.add_rule("keyword_blacklist", ["广告", "代练", "外挂"])
            
            # 测试有规则过滤
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
            with_rule_qps = test_count / with_rule_time
            
            results = {
                "test_count": test_count,
                "no_rule_qps": round(no_rule_qps, 2),
                "with_rule_qps": round(with_rule_qps, 2),
                "passed": passed,
                "blocked": blocked,
                "block_rate": round((blocked / test_count) * 100, 2),
            }
            
            ColorPrinter.success(f"无规则过滤: {no_rule_qps:.2f} msg/s")
            ColorPrinter.success(f"有规则过滤: {with_rule_qps:.2f} msg/s")
            ColorPrinter.success(f"拦截率: {results['block_rate']}% ({blocked}/{test_count})")
            
            self.results["message_filter"] = results
            
        except Exception as e:
            ColorPrinter.error(f"过滤器测试失败: {e}")
            self.results["message_filter"] = {"error": str(e)}
    
    async def test_database(self):
        """测试5: 数据库操作"""
        ColorPrinter.header("测试5: 数据库性能测试")
        
        db_path = Path(__file__).parent / "backend" / "data" / "kook_forwarder.db"
        
        if not db_path.exists():
            ColorPrinter.warning("数据库文件不存在，跳过测试")
            self.results["database"] = {"status": "skipped"}
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 测试简单查询
            operations = 1000
            start = time.time()
            for _ in range(operations):
                cursor.execute("SELECT COUNT(*) FROM message_logs")
                cursor.fetchone()
            simple_query_time = time.time() - start
            simple_qps = operations / simple_query_time
            
            # 测试插入
            start = time.time()
            cursor.execute("BEGIN TRANSACTION")
            for i in range(100):
                cursor.execute("""
                    INSERT INTO message_logs 
                    (kook_message_id, kook_channel_id, content, message_type, 
                     sender_name, target_platform, target_channel, status, latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"test_{int(time.time())}_{i}",
                    "test_channel",
                    f"测试消息 {i}",
                    "text",
                    "测试用户",
                    "discord",
                    "test",
                    "success",
                    100
                ))
            cursor.execute("COMMIT")
            insert_time = time.time() - start
            insert_qps = 100 / insert_time
            
            # 清理
            cursor.execute("DELETE FROM message_logs WHERE kook_channel_id = 'test_channel'")
            conn.commit()
            conn.close()
            
            results = {
                "simple_query_qps": round(simple_qps, 2),
                "insert_qps": round(insert_qps, 2),
            }
            
            ColorPrinter.success(f"简单查询: {simple_qps:.2f} qps")
            ColorPrinter.success(f"批量插入: {insert_qps:.2f} qps")
            
            self.results["database"] = results
            
        except Exception as e:
            ColorPrinter.error(f"数据库测试失败: {e}")
            self.results["database"] = {"error": str(e)}
    
    async def test_redis_queue(self):
        """测试6: Redis队列"""
        ColorPrinter.header("测试6: Redis队列性能测试")
        
        try:
            import redis.asyncio as aioredis
            
            try:
                redis_client = await aioredis.from_url(
                    "redis://127.0.0.1:6379",
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                
                await redis_client.ping()
                ColorPrinter.success("Redis连接成功")
                
            except Exception as e:
                ColorPrinter.warning(f"Redis未运行，跳过测试: {e}")
                self.results["redis_queue"] = {"status": "skipped"}
                return
            
            test_queue = f"stress_test_{int(time.time())}"
            
            # 测试单条操作
            batch_size = 1000
            messages = [
                json.dumps({"id": i, "content": f"消息{i}", "data": "x" * 100})
                for i in range(batch_size)
            ]
            
            # 入队
            start = time.time()
            for msg in messages:
                await redis_client.rpush(test_queue, msg)
            enqueue_time = time.time() - start
            enqueue_qps = batch_size / enqueue_time
            
            # 出队
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
            
            await redis_client.delete(test_queue)
            await redis_client.close()
            
            results = {
                "batch_size": batch_size,
                "enqueue_qps": round(enqueue_qps, 2),
                "dequeue_qps": round(dequeue_qps, 2),
                "batch_qps": round(batch_qps, 2),
            }
            
            ColorPrinter.success(f"单条入队: {enqueue_qps:.2f} msg/s")
            ColorPrinter.success(f"单条出队: {dequeue_qps:.2f} msg/s")
            ColorPrinter.success(f"批量入队: {batch_qps:.2f} msg/s")
            
            self.results["redis_queue"] = results
            
        except Exception as e:
            ColorPrinter.error(f"Redis队列测试失败: {e}")
            self.results["redis_queue"] = {"error": str(e)}
    
    def generate_report(self):
        """生成测试报告"""
        ColorPrinter.header("测试总结")
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"测试时长: {duration:.2f}秒")
        print(f"完成测试: {len(self.results)}个模块\n")
        
        # 保存JSON报告
        report_dir = Path(__file__).parent / "test_results"
        report_dir.mkdir(exist_ok=True)
        
        report_data = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": round(duration, 2),
            "results": self.results
        }
        
        json_path = report_dir / "module_stress_test_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        ColorPrinter.success(f"JSON报告已保存: {json_path}")
        
        # 生成Markdown报告
        md_path = report_dir / "模块压力测试报告.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# KOOK消息转发系统 - 模块压力测试报告\n\n")
            f.write(f"**测试时间**: {self.start_time}\n")
            f.write(f"**测试时长**: {duration:.2f}秒\n\n")
            f.write("---\n\n")
            
            for test_name, test_data in self.results.items():
                f.write(f"## {test_name}\n\n")
                
                if isinstance(test_data, dict) and "error" not in test_data:
                    for key, value in test_data.items():
                        if isinstance(value, (list, dict)):
                            f.write(f"**{key}**:\n```json\n{json.dumps(value, indent=2, ensure_ascii=False)}\n```\n\n")
                        else:
                            f.write(f"- **{key}**: {value}\n")
                elif isinstance(test_data, list):
                    for item in test_data:
                        for key, value in item.items():
                            f.write(f"- **{key}**: {value}\n")
                        f.write("\n")
                else:
                    f.write(f"```\n{test_data}\n```\n")
                f.write("\n")
            
            f.write("---\n\n")
            f.write(f"**报告生成时间**: {datetime.now()}\n")
        
        ColorPrinter.success(f"Markdown报告已保存: {md_path}")
        
        ColorPrinter.success("\n✅ 所有测试完成！")


async def main():
    """主函数"""
    tester = ModuleStressTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
