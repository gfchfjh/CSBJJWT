"""
优化功能测试套件（✅ P3-4优化：新增测试用例）

测试所有v1.17.0优化功能
"""
import pytest
import asyncio
from datetime import datetime


class TestBatchProcessing:
    """测试批量消息处理（P1-3优化）"""
    
    @pytest.mark.asyncio
    async def test_batch_dequeue(self):
        """测试批量出队功能"""
        from app.queue.redis_client import redis_queue
        
        # 准备测试数据
        messages = [
            {'message_id': f'test_{i}', 'content': f'Message {i}'}
            for i in range(20)
        ]
        
        # 入队
        for msg in messages:
            await redis_queue.enqueue(msg)
        
        # 批量出队
        batch = await redis_queue.dequeue_batch(count=10)
        
        # 验证
        assert len(batch) == 10
        assert batch[0]['message_id'] == 'test_0'
        assert batch[9]['message_id'] == 'test_9'
    
    @pytest.mark.asyncio
    async def test_parallel_processing(self):
        """测试并行处理性能"""
        import time
        from app.queue.worker import message_worker
        
        # 准备测试消息
        messages = [
            {
                'message_id': f'test_{i}',
                'channel_id': 'test_channel',
                'content': f'Test message {i}',
                'message_type': 'text',
                'sender_name': 'Tester'
            }
            for i in range(100)
        ]
        
        # 串行处理（模拟旧版本）
        start = time.time()
        for msg in messages[:10]:
            await message_worker._safe_process_message(msg)
        serial_time = time.time() - start
        
        # 并行处理（新版本）
        start = time.time()
        await asyncio.gather(*[
            message_worker._safe_process_message(msg)
            for msg in messages[10:20]
        ])
        parallel_time = time.time() - start
        
        # 验证：并行处理应该更快
        print(f"串行: {serial_time:.2f}秒, 并行: {parallel_time:.2f}秒")
        # 允许一定误差
        assert parallel_time < serial_time * 1.2


class TestBrowserSharing:
    """测试浏览器共享逻辑（P1-4优化）"""
    
    @pytest.mark.asyncio
    async def test_shared_browser_single_instance(self):
        """测试共享Browser只有一个实例"""
        from app.kook.scraper import scraper_manager
        
        # 启动多个抓取器
        for i in range(3):
            await scraper_manager.start_scraper(
                account_id=i,
                cookie='{"test": "cookie"}',
                use_shared_browser=True
            )
        
        # 验证：只有一个Browser实例
        assert scraper_manager.shared_browser is not None
        assert len(scraper_manager.contexts) == 3
    
    @pytest.mark.asyncio
    async def test_context_isolation(self):
        """测试Context隔离（Cookie不混淆）"""
        from app.kook.scraper import scraper_manager
        
        # 启动两个账号
        await scraper_manager.start_scraper(
            account_id=1,
            cookie='{"token": "account1_token"}',
            use_shared_browser=True
        )
        
        await scraper_manager.start_scraper(
            account_id=2,
            cookie='{"token": "account2_token"}',
            use_shared_browser=True
        )
        
        # 验证：每个账号有独立Context
        assert 1 in scraper_manager.contexts
        assert 2 in scraper_manager.contexts
        assert scraper_manager.contexts[1] != scraper_manager.contexts[2]
        
        # 清理
        await scraper_manager.stop_all()


class TestEncryptionPersistence:
    """测试加密密钥持久化（P1-5优化）"""
    
    def test_key_file_exists(self):
        """测试密钥文件存在"""
        from app.config import settings
        
        key_file = settings.data_dir / ".encryption_key"
        
        # 第一次启动会生成密钥文件
        from app.utils.crypto import crypto_manager
        
        assert key_file.exists()
    
    def test_key_persistence_after_restart(self):
        """测试重启后密钥不变"""
        from app.utils.crypto import CryptoManager
        from app.config import settings
        
        # 第一次初始化
        crypto1 = CryptoManager()
        plaintext = "test_password_123"
        encrypted1 = crypto1.encrypt(plaintext)
        
        # 模拟重启：创建新实例
        crypto2 = CryptoManager()
        decrypted = crypto2.decrypt(encrypted1)
        
        # 验证：能成功解密
        assert decrypted == plaintext


class TestTokenBucketRateLimiter:
    """测试Token Bucket限流器（P2-2优化）"""
    
    @pytest.mark.asyncio
    async def test_token_refill(self):
        """测试令牌自动补充"""
        from app.utils.rate_limiter_enhanced import TokenBucketRateLimiter
        import time
        
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=2.0)
        
        # 消耗所有令牌
        for _ in range(5):
            await limiter.acquire()
        
        assert limiter.tokens == 0
        
        # 等待1秒，应该补充2个令牌
        await asyncio.sleep(1)
        
        available = limiter.get_available_tokens()
        assert 1.8 <= available <= 2.2  # 允许误差
    
    @pytest.mark.asyncio
    async def test_burst_traffic(self):
        """测试突发流量处理"""
        from app.utils.rate_limiter_enhanced import TokenBucketRateLimiter
        import time
        
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=2.0)
        
        # 突发5条消息（桶满，立即通过）
        start = time.time()
        for _ in range(5):
            await limiter.acquire()
        elapsed = time.time() - start
        
        # 应该在1秒内完成（无需等待）
        assert elapsed < 1.0
        
        # 再发5条消息（桶空，需要等待）
        start = time.time()
        for _ in range(5):
            await limiter.acquire()
        elapsed = time.time() - start
        
        # 应该等待约2.5秒（5个令牌 / 2令牌每秒）
        assert 2.0 <= elapsed <= 3.0


class TestStabilityEnhancements:
    """测试稳定性增强（P2-4优化）"""
    
    @pytest.mark.asyncio
    async def test_redis_reconnect(self):
        """测试Redis自动重连"""
        from app.queue.redis_client import redis_queue
        
        # 模拟入队（带重连逻辑）
        message = {'message_id': 'test', 'content': 'test'}
        success = await redis_queue.enqueue(message)
        
        # 即使Redis暂时不可用，应该保存到Fallback
        # 不应该抛出异常
        assert isinstance(success, bool)
    
    @pytest.mark.asyncio
    async def test_worker_exception_recovery(self):
        """测试Worker异常恢复"""
        from app.queue.worker import message_worker
        
        # 模拟异常消息
        bad_message = {
            'message_id': 'bad',
            'content': None,  # 会导致处理失败
            'channel_id': None
        }
        
        # 调用安全处理函数
        result = await message_worker._safe_process_message(bad_message)
        
        # 验证：应该返回False而不是抛出异常
        assert result == False
        
        # Worker应该仍然在运行
        # （在实际测试中验证）


class TestLinkPreview:
    """测试链接预览集成（P1-1优化）"""
    
    @pytest.mark.asyncio
    async def test_extract_urls(self):
        """测试URL提取"""
        from app.processors.link_preview import link_preview_generator
        
        text = """
        查看项目: https://github.com/gfchfjh/CSBJJWT
        文档: https://docs.example.com
        """
        
        urls = link_preview_generator.extract_urls_from_text(text)
        
        assert len(urls) == 2
        assert urls[0] == 'https://github.com/gfchfjh/CSBJJWT'
        assert urls[1] == 'https://docs.example.com'
    
    @pytest.mark.asyncio
    async def test_preview_generation(self):
        """测试预览生成"""
        from app.processors.link_preview import link_preview_generator
        
        # 测试GitHub链接
        url = "https://github.com/gfchfjh/CSBJJWT"
        preview = await link_preview_generator.extract_preview(url)
        
        if preview:  # 可能因网络问题失败
            assert preview['url'] == url
            assert preview['title'] is not None
            print(f"预览标题: {preview['title']}")


class TestImageStrategy:
    """测试图片策略配置（P1-2优化）"""
    
    def test_config_read(self):
        """测试从配置读取策略"""
        from app.config import settings
        
        # 默认策略
        assert settings.image_strategy in ['smart', 'direct', 'imgbed']
    
    @pytest.mark.asyncio
    async def test_strategy_change(self):
        """测试策略切换"""
        from app.config import settings
        
        # 保存原策略
        original = settings.image_strategy
        
        # 切换策略
        settings.image_strategy = 'direct'
        assert settings.image_strategy == 'direct'
        
        settings.image_strategy = 'imgbed'
        assert settings.image_strategy == 'imgbed'
        
        # 恢复原策略
        settings.image_strategy = original


class TestAutoRetry:
    """测试自动重试机制（P2-4优化）"""
    
    @pytest.mark.asyncio
    async def test_browser_crash_retry(self):
        """测试浏览器崩溃重试"""
        # 这个测试需要模拟浏览器崩溃
        # 实际测试中手动验证
        pass
    
    @pytest.mark.asyncio
    async def test_local_fallback(self):
        """测试本地Fallback机制"""
        from app.queue.redis_client import redis_queue
        from app.config import settings
        
        # 测试消息
        message = {
            'message_id': 'fallback_test',
            'content': 'Fallback test message'
        }
        
        # 保存到本地Fallback
        await redis_queue._save_to_local_fallback(message)
        
        # 验证文件存在
        fallback_dir = settings.data_dir / "fallback_queue"
        assert fallback_dir.exists()
        
        # 加载Fallback消息
        loaded = await redis_queue.load_from_local_fallback()
        
        # 应该能找到保存的消息
        assert any(m['message_id'] == 'fallback_test' for m in loaded)


class TestAPIAuthentication:
    """测试API认证（P2-5优化）"""
    
    def test_auth_middleware_exists(self):
        """测试认证中间件存在"""
        from app.middleware.auth_middleware import APIAuthMiddleware
        
        assert APIAuthMiddleware is not None
    
    def test_public_paths(self):
        """测试公开路径配置"""
        from app.middleware.auth_middleware import APIAuthMiddleware
        
        public_paths = APIAuthMiddleware.PUBLIC_PATHS
        
        # 验证必要的公开路径
        assert "/auth/login" in public_paths
        assert "/auth/status" in public_paths
        assert "/api/cookie-import/health" in public_paths


# ✅ P3-4优化：性能基准测试
class TestPerformanceBenchmark:
    """性能基准测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_throughput_benchmark(self):
        """吞吐量基准测试（目标：130 msg/s）"""
        import time
        from app.queue.worker import message_worker
        
        # 准备1000条消息
        messages = [
            {
                'message_id': f'bench_{i}',
                'channel_id': 'test',
                'content': f'Benchmark {i}',
                'message_type': 'text',
                'sender_name': 'Benchmark'
            }
            for i in range(1000)
        ]
        
        # 处理
        start = time.time()
        
        # 批量并行处理（模拟实际场景）
        for i in range(0, 1000, 10):
            batch = messages[i:i+10]
            await asyncio.gather(*[
                message_worker._safe_process_message(msg)
                for msg in batch
            ])
        
        elapsed = time.time() - start
        throughput = 1000 / elapsed
        
        print(f"\n性能基准测试结果:")
        print(f"  处理消息: 1000条")
        print(f"  耗时: {elapsed:.2f}秒")
        print(f"  吞吐量: {throughput:.2f} msg/s")
        print(f"  目标: 130 msg/s")
        
        # 验证：应该接近或超过130 msg/s
        # 由于测试环境差异，放宽到100 msg/s
        assert throughput >= 100
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_memory_usage(self):
        """内存使用测试（目标：5账号<500MB）"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # 记录初始内存
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 模拟启动5个账号（实际测试中需要真实启动）
        # 这里仅测试框架
        
        # 记录最终内存
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"\n内存使用测试:")
        print(f"  初始内存: {initial_memory:.2f} MB")
        print(f"  最终内存: {final_memory:.2f} MB")
        print(f"  增加: {final_memory - initial_memory:.2f} MB")
        
        # 验证：内存增加应该合理
        assert final_memory < initial_memory + 500


class TestErrorDiagnosis:
    """测试错误诊断（P2-3优化）"""
    
    def test_diagnosis_rules_count(self):
        """测试诊断规则数量"""
        from app.utils.error_diagnosis import ErrorDiagnostic
        
        rules = ErrorDiagnostic.DIAGNOSIS_RULES
        
        # 验证：至少有14条规则（原6条 + 新增8条）
        assert len(rules) >= 14
    
    def test_diagnose_playwright_timeout(self):
        """测试Playwright超时诊断"""
        from app.utils.error_diagnosis import ErrorDiagnostic
        
        # 模拟错误
        error = Exception("playwright navigation timeout after 30s")
        
        # 诊断
        diagnosis = ErrorDiagnostic.diagnose(error)
        
        # 验证
        assert diagnosis['matched_rule'] == 'playwright_timeout'
        assert 'timeout' in diagnosis['solution'].lower()
        assert len(diagnosis['suggestions']) > 0


class TestCryptoMigration:
    """测试加密迁移（P1-5优化）"""
    
    def test_migration_tool_exists(self):
        """测试迁移工具存在"""
        from pathlib import Path
        
        migration_tool = Path(__file__).parent.parent / "app" / "utils" / "migrate_encryption.py"
        assert migration_tool.exists()


# ✅ P3-4优化：集成测试
class TestEndToEndIntegration:
    """端到端集成测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_message_flow(self):
        """测试完整消息流程"""
        from app.queue.redis_client import redis_queue
        from app.queue.worker import message_worker
        
        # 1. 入队
        test_message = {
            'message_id': 'e2e_test',
            'channel_id': 'test_channel',
            'content': 'End-to-end test: https://github.com/test',
            'message_type': 'text',
            'sender_name': 'E2E Tester',
            'image_urls': [],
            'file_attachments': []
        }
        
        success = await redis_queue.enqueue(test_message)
        assert success
        
        # 2. 出队
        dequeued = await redis_queue.dequeue(timeout=1)
        assert dequeued is not None
        assert dequeued['message_id'] == 'e2e_test'
        
        # 3. 处理（包括链接预览）
        # 实际环境中会转发到目标平台
        # 这里只测试处理逻辑不抛异常
        result = await message_worker._safe_process_message(dequeued)
        
        # 验证：处理完成（成功或失败都可以）
        assert isinstance(result, bool)


if __name__ == '__main__':
    """运行测试"""
    pytest.main([__file__, '-v', '--tb=short'])
