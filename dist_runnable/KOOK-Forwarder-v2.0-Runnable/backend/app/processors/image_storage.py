"""
图片存储管理模块
从image.py拆分出来，专注于图片存储、Token管理和清理
"""
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional
from ..config import settings
from ..utils.structured_logger import logger
from ..utils.metrics import metrics


class ImageStorage:
    """图片存储管理器"""
    
    def __init__(self):
        # 图片存储目录
        self.storage_path = Path(settings.data_dir) / "images"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Token映射（文件路径 -> Token信息）
        self.url_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Token有效期（默认2小时）
        self.token_ttl = 7200
    
    def save_to_local(self, image_data: bytes, filename: Optional[str] = None) -> str:
        """
        保存图片到本地
        
        Args:
            image_data: 图片数据
            filename: 文件名（可选，默认使用hash）
            
        Returns:
            文件路径
        """
        try:
            # 生成文件名（使用MD5 hash）
            if not filename:
                file_hash = hashlib.md5(image_data).hexdigest()
                filename = f"{file_hash}.jpg"
            
            # 保存文件
            filepath = self.storage_path / filename
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"图片保存成功: {filepath}")
            
            # 更新存储大小指标
            self._update_storage_metrics()
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"图片保存失败: {str(e)}")
            raise
    
    def generate_url(self, filepath: str, expire_hours: int = 2) -> str:
        """
        生成图片访问URL（带Token）
        
        Args:
            filepath: 文件路径
            expire_hours: 过期时间（小时）
            
        Returns:
            访问URL
        """
        # 生成随机Token
        token = hashlib.sha256(f"{filepath}{time.time()}".encode()).hexdigest()[:16]
        
        # 保存Token映射
        self.url_tokens[filepath] = {
            'token': token,
            'expire_at': time.time() + (expire_hours * 3600)
        }
        
        # 生成URL
        filename = Path(filepath).name
        url = f"http://localhost:{settings.image_server_port}/images/{filename}?token={token}"
        
        metrics.record_image_operation('generate_url', 'success')
        
        return url
    
    def verify_token(self, filepath: str, token: str) -> bool:
        """
        验证Token是否有效
        
        Args:
            filepath: 文件路径
            token: Token字符串
            
        Returns:
            是否有效
        """
        if filepath not in self.url_tokens:
            return False
        
        token_info = self.url_tokens[filepath]
        
        # 检查Token是否匹配
        if token_info['token'] != token:
            logger.warning(f"Token不匹配: {filepath}")
            return False
        
        # 检查是否过期
        if time.time() > token_info['expire_at']:
            logger.info(f"Token已过期: {filepath}")
            del self.url_tokens[filepath]
            return False
        
        return True
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        获取详细的存储信息
        
        Returns:
            存储信息字典
        """
        total_size = 0
        file_count = 0
        oldest_file_time = None
        newest_file_time = None
        
        for filepath in self.storage_path.glob("*.jpg"):
            stat = filepath.stat()
            total_size += stat.st_size
            file_count += 1
            
            # 记录最旧和最新文件时间
            if oldest_file_time is None or stat.st_mtime < oldest_file_time:
                oldest_file_time = stat.st_mtime
            if newest_file_time is None or stat.st_mtime > newest_file_time:
                newest_file_time = stat.st_mtime
        
        size_gb = total_size / (1024 ** 3)
        max_size_gb = settings.image_max_size_gb
        usage_percent = (size_gb / max_size_gb * 100) if max_size_gb > 0 else 0
        
        return {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'total_size_gb': size_gb,
            'file_count': file_count,
            'max_size_gb': max_size_gb,
            'usage_percent': round(usage_percent, 2),
            'is_full': size_gb >= max_size_gb,
            'oldest_file_time': oldest_file_time,
            'newest_file_time': newest_file_time,
            'storage_path': str(self.storage_path)
        }
    
    def _update_storage_metrics(self):
        """更新Prometheus存储指标"""
        try:
            info = self.get_storage_info()
            metrics.update_image_storage_size(info['total_size_bytes'])
        except:
            pass
    
    async def cleanup_old_images(self, days: int = 7) -> Dict[str, Any]:
        """
        清理旧图片
        
        Args:
            days: 保留天数
            
        Returns:
            清理统计信息
        """
        try:
            current_time = time.time()
            deleted_count = 0
            freed_space = 0
            
            for filepath in self.storage_path.glob("*.jpg"):
                # 检查文件修改时间
                mtime = filepath.stat().st_mtime
                age_days = (current_time - mtime) / (24 * 3600)
                
                if age_days > days:
                    # 获取文件大小
                    file_size = filepath.stat().st_size
                    
                    # 删除文件
                    filepath.unlink()
                    deleted_count += 1
                    freed_space += file_size
                    
                    # 删除Token映射
                    filepath_str = str(filepath)
                    if filepath_str in self.url_tokens:
                        del self.url_tokens[filepath_str]
            
            freed_mb = freed_space / (1024 * 1024)
            logger.info(f"清理旧图片完成: 删除 {deleted_count} 个文件, 释放 {freed_mb:.2f}MB 空间")
            
            # 更新指标
            self._update_storage_metrics()
            
            return {
                'deleted_count': deleted_count,
                'freed_space_mb': freed_mb,
                'freed_space_gb': freed_mb / 1024
            }
            
        except Exception as e:
            logger.error(f"清理旧图片失败: {str(e)}")
            return {
                'deleted_count': 0,
                'freed_space_mb': 0,
                'freed_space_gb': 0,
                'error': str(e)
            }
    
    async def cleanup_expired_tokens(self):
        """清理过期Token（后台任务）"""
        current_time = time.time()
        expired_keys = []
        
        for filepath, token_info in list(self.url_tokens.items()):
            if token_info['expire_at'] < current_time:
                expired_keys.append(filepath)
        
        for key in expired_keys:
            del self.url_tokens[key]
        
        if expired_keys:
            logger.info(f"🧹 清理了 {len(expired_keys)} 个过期Token，剩余 {len(self.url_tokens)} 个有效Token")
    
    def get_token_stats(self) -> Dict[str, Any]:
        """获取Token统计信息"""
        current_time = time.time()
        total_tokens = len(self.url_tokens)
        expired_tokens = 0
        valid_tokens = 0
        
        for token_info in self.url_tokens.values():
            if current_time > token_info['expire_at']:
                expired_tokens += 1
            else:
                valid_tokens += 1
        
        return {
            'total_tokens': total_tokens,
            'valid_tokens': valid_tokens,
            'expired_tokens': expired_tokens
        }


# 创建全局存储管理器实例
storage = ImageStorage()
