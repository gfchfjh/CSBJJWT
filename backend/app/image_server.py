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
    return {
        "status": "ok",
        "storage_size_gb": round(storage_size_gb, 2),
        "storage_path": str(image_processor.storage_path)
    }


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
