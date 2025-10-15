"""
图床HTTP服务器
提供本地图片访问服务
"""
import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
from .config import settings
from .processors.image import image_processor
from .utils.logger import logger


# 创建FastAPI应用
image_app = FastAPI(title="KOOK图床服务")


@image_app.get("/images/{filename}")
async def get_image(filename: str, token: str = Query(...)):
    """
    获取图片
    
    Args:
        filename: 文件名
        token: 访问Token
        
    Returns:
        图片文件
    """
    try:
        # 构建文件路径
        filepath = Path(settings.data_dir) / "images" / filename
        
        # 检查文件是否存在
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="图片不存在")
        
        # 验证Token
        if not image_processor.verify_token(str(filepath), token):
            raise HTTPException(status_code=403, detail="Token无效或已过期")
        
        # 返回文件
        return FileResponse(filepath, media_type="image/jpeg")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@image_app.get("/health")
async def health_check():
    """健康检查"""
    storage_size_gb = image_processor.get_storage_size()
    
    # 统计图片数量
    image_count = len(list(image_processor.storage_path.glob("*.jpg")))
    
    return {
        "status": "ok",
        "storage_size_gb": round(storage_size_gb, 2),
        "storage_path": str(image_processor.storage_path),
        "image_count": image_count,
        "max_size_gb": settings.image_max_size_gb
    }


@image_app.post("/cleanup")
async def cleanup_old_images(days: int = Query(default=7, ge=1, le=30)):
    """
    清理旧图片
    
    Args:
        days: 清理多少天前的图片
    """
    try:
        await image_processor.cleanup_old_images(days)
        return {"status": "success", "message": f"已清理{days}天前的图片"}
    except Exception as e:
        logger.error(f"清理图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@image_app.get("/stats")
async def get_stats():
    """获取图床统计信息"""
    try:
        storage_path = image_processor.storage_path
        
        # 统计各类信息
        total_images = 0
        total_size_bytes = 0
        
        for filepath in storage_path.glob("*.jpg"):
            total_images += 1
            total_size_bytes += filepath.stat().st_size
        
        return {
            "total_images": total_images,
            "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
            "total_size_gb": round(total_size_bytes / (1024 ** 3), 2),
            "storage_path": str(storage_path),
            "active_tokens": len(image_processor.url_tokens)
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def start_image_server():
    """启动图床服务器"""
    import uvicorn
    
    config = uvicorn.Config(
        image_app,
        host="127.0.0.1",
        port=settings.image_server_port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    logger.info(f"图床服务器启动: http://127.0.0.1:{settings.image_server_port}")
    
    try:
        await server.serve()
    except Exception as e:
        logger.error(f"图床服务器异常: {str(e)}")


if __name__ == "__main__":
    asyncio.run(start_image_server())
