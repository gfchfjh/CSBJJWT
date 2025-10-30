"""
外部图床服务集成
✅ P0-30: SM.MS、阿里云OSS、七牛云存储
"""
import aiohttp
import asyncio
import base64
from typing import Optional, Tuple, Dict
from pathlib import Path
from ..utils.logger import logger
from ..config import settings


class ImageBedProvider:
    """图床服务提供商基类"""
    
    async def upload(self, image_data: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        上传图片
        
        Args:
            image_data: 图片数据
            filename: 文件名
            
        Returns:
            (是否成功, 图片URL, 错误信息)
        """
        raise NotImplementedError


class SmMsProvider(ImageBedProvider):
    """SM.MS图床"""
    
    def __init__(self, api_token: str = None):
        self.api_token = api_token or getattr(settings, 'smms_api_token', '')
        self.api_url = 'https://sm.ms/api/v2/upload'
        
    async def upload(self, image_data: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """上传图片到SM.MS"""
        try:
            headers = {}
            if self.api_token:
                headers['Authorization'] = self.api_token
            
            data = aiohttp.FormData()
            data.add_field('smfile', image_data, filename=filename, content_type='image/jpeg')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, data=data, timeout=30) as response:
                    result = await response.json()
                    
                    if result.get('success'):
                        image_url = result['data']['url']
                        logger.info(f"SM.MS上传成功: {image_url}")
                        return True, image_url, None
                    else:
                        error = result.get('message', '未知错误')
                        logger.error(f"SM.MS上传失败: {error}")
                        return False, None, error
                        
        except Exception as e:
            logger.error(f"SM.MS上传异常: {str(e)}")
            return False, None, str(e)


class AliyunOSSProvider(ImageBedProvider):
    """阿里云OSS"""
    
    def __init__(self):
        self.access_key_id = getattr(settings, 'aliyun_access_key_id', '')
        self.access_key_secret = getattr(settings, 'aliyun_access_key_secret', '')
        self.bucket = getattr(settings, 'aliyun_oss_bucket', '')
        self.endpoint = getattr(settings, 'aliyun_oss_endpoint', '')
        self.base_url = getattr(settings, 'aliyun_oss_base_url', '')
        
    async def upload(self, image_data: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """上传图片到阿里云OSS"""
        try:
            import oss2
            
            # 创建Bucket对象
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
            
            # 生成对象key
            object_key = f'images/{filename}'
            
            # 上传
            result = bucket.put_object(object_key, image_data)
            
            if result.status == 200:
                # 构建URL
                image_url = f"{self.base_url}/{object_key}"
                logger.info(f"阿里云OSS上传成功: {image_url}")
                return True, image_url, None
            else:
                error = f"上传失败，状态码: {result.status}"
                logger.error(f"阿里云OSS上传失败: {error}")
                return False, None, error
                
        except Exception as e:
            logger.error(f"阿里云OSS上传异常: {str(e)}")
            return False, None, str(e)


class QiniuProvider(ImageBedProvider):
    """七牛云存储"""
    
    def __init__(self):
        self.access_key = getattr(settings, 'qiniu_access_key', '')
        self.secret_key = getattr(settings, 'qiniu_secret_key', '')
        self.bucket = getattr(settings, 'qiniu_bucket', '')
        self.base_url = getattr(settings, 'qiniu_base_url', '')
        
    async def upload(self, image_data: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """上传图片到七牛云"""
        try:
            from qiniu import Auth, put_data
            
            # 生成上传凭证
            q = Auth(self.access_key, self.secret_key)
            token = q.upload_token(self.bucket, filename)
            
            # 上传
            ret, info = put_data(token, filename, image_data)
            
            if info.status_code == 200:
                # 构建URL
                image_url = f"{self.base_url}/{ret['key']}"
                logger.info(f"七牛云上传成功: {image_url}")
                return True, image_url, None
            else:
                error = f"上传失败，状态码: {info.status_code}"
                logger.error(f"七牛云上传失败: {error}")
                return False, None, error
                
        except Exception as e:
            logger.error(f"七牛云上传异常: {str(e)}")
            return False, None, str(e)


class ExternalImageBed:
    """外部图床管理器"""
    
    def __init__(self):
        self.provider_type = getattr(settings, 'image_bed_provider', 'smms')
        self.provider = self._create_provider()
        
        # 统计
        self.stats = {
            'total_uploaded': 0,
            'success': 0,
            'failed': 0
        }
        
    def _create_provider(self) -> ImageBedProvider:
        """创建图床提供商"""
        if self.provider_type == 'smms':
            return SmMsProvider()
        elif self.provider_type == 'aliyun':
            return AliyunOSSProvider()
        elif self.provider_type == 'qiniu':
            return QiniuProvider()
        else:
            logger.warning(f"未知的图床提供商: {self.provider_type}，使用SM.MS")
            return SmMsProvider()
    
    async def upload(self, image_data: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        上传图片
        
        Args:
            image_data: 图片数据
            filename: 文件名
            
        Returns:
            (是否成功, 图片URL, 错误信息)
        """
        self.stats['total_uploaded'] += 1
        
        try:
            success, url, error = await self.provider.upload(image_data, filename)
            
            if success:
                self.stats['success'] += 1
            else:
                self.stats['failed'] += 1
            
            return success, url, error
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"图片上传失败: {str(e)}")
            return False, None, str(e)
    
    async def upload_from_file(self, filepath: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """从文件上传"""
        try:
            with open(filepath, 'rb') as f:
                image_data = f.read()
            
            return await self.upload(image_data, filepath.name)
            
        except Exception as e:
            logger.error(f"读取文件失败: {str(e)}")
            return False, None, str(e)
    
    async def upload_from_url(self, url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """从URL上传"""
        try:
            # 下载图片
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # 生成文件名
                        import hashlib
                        filename = hashlib.md5(url.encode()).hexdigest() + '.jpg'
                        
                        return await self.upload(image_data, filename)
                    else:
                        return False, None, f"下载失败，状态码: {response.status}"
                        
        except Exception as e:
            logger.error(f"从URL上传失败: {str(e)}")
            return False, None, str(e)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'provider': self.provider_type,
            'success_rate': self.stats['success'] / self.stats['total_uploaded'] * 100 if self.stats['total_uploaded'] > 0 else 0
        }
    
    def switch_provider(self, provider_type: str):
        """切换图床提供商"""
        self.provider_type = provider_type
        self.provider = self._create_provider()
        logger.info(f"已切换到图床: {provider_type}")


# 全局实例
external_image_bed = ExternalImageBed()
