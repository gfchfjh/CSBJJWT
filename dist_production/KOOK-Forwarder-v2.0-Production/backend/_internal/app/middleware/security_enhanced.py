"""
安全中间件（增强版）
P2-7~9: 安全加固

功能：
1. 强制 API Token 认证
2. 密码复杂度验证
3. 审计日志
4. 请求限流
5. 安全响应头
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import hashlib
from ..utils.logger import logger
from ..utils.audit_logger import audit_logger
from ..config import settings


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(self, app, require_token: bool = True):
        super().__init__(app)
        self.require_token = require_token
        
        # 白名单路径（不需要 Token）
        self.whitelist_paths = [
            "/",
            "/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/password-reset/request",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        
        # 请求限流（简单实现）
        self.request_counts = {}  # {ip: [(timestamp, path), ...]}
        self.rate_limit_window = 60  # 1 分钟窗口
        self.rate_limit_max = 100  # 最多 100 个请求
    
    async def dispatch(self, request: Request, call_next: Callable):
        """处理请求"""
        start_time = time.time()
        
        # 1. 安全响应头
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
        }
        
        # 2. API Token 认证（生产环境强制）
        if self.require_token and not settings.debug:
            if request.url.path not in self.whitelist_paths:
                if not await self._verify_token(request):
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "未授权：缺少或无效的 API Token"},
                        headers=headers
                    )
        
        # 3. 请求限流
        if not await self._check_rate_limit(request):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "请求过于频繁，请稍后再试"},
                headers=headers
            )
        
        # 4. 执行请求
        try:
            response = await call_next(request)
            
            # 添加安全响应头
            for key, value in headers.items():
                response.headers[key] = value
            
            # 5. 审计日志
            duration = time.time() - start_time
            await self._log_request(request, response.status_code, duration)
            
            return response
            
        except Exception as e:
            logger.error(f"请求处理异常: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "服务器内部错误"},
                headers=headers
            )
    
    async def _verify_token(self, request: Request) -> bool:
        """验证 API Token"""
        token = request.headers.get(settings.api_token_header)
        
        if not token:
            logger.warning(f"缺少 API Token: {request.url.path}")
            return False
        
        if token != settings.api_token:
            logger.warning(f"无效的 API Token: {request.url.path}")
            return False
        
        return True
    
    async def _check_rate_limit(self, request: Request) -> bool:
        """检查请求限流"""
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        current_time = time.time()
        
        # 清理过期记录
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                (ts, path) for ts, path in self.request_counts[client_ip]
                if current_time - ts < self.rate_limit_window
            ]
        else:
            self.request_counts[client_ip] = []
        
        # 检查是否超限
        if len(self.request_counts[client_ip]) >= self.rate_limit_max:
            logger.warning(f"⚠️ 请求限流: {client_ip} ({len(self.request_counts[client_ip])} 请求/分钟)")
            return False
        
        # 记录请求
        self.request_counts[client_ip].append((current_time, str(request.url.path)))
        
        return True
    
    async def _log_request(self, request: Request, status_code: int, duration: float):
        """记录请求审计日志"""
        try:
            log_data = {
                'method': request.method,
                'path': str(request.url.path),
                'client_ip': request.client.host if request.client else "unknown",
                'status_code': status_code,
                'duration_ms': int(duration * 1000),
                'user_agent': request.headers.get('user-agent', ''),
            }
            
            # 记录到审计日志
            audit_logger.log_api_request(log_data)
            
        except Exception as e:
            logger.error(f"记录审计日志失败: {str(e)}")


class PasswordValidator:
    """密码验证器（P2-8）"""
    
    @staticmethod
    def validate(password: str) -> tuple[bool, str]:
        """
        验证密码复杂度
        
        要求：
        - 至少 8 位
        - 包含大写字母
        - 包含小写字母
        - 包含数字
        - 包含特殊字符（可选）
        
        Args:
            password: 密码
            
        Returns:
            (是否有效, 错误消息)
        """
        if len(password) < 8:
            return False, "密码至少需要 8 位字符"
        
        if len(password) > 128:
            return False, "密码不能超过 128 位字符"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not has_upper:
            return False, "密码必须包含至少一个大写字母"
        
        if not has_lower:
            return False, "密码必须包含至少一个小写字母"
        
        if not has_digit:
            return False, "密码必须包含至少一个数字"
        
        # 可选：检查特殊字符
        # has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        # if not has_special:
        #     return False, "密码建议包含特殊字符"
        
        return True, "密码强度足够"
    
    @staticmethod
    def get_strength(password: str) -> str:
        """
        获取密码强度
        
        Returns:
            "weak" | "medium" | "strong"
        """
        score = 0
        
        # 长度
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # 字符类型
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 2
        
        if score <= 4:
            return "weak"
        elif score <= 7:
            return "medium"
        else:
            return "strong"


# 全局实例
password_validator = PasswordValidator()
