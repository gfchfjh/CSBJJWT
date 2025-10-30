"""
视频教程管理API
✅ 新增：视频教程的管理、播放记录、统计功能
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from ..database import db
from ..utils.logger import logger

router = APIRouter(prefix="/api/videos", tags=["video_tutorials"])


class VideoInfo(BaseModel):
    """视频信息模型"""
    id: int
    title: str
    duration: str
    url: str
    poster: str
    description: str
    category: str
    difficulty: str
    order: int = 0


class MarkWatchedRequest(BaseModel):
    """标记观看请求"""
    video_id: int


class IncrementViewsRequest(BaseModel):
    """增加观看次数请求"""
    video_id: int


# 默认视频列表
DEFAULT_VIDEOS = [
    {
        "id": 1,
        "title": "01. 快速入门指南 - 5分钟上手",
        "duration": "5:30",
        "url": "https://example.com/videos/01-quickstart.mp4",
        "poster": "/images/video-posters/01-quickstart.jpg",
        "description": "本教程将带您快速了解KOOK消息转发系统的核心功能，5分钟即可完成首次配置。",
        "shortDesc": "快速了解系统核心功能",
        "category": "beginner",
        "difficulty": "⭐ 入门",
        "order": 1,
        "chapters": [
            {"time": 0, "title": "欢迎介绍"},
            {"time": 30, "title": "Cookie导入"},
            {"time": 120, "title": "配置Bot"},
            {"time": 240, "title": "频道映射"},
            {"time": 300, "title": "启动服务"}
        ]
    },
    {
        "id": 2,
        "title": "02. Cookie获取详细教程",
        "duration": "3:15",
        "url": "https://example.com/videos/02-cookie.mp4",
        "poster": "/images/video-posters/02-cookie.jpg",
        "description": "详细演示如何从浏览器中获取KOOK的Cookie，支持Chrome、Firefox、Edge等浏览器。",
        "shortDesc": "3种方法获取Cookie",
        "category": "beginner",
        "difficulty": "⭐ 入门",
        "order": 2
    },
    {
        "id": 3,
        "title": "03. Discord Webhook配置",
        "duration": "2:45",
        "url": "https://example.com/videos/03-discord.mp4",
        "poster": "/images/video-posters/03-discord.jpg",
        "description": "手把手教您创建Discord Webhook，包括权限设置和测试验证。",
        "shortDesc": "创建Webhook，2分钟搞定",
        "category": "config",
        "difficulty": "⭐ 入门",
        "order": 3
    },
    {
        "id": 4,
        "title": "04. Telegram Bot配置教程",
        "duration": "4:20",
        "url": "https://example.com/videos/04-telegram.mp4",
        "poster": "/images/video-posters/04-telegram.jpg",
        "description": "详细讲解如何与BotFather创建Bot，获取Token和Chat ID。",
        "shortDesc": "创建Bot，4分钟完成",
        "category": "config",
        "difficulty": "⭐⭐ 简单",
        "order": 4
    },
    {
        "id": 5,
        "title": "05. 飞书自建应用配置",
        "duration": "6:30",
        "url": "https://example.com/videos/05-feishu.mp4",
        "poster": "/images/video-posters/05-feishu.jpg",
        "description": "完整演示飞书开放平台创建自建应用的流程，包括权限配置和群组添加。",
        "shortDesc": "自建应用，10分钟配置",
        "category": "config",
        "difficulty": "⭐⭐ 简单",
        "order": 5
    },
    {
        "id": 6,
        "title": "06. 智能映射功能详解",
        "duration": "5:50",
        "url": "https://example.com/videos/06-smart-mapping.mp4",
        "poster": "/images/video-posters/06-smart-mapping.jpg",
        "description": "详细介绍智能映射算法，如何使用60+映射规则自动匹配频道。",
        "shortDesc": "自动匹配，效率提升500%",
        "category": "advanced",
        "difficulty": "⭐⭐⭐ 中等",
        "order": 6
    },
    {
        "id": 7,
        "title": "07. 过滤规则使用技巧",
        "duration": "4:15",
        "url": "https://example.com/videos/07-filter-rules.mp4",
        "poster": "/images/video-posters/07-filter-rules.jpg",
        "description": "讲解如何配置关键词过滤、用户过滤和消息类型过滤，实现精准转发。",
        "shortDesc": "精准过滤，避免噪音",
        "category": "advanced",
        "difficulty": "⭐⭐ 简单",
        "order": 7
    },
    {
        "id": 8,
        "title": "08. 常见问题排查指南",
        "duration": "7:20",
        "url": "https://example.com/videos/08-troubleshooting.mp4",
        "poster": "/images/video-posters/08-troubleshooting.jpg",
        "description": "介绍常见问题的排查方法，包括登录失败、转发失败、性能问题等。",
        "shortDesc": "问题排查，自助解决",
        "category": "advanced",
        "difficulty": "⭐⭐⭐ 中等",
        "order": 8
    },
    {
        "id": 9,
        "title": "09. Chrome扩展使用教程",
        "duration": "2:30",
        "url": "https://example.com/videos/09-chrome-extension.mp4",
        "poster": "/images/video-posters/09-chrome-extension.jpg",
        "description": "演示如何安装和使用Chrome扩展一键导出Cookie，让登录更简单。",
        "shortDesc": "3秒完成Cookie导出",
        "category": "beginner",
        "difficulty": "⭐ 入门",
        "order": 9
    },
    {
        "id": 10,
        "title": "10. 高级功能完整演示",
        "duration": "12:45",
        "url": "https://example.com/videos/10-advanced.mp4",
        "poster": "/images/video-posters/10-advanced.jpg",
        "description": "全面介绍插件系统、消息翻译、敏感词过滤、权限管理等高级功能。",
        "shortDesc": "解锁所有高级特性",
        "category": "advanced",
        "difficulty": "⭐⭐⭐⭐ 困难",
        "order": 10
    }
]


@router.get("/list")
async def get_video_list(
    category: Optional[str] = None,
    difficulty: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取视频教程列表
    
    Args:
        category: 分类过滤（beginner/config/advanced）
        difficulty: 难度过滤
    """
    try:
        videos = DEFAULT_VIDEOS.copy()
        
        # 分类过滤
        if category:
            videos = [v for v in videos if v['category'] == category]
        
        # 难度过滤
        if difficulty:
            videos = [v for v in videos if difficulty in v['difficulty']]
        
        # 按顺序排序
        videos.sort(key=lambda x: x['order'])
        
        return {
            "success": True,
            "videos": videos,
            "total": len(videos)
        }
        
    except Exception as e:
        logger.error(f"获取视频列表失败: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/{video_id}")
async def get_video_info(video_id: int) -> Dict[str, Any]:
    """
    获取单个视频信息
    """
    try:
        video = next((v for v in DEFAULT_VIDEOS if v['id'] == video_id), None)
        
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")
        
        # 获取观看记录
        result = db.execute_query(
            "SELECT * FROM video_watch_history WHERE video_id = ?",
            (video_id,)
        )
        
        watch_history = result[0] if result else None
        
        return {
            "success": True,
            "video": video,
            "watch_history": watch_history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取视频信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-watched")
async def mark_video_watched(request: MarkWatchedRequest) -> Dict[str, Any]:
    """
    标记视频为已观看
    """
    try:
        video_id = request.video_id
        
        # 检查表是否存在
        db.execute("""
            CREATE TABLE IF NOT EXISTS video_watch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL UNIQUE,
                watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                watch_count INTEGER DEFAULT 1,
                last_position REAL DEFAULT 0
            )
        """)
        
        # 插入或更新观看记录
        db.execute("""
            INSERT INTO video_watch_history (video_id, watched_at, watch_count)
            VALUES (?, datetime('now'), 1)
            ON CONFLICT(video_id) DO UPDATE SET
                watched_at = datetime('now'),
                watch_count = watch_count + 1
        """, (video_id,))
        
        logger.info(f"视频 {video_id} 已标记为观看")
        
        return {
            "success": True,
            "message": "已标记为观看"
        }
        
    except Exception as e:
        logger.error(f"标记视频观看失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/increment-views")
async def increment_video_views(request: IncrementViewsRequest) -> Dict[str, Any]:
    """
    增加视频观看次数
    """
    try:
        video_id = request.video_id
        
        # 确保表存在
        db.execute("""
            CREATE TABLE IF NOT EXISTS video_statistics (
                video_id INTEGER PRIMARY KEY,
                total_views INTEGER DEFAULT 0,
                unique_viewers INTEGER DEFAULT 0,
                avg_completion_rate REAL DEFAULT 0,
                last_viewed_at TIMESTAMP
            )
        """)
        
        # 增加观看次数
        db.execute("""
            INSERT INTO video_statistics (video_id, total_views, last_viewed_at)
            VALUES (?, 1, datetime('now'))
            ON CONFLICT(video_id) DO UPDATE SET
                total_views = total_views + 1,
                last_viewed_at = datetime('now')
        """, (video_id,))
        
        return {
            "success": True,
            "message": "观看次数已更新"
        }
        
    except Exception as e:
        logger.error(f"增加观看次数失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watched")
async def get_watched_videos() -> Dict[str, Any]:
    """
    获取已观看的视频列表
    """
    try:
        # 确保表存在
        db.execute("""
            CREATE TABLE IF NOT EXISTS video_watch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL UNIQUE,
                watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                watch_count INTEGER DEFAULT 1,
                last_position REAL DEFAULT 0
            )
        """)
        
        result = db.execute_query("SELECT video_id FROM video_watch_history")
        
        watched_ids = [row['video_id'] for row in result]
        
        return {
            "success": True,
            "watched_ids": watched_ids
        }
        
    except Exception as e:
        logger.error(f"获取观看记录失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "watched_ids": []
        }


@router.post("/save-progress")
async def save_video_progress(
    video_id: int,
    position: float
) -> Dict[str, Any]:
    """
    保存视频播放进度
    
    Args:
        video_id: 视频ID
        position: 播放位置（秒）
    """
    try:
        db.execute("""
            INSERT INTO video_watch_history (video_id, last_position)
            VALUES (?, ?)
            ON CONFLICT(video_id) DO UPDATE SET
                last_position = ?
        """, (video_id, position, position))
        
        return {
            "success": True,
            "message": "播放进度已保存"
        }
        
    except Exception as e:
        logger.error(f"保存播放进度失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_video_statistics() -> Dict[str, Any]:
    """
    获取视频统计信息
    """
    try:
        # 总观看次数
        total_views = db.execute_query(
            "SELECT COALESCE(SUM(total_views), 0) as total FROM video_statistics"
        )
        
        # 已观看视频数
        watched_count = db.execute_query(
            "SELECT COUNT(*) as count FROM video_watch_history"
        )
        
        # 最受欢迎的视频
        popular_videos = db.execute_query("""
            SELECT video_id, total_views 
            FROM video_statistics 
            ORDER BY total_views DESC 
            LIMIT 5
        """)
        
        return {
            "success": True,
            "statistics": {
                "total_views": total_views[0]['total'] if total_views else 0,
                "watched_count": watched_count[0]['count'] if watched_count else 0,
                "total_videos": len(DEFAULT_VIDEOS),
                "popular_videos": popular_videos
            }
        }
        
    except Exception as e:
        logger.error(f"获取视频统计失败: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    title: str = "",
    description: str = "",
    category: str = "beginner"
) -> Dict[str, Any]:
    """
    上传自定义视频教程
    
    Args:
        file: 视频文件
        title: 标题
        description: 描述
        category: 分类
    """
    try:
        # 检查文件类型
        allowed_types = ['video/mp4', 'video/webm', 'video/ogg']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="不支持的视频格式")
        
        # 检查文件大小（最大100MB）
        max_size = 100 * 1024 * 1024
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="视频文件过大（最大100MB）")
        
        # 保存文件
        videos_dir = Path("data/videos")
        videos_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = videos_dir / file.filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"视频已上传: {file_path}")
        
        return {
            "success": True,
            "message": "视频上传成功",
            "url": f"/videos/{file.filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传视频失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{video_id}")
async def delete_custom_video(video_id: int) -> Dict[str, Any]:
    """
    删除自定义视频
    
    注意：默认视频不可删除
    """
    try:
        # 检查是否为默认视频
        if video_id <= 10:
            raise HTTPException(status_code=400, detail="不能删除默认视频")
        
        # 删除观看记录
        db.execute("DELETE FROM video_watch_history WHERE video_id = ?", (video_id,))
        db.execute("DELETE FROM video_statistics WHERE video_id = ?", (video_id,))
        
        # 注意：实际视频文件删除需要额外处理
        
        return {
            "success": True,
            "message": "视频已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除视频失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{video_id}")
async def get_video_download_info(video_id: int) -> Dict[str, Any]:
    """
    获取视频下载信息（用于离线观看）
    """
    try:
        video = next((v for v in DEFAULT_VIDEOS if v['id'] == video_id), None)
        
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")
        
        return {
            "success": True,
            "download_url": video['url'],
            "filename": f"{video['title']}.mp4",
            "size": "待计算"  # 实际应该获取文件大小
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取下载信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
