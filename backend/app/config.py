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
    app_version: str = "1.4.0"  # 更新版本号
    debug: bool = False
    data_dir: Path = DATA_DIR
    
    # Redis嵌入式配置
    redis_embedded: bool = True  # 是否使用嵌入式Redis（自动启动）
    redis_auto_start: bool = True  # 是否自动启动Redis
    
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
    api_token: Optional[str] = None  # API访问Token（如果设置则启用认证）
    api_token_header: str = "X-API-Token"  # Token请求头名称
    
    # 验证码自动识别配置
    captcha_2captcha_api_key: Optional[str] = None
    captcha_auto_solve: bool = True  # 是否启用自动识别
    
    # 健康检查配置
    health_check_interval: int = 300  # 健康检查间隔（秒）
    health_check_enabled: bool = True  # 是否启用健康检查
    
    # 自动更新配置
    auto_update_enabled: bool = True  # 是否启用自动更新检查
    auto_update_check_interval: int = 86400  # 检查间隔（秒，默认24小时）
    github_repo: str = "gfchfjh/CSBJJWT"  # GitHub仓库
    
    # 选择器配置
    selector_config_path: Path = DATA_DIR / "selectors.yaml"  # 选择器配置文件路径
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 创建全局配置实例
settings = Settings()

# 创建日志目录
settings.log_dir.mkdir(parents=True, exist_ok=True)
