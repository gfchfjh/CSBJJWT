"""
日志工具模块
"""
from loguru import logger
from pathlib import Path
import sys
import re
from ..config import settings


def sanitize_log_message(message: str) -> str:
    """
    脱敏日志信息（v1.7.2新增）
    自动移除或隐藏敏感信息，防止泄露
    
    Args:
        message: 原始日志消息
        
    Returns:
        脱敏后的消息
    """
    if not isinstance(message, str):
        return message
    
    # 1. 脱敏Discord Webhook URL
    message = re.sub(
        r'(https://discord\.com/api/webhooks/\d{10,20}/)([a-zA-Z0-9_-]{20,})',
        r'\1***REDACTED***',
        message
    )
    
    # 2. 脱敏Telegram Bot Token (格式: 1234567890:ABC...)
    message = re.sub(
        r'\b\d{8,10}:[a-zA-Z0-9_-]{30,40}\b',
        '***TOKEN_REDACTED***',
        message
    )
    
    # 3. 脱敏飞书App Secret
    message = re.sub(
        r'(app_secret["\s:=]+)([a-zA-Z0-9]{20,})',
        r'\1***SECRET_REDACTED***',
        message,
        flags=re.IGNORECASE
    )
    
    # 4. 脱敏Cookie（长字符串）
    message = re.sub(
        r'("cookie":\s*")([^"]{50,})"',
        r'\1***COOKIE_REDACTED***"',
        message
    )
    
    # 5. 脱敏密码字段
    message = re.sub(
        r'(password["\s:=]+)([^\s,}\]]{6,})',
        r'\1***PASSWORD_REDACTED***',
        message,
        flags=re.IGNORECASE
    )
    
    # 6. 脱敏API Key
    message = re.sub(
        r'(api[_-]?key["\s:=]+)([a-zA-Z0-9]{20,})',
        r'\1***KEY_REDACTED***',
        message,
        flags=re.IGNORECASE
    )
    
    # 7. 脱敏邮箱地址（部分隐藏）
    message = re.sub(
        r'\b([a-zA-Z0-9._%+-]{1,3})[a-zA-Z0-9._%+-]*@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
        r'\1***@\2',
        message
    )
    
    # 8. 脱敏访问Token（JWT格式）
    message = re.sub(
        r'\beyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\b',
        '***JWT_TOKEN_REDACTED***',
        message
    )
    
    return message


def setup_logger():
    """配置日志系统"""
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出（带敏感信息脱敏）
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
        filter=lambda record: record.update(message=sanitize_log_message(record["message"])) or True
    )
    
    # 文件输出 - 所有日志（带敏感信息脱敏）
    logger.add(
        settings.log_dir / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="DEBUG",
        rotation="100 MB",  # 文件大小达到100MB时轮转（或每天00:00）
        retention=f"{settings.log_retention_days} days",  # 保留天数
        compression="zip",  # 压缩旧日志
        encoding="utf-8",
        enqueue=True,  # 异步写入，提高性能
        backtrace=True,  # 显示异常回溯
        diagnose=True,  # 显示变量值
        filter=lambda record: record.update(message=sanitize_log_message(record["message"])) or True
    )
    
    # 错误日志单独文件（带敏感信息脱敏）
    logger.add(
        settings.log_dir / "error_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="ERROR",
        rotation="50 MB",  # 错误日志50MB轮转
        retention=f"{settings.log_retention_days} days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        diagnose=True,
        filter=lambda record: record.update(message=sanitize_log_message(record["message"])) or True
    )
    
    logger.info(f"日志系统已初始化，日志目录: {settings.log_dir}")


# 初始化日志
setup_logger()
