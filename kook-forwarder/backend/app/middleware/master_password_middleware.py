"""
主密码验证中间件
✅ P0-8优化：保护API访问
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from ..utils.master_password import master_password_manager
from ..utils.logger import logger


async def master_password_middleware(request: Request, call_next):
    """
    主密码验证中间件
    
    排除的路径：
    - /api/auth/unlock - 解锁接口
    - /health - 健康检查
    - / - 根路径
    """
    # 排除不需要验证的路径
    excluded_paths = [
        "/api/auth/unlock",
        "/api/auth/set-master-password",
        "/health",
        "/"
    ]
    
    # 检查是否在排除列表中
    for excluded in excluded_paths:
        if request.url.path == excluded or request.url.path.startswith(excluded + "/"):
            return await call_next(request)
    
    # 检查是否已设置主密码
    if not master_password_manager.is_password_set():
        # 未设置密码，允许访问
        return await call_next(request)
    
    # 获取Token
    token = request.headers.get("X-Master-Token")
    if not token:
        # 尝试从Cookie获取
        token = request.cookies.get("master_token")
    
    # 验证Token
    if not token or not master_password_manager.is_unlocked(token):
        logger.warning(f"未授权访问尝试: {request.url.path} from {request.client.host}")
        return JSONResponse(
            status_code=401,
            content={
                "error": "unauthorized",
                "message": "请先解锁应用",
                "require_master_password": True
            }
        )
    
    # Token有效，继续处理请求
    return await call_next(request)
