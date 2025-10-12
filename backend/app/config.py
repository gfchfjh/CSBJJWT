"""配置管理模块"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """系统配置"""
    
    # 应用基础配置
    APP_NAME: str = "KOOK消息转发系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务端口
    API_PORT: int = 9527
    REDIS_PORT: int = 6379
    IMAGE_SERVER_PORT: int = 9528
    
    # 数据存储路径
    BASE_DATA_DIR: Path = Path.home() / "Documents" / "KookForwarder" / "data"
    DATABASE_PATH: Path = BASE_DATA_DIR / "config.db"
    REDIS_DATA_DIR: Path = BASE_DATA_DIR / "redis"
    IMAGE_STORAGE_DIR: Path = BASE_DATA_DIR / "images"
    LOG_DIR: Path = BASE_DATA_DIR / "logs"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # 消息队列配置
    MESSAGE_QUEUE_NAME: str = "kook:messages"
    FAILED_QUEUE_NAME: str = "kook:failed"
    
    # 限流配置
    DISCORD_RATE_LIMIT: int = 5  # 每5秒最多5条
    TELEGRAM_RATE_LIMIT: int = 30  # 每秒最多30条
    FEISHU_RATE_LIMIT: int = 20  # 每秒最多20条
    
    # 图片处理配置
    IMAGE_MAX_SIZE_MB: int = 50
    IMAGE_STORAGE_MAX_GB: int = 10
    IMAGE_CLEANUP_DAYS: int = 7
    IMAGE_TOKEN_EXPIRE_HOURS: int = 2
    
    # 重试配置
    MAX_RETRY_TIMES: int = 3
    RETRY_DELAY_SECONDS: int = 30
    
    # 安全配置
    ENCRYPTION_KEY: str = ""  # 运行时生成
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def initialize_directories(self):
        """初始化必要的目录"""
        for directory in [
            self.BASE_DATA_DIR,
            self.REDIS_DATA_DIR,
            self.IMAGE_STORAGE_DIR,
            self.LOG_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.initialize_directories()
