"""
视频API - ✅ P0-1优化：视频占位符和管理接口
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from pathlib import Path
from ..utils.logger import logger
from ..utils.video_manager import video_manager

router = APIRouter(prefix="/api/videos", tags=["videos"])


class VideoUploadRequest(BaseModel):
    """视频上传请求"""
    video_id: str
    title: str
    description: Optional[str] = None


# ============ 视频状态和信息接口 ============

@router.get("/status")
async def get_videos_status():
    """
    获取所有视频的状态概览
    
    Returns:
        {
            "total": 5,
            "available": 2,
            "placeholder": 3,
            "missing": 0,
            "completion_rate": 40.0,
            "videos": [...]
        }
    """
    try:
        status = video_manager.get_all_videos_status()
        return status
    except Exception as e:
        logger.error(f"获取视频状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/info")
async def get_video_info(video_id: str):
    """
    获取特定视频的信息
    
    Args:
        video_id: 视频ID
        
    Returns:
        视频信息或占位符信息
    """
    try:
        info = video_manager.get_video_info(video_id)
        
        if info["status"] == "placeholder":
            # 返回占位符信息
            placeholder = video_manager.get_placeholder_info(
                video_id=video_id,
                video_title="教程视频",
                duration="未知",
                description="视频制作中"
            )
            return {
                **info,
                "placeholder": placeholder
            }
        
        return info
    except Exception as e:
        logger.error(f"获取视频信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/stream")
async def stream_video(video_id: str):
    """
    流式传输视频文件
    
    Args:
        video_id: 视频ID
        
    Returns:
        视频文件或错误信息
    """
    try:
        info = video_manager.get_video_info(video_id)
        
        if info["status"] != "available":
            # 视频不可用，返回占位符信息
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "video_not_available",
                    "message": "🎬 视频教程制作中，敬请期待！",
                    "alternative": "请查看图文教程获取详细信息",
                    "tutorial_link": f"/api/help/tutorials/{video_id}"
                }
            )
        
        video_path = Path(info["path"])
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="视频文件不存在")
        
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"{video_id}.mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"流式传输视频失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/thumbnail")
async def get_video_thumbnail(video_id: str):
    """
    获取视频缩略图
    
    Args:
        video_id: 视频ID
        
    Returns:
        缩略图文件
    """
    try:
        info = video_manager.get_video_info(video_id)
        
        if info["thumbnail_exists"]:
            thumbnail_path = video_manager.thumbnail_dir / f"{video_id}.jpg"
            return FileResponse(
                thumbnail_path,
                media_type="image/jpeg",
                filename=f"{video_id}_thumbnail.jpg"
            )
        else:
            # 返回默认占位符图片
            raise HTTPException(
                status_code=404,
                detail="缩略图不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取缩略图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 视频上传和管理接口 ============

@router.post("/upload")
async def upload_video(
    video_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...)
):
    """
    上传视频文件
    
    Args:
        video_id: 视频ID
        title: 视频标题
        file: 视频文件
        
    Returns:
        上传结果
    """
    try:
        # 检查文件类型
        if not file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400,
                detail="文件类型必须是视频格式"
            )
        
        # 保存临时文件
        temp_path = video_manager.video_dir / f"temp_{video_id}.mp4"
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 上传到系统
        result = video_manager.upload_video(video_id, str(temp_path))
        
        # 删除临时文件
        if temp_path.exists():
            temp_path.unlink()
        
        if result["success"]:
            # 自动生成缩略图
            video_manager.generate_thumbnail(video_id)
            
            return {
                "success": True,
                "message": f"✅ 视频上传成功: {title}",
                "video_id": video_id,
                "file_size_mb": result["file_size_mb"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传视频失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{video_id}/generate-thumbnail")
async def generate_thumbnail(video_id: str):
    """
    生成视频缩略图
    
    Args:
        video_id: 视频ID
        
    Returns:
        生成结果
    """
    try:
        thumbnail_path = video_manager.generate_thumbnail(video_id)
        
        if thumbnail_path:
            return {
                "success": True,
                "message": "✅ 缩略图生成成功",
                "thumbnail_url": f"/api/videos/{video_id}/thumbnail"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="缩略图生成失败"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成缩略图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """
    删除视频文件
    
    Args:
        video_id: 视频ID
        
    Returns:
        删除结果
    """
    try:
        video_path = video_manager.video_dir / f"{video_id}.mp4"
        thumbnail_path = video_manager.thumbnail_dir / f"{video_id}.jpg"
        
        deleted = []
        
        if video_path.exists():
            video_path.unlink()
            deleted.append("video")
        
        if thumbnail_path.exists():
            thumbnail_path.unlink()
            deleted.append("thumbnail")
        
        # 清除缓存
        video_manager.clear_cache()
        
        if deleted:
            return {
                "success": True,
                "message": f"✅ 已删除: {', '.join(deleted)}",
                "deleted": deleted
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="视频文件不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除视频失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_cache():
    """清除视频状态缓存"""
    try:
        video_manager.clear_cache()
        return {
            "success": True,
            "message": "✅ 缓存已清除"
        }
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
