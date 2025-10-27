"""
文件附件处理器
✅ P0-4优化：支持文件附件转发
"""
import aiohttp
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
from ..config import settings
from ..utils.logger import logger


class FileProcessor:
    """文件附件处理器"""
    
    # 文件大小限制（50MB）
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    # 允许的文件类型
    ALLOWED_TYPES = [
        # 文档
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.txt', '.md', '.csv',
        # 压缩文件
        '.zip', '.rar', '.7z', '.tar', '.gz',
        # 图片（补充）
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
        # 音频
        '.mp3', '.wav', '.flac', '.m4a', '.ogg',
        # 视频（小文件）
        '.mp4', '.avi', '.mkv', '.mov', '.flv',
        # 代码
        '.py', '.js', '.java', '.cpp', '.c', '.go', '.rs',
        '.html', '.css', '.json', '.xml', '.yaml', '.yml',
        # 其他
        '.log', '.sql', '.ini', '.conf', '.config'
    ]
    
    # 危险文件类型（不允许）
    DANGEROUS_TYPES = [
        '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js',
        '.jar', '.msi', '.dll', '.sys', '.sh', '.bash'
    ]
    
    def __init__(self):
        self.temp_dir = Path(settings.data_dir) / "temp_files"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_file(self, url: str, cookies: Dict, 
                           referer: Optional[str] = None) -> Optional[Dict]:
        """
        下载文件附件
        
        Args:
            url: 文件URL
            cookies: Cookie字典
            referer: Referer头
            
        Returns:
            {
                "data": bytes,
                "filename": str,
                "size": int,
                "content_type": str
            }
        """
        try:
            # 先获取文件信息（HEAD请求）
            file_info = await self._get_file_info(url, cookies, referer)
            
            if not file_info:
                logger.error(f"无法获取文件信息: {url}")
                return None
            
            # 检查文件大小
            if file_info['size'] > self.MAX_FILE_SIZE:
                logger.error(f"文件过大: {file_info['size']/1024/1024:.1f}MB > {self.MAX_FILE_SIZE/1024/1024}MB")
                return None
            
            # 验证文件类型
            if not self.validate_file_type(file_info['filename']):
                logger.error(f"不允许的文件类型: {file_info['filename']}")
                return None
            
            # 下载文件
            logger.info(f"开始下载文件: {file_info['filename']} ({file_info['size']/1024:.1f}KB)")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            if referer:
                headers['Referer'] = referer
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    timeout=aiohttp.ClientTimeout(total=180)  # 3分钟超时
                ) as response:
                    if response.status == 200:
                        data = await response.read()
                        
                        logger.info(f"文件下载成功: {file_info['filename']}")
                        
                        return {
                            "data": data,
                            "filename": file_info['filename'],
                            "size": len(data),
                            "content_type": file_info['content_type']
                        }
                    else:
                        logger.error(f"文件下载失败: HTTP {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"文件下载超时: {url}")
            return None
        except Exception as e:
            logger.error(f"文件下载异常: {str(e)}")
            return None
    
    async def _get_file_info(self, url: str, cookies: Dict, 
                             referer: Optional[str] = None) -> Optional[Dict]:
        """
        获取文件信息（不下载完整文件）
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            if referer:
                headers['Referer'] = referer
            
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    url,
                    headers=headers,
                    cookies=cookies,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        # 从响应头获取文件信息
                        size = int(response.headers.get('Content-Length', 0))
                        content_type = response.headers.get('Content-Type', 'application/octet-stream')
                        
                        # 尝试从Content-Disposition获取文件名
                        filename = 'unknown'
                        content_disposition = response.headers.get('Content-Disposition', '')
                        if 'filename=' in content_disposition:
                            import re
                            match = re.search(r'filename="?([^"]+)"?', content_disposition)
                            if match:
                                filename = match.group(1)
                        
                        # 如果没有文件名，从URL提取
                        if filename == 'unknown':
                            from urllib.parse import urlparse, unquote
                            parsed = urlparse(url)
                            filename = Path(unquote(parsed.path)).name or 'unknown'
                        
                        return {
                            "filename": filename,
                            "size": size,
                            "content_type": content_type
                        }
                    else:
                        return None
                        
        except Exception as e:
            logger.debug(f"HEAD请求失败，尝试GET请求: {str(e)}")
            
            # HEAD失败时，尝试用GET获取少量数据
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers=headers,
                        cookies=cookies,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            # 只读取前1KB来获取信息
                            await response.content.read(1024)
                            
                            size = int(response.headers.get('Content-Length', 0))
                            content_type = response.headers.get('Content-Type', 'application/octet-stream')
                            
                            # 从URL提取文件名
                            from urllib.parse import urlparse, unquote
                            parsed = urlparse(url)
                            filename = Path(unquote(parsed.path)).name or 'unknown'
                            
                            return {
                                "filename": filename,
                                "size": size,
                                "content_type": content_type
                            }
                        else:
                            return None
            except:
                return None
    
    def validate_file_type(self, filename: str) -> bool:
        """
        验证文件类型是否允许
        """
        ext = Path(filename).suffix.lower()
        
        # 检查是否在危险列表中
        if ext in self.DANGEROUS_TYPES:
            logger.warning(f"危险文件类型: {ext}")
            return False
        
        # 检查是否在允许列表中
        if ext not in self.ALLOWED_TYPES:
            logger.warning(f"不允许的文件类型: {ext}")
            return False
        
        return True
    
    async def save_temp_file(self, data: bytes, filename: str) -> Optional[Path]:
        """
        保存临时文件
        """
        try:
            # 生成唯一文件名
            import hashlib
            import time
            
            file_hash = hashlib.md5(data).hexdigest()[:8]
            timestamp = int(time.time())
            safe_filename = f"{timestamp}_{file_hash}_{filename}"
            
            file_path = self.temp_dir / safe_filename
            
            # 异步写入文件
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, file_path.write_bytes, data)
            
            logger.info(f"临时文件已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"保存临时文件失败: {str(e)}")
            return None
    
    def cleanup_temp_file(self, file_path: Path):
        """
        清理临时文件
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"临时文件已删除: {file_path}")
        except Exception as e:
            logger.error(f"删除临时文件失败: {str(e)}")
    
    async def cleanup_old_temp_files(self, max_age_hours: int = 24):
        """
        清理旧的临时文件
        """
        try:
            import time
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            deleted_count = 0
            
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"清理了 {deleted_count} 个过期临时文件")
                
        except Exception as e:
            logger.error(f"清理临时文件异常: {str(e)}")


# 创建全局实例
file_processor = FileProcessor()
