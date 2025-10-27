"""
图床存储管理API - 终极版（✨ P0-5优化）
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time
from pathlib import Path
from ..utils.logger import logger
from ..processors.image_strategy_ultimate import image_processor_ultimate


router = APIRouter(prefix="/api/image-storage", tags=["图床存储"])


class ImageInfo(BaseModel):
    """图片信息"""
    id: int
    filename: str
    size: int
    upload_time: int
    last_access: int
    url: str


class ImageListResponse(BaseModel):
    """图片列表响应"""
    images: List[ImageInfo]
    stats: dict


class DeleteRequest(BaseModel):
    """删除请求"""
    image_ids: List[int]


class CleanupRequest(BaseModel):
    """清理请求"""
    strategy: str  # 'days' | 'all'
    days: Optional[int] = 7


@router.get("/list", response_model=ImageListResponse)
async def get_image_list():
    """
    获取图片列表
    
    Returns:
        图片列表和统计信息
    """
    try:
        from ..database import db
        
        # 获取图片列表
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT id, filename, size, upload_time, last_access
            FROM image_storage
            ORDER BY upload_time DESC
        """)
        
        images = []
        for row in cursor.fetchall():
            image_id, filename, size, upload_time, last_access = row
            
            # 生成URL
            token = image_processor_ultimate._generate_token(filename)
            url = f"{image_processor_ultimate.imgbed_base_url}/images/{filename}?token={token}"
            
            images.append(ImageInfo(
                id=image_id,
                filename=filename,
                size=size,
                upload_time=upload_time,
                last_access=last_access,
                url=url
            ))
        
        # 获取统计信息
        stats = image_processor_ultimate.get_storage_stats()
        
        return ImageListResponse(
            images=images,
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"获取图片列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_images(request: DeleteRequest):
    """
    删除图片
    
    Args:
        image_ids: 要删除的图片ID列表
    """
    try:
        from ..database import db
        
        deleted_count = 0
        
        for image_id in request.image_ids:
            # 获取文件名
            cursor = db.conn.cursor()
            cursor.execute("SELECT filename FROM image_storage WHERE id = ?", (image_id,))
            row = cursor.fetchone()
            
            if not row:
                continue
            
            filename = row[0]
            
            # 删除文件
            file_path = image_processor_ultimate.imgbed_dir / filename
            if file_path.exists():
                file_path.unlink()
            
            # 删除数据库记录
            cursor.execute("DELETE FROM image_storage WHERE id = ?", (image_id,))
            db.conn.commit()
            
            deleted_count += 1
        
        logger.info(f"✅ 删除了 {deleted_count} 张图片")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"成功删除 {deleted_count} 张图片"
        }
        
    except Exception as e:
        logger.error(f"删除图片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_images(request: CleanupRequest):
    """
    智能清理图片
    
    Args:
        strategy: 清理策略 ('days' | 'all')
        days: 保留天数（strategy='days'时有效）
    """
    try:
        from ..database import db
        
        deleted_count = 0
        deleted_size = 0
        
        if request.strategy == 'all':
            # 清空全部
            cursor = db.conn.cursor()
            cursor.execute("SELECT filename, size FROM image_storage")
            
            for row in cursor.fetchall():
                filename, size = row
                file_path = image_processor_ultimate.imgbed_dir / filename
                if file_path.exists():
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += size
            
            # 清空数据库
            cursor.execute("DELETE FROM image_storage")
            db.conn.commit()
            
        elif request.strategy == 'days':
            # 按天数清理
            cutoff_time = int(time.time()) - (request.days * 24 * 60 * 60)
            
            cursor = db.conn.cursor()
            cursor.execute(
                "SELECT id, filename, size FROM image_storage WHERE upload_time < ?",
                (cutoff_time,)
            )
            
            for row in cursor.fetchall():
                image_id, filename, size = row
                file_path = image_processor_ultimate.imgbed_dir / filename
                if file_path.exists():
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += size
            
            # 删除数据库记录
            cursor.execute("DELETE FROM image_storage WHERE upload_time < ?", (cutoff_time,))
            db.conn.commit()
        
        logger.info(f"✅ 清理完成: 删除 {deleted_count} 张图片，释放 {deleted_size/1024/1024:.2f}MB")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "deleted_size": deleted_size,
            "deleted_size_mb": deleted_size / 1024 / 1024,
            "message": f"清理完成，删除 {deleted_count} 张图片"
        }
        
    except Exception as e:
        logger.error(f"清理图片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_storage_stats():
    """
    获取存储统计信息
    """
    try:
        stats = image_processor_ultimate.get_storage_stats()
        return stats
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
