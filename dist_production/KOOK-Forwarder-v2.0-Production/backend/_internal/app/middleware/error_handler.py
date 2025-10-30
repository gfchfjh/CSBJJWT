"""
全局错误处理中间件
捕获并翻译所有异常为用户友好的消息
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from ..utils.error_translator import error_translator
from ..utils.logger import logger


async def global_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理器
    
    捕获所有未处理的异常并返回用户友好的错误消息
    """
    # 记录原始错误
    logger.error(f"全局错误捕获: {type(exc).__name__}: {str(exc)}")
    logger.error(f"请求路径: {request.url.path}")
    logger.error(f"错误堆栈:\n{traceback.format_exc()}")
    
    # 翻译错误
    error_info = error_translator.translate_error(exc)
    
    # 判断HTTP状态码
    if isinstance(exc, StarletteHTTPException):
        status_code = exc.status_code
    elif isinstance(exc, RequestValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        # 特殊处理验证错误
        error_info = {
            "title": "输入数据验证失败",
            "message": "提供的数据格式不正确，请检查输入",
            "actions": ["检查输入格式", "查看API文档"],
            "severity": "error",
            "technical_detail": str(exc),
            "validation_errors": exc.errors()
        }
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # 返回用户友好的错误响应
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": error_info["title"],
            "error_detail": error_info["message"],
            "suggested_actions": error_info["actions"],
            "severity": error_info["severity"],
            "technical_info": error_info.get("technical_detail"),
            "show_technical": error_info.get("show_technical", False),
            # 额外的上下文信息
            "request_path": str(request.url.path),
            "timestamp": str(request.state.request_time) if hasattr(request.state, 'request_time') else None
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    HTTP异常处理器
    
    处理标准的HTTP异常（404, 403等）
    """
    error_messages = {
        404: {
            "title": "页面不存在",
            "message": "您访问的页面不存在，请检查URL是否正确",
            "actions": ["返回首页", "查看文档"]
        },
        403: {
            "title": "权限不足",
            "message": "您没有权限访问此资源",
            "actions": ["登录", "联系管理员"]
        },
        401: {
            "title": "未授权",
            "message": "请先登录后再访问",
            "actions": ["登录"]
        },
        500: {
            "title": "服务器错误",
            "message": "服务器内部错误，请稍后重试",
            "actions": ["刷新页面", "稍后重试", "联系支持"]
        }
    }
    
    error_info = error_messages.get(exc.status_code, {
        "title": f"HTTP {exc.status_code}",
        "message": exc.detail,
        "actions": ["刷新页面"]
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": error_info["title"],
            "error_detail": error_info["message"],
            "suggested_actions": error_info["actions"],
            "severity": "error",
            "request_path": str(request.url.path)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    请求验证异常处理器
    
    处理Pydantic模型验证错误
    """
    # 提取验证错误详情
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_messages.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "输入验证失败",
            "error_detail": "请求数据格式不正确",
            "validation_errors": error_messages,
            "suggested_actions": ["检查输入格式", "查看API文档"],
            "severity": "error",
            "request_path": str(request.url.path)
        }
    )
