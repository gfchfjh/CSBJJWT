"""
安全图床服务器 - P0-4优化
特性:
- 仅允许本地访问
- Token验证
- 防止路径遍历攻击
- 自动清理过期Token
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pathlib import Path
import time
from .config import settings
from .utils.logger import logger
from .processors.image import image_processor


app = FastAPI(title="KOOK图床服务（安全版）")


def check_local_access(request: Request):
    """
    检查是否为本地访问
    
    Args:
        request: FastAPI请求对象
        
    Raises:
        HTTPException: 如果不是本地访问
    """
    client_host = request.client.host
    
    # 允许的本地地址
    allowed_hosts = ['127.0.0.1', 'localhost', '::1', '::ffff:127.0.0.1']
    
    if client_host not in allowed_hosts:
        logger.warning(f"🚫 拒绝非本地访问: {client_host}")
        raise HTTPException(
            status_code=403,
            detail="仅允许本地访问（Forbidden: Local access only）"
        )


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，防止路径遍历攻击
    
    Args:
        filename: 原始文件名
        
    Returns:
        安全的文件名
        
    Raises:
        HTTPException: 如果文件名包含危险字符
    """
    # 检查路径遍历攻击
    if '..' in filename:
        logger.warning(f"🚫 检测到路径遍历攻击: {filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid filename: Path traversal detected"
        )
    
    # 检查路径分隔符
    if '/' in filename or '\\' in filename:
        logger.warning(f"🚫 检测到非法路径分隔符: {filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid filename: Path separator not allowed"
        )
    
    # 检查特殊字符
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
    for char in dangerous_chars:
        if char in filename:
            logger.warning(f"🚫 检测到危险字符: {filename}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid filename: Dangerous character '{char}' not allowed"
            )
    
    return filename


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "KOOK图床服务（安全版）",
        "version": "2.0",
        "status": "running",
        "security": {
            "local_only": True,
            "token_required": True,
            "path_traversal_protection": True
        }
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "storage_path": str(settings.image_storage_path),
        "storage_size_gb": image_processor.get_storage_size(),
        "active_tokens": len(image_processor.url_tokens)
    }


@app.get("/images/{filename}")
async def serve_image(
    filename: str,
    token: str,
    request: Request
):
    """
    提供图片文件（安全版）
    
    Args:
        filename: 文件名
        token: 访问Token
        request: 请求对象
        
    Returns:
        文件响应
        
    Raises:
        HTTPException: 访问被拒绝
    """
    try:
        # 1. 检查本地访问
        check_local_access(request)
        
        # 2. 清理文件名（防止路径遍历）
        safe_filename = sanitize_filename(filename)
        
        # 3. 构造安全的文件路径
        storage_path = Path(settings.image_storage_path)
        filepath = storage_path / safe_filename
        
        # 4. 验证路径是否在存储目录内（双重保险）
        try:
            filepath = filepath.resolve()
            storage_path = storage_path.resolve()
            
            if not str(filepath).startswith(str(storage_path)):
                logger.warning(f"🚫 路径遍历尝试: {filepath}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file path"
                )
        except Exception as e:
            logger.error(f"路径解析失败: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid file path"
            )
        
        # 5. 验证Token
        if not image_processor.verify_token(str(filepath), token):
            logger.warning(f"🚫 Token验证失败: {filename}, token={token[:10]}...")
            
            # 记录失败的访问尝试
            image_processor.stats['access_logs'].append({
                'timestamp': time.time(),
                'filename': safe_filename,
                'token': token[:10] + '...',
                'result': 'failed',
                'reason': 'Invalid or expired token',
                'client': request.client.host
            })
            
            # 只保留最近100条日志
            if len(image_processor.stats['access_logs']) > 100:
                image_processor.stats['access_logs'] = image_processor.stats['access_logs'][-100:]
            
            raise HTTPException(
                status_code=403,
                detail="Token无效或已过期（Invalid or expired token）"
            )
        
        # 6. 检查文件是否存在
        if not filepath.exists():
            logger.warning(f"🚫 文件不存在: {filepath}")
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # 7. 检查是否为文件（不是目录）
        if not filepath.is_file():
            logger.warning(f"🚫 不是文件: {filepath}")
            raise HTTPException(
                status_code=400,
                detail="Not a file"
            )
        
        # 8. 记录成功的访问
        image_processor.stats['access_logs'].append({
            'timestamp': time.time(),
            'filename': safe_filename,
            'token': token[:10] + '...',
            'result': 'success',
            'client': request.client.host
        })
        
        # 只保留最近100条日志
        if len(image_processor.stats['access_logs']) > 100:
            image_processor.stats['access_logs'] = image_processor.stats['access_logs'][-100:]
        
        # 9. 返回文件
        logger.info(f"✅ 图片访问成功: {safe_filename}")
        
        return FileResponse(
            filepath,
            media_type='image/jpeg',  # 根据文件类型可能需要调整
            headers={
                'Cache-Control': 'public, max-age=7200',  # 缓存2小时
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 图片服务异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/stats")
async def get_stats(request: Request):
    """
    获取统计信息
    
    Args:
        request: 请求对象
        
    Returns:
        统计信息
    """
    # 检查本地访问
    check_local_access(request)
    
    token_stats = image_processor.get_token_stats()
    storage_info = image_processor.get_storage_info()
    processing_stats = image_processor.get_processing_stats()
    
    return {
        "tokens": token_stats,
        "storage": storage_info,
        "processing": processing_stats,
        "recent_access": image_processor.stats['access_logs'][-20:]  # 最近20条访问记录
    }


@app.post("/cleanup")
async def manual_cleanup(request: Request):
    """
    手动触发清理
    
    Args:
        request: 请求对象
        
    Returns:
        清理结果
    """
    # 检查本地访问
    check_local_access(request)
    
    try:
        # 清理过期Token
        expired_count = image_processor.cleanup_expired_tokens()
        
        # 清理旧图片
        cleanup_result = await image_processor.cleanup_old_images(
            days=settings.image_cleanup_days
        )
        
        return {
            "success": True,
            "expired_tokens_removed": expired_count,
            "old_images_removed": cleanup_result.get('deleted_count', 0),
            "space_freed_mb": cleanup_result.get('freed_space_mb', 0)
        }
        
    except Exception as e:
        logger.error(f"手动清理失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# 启动时的初始化
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("=" * 50)
    logger.info("🖼️ 安全图床服务启动")
    logger.info(f"📁 存储路径: {settings.image_storage_path}")
    logger.info(f"🔐 安全特性:")
    logger.info("  ✅ 仅本地访问")
    logger.info("  ✅ Token验证（2小时有效期）")
    logger.info("  ✅ 路径遍历防护")
    logger.info("  ✅ 自动清理过期Token（每15分钟）")
    logger.info("=" * 50)
    
    # 启动Token自动清理任务
    logger.info("启动Token自动清理任务...")
    # 注意：cleanup_expired_tokens现在是一个同步方法，已经有后台任务在image.py中处理


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("🛑 安全图床服务关闭")
    
    # 停止Token清理任务
    image_processor.stop_cleanup_task()


# 异常处理器
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404处理器"""
    return {
        "error": "Not Found",
        "detail": "The requested resource was not found",
        "path": request.url.path
    }


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    """403处理器"""
    return {
        "error": "Forbidden",
        "detail": str(exc.detail) if hasattr(exc, 'detail') else "Access denied",
        "client_ip": request.client.host
    }


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """500处理器"""
    logger.error(f"内部错误: {exc}")
    return {
        "error": "Internal Server Error",
        "detail": "An internal error occurred",
        "path": request.url.path
    }


# 导出应用实例
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="127.0.0.1",  # 仅监听本地
        port=settings.image_server_port,
        log_level="info"
    )
