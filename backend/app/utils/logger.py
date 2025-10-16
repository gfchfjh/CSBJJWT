"""
日志工具模块
"""
from loguru import logger
from pathlib import Path
import sys
from ..config import settings


def setup_logger():
    """配置日志系统"""
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # 文件输出 - 所有日志
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
        diagnose=True  # 显示变量值
    )
    
    # 错误日志单独文件
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
        diagnose=True
    )
    
    logger.info(f"日志系统已初始化，日志目录: {settings.log_dir}")


# 初始化日志
setup_logger()
