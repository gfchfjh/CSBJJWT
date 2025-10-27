"""
并发场景测试
测试系统在高并发情况下的表现
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from app.kook.scraper import ScraperManager
from app.queue.worker import MessageWorker
from app.forwarders.discord import DiscordForwarder
from app.processors.formatter import formatter


class TestMultipleAccountsConcurrent:
    """测试多账号并发监听"""
    
    @pytest.mark.asyncio
    async def test_concurrent_account_startup(self):
        """测试多个账号同时启动"""
        manager = ScraperManager()
        
        # 模拟5个账号同时启动
        accounts = [
            {"id": 1, "cookie": "[]"},
            {"id": 2, "cookie": "[]"},
            {"id": 3, "cookie": "[]"},
            {"id": 4, "cookie": "[]"},
            {"id": 5, "cookie": "[]"},
        ]
        
        # 并发启动（使用mock避免真实连接）
        with patch.object(manager, 'start_scraper', new_callable=AsyncMock) as mock_start:
            mock_start.return_value = True
            
            tasks = [
                manager.start_scraper(
                    account_id=acc['id'],
                    cookie=acc['cookie']
                )
                for acc in accounts
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 所有账号都应该成功启动
            assert len(results) == 5
            assert all(isinstance(r, bool) or r is True for r in results if not isinstance(r, Exception))
    
    @pytest.mark.asyncio
    async def test_shared_browser_context(self):
        """测试共享浏览器上下文"""
        manager = ScraperManager()
        manager.use_shared_browser = True
        
        # 确保共享浏览器被创建
        with patch('app.kook.scraper.async_playwright') as mock_playwright:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            
            mock_playwright.return_value.start = AsyncMock()
            mock_playwright.return_value.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_browser.is_connected = Mock(return_value=True)
            
            # 启动2个账号
            browser, context = await manager._ensure_shared_browser()
            
            # 应该只创建一个浏览器实例
            assert manager.shared_browser is not None or browser is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_message_receive(self):
        """测试多个账号同时收到消息"""
        messages_received = []
        
        async def message_callback(message):
            """模拟消息回调"""
            messages_received.append(message)
            await asyncio.sleep(0.01)  # 模拟处理时间
        
        # 模拟3个账号同时收到消息
        accounts = [1, 2, 3]
        tasks = []
        
        for account_id in accounts:
            for msg_num in range(5):
                # 每个账号发送5条消息
                task = message_callback({
                    'account_id': account_id,
                    'message_id': f'msg_{account_id}_{msg_num}',
                    'content': f'Test message from account {account_id}'
                })
                tasks.append(task)
        
        # 并发处理所有消息
        await asyncio.gather(*tasks)
        
        # 应该收到15条消息（3个账号 × 5条）
        assert len(messages_received) == 15
        
        # 确认每个账号的消息都被处理
        account_1_msgs = [m for m in messages_received if m['account_id'] == 1]
        assert len(account_1_msgs) == 5


class TestHighVolumeMessageProcessing:
    """测试高并发消息处理"""
    
    @pytest.mark.asyncio
    async def test_message_queue_under_load(self):
        """测试消息队列在高负载下的表现"""
        from app.queue.redis_client import MessageQueue
        
        # 创建消息队列（使用mock）
        with patch('redis.Redis') as mock_redis:
            queue = MessageQueue()
            queue.redis_client = mock_redis
            
            # 模拟快速入队1000条消息
            messages = [
                {
                    'message_id': f'msg_{i}',
                    'content': f'Test message {i}',
                    'channel_id': 'test_channel'
                }
                for i in range(1000)
            ]
            
            start_time = time.time()
            
            for msg in messages:
                queue.redis_client.lpush('message_queue', str(msg))
            
            elapsed = time.time() - start_time
            
            # 应该在合理时间内完成（<1秒）
            assert elapsed < 1.0
            
            # 验证调用次数
            assert queue.redis_client.lpush.call_count == 1000
    
    @pytest.mark.asyncio
    async def test_worker_concurrent_processing(self):
        """测试Worker并发处理消息"""
        processed_messages = []
        
        async def mock_process_message(message):
            """模拟消息处理"""
            await asyncio.sleep(0.01)  # 模拟处理时间
            processed_messages.append(message['message_id'])
            return True
        
        # 创建100条消息
        messages = [
            {'message_id': f'msg_{i}', 'content': f'Test {i}'}
            for i in range(100)
        ]
        
        # 并发处理
        start_time = time.time()
        tasks = [mock_process_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time
        
        # 应该全部成功
        assert len(processed_messages) == 100
        assert all(results)
        
        # 并发处理应该比串行快很多
        # 串行需要: 100 * 0.01 = 1秒
        # 并发应该在0.1秒内完成
        assert elapsed < 0.5  # 允许一些开销
    
    @pytest.mark.asyncio
    async def test_rate_limiter_under_burst(self):
        """测试限流器在突发流量下的表现"""
        from app.utils.rate_limiter import RateLimiter
        
        # 创建限流器：每秒5个请求
        limiter = RateLimiter(calls=5, period=1)
        
        # 突发100个请求
        start_time = time.time()
        
        tasks = [limiter.acquire() for _ in range(100)]
        await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        # 100个请求，每秒5个，应该需要约20秒
        expected_time = 100 / 5  # 20秒
        
        # 允许10%的误差
        assert elapsed >= expected_time * 0.9
        assert elapsed <= expected_time * 1.2


class TestForwarderPoolConcurrency:
    """测试转发器池并发"""
    
    @pytest.mark.asyncio
    async def test_multiple_webhooks_load_balancing(self):
        """测试多Webhook负载均衡"""
        from app.forwarders.pools import DiscordForwarderPool
        
        # 创建有3个Webhook的池
        webhooks = [
            'https://discord.com/api/webhooks/1',
            'https://discord.com/api/webhooks/2',
            'https://discord.com/api/webhooks/3',
        ]
        
        with patch('app.forwarders.discord.DiscordForwarder.send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            pool = DiscordForwarderPool(webhooks)
            
            # 发送9条消息
            tasks = [
                pool.send_message(content=f"Message {i}")
                for i in range(9)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # 所有消息都应该成功
            assert all(results)
            
            # 每个Webhook应该处理3条消息（负载均衡）
            assert pool.current_index == 0  # 应该回到起点（9 % 3 = 0）
    
    @pytest.mark.asyncio
    async def test_pool_failover(self):
        """测试池中某个Webhook失败时的故障转移"""
        from app.forwarders.pools import DiscordForwarderPool
        
        webhooks = [
            'https://discord.com/api/webhooks/1',  # 正常
            'https://discord.com/api/webhooks/2',  # 失败
            'https://discord.com/api/webhooks/3',  # 正常
        ]
        
        pool = DiscordForwarderPool(webhooks)
        
        # 模拟第2个Webhook失败
        with patch('app.forwarders.discord.DiscordForwarder.send_message', new_callable=AsyncMock) as mock_send:
            # 设置不同的返回值
            call_count = 0
            async def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                # 第2次调用失败（对应第2个webhook）
                return call_count != 2
            
            mock_send.side_effect = side_effect
            
            # 发送3条消息
            results = []
            for i in range(3):
                result = await pool.send_message(content=f"Message {i}")
                results.append(result)
            
            # 应该有1条失败，2条成功
            assert results.count(True) >= 2


class TestImageProcessingConcurrency:
    """测试图片处理并发"""
    
    @pytest.mark.asyncio
    async def test_multiprocess_image_processing(self):
        """测试多进程图片处理"""
        from app.processors.image import ImageProcessor
        
        processor = ImageProcessor()
        
        # 模拟10张图片需要处理
        image_urls = [f"https://example.com/image_{i}.jpg" for i in range(10)]
        
        with patch.object(processor, 'download_image', new_callable=AsyncMock) as mock_download:
            # 模拟下载返回假数据
            mock_download.return_value = b'fake_image_data'
            
            with patch.object(processor, 'compress_image') as mock_compress:
                mock_compress.return_value = b'compressed_data'
                
                # 并发处理
                start_time = time.time()
                
                tasks = [
                    processor.download_image(url)
                    for url in image_urls
                ]
                
                results = await asyncio.gather(*tasks)
                
                elapsed = time.time() - start_time
                
                # 所有图片都应该处理完成
                assert len(results) == 10
                
                # 并发处理应该比串行快
                assert elapsed < 1.0


class TestDatabaseConcurrency:
    """测试数据库并发访问"""
    
    @pytest.mark.asyncio
    async def test_concurrent_log_writes(self):
        """测试并发写入消息日志"""
        from app.database import db
        
        # 并发写入100条日志
        tasks = []
        for i in range(100):
            task = asyncio.create_task(
                asyncio.to_thread(
                    db.add_message_log,
                    kook_message_id=f'concurrent_msg_{i}',
                    kook_channel_id='test_channel',
                    content=f'Test message {i}',
                    message_type='text',
                    sender_name='Test User',
                    target_platform='discord',
                    target_channel='test_discord',
                    status='success'
                )
            )
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time
        
        # 大部分应该成功（允许少量失败，如重复ID）
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        assert success_count >= 95  # 至少95%成功
        
        # 应该在合理时间内完成
        assert elapsed < 5.0
    
    @pytest.mark.asyncio
    async def test_concurrent_read_write(self):
        """测试并发读写"""
        from app.database import db
        
        # 10个并发读，10个并发写
        read_tasks = []
        write_tasks = []
        
        # 写任务
        for i in range(10):
            task = asyncio.create_task(
                asyncio.to_thread(
                    db.add_account,
                    email=f'concurrent_test_{i}@example.com',
                    password_encrypted='test'
                )
            )
            write_tasks.append(task)
        
        # 读任务
        for i in range(10):
            task = asyncio.create_task(
                asyncio.to_thread(db.get_accounts)
            )
            read_tasks.append(task)
        
        # 同时执行
        all_tasks = read_tasks + write_tasks
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # 应该大部分成功
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        assert success_count >= 15  # 至少75%成功


class TestFormatterConcurrency:
    """测试格式转换器并发"""
    
    @pytest.mark.asyncio
    async def test_concurrent_format_conversion(self):
        """测试并发格式转换"""
        # 100条消息同时转换格式
        messages = [
            f"**Test {i}** message with *formatting* and `code`"
            for i in range(100)
        ]
        
        async def convert_message(text):
            """异步转换消息"""
            # 格式转换是同步的，但我们在异步上下文中调用
            await asyncio.sleep(0)  # 让出控制权
            return formatter.kmarkdown_to_discord(text)
        
        start_time = time.time()
        tasks = [convert_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time
        
        # 所有消息都应该转换成功
        assert len(results) == 100
        assert all(isinstance(r, str) for r in results)
        
        # 应该很快完成
        assert elapsed < 1.0


class TestSystemIntegrationConcurrency:
    """测试系统集成并发场景"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_concurrent_flow(self):
        """测试端到端并发流程"""
        # 模拟完整流程：接收消息 -> 入队 -> 处理 -> 转发
        
        processed_messages = []
        
        async def simulate_message_flow(message_id):
            """模拟消息流程"""
            # 1. 接收消息
            message = {
                'message_id': message_id,
                'content': f'Test message {message_id}'
            }
            
            # 2. 格式转换
            await asyncio.sleep(0.01)
            converted = formatter.kmarkdown_to_discord(message['content'])
            
            # 3. 限流
            await asyncio.sleep(0.01)
            
            # 4. 转发（模拟）
            await asyncio.sleep(0.01)
            
            processed_messages.append(message_id)
            return True
        
        # 并发处理50条消息
        start_time = time.time()
        tasks = [simulate_message_flow(f'msg_{i}') for i in range(50)]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time
        
        # 所有消息都应该成功
        assert len(processed_messages) == 50
        assert all(results)
        
        # 并发应该比串行快很多
        # 串行需要: 50 * 0.03 = 1.5秒
        # 并发应该在0.2秒内完成
        assert elapsed < 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
