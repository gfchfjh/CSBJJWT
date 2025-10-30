"""
✅ P0-3深度优化：图床存储管理API

功能：
- 存储空间统计
- 图片列表查询
- 手动清理旧图片
- 图片预览和删除
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
from ...config import settings
from ...utils.logger import logger

router = APIRouter(prefix="/api/image-storage", tags=["image-storage"])


class StorageInfo(BaseModel):
    """存储信息"""
    used_gb: float
    max_gb: float
    image_count: int
    storage_path: str
    auto_clean_days: int
    recent_images: List[Dict[str, Any]]
    usage_percentage: float


class CleanupResult(BaseModel):
    """清理结果"""
    deleted_count: int
    freed_mb: float
    freed_gb: float


@router.get("/info", response_model=StorageInfo)
async def get_storage_info():
    """
    获取图床存储信息
    
    Returns:
        存储统计信息
    """
    try:
        storage_path = Path(settings.data_dir) / "images"
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # 计算已用空间
        total_size = 0
        image_files = []
        
        for file_path in storage_path.glob('*.*'):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                total_size += file_size
                
                # 收集图片信息
                image_files.append({
                    'path': file_path,
                    'size': file_size,
                    'mtime': file_path.stat().st_mtime
                })
        
        used_gb = total_size / (1024 ** 3)
        max_gb = float(getattr(settings, 'image_storage_max_gb', 10))
        
        # 获取最近100张图片
        image_files.sort(key=lambda x: x['mtime'], reverse=True)
        recent_images = [
            {
                'filename': img['path'].name,
                'size': f"{img['size'] / 1024:.1f}KB" if img['size'] < 1024*1024 else f"{img['size'] / (1024*1024):.2f}MB",
                'size_bytes': img['size'],
                'upload_time': datetime.fromtimestamp(img['mtime']).strftime('%Y-%m-%d %H:%M:%S'),
                'upload_timestamp': img['mtime']
            }
            for img in image_files[:100]
        ]
        
        usage_percentage = (used_gb / max_gb * 100) if max_gb > 0 else 0
        
        return StorageInfo(
            used_gb=round(used_gb, 2),
            max_gb=max_gb,
            image_count=len(image_files),
            storage_path=str(storage_path),
            auto_clean_days=getattr(settings, 'image_auto_clean_days', 7),
            recent_images=recent_images,
            usage_percentage=round(usage_percentage, 1)
        )
        
    except Exception as e:
        logger.error(f"获取存储信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup", response_model=CleanupResult)
async def cleanup_old_images(days: int = 7):
    """
    清理N天前的旧图片
    
    Args:
        days: 天数（默认7天）
    
    Returns:
        清理结果
    """
    try:
        storage_path = Path(settings.data_dir) / "images"
        cutoff_time = time.time() - (days * 86400)
        
        deleted_count = 0
        freed_bytes = 0
        
        logger.info(f"开始清理{days}天前的图片...")
        
        for file_path in storage_path.glob('*.*'):
            if file_path.is_file():
                file_mtime = file_path.stat().st_mtime
                
                if file_mtime < cutoff_time:
                    file_size = file_path.stat().st_size
                    
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        freed_bytes += file_size
                        logger.debug(f"删除文件: {file_path.name}")
                    except Exception as e:
                        logger.error(f"删除文件失败 {file_path.name}: {str(e)}")
        
        freed_mb = freed_bytes / (1024 ** 2)
        freed_gb = freed_bytes / (1024 ** 3)
        
        logger.info(f"清理完成：删除{deleted_count}个文件，释放{freed_mb:.2f}MB空间")
        
        return CleanupResult(
            deleted_count=deleted_count,
            freed_mb=round(freed_mb, 2),
            freed_gb=round(freed_gb, 3)
        )
        
    except Exception as e:
        logger.error(f"清理图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup-all", response_model=CleanupResult)
async def cleanup_all_images():
    """
    清空所有图片（危险操作）
    
    Returns:
        清理结果
    """
    try:
        storage_path = Path(settings.data_dir) / "images"
        
        deleted_count = 0
        freed_bytes = 0
        
        logger.warning("清空所有图片...")
        
        for file_path in storage_path.glob('*.*'):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                
                try:
                    file_path.unlink()
                    deleted_count += 1
                    freed_bytes += file_size
                except Exception as e:
                    logger.error(f"删除文件失败 {file_path.name}: {str(e)}")
        
        freed_mb = freed_bytes / (1024 ** 2)
        freed_gb = freed_bytes / (1024 ** 3)
        
        logger.info(f"清空完成：删除{deleted_count}个文件，释放{freed_mb:.2f}MB空间")
        
        return CleanupResult(
            deleted_count=deleted_count,
            freed_mb=round(freed_mb, 2),
            freed_gb=round(freed_gb, 3)
        )
        
    except Exception as e:
        logger.error(f"清空图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/image/{filename}")
async def delete_image(filename: str):
    """
    删除单个图片
    
    Args:
        filename: 文件名
    
    Returns:
        删除结果
    """
    try:
        storage_path = Path(settings.data_dir) / "images"
        file_path = storage_path / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="不是文件")
        
        file_size = file_path.stat().st_size
        file_path.unlink()
        
        logger.info(f"删除图片: {filename}")
        
        return {
            "success": True,
            "message": f"已删除文件: {filename}",
            "freed_bytes": file_size,
            "freed_kb": round(file_size / 1024, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/open-folder")
async def open_storage_folder():
    """
    打开图床存储文件夹
    
    Returns:
        文件夹路径
    """
    try:
        import platform
        import subprocess
        
        storage_path = Path(settings.data_dir) / "images"
        storage_path.mkdir(parents=True, exist_ok=True)
        
        system = platform.system()
        
        if system == 'Windows':
            subprocess.Popen(['explorer', str(storage_path)])
        elif system == 'Darwin':  # macOS
            subprocess.Popen(['open', str(storage_path)])
        else:  # Linux
            subprocess.Popen(['xdg-open', str(storage_path)])
        
        return {
            "success": True,
            "path": str(storage_path)
        }
        
    except Exception as e:
        logger.error(f"打开文件夹失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
