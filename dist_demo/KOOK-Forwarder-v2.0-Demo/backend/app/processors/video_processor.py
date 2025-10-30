"""
视频处理器
✅ P0-22: 视频下载、转码和转发支持
"""
import aiohttp
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from ..utils.logger import logger
from ..config import settings


class VideoProcessor:
    """视频处理器"""
    
    def __init__(self):
        self.storage_path = settings.video_storage_path or Path('data/videos')
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 配置
        self.max_size_mb = getattr(settings, 'video_max_size_mb', 100)
        self.transcode_enabled = getattr(settings, 'video_transcode_enabled', True)
        self.target_format = getattr(settings, 'video_target_format', 'mp4')
        self.target_codec = getattr(settings, 'video_target_codec', 'h264')
        
        # 统计
        self.stats = {
            'total_processed': 0,
            'download_success': 0,
            'transcode_success': 0,
            'failed': 0
        }
    
    async def process_video(
        self,
        video_url: str,
        platform: str,
        context: dict = None
    ) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        处理视频
        
        Args:
            video_url: 视频URL
            platform: 目标平台
            context: 上下文信息
            
        Returns:
            (成功标志, 文件路径, 错误信息)
        """
        self.stats['total_processed'] += 1
        
        try:
            # 1. 下载视频
            logger.info(f"开始下载视频: {video_url}")
            success, filepath, error = await self._download_video(video_url, context)
            
            if not success:
                self.stats['failed'] += 1
                return False, None, error
            
            self.stats['download_success'] += 1
            logger.info(f"视频下载成功: {filepath}")
            
            # 2. 检查大小
            file_size = filepath.stat().st_size
            size_mb = file_size / 1024 / 1024
            
            logger.info(f"视频大小: {size_mb:.1f}MB")
            
            # 3. 判断是否需要转码
            needs_transcode = self._needs_transcode(filepath, size_mb, platform)
            
            if needs_transcode and self.transcode_enabled:
                logger.info("开始转码视频...")
                success, transcoded_path, error = await self._transcode_video(filepath)
                
                if success:
                    self.stats['transcode_success'] += 1
                    logger.info(f"转码成功: {transcoded_path}")
                    
                    # 删除原文件
                    filepath.unlink()
                    
                    return True, transcoded_path, None
                else:
                    logger.warning(f"转码失败: {error}，使用原视频")
                    return True, filepath, None
            
            return True, filepath, None
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"视频处理失败: {str(e)}")
            return False, None, str(e)
    
    async def _download_video(
        self,
        url: str,
        context: dict = None
    ) -> Tuple[bool, Optional[Path], Optional[str]]:
        """下载视频"""
        try:
            # 生成文件名
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()
            filename = f"video_{int(time.time())}_{url_hash}.mp4"
            filepath = self.storage_path / filename
            
            # 下载
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://www.kookapp.cn/'
            }
            
            if context and context.get('cookies'):
                # 添加Cookie
                pass
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=300) as response:
                    if response.status == 200:
                        with open(filepath, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        return True, filepath, None
                    else:
                        return False, None, f"下载失败，状态码: {response.status}"
                        
        except Exception as e:
            return False, None, str(e)
    
    def _needs_transcode(self, filepath: Path, size_mb: float, platform: str) -> bool:
        """判断是否需要转码"""
        # 1. 大小超限
        if size_mb > self.max_size_mb:
            return True
        
        # 2. 格式不兼容
        if filepath.suffix.lower() not in ['.mp4', '.mov']:
            return True
        
        # 3. 平台特殊要求
        platform_limits = {
            'discord': 8,  # Discord免费版8MB限制
            'telegram': 50,  # Telegram 50MB限制
            'feishu': 200  # 飞书200MB限制
        }
        
        limit = platform_limits.get(platform, 100)
        if size_mb > limit:
            return True
        
        return False
    
    async def _transcode_video(
        self,
        input_path: Path
    ) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        转码视频
        
        使用ffmpeg压缩视频
        """
        try:
            # 检查ffmpeg
            if not self._check_ffmpeg():
                return False, None, "ffmpeg未安装"
            
            # 输出路径
            output_path = input_path.with_name(
                input_path.stem + f'_transcoded.{self.target_format}'
            )
            
            # ffmpeg命令
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-c:v', self.target_codec,
                '-crf', '28',  # 质量因子（越小质量越高）
                '-preset', 'medium',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',  # 覆盖输出文件
                str(output_path)
            ]
            
            # 执行转码
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return True, output_path, None
            else:
                error = stderr.decode() if stderr else "未知错误"
                return False, None, error
                
        except Exception as e:
            return False, None, str(e)
    
    def _check_ffmpeg(self) -> bool:
        """检查ffmpeg是否可用"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    async def cleanup_old_videos(self, days: int = 3):
        """清理旧视频"""
        try:
            import time
            cleanup_before = time.time() - (days * 86400)
            
            cleaned_count = 0
            cleaned_size = 0
            
            for filepath in self.storage_path.glob('*.mp4'):
                try:
                    mtime = filepath.stat().st_mtime
                    
                    if mtime < cleanup_before:
                        size = filepath.stat().st_size
                        filepath.unlink()
                        
                        cleaned_count += 1
                        cleaned_size += size
                        
                except Exception as e:
                    logger.error(f"删除视频失败 {filepath}: {str(e)}")
                    continue
            
            if cleaned_count > 0:
                logger.info(
                    f"清理完成: 删除{cleaned_count}个视频文件，"
                    f"释放{cleaned_size / 1024 / 1024:.1f}MB空间"
                )
            
            return cleaned_count, cleaned_size
            
        except Exception as e:
            logger.error(f"清理视频失败: {str(e)}")
            return 0, 0
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        # 计算存储使用情况
        total_size = sum(f.stat().st_size for f in self.storage_path.glob('*.mp4'))
        file_count = len(list(self.storage_path.glob('*.mp4')))
        
        return {
            **self.stats,
            'storage': {
                'total_files': file_count,
                'total_size_mb': total_size / 1024 / 1024
            }
        }


# 全局实例
video_processor = VideoProcessor()
