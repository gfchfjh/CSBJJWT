"""
错误码和用户友好的错误消息管理
提供统一的错误处理和用户提示
"""
from enum import Enum
from typing import Dict, Optional


class ErrorCode(str, Enum):
    """错误码枚举"""
    
    # 通用错误 (1000-1099)
    UNKNOWN_ERROR = "1000"
    INVALID_PARAMETER = "1001"
    MISSING_PARAMETER = "1002"
    DATABASE_ERROR = "1003"
    NETWORK_ERROR = "1004"
    TIMEOUT_ERROR = "1005"
    RATE_LIMIT_ERROR = "1006"
    
    # 认证错误 (1100-1199)
    AUTH_FAILED = "1100"
    INVALID_TOKEN = "1101"
    TOKEN_EXPIRED = "1102"
    INSUFFICIENT_PERMISSION = "1103"
    PASSWORD_INCORRECT = "1104"
    
    # KOOK账号相关 (1200-1299)
    KOOK_LOGIN_FAILED = "1200"
    KOOK_COOKIE_INVALID = "1201"
    KOOK_ACCOUNT_BANNED = "1202"
    KOOK_CAPTCHA_REQUIRED = "1203"
    KOOK_CONNECTION_FAILED = "1204"
    KOOK_ACCOUNT_NOT_FOUND = "1205"
    KOOK_SCRAPER_ERROR = "1206"
    
    # Bot配置相关 (1300-1399)
    BOT_NOT_FOUND = "1300"
    BOT_CONFIG_INVALID = "1301"
    DISCORD_WEBHOOK_INVALID = "1302"
    TELEGRAM_TOKEN_INVALID = "1303"
    FEISHU_APP_INVALID = "1304"
    BOT_TEST_FAILED = "1305"
    
    # 消息转发相关 (1400-1499)
    MESSAGE_SEND_FAILED = "1400"
    MESSAGE_QUEUE_FULL = "1401"
    MESSAGE_FORMAT_ERROR = "1402"
    IMAGE_DOWNLOAD_FAILED = "1403"
    IMAGE_UPLOAD_FAILED = "1404"
    CHANNEL_MAPPING_NOT_FOUND = "1405"
    
    # 系统配置相关 (1500-1599)
    CONFIG_NOT_FOUND = "1500"
    CONFIG_INVALID = "1501"
    EMAIL_CONFIG_INCOMPLETE = "1502"
    SMTP_CONNECTION_FAILED = "1503"
    EMAIL_SEND_FAILED = "1504"
    
    # 验证码相关 (1600-1699)
    VERIFICATION_CODE_INVALID = "1600"
    VERIFICATION_CODE_EXPIRED = "1601"
    VERIFICATION_CODE_SEND_FAILED = "1602"


# 错误消息映射表
ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    # 通用错误
    ErrorCode.UNKNOWN_ERROR: {
        "message": "系统错误，请稍后重试",
        "suggestion": "如果问题持续存在，请联系技术支持"
    },
    ErrorCode.INVALID_PARAMETER: {
        "message": "参数格式不正确",
        "suggestion": "请检查输入的信息是否符合要求"
    },
    ErrorCode.MISSING_PARAMETER: {
        "message": "缺少必填参数",
        "suggestion": "请填写所有必填字段"
    },
    ErrorCode.DATABASE_ERROR: {
        "message": "数据库操作失败",
        "suggestion": "请稍后重试，如果问题持续请检查数据库连接"
    },
    ErrorCode.NETWORK_ERROR: {
        "message": "网络连接失败",
        "suggestion": "请检查网络连接是否正常"
    },
    ErrorCode.TIMEOUT_ERROR: {
        "message": "操作超时",
        "suggestion": "请检查网络连接，或稍后重试"
    },
    ErrorCode.RATE_LIMIT_ERROR: {
        "message": "操作过于频繁，请稍后再试",
        "suggestion": "系统正在限流保护中，请等待一段时间后重试"
    },
    
    # 认证错误
    ErrorCode.AUTH_FAILED: {
        "message": "认证失败",
        "suggestion": "请检查用户名和密码是否正确"
    },
    ErrorCode.INVALID_TOKEN: {
        "message": "认证令牌无效",
        "suggestion": "请重新登录"
    },
    ErrorCode.TOKEN_EXPIRED: {
        "message": "认证令牌已过期",
        "suggestion": "请重新登录"
    },
    ErrorCode.PASSWORD_INCORRECT: {
        "message": "密码错误",
        "suggestion": "请检查密码是否正确，或使用忘记密码功能"
    },
    
    # KOOK账号相关
    ErrorCode.KOOK_LOGIN_FAILED: {
        "message": "KOOK账号登录失败",
        "suggestion": "请检查账号密码是否正确，或尝试重新导入Cookie"
    },
    ErrorCode.KOOK_COOKIE_INVALID: {
        "message": "KOOK Cookie无效或已过期",
        "suggestion": "请重新获取并导入Cookie，或使用账号密码登录"
    },
    ErrorCode.KOOK_ACCOUNT_BANNED: {
        "message": "KOOK账号已被封禁",
        "suggestion": "请联系KOOK客服了解封禁原因"
    },
    ErrorCode.KOOK_CAPTCHA_REQUIRED: {
        "message": "需要验证码验证",
        "suggestion": "请输入验证码，或稍后重试"
    },
    ErrorCode.KOOK_CONNECTION_FAILED: {
        "message": "无法连接到KOOK服务器",
        "suggestion": "请检查网络连接，确认KOOK服务是否正常"
    },
    ErrorCode.KOOK_ACCOUNT_NOT_FOUND: {
        "message": "KOOK账号不存在",
        "suggestion": "请先添加KOOK账号"
    },
    ErrorCode.KOOK_SCRAPER_ERROR: {
        "message": "KOOK消息抓取失败",
        "suggestion": "请重启服务，或检查日志了解详细错误"
    },
    
    # Bot配置相关
    ErrorCode.BOT_NOT_FOUND: {
        "message": "Bot配置不存在",
        "suggestion": "请先添加并配置Bot"
    },
    ErrorCode.BOT_CONFIG_INVALID: {
        "message": "Bot配置信息不完整或格式错误",
        "suggestion": "请检查所有必填字段是否正确填写"
    },
    ErrorCode.DISCORD_WEBHOOK_INVALID: {
        "message": "Discord Webhook URL无效",
        "suggestion": "请检查Webhook URL格式是否正确（应以https://discord.com/api/webhooks/开头）"
    },
    ErrorCode.TELEGRAM_TOKEN_INVALID: {
        "message": "Telegram Bot Token无效",
        "suggestion": "请检查Token是否正确，或重新从@BotFather获取"
    },
    ErrorCode.FEISHU_APP_INVALID: {
        "message": "飞书应用配置无效",
        "suggestion": "请检查App ID和App Secret是否正确"
    },
    ErrorCode.BOT_TEST_FAILED: {
        "message": "Bot测试连接失败",
        "suggestion": "请检查配置是否正确，确认目标平台服务正常"
    },
    
    # 消息转发相关
    ErrorCode.MESSAGE_SEND_FAILED: {
        "message": "消息发送失败",
        "suggestion": "请检查Bot配置和网络连接，或查看日志了解详细错误"
    },
    ErrorCode.MESSAGE_QUEUE_FULL: {
        "message": "消息队列已满",
        "suggestion": "系统正在处理大量消息，请稍后重试"
    },
    ErrorCode.MESSAGE_FORMAT_ERROR: {
        "message": "消息格式转换失败",
        "suggestion": "消息内容可能包含不支持的格式"
    },
    ErrorCode.IMAGE_DOWNLOAD_FAILED: {
        "message": "图片下载失败",
        "suggestion": "请检查网络连接，或确认图片URL是否有效"
    },
    ErrorCode.IMAGE_UPLOAD_FAILED: {
        "message": "图片上传失败",
        "suggestion": "图片可能过大或格式不支持，请尝试其他图片策略"
    },
    ErrorCode.CHANNEL_MAPPING_NOT_FOUND: {
        "message": "未找到频道映射配置",
        "suggestion": "请先在频道映射页面配置转发规则"
    },
    
    # 系统配置相关
    ErrorCode.CONFIG_NOT_FOUND: {
        "message": "配置不存在",
        "suggestion": "请先完成相关配置"
    },
    ErrorCode.CONFIG_INVALID: {
        "message": "配置信息无效",
        "suggestion": "请检查配置项是否正确"
    },
    ErrorCode.EMAIL_CONFIG_INCOMPLETE: {
        "message": "邮件配置不完整",
        "suggestion": "请填写SMTP服务器、用户名、密码等必填项"
    },
    ErrorCode.SMTP_CONNECTION_FAILED: {
        "message": "无法连接到SMTP服务器",
        "suggestion": "请检查服务器地址、端口是否正确，确认防火墙设置"
    },
    ErrorCode.EMAIL_SEND_FAILED: {
        "message": "邮件发送失败",
        "suggestion": "请检查邮件配置和网络连接"
    },
    
    # 验证码相关
    ErrorCode.VERIFICATION_CODE_INVALID: {
        "message": "验证码错误",
        "suggestion": "请输入正确的验证码"
    },
    ErrorCode.VERIFICATION_CODE_EXPIRED: {
        "message": "验证码已过期",
        "suggestion": "请重新获取验证码"
    },
    ErrorCode.VERIFICATION_CODE_SEND_FAILED: {
        "message": "验证码发送失败",
        "suggestion": "请检查邮件配置，或稍后重试"
    },
}


class UserFriendlyError(Exception):
    """用户友好的异常类"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        detail: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        """
        初始化用户友好的异常
        
        Args:
            error_code: 错误码
            detail: 额外的错误详情（用户可见）
            technical_detail: 技术详情（仅记录日志）
        """
        self.error_code = error_code
        self.detail = detail
        self.technical_detail = technical_detail
        
        # 获取错误消息
        error_info = ERROR_MESSAGES.get(error_code, {})
        self.message = error_info.get("message", "未知错误")
        self.suggestion = error_info.get("suggestion", "请联系技术支持")
        
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """转换为字典格式（用于API响应）"""
        result = {
            "error_code": self.error_code,
            "message": self.message,
            "suggestion": self.suggestion
        }
        
        if self.detail:
            result["detail"] = self.detail
        
        return result


def get_error_message(error_code: ErrorCode) -> Dict[str, str]:
    """
    获取错误消息
    
    Args:
        error_code: 错误码
        
    Returns:
        包含message和suggestion的字典
    """
    return ERROR_MESSAGES.get(
        error_code,
        {
            "message": "未知错误",
            "suggestion": "请联系技术支持"
        }
    )


def format_api_error(error_code: ErrorCode, detail: Optional[str] = None) -> dict:
    """
    格式化API错误响应
    
    Args:
        error_code: 错误码
        detail: 额外详情
        
    Returns:
        错误响应字典
    """
    error_info = get_error_message(error_code)
    
    result = {
        "success": False,
        "error_code": error_code,
        "message": error_info["message"],
        "suggestion": error_info["suggestion"]
    }
    
    if detail:
        result["detail"] = detail
    
    return result
