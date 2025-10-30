"""
友好错误提示系统
将技术错误转换为用户可理解的提示，并附带解决方案
"""
from typing import Dict, Tuple


# 错误码映射表（技术错误 → 友好提示 + 解决方案）
ERROR_MESSAGES = {
    # KOOK相关错误
    "KOOK_LOGIN_FAILED": {
        "message": "KOOK登录失败",
        "detail": "无法登录到KOOK账号，可能是Cookie已过期或账号密码错误",
        "solutions": [
            "重新导出Cookie并导入",
            "使用账号密码重新登录",
            "检查账号是否被封禁",
            "确认网络连接正常"
        ],
        "severity": "error"
    },
    
    "KOOK_COOKIE_EXPIRED": {
        "message": "Cookie已过期",
        "detail": "KOOK的Cookie已失效，需要重新登录",
        "solutions": [
            "点击账号管理中的\"重新登录\"按钮",
            "使用Chrome扩展重新导出Cookie",
            "如果频繁过期，建议使用账号密码登录"
        ],
        "severity": "warning"
    },
    
    "KOOK_NETWORK_ERROR": {
        "message": "网络连接失败",
        "detail": "无法连接到KOOK服务器",
        "solutions": [
            "检查网络连接",
            "检查防火墙设置",
            "尝试使用VPN",
            "稍后重试"
        ],
        "severity": "warning"
    },
    
    "KOOK_RATE_LIMITED": {
        "message": "请求过于频繁",
        "detail": "KOOK服务器限制了您的请求频率",
        "solutions": [
            "请等待几分钟后重试",
            "减少监听的频道数量",
            "降低消息转发频率"
        ],
        "severity": "warning"
    },
    
    # Discord相关错误
    "DISCORD_WEBHOOK_INVALID": {
        "message": "Discord Webhook无效",
        "detail": "提供的Webhook URL不正确或已被删除",
        "solutions": [
            "在Discord中重新创建Webhook",
            "复制完整的Webhook URL",
            "确认Webhook所在频道仍然存在",
            "检查Bot是否有权限"
        ],
        "severity": "error"
    },
    
    "DISCORD_RATE_LIMIT": {
        "message": "Discord限流",
        "detail": "消息发送过快，触发Discord速率限制",
        "solutions": [
            "系统将自动排队发送，请耐心等待",
            "考虑减少监听的KOOK频道",
            "使用多个Webhook分担负载"
        ],
        "severity": "info"
    },
    
    "DISCORD_MESSAGE_TOO_LONG": {
        "message": "消息过长",
        "detail": "消息超过Discord的2000字符限制",
        "solutions": [
            "系统会自动分段发送",
            "如果仍然失败，请检查消息格式"
        ],
        "severity": "info"
    },
    
    # Telegram相关错误
    "TELEGRAM_BOT_TOKEN_INVALID": {
        "message": "Telegram Bot Token无效",
        "detail": "提供的Bot Token不正确",
        "solutions": [
            "与 @BotFather 对话重新获取Token",
            "确认Token完整复制（包括冒号和所有字符）",
            "检查Token是否被撤销"
        ],
        "severity": "error"
    },
    
    "TELEGRAM_CHAT_NOT_FOUND": {
        "message": "Telegram群组未找到",
        "detail": "无法找到指定的Chat ID对应的群组",
        "solutions": [
            "确认Bot已被添加到目标群组",
            "使用软件内置工具重新获取Chat ID",
            "检查Chat ID是否正确（负数需要包含减号）"
        ],
        "severity": "error"
    },
    
    "TELEGRAM_NO_PERMISSION": {
        "message": "Telegram Bot权限不足",
        "detail": "Bot没有发送消息的权限",
        "solutions": [
            "在群组中将Bot设置为管理员",
            "或确保群组允许成员发送消息",
            "检查Bot是否被禁言"
        ],
        "severity": "error"
    },
    
    # 飞书相关错误
    "FEISHU_APP_ID_INVALID": {
        "message": "飞书App ID无效",
        "detail": "提供的App ID或App Secret不正确",
        "solutions": [
            "在飞书开放平台重新确认App ID",
            "确认App Secret完整且未过期",
            "检查应用是否被停用"
        ],
        "severity": "error"
    },
    
    # 图片相关错误
    "IMAGE_DOWNLOAD_FAILED": {
        "message": "图片下载失败",
        "detail": "无法下载图片文件",
        "solutions": [
            "检查网络连接",
            "图片可能已被删除或移动",
            "KOOK图片可能有防盗链，系统会自动重试",
            "如果持续失败，可以跳过图片消息"
        ],
        "severity": "warning"
    },
    
    "IMAGE_UPLOAD_FAILED": {
        "message": "图片上传失败",
        "detail": "无法将图片上传到目标平台",
        "solutions": [
            "系统将自动使用图床模式",
            "检查目标平台的文件大小限制",
            "图片可能格式不支持，系统会尝试转换"
        ],
        "severity": "warning"
    },
    
    "IMAGE_TOO_LARGE": {
        "message": "图片文件过大",
        "detail": "图片超过目标平台的大小限制",
        "solutions": [
            "系统会自动压缩图片",
            "如果压缩后仍超限，将使用图床链接",
            "建议在设置中调整图片压缩质量"
        ],
        "severity": "info"
    },
    
    # 系统相关错误
    "REDIS_CONNECTION_FAILED": {
        "message": "Redis连接失败",
        "detail": "无法连接到消息队列服务",
        "solutions": [
            "系统将尝试自动启动Redis",
            "如果持续失败，请检查端口6379是否被占用",
            "可以在设置中更改Redis端口",
            "重启应用"
        ],
        "severity": "error"
    },
    
    "DATABASE_ERROR": {
        "message": "数据库错误",
        "detail": "无法访问本地数据库",
        "solutions": [
            "检查磁盘空间是否充足",
            "确认数据库文件未被其他程序占用",
            "尝试重启应用",
            "如果问题持续，可能需要重置数据库"
        ],
        "severity": "error"
    },
    
    "CHROMIUM_NOT_FOUND": {
        "message": "Chromium浏览器未安装",
        "detail": "系统需要Chromium浏览器来抓取KOOK消息",
        "solutions": [
            "点击\"环境检测\"中的\"自动修复\"",
            "系统会自动下载Chromium（约200MB）",
            "确保网络连接正常",
            "如果下载失败，可以手动安装Playwright"
        ],
        "severity": "warning"
    },
    
    "PORT_ALREADY_IN_USE": {
        "message": "端口被占用",
        "detail": "所需的网络端口已被其他程序使用",
        "solutions": [
            "关闭占用端口的程序",
            "在设置中更改端口号",
            "系统会自动尝试备用端口",
            "重启计算机"
        ],
        "severity": "warning"
    },
    
    # 配置相关错误
    "MAPPING_NOT_FOUND": {
        "message": "未配置频道映射",
        "detail": "该KOOK频道没有配置转发目标",
        "solutions": [
            "在\"频道映射\"页面添加映射",
            "使用\"智能映射\"功能自动配置",
            "确认已配置至少一个Bot"
        ],
        "severity": "info"
    },
    
    "NO_BOT_CONFIGURED": {
        "message": "未配置转发Bot",
        "detail": "没有配置任何Discord/Telegram/飞书Bot",
        "solutions": [
            "在\"Bot配置\"页面添加Bot",
            "参考帮助文档创建Bot",
            "运行配置向导完成设置"
        ],
        "severity": "warning"
    },
}


def get_friendly_error(error_code: str, 
                       context: Dict = None) -> Tuple[str, str, list]:
    """
    获取友好的错误提示
    
    Args:
        error_code: 错误代码
        context: 额外上下文信息（可用于错误消息插值）
        
    Returns:
        (message, detail, solutions)
    """
    error_info = ERROR_MESSAGES.get(error_code)
    
    if not error_info:
        # 未知错误，返回通用提示
        return (
            "发生未知错误",
            f"错误代码: {error_code}",
            ["请查看日志获取详细信息", "如果问题持续，请联系技术支持"]
        )
    
    message = error_info["message"]
    detail = error_info["detail"]
    solutions = error_info["solutions"]
    
    # 如果有上下文，可以进行字符串插值（未来扩展）
    if context:
        # 例如: detail = detail.format(**context)
        pass
    
    return message, detail, solutions


def format_error_for_ui(error_code: str, context: Dict = None) -> Dict:
    """
    格式化错误信息为UI显示格式
    
    Returns:
        {
            "code": "KOOK_LOGIN_FAILED",
            "message": "KOOK登录失败",
            "detail": "...",
            "solutions": [...],
            "severity": "error",  # error/warning/info
            "timestamp": "2025-10-27 12:00:00"
        }
    """
    message, detail, solutions = get_friendly_error(error_code, context)
    
    error_info = ERROR_MESSAGES.get(error_code, {})
    severity = error_info.get("severity", "error")
    
    return {
        "code": error_code,
        "message": message,
        "detail": detail,
        "solutions": solutions,
        "severity": severity,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# 常用错误快捷函数
def kook_login_failed(detail: str = None) -> Dict:
    """KOOK登录失败"""
    return format_error_for_ui("KOOK_LOGIN_FAILED", {"detail": detail} if detail else None)


def discord_webhook_invalid() -> Dict:
    """Discord Webhook无效"""
    return format_error_for_ui("DISCORD_WEBHOOK_INVALID")


def telegram_bot_token_invalid() -> Dict:
    """Telegram Bot Token无效"""
    return format_error_for_ui("TELEGRAM_BOT_TOKEN_INVALID")


def image_download_failed(url: str = None) -> Dict:
    """图片下载失败"""
    return format_error_for_ui("IMAGE_DOWNLOAD_FAILED", {"url": url} if url else None)


def redis_connection_failed() -> Dict:
    """Redis连接失败"""
    return format_error_for_ui("REDIS_CONNECTION_FAILED")
