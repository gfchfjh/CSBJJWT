"""
配置管理模块
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


# 获取用户文档目录
USER_HOME = Path.home()
APP_DATA_DIR = USER_HOME / "Documents" / "KookForwarder"
DATA_DIR = APP_DATA_DIR / "data"
IMAGE_DIR = DATA_DIR / "images"
REDIS_DIR = DATA_DIR / "redis"
DB_PATH = DATA_DIR / "config.db"

# 确保目录存在
for directory in [APP_DATA_DIR, DATA_DIR, IMAGE_DIR, REDIS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    app_name: str = "KOOK消息转发系统"
    app_version: str = "1.0.0"
    debug: bool = False
    data_dir: Path = DATA_DIR
    
    # API服务配置
    api_host: str = "127.0.0.1"
    api_port: int = 9527
    
    # Redis配置
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # 数据库配置
    database_url: str = f"sqlite:///{DB_PATH}"
    
    # 图床配置
    image_server_port: int = 9528
    image_max_size_gb: int = 10
    image_cleanup_days: int = 7
    image_storage_path: Path = IMAGE_DIR
    image_max_size_mb: float = 10.0  # 单个图片最大大小
    image_compression_quality: int = 85  # 压缩质量
    image_strategy: str = "smart"  # smart/direct/imgbed
    
    # 日志配置
    log_level: str = "INFO"
    log_retention_days: int = 3
    log_dir: Path = DATA_DIR / "logs"
    
    # 限流配置
    discord_rate_limit_calls: int = 5
    discord_rate_limit_period: int = 5
    telegram_rate_limit_calls: int = 30
    telegram_rate_limit_period: int = 1
    feishu_rate_limit_calls: int = 20
    feishu_rate_limit_period: int = 1
    
    # 消息重试配置
    message_retry_max: int = 3
    message_retry_interval: int = 30
    
    # 安全配置
    encryption_key: Optional[str] = None
    require_password: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 创建全局配置实例
settings = Settings()

# 创建日志目录
settings.log_dir.mkdir(parents=True, exist_ok=True)
