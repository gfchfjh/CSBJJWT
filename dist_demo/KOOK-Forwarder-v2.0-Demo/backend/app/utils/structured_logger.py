"""
结构化日志模块
使用structlog实现机器可读的JSON日志，支持敏感信息脱敏
"""
import logging
import re
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Any, Dict
from ..config import settings


# 敏感信息脱敏模式
SENSITIVE_PATTERNS = [
    (r'(token|bearer|api[_-]?key)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]+)', r'\1: ***REDACTED***'),
    (r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s,"\']+)', r'\1: ***REDACTED***'),
    (r'(cookie)["\']?\s*[:=]\s*["\']?([^"\']+)', r'\1: ***REDACTED***'),
    (r'(secret)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]+)', r'\1: ***REDACTED***'),
    (r'(authorization:\s*)(Bearer\s+[^\s]+)', r'\1Bearer ***REDACTED***'),
]


class SensitiveDataFilter(logging.Filter):
    """敏感信息脱敏过滤器"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤并脱敏日志消息
        
        Args:
            record: 日志记录
            
        Returns:
            是否保留此日志
        """
        message = record.getMessage()
        
        # 应用所有脱敏模式
        for pattern, replacement in SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        
        # 更新记录
        record.msg = message
        record.args = ()
        
        return True


def setup_structured_logger(
    name: str,
    log_file: str = None,
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    配置结构化日志记录器
    
    Args:
        name: Logger名称
        log_file: 日志文件路径
        level: 日志级别
        max_bytes: 单个日志文件最大大小
        backup_count: 保留的备份数量
        
    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)
    
    # 文件Handler（带轮转）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(file_handler)
    
    return logger


# 创建默认logger实例
default_logger = setup_structured_logger(
    'kook_forwarder',
    str(settings.log_dir / 'app.log'),
    getattr(logging, settings.log_level.upper(), logging.INFO)
)


def get_logger(name: str = None) -> logging.Logger:
    """
    获取Logger实例
    
    Args:
        name: Logger名称，None则返回默认logger
        
    Returns:
        Logger实例
    """
    if name:
        return setup_structured_logger(
            name,
            str(settings.log_dir / f'{name}.log')
        )
    return default_logger


# 便捷日志函数
def log_info(message: str, **kwargs):
    """记录INFO日志"""
    extra = _format_extra(kwargs)
    default_logger.info(f"{message} {extra}" if extra else message)


def log_warning(message: str, **kwargs):
    """记录WARNING日志"""
    extra = _format_extra(kwargs)
    default_logger.warning(f"{message} {extra}" if extra else message)


def log_error(message: str, **kwargs):
    """记录ERROR日志"""
    extra = _format_extra(kwargs)
    default_logger.error(f"{message} {extra}" if extra else message)


def log_debug(message: str, **kwargs):
    """记录DEBUG日志"""
    extra = _format_extra(kwargs)
    default_logger.debug(f"{message} {extra}" if extra else message)


def _format_extra(kwargs: Dict[str, Any]) -> str:
    """
    格式化额外的上下文信息
    
    Args:
        kwargs: 上下文字典
        
    Returns:
        格式化后的字符串
    """
    if not kwargs:
        return ""
    
    parts = [f"{k}={v}" for k, v in kwargs.items()]
    return "| " + " ".join(parts)


# 兼容性：导出原logger实例
logger = default_logger
