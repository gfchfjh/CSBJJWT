"""
统一异常处理模块（✅ 优化12：重构错误处理）

定义了所有自定义异常类型，统一错误处理逻辑
"""
from typing import Dict, Any, Optional


class KookForwarderException(Exception):
    """
    基础异常类
    
    所有自定义异常都继承自此类
    """
    
    def __init__(self, message: str, error_code: str, **context):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码（用于前端识别）
            **context: 错误上下文信息
        """
        self.message = message
        self.error_code = error_code
        self.context = context
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context
        }


# ==================== 登录相关异常 ====================

class LoginException(KookForwarderException):
    """登录异常基类"""
    pass


class LoginFailedException(LoginException):
    """登录失败异常"""
    
    def __init__(self, reason: str, email: Optional[str] = None):
        super().__init__(
            message=f"KOOK登录失败: {reason}",
            error_code="LOGIN_FAILED",
            reason=reason,
            email=email
        )


class CookieExpiredException(LoginException):
    """Cookie过期异常"""
    
    def __init__(self, account_id: int):
        super().__init__(
            message=f"账号 {account_id} 的Cookie已过期",
            error_code="COOKIE_EXPIRED",
            account_id=account_id
        )


class CaptchaRequiredException(LoginException):
    """需要验证码异常"""
    
    def __init__(self, captcha_url: str, account_id: int):
        super().__init__(
            message="登录需要验证码",
            error_code="CAPTCHA_REQUIRED",
            captcha_url=captcha_url,
            account_id=account_id
        )


# ==================== 消息转发相关异常 ====================

class ForwardException(KookForwarderException):
    """消息转发异常基类"""
    pass


class MessageForwardException(ForwardException):
    """消息转发失败异常"""
    
    def __init__(self, platform: str, reason: str, message_id: Optional[str] = None):
        super().__init__(
            message=f"{platform}消息转发失败: {reason}",
            error_code="FORWARD_FAILED",
            platform=platform,
            reason=reason,
            message_id=message_id
        )


class DiscordWebhookException(ForwardException):
    """Discord Webhook异常"""
    
    def __init__(self, webhook_url: str, reason: str, status_code: Optional[int] = None):
        super().__init__(
            message=f"Discord Webhook失败: {reason}",
            error_code="DISCORD_WEBHOOK_ERROR",
            webhook_url=webhook_url[:50] + "...",  # 截断URL
            reason=reason,
            status_code=status_code
        )


class TelegramBotException(ForwardException):
    """Telegram Bot异常"""
    
    def __init__(self, token: str, reason: str, error_code: Optional[int] = None):
        super().__init__(
            message=f"Telegram Bot失败: {reason}",
            error_code="TELEGRAM_BOT_ERROR",
            token=token[:10] + "...",  # 仅显示前10位
            reason=reason,
            api_error_code=error_code
        )


class FeishuAppException(ForwardException):
    """飞书应用异常"""
    
    def __init__(self, app_id: str, reason: str, error_code: Optional[int] = None):
        super().__init__(
            message=f"飞书应用失败: {reason}",
            error_code="FEISHU_APP_ERROR",
            app_id=app_id,
            reason=reason,
            api_error_code=error_code
        )


# ==================== 图片处理相关异常 ====================

class ImageException(KookForwarderException):
    """图片处理异常基类"""
    pass


class ImageDownloadException(ImageException):
    """图片下载失败异常"""
    
    def __init__(self, url: str, reason: str, status_code: Optional[int] = None):
        super().__init__(
            message=f"图片下载失败: {reason}",
            error_code="IMAGE_DOWNLOAD_FAILED",
            url=url,
            reason=reason,
            status_code=status_code
        )


class ImageCompressionException(ImageException):
    """图片压缩失败异常"""
    
    def __init__(self, reason: str, original_size: Optional[int] = None):
        super().__init__(
            message=f"图片压缩失败: {reason}",
            error_code="IMAGE_COMPRESSION_FAILED",
            reason=reason,
            original_size=original_size
        )


class ImageUploadException(ImageException):
    """图片上传失败异常"""
    
    def __init__(self, platform: str, reason: str):
        super().__init__(
            message=f"{platform}图片上传失败: {reason}",
            error_code="IMAGE_UPLOAD_FAILED",
            platform=platform,
            reason=reason
        )


# ==================== 数据库相关异常 ====================

class DatabaseException(KookForwarderException):
    """数据库异常基类"""
    pass


class RecordNotFoundException(DatabaseException):
    """记录未找到异常"""
    
    def __init__(self, table: str, record_id: Any):
        super().__init__(
            message=f"{table}记录未找到: {record_id}",
            error_code="RECORD_NOT_FOUND",
            table=table,
            record_id=record_id
        )


class DuplicateRecordException(DatabaseException):
    """重复记录异常"""
    
    def __init__(self, table: str, field: str, value: Any):
        super().__init__(
            message=f"{table}中已存在 {field}={value} 的记录",
            error_code="DUPLICATE_RECORD",
            table=table,
            field=field,
            value=value
        )


# ==================== 配置相关异常 ====================

class ConfigException(KookForwarderException):
    """配置异常基类"""
    pass


class InvalidConfigException(ConfigException):
    """无效配置异常"""
    
    def __init__(self, field: str, reason: str, value: Optional[Any] = None):
        super().__init__(
            message=f"配置错误 ({field}): {reason}",
            error_code="INVALID_CONFIG",
            field=field,
            reason=reason,
            value=value
        )


class MissingConfigException(ConfigException):
    """缺失配置异常"""
    
    def __init__(self, field: str):
        super().__init__(
            message=f"缺少必需的配置项: {field}",
            error_code="MISSING_CONFIG",
            field=field
        )


# ==================== 限流相关异常 ====================

class RateLimitException(KookForwarderException):
    """限流异常"""
    
    def __init__(self, platform: str, wait_seconds: int):
        super().__init__(
            message=f"{platform}触发限流，需等待{wait_seconds}秒",
            error_code="RATE_LIMITED",
            platform=platform,
            wait_seconds=wait_seconds
        )


# ==================== 网络相关异常 ====================

class NetworkException(KookForwarderException):
    """网络异常基类"""
    pass


class ConnectionTimeoutException(NetworkException):
    """连接超时异常"""
    
    def __init__(self, target: str, timeout: int):
        super().__init__(
            message=f"连接{target}超时（{timeout}秒）",
            error_code="CONNECTION_TIMEOUT",
            target=target,
            timeout=timeout
        )


class APIException(NetworkException):
    """API调用异常"""
    
    def __init__(self, api_name: str, status_code: int, response: Optional[str] = None):
        super().__init__(
            message=f"API调用失败: {api_name} (HTTP {status_code})",
            error_code="API_ERROR",
            api_name=api_name,
            status_code=status_code,
            response=response[:200] if response else None  # 限制响应长度
        )


# ==================== 辅助函数 ====================

def get_exception_handler():
    """
    获取FastAPI异常处理器
    
    Usage:
        from .utils.exceptions import KookForwarderException, get_exception_handler
        
        @app.exception_handler(KookForwarderException)
        async def handle_kook_exception(request, exc):
            return get_exception_handler()(request, exc)
    """
    from fastapi.responses import JSONResponse
    from .logger import logger
    
    def handler(request, exc: KookForwarderException):
        # 记录错误日志
        logger.error(f"捕获异常: {exc.error_code} - {exc.message}")
        logger.error(f"异常上下文: {exc.context}")
        
        # 返回JSON响应
        return JSONResponse(
            status_code=400,  # 默认400，可根据错误类型调整
            content=exc.to_dict()
        )
    
    return handler


# ==================== 错误代码映射 ====================

ERROR_MESSAGES = {
    # 登录相关
    'LOGIN_FAILED': '登录失败，请检查账号密码',
    'COOKIE_EXPIRED': 'Cookie已过期，请重新登录',
    'CAPTCHA_REQUIRED': '需要验证码',
    
    # 转发相关
    'FORWARD_FAILED': '消息转发失败',
    'DISCORD_WEBHOOK_ERROR': 'Discord Webhook配置错误',
    'TELEGRAM_BOT_ERROR': 'Telegram Bot配置错误',
    'FEISHU_APP_ERROR': '飞书应用配置错误',
    
    # 图片处理
    'IMAGE_DOWNLOAD_FAILED': '图片下载失败',
    'IMAGE_COMPRESSION_FAILED': '图片压缩失败',
    'IMAGE_UPLOAD_FAILED': '图片上传失败',
    
    # 数据库
    'RECORD_NOT_FOUND': '记录不存在',
    'DUPLICATE_RECORD': '记录已存在',
    
    # 配置
    'INVALID_CONFIG': '配置无效',
    'MISSING_CONFIG': '缺少配置',
    
    # 网络
    'CONNECTION_TIMEOUT': '连接超时',
    'RATE_LIMITED': '触发限流',
    'API_ERROR': 'API调用失败',
}


def get_user_friendly_message(error_code: str) -> str:
    """
    获取用户友好的错误消息
    
    Args:
        error_code: 错误代码
        
    Returns:
        用户友好的错误消息
    """
    return ERROR_MESSAGES.get(error_code, '未知错误')
