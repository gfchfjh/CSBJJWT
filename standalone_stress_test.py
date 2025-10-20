"""
KOOK消息转发系统 - 独立压力测试
不依赖后端服务，直接测试核心模块
"""
import asyncio
import time
import random
import json
import sys
import sqlite3
import statistics
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 测试结果
test_results = {
    "start_time": datetime.now().isoformat(),
    "tests": {},
    "summary": {}
}


class StandaloneStressTest:
    """独立压力测试"""
    
    def __init__(self):
        self.backend_path = Path(__file__).parent / "backend"
        self.test_count = 0
        self.success_count = 0
        self.fail_count = 0
    
    def print_header(self, title: str):
        """打印测试标题"""
        print("\n" + "=" * 100)
        print(title)
        print("=" * 100)
    
    def print_result(self, name: str, success: bool, time_ms: float = 0, extra: str = ""):
        """打印测试结果"""
        self.test_count += 1
        if success:
            self.success_count += 1
            status = "✅"
        else:
            self.fail_count += 1
            status = "❌"
        
        time_str = f"{time_ms:.2f}ms" if time_ms > 0 else ""
        extra_str = f" - {extra}" if extra else ""
        print(f"  {status} {name:50s} {time_str:>12s}{extra_str}")
    
    # ==================== 测试1: 数据库性能测试 ====================
    
    def test_database_performance(self) -> Dict[str, Any]:
        """测试1: 数据库性能压力测试"""
        self.print_header("测试1: 数据库性能压力测试")
        
        db_path = self.backend_path / "data" / "kook_forwarder.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建测试数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建表
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
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON message_logs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON message_logs(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel ON message_logs(kook_channel_id)")
        
        conn.commit()
        
        results = {}
        
        # 子测试1: 高频简单查询
        print("\n1.1 高频简单查询测试")
        iterations = 10000
        start = time.time()
        for _ in range(iterations):
            cursor.execute("SELECT COUNT(*) FROM message_logs")
            cursor.fetchone()
        elapsed = time.time() - start
        qps = iterations / elapsed
        self.print_result(f"执行{iterations:,}次COUNT查询", True, elapsed * 1000, f"QPS: {qps:.0f}")
        results["simple_query"] = {"iterations": iterations, "time_sec": elapsed, "qps": qps}
        
        # 子测试2: 批量插入（小批次）
        print("\n1.2 批量插入测试（小批次）")
        batch_size = 1000
        start = time.time()
        cursor.execute("BEGIN TRANSACTION")
        for i in range(batch_size):
            cursor.execute("""
                INSERT OR IGNORE INTO message_logs 
                (kook_message_id, kook_channel_id, content, message_type, sender_name, 
                 target_platform, target_channel, status, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"test_small_{int(time.time()*1000000)}_{i}",
                f"channel_{i%10}",
                f"测试消息 {i}",
                "text",
                "测试用户",
                random.choice(["discord", "telegram", "feishu"]),
                "test_target",
                random.choice(["success", "failed", "pending"]),
                random.randint(50, 500)
            ))
        cursor.execute("COMMIT")
        elapsed = time.time() - start
        qps = batch_size / elapsed
        self.print_result(f"插入{batch_size:,}条记录", True, elapsed * 1000, f"QPS: {qps:.0f}")
        results["small_batch_insert"] = {"count": batch_size, "time_sec": elapsed, "qps": qps}
        
        # 子测试3: 大批量插入
        print("\n1.3 大批量插入测试")
        batch_size = 50000
        start = time.time()
        cursor.execute("BEGIN TRANSACTION")
        for i in range(batch_size):
            cursor.execute("""
                INSERT OR IGNORE INTO message_logs 
                (kook_message_id, kook_channel_id, content, message_type, sender_name, 
                 target_platform, target_channel, status, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"test_large_{int(time.time()*1000000)}_{i}",
                f"channel_{i%100}",
                f"大批量测试消息 {i}" * 5,  # 稍微长一点的内容
                "text",
                f"用户{i%1000}",
                random.choice(["discord", "telegram", "feishu"]),
                f"target_{i%50}",
                random.choice(["success", "failed"]),
                random.randint(50, 2000)
            ))
            
            if i % 10000 == 0 and i > 0:
                print(f"    已插入 {i:,} / {batch_size:,} 条...")
        
        cursor.execute("COMMIT")
        elapsed = time.time() - start
        qps = batch_size / elapsed
        self.print_result(f"插入{batch_size:,}条记录", True, elapsed * 1000, f"QPS: {qps:.0f}")
        results["large_batch_insert"] = {"count": batch_size, "time_sec": elapsed, "qps": qps}
        
        # 子测试4: 复杂查询（带WHERE和ORDER BY）
        print("\n1.4 复杂查询测试")
        iterations = 5000
        start = time.time()
        for i in range(iterations):
            cursor.execute("""
                SELECT * FROM message_logs 
                WHERE status = ? AND kook_channel_id LIKE ?
                ORDER BY created_at DESC 
                LIMIT 20
            """, (random.choice(["success", "failed"]), f"channel_{i%10}%"))
            cursor.fetchall()
        elapsed = time.time() - start
        qps = iterations / elapsed
        self.print_result(f"执行{iterations:,}次复杂查询", True, elapsed * 1000, f"QPS: {qps:.0f}")
        results["complex_query"] = {"iterations": iterations, "time_sec": elapsed, "qps": qps}
        
        # 子测试5: 聚合查询
        print("\n1.5 聚合查询测试")
        iterations = 1000
        start = time.time()
        for _ in range(iterations):
            cursor.execute("""
                SELECT target_platform, COUNT(*) as count, AVG(latency_ms) as avg_latency
                FROM message_logs 
                WHERE status = 'success'
                GROUP BY target_platform
            """)
            cursor.fetchall()
        elapsed = time.time() - start
        qps = iterations / elapsed
        self.print_result(f"执行{iterations:,}次聚合查询", True, elapsed * 1000, f"QPS: {qps:.0f}")
        results["aggregate_query"] = {"iterations": iterations, "time_sec": elapsed, "qps": qps}
        
        # 子测试6: 批量更新
        print("\n1.6 批量更新测试")
        start = time.time()
        cursor.execute("""
            UPDATE message_logs 
            SET status = 'retried', latency_ms = latency_ms + 50
            WHERE status = 'failed' AND kook_channel_id LIKE 'channel_1%'
        """)
        conn.commit()
        elapsed = time.time() - start
        updated = cursor.rowcount
        self.print_result(f"更新{updated:,}条记录", True, elapsed * 1000)
        results["batch_update"] = {"count": updated, "time_sec": elapsed}
        
        # 子测试7: 索引效果测试
        print("\n1.7 索引效果对比测试")
        
        # 有索引的查询
        start = time.time()
        for _ in range(1000):
            cursor.execute("SELECT * FROM message_logs WHERE status = 'success' LIMIT 10")
            cursor.fetchall()
        with_index_time = time.time() - start
        
        # 删除索引
        cursor.execute("DROP INDEX IF EXISTS idx_status")
        
        # 无索引的查询
        start = time.time()
        for _ in range(1000):
            cursor.execute("SELECT * FROM message_logs WHERE status = 'success' LIMIT 10")
            cursor.fetchall()
        without_index_time = time.time() - start
        
        # 恢复索引
        cursor.execute("CREATE INDEX idx_status ON message_logs(status)")
        
        speedup = without_index_time / with_index_time if with_index_time > 0 else 0
        self.print_result(f"索引加速比", True, 0, f"{speedup:.2f}x (有索引: {with_index_time*1000:.0f}ms, 无索引: {without_index_time*1000:.0f}ms)")
        results["index_effect"] = {
            "with_index_ms": with_index_time * 1000,
            "without_index_ms": without_index_time * 1000,
            "speedup": speedup
        }
        
        # 数据库统计
        print("\n1.8 数据库统计信息")
        cursor.execute("SELECT COUNT(*) FROM message_logs")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]
        
        self.print_result(f"总记录数", True, 0, f"{total_records:,} 条")
        self.print_result(f"数据库大小", True, 0, f"{db_size/1024/1024:.2f} MB")
        
        results["statistics"] = {
            "total_records": total_records,
            "db_size_mb": db_size / 1024 / 1024
        }
        
        conn.close()
        
        return {
            "test_name": "数据库性能压力测试",
            "status": "success",
            "results": results
        }
    
    # ==================== 测试2: 消息格式转换性能 ====================
    
    def test_message_formatter(self) -> Dict[str, Any]:
        """测试2: 消息格式转换性能"""
        self.print_header("测试2: 消息格式转换性能测试")
        
        try:
            from app.processors.formatter import (
                kmarkdown_to_discord,
                kmarkdown_to_telegram_html,
                kmarkdown_to_feishu
            )
        except ImportError as e:
            self.print_result("导入格式转换模块", False, 0, str(e))
            return {"status": "skipped", "error": str(e)}
        
        # 准备测试文本
        test_texts = {
            "simple": "这是一条简单的消息",
            "formatted": "**粗体** *斜体* `代码` (emj)开心(emj)",
            "complex": """
**重要通知**
这是一条包含多种格式的复杂消息：
- *斜体文本*
- `代码块`
- (emj)笑(emj) (emj)爱心(emj)
- @用户名 @全体成员
- http://example.com/link

> 引用内容
            """,
            "large": ("测试消息内容 " * 1000),
        }
        
        results = {}
        
        for text_type, text in test_texts.items():
            print(f"\n2.{len(results)+1} {text_type.upper()} 文本测试 (长度: {len(text)} 字符)")
            
            # Discord转换
            iterations = 10000 if len(text) < 1000 else 1000
            start = time.time()
            for _ in range(iterations):
                kmarkdown_to_discord(text)
            discord_time = time.time() - start
            discord_ops = iterations / discord_time
            self.print_result(f"Discord转换 ({iterations:,}次)", True, discord_time * 1000, f"{discord_ops:.0f} ops/s")
            
            # Telegram转换
            start = time.time()
            for _ in range(iterations):
                kmarkdown_to_telegram_html(text)
            telegram_time = time.time() - start
            telegram_ops = iterations / telegram_time
            self.print_result(f"Telegram转换 ({iterations:,}次)", True, telegram_time * 1000, f"{telegram_ops:.0f} ops/s")
            
            # 飞书转换
            start = time.time()
            for _ in range(iterations):
                kmarkdown_to_feishu(text)
            feishu_time = time.time() - start
            feishu_ops = iterations / feishu_time
            self.print_result(f"飞书转换 ({iterations:,}次)", True, feishu_time * 1000, f"{feishu_ops:.0f} ops/s")
            
            results[text_type] = {
                "text_length": len(text),
                "iterations": iterations,
                "discord": {"time_sec": discord_time, "ops_per_sec": discord_ops},
                "telegram": {"time_sec": telegram_time, "ops_per_sec": telegram_ops},
                "feishu": {"time_sec": feishu_time, "ops_per_sec": feishu_ops}
            }
        
        return {
            "test_name": "消息格式转换性能测试",
            "status": "success",
            "results": results
        }
    
    # ==================== 测试3: 限流器性能 ====================
    
    async def test_rate_limiter(self) -> Dict[str, Any]:
        """测试3: 限流器性能测试"""
        self.print_header("测试3: 限流器性能测试")
        
        try:
            from app.utils.rate_limiter import RateLimiter
        except ImportError as e:
            self.print_result("导入限流器模块", False, 0, str(e))
            return {"status": "skipped", "error": str(e)}
        
        results = []
        
        configs = [
            (5, 5, "Discord (5请求/5秒)"),
            (30, 1, "Telegram (30请求/1秒)"),
            (20, 1, "飞书 (20请求/1秒)"),
            (100, 1, "高负载 (100请求/1秒)"),
        ]
        
        test_num = 1
        for calls, period, name in configs:
            print(f"\n3.{test_num} {name}")
            limiter = RateLimiter(calls=calls, period=period)
            
            # 发送calls*2个请求
            test_requests = calls * 2
            start = time.time()
            
            for _ in range(test_requests):
                await limiter.acquire()
            
            elapsed = time.time() - start
            actual_qps = test_requests / elapsed
            expected_qps = calls / period
            accuracy = abs(actual_qps - expected_qps) / expected_qps
            
            self.print_result(
                f"限流测试 ({test_requests}个请求)",
                accuracy < 0.15,  # 误差<15%
                elapsed * 1000,
                f"实际QPS: {actual_qps:.1f}, 期望QPS: {expected_qps:.1f}, 误差: {accuracy*100:.1f}%"
            )
            
            results.append({
                "name": name,
                "calls": calls,
                "period": period,
                "test_requests": test_requests,
                "elapsed_sec": elapsed,
                "actual_qps": actual_qps,
                "expected_qps": expected_qps,
                "accuracy": 1 - accuracy
            })
            
            test_num += 1
        
        return {
            "test_name": "限流器性能测试",
            "status": "success",
            "results": results
        }
    
    # ==================== 测试4: 加密性能 ====================
    
    def test_crypto_performance(self) -> Dict[str, Any]:
        """测试4: 加密解密性能测试"""
        self.print_header("测试4: 加密解密性能测试")
        
        try:
            from app.utils.crypto import encrypt_data, decrypt_data
        except ImportError as e:
            self.print_result("导入加密模块", False, 0, str(e))
            return {"status": "skipped", "error": str(e)}
        
        results = {}
        
        # 测试不同长度的数据
        test_data_sizes = [
            (10, "短文本(10字节)"),
            (100, "中文本(100字节)"),
            (1000, "长文本(1KB)"),
            (10000, "超长文本(10KB)"),
        ]
        
        test_num = 1
        for size, name in test_data_sizes:
            print(f"\n4.{test_num} {name}")
            data = "x" * size
            
            # 加密测试
            iterations = 5000 if size < 1000 else 1000
            start = time.time()
            encrypted_data = None
            for _ in range(iterations):
                encrypted_data = encrypt_data(data)
            encrypt_time = time.time() - start
            encrypt_ops = iterations / encrypt_time
            
            self.print_result(f"加密 ({iterations:,}次)", True, encrypt_time * 1000, f"{encrypt_ops:.0f} ops/s")
            
            # 解密测试
            start = time.time()
            for _ in range(iterations):
                decrypt_data(encrypted_data)
            decrypt_time = time.time() - start
            decrypt_ops = iterations / decrypt_time
            
            self.print_result(f"解密 ({iterations:,}次)", True, decrypt_time * 1000, f"{decrypt_ops:.0f} ops/s")
            
            results[name] = {
                "data_size_bytes": size,
                "iterations": iterations,
                "encrypt": {"time_sec": encrypt_time, "ops_per_sec": encrypt_ops},
                "decrypt": {"time_sec": decrypt_time, "ops_per_sec": decrypt_ops}
            }
            
            test_num += 1
        
        return {
            "test_name": "加密解密性能测试",
            "status": "success",
            "results": results
        }
    
    # ==================== 测试5: 消息验证性能 ====================
    
    def test_message_validator(self) -> Dict[str, Any]:
        """测试5: 消息验证性能测试"""
        self.print_header("测试5: 消息验证性能测试")
        
        try:
            from app.processors.message_validator import MessageValidator
        except ImportError as e:
            self.print_result("导入消息验证模块", False, 0, str(e))
            return {"status": "skipped", "error": str(e)}
        
        validator = MessageValidator()
        
        # 测试消息
        valid_messages = [
            {"id": "123", "type": "text", "content": "测试消息"},
            {"id": "456", "type": "image", "content": "http://example.com/image.jpg"},
        ]
        
        invalid_messages = [
            {},  # 缺少字段
            {"id": "", "type": "text", "content": ""},  # 空值
            {"id": "789", "type": "invalid_type", "content": "test"},  # 无效类型
        ]
        
        results = {}
        
        # 测试有效消息验证
        print("\n5.1 有效消息验证")
        iterations = 50000
        start = time.time()
        for _ in range(iterations):
            for msg in valid_messages:
                validator.validate(msg)
        elapsed = time.time() - start
        ops = iterations * len(valid_messages) / elapsed
        self.print_result(f"验证{iterations * len(valid_messages):,}条有效消息", True, elapsed * 1000, f"{ops:.0f} ops/s")
        
        results["valid_messages"] = {
            "count": iterations * len(valid_messages),
            "time_sec": elapsed,
            "ops_per_sec": ops
        }
        
        # 测试无效消息验证
        print("\n5.2 无效消息验证")
        iterations = 50000
        start = time.time()
        for _ in range(iterations):
            for msg in invalid_messages:
                try:
                    validator.validate(msg)
                except:
                    pass
        elapsed = time.time() - start
        ops = iterations * len(invalid_messages) / elapsed
        self.print_result(f"验证{iterations * len(invalid_messages):,}条无效消息", True, elapsed * 1000, f"{ops:.0f} ops/s")
        
        results["invalid_messages"] = {
            "count": iterations * len(invalid_messages),
            "time_sec": elapsed,
            "ops_per_sec": ops
        }
        
        return {
            "test_name": "消息验证性能测试",
            "status": "success",
            "results": results
        }
    
    # ==================== 主测试流程 ====================
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 100)
        print("KOOK消息转发系统 - 独立压力测试")
        print("=" * 100)
        print(f"开始时间: {test_results['start_time']}")
        print(f"Python版本: {sys.version.split()[0]}")
        print("=" * 100)
        
        # 测试1: 数据库性能
        test_results["tests"]["database"] = self.test_database_performance()
        
        # 测试2: 消息格式转换
        test_results["tests"]["formatter"] = self.test_message_formatter()
        
        # 测试3: 限流器
        test_results["tests"]["rate_limiter"] = await self.test_rate_limiter()
        
        # 测试4: 加密性能
        test_results["tests"]["crypto"] = self.test_crypto_performance()
        
        # 测试5: 消息验证
        test_results["tests"]["validator"] = self.test_message_validator()
        
        # 生成总结
        self.generate_summary()
    
    def generate_summary(self):
        """生成测试总结"""
        self.print_header("测试总结")
        
        print(f"\n总测试项: {self.test_count}")
        print(f"成功: {self.success_count} ({self.success_count/self.test_count*100:.1f}%)")
        print(f"失败: {self.fail_count} ({self.fail_count/self.test_count*100:.1f}%)")
        
        test_results["summary"] = {
            "total_tests": self.test_count,
            "success_count": self.success_count,
            "fail_count": self.fail_count,
            "success_rate": self.success_count / self.test_count if self.test_count > 0 else 0
        }


async def main():
    """主函数"""
    tester = StandaloneStressTest()
    await tester.run_all_tests()
    
    # 保存结果
    test_results["end_time"] = datetime.now().isoformat()
    
    report_path = Path(__file__).parent / "standalone_stress_test_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n✅ 测试完成! 报告已保存至: {report_path}")
    
    # 生成Markdown报告
    generate_markdown_report()


def generate_markdown_report():
    """生成Markdown报告"""
    report_path = Path(__file__).parent / "独立压力测试报告.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# KOOK消息转发系统 - 独立压力测试报告\n\n")
        f.write(f"**开始时间**: {test_results['start_time']}\n\n")
        f.write(f"**结束时间**: {test_results['end_time']}\n\n")
        f.write("---\n\n")
        
        # 测试总结
        if "summary" in test_results:
            s = test_results["summary"]
            f.write("## 📊 测试总结\n\n")
            f.write(f"- **总测试项**: {s['total_tests']}\n")
            f.write(f"- **成功**: {s['success_count']} ({s['success_rate']*100:.1f}%)\n")
            f.write(f"- **失败**: {s['fail_count']}\n\n")
        
        f.write("---\n\n")
        
        # 详细结果
        for test_key, test_data in test_results["tests"].items():
            f.write(f"## {test_data.get('test_name', test_key)}\n\n")
            
            if test_data.get("status") == "skipped":
                f.write(f"⚠️ **跳过**: {test_data.get('error', 'Unknown')}\n\n")
                continue
            
            f.write(f"✅ **状态**: 成功\n\n")
            
            if "results" in test_data:
                f.write("### 详细结果\n\n")
                f.write("```json\n")
                f.write(json.dumps(test_data["results"], indent=2, ensure_ascii=False))
                f.write("\n```\n\n")
        
        f.write("---\n\n")
        f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    print(f"✅ Markdown报告已保存至: {report_path}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        sys.exit(1)
