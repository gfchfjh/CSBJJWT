"""
全局异常处理器（终极版）
======================
功能：
1. 捕获所有未处理异常
2. 记录详细错误日志
3. 返回友好错误信息
4. 崩溃报告收集

作者：KOOK Forwarder Team
日期：2025-10-25
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import traceback
import json
from pathlib import Path
from ..utils.logger import logger
from ..utils.error_messages_friendly import friendly_errors
from ..config import settings


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理器
    
    Args:
        request: 请求对象
        exc: 异常对象
        
    Returns:
        JSON响应
    """
    # 提取错误信息
    error_type = type(exc).__name__
    error_message = str(exc)
    stack_trace = traceback.format_exc()
    
    # 记录详细错误日志
    logger.error("=" * 70)
    logger.error(f"❌ 未处理的异常: {error_type}")
    logger.error(f"📍 请求URL: {request.url}")
    logger.error(f"🔧 请求方法: {request.method}")
    logger.error(f"💬 错误消息: {error_message}")
    logger.error(f"📚 堆栈跟踪:\n{stack_trace}")
    logger.error("=" * 70)
    
    # 收集崩溃信息
    crash_report = {
        'timestamp': datetime.now().isoformat(),
        'exception_type': error_type,
        'exception_message': error_message,
        'traceback': stack_trace,
        'request_url': str(request.url),
        'request_method': request.method,
        'request_headers': dict(request.headers),
        'client_host': request.client.host if request.client else 'unknown'
    }
    
    # 保存崩溃报告
    try:
        crash_log_path = settings.log_dir / 'crashes.jsonl'
        with open(crash_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(crash_report, ensure_ascii=False) + '\n')
        logger.info(f"💾 崩溃报告已保存: {crash_log_path}")
    except Exception as e:
        logger.error(f"保存崩溃报告失败: {e}")
    
    # 转换为友好错误信息
    friendly_error = friendly_errors.translate(
        exc,
        context={
            'url': str(request.url),
            'method': request.method
        }
    )
    
    # 返回友好错误响应
    return JSONResponse(
        status_code=500,
        content={
            'success': False,
            'error': {
                'icon': friendly_error['icon'],
                'title': friendly_error['title'],
                'message': friendly_error['message'],
                'suggestions': friendly_error['suggestions'],
                'auto_fix': friendly_error.get('auto_fix'),
                'technical_details': friendly_error['technical_details'] if settings.debug else None
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP异常处理器
    
    Args:
        request: 请求对象
        exc: HTTP异常
        
    Returns:
        JSON响应
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'success': False,
            'error': {
                'icon': '⚠️',
                'title': 'HTTP错误',
                'message': exc.detail,
                'status_code': exc.status_code
            }
        }
    )
