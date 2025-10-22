#!/usr/bin/env python3
"""
KOOK消息转发系统 - 独立压力测试
完全独立，无需任何依赖
"""

import time
import json
import re
import asyncio
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import deque


# ============ 模拟核心功能模块 ============

class MessageFormatter:
    """消息格式转换器（独立版本）"""
    
    EMOJI_MAP = {
        "开心": "😊", "笑": "😄", "大笑": "😆", "哈哈": "😂",
        "哭": "😭", "伤心": "😞", "生气": "😠", "爱心": "❤️",
        "赞": "👍", "火": "🔥", "星星": "⭐", "钱": "💰"
    }
    
    @staticmethod
    def kmarkdown_to_discord(text: str) -> str:
        """KMarkdown转Discord Markdown"""
        if not text:
            return ""
        
        # 转换表情
        text = re.sub(
            r'\(emj\)(\w+)\(emj\)',
            lambda m: MessageFormatter.EMOJI_MAP.get(m.group(1), f":{m.group(1)}:"),
            text
        )
        
        return text
    
    @staticmethod
    def kmarkdown_to_telegram_html(text: str) -> str:
        """KMarkdown转Telegram HTML"""
        if not text:
            return ""
        
        # 转换表情
        text = re.sub(
            r'\(emj\)(\w+)\(emj\)',
            lambda m: MessageFormatter.EMOJI_MAP.get(m.group(1), f":{m.group(1)}:"),
            text
        )
        
        # 转换格式
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        
        return text
    
    @staticmethod
    def split_long_message(text: str, max_length: int) -> list:
        """智能分割超长消息"""
        if len(text) <= max_length:
            return [text]
        
        messages = []
        current = ""
        
        for char in text:
            if len(current) + 1 <= max_length:
                current += char
            else:
                messages.append(current)
                current = char
        
        if current:
            messages.append(current)
        
        return messages


class RateLimiter:
    """限流器（独立版本）"""
    
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.timestamps = deque()
    
    async def acquire(self):
        """获取许可"""
        now = time.time()
        
        # 清理过期时间戳
        while self.timestamps and self.timestamps[0] < now - self.period:
            self.timestamps.popleft()
        
        if len(self.timestamps) >= self.calls:
            # 需要等待
            sleep_time = self.period - (now - self.timestamps[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            return await self.acquire()
        
        self.timestamps.append(now)


# ============ 压力测试类 ============

class StandaloneStressTest:
    """独立压力测试"""
    
    def __init__(self):
        self.formatter = MessageFormatter()
        self.results = {
            "test_time": datetime.now().isoformat(),
            "test_type": "独立压力测试",
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "performance_metrics": {}
        }
    
    def print_header(self, title: str):
        """打印标题"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def print_result(self, name: str, value: float, unit: str = ""):
        """打印结果"""
        print(f"  ✓ {name}: {value:,.2f} {unit}")
    
    # ========== 测试1: 消息格式转换 ==========
    
    def test_message_formatting(self):
        """测试消息格式转换"""
        self.print_header("测试1: 消息格式转换性能")
        
        test_texts = [
            "**粗体** *斜体* `代码`",
            "(emj)开心(emj) (emj)笑(emj) @用户名",
            "这是一段很长的文本，用于测试性能。" * 10,
            "~~删除线~~ [链接](https://example.com)",
        ]
        
        metrics = []
        
        # Discord转换
        for iterations in [1000, 5000, 10000, 50000, 100000]:
            start = time.time()
            for _ in range(iterations):
                for text in test_texts:
                    self.formatter.kmarkdown_to_discord(text)
            elapsed = time.time() - start
            ops_per_sec = (iterations * len(test_texts)) / elapsed
            
            metrics.append({
                "test": f"Discord格式转换({iterations}次)",
                "ops_per_second": ops_per_sec,
                "elapsed": elapsed
            })
            
            print(f"ℹ️  Discord格式转换 ({iterations:,}次)")
            self.print_result("性能", ops_per_sec, "ops/s")
            self.print_result("耗时", elapsed, "秒")
            
            self.results["total_tests"] += 1
            if ops_per_sec > 10000:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        # Telegram转换
        for iterations in [10000, 50000]:
            start = time.time()
            for _ in range(iterations):
                for text in test_texts:
                    self.formatter.kmarkdown_to_telegram_html(text)
            elapsed = time.time() - start
            ops_per_sec = (iterations * len(test_texts)) / elapsed
            
            metrics.append({
                "test": f"Telegram格式转换({iterations}次)",
                "ops_per_second": ops_per_sec,
                "elapsed": elapsed
            })
            
            print(f"ℹ️  Telegram格式转换 ({iterations:,}次)")
            self.print_result("性能", ops_per_sec, "ops/s")
            
            self.results["total_tests"] += 1
            if ops_per_sec > 8000:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        # 消息分段
        long_text = "这是一段很长的文本。" * 200
        iterations = 10000
        start = time.time()
        for _ in range(iterations):
            self.formatter.split_long_message(long_text, 2000)
        elapsed = time.time() - start
        ops_per_sec = iterations / elapsed
        
        metrics.append({
            "test": f"消息智能分段({iterations}次)",
            "ops_per_second": ops_per_sec,
            "elapsed": elapsed
        })
        
        print(f"ℹ️  消息智能分段 ({iterations:,}次)")
        self.print_result("性能", ops_per_sec, "ops/s")
        
        self.results["total_tests"] += 1
        if ops_per_sec > 1000:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
        
        self.results["performance_metrics"]["message_formatting"] = metrics
        print("✅ 消息格式转换测试完成\n")
    
    # ========== 测试2: 限流器 ==========
    
    async def test_rate_limiter(self):
        """测试限流器"""
        self.print_header("测试2: 限流器准确性")
        
        test_configs = [
            {"calls": 5, "period": 1, "name": "Discord限流(5/1s)"},
            {"calls": 30, "period": 1, "name": "Telegram限流(30/1s)"},
            {"calls": 20, "period": 1, "name": "飞书限流(20/1s)"},
            {"calls": 100, "period": 5, "name": "自定义限流(100/5s)"},
        ]
        
        metrics = []
        
        for config in test_configs:
            limiter = RateLimiter(config["calls"], config["period"])
            
            start = time.time()
            for _ in range(config["calls"]):
                await limiter.acquire()
            elapsed = time.time() - start
            
            accuracy = min(100, (config["period"] / elapsed) * 100)
            
            metrics.append({
                "test": config["name"],
                "expected": config["period"],
                "actual": elapsed,
                "accuracy": accuracy
            })
            
            print(f"ℹ️  {config['name']}")
            print(f"  ✓ 预期: {config['period']:.2f}s, 实际: {elapsed:.2f}s")
            self.print_result("准确度", accuracy, "%")
            
            self.results["total_tests"] += 1
            if accuracy > 95:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        self.results["performance_metrics"]["rate_limiter"] = metrics
        print("✅ 限流器测试完成\n")
    
    # ========== 测试3: 并发处理 ==========
    
    async def test_concurrent_processing(self):
        """测试并发处理"""
        self.print_header("测试3: 并发处理能力")
        
        async def process_message(msg_id: int) -> bool:
            """模拟消息处理"""
            text = f"**消息{msg_id}** 内容测试 (emj)开心(emj)"
            self.formatter.kmarkdown_to_discord(text)
            await asyncio.sleep(0.001)  # 模拟I/O
            return True
        
        metrics = []
        
        for level in [10, 50, 100, 200, 500, 1000]:
            start = time.time()
            tasks = [process_message(i) for i in range(level)]
            results = await asyncio.gather(*tasks)
            elapsed = time.time() - start
            
            throughput = level / elapsed
            success_rate = (sum(results) / len(results)) * 100
            
            metrics.append({
                "concurrent_level": level,
                "throughput": throughput,
                "elapsed": elapsed,
                "success_rate": success_rate
            })
            
            print(f"ℹ️  并发级别: {level}")
            self.print_result("吞吐量", throughput, "msg/s")
            self.print_result("成功率", success_rate, "%")
            
            self.results["total_tests"] += 1
            if throughput > 50:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        self.results["performance_metrics"]["concurrent_processing"] = metrics
        print("✅ 并发处理测试完成\n")
    
    # ========== 测试4: 队列性能 ==========
    
    def test_queue_performance(self):
        """测试队列性能"""
        self.print_header("测试4: 队列性能")
        
        metrics = []
        
        for batch_size in [100, 500, 1000, 5000, 10000, 50000]:
            # 入队
            queue = deque()
            messages = [{"id": i, "content": f"消息{i}"} for i in range(batch_size)]
            
            start = time.time()
            for msg in messages:
                queue.append(json.dumps(msg))
            elapsed = time.time() - start
            enqueue_qps = batch_size / elapsed if elapsed > 0 else 0
            
            # 出队
            start = time.time()
            while queue:
                msg = queue.popleft()
                json.loads(msg)
            elapsed = time.time() - start
            dequeue_qps = batch_size / elapsed if elapsed > 0 else 0
            
            metrics.append({
                "batch_size": batch_size,
                "enqueue_qps": enqueue_qps,
                "dequeue_qps": dequeue_qps
            })
            
            print(f"ℹ️  批量大小: {batch_size:,}")
            self.print_result("入队QPS", enqueue_qps, "msg/s")
            self.print_result("出队QPS", dequeue_qps, "msg/s")
            
            self.results["total_tests"] += 1
            if enqueue_qps > 10000 and dequeue_qps > 10000:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        self.results["performance_metrics"]["queue_performance"] = metrics
        print("✅ 队列性能测试完成\n")
    
    # ========== 测试5: JSON序列化 ==========
    
    def test_json_serialization(self):
        """测试JSON序列化"""
        self.print_header("测试5: JSON序列化性能")
        
        test_data = {
            "message_id": "msg_12345",
            "channel_id": "channel_67890",
            "content": "这是一条测试消息 (emj)开心(emj)",
            "sender": "用户A",
            "timestamp": 1698765432,
            "attachments": [
                {"type": "image", "url": "https://example.com/image1.jpg"},
                {"type": "file", "url": "https://example.com/file1.pdf"}
            ]
        }
        
        metrics = []
        
        # 序列化测试
        iterations = 100000
        start = time.time()
        for _ in range(iterations):
            json.dumps(test_data, ensure_ascii=False)
        elapsed = time.time() - start
        serialize_qps = iterations / elapsed
        
        # 反序列化测试
        json_str = json.dumps(test_data, ensure_ascii=False)
        start = time.time()
        for _ in range(iterations):
            json.loads(json_str)
        elapsed = time.time() - start
        deserialize_qps = iterations / elapsed
        
        metrics.append({
            "iterations": iterations,
            "serialize_qps": serialize_qps,
            "deserialize_qps": deserialize_qps
        })
        
        print(f"ℹ️  测试次数: {iterations:,}")
        self.print_result("序列化QPS", serialize_qps, "ops/s")
        self.print_result("反序列化QPS", deserialize_qps, "ops/s")
        
        self.results["total_tests"] += 1
        if serialize_qps > 10000 and deserialize_qps > 10000:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
        
        self.results["performance_metrics"]["json_serialization"] = metrics
        print("✅ JSON序列化测试完成\n")
    
    # ========== 主测试函数 ==========
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("  KOOK消息转发系统 - 独立压力测试")
        print("=" * 80)
        print(f"\n测试时间: {self.results['test_time']}")
        print("说明: 完全独立运行，无需任何外部依赖\n")
        
        # 执行所有测试
        self.test_message_formatting()
        await self.test_rate_limiter()
        await self.test_concurrent_processing()
        self.test_queue_performance()
        self.test_json_serialization()
        
        # 打印总结
        self.print_summary()
        
        # 生成报告
        self.generate_report()
    
    def print_summary(self):
        """打印总结"""
        self.print_header("测试总结")
        
        print(f"测试时间: {self.results['test_time']}")
        print(f"总测试数: {self.results['total_tests']}")
        print(f"通过数量: {self.results['passed']}")
        print(f"失败数量: {self.results['failed']}")
        
        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed'] / self.results['total_tests']) * 100
            print(f"成功率: {success_rate:.2f}%")
        
        # 性能亮点
        print("\n" + "=" * 80)
        print("  性能亮点")
        print("=" * 80 + "\n")
        
        # 格式转换最佳性能
        if "message_formatting" in self.results["performance_metrics"]:
            metrics = self.results["performance_metrics"]["message_formatting"]
            max_ops = max(m["ops_per_second"] for m in metrics)
            print(f"✨ 消息格式转换峰值: {max_ops:,.0f} ops/s")
        
        # 队列最佳性能
        if "queue_performance" in self.results["performance_metrics"]:
            metrics = self.results["performance_metrics"]["queue_performance"]
            max_enqueue = max(m["enqueue_qps"] for m in metrics)
            max_dequeue = max(m["dequeue_qps"] for m in metrics)
            print(f"✨ 队列入队峰值: {max_enqueue:,.0f} msg/s")
            print(f"✨ 队列出队峰值: {max_dequeue:,.0f} msg/s")
        
        # 并发最佳性能
        if "concurrent_processing" in self.results["performance_metrics"]:
            metrics = self.results["performance_metrics"]["concurrent_processing"]
            max_throughput = max(m["throughput"] for m in metrics)
            print(f"✨ 并发处理峰值: {max_throughput:,.0f} msg/s")
        
        print()
    
    def generate_report(self):
        """生成报告"""
        # 确保目录存在
        report_dir = Path("test_results")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON报告
        json_path = report_dir / "standalone_stress_test_report.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON报告已保存: {json_path}")
        
        # Markdown报告
        md_path = report_dir / "独立压力测试报告.md"
        self.generate_markdown_report(md_path)
        print(f"✅ Markdown报告已保存: {md_path}")
    
    def generate_markdown_report(self, output_path: Path):
        """生成Markdown报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# KOOK消息转发系统 - 独立压力测试报告\n\n")
            f.write(f"**测试时间**: {self.results['test_time']}  \n")
            f.write(f"**测试类型**: {self.results['test_type']}  \n\n")
            
            f.write("## 📊 测试总结\n\n")
            f.write("| 指标 | 数值 |\n")
            f.write("|------|------|\n")
            f.write(f"| 总测试数 | {self.results['total_tests']} |\n")
            f.write(f"| 通过数量 | {self.results['passed']} |\n")
            f.write(f"| 失败数量 | {self.results['failed']} |\n")
            
            if self.results['total_tests'] > 0:
                success_rate = (self.results['passed'] / self.results['total_tests']) * 100
                f.write(f"| 成功率 | {success_rate:.2f}% |\n")
            
            f.write("\n## 📈 性能指标\n\n")
            
            for category, metrics in self.results["performance_metrics"].items():
                f.write(f"### {category}\n\n")
                
                if metrics:
                    f.write("| 测试项 | 性能指标 |\n")
                    f.write("|--------|----------|\n")
                    
                    for metric in metrics[:5]:  # 只显示前5个
                        metric_str = json.dumps(metric, ensure_ascii=False)
                        f.write(f"| {metric.get('test', category)} | {metric_str} |\n")
                
                f.write("\n")


async def main():
    """主函数"""
    tester = StandaloneStressTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
