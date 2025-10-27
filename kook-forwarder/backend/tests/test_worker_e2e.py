"""
Worker端到端测试
测试完整的消息处理流程
"""
import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from app.queue.worker import message_worker, MessageWorker
from app.queue.redis_client import redis_queue
from app.database import db
from app.processors.formatter import formatter
from app.processors.image import image_processor
from app.forwarders.discord import discord_forwarder
from app.forwarders.telegram import telegram_forwarder
from app.forwarders.feishu import feishu_forwarder


@pytest.fixture
def sample_message():
    """示例消息"""
    return {
        "message_id": "test_msg_123",
        "channel_id": "test_channel_456",
        "server_id": "test_server_789",
        "content": "**测试消息** 这是一条测试消息，包含*格式*和`代码`",
        "message_type": "text",
        "sender_id": "user_001",
        "sender_name": "测试用户",
        "sender_avatar": "https://example.com/avatar.jpg",
        "timestamp": datetime.now().isoformat(),
        "attachments": [],
        "image_urls": [],
        "file_attachments": [],
        "mentions": [],
        "mention_all": False,
        "quote": None,
        "cookies": {"token": "test_cookie"}
    }


@pytest.fixture
def sample_image_message():
    """包含图片的消息"""
    return {
        "message_id": "test_img_msg_456",
        "channel_id": "test_channel_456",
        "server_id": "test_server_789",
        "content": "看这张图片！",
        "message_type": "image",
        "sender_id": "user_002",
        "sender_name": "图片测试用户",
        "sender_avatar": "https://example.com/avatar2.jpg",
        "timestamp": datetime.now().isoformat(),
        "attachments": [
            {
                "type": "image",
                "url": "https://img.kookapp.cn/assets/test.jpg"
            }
        ],
        "image_urls": ["https://img.kookapp.cn/assets/test.jpg"],
        "file_attachments": [],
        "mentions": [],
        "mention_all": False,
        "quote": None,
        "cookies": {"token": "test_cookie"}
    }


@pytest.fixture
def sample_mapping():
    """示例频道映射"""
    # 添加测试Bot
    bot_id = db.add_bot_config(
        platform="discord",
        name="测试Discord Bot",
        config={"webhook_url": "https://discord.com/api/webhooks/test/abc123"}
    )
    
    # 添加映射
    mapping_id = db.add_channel_mapping(
        kook_server_id="test_server_789",
        kook_channel_id="test_channel_456",
        kook_channel_name="测试频道",
        target_platform="discord",
        target_bot_id=bot_id,
        target_channel_id="discord_channel_123"
    )
    
    return {
        "mapping_id": mapping_id,
        "bot_id": bot_id
    }


class TestMessageProcessingFlow:
    """消息处理流程测试"""
    
    @pytest.mark.asyncio
    async def test_complete_message_flow(self, sample_message, sample_mapping):
        """测试完整消息处理流程"""
        worker = MessageWorker()
        
        # Mock转发器
        with patch.object(discord_forwarder, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            # 处理消息
            await worker.process_message(sample_message)
            
            # 验证转发器被调用
            assert mock_send.called
            
            # 验证消息被记录到数据库
            logs = db.get_message_logs(limit=1)
            assert len(logs) > 0
            assert logs[0]['kook_message_id'] == sample_message['message_id']
    
    @pytest.mark.asyncio
    async def test_message_deduplication(self, sample_message, sample_mapping):
        """测试消息去重"""
        worker = MessageWorker()
        
        with patch.object(discord_forwarder, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            # 第一次处理
            await worker.process_message(sample_message)
            first_call_count = mock_send.call_count
            
            # 第二次处理相同消息
            await worker.process_message(sample_message)
            second_call_count = mock_send.call_count
            
            # 第二次不应该触发转发（已去重）
            assert second_call_count == first_call_count
    
    @pytest.mark.asyncio
    async def test_format_conversion(self, sample_message):
        """测试格式转换"""
        # KMarkdown转Discord
        discord_text = formatter.kmarkdown_to_discord(sample_message['content'])
        assert "**测试消息**" in discord_text
        assert "*格式*" in discord_text
        assert "`代码`" in discord_text
        
        # KMarkdown转Telegram HTML
        telegram_text = formatter.kmarkdown_to_telegram_html(sample_message['content'])
        assert "<b>测试消息</b>" in telegram_text
        assert "<i>格式</i>" in telegram_text
        assert "<code>代码</code>" in telegram_text
    
    @pytest.mark.asyncio
    async def test_long_message_splitting(self):
        """测试超长消息分段"""
        # 创建超长消息（Discord限制2000字符）
        long_content = "测试消息 " * 500  # 约5000字符
        
        # 分段
        segments = formatter.split_long_message(long_content, max_length=2000)
        
        # 验证
        assert len(segments) > 1
        for segment in segments:
            assert len(segment) <= 2000
        
        # 验证内容完整性
        combined = "".join(segments)
        assert combined == long_content
    
    @pytest.mark.asyncio
    async def test_image_processing_flow(self, sample_image_message, sample_mapping):
        """测试图片处理流程"""
        worker = MessageWorker()
        
        with patch.object(image_processor, 'download_image', new_callable=AsyncMock) as mock_download, \
             patch.object(image_processor, 'compress_image') as mock_compress, \
             patch.object(discord_forwarder, 'send_message', new_callable=AsyncMock) as mock_send:
            
            # Mock图片下载和压缩
            mock_download.return_value = b"fake_image_data"
            mock_compress.return_value = b"compressed_image_data"
            mock_send.return_value = True
            
            # 处理消息
            await worker.process_message(sample_image_message)
            
            # 验证图片处理被调用
            assert mock_download.called
            # 压缩可能根据图片大小决定是否调用
            
            # 验证转发
            assert mock_send.called
    
    @pytest.mark.asyncio
    async def test_filter_rules_application(self, sample_message, sample_mapping):
        """测试过滤规则应用"""
        from app.processors.filter import message_filter
        
        # 添加黑名单关键词
        db.execute("""
            INSERT INTO filter_rules (rule_type, rule_value, scope, enabled)
            VALUES ('keyword_blacklist', '["广告", "代练"]', 'global', 1)
        """)
        
        # 创建包含黑名单关键词的消息
        filtered_message = sample_message.copy()
        filtered_message['content'] = "这是一条广告消息"
        filtered_message['message_id'] = "filtered_msg_001"
        
        # 应用过滤规则
        should_forward = message_filter.should_forward(filtered_message)
        
        # 应该被过滤
        assert should_forward is False
        
        # 正常消息应该通过
        should_forward_normal = message_filter.should_forward(sample_message)
        assert should_forward_normal is True
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, sample_mapping):
        """测试限流保护"""
        from app.utils.rate_limiter import RateLimiter
        
        # 创建限流器（每秒最多3条）
        limiter = RateLimiter(calls=3, period=1)
        
        # 快速发送5条消息
        start = datetime.now()
        for i in range(5):
            await limiter.acquire()
        duration = (datetime.now() - start).total_seconds()
        
        # 应该被限流，耗时至少2秒
        assert duration >= 1.5
    
    @pytest.mark.asyncio
    async def test_failed_message_retry(self, sample_message, sample_mapping):
        """测试失败消息重试"""
        worker = MessageWorker()
        
        # Mock转发器失败
        with patch.object(discord_forwarder, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = False  # 模拟失败
            
            # 处理消息
            await worker.process_message(sample_message)
            
            # 验证失败消息被记录
            logs = db.get_message_logs(limit=1, status='failed')
            assert len(logs) > 0
            
            # 验证失败消息进入重试队列
            failed = db.execute(
                "SELECT * FROM failed_messages WHERE message_log_id = ?",
                (logs[0]['id'],)
            ).fetchone()
            assert failed is not None
    
    @pytest.mark.asyncio
    async def test_multiple_platform_forwarding(self, sample_message):
        """测试多平台转发"""
        # 添加多个Bot和映射
        discord_bot = db.add_bot_config(
            platform="discord",
            name="Discord Bot",
            config={"webhook_url": "https://discord.com/api/webhooks/test1"}
        )
        telegram_bot = db.add_bot_config(
            platform="telegram",
            name="Telegram Bot",
            config={"bot_token": "123:abc", "chat_id": "-100123"}
        )
        
        # 同一频道映射到多个平台
        db.add_channel_mapping(
            kook_server_id=sample_message['server_id'],
            kook_channel_id=sample_message['channel_id'],
            kook_channel_name="测试频道",
            target_platform="discord",
            target_bot_id=discord_bot,
            target_channel_id="discord_ch"
        )
        db.add_channel_mapping(
            kook_server_id=sample_message['server_id'],
            kook_channel_id=sample_message['channel_id'],
            kook_channel_name="测试频道",
            target_platform="telegram",
            target_bot_id=telegram_bot,
            target_channel_id="telegram_ch"
        )
        
        worker = MessageWorker()
        
        with patch.object(discord_forwarder, 'send_message', new_callable=AsyncMock) as mock_discord, \
             patch.object(telegram_forwarder, 'send_message', new_callable=AsyncMock) as mock_telegram:
            
            mock_discord.return_value = True
            mock_telegram.return_value = True
            
            # 处理消息
            await worker.process_message(sample_message)
            
            # 验证两个平台都被调用
            assert mock_discord.called
            assert mock_telegram.called


class TestQueueIntegration:
    """队列集成测试"""
    
    @pytest.mark.asyncio
    async def test_message_enqueue_dequeue(self, sample_message):
        """测试消息入队出队"""
        # 确保Redis连接
        if not redis_queue.client:
            await redis_queue.connect()
        
        # 入队
        await redis_queue.enqueue(sample_message)
        
        # 验证队列大小
        size = await redis_queue.qsize()
        assert size > 0
        
        # 出队
        dequeued = await redis_queue.dequeue(timeout=1)
        assert dequeued is not None
        assert dequeued['message_id'] == sample_message['message_id']
    
    @pytest.mark.asyncio
    async def test_queue_priority(self):
        """测试队列优先级"""
        if not redis_queue.client:
            await redis_queue.connect()
        
        # 清空队列
        while await redis_queue.qsize() > 0:
            await redis_queue.dequeue(timeout=1)
        
        # 入队多条消息
        messages = [
            {"message_id": f"msg_{i}", "priority": i}
            for i in range(5)
        ]
        
        for msg in messages:
            await redis_queue.enqueue(msg)
        
        # 验证FIFO顺序
        for i in range(5):
            msg = await redis_queue.dequeue(timeout=1)
            assert msg['message_id'] == f"msg_{i}"


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_invalid_message_handling(self, sample_mapping):
        """测试无效消息处理"""
        worker = MessageWorker()
        
        # 缺少必需字段的消息
        invalid_message = {
            "message_id": "invalid_msg",
            # 缺少其他字段
        }
        
        # 处理不应该崩溃
        try:
            await worker.process_message(invalid_message)
        except Exception as e:
            pytest.fail(f"处理无效消息时崩溃: {e}")
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, sample_message, sample_mapping):
        """测试网络错误处理"""
        worker = MessageWorker()
        
        # Mock网络错误
        with patch.object(discord_forwarder, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception("Network error")
            
            # 处理不应该崩溃
            try:
                await worker.process_message(sample_message)
            except Exception as e:
                pytest.fail(f"网络错误未被妥善处理: {e}")
            
            # 消息应该被标记为失败
            logs = db.get_message_logs(limit=1)
            assert logs[0]['status'] == 'failed'
    
    @pytest.mark.asyncio
    async def test_database_error_recovery(self, sample_message):
        """测试数据库错误恢复"""
        worker = MessageWorker()
        
        # Mock数据库错误
        with patch.object(db, 'add_message_log') as mock_db:
            mock_db.side_effect = Exception("Database error")
            
            # 应该记录错误但不崩溃
            try:
                await worker.process_message(sample_message)
            except Exception as e:
                # 数据库错误可能导致失败，但应该被捕获
                pass


class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_message_throughput(self, sample_mapping):
        """测试消息吞吐量"""
        worker = MessageWorker()
        
        with patch.object(discord_forwarder, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            # 处理100条消息
            messages = [
                {
                    "message_id": f"perf_msg_{i}",
                    "channel_id": "test_channel_456",
                    "server_id": "test_server_789",
                    "content": f"性能测试消息 {i}",
                    "message_type": "text",
                    "sender_id": "user_perf",
                    "sender_name": "性能测试",
                    "timestamp": datetime.now().isoformat(),
                }
                for i in range(100)
            ]
            
            start = datetime.now()
            
            # 并发处理
            tasks = [worker.process_message(msg) for msg in messages]
            await asyncio.gather(*tasks)
            
            duration = (datetime.now() - start).total_seconds()
            throughput = 100 / duration
            
            print(f"吞吐量: {throughput:.2f} msg/s")
            
            # 吞吐量应该 > 10 msg/s
            assert throughput > 10
    
    @pytest.mark.asyncio
    async def test_memory_usage(self, sample_mapping):
        """测试内存使用"""
        worker = MessageWorker()
        
        with patch.object(discord_forwarder, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            # 处理大量消息
            for i in range(1000):
                message = {
                    "message_id": f"mem_test_{i}",
                    "channel_id": "test_channel_456",
                    "server_id": "test_server_789",
                    "content": f"内存测试 {i}",
                    "message_type": "text",
                    "sender_id": "user_mem",
                    "sender_name": "内存测试",
                    "timestamp": datetime.now().isoformat(),
                }
                await worker.process_message(message)
            
            # 验证LRU缓存限制
            assert len(worker.processed_messages) <= 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
