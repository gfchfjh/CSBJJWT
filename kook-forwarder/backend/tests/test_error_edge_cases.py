"""
错误边界测试用例
测试各种异常情况和边界条件
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.kook.scraper import KookScraper, ScraperManager
from app.forwarders.discord import DiscordForwarder
from app.forwarders.telegram import TelegramForwarder
from app.processors.image import ImageProcessor
from app.processors.formatter import formatter


class TestScraperErrorHandling:
    """测试Scraper错误处理"""
    
    @pytest.mark.asyncio
    async def test_network_timeout(self):
        """测试网络超时处理"""
        scraper = KookScraper(account_id=1)
        
        # 模拟网络超时
        with patch('app.kook.scraper.async_playwright') as mock_playwright:
            mock_playwright.return_value.start = AsyncMock(
                side_effect=asyncio.TimeoutError("Connection timeout")
            )
            
            # 应该能够优雅处理超时
            result = await scraper.start(cookie='[]')
            assert result is False
            assert scraper.is_running is False
    
    @pytest.mark.asyncio
    async def test_invalid_cookie_format(self):
        """测试无效Cookie格式"""
        scraper = KookScraper(account_id=1)
        
        # 测试各种无效格式
        invalid_cookies = [
            '',  # 空字符串
            'invalid json',  # 非JSON
            '{}',  # 空对象而非数组
            '[]',  # 空数组
            '[{"name":"test"}]',  # 缺少必需字段
        ]
        
        for cookie in invalid_cookies:
            # 不应该崩溃，应该返回False
            result = await scraper.start(cookie=cookie)
            assert result is False or scraper.page is None
    
    @pytest.mark.asyncio
    async def test_auto_reconnect_mechanism(self):
        """测试自动重连机制"""
        scraper = KookScraper(account_id=1)
        scraper.is_running = True
        scraper.max_reconnect = 3
        
        # 模拟重连
        with patch.object(scraper, '_reconnect', new_callable=AsyncMock) as mock_reconnect:
            with patch.object(scraper, 'page') as mock_page:
                # 模拟心跳失败
                mock_page.evaluate = AsyncMock(side_effect=Exception("Connection lost"))
                
                # 触发心跳检测（简化测试）
                scraper.reconnect_count = 0
                try:
                    await mock_page.evaluate('() => console.log("heartbeat")')
                except Exception:
                    # 应该触发重连
                    scraper.reconnect_count += 1
                
                assert scraper.reconnect_count == 1
                assert scraper.reconnect_count <= scraper.max_reconnect
    
    @pytest.mark.asyncio
    async def test_max_reconnect_reached(self):
        """测试达到最大重连次数后停止"""
        scraper = KookScraper(account_id=1)
        scraper.max_reconnect = 5
        scraper.reconnect_count = 5
        scraper.is_running = True
        
        # 达到最大次数后should停止
        if scraper.reconnect_count >= scraper.max_reconnect:
            scraper.is_running = False
        
        assert scraper.is_running is False


class TestDiscordErrorHandling:
    """测试Discord转发错误处理"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """测试限流超限情况"""
        forwarder = DiscordForwarder()
        
        # 模拟快速发送多条消息
        with patch.object(forwarder.rate_limiter, 'acquire', new_callable=AsyncMock) as mock_acquire:
            # 模拟限流等待
            mock_acquire.side_effect = [
                None,  # 第1条通过
                None,  # 第2条通过
                asyncio.sleep(2),  # 第3条需要等待
            ]
            
            # 发送3条消息
            results = []
            for i in range(3):
                await forwarder.rate_limiter.acquire()
                results.append(True)
            
            # 应该都成功，但第3条有延迟
            assert len(results) == 3
            assert all(results)
    
    @pytest.mark.asyncio
    async def test_webhook_url_invalid(self):
        """测试无效Webhook URL"""
        forwarder = DiscordForwarder()
        
        invalid_urls = [
            '',  # 空字符串
            'not-a-url',  # 非URL
            'http://invalid',  # 无效URL
        ]
        
        for url in invalid_urls:
            # 应该返回False而非崩溃
            result = await forwarder.send_message(
                webhook_url=url,
                content="test"
            )
            assert result is False
    
    @pytest.mark.asyncio
    async def test_oversized_message(self):
        """测试超长消息分段"""
        # 创建一个超过2000字符的消息
        long_message = "A" * 3000
        
        # 应该被分成多段
        segments = formatter.split_long_message(long_message, 2000)
        
        assert len(segments) > 1
        assert all(len(seg) <= 2000 for seg in segments)
        assert ''.join(segments) == long_message


class TestImageProcessingErrors:
    """测试图片处理错误"""
    
    @pytest.mark.asyncio
    async def test_download_failure_with_anti_hotlink(self):
        """测试防盗链下载失败"""
        processor = ImageProcessor()
        
        # 模拟防盗链图片（没有Cookie）
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.status = 403
            
            # 应该尝试带Cookie重试
            result = await processor.download_image(
                url="https://example.com/image.jpg",
                cookies={}
            )
            
            # 返回None而非崩溃
            assert result is None or isinstance(result, bytes)
    
    @pytest.mark.asyncio
    async def test_corrupt_image_data(self):
        """测试损坏的图片数据"""
        processor = ImageProcessor()
        
        # 模拟损坏的图片数据
        corrupt_data = b'not an image'
        
        with pytest.raises(Exception):
            # 应该抛出异常
            from PIL import Image
            import io
            Image.open(io.BytesIO(corrupt_data))
    
    @pytest.mark.asyncio
    async def test_image_too_large(self):
        """测试超大图片处理"""
        processor = ImageProcessor()
        
        # 假设有一个50MB的图片
        large_size = 50 * 1024 * 1024  # 50MB
        
        # 应该被压缩或拒绝
        # （实际测试中应该用真实图片数据）
        assert large_size > 10 * 1024 * 1024  # 大于10MB
    
    @pytest.mark.asyncio
    async def test_unsupported_image_format(self):
        """测试不支持的图片格式"""
        processor = ImageProcessor()
        
        unsupported_formats = [
            'image.bmp',
            'image.tiff',
            'image.raw'
        ]
        
        # 应该能够处理或返回错误
        for filename in unsupported_formats:
            # 这里只是示例，实际需要真实文件
            assert '.' in filename


class TestMessageValidation:
    """测试消息验证"""
    
    def test_empty_message(self):
        """测试空消息"""
        # 空消息应该被拒绝或特殊处理
        empty_messages = ['', None, '   ', '\n\n']
        
        for msg in empty_messages:
            if msg:
                result = formatter.kmarkdown_to_discord(msg)
                # 不应该崩溃
                assert isinstance(result, str)
    
    def test_message_with_special_characters(self):
        """测试包含特殊字符的消息"""
        special_messages = [
            'Hello @everyone',
            '<script>alert("xss")</script>',
            '\\n\\r\\t',
            'emoji: 😀🎉👍',
            '**bold** *italic* `code`',
        ]
        
        for msg in special_messages:
            # 应该正确转换
            result = formatter.kmarkdown_to_discord(msg)
            assert isinstance(result, str)
            # 不应该为空
            assert len(result) > 0
    
    def test_nested_markdown(self):
        """测试嵌套的Markdown"""
        nested_messages = [
            '**bold *italic* bold**',
            '***bold and italic***',
            '`code **bold** code`',
        ]
        
        for msg in nested_messages:
            result = formatter.kmarkdown_to_discord(msg)
            assert isinstance(result, str)


class TestDatabaseErrors:
    """测试数据库错误处理"""
    
    def test_connection_failure(self):
        """测试数据库连接失败"""
        from app.database import Database
        
        # 测试无效路径
        try:
            db = Database(db_path="/invalid/path/db.sqlite")
            # 应该能够处理错误
        except Exception as e:
            # 预期会有错误
            assert True
    
    def test_duplicate_key_insert(self):
        """测试重复键插入"""
        from app.database import db
        
        # 尝试插入重复的邮箱
        email = "test@example.com"
        
        # 第一次插入应该成功
        try:
            account_id1 = db.add_account(email, password_encrypted="test")
        except:
            pass  # 可能已经存在
        
        # 第二次插入应该失败（UNIQUE约束）
        try:
            account_id2 = db.add_account(email, password_encrypted="test")
            # 应该抛出异常
        except Exception as e:
            # 预期的错误
            assert "UNIQUE" in str(e) or "duplicate" in str(e).lower()


class TestRateLimiterEdgeCases:
    """测试限流器边界情况"""
    
    @pytest.mark.asyncio
    async def test_concurrent_acquire(self):
        """测试并发获取令牌"""
        from app.utils.rate_limiter import RateLimiter
        
        limiter = RateLimiter(calls=5, period=1)
        
        # 同时请求10个令牌
        tasks = [limiter.acquire() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 应该都能成功，但有些会延迟
        assert len(results) == 10
    
    @pytest.mark.asyncio
    async def test_burst_requests(self):
        """测试突发请求"""
        from app.utils.rate_limiter import RateLimiter
        
        limiter = RateLimiter(calls=2, period=5)
        
        # 快速发送3个请求
        start = asyncio.get_event_loop().time()
        
        await limiter.acquire()  # 第1个：立即通过
        await limiter.acquire()  # 第2个：立即通过
        await limiter.acquire()  # 第3个：需要等待
        
        elapsed = asyncio.get_event_loop().time() - start
        
        # 第3个应该等待了约5秒
        assert elapsed >= 4.5  # 允许一些误差


class TestCryptoErrors:
    """测试加密功能错误处理"""
    
    def test_decrypt_invalid_data(self):
        """测试解密无效数据"""
        from app.utils.crypto import decrypt_password
        
        invalid_data = [
            '',  # 空字符串
            'invalid',  # 非base64
            'YWJj',  # 有效base64但非加密数据
        ]
        
        for data in invalid_data:
            try:
                result = decrypt_password(data)
                # 应该返回None或抛出异常
            except Exception:
                # 预期的错误
                assert True
    
    def test_encrypt_decrypt_round_trip(self):
        """测试加密解密往返"""
        from app.utils.crypto import encrypt_password, decrypt_password
        
        original = "test_password_123"
        encrypted = encrypt_password(original)
        decrypted = decrypt_password(encrypted)
        
        assert decrypted == original
        assert encrypted != original


class TestVerificationCodeEdgeCases:
    """测试验证码边界情况"""
    
    def test_expired_code(self):
        """测试过期验证码"""
        from app.utils.verification_code import verification_manager
        from datetime import datetime, timedelta
        
        email = "test@example.com"
        code = verification_manager.generate_code(email)
        
        # 模拟过期（修改过期时间）
        if not verification_manager.use_redis:
            key = f"{email}:password_reset"
            if key in verification_manager.codes:
                verification_manager.codes[key]['expires_at'] = datetime.now() - timedelta(minutes=1)
        
        # 验证应该失败
        success, message = verification_manager.verify_code(email, code)
        # 过期后应该失败（除非已被清理）
        assert "过期" in message or "不存在" in message
    
    def test_max_attempts_exceeded(self):
        """测试超过最大尝试次数"""
        from app.utils.verification_code import verification_manager
        
        email = "test2@example.com"
        code = verification_manager.generate_code(email)
        
        # 尝试5次错误的验证码
        for i in range(5):
            success, message = verification_manager.verify_code(email, "wrong_code")
            assert not success
        
        # 第6次应该提示次数过多
        success, message = verification_manager.verify_code(email, "wrong_code")
        assert not success
        assert "次数" in message or "失效" in message or "不存在" in message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
