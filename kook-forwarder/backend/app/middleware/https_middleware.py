"""
HTTPS强制中间件
✅ P1-4优化: 防止Cookie劫持和中间人攻击
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List


class HTTPSOnlyMiddleware(BaseHTTPMiddleware):
    """
    HTTPS强制中间件
    
    功能:
    1. 生产环境强制HTTPS连接
    2. 本地开发环境豁免
    3. 可配置豁免主机列表
    
    使用方式:
    ```python
    from .middleware.https_middleware import HTTPSOnlyMiddleware
    
    app.add_middleware(
        HTTPSOnlyMiddleware,
        exempt_hosts=['127.0.0.1', 'localhost'],
        enforce=True
    )
    ```
    """
    
    def __init__(self, app, exempt_hosts: List[str] = None, enforce: bool = True):
        """
        初始化中间件
        
        Args:
            app: FastAPI应用
            exempt_hosts: 豁免主机列表（默认: ['127.0.0.1', 'localhost']）
            enforce: 是否强制HTTPS（可通过配置关闭）
        """
        super().__init__(app)
        self.exempt_hosts = exempt_hosts or ['127.0.0.1', 'localhost', '::1']
        self.enforce = enforce
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 如果未启用强制HTTPS，直接放行
        if not self.enforce:
            return await call_next(request)
        
        # 检查是否为豁免主机
        client_host = request.client.host if request.client else None
        if client_host in self.exempt_hosts:
            return await call_next(request)
        
        # 检查是否使用HTTPS
        # 注意: 考虑反向代理的情况（检查X-Forwarded-Proto头）
        is_https = False
        
        # 方法1: 检查URL scheme
        if request.url.scheme == 'https':
            is_https = True
        
        # 方法2: 检查X-Forwarded-Proto头（反向代理）
        forwarded_proto = request.headers.get('X-Forwarded-Proto', '').lower()
        if forwarded_proto == 'https':
            is_https = True
        
        # 方法3: 检查X-Forwarded-Ssl头
        forwarded_ssl = request.headers.get('X-Forwarded-Ssl', '').lower()
        if forwarded_ssl == 'on':
            is_https = True
        
        # 如果不是HTTPS，拒绝请求
        if not is_https:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "HTTPS_REQUIRED",
                    "message": "此接口仅支持HTTPS连接，请使用https://访问",
                    "hint": "为了保护您的数据安全，敏感接口必须通过HTTPS访问"
                }
            )
        
        # HTTPS连接，继续处理
        return await call_next(request)


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全响应头中间件
    
    功能:
    1. 添加安全相关的HTTP响应头
    2. 防止XSS、点击劫持等攻击
    
    使用方式:
    ```python
    app.add_middleware(SecureHeadersMiddleware)
    ```
    """
    
    def __init__(self, app, hsts_enabled: bool = True):
        """
        初始化中间件
        
        Args:
            app: FastAPI应用
            hsts_enabled: 是否启用HSTS（HTTP Strict Transport Security）
        """
        super().__init__(app)
        self.hsts_enabled = hsts_enabled
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        response = await call_next(request)
        
        # 添加安全响应头
        
        # 1. X-Content-Type-Options: 防止MIME类型嗅探
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # 2. X-Frame-Options: 防止点击劫持
        response.headers['X-Frame-Options'] = 'DENY'
        
        # 3. X-XSS-Protection: XSS过滤器
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # 4. Content-Security-Policy: 内容安全策略
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:;"
        )
        
        # 5. Referrer-Policy: 引用策略
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # 6. Permissions-Policy: 权限策略（替代Feature-Policy）
        response.headers['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
        
        # 7. HSTS: 强制HTTPS（仅HTTPS连接时添加）
        if self.hsts_enabled and request.url.scheme == 'https':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
