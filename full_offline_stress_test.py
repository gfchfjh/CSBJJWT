#!/usr/bin/env python3
"""
KOOK消息转发系统 - 全面离线压力测试
无需后端服务即可测试所有核心功能
"""

import sys
import os
import time
import json
import asyncio
import statistics
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# 添加backend路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 导入核心模块
try:
    from app.processors.formatter import formatter, MessageFormatter
    from app.utils.rate_limiter import RateLimiter
    from app.database import Database
    from app.utils.crypto import crypto_manager
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("💡 提示: 请确保在项目根目录运行此脚本")
    sys.exit(1)


class FullOfflineStressTest:
    """全面离线压力测试"""
    
    def __init__(self):
        self.results = {
            "test_time": datetime.now().isoformat(),
            "test_type": "全面离线压力测试",
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "modules": {}
        }
        
        # 创建测试数据库
        self.test_db_path = Path("test_results/test_stress.db")
        self.test_db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.test_db_path.exists():
            self.test_db_path.unlink()
        
        self.db = Database(self.test_db_path)
    
    def print_header(self, title: str):
        """打印测试标题"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def print_result(self, name: str, value: Any, unit: str = ""):
        """打印测试结果"""
        print(f"  ✓ {name}: {value:,.2f} {unit}")
    
    # ================== 测试1: 消息格式转换 ==================
    
    def test_message_formatting(self) -> Dict[str, Any]:
        """测试消息格式转换性能"""
        self.print_header("测试1: 消息格式转换性能")
        
        results = {
            "module_name": "消息格式转换",
            "tests": []
        }
        
        test_texts = [
            "**粗体** *斜体* `代码`",
            "(emj)开心(emj) (emj)笑(emj) @用户名 [链接](https://example.com)",
            "这是一段很长的文本，用于测试性能。" * 10,
            "~~删除线~~ **加粗** *斜体* `代码块` (emj)火(emj)",
        ]
        
        # Discord格式转换
        iterations = [1000, 5000, 10000, 50000]
        for n in iterations:
            start = time.time()
            for _ in range(n):
                for text in test_texts:
                    formatter.kmarkdown_to_discord(text)
            elapsed = time.time() - start
            ops_per_sec = (n * len(test_texts)) / elapsed
            
            results["tests"].append({
                "name": f"Discord格式转换 ({n}次)",
                "operations": n * len(test_texts),
                "elapsed_seconds": elapsed,
                "ops_per_second": ops_per_sec,
                "status": "PASSED" if ops_per_sec > 10000 else "FAILED"
            })
            
            print(f"ℹ️  Discord格式转换 ({n}次)")
            self.print_result("性能", ops_per_sec, "ops/s")
        
        # Telegram格式转换
        for n in [10000]:
            start = time.time()
            for _ in range(n):
                for text in test_texts:
                    formatter.kmarkdown_to_telegram_html(text)
            elapsed = time.time() - start
            ops_per_sec = (n * len(test_texts)) / elapsed
            
            results["tests"].append({
                "name": f"Telegram格式转换 ({n}次)",
                "operations": n * len(test_texts),
                "elapsed_seconds": elapsed,
                "ops_per_second": ops_per_sec,
                "status": "PASSED" if ops_per_sec > 8000 else "FAILED"
            })
            
            print(f"ℹ️  Telegram格式转换 ({n}次)")
            self.print_result("性能", ops_per_sec, "ops/s")
        
        # 消息分段测试
        long_text = "这是一段很长的文本。" * 200
        start = time.time()
        for _ in range(1000):
            formatter.split_long_message(long_text, 2000)
        elapsed = time.time() - start
        ops_per_sec = 1000 / elapsed
        
        results["tests"].append({
            "name": "消息智能分段 (1000次)",
            "operations": 1000,
            "elapsed_seconds": elapsed,
            "ops_per_second": ops_per_sec,
            "status": "PASSED" if ops_per_sec > 1000 else "FAILED"
        })
        
        print(f"ℹ️  消息智能分段 (1000次)")
        self.print_result("性能", ops_per_sec, "ops/s")
        
        print("✅ 消息格式转换测试完成\n")
        return results
    
    # ================== 测试2: 限流器 ==================
    
    async def test_rate_limiter(self) -> Dict[str, Any]:
        """测试限流器准确性"""
        self.print_header("测试2: 限流器准确性和性能")
        
        results = {
            "module_name": "限流器",
            "tests": []
        }
        
        # 测试配置
        test_configs = [
            {"calls": 5, "period": 1, "name": "Discord限流(5/1秒)"},
            {"calls": 30, "period": 1, "name": "Telegram限流(30/1秒)"},
            {"calls": 20, "period": 1, "name": "飞书限流(20/1秒)"},
            {"calls": 100, "period": 5, "name": "自定义限流(100/5秒)"},
        ]
        
        for config in test_configs:
            limiter = RateLimiter(config["calls"], config["period"])
            
            start = time.time()
            for _ in range(config["calls"]):
                await limiter.acquire()
            elapsed = time.time() - start
            
            accuracy = min(100, (config["period"] / elapsed) * 100)
            
            results["tests"].append({
                "name": config["name"],
                "expected_time": config["period"],
                "actual_time": elapsed,
                "accuracy_percent": accuracy,
                "status": "PASSED" if accuracy > 95 else "FAILED"
            })
            
            print(f"ℹ️  {config['name']}")
            print(f"  ✓ 预期时间: {config['period']:.2f}s")
            print(f"  ✓ 实际时间: {elapsed:.2f}s")
            self.print_result("准确度", accuracy, "%")
        
        print("✅ 限流器测试完成\n")
        return results
    
    # ================== 测试3: 数据库性能 ==================
    
    def test_database_performance(self) -> Dict[str, Any]:
        """测试数据库性能"""
        self.print_header("测试3: 数据库性能")
        
        results = {
            "module_name": "数据库性能",
            "tests": []
        }
        
        # 测试插入性能
        operation_counts = [100, 500, 1000, 5000]
        
        for count in operation_counts:
            # 账号插入
            start = time.time()
            for i in range(count):
                try:
                    self.db.add_account(
                        email=f"test{i}@example.com",
                        cookie=json.dumps({"session": f"token{i}"})
                    )
                except:
                    pass  # 忽略重复错误
            elapsed = time.time() - start
            qps = count / elapsed
            
            results["tests"].append({
                "name": f"账号插入 ({count}条)",
                "operations": count,
                "elapsed_seconds": elapsed,
                "qps": qps,
                "status": "PASSED" if qps > 100 else "FAILED"
            })
            
            print(f"ℹ️  账号插入 ({count}条)")
            self.print_result("QPS", qps, "ops/s")
        
        # 测试查询性能
        for count in [100, 1000, 10000]:
            start = time.time()
            for _ in range(count):
                self.db.get_accounts()
            elapsed = time.time() - start
            qps = count / elapsed
            
            results["tests"].append({
                "name": f"账号查询 ({count}次)",
                "operations": count,
                "elapsed_seconds": elapsed,
                "qps": qps,
                "status": "PASSED" if qps > 500 else "FAILED"
            })
            
            print(f"ℹ️  账号查询 ({count}次)")
            self.print_result("QPS", qps, "ops/s")
        
        # 测试消息日志插入
        for count in [100, 500, 1000]:
            start = time.time()
            for i in range(count):
                self.db.add_message_log(
                    kook_message_id=f"msg_{int(time.time()*1000000)}_{i}",
                    kook_channel_id="channel123",
                    content=f"测试消息{i}",
                    message_type="text",
                    sender_name="测试用户",
                    target_platform="discord",
                    target_channel="channel456",
                    status="success",
                    latency_ms=50
                )
            elapsed = time.time() - start
            qps = count / elapsed
            
            results["tests"].append({
                "name": f"消息日志插入 ({count}条)",
                "operations": count,
                "elapsed_seconds": elapsed,
                "qps": qps,
                "status": "PASSED" if qps > 200 else "FAILED"
            })
            
            print(f"ℹ️  消息日志插入 ({count}条)")
            self.print_result("QPS", qps, "ops/s")
        
        print("✅ 数据库性能测试完成\n")
        return results
    
    # ================== 测试4: 加密解密性能 ==================
    
    def test_crypto_performance(self) -> Dict[str, Any]:
        """测试加密解密性能"""
        self.print_header("测试4: 加密解密性能")
        
        results = {
            "module_name": "加密解密",
            "tests": []
        }
        
        test_data_lengths = [10, 50, 100, 500, 1000]
        
        for length in test_data_lengths:
            test_data = "a" * length
            
            # 加密性能
            start = time.time()
            encrypted_data = []
            for _ in range(1000):
                encrypted = crypto_manager.encrypt(test_data)
                encrypted_data.append(encrypted)
            elapsed = time.time() - start
            encrypt_qps = 1000 / elapsed
            
            # 解密性能
            start = time.time()
            for encrypted in encrypted_data:
                decrypted = crypto_manager.decrypt(encrypted)
                assert decrypted == test_data
            elapsed = time.time() - start
            decrypt_qps = 1000 / elapsed
            
            results["tests"].append({
                "name": f"加密解密 ({length}字节)",
                "data_length": length,
                "encrypt_qps": encrypt_qps,
                "decrypt_qps": decrypt_qps,
                "status": "PASSED" if encrypt_qps > 5000 and decrypt_qps > 5000 else "FAILED"
            })
            
            print(f"ℹ️  数据长度: {length}字节")
            self.print_result("加密QPS", encrypt_qps, "ops/s")
            self.print_result("解密QPS", decrypt_qps, "ops/s")
        
        print("✅ 加密解密测试完成\n")
        return results
    
    # ================== 测试5: 并发处理 ==================
    
    async def test_concurrent_processing(self) -> Dict[str, Any]:
        """测试并发处理能力"""
        self.print_header("测试5: 并发处理能力")
        
        results = {
            "module_name": "并发处理",
            "tests": []
        }
        
        async def process_message(msg_id: int) -> bool:
            """模拟消息处理"""
            # 格式转换
            text = f"**消息{msg_id}** 内容测试"
            formatter.kmarkdown_to_discord(text)
            
            # 小延迟模拟I/O
            await asyncio.sleep(0.001)
            
            return True
        
        concurrent_levels = [10, 50, 100, 200, 500]
        
        for level in concurrent_levels:
            start = time.time()
            
            tasks = [process_message(i) for i in range(level)]
            results_list = await asyncio.gather(*tasks)
            
            elapsed = time.time() - start
            throughput = level / elapsed
            success_rate = (sum(results_list) / len(results_list)) * 100
            
            results["tests"].append({
                "name": f"并发处理 ({level}并发)",
                "concurrent_level": level,
                "elapsed_seconds": elapsed,
                "throughput": throughput,
                "success_rate": success_rate,
                "status": "PASSED" if throughput > 50 else "FAILED"
            })
            
            print(f"ℹ️  并发级别: {level}")
            self.print_result("吞吐量", throughput, "msg/s")
            self.print_result("成功率", success_rate, "%")
        
        print("✅ 并发处理测试完成\n")
        return results
    
    # ================== 测试6: 队列性能 ==================
    
    def test_queue_performance(self) -> Dict[str, Any]:
        """测试队列性能（使用内存队列模拟）"""
        self.print_header("测试6: 队列性能")
        
        results = {
            "module_name": "队列性能",
            "tests": []
        }
        
        from collections import deque
        
        batch_sizes = [100, 500, 1000, 5000, 10000]
        
        for batch_size in batch_sizes:
            # 入队测试
            queue = deque()
            messages = [{"id": i, "content": f"消息{i}"} for i in range(batch_size)]
            
            start = time.time()
            for msg in messages:
                queue.append(json.dumps(msg))
            elapsed = time.time() - start
            enqueue_qps = batch_size / elapsed
            
            # 出队测试
            start = time.time()
            while queue:
                msg = queue.popleft()
                json.loads(msg)
            elapsed = time.time() - start
            dequeue_qps = batch_size / elapsed
            
            results["tests"].append({
                "name": f"队列操作 ({batch_size}条)",
                "batch_size": batch_size,
                "enqueue_qps": enqueue_qps,
                "dequeue_qps": dequeue_qps,
                "status": "PASSED" if enqueue_qps > 10000 and dequeue_qps > 10000 else "FAILED"
            })
            
            print(f"ℹ️  批量大小: {batch_size}")
            self.print_result("入队QPS", enqueue_qps, "msg/s")
            self.print_result("出队QPS", dequeue_qps, "msg/s")
        
        print("✅ 队列性能测试完成\n")
        return results
    
    # ================== 测试7: 表情映射 ==================
    
    def test_emoji_mapping(self) -> Dict[str, Any]:
        """测试表情映射性能"""
        self.print_header("测试7: 表情映射性能")
        
        results = {
            "module_name": "表情映射",
            "tests": []
        }
        
        # 测试文本包含多个表情
        test_text = "(emj)开心(emj) (emj)笑(emj) (emj)哭(emj) (emj)爱心(emj) (emj)赞(emj)"
        
        iterations = [1000, 10000, 50000]
        
        for n in iterations:
            start = time.time()
            for _ in range(n):
                formatter.kmarkdown_to_discord(test_text)
            elapsed = time.time() - start
            ops_per_sec = n / elapsed
            
            results["tests"].append({
                "name": f"表情转换 ({n}次)",
                "operations": n,
                "elapsed_seconds": elapsed,
                "ops_per_second": ops_per_sec,
                "status": "PASSED" if ops_per_sec > 5000 else "FAILED"
            })
            
            print(f"ℹ️  迭代次数: {n}")
            self.print_result("性能", ops_per_sec, "ops/s")
        
        print("✅ 表情映射测试完成\n")
        return results
    
    # ================== 主测试函数 ==================
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("  KOOK消息转发系统 - 全面离线压力测试")
        print("=" * 80)
        print(f"\n测试时间: {self.results['test_time']}")
        print("说明: 无需后端服务即可测试所有核心功能\n")
        
        all_results = []
        
        # 执行所有测试
        all_results.append(self.test_message_formatting())
        all_results.append(await self.test_rate_limiter())
        all_results.append(self.test_database_performance())
        all_results.append(self.test_crypto_performance())
        all_results.append(await self.test_concurrent_processing())
        all_results.append(self.test_queue_performance())
        all_results.append(self.test_emoji_mapping())
        
        # 汇总结果
        for module_result in all_results:
            module_name = module_result["module_name"]
            tests = module_result["tests"]
            
            passed = sum(1 for t in tests if t["status"] == "PASSED")
            failed = sum(1 for t in tests if t["status"] == "FAILED")
            
            self.results["modules"][module_name] = {
                "total": len(tests),
                "passed": passed,
                "failed": failed,
                "tests": tests
            }
            
            self.results["total_tests"] += len(tests)
            self.results["passed"] += passed
            self.results["failed"] += failed
        
        # 打印总结
        self.print_summary()
        
        # 生成报告
        self.generate_report()
    
    def print_summary(self):
        """打印测试总结"""
        self.print_header("测试总结")
        
        print(f"测试时间: {self.results['test_time']}")
        print(f"总测试数: {self.results['total_tests']}")
        print(f"通过数量: {self.results['passed']}")
        print(f"失败数量: {self.results['failed']}")
        
        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed'] / self.results['total_tests']) * 100
            print(f"成功率: {success_rate:.2f}%")
        
        print("\n模块测试结果:")
        for module_name, module_data in self.results["modules"].items():
            status_icon = "✅" if module_data["failed"] == 0 else "⚠️"
            print(f"  {status_icon} {module_name}: {module_data['passed']}/{module_data['total']} 通过")
        
        print()
    
    def generate_report(self):
        """生成测试报告"""
        # JSON报告
        json_path = Path("test_results/full_offline_stress_test_report.json")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON报告已保存: {json_path}")
        
        # Markdown报告
        md_path = Path("test_results/全面离线压力测试报告.md")
        self.generate_markdown_report(md_path)
        print(f"✅ Markdown报告已保存: {md_path}")
    
    def generate_markdown_report(self, output_path: Path):
        """生成Markdown格式报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# KOOK消息转发系统 - 全面离线压力测试报告\n\n")
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
            
            f.write("\n## 📈 详细测试结果\n\n")
            
            for module_name, module_data in self.results["modules"].items():
                f.write(f"### {module_name}\n\n")
                f.write(f"**通过率**: {module_data['passed']}/{module_data['total']}  \n\n")
                
                f.write("| 测试项 | 结果 |\n")
                f.write("|--------|------|\n")
                
                for test in module_data["tests"]:
                    status_icon = "✅" if test["status"] == "PASSED" else "❌"
                    f.write(f"| {test['name']} | {status_icon} |\n")
                
                f.write("\n")


async def main():
    """主函数"""
    tester = FullOfflineStressTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
