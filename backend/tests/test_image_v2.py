"""
图片处理模块v2测试
版本: v6.0.0
"""

import pytest
import asyncio
from io import BytesIO
from PIL import Image
from app.processors.image_v2 import ImageProcessorV2, LRUTokenCache


class TestLRUTokenCache:
    """LRU Token缓存测试"""
    
    def test_basic_operations(self):
        """测试基础操作"""
        cache = LRUTokenCache(max_size=3, ttl=3600)
        
        # 设置Token
        cache.set('/path/1', 'token1')
        cache.set('/path/2', 'token2')
        cache.set('/path/3', 'token3')
        
        # 获取Token
        assert cache.get('/path/1')['token'] == 'token1'
        assert cache.get('/path/2')['token'] == 'token2'
        assert cache.get('/path/3')['token'] == 'token3'
    
    def test_lru_eviction(self):
        """测试LRU淘汰"""
        cache = LRUTokenCache(max_size=3, ttl=3600)
        
        cache.set('/path/1', 'token1')
        cache.set('/path/2', 'token2')
        cache.set('/path/3', 'token3')
        
        # 访问path1（移到末尾）
        cache.get('/path/1')
        
        # 添加新Token，应该淘汰path2（最久未使用）
        cache.set('/path/4', 'token4')
        
        assert cache.get('/path/1') is not None  # 仍存在
        assert cache.get('/path/2') is None      # 已淘汰
        assert cache.get('/path/3') is not None  # 仍存在
        assert cache.get('/path/4') is not None  # 新添加
    
    def test_expiration(self):
        """测试过期"""
        import time
        cache = LRUTokenCache(max_size=10, ttl=1)  # 1秒过期
        
        cache.set('/path/1', 'token1')
        
        # 立即获取，应该存在
        assert cache.get('/path/1') is not None
        
        # 等待过期
        time.sleep(1.1)
        
        # 再次获取，应该None
        assert cache.get('/path/1') is None
    
    def test_stats(self):
        """测试统计信息"""
        cache = LRUTokenCache(max_size=10, ttl=3600)
        
        cache.set('/path/1', 'token1')
        cache.get('/path/1')  # 命中
        cache.get('/path/2')  # 未命中
        
        stats = cache.get_stats()
        
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['cache_size'] == 1


class TestImageProcessorV2:
    """图片处理器v2测试"""
    
    @pytest.fixture
    def processor(self):
        """图片处理器fixture"""
        return ImageProcessorV2()
    
    @pytest.fixture
    def test_image_small(self):
        """小测试图片（100KB）"""
        img = Image.new('RGB', (800, 600), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        return buffer.getvalue()
    
    @pytest.fixture
    def test_image_large(self):
        """大测试图片（5MB）"""
        img = Image.new('RGB', (4000, 3000), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        return buffer.getvalue()
    
    def test_detect_format_jpeg(self):
        """测试JPEG格式检测"""
        img = Image.new('RGB', (100, 100))
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        
        format_type = ImageProcessorV2._detect_format(buffer.getvalue())
        assert format_type == 'JPEG'
    
    def test_detect_format_png(self):
        """测试PNG格式检测"""
        img = Image.new('RGB', (100, 100))
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        format_type = ImageProcessorV2._detect_format(buffer.getvalue())
        assert format_type == 'PNG'
    
    def test_detect_format_webp(self):
        """测试WEBP格式检测"""
        img = Image.new('RGB', (100, 100))
        buffer = BytesIO()
        img.save(buffer, format='WEBP')
        
        format_type = ImageProcessorV2._detect_format(buffer.getvalue())
        assert format_type == 'WEBP'
    
    @pytest.mark.asyncio
    async def test_compress_small_image(self, processor, test_image_small):
        """测试小图片压缩（应使用线程池）"""
        compressed, stats = await processor.compress_image(
            test_image_small,
            max_size_mb=5.0,
            quality=85,
            target_platform='discord'
        )
        
        assert len(compressed) > 0
        assert stats['process_time_ms'] < 500  # 应该<500ms
        assert processor.stats['thread_pool_used'] > 0
    
    @pytest.mark.asyncio
    async def test_compress_large_image(self, processor, test_image_large):
        """测试大图片压缩（应使用进程池）"""
        compressed, stats = await processor.compress_image(
            test_image_large,
            max_size_mb=3.0,
            quality=85,
            target_platform='telegram'
        )
        
        assert len(compressed) > 0
        compressed_size_mb = len(compressed) / (1024 * 1024)
        assert compressed_size_mb <= 3.0  # 应该被压缩到3MB以下
        assert processor.stats['process_pool_used'] > 0
    
    @pytest.mark.asyncio
    async def test_format_conversion(self, processor):
        """测试格式转换"""
        # 创建PNG图片
        img = Image.new('RGB', (1000, 1000), color='green')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        png_data = buffer.getvalue()
        
        # 转换为JPEG
        compressed, stats = await processor.compress_image(
            png_data,
            max_size_mb=10.0,
            quality=85,
            target_platform='telegram'  # Telegram推荐JPEG
        )
        
        # 验证已转换为JPEG
        assert stats['original_format'] == 'PNG'
        assert stats['target_format'] == 'JPEG'
        assert stats['format_converted'] == True
    
    @pytest.mark.asyncio
    async def test_resize_large_image(self, processor):
        """测试超大图片缩放"""
        # 创建超大图片（>4096px）
        img = Image.new('RGB', (5000, 4000), color='yellow')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        large_data = buffer.getvalue()
        
        compressed, stats = await processor.compress_image(
            large_data,
            max_size_mb=5.0,
            quality=85
        )
        
        # 验证已缩放
        assert stats['resized'] == True
        
        # 验证缩放后尺寸
        compressed_img = Image.open(BytesIO(compressed))
        assert max(compressed_img.size) <= 4096
    
    @pytest.mark.asyncio
    async def test_performance_small_image(self, processor, test_image_small):
        """测试小图片性能（目标<200ms）"""
        compressed, stats = await processor.compress_image(test_image_small)
        
        assert stats['process_time_ms'] < 200
    
    @pytest.mark.asyncio
    async def test_performance_medium_image(self, processor):
        """测试中等图片性能（目标<500ms）"""
        img = Image.new('RGB', (2000, 1500))
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        image_data = buffer.getvalue()
        
        compressed, stats = await processor.compress_image(image_data)
        
        assert stats['process_time_ms'] < 500
    
    def test_token_generation(self, processor):
        """测试Token生成"""
        token1 = processor._generate_token('/path/test.jpg')
        token2 = processor._generate_token('/path/test.jpg')
        
        # 每次生成应该不同（包含随机数）
        assert token1 != token2
        
        # 长度应该是32
        assert len(token1) == 32
        assert len(token2) == 32
    
    def test_token_verification(self, processor):
        """测试Token验证"""
        filepath = '/path/test.jpg'
        token = processor._generate_token(filepath)
        
        # 添加到缓存
        processor.token_cache.set(filepath, token)
        
        # 验证应该通过
        assert processor.verify_token(filepath, token) == True
        
        # 错误Token应该失败
        assert processor.verify_token(filepath, 'wrong_token') == False
        
        # 不存在的路径应该失败
        assert processor.verify_token('/path/not_exist.jpg', token) == False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
