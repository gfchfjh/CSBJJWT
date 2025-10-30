"""
错误处理和友好提示模块
提供更友好的错误信息和解决方案建议
"""
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from .logger import logger


class ErrorCategory(Enum):
    """错误类别"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    PERMISSION = "permission"
    API_LIMIT = "api_limit"
    DATA_FORMAT = "data_format"
    STORAGE = "storage"
    PLATFORM_API = "platform_api"
    KOOK = "kook"
    UNKNOWN = "unknown"


class ErrorSolution:
    """错误解决方案"""
    
    # 错误信息模板
    ERROR_TEMPLATES = {
        # 网络错误
        "network_timeout": {
            "category": ErrorCategory.NETWORK,
            "user_message": "网络连接超时",
            "detail": "无法连接到{target}，请检查网络连接",
            "solutions": [
                "检查您的网络连接是否正常",
                "尝试访问 {target} 确认服务是否可用",
                "检查防火墙或代理设置",
                "稍后重试"
            ],
            "docs_link": None
        },
        "network_connection_refused": {
            "category": ErrorCategory.NETWORK,
            "user_message": "连接被拒绝",
            "detail": "无法连接到{target}",
            "solutions": [
                "检查目标服务是否正在运行",
                "确认端口号是否正确",
                "检查防火墙设置"
            ],
            "docs_link": None
        },
        
        # 认证错误
        "auth_invalid_cookie": {
            "category": ErrorCategory.AUTHENTICATION,
            "user_message": "Cookie无效或已过期",
            "detail": "KOOK Cookie验证失败",
            "solutions": [
                "重新获取KOOK Cookie",
                "确认Cookie格式正确（JSON数组格式）",
                "尝试使用账号密码登录"
            ],
            "docs_link": "docs/完整用户手册.md#cookie导入"
        },
        "auth_login_failed": {
            "category": ErrorCategory.AUTHENTICATION,
            "user_message": "登录失败",
            "detail": "KOOK账号密码验证失败",
            "solutions": [
                "检查账号和密码是否正确",
                "确认账号未被封禁",
                "尝试在浏览器手动登录验证",
                "如需验证码，请确保正确输入"
            ],
            "docs_link": "docs/完整用户手册.md#账号密码登录"
        },
        "auth_bot_token_invalid": {
            "category": ErrorCategory.AUTHENTICATION,
            "user_message": "Bot Token无效",
            "detail": "{platform} Bot Token验证失败",
            "solutions": [
                "检查Token是否正确复制",
                "确认Bot未被删除或禁用",
                "尝试重新创建Bot获取新Token"
            ],
            "docs_link": "docs/{platform}配置教程.md"
        },
        
        # 配置错误
        "config_missing_required": {
            "category": ErrorCategory.CONFIGURATION,
            "user_message": "缺少必需配置",
            "detail": "缺少配置项: {field}",
            "solutions": [
                "前往设置页面完善{field}配置",
                "参考文档了解如何配置",
                "使用配置向导重新配置"
            ],
            "docs_link": "docs/完整用户手册.md"
        },
        "config_invalid_format": {
            "category": ErrorCategory.CONFIGURATION,
            "user_message": "配置格式错误",
            "detail": "{field}格式不正确",
            "solutions": [
                "检查{field}格式是否符合要求",
                "参考示例配置",
                "尝试重新输入"
            ],
            "docs_link": None
        },
        
        # API限流错误
        "rate_limit_discord": {
            "category": ErrorCategory.API_LIMIT,
            "user_message": "Discord API限流",
            "detail": "消息发送过快，已被限流",
            "solutions": [
                "消息将自动排队等待发送",
                "如频繁出现，请减少频道映射数量",
                "考虑使用多个Webhook分散流量"
            ],
            "docs_link": None
        },
        "rate_limit_telegram": {
            "category": ErrorCategory.API_LIMIT,
            "user_message": "Telegram API限流",
            "detail": "消息发送过快，已被限流",
            "solutions": [
                "消息将自动排队等待发送",
                "如频繁出现，请减少频道映射数量"
            ],
            "docs_link": None
        },
        
        # 存储错误
        "storage_disk_full": {
            "category": ErrorCategory.STORAGE,
            "user_message": "磁盘空间不足",
            "detail": "磁盘使用率: {usage_percent}%",
            "solutions": [
                "清理不需要的文件释放空间",
                "在设置中清理旧图片缓存",
                "减小图片最大缓存空间设置",
                "更换存储路径到更大的磁盘"
            ],
            "docs_link": None
        },
        
        # KOOK相关错误
        "kook_scraper_failed": {
            "category": ErrorCategory.KOOK,
            "user_message": "KOOK消息抓取失败",
            "detail": "无法获取KOOK消息",
            "solutions": [
                "检查KOOK账号是否在线",
                "确认Cookie是否有效",
                "检查网络连接",
                "查看是否需要更新选择器配置"
            ],
            "docs_link": None
        },
        "kook_selector_failed": {
            "category": ErrorCategory.KOOK,
            "user_message": "页面元素查找失败",
            "detail": "无法找到{element}",
            "solutions": [
                "KOOK页面可能已更新，需要更新选择器配置",
                "前往「设置 → 高级 → 选择器配置」检查",
                "联系开发者获取最新选择器配置",
                "查看GitHub Issues了解是否有类似问题"
            ],
            "docs_link": "docs/开发指南.md#选择器配置"
        },
        
        # 平台API错误
        "platform_webhook_invalid": {
            "category": ErrorCategory.PLATFORM_API,
            "user_message": "Webhook无效",
            "detail": "{platform} Webhook验证失败",
            "solutions": [
                "检查Webhook URL是否正确",
                "确认Webhook未被删除",
                "尝试重新创建Webhook",
                "使用「测试连接」功能验证"
            ],
            "docs_link": "docs/{platform}配置教程.md"
        },
        "platform_api_error": {
            "category": ErrorCategory.PLATFORM_API,
            "user_message": "平台API错误",
            "detail": "{platform} API返回错误: {error_code}",
            "solutions": [
                "检查Bot配置是否正确",
                "确认Bot有足够权限",
                "查看{platform}官方文档了解错误码含义",
                "尝试重新配置Bot"
            ],
            "docs_link": None
        }
    }
    
    @classmethod
    def get_friendly_error(cls, error_key: str, **kwargs) -> Dict[str, Any]:
        """
        获取友好的错误信息
        
        Args:
            error_key: 错误键
            **kwargs: 格式化参数
            
        Returns:
            错误信息字典
        """
        template = cls.ERROR_TEMPLATES.get(error_key)
        
        if not template:
            # 未知错误，返回通用提示
            return {
                "category": ErrorCategory.UNKNOWN.value,
                "user_message": "发生未知错误",
                "detail": kwargs.get("detail", "请查看日志了解详情"),
                "solutions": [
                    "查看详细日志定位问题",
                    "尝试重启服务",
                    "检查系统资源是否充足",
                    "联系技术支持"
                ],
                "docs_link": None,
                "technical_error": kwargs.get("technical_error", ""),
                "timestamp": None
            }
        
        # 格式化消息
        detail = template["detail"].format(**kwargs)
        solutions = [s.format(**kwargs) for s in template["solutions"]]
        docs_link = template.get("docs_link")
        if docs_link:
            docs_link = docs_link.format(**kwargs)
        
        return {
            "category": template["category"].value,
            "user_message": template["user_message"],
            "detail": detail,
            "solutions": solutions,
            "docs_link": docs_link,
            "technical_error": kwargs.get("technical_error", ""),
        }
    
    @classmethod
    def format_exception(cls, exception: Exception, context: Optional[str] = None) -> Dict[str, Any]:
        """
        格式化异常为友好的错误信息
        
        Args:
            exception: 异常对象
            context: 上下文信息
            
        Returns:
            错误信息字典
        """
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # 根据异常类型匹配错误键
        error_key = None
        kwargs = {
            "technical_error": f"{error_type}: {error_message}"
        }
        
        # 网络相关异常
        if "timeout" in error_message.lower() or error_type in ["TimeoutError", "asyncio.TimeoutError"]:
            error_key = "network_timeout"
            kwargs["target"] = context or "目标服务"
        
        elif "connection refused" in error_message.lower():
            error_key = "network_connection_refused"
            kwargs["target"] = context or "目标服务"
        
        # Cookie相关
        elif "cookie" in error_message.lower() and "invalid" in error_message.lower():
            error_key = "auth_invalid_cookie"
        
        # 磁盘空间
        elif "disk" in error_message.lower() or "space" in error_message.lower():
            error_key = "storage_disk_full"
            kwargs["usage_percent"] = kwargs.get("usage_percent", "未知")
        
        # 获取友好错误信息
        error_info = cls.get_friendly_error(error_key or "unknown", **kwargs)
        
        # 添加上下文
        if context:
            error_info["context"] = context
        
        # 记录到日志
        logger.error(f"❌ {error_info['user_message']}: {error_info['detail']}")
        logger.debug(f"技术详情: {error_info['technical_error']}")
        
        return error_info


def handle_error(error_key: str, **kwargs) -> Tuple[int, Dict[str, Any]]:
    """
    处理错误并返回API响应格式
    
    Args:
        error_key: 错误键
        **kwargs: 格式化参数
        
    Returns:
        (HTTP状态码, 响应字典)
    """
    error_info = ErrorSolution.get_friendly_error(error_key, **kwargs)
    
    # 根据错误类别确定HTTP状态码
    status_code = 500
    if error_info["category"] == ErrorCategory.AUTHENTICATION.value:
        status_code = 401
    elif error_info["category"] == ErrorCategory.PERMISSION.value:
        status_code = 403
    elif error_info["category"] == ErrorCategory.CONFIGURATION.value:
        status_code = 400
    elif error_info["category"] == ErrorCategory.API_LIMIT.value:
        status_code = 429
    
    response = {
        "success": False,
        "error": error_info
    }
    
    return status_code, response


def format_success_message(action: str, detail: Optional[str] = None) -> Dict[str, Any]:
    """
    格式化成功消息
    
    Args:
        action: 操作描述
        detail: 详细信息
        
    Returns:
        消息字典
    """
    message = {
        "success": True,
        "message": f"✅ {action}成功"
    }
    
    if detail:
        message["detail"] = detail
    
    return message
