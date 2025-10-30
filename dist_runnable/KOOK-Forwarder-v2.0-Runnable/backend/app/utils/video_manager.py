"""
视频管理器 - ✅ P0-1优化：视频占位符系统
"""
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..utils.logger import logger
from ..config import settings
import os


class VideoManager:
    """视频管理器 - 处理视频教程的存储、访问和占位符"""
    
    def __init__(self):
        # 视频存储目录
        self.video_dir = Path(settings.data_dir) / "videos"
        self.thumbnail_dir = self.video_dir / "thumbnails"
        
        # 创建目录
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        
        # 视频状态缓存
        self.video_status_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"✅ 视频管理器已初始化，存储路径: {self.video_dir}")
    
    def check_video_exists(self, video_id: str) -> bool:
        """
        检查视频文件是否存在
        
        Args:
            video_id: 视频ID
            
        Returns:
            是否存在
        """
        video_path = self.video_dir / f"{video_id}.mp4"
        return video_path.exists()
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        获取视频信息
        
        Args:
            video_id: 视频ID
            
        Returns:
            {
                "id": str,
                "exists": bool,
                "file_size": int,  # 字节
                "file_size_mb": float,
                "path": str,
                "url": str,
                "thumbnail_exists": bool,
                "thumbnail_url": str,
                "status": "available" | "placeholder" | "encoding" | "missing"
            }
        """
        # 检查缓存
        if video_id in self.video_status_cache:
            return self.video_status_cache[video_id]
        
        video_path = self.video_dir / f"{video_id}.mp4"
        thumbnail_path = self.thumbnail_dir / f"{video_id}.jpg"
        
        info = {
            "id": video_id,
            "exists": video_path.exists(),
            "file_size": 0,
            "file_size_mb": 0.0,
            "path": str(video_path),
            "url": f"/videos/{video_id}.mp4",
            "thumbnail_exists": thumbnail_path.exists(),
            "thumbnail_url": f"/videos/thumbnails/{video_id}.jpg",
            "status": "missing"
        }
        
        if video_path.exists():
            # 视频文件存在
            info["file_size"] = video_path.stat().st_size
            info["file_size_mb"] = round(info["file_size"] / 1024 / 1024, 2)
            info["status"] = "available"
        else:
            # 视频文件不存在，使用占位符
            info["status"] = "placeholder"
        
        # 缓存结果
        self.video_status_cache[video_id] = info
        
        return info
    
    def get_placeholder_info(self, video_id: str, video_title: str, 
                            duration: str, description: str) -> Dict[str, Any]:
        """
        获取占位符信息（视频文件不存在时）
        
        Args:
            video_id: 视频ID
            video_title: 视频标题
            duration: 预计时长
            description: 描述
            
        Returns:
            占位符信息
        """
        return {
            "id": video_id,
            "title": video_title,
            "duration": duration,
            "description": description,
            "status": "coming_soon",
            "message": "🎬 视频教程制作中，敬请期待！",
            "alternative": "请查看图文教程获取详细信息",
            "tutorial_link": f"/api/help/tutorials/{video_id}",
            "placeholder_image": f"/images/video-placeholder-{video_id}.png",
            "expected_release": "即将发布",
            "notify_available": True,  # 用户可以订阅通知
            "fallback_content": {
                "type": "tutorial",
                "id": video_id,
                "format": "text"
            }
        }
    
    def get_all_videos_status(self) -> Dict[str, Any]:
        """
        获取所有视频的状态概览
        
        Returns:
            {
                "total": int,
                "available": int,
                "placeholder": int,
                "missing": int,
                "videos": List[Dict]
            }
        """
        # 预定义的视频列表
        video_ids = [
            "video_full_config",
            "video_cookie",
            "video_discord",
            "video_telegram",
            "video_feishu"
        ]
        
        videos = []
        stats = {
            "total": len(video_ids),
            "available": 0,
            "placeholder": 0,
            "missing": 0
        }
        
        for video_id in video_ids:
            info = self.get_video_info(video_id)
            videos.append(info)
            
            if info["status"] == "available":
                stats["available"] += 1
            elif info["status"] == "placeholder":
                stats["placeholder"] += 1
            else:
                stats["missing"] += 1
        
        return {
            **stats,
            "videos": videos,
            "completion_rate": round(stats["available"] / stats["total"] * 100, 1)
        }
    
    def create_placeholder_video(self, video_id: str, video_info: Dict[str, Any]) -> str:
        """
        创建视频占位符文件（1秒的纯色视频）
        
        Args:
            video_id: 视频ID
            video_info: 视频信息
            
        Returns:
            占位符文件路径
        """
        placeholder_path = self.video_dir / f"{video_id}_placeholder.mp4"
        
        # 使用ffmpeg创建1秒的占位符视频（如果安装了ffmpeg）
        try:
            import subprocess
            
            # 创建1秒的纯黑视频，带有"Coming Soon"文字
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c=black:s=1920x1080:d=1',
                '-vf', f"drawtext=text='🎬 Coming Soon\\n{video_info['title']}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
                '-y',
                str(placeholder_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"✅ 创建占位符视频: {video_id}")
                return str(placeholder_path)
            else:
                logger.warning(f"⚠️ ffmpeg创建占位符失败，使用文本占位符")
        except Exception as e:
            logger.warning(f"⚠️ 无法创建视频占位符: {e}")
        
        return ""
    
    def upload_video(self, video_id: str, video_file_path: str) -> Dict[str, Any]:
        """
        上传视频文件到系统
        
        Args:
            video_id: 视频ID
            video_file_path: 源视频文件路径
            
        Returns:
            上传结果
        """
        import shutil
        
        source = Path(video_file_path)
        
        if not source.exists():
            return {
                "success": False,
                "error": "源视频文件不存在"
            }
        
        # 复制到视频目录
        dest = self.video_dir / f"{video_id}.mp4"
        
        try:
            shutil.copy2(source, dest)
            
            # 清除缓存
            if video_id in self.video_status_cache:
                del self.video_status_cache[video_id]
            
            logger.info(f"✅ 视频上传成功: {video_id} ({dest.stat().st_size / 1024 / 1024:.2f} MB)")
            
            return {
                "success": True,
                "video_id": video_id,
                "file_size_mb": round(dest.stat().st_size / 1024 / 1024, 2),
                "path": str(dest)
            }
        except Exception as e:
            logger.error(f"❌ 视频上传失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_thumbnail(self, video_id: str) -> Optional[str]:
        """
        从视频生成缩略图
        
        Args:
            video_id: 视频ID
            
        Returns:
            缩略图路径
        """
        video_path = self.video_dir / f"{video_id}.mp4"
        thumbnail_path = self.thumbnail_dir / f"{video_id}.jpg"
        
        if not video_path.exists():
            return None
        
        try:
            import subprocess
            
            # 使用ffmpeg提取第5秒的帧作为缩略图
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-ss', '00:00:05',
                '-vframes', '1',
                '-vf', 'scale=640:-1',
                '-y',
                str(thumbnail_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"✅ 生成缩略图: {video_id}")
                return str(thumbnail_path)
            else:
                logger.warning(f"⚠️ ffmpeg生成缩略图失败")
        except Exception as e:
            logger.warning(f"⚠️ 无法生成缩略图: {e}")
        
        return None
    
    def clear_cache(self):
        """清除状态缓存"""
        self.video_status_cache.clear()
        logger.info("🗑️ 视频状态缓存已清除")


# 全局视频管理器实例
video_manager = VideoManager()
