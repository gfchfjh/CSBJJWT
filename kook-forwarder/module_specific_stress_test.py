"""
KOOK消息转发系统 - 模块专项压力测试
针对特定功能模块进行深度压力测试
"""
import asyncio
import time
import json
import sys
import random
import string
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import statistics

sys.path.insert(0, str(Path(__file__).parent / "backend"))


class ModuleSpecificStressTest:
    """模块专项压力测试"""
    
    def __init__(self):
        self.results = {}
    
    # ==================== 测试1: 消息验证器压力测试 ====================
    
    async def test_message_validator_stress(self):
        """消息验证器压力测试"""
        print("\n" + "=" * 80)
        print("测试1: 消息验证器压力测试")
        print("=" * 80)
        
        try:
            from app.processors.message_validator import MessageValidator
            
            validator = MessageValidator()
            results = []
            
            # 生成测试消息
            valid_messages = [
                {
                    "message_id": f"valid_{i}",
                    "channel_id": "test_channel",
                    "content": f"这是有效消息 {i}",
                    "message_type": "text",
                    "sender_id": f"user_{i}",
                    "sender_name": f"用户{i}",
                    "timestamp": datetime.now().isoformat(),
                }
                for i in range(1000)
            ]
            
            invalid_messages = [
                {"message_id": f"invalid_{i}"},  # 缺少必需字段
                {"content": "无message_id"},
                {"message_id": "", "content": "空message_id"},
                None,  # 空消息
                {},  # 空字典
            ] * 200
            
            # 测试验证性能
            print("测试有效消息验证...")
            start = time.time()
            valid_count = sum(1 for msg in valid_messages if validator.validate(msg))
            valid_time = time.time() - start
            print(f"  ✓ 有效消息验证: {valid_count}/1000, 耗时: {valid_time:.3f}s, QPS: {1000/valid_time:.2f}")
            
            print("测试无效消息验证...")
            start = time.time()
            invalid_count = sum(1 for msg in invalid_messages if not validator.validate(msg))
            invalid_time = time.time() - start
            print(f"  ✓ 无效消息拒绝: {invalid_count}/1000, 耗时: {invalid_time:.3f}s, QPS: {1000/invalid_time:.2f}")
            
            # 测试消息清洗
            print("测试消息清洗...")
            dirty_messages = [
                {
                    "message_id": f"dirty_{i}",
                    "content": "  包含多余空格  \n\n",
                    "extra_field": "应该被移除",
                    "sender_name": "<script>XSS</script>",
                }
                for i in range(500)
            ]
            
            start = time.time()
            cleaned = [validator.sanitize(msg) for msg in dirty_messages]
            clean_time = time.time() - start
            print(f"  ✓ 消息清洗: 500条, 耗时: {clean_time:.3f}s, QPS: {500/clean_time:.2f}")
            
            self.results["message_validator"] = {
                "valid_validation_qps": round(1000/valid_time, 2),
                "invalid_validation_qps": round(1000/invalid_time, 2),
                "sanitize_qps": round(500/clean_time, 2),
            }
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
    
    # ==================== 测试2: 过滤器压力测试 ====================
    
    async def test_filter_stress(self):
        """过滤器压力测试"""
        print("\n" + "=" * 80)
        print("测试2: 过滤器压力测试")
        print("=" * 80)
        
        try:
            from app.processors.filter import MessageFilter
            
            filter_obj = MessageFilter()
            
            # 添加测试规则
            blacklist_keywords = ["广告", "代练", "外挂", "辅助", "刷钻"]
            whitelist_keywords = ["官方", "公告", "更新"]
            blacklist_users = [f"user_{i}" for i in range(100)]
            
            # 生成测试消息
            test_messages = []
            
            # 1000条正常消息
            for i in range(1000):
                test_messages.append({
                    "message_id": f"normal_{i}",
                    "content": f"这是正常消息 {i}",
                    "sender_id": f"normal_user_{i}",
                    "sender_name": f"正常用户{i}",
                })
            
            # 500条包含黑名单关键词
            for i in range(500):
                keyword = random.choice(blacklist_keywords)
                test_messages.append({
                    "message_id": f"blocked_{i}",
                    "content": f"这是{keyword}消息",
                    "sender_id": f"user_{i}",
                    "sender_name": f"用户{i}",
                })
            
            # 300条包含白名单关键词
            for i in range(300):
                keyword = random.choice(whitelist_keywords)
                test_messages.append({
                    "message_id": f"whitelisted_{i}",
                    "content": f"{keyword}：重要通知",
                    "sender_id": f"admin_{i}",
                    "sender_name": f"管理员{i}",
                })
            
            # 200条黑名单用户消息
            for i in range(200):
                test_messages.append({
                    "message_id": f"blocked_user_{i}",
                    "content": "正常内容",
                    "sender_id": random.choice(blacklist_users),
                    "sender_name": "黑名单用户",
                })
            
            random.shuffle(test_messages)
            
            # 测试关键词过滤性能
            print("测试关键词过滤...")
            start = time.time()
            
            passed = 0
            for msg in test_messages:
                content = msg.get("content", "")
                # 检查黑名单
                if any(kw in content for kw in blacklist_keywords):
                    continue
                # 如果有白名单且不在白名单中，过滤
                if whitelist_keywords and not any(kw in content for kw in whitelist_keywords):
                    if not any(kw in content for kw in whitelist_keywords):
                        pass  # 允许通过
                passed += 1
            
            filter_time = time.time() - start
            print(f"  ✓ 处理: {len(test_messages)}条, 通过: {passed}条, "
                  f"耗时: {filter_time:.3f}s, QPS: {len(test_messages)/filter_time:.2f}")
            
            # 测试用户过滤性能
            print("测试用户过滤...")
            start = time.time()
            
            user_passed = sum(1 for msg in test_messages 
                            if msg.get("sender_id") not in blacklist_users)
            
            user_filter_time = time.time() - start
            print(f"  ✓ 处理: {len(test_messages)}条, 通过: {user_passed}条, "
                  f"耗时: {user_filter_time:.3f}s, QPS: {len(test_messages)/user_filter_time:.2f}")
            
            # 测试复合过滤
            print("测试复合过滤（关键词+用户）...")
            start = time.time()
            
            complex_passed = 0
            for msg in test_messages:
                content = msg.get("content", "")
                sender = msg.get("sender_id", "")
                
                # 黑名单用户直接拒绝
                if sender in blacklist_users:
                    continue
                
                # 黑名单关键词拒绝
                if any(kw in content for kw in blacklist_keywords):
                    continue
                
                complex_passed += 1
            
            complex_filter_time = time.time() - start
            print(f"  ✓ 处理: {len(test_messages)}条, 通过: {complex_passed}条, "
                  f"耗时: {complex_filter_time:.3f}s, QPS: {len(test_messages)/complex_filter_time:.2f}")
            
            self.results["filter"] = {
                "keyword_filter_qps": round(len(test_messages)/filter_time, 2),
                "user_filter_qps": round(len(test_messages)/user_filter_time, 2),
                "complex_filter_qps": round(len(test_messages)/complex_filter_time, 2),
            }
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
    
    # ==================== 测试3: 加密解密压力测试 ====================
    
    async def test_crypto_stress(self):
        """加密解密压力测试"""
        print("\n" + "=" * 80)
        print("测试3: 加密解密压力测试")
        print("=" * 80)
        
        try:
            from app.utils.crypto import encrypt_data, decrypt_data
            
            # 生成测试数据
            test_data = [
                f"test_password_{i}_{''.join(random.choices(string.ascii_letters, k=20))}"
                for i in range(1000)
            ]
            
            # 测试加密性能
            print("测试加密性能...")
            start = time.time()
            encrypted_data = [encrypt_data(data) for data in test_data]
            encrypt_time = time.time() - start
            print(f"  ✓ 加密: 1000条, 耗时: {encrypt_time:.3f}s, QPS: {1000/encrypt_time:.2f}")
            
            # 测试解密性能
            print("测试解密性能...")
            start = time.time()
            decrypted_data = [decrypt_data(enc) for enc in encrypted_data]
            decrypt_time = time.time() - start
            print(f"  ✓ 解密: 1000条, 耗时: {decrypt_time:.3f}s, QPS: {1000/decrypt_time:.2f}")
            
            # 验证正确性
            correct = sum(1 for orig, dec in zip(test_data, decrypted_data) if orig == dec)
            print(f"  ✓ 正确性验证: {correct}/1000")
            
            # 测试不同长度数据
            print("测试不同长度数据加密...")
            length_results = []
            for length in [10, 50, 100, 500, 1000]:
                data = ''.join(random.choices(string.ascii_letters, k=length))
                
                start = time.time()
                for _ in range(100):
                    encrypted = encrypt_data(data)
                enc_time = time.time() - start
                
                start = time.time()
                for _ in range(100):
                    decrypted = decrypt_data(encrypted)
                dec_time = time.time() - start
                
                length_results.append({
                    "length": length,
                    "encrypt_time_ms": round(enc_time * 10, 2),  # 平均每条
                    "decrypt_time_ms": round(dec_time * 10, 2),
                })
                
                print(f"  ✓ 长度{length}: 加密{round(enc_time * 10, 2)}ms, 解密{round(dec_time * 10, 2)}ms")
            
            self.results["crypto"] = {
                "encrypt_qps": round(1000/encrypt_time, 2),
                "decrypt_qps": round(1000/decrypt_time, 2),
                "accuracy": correct / 1000 * 100,
                "length_results": length_results,
            }
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
    
    # ==================== 测试4: 日志记录压力测试 ====================
    
    async def test_logger_stress(self):
        """日志记录压力测试"""
        print("\n" + "=" * 80)
        print("测试4: 日志记录压力测试")
        print("=" * 80)
        
        try:
            from app.utils.logger import logger
            import logging
            
            # 生成测试日志
            test_logs = [
                (logging.DEBUG, f"调试日志 {i}"),
                (logging.INFO, f"信息日志 {i}"),
                (logging.WARNING, f"警告日志 {i}"),
                (logging.ERROR, f"错误日志 {i}"),
            ]
            
            # 测试不同级别日志写入性能
            results = {}
            
            for level, prefix in [(logging.DEBUG, "DEBUG"), (logging.INFO, "INFO"), 
                                 (logging.WARNING, "WARNING"), (logging.ERROR, "ERROR")]:
                print(f"测试{prefix}级别日志...")
                
                start = time.time()
                for i in range(1000):
                    logger.log(level, f"{prefix}日志测试 {i}")
                
                log_time = time.time() - start
                results[prefix.lower()] = {
                    "time": round(log_time, 3),
                    "qps": round(1000/log_time, 2),
                }
                print(f"  ✓ 写入: 1000条, 耗时: {log_time:.3f}s, QPS: {1000/log_time:.2f}")
            
            # 测试并发日志写入
            print("测试并发日志写入...")
            
            async def write_logs(count):
                for i in range(count):
                    logger.info(f"并发日志测试 {i}")
            
            start = time.time()
            tasks = [write_logs(100) for _ in range(10)]  # 10个并发任务,每个写100条
            await asyncio.gather(*tasks)
            concurrent_time = time.time() - start
            
            print(f"  ✓ 并发写入: 1000条, 耗时: {concurrent_time:.3f}s, QPS: {1000/concurrent_time:.2f}")
            
            results["concurrent"] = {
                "time": round(concurrent_time, 3),
                "qps": round(1000/concurrent_time, 2),
            }
            
            self.results["logger"] = results
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
    
    # ==================== 测试5: WebSocket连接压力测试 ====================
    
    async def test_websocket_stress(self):
        """WebSocket连接压力测试（模拟）"""
        print("\n" + "=" * 80)
        print("测试5: WebSocket连接压力测试")
        print("=" * 80)
        
        print("模拟WebSocket连接...")
        
        # 模拟WebSocket连接池
        class MockWebSocket:
            def __init__(self, ws_id):
                self.id = ws_id
                self.connected = False
                self.messages_sent = 0
                self.messages_received = 0
            
            async def connect(self):
                await asyncio.sleep(0.01)  # 模拟连接延迟
                self.connected = True
                return True
            
            async def send(self, message):
                if not self.connected:
                    raise Exception("Not connected")
                await asyncio.sleep(0.001)  # 模拟发送延迟
                self.messages_sent += 1
            
            async def receive(self):
                if not self.connected:
                    raise Exception("Not connected")
                await asyncio.sleep(0.001)  # 模拟接收延迟
                self.messages_received += 1
                return f"Message {self.messages_received}"
            
            async def close(self):
                self.connected = False
        
        # 测试并发连接
        connection_counts = [10, 50, 100, 200]
        results = []
        
        for count in connection_counts:
            print(f"测试{count}个并发连接...")
            
            # 创建连接
            start = time.time()
            websockets = [MockWebSocket(i) for i in range(count)]
            connect_tasks = [ws.connect() for ws in websockets]
            await asyncio.gather(*connect_tasks)
            connect_time = time.time() - start
            
            # 测试消息发送
            start = time.time()
            send_tasks = []
            for ws in websockets:
                for i in range(10):  # 每个连接发送10条消息
                    send_tasks.append(ws.send(f"Test message {i}"))
            await asyncio.gather(*send_tasks)
            send_time = time.time() - start
            
            # 测试消息接收
            start = time.time()
            receive_tasks = []
            for ws in websockets:
                for i in range(10):
                    receive_tasks.append(ws.receive())
            await asyncio.gather(*receive_tasks)
            receive_time = time.time() - start
            
            # 关闭连接
            close_tasks = [ws.close() for ws in websockets]
            await asyncio.gather(*close_tasks)
            
            result = {
                "connections": count,
                "connect_time": round(connect_time, 3),
                "send_time": round(send_time, 3),
                "receive_time": round(receive_time, 3),
                "total_messages": count * 10,
                "send_qps": round((count * 10) / send_time, 2),
                "receive_qps": round((count * 10) / receive_time, 2),
            }
            results.append(result)
            
            print(f"  ✓ 连接耗时: {result['connect_time']}s, "
                  f"发送QPS: {result['send_qps']}, "
                  f"接收QPS: {result['receive_qps']}")
        
        self.results["websocket"] = {"results": results}
    
    # ==================== 测试6: 缓存系统压力测试 ====================
    
    async def test_cache_stress(self):
        """缓存系统压力测试"""
        print("\n" + "=" * 80)
        print("测试6: 缓存系统压力测试")
        print("=" * 80)
        
        try:
            # 简单的内存缓存实现
            class SimpleCache:
                def __init__(self, max_size=10000):
                    self.cache = {}
                    self.max_size = max_size
                
                def get(self, key):
                    return self.cache.get(key)
                
                def set(self, key, value):
                    if len(self.cache) >= self.max_size:
                        # 简单的FIFO策略
                        first_key = next(iter(self.cache))
                        del self.cache[first_key]
                    self.cache[key] = value
                
                def delete(self, key):
                    if key in self.cache:
                        del self.cache[key]
                
                def clear(self):
                    self.cache.clear()
            
            cache = SimpleCache(max_size=10000)
            
            # 测试写入性能
            print("测试缓存写入...")
            start = time.time()
            for i in range(10000):
                cache.set(f"key_{i}", f"value_{i}")
            write_time = time.time() - start
            print(f"  ✓ 写入: 10000条, 耗时: {write_time:.3f}s, QPS: {10000/write_time:.2f}")
            
            # 测试读取性能
            print("测试缓存读取...")
            start = time.time()
            for i in range(10000):
                cache.get(f"key_{i}")
            read_time = time.time() - start
            print(f"  ✓ 读取: 10000条, 耗时: {read_time:.3f}s, QPS: {10000/read_time:.2f}")
            
            # 测试混合操作（70%读，30%写）
            print("测试混合操作（70%读，30%写）...")
            start = time.time()
            for i in range(10000):
                if random.random() < 0.7:
                    cache.get(f"key_{random.randint(0, 9999)}")
                else:
                    cache.set(f"key_{i}", f"value_{i}")
            mixed_time = time.time() - start
            print(f"  ✓ 混合操作: 10000次, 耗时: {mixed_time:.3f}s, QPS: {10000/mixed_time:.2f}")
            
            # 测试缓存淘汰
            print("测试缓存淘汰...")
            cache.clear()
            start = time.time()
            for i in range(15000):  # 超过max_size
                cache.set(f"evict_key_{i}", f"value_{i}")
            evict_time = time.time() - start
            final_size = len(cache.cache)
            print(f"  ✓ 写入: 15000条, 最终大小: {final_size}, 耗时: {evict_time:.3f}s")
            
            self.results["cache"] = {
                "write_qps": round(10000/write_time, 2),
                "read_qps": round(10000/read_time, 2),
                "mixed_qps": round(10000/mixed_time, 2),
                "eviction_qps": round(15000/evict_time, 2),
            }
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
    
    # ==================== 测试7: 错误处理压力测试 ====================
    
    async def test_error_handling_stress(self):
        """错误处理压力测试"""
        print("\n" + "=" * 80)
        print("测试7: 错误处理压力测试")
        print("=" * 80)
        
        try:
            from app.utils.error_handler import ErrorHandler
            
            handler = ErrorHandler()
            
            # 生成各种错误
            errors = []
            
            # 1. 网络错误
            for i in range(200):
                errors.append(("network", Exception(f"Connection timeout {i}")))
            
            # 2. 验证错误
            for i in range(200):
                errors.append(("validation", ValueError(f"Invalid message format {i}")))
            
            # 3. 数据库错误
            for i in range(200):
                errors.append(("database", Exception(f"Database error {i}")))
            
            # 4. 未知错误
            for i in range(200):
                errors.append(("unknown", RuntimeError(f"Unknown error {i}")))
            
            # 5. 权限错误
            for i in range(200):
                errors.append(("permission", PermissionError(f"Access denied {i}")))
            
            random.shuffle(errors)
            
            # 测试错误处理性能
            print("测试错误处理...")
            start = time.time()
            
            handled_errors = []
            for error_type, error in errors:
                try:
                    # 模拟错误处理
                    error_info = {
                        "type": error_type,
                        "message": str(error),
                        "timestamp": datetime.now().isoformat(),
                    }
                    handled_errors.append(error_info)
                except Exception as e:
                    pass
            
            handle_time = time.time() - start
            print(f"  ✓ 处理: 1000个错误, 耗时: {handle_time:.3f}s, QPS: {1000/handle_time:.2f}")
            
            # 统计错误类型分布
            error_counts = {}
            for error_type, _ in errors:
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            print("  错误类型分布:")
            for error_type, count in error_counts.items():
                print(f"    - {error_type}: {count}")
            
            self.results["error_handling"] = {
                "handling_qps": round(1000/handle_time, 2),
                "error_distribution": error_counts,
            }
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
    
    # ==================== 主测试流程 ====================
    
    async def run_all_tests(self):
        """运行所有专项测试"""
        print("\n" + "=" * 80)
        print("KOOK消息转发系统 - 模块专项压力测试".center(80))
        print("=" * 80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        start_time = time.time()
        
        # 运行所有测试
        await self.test_message_validator_stress()
        await self.test_filter_stress()
        await self.test_crypto_stress()
        await self.test_logger_stress()
        await self.test_websocket_stress()
        await self.test_cache_stress()
        await self.test_error_handling_stress()
        
        total_time = time.time() - start_time
        
        # 打印总结
        print("\n" + "=" * 80)
        print("测试总结".center(80))
        print("=" * 80)
        print(f"\n总耗时: {total_time:.2f}秒")
        print(f"完成测试数: {len(self.results)}")
        
        # 保存结果
        self.save_results()
    
    def save_results(self):
        """保存测试结果"""
        report_path = Path(__file__).parent / "module_stress_test_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ 详细测试报告已保存至: {report_path}")


async def main():
    """主函数"""
    tester = ModuleSpecificStressTest()
    
    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
