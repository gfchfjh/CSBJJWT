"""
KOOK消息转发系统 - 独立压力测试
不需要启动后端服务，直接测试核心模块性能
"""
import asyncio
import time
import json
import sys
import os
import sqlite3
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("=" * 100)
print(" " * 25 + "KOOK消息转发系统 - 独立压力测试")
print("=" * 100)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python版本: {sys.version.split()[0]}")
print(f"CPU核心数: {multiprocessing.cpu_count()}")
print("=" * 100)
print()

test_results = {
    "start_time": datetime.now().isoformat(),
    "tests": {},
    "environment": {
        "python_version": sys.version.split()[0],
        "cpu_cores": multiprocessing.cpu_count()
    }
}


def test_1_message_formatter_performance():
    """测试1: 消息格式转换性能"""
    print("\n" + "=" * 100)
    print("测试1: 消息格式转换性能测试")
    print("=" * 100)
    
    try:
        from app.processors.formatter import (
            kmarkdown_to_discord,
            kmarkdown_to_telegram_html,
            kmarkdown_to_feishu
        )
        
        test_text = """
        **这是粗体文本** *这是斜体文本* `这是代码`
        (emj)开心(emj) (emj)笑(emj) (emj)爱心(emj)
        @用户名 @全体成员 #频道
        http://example.com/test
        这是一段很长的文本，用来测试消息分段功能。""" * 5
        
        results = []
        
        # Discord转换
        print("\n测试Discord格式转换 (10000次)...", end=" ")
        start = time.time()
        for _ in range(10000):
            kmarkdown_to_discord(test_text)
        discord_time = time.time() - start
        print(f"✅ 耗时: {discord_time:.3f}s, 速度: {10000/discord_time:.0f} ops/s")
        
        results.append({
            "format": "Discord",
            "iterations": 10000,
            "time_seconds": round(discord_time, 3),
            "ops_per_second": round(10000 / discord_time, 0)
        })
        
        # Telegram转换
        print("测试Telegram格式转换 (10000次)...", end=" ")
        start = time.time()
        for _ in range(10000):
            kmarkdown_to_telegram_html(test_text)
        telegram_time = time.time() - start
        print(f"✅ 耗时: {telegram_time:.3f}s, 速度: {10000/telegram_time:.0f} ops/s")
        
        results.append({
            "format": "Telegram",
            "iterations": 10000,
            "time_seconds": round(telegram_time, 3),
            "ops_per_second": round(10000 / telegram_time, 0)
        })
        
        # 飞书转换
        print("测试飞书格式转换 (10000次)...", end=" ")
        start = time.time()
        for _ in range(10000):
            kmarkdown_to_feishu(test_text)
        feishu_time = time.time() - start
        print(f"✅ 耗时: {feishu_time:.3f}s, 速度: {10000/feishu_time:.0f} ops/s")
        
        results.append({
            "format": "飞书",
            "iterations": 10000,
            "time_seconds": round(feishu_time, 3),
            "ops_per_second": round(10000 / feishu_time, 0)
        })
        
        return {
            "test_name": "消息格式转换性能测试",
            "status": "success",
            "results": results
        }
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return {"test_name": "消息格式转换性能测试", "status": "failed", "error": str(e)}


def test_2_database_performance():
    """测试2: 数据库性能测试"""
    print("\n" + "=" * 100)
    print("测试2: 数据库性能测试")
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
                kook_message_id TEXT,
                kook_channel_id TEXT,
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
            CREATE INDEX IF NOT EXISTS idx_status ON message_logs(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON message_logs(created_at)
        """)
        
        conn.commit()
        conn.close()
        print("✅ 测试数据库创建完成")
    
    results = []
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 测试1: 批量插入
    print("\n测试批量插入 (10000条)...", end=" ")
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
            random.choice(["discord", "telegram", "feishu"]),
            "test_target",
            random.choice(["success", "failed"]),
            random.randint(50, 500)
        ))
    cursor.execute("COMMIT")
    insert_time = time.time() - start
    print(f"✅ 耗时: {insert_time:.3f}s, 速度: {10000/insert_time:.0f} 条/秒")
    
    results.append({
        "operation": "批量插入",
        "records": 10000,
        "time_seconds": round(insert_time, 3),
        "records_per_second": round(10000 / insert_time, 0)
    })
    
    # 测试2: 索引查询
    print("测试索引查询 (5000次)...", end=" ")
    start = time.time()
    for _ in range(5000):
        cursor.execute("""
            SELECT * FROM message_logs 
            WHERE status = 'success' 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        cursor.fetchall()
    query_time = time.time() - start
    print(f"✅ 耗时: {query_time:.3f}s, 速度: {5000/query_time:.0f} 查询/秒")
    
    results.append({
        "operation": "索引查询",
        "queries": 5000,
        "time_seconds": round(query_time, 3),
        "queries_per_second": round(5000 / query_time, 0)
    })
    
    # 测试3: 复杂查询
    print("测试复杂查询 (1000次)...", end=" ")
    start = time.time()
    for _ in range(1000):
        cursor.execute("""
            SELECT target_platform, COUNT(*), AVG(latency_ms)
            FROM message_logs
            WHERE status = 'success'
            GROUP BY target_platform
        """)
        cursor.fetchall()
    complex_query_time = time.time() - start
    print(f"✅ 耗时: {complex_query_time:.3f}s, 速度: {1000/complex_query_time:.0f} 查询/秒")
    
    results.append({
        "operation": "复杂聚合查询",
        "queries": 1000,
        "time_seconds": round(complex_query_time, 3),
        "queries_per_second": round(1000 / complex_query_time, 0)
    })
    
    # 清理测试数据
    cursor.execute("DELETE FROM message_logs WHERE kook_channel_id = 'stress_test_channel'")
    conn.commit()
    conn.close()
    
    return {
        "test_name": "数据库性能测试",
        "status": "success",
        "results": results
    }


def test_3_redis_queue_performance():
    """测试3: Redis队列性能测试"""
    print("\n" + "=" * 100)
    print("测试3: Redis队列性能测试")
    print("=" * 100)
    
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis连接成功")
    except Exception as e:
        print(f"⚠️  Redis未运行: {e}")
        return {
            "test_name": "Redis队列性能测试",
            "status": "skipped",
            "reason": "Redis未运行"
        }
    
    results = []
    
    # 测试1: 单次操作
    print("\n测试单次入队/出队 (10000次)...", end=" ")
    start = time.time()
    for i in range(10000):
        r.lpush("test_queue", f"message_{i}")
    enqueue_time = time.time() - start
    
    start = time.time()
    for _ in range(10000):
        r.rpop("test_queue")
    dequeue_time = time.time() - start
    
    print(f"✅ 入队: {enqueue_time:.3f}s, 出队: {dequeue_time:.3f}s")
    
    results.append({
        "operation": "单次操作",
        "count": 10000,
        "enqueue_time_seconds": round(enqueue_time, 3),
        "dequeue_time_seconds": round(dequeue_time, 3),
        "enqueue_ops_per_second": round(10000 / enqueue_time, 0),
        "dequeue_ops_per_second": round(10000 / dequeue_time, 0)
    })
    
    # 测试2: Pipeline批量操作
    print("测试Pipeline批量操作 (50000次)...", end=" ")
    start = time.time()
    pipe = r.pipeline()
    for i in range(50000):
        pipe.lpush("batch_queue", f"message_{i}")
    pipe.execute()
    batch_enqueue_time = time.time() - start
    
    start = time.time()
    pipe = r.pipeline()
    for _ in range(50000):
        pipe.rpop("batch_queue")
    pipe.execute()
    batch_dequeue_time = time.time() - start
    
    speedup = enqueue_time / batch_enqueue_time * 5  # 因为是5倍数量
    print(f"✅ 批量入队: {batch_enqueue_time:.3f}s, 加速: {speedup:.1f}x")
    
    results.append({
        "operation": "Pipeline批量",
        "count": 50000,
        "enqueue_time_seconds": round(batch_enqueue_time, 3),
        "dequeue_time_seconds": round(batch_dequeue_time, 3),
        "enqueue_ops_per_second": round(50000 / batch_enqueue_time, 0),
        "dequeue_ops_per_second": round(50000 / batch_dequeue_time, 0),
        "speedup": round(speedup, 1)
    })
    
    return {
        "test_name": "Redis队列性能测试",
        "status": "success",
        "results": results
    }


def test_4_crypto_performance():
    """测试4: 加密解密性能测试"""
    print("\n" + "=" * 100)
    print("测试4: 加密解密性能测试")
    print("=" * 100)
    
    try:
        from app.utils.crypto import encrypt_data, decrypt_data
        
        test_data = "这是一段需要加密的敏感数据" * 10
        results = []
        
        print(f"\n测试数据大小: {len(test_data)} 字节")
        
        # 测试加密
        print("测试AES-256加密 (5000次)...", end=" ")
        start = time.time()
        encrypted_list = []
        for _ in range(5000):
            encrypted = encrypt_data(test_data)
            encrypted_list.append(encrypted)
        encrypt_time = time.time() - start
        print(f"✅ 耗时: {encrypt_time:.3f}s, 速度: {5000/encrypt_time:.0f} ops/s")
        
        # 测试解密
        print("测试AES-256解密 (5000次)...", end=" ")
        start = time.time()
        for encrypted in encrypted_list:
            decrypt_data(encrypted)
        decrypt_time = time.time() - start
        print(f"✅ 耗时: {decrypt_time:.3f}s, 速度: {5000/decrypt_time:.0f} ops/s")
        
        results.append({
            "operation": "AES-256加密解密",
            "data_size_bytes": len(test_data),
            "iterations": 5000,
            "encrypt_time_seconds": round(encrypt_time, 3),
            "decrypt_time_seconds": round(decrypt_time, 3),
            "encrypt_ops_per_second": round(5000 / encrypt_time, 0),
            "decrypt_ops_per_second": round(5000 / decrypt_time, 0)
        })
        
        return {
            "test_name": "加密解密性能测试",
            "status": "success",
            "results": results
        }
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return {"test_name": "加密解密性能测试", "status": "failed", "error": str(e)}


def test_5_rate_limiter_performance():
    """测试5: 限流器性能测试"""
    print("\n" + "=" * 100)
    print("测试5: 限流器性能测试")
    print("=" * 100)
    
    try:
        from app.utils.rate_limiter import RateLimiter
        
        results = []
        
        # 测试不同限流配置
        configs = [
            (10, 1, "低速限流 (10/秒)"),
            (50, 1, "中速限流 (50/秒)"),
            (100, 1, "高速限流 (100/秒)"),
        ]
        
        async def test_limiter(calls: int, period: int, name: str):
            print(f"\n测试 {name}...")
            limiter = RateLimiter(calls=calls, period=period)
            
            start = time.time()
            acquire_times = []
            
            # 发送calls * 2个请求
            for i in range(calls * 2):
                acquire_start = time.time()
                await limiter.acquire()
                acquire_time = time.time() - acquire_start
                acquire_times.append(acquire_time)
            
            total_time = time.time() - start
            
            # 统计
            immediate = sum(1 for t in acquire_times if t < 0.01)  # 立即通过
            delayed = len(acquire_times) - immediate
            
            print(f"  ✅ 总耗时: {total_time:.3f}s")
            print(f"  ✅ 立即通过: {immediate}, 被限流: {delayed}")
            print(f"  ✅ 平均等待: {sum(acquire_times)/len(acquire_times)*1000:.2f}ms")
            
            return {
                "limiter_name": name,
                "calls_per_period": calls,
                "period_seconds": period,
                "total_requests": calls * 2,
                "total_time_seconds": round(total_time, 3),
                "immediate_pass": immediate,
                "delayed": delayed,
                "avg_wait_ms": round(sum(acquire_times)/len(acquire_times)*1000, 2)
            }
        
        async def run_tests():
            for calls, period, name in configs:
                result = await test_limiter(calls, period, name)
                results.append(result)
        
        asyncio.run(run_tests())
        
        return {
            "test_name": "限流器性能测试",
            "status": "success",
            "results": results
        }
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return {"test_name": "限流器性能测试", "status": "failed", "error": str(e)}


def test_6_filter_performance():
    """测试6: 过滤器性能测试"""
    print("\n" + "=" * 100)
    print("测试6: 过滤器性能测试")
    print("=" * 100)
    
    # 生成测试消息
    test_messages = []
    keywords = ["广告", "spam", "垃圾", "正常", "重要", "公告"]
    users = ["user1", "user2", "spam_user", "admin"]
    
    for i in range(10000):
        test_messages.append({
            "content": f"消息内容 {random.choice(keywords)} {i}",
            "sender": random.choice(users),
            "type": random.choice(["text", "image", "file"])
        })
    
    results = []
    
    # 测试1: 关键词过滤
    print("\n测试关键词过滤 (10000条消息)...", end=" ")
    blacklist_keywords = ["广告", "spam", "垃圾"]
    
    start = time.time()
    filtered = 0
    for msg in test_messages:
        if any(kw in msg["content"] for kw in blacklist_keywords):
            filtered += 1
    keyword_time = time.time() - start
    
    print(f"✅ 耗时: {keyword_time:.3f}s, 过滤: {filtered}条, 吞吐: {10000/keyword_time:.0f} 消息/秒")
    
    results.append({
        "filter_type": "关键词过滤",
        "messages": 10000,
        "filtered_count": filtered,
        "time_seconds": round(keyword_time, 3),
        "throughput": round(10000 / keyword_time, 0)
    })
    
    # 测试2: 用户过滤
    print("测试用户过滤 (10000条消息)...", end=" ")
    blacklist_users = ["spam_user"]
    
    start = time.time()
    filtered = 0
    for msg in test_messages:
        if msg["sender"] in blacklist_users:
            filtered += 1
    user_time = time.time() - start
    
    print(f"✅ 耗时: {user_time:.3f}s, 过滤: {filtered}条, 吞吐: {10000/user_time:.0f} 消息/秒")
    
    results.append({
        "filter_type": "用户过滤",
        "messages": 10000,
        "filtered_count": filtered,
        "time_seconds": round(user_time, 3),
        "throughput": round(10000 / user_time, 0)
    })
    
    # 测试3: 组合过滤
    print("测试组合过滤 (10000条消息)...", end=" ")
    
    start = time.time()
    filtered = 0
    for msg in test_messages:
        if any(kw in msg["content"] for kw in blacklist_keywords) or \
           msg["sender"] in blacklist_users or \
           msg["type"] == "file":
            filtered += 1
    combined_time = time.time() - start
    
    print(f"✅ 耗时: {combined_time:.3f}s, 过滤: {filtered}条, 吞吐: {10000/combined_time:.0f} 消息/秒")
    
    results.append({
        "filter_type": "组合过滤",
        "messages": 10000,
        "filtered_count": filtered,
        "time_seconds": round(combined_time, 3),
        "throughput": round(10000 / combined_time, 0)
    })
    
    return {
        "test_name": "过滤器性能测试",
        "status": "success",
        "results": results
    }


def test_7_multiprocessing_performance():
    """测试7: 多进程处理性能测试"""
    print("\n" + "=" * 100)
    print("测试7: 多进程处理性能测试")
    print("=" * 100)
    
    def process_task(data):
        """模拟图片处理等CPU密集型任务"""
        result = 0
        for i in range(10000):
            result += data * i
        return result
    
    test_data = list(range(1000))
    results = []
    
    # 测试1: 单线程
    print("\n测试单线程处理 (1000个任务)...", end=" ")
    start = time.time()
    for data in test_data:
        process_task(data)
    single_time = time.time() - start
    print(f"✅ 耗时: {single_time:.3f}s")
    
    results.append({
        "method": "单线程",
        "tasks": 1000,
        "time_seconds": round(single_time, 3),
        "tasks_per_second": round(1000 / single_time, 0)
    })
    
    # 测试2: 多线程
    print(f"测试多线程处理 ({multiprocessing.cpu_count()}线程, 1000个任务)...", end=" ")
    start = time.time()
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        list(executor.map(process_task, test_data))
    thread_time = time.time() - start
    print(f"✅ 耗时: {thread_time:.3f}s, 加速: {single_time/thread_time:.1f}x")
    
    results.append({
        "method": f"多线程({multiprocessing.cpu_count()})",
        "tasks": 1000,
        "time_seconds": round(thread_time, 3),
        "tasks_per_second": round(1000 / thread_time, 0),
        "speedup": round(single_time / thread_time, 2)
    })
    
    # 测试3: 多进程
    print(f"测试多进程处理 ({multiprocessing.cpu_count()}进程, 1000个任务)...", end=" ")
    start = time.time()
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        list(executor.map(process_task, test_data))
    process_time = time.time() - start
    print(f"✅ 耗时: {process_time:.3f}s, 加速: {single_time/process_time:.1f}x")
    
    results.append({
        "method": f"多进程({multiprocessing.cpu_count()})",
        "tasks": 1000,
        "time_seconds": round(process_time, 3),
        "tasks_per_second": round(1000 / process_time, 0),
        "speedup": round(single_time / process_time, 2)
    })
    
    return {
        "test_name": "多进程处理性能测试",
        "status": "success",
        "cpu_cores": multiprocessing.cpu_count(),
        "results": results
    }


def generate_report():
    """生成测试报告"""
    report_path = Path(__file__).parent / "独立压力测试报告.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# KOOK消息转发系统 - 独立压力测试报告\n\n")
        f.write(f"**测试时间**: {test_results['start_time']}\n")
        f.write(f"**Python版本**: {test_results['environment']['python_version']}\n")
        f.write(f"**CPU核心数**: {test_results['environment']['cpu_cores']}\n\n")
        f.write("---\n\n")
        
        f.write("## 📊 测试概览\n\n")
        f.write("| 测试项 | 状态 |\n")
        f.write("|--------|------|\n")
        
        for test_name, test_data in test_results["tests"].items():
            status = "✅" if test_data.get("status") == "success" else "⚠️" if test_data.get("status") == "skipped" else "❌"
            f.write(f"| {test_data.get('test_name', test_name)} | {status} |\n")
        
        f.write("\n---\n\n")
        
        for test_name, test_data in test_results["tests"].items():
            f.write(f"## {test_data.get('test_name', test_name)}\n\n")
            
            if test_data.get("status") == "skipped":
                f.write(f"**状态**: ⚠️ 跳过 - {test_data.get('reason', 'Unknown')}\n\n")
                continue
            
            if test_data.get("status") == "failed":
                f.write(f"**状态**: ❌ 失败 - {test_data.get('error', 'Unknown')}\n\n")
                continue
            
            if "results" in test_data and isinstance(test_data["results"], list):
                if test_data["results"]:
                    keys = test_data["results"][0].keys()
                    f.write("| " + " | ".join(keys) + " |\n")
                    f.write("|" + "|".join(["---"] * len(keys)) + "|\n")
                    
                    for result in test_data["results"]:
                        values = []
                        for k in keys:
                            v = result.get(k, "")
                            if isinstance(v, float):
                                values.append(f"{v:.2f}")
                            else:
                                values.append(str(v))
                        f.write("| " + " | ".join(values) + " |\n")
            
            f.write("\n")
        
        f.write("---\n\n")
        f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"\n{'='*100}")
    print(f"📄 测试报告已保存至: {report_path}")
    print(f"{'='*100}")


def main():
    """主函数"""
    try:
        # 运行所有测试
        test_results["tests"]["test_1"] = test_1_message_formatter_performance()
        test_results["tests"]["test_2"] = test_2_database_performance()
        test_results["tests"]["test_3"] = test_3_redis_queue_performance()
        test_results["tests"]["test_4"] = test_4_crypto_performance()
        test_results["tests"]["test_5"] = test_5_rate_limiter_performance()
        test_results["tests"]["test_6"] = test_6_filter_performance()
        test_results["tests"]["test_7"] = test_7_multiprocessing_performance()
        
        # 保存结果
        test_results["end_time"] = datetime.now().isoformat()
        
        # 保存JSON
        json_path = Path(__file__).parent / "standalone_stress_test_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*100}")
        print(f"📊 JSON结果已保存至: {json_path}")
        
        # 生成报告
        generate_report()
        
        print(f"\n{'='*100}")
        print("✅ 所有测试完成！")
        print(f"{'='*100}\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
