"""
图片处理器测试
"""
import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from PIL import Image
from io import BytesIO
from backend.app.processors.image import ImageProcessor


@pytest.fixture
def image_processor():
    """创建图片处理器（使用临时目录）"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    processor = ImageProcessor()
    processor.storage_path = Path(temp_dir)
    processor.storage_path.mkdir(parents=True, exist_ok=True)
    
    yield processor
    
    # 清理临时目录
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_image_data():
    """生成示例图片数据"""
    # 创建一个简单的测试图片（100x100红色方块）
    img = Image.new('RGB', (100, 100), color='red')
    
    output = BytesIO()
    img.save(output, format='JPEG', quality=90)
    data = output.getvalue()
    
    return data


@pytest.fixture
def large_image_data():
    """生成大尺寸图片（用于测试压缩）"""
    # 创建一个大图片（2000x2000）
    img = Image.new('RGB', (2000, 2000), color='blue')
    
    output = BytesIO()
    img.save(output, format='JPEG', quality=95)
    data = output.getvalue()
    
    return data


class TestImageProcessor:
    """图片处理器测试类"""
    
    def test_compress_small_image(self, image_processor, sample_image_data):
        """测试压缩小图片（不应该压缩）"""
        original_size = len(sample_image_data) / (1024 * 1024)
        
        # 压缩图片（最大10MB）
        compressed = image_processor.compress_image(sample_image_data, max_size_mb=10.0)
        
        # 小图片不应该被压缩
        assert compressed == sample_image_data
    
    def test_compress_large_image(self, image_processor, large_image_data):
        """测试压缩大图片"""
        original_size_mb = len(large_image_data) / (1024 * 1024)
        
        # 压缩到1MB以下
        compressed = image_processor.compress_image(large_image_data, max_size_mb=1.0)
        compressed_size_mb = len(compressed) / (1024 * 1024)
        
        # 应该被压缩了
        assert compressed_size_mb < original_size_mb
        
        # 验证压缩后的图片可以正常打开
        img = Image.open(BytesIO(compressed))
        assert img.size == (2000, 2000)
    
    def test_compress_rgba_image(self, image_processor):
        """测试压缩RGBA图片（应转换为RGB）"""
        # 创建RGBA图片（带透明通道）
        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        
        output = BytesIO()
        img.save(output, format='PNG')
        rgba_data = output.getvalue()
        
        # 压缩（会转换为RGB）
        compressed = image_processor.compress_image(rgba_data)
        
        # 验证转换成功
        compressed_img = Image.open(BytesIO(compressed))
        assert compressed_img.mode == 'RGB'
    
    def test_save_to_local(self, image_processor, sample_image_data):
        """测试保存图片到本地"""
        # 保存图片
        filepath = image_processor.save_to_local(sample_image_data)
        
        # 验证文件存在
        assert os.path.exists(filepath)
        
        # 验证文件内容
        with open(filepath, 'rb') as f:
            saved_data = f.read()
        
        assert saved_data == sample_image_data
    
    def test_save_with_custom_filename(self, image_processor, sample_image_data):
        """测试使用自定义文件名保存"""
        custom_name = "test_image.jpg"
        
        filepath = image_processor.save_to_local(sample_image_data, filename=custom_name)
        
        # 验证文件名正确
        assert Path(filepath).name == custom_name
    
    def test_generate_url(self, image_processor, sample_image_data):
        """测试生成访问URL"""
        # 保存图片
        filepath = image_processor.save_to_local(sample_image_data)
        
        # 生成URL
        url = image_processor.generate_url(filepath, expire_hours=2)
        
        # 验证URL格式
        assert 'http://localhost:' in url
        assert '/images/' in url
        assert 'token=' in url
        
        # 验证Token已保存
        assert filepath in image_processor.url_tokens
    
    def test_verify_token_valid(self, image_processor, sample_image_data):
        """测试验证有效Token"""
        filepath = image_processor.save_to_local(sample_image_data)
        url = image_processor.generate_url(filepath, expire_hours=2)
        
        # 提取Token
        token = url.split('token=')[1]
        
        # 验证Token
        assert image_processor.verify_token(filepath, token) is True
    
    def test_verify_token_invalid(self, image_processor, sample_image_data):
        """测试验证无效Token"""
        filepath = image_processor.save_to_local(sample_image_data)
        image_processor.generate_url(filepath, expire_hours=2)
        
        # 使用错误的Token
        assert image_processor.verify_token(filepath, 'invalid_token') is False
    
    def test_verify_token_expired(self, image_processor, sample_image_data):
        """测试验证过期Token"""
        import time
        
        filepath = image_processor.save_to_local(sample_image_data)
        
        # 生成短时效Token（0.001小时 = 3.6秒）
        url = image_processor.generate_url(filepath, expire_hours=0.001)
        token = url.split('token=')[1]
        
        # 等待Token过期
        time.sleep(4)
        
        # 验证Token（应该过期）
        assert image_processor.verify_token(filepath, token) is False
    
    def test_cleanup_expired_tokens(self, image_processor, sample_image_data):
        """测试清理过期Token"""
        import time
        
        # 生成多个Token，其中一些已过期
        filepath1 = image_processor.save_to_local(sample_image_data, 'img1.jpg')
        filepath2 = image_processor.save_to_local(sample_image_data, 'img2.jpg')
        
        # 生成短时效Token
        image_processor.generate_url(filepath1, expire_hours=0.001)
        # 生成长时效Token
        image_processor.generate_url(filepath2, expire_hours=10)
        
        # 等待第一个Token过期
        time.sleep(4)
        
        # 清理过期Token
        cleaned = image_processor.cleanup_expired_tokens()
        
        # 应该清理了1个
        assert cleaned == 1
        
        # 验证剩余Token
        assert filepath1 not in image_processor.url_tokens
        assert filepath2 in image_processor.url_tokens
    
    def test_get_token_stats(self, image_processor, sample_image_data):
        """测试获取Token统计"""
        # 生成多个Token
        for i in range(5):
            filepath = image_processor.save_to_local(sample_image_data, f'img{i}.jpg')
            image_processor.generate_url(filepath, expire_hours=2)
        
        # 获取统计
        stats = image_processor.get_token_stats()
        
        assert stats['total_tokens'] == 5
        assert stats['valid_tokens'] == 5
        assert stats['expired_tokens'] == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_old_images(self, image_processor, sample_image_data):
        """测试清理旧图片"""
        import time
        
        # 保存多个图片
        filepath1 = image_processor.save_to_local(sample_image_data, 'old.jpg')
        
        # 修改文件时间（模拟旧文件）
        old_time = time.time() - (8 * 24 * 3600)  # 8天前
        os.utime(filepath1, (old_time, old_time))
        
        # 保存新文件
        filepath2 = image_processor.save_to_local(sample_image_data, 'new.jpg')
        
        # 清理7天前的图片
        await image_processor.cleanup_old_images(days=7)
        
        # 验证旧文件被删除
        assert not os.path.exists(filepath1)
        
        # 验证新文件保留
        assert os.path.exists(filepath2)
    
    def test_get_storage_size(self, image_processor, sample_image_data):
        """测试获取存储空间"""
        # 初始应该为0
        initial_size = image_processor.get_storage_size()
        assert initial_size == 0.0
        
        # 保存几个文件
        for i in range(3):
            image_processor.save_to_local(sample_image_data, f'test{i}.jpg')
        
        # 获取存储大小
        storage_size = image_processor.get_storage_size()
        
        # 应该大于0
        assert storage_size > 0.0
        
        # 应该约等于 3 * 文件大小
        expected_size_gb = (len(sample_image_data) * 3) / (1024 ** 3)
        assert abs(storage_size - expected_size_gb) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
