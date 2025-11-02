from typing import Optional, Dict, Any
"""
API认证中间件（✅ P2-5优化：全局API认证）
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from ..config import settings
from ..utils.logger import logger


class APIAuthMiddleware(BaseHTTPMiddleware):
    """
    API认证中间件（✅ P2-5优化）
    
    功能：
    1. 验证所有API请求的Token
    2. 白名单路径（登录、健康检查等）无需认证
    3. 记录未授权访问尝试
    """
    
    # 无需认证的路径（白名单）
    PUBLIC_PATHS = [
        "/auth/status",
        "/auth/setup",
        "/auth/login",
        "/auth/reset-password",
        "/password-reset",
        "/api/cookie-import/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]
    
    def __init__(self, app, enabled: bool = True):
        """
        初始化中间件
        
        Args:
            app: FastAPI应用
            enabled: 是否启用认证（默认启用，可通过配置关闭）
        """
        super().__init__(app)
        self.enabled = enabled and settings.api_token is not None
        
        if self.enabled:
            logger.info("✅ API认证中间件已启用")
        else:
            logger.warning("⚠️ API认证中间件未启用（未配置api_token）")
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        处理请求
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            响应对象
        """
        # 如果未启用认证，直接放行
        if not self.enabled:
            return await call_next(request)
        
        # 检查是否是白名单路径
        path = request.url.path
        
        # 白名单路径直接放行
        if self._is_public_path(path):
            return await call_next(request)
        
        # 检查Token
        token = self._extract_token(request)
        
        if not token:
            logger.warning(f"未授权访问尝试: {request.client.host} → {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "未提供API Token",
                    "hint": "请在请求头中添加: X-API-Token: your_token"
                }
            )
        
        # 验证Token
        if not self._verify_token(token):
            logger.warning(f"无效Token访问尝试: {request.client.host} → {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "API Token无效",
                    "hint": "请检查Token是否正确"
                }
            )
        
        # Token有效，继续处理
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """
        检查是否是公开路径
        
        Args:
            path: 请求路径
            
        Returns:
            是否是公开路径
        """
        # 精确匹配
        if path in self.PUBLIC_PATHS:
            return True
        
        # 前缀匹配
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        
        return False
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """
        从请求中提取Token
        
        优先级：
        1. Header: X-API-Token
        2. Header: Authorization (Bearer token)
        3. Query: token
        
        Args:
            request: 请求对象
            
        Returns:
            Token字符串，如果不存在返回None
        """
        # 1. 检查自定义Header
        token = request.headers.get(settings.api_token_header)
        if token:
            return token
        
        # 2. 检查Authorization头
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]
        
        # 3. 检查Query参数
        token = request.query_params.get("token")
        if token:
            return token
        
        return None
    
    def _verify_token(self, token: str) -> bool:
        """
        验证Token是否有效
        
        Args:
            token: Token字符串
            
        Returns:
            是否有效
        """
        # 简单验证：与配置中的token比对
        return token == settings.api_token


# 创建中间件实例（供main.py使用）
def create_auth_middleware(app, enabled: bool = True):
    """
    创建认证中间件
    
    Args:
        app: FastAPI应用
        enabled: 是否启用
        
    Returns:
        中间件实例
    """
    return APIAuthMiddleware(app, enabled=enabled)
