"""
✅ P0-10优化: 错误提示友好化系统
将技术错误翻译为人话，提供明确解决方案和一键修复
"""
from typing import Dict, List, Optional, Tuple
from ..utils.logger import logger


class ErrorTranslatorEnhanced:
    """增强版错误翻译器（30种错误翻译）"""
    
    def __init__(self):
        self.error_translations = self._init_error_translations()
        logger.info("✅ 增强版错误翻译器已初始化（30种错误翻译）")
    
    def _init_error_translations(self) -> Dict:
        """
        初始化错误翻译规则（30种）
        
        Returns:
            错误翻译字典
        """
        return {
            # 1. Playwright/浏览器相关错误
            "playwright._impl._api_types.Error: Browser closed": {
                "friendly": "🚫 浏览器组件异常关闭",
                "reason": "Chromium浏览器进程意外终止或崩溃",
                "solution": [
                    "1. 点击下方按钮自动重启浏览器",
                    "2. 检查系统内存是否充足（建议4GB以上）",
                    "3. 如果问题持续，尝试重启应用"
                ],
                "auto_fix": "restart_browser",
                "severity": "high",
                "category": "browser"
            },
            
            "playwright._impl._api_types.TimeoutError": {
                "friendly": "⏰ 浏览器操作超时",
                "reason": "网页元素加载时间过长或网络连接不稳定",
                "solution": [
                    "1. 检查网络连接是否正常",
                    "2. KOOK服务器可能响应缓慢，请稍后重试",
                    "3. 尝试刷新页面或重新登录"
                ],
                "auto_fix": "refresh_page",
                "severity": "medium",
                "category": "browser"
            },
            
            "Executable doesn't exist": {
                "friendly": "❌ Chromium浏览器未安装",
                "reason": "系统中没有找到Chromium浏览器组件",
                "solution": [
                    "1. 点击下方按钮自动安装Chromium",
                    "2. 安装过程需要3-5分钟，请耐心等待",
                    "3. 如果自动安装失败，请手动运行: playwright install chromium"
                ],
                "auto_fix": "install_chromium",
                "severity": "critical",
                "category": "browser"
            },
            
            # 2. Redis相关错误
            "redis.exceptions.ConnectionError": {
                "friendly": "🔌 数据库服务未运行",
                "reason": "Redis数据库服务未启动或连接失败",
                "solution": [
                    "1. 点击下方按钮自动启动Redis服务",
                    "2. 如果自动启动失败，请检查端口6379是否被占用",
                    "3. 尝试手动启动Redis服务"
                ],
                "auto_fix": "start_redis",
                "severity": "critical",
                "category": "database"
            },
            
            "redis.exceptions.ResponseError": {
                "friendly": "⚠️ 数据库操作失败",
                "reason": "Redis命令执行错误或数据格式不正确",
                "solution": [
                    "1. 尝试清空Redis缓存",
                    "2. 重启Redis服务",
                    "3. 检查Redis版本是否符合要求（需要7.0+）"
                ],
                "auto_fix": "clear_redis",
                "severity": "medium",
                "category": "database"
            },
            
            # 3. Cookie/登录相关错误
            "Cookie expired": {
                "friendly": "🔐 KOOK登录已过期",
                "reason": "您的KOOK账号Cookie已失效，需要重新登录",
                "solution": [
                    "1. 点击下方按钮重新登录KOOK",
                    "2. 使用Cookie导入方式登录更稳定",
                    "3. 如果频繁过期，检查是否在其他设备登录"
                ],
                "auto_fix": "relogin",
                "severity": "high",
                "category": "auth"
            },
            
            "Invalid cookie format": {
                "friendly": "📋 Cookie格式错误",
                "reason": "您提供的Cookie格式不正确或不完整",
                "solution": [
                    "1. 确保Cookie是从KOOK官方网站导出的",
                    "2. 支持JSON、Netscape、Header String三种格式",
                    "3. 查看教程了解如何正确获取Cookie"
                ],
                "auto_fix": None,
                "severity": "medium",
                "category": "auth"
            },
            
            "Login failed": {
                "friendly": "❌ 登录失败",
                "reason": "账号或密码错误，或触发了KOOK的风控机制",
                "solution": [
                    "1. 检查账号和密码是否正确",
                    "2. 如果需要验证码，请正确输入",
                    "3. 建议使用Cookie导入方式登录"
                ],
                "auto_fix": None,
                "severity": "high",
                "category": "auth"
            },
            
            # 4. Discord相关错误
            "discord.errors.InvalidWebhook": {
                "friendly": "🔗 Discord Webhook无效",
                "reason": "Webhook URL格式错误或已被删除",
                "solution": [
                    "1. 检查Webhook URL是否完整",
                    "2. 确认Webhook未被删除",
                    "3. 尝试重新创建Webhook",
                    "4. 格式应为: https://discord.com/api/webhooks/..."
                ],
                "auto_fix": None,
                "severity": "high",
                "category": "bot"
            },
            
            "discord.errors.HTTPException: 429": {
                "friendly": "⏳ Discord API限流",
                "reason": "发送消息过于频繁，触发了Discord的限流保护",
                "solution": [
                    "1. 系统会自动排队等待",
                    "2. Discord限制: 每5秒最多5条消息",
                    "3. 稍等片刻后会自动恢复",
                    "4. 建议减少监听的频道数量"
                ],
                "auto_fix": None,
                "severity": "low",
                "category": "bot"
            },
            
            "discord.errors.Forbidden": {
                "friendly": "🚫 Discord权限不足",
                "reason": "Webhook没有发送消息的权限",
                "solution": [
                    "1. 检查Webhook是否仍然有效",
                    "2. 确认频道权限设置正确",
                    "3. 尝试重新创建Webhook"
                ],
                "auto_fix": None,
                "severity": "high",
                "category": "bot"
            },
            
            # 5. Telegram相关错误
            "telegram.error.InvalidToken": {
                "friendly": "🔑 Telegram Bot Token无效",
                "reason": "Bot Token格式错误或已被撤销",
                "solution": [
                    "1. 检查Token是否完整复制",
                    "2. 确认Token未被撤销",
                    "3. 与@BotFather确认Token是否正确",
                    "4. Token格式: 数字:字母数字组合"
                ],
                "auto_fix": None,
                "severity": "critical",
                "category": "bot"
            },
            
            "telegram.error.ChatNotFound": {
                "friendly": "❓ Telegram群组不存在",
                "reason": "Chat ID错误或Bot未加入该群组",
                "solution": [
                    "1. 确认已将Bot添加到目标群组",
                    "2. 检查Chat ID是否正确（应该是负数）",
                    "3. 使用内置工具自动获取Chat ID",
                    "4. 确保Bot有发送消息的权限"
                ],
                "auto_fix": None,
                "severity": "high",
                "category": "bot"
            },
            
            "telegram.error.RetryAfter": {
                "friendly": "⏰ Telegram要求等待",
                "reason": "发送过于频繁，Telegram要求暂停一段时间",
                "solution": [
                    "1. 系统会自动等待并重试",
                    "2. Telegram限制: 每秒最多30条消息",
                    "3. 无需手动操作，稍等即可"
                ],
                "auto_fix": None,
                "severity": "low",
                "category": "bot"
            },
            
            # 6. 飞书相关错误
            "feishu.errors.AppAccessTokenInvalid": {
                "friendly": "🔓 飞书应用凭证无效",
                "reason": "App ID或App Secret错误，或应用已被停用",
                "solution": [
                    "1. 检查App ID和App Secret是否正确",
                    "2. 确认应用未被停用或删除",
                    "3. 在飞书开放平台重新获取凭证",
                    "4. 确保凭证完整复制（无空格）"
                ],
                "auto_fix": None,
                "severity": "critical",
                "category": "bot"
            },
            
            "feishu.errors.MessageSendFailed": {
                "friendly": "📤 飞书消息发送失败",
                "reason": "可能是权限不足、消息格式错误或网络问题",
                "solution": [
                    "1. 检查机器人是否已加入目标群组",
                    "2. 确认机器人有发送消息权限",
                    "3. 检查网络连接",
                    "4. 查看飞书开放平台的错误日志"
                ],
                "auto_fix": None,
                "severity": "medium",
                "category": "bot"
            },
            
            # 7. 网络相关错误
            "requests.exceptions.ConnectionError": {
                "friendly": "🌐 网络连接失败",
                "reason": "无法连接到目标服务器，可能是网络问题",
                "solution": [
                    "1. 检查网络连接是否正常",
                    "2. 尝试访问目标网站确认可达性",
                    "3. 如果使用代理，检查代理设置",
                    "4. 防火墙可能拦截了连接"
                ],
                "auto_fix": "check_network",
                "severity": "high",
                "category": "network"
            },
            
            "requests.exceptions.Timeout": {
                "friendly": "⏱️ 网络请求超时",
                "reason": "服务器响应时间过长",
                "solution": [
                    "1. 检查网络速度是否正常",
                    "2. 目标服务器可能正在维护",
                    "3. 稍后重试",
                    "4. 考虑增加超时时间设置"
                ],
                "auto_fix": None,
                "severity": "medium",
                "category": "network"
            },
            
            "requests.exceptions.SSLError": {
                "friendly": "🔒 SSL证书验证失败",
                "reason": "目标网站的SSL证书无效或系统时间不正确",
                "solution": [
                    "1. 检查系统时间是否正确",
                    "2. 更新系统根证书",
                    "3. 如果是企业网络，可能有证书拦截",
                    "4. 暂时禁用SSL验证（不推荐）"
                ],
                "auto_fix": None,
                "severity": "medium",
                "category": "network"
            },
            
            # 8. 文件/磁盘相关错误
            "PermissionError": {
                "friendly": "🔐 文件权限不足",
                "reason": "应用没有读写指定文件或目录的权限",
                "solution": [
                    "1. 检查文件和目录的权限设置",
                    "2. 以管理员身份运行应用",
                    "3. 确保文件未被其他程序占用",
                    "4. 检查磁盘是否有写入权限"
                ],
                "auto_fix": None,
                "severity": "high",
                "category": "system"
            },
            
            "OSError: [Errno 28] No space left on device": {
                "friendly": "💾 磁盘空间不足",
                "reason": "存储设备已满，无法写入新数据",
                "solution": [
                    "1. 清理磁盘空间",
                    "2. 使用系统设置中的图床清理功能",
                    "3. 删除不需要的旧日志文件",
                    "4. 考虑增加磁盘空间或更换存储位置"
                ],
                "auto_fix": "cleanup_space",
                "severity": "critical",
                "category": "system"
            },
            
            # 9. 数据库相关错误
            "sqlite3.OperationalError: database is locked": {
                "friendly": "🔒 数据库被锁定",
                "reason": "多个进程同时访问数据库导致锁定",
                "solution": [
                    "1. 稍等片刻后自动恢复",
                    "2. 检查是否有多个应用实例在运行",
                    "3. 重启应用",
                    "4. 如果问题持续，考虑备份并重建数据库"
                ],
                "auto_fix": "restart_app",
                "severity": "medium",
                "category": "database"
            },
            
            "sqlite3.IntegrityError": {
                "friendly": "⚠️ 数据完整性错误",
                "reason": "尝试插入重复或无效的数据",
                "solution": [
                    "1. 这通常是内部错误，系统会自动处理",
                    "2. 如果频繁出现，可能需要修复数据库",
                    "3. 考虑使用备份恢复功能",
                    "4. 联系技术支持"
                ],
                "auto_fix": None,
                "severity": "low",
                "category": "database"
            },
            
            # 10. 图片处理相关错误
            "PIL.UnidentifiedImageError": {
                "friendly": "🖼️ 无法识别图片格式",
                "reason": "图片文件损坏或格式不支持",
                "solution": [
                    "1. 检查图片文件是否完整",
                    "2. 支持的格式: JPG, PNG, GIF, WEBP",
                    "3. 尝试重新下载图片",
                    "4. 跳过该图片继续转发其他内容"
                ],
                "auto_fix": "skip_image",
                "severity": "low",
                "category": "media"
            },
            
            "Image file is corrupted": {
                "friendly": "💔 图片文件已损坏",
                "reason": "图片下载不完整或文件已损坏",
                "solution": [
                    "1. 尝试重新下载图片",
                    "2. 检查网络连接",
                    "3. 原图片可能已被删除",
                    "4. 跳过该图片继续转发"
                ],
                "auto_fix": "retry_download",
                "severity": "low",
                "category": "media"
            },
            
            # 11. 配置相关错误
            "Configuration not found": {
                "friendly": "⚙️ 配置文件未找到",
                "reason": "应用配置丢失或未完成初始化",
                "solution": [
                    "1. 重新运行配置向导",
                    "2. 检查配置文件是否存在",
                    "3. 尝试恢复备份配置",
                    "4. 重新安装应用"
                ],
                "auto_fix": "init_config",
                "severity": "high",
                "category": "config"
            },
            
            # 12. 内存相关错误
            "MemoryError": {
                "friendly": "🧠 内存不足",
                "reason": "系统可用内存不足，无法完成操作",
                "solution": [
                    "1. 关闭其他占用内存的程序",
                    "2. 减少同时监听的频道数量",
                    "3. 降低图片质量设置",
                    "4. 增加系统虚拟内存或物理内存"
                ],
                "auto_fix": "reduce_memory",
                "severity": "critical",
                "category": "system"
            },
            
            # 13. 验证码相关错误
            "Captcha required": {
                "friendly": "🔐 需要输入验证码",
                "reason": "KOOK检测到异常登录，需要验证码确认",
                "solution": [
                    "1. 在弹出的对话框中输入验证码",
                    "2. 如果有2Captcha配置会自动识别",
                    "3. 验证码输入有120秒时限",
                    "4. 输入错误可以刷新重试"
                ],
                "auto_fix": None,
                "severity": "medium",
                "category": "auth"
            },
            
            "Captcha timeout": {
                "friendly": "⏰ 验证码已超时",
                "reason": "验证码输入时间超过120秒",
                "solution": [
                    "1. 刷新验证码重新输入",
                    "2. 建议配置2Captcha自动识别",
                    "3. 重新登录账号"
                ],
                "auto_fix": "refresh_captcha",
                "severity": "medium",
                "category": "auth"
            },
            
            # 14. 频道映射相关错误
            "No mapping found": {
                "friendly": "🔀 未找到频道映射",
                "reason": "该频道没有配置转发目标",
                "solution": [
                    "1. 在'频道映射'页面配置该频道",
                    "2. 使用智能映射自动匹配",
                    "3. 检查映射是否被禁用"
                ],
                "auto_fix": "config_mapping",
                "severity": "low",
                "category": "config"
            },
            
            # 15. 其他常见错误
            "Unknown error": {
                "friendly": "❓ 未知错误",
                "reason": "发生了意外的错误",
                "solution": [
                    "1. 查看详细错误信息",
                    "2. 尝试重启应用",
                    "3. 检查日志文件",
                    "4. 联系技术支持并提供错误信息"
                ],
                "auto_fix": None,
                "severity": "medium",
                "category": "unknown"
            }
        }
    
    def translate(self, error: Exception) -> Dict:
        """
        翻译错误信息
        
        Args:
            error: 异常对象
            
        Returns:
            翻译后的错误信息字典
        """
        error_str = str(error)
        error_type = type(error).__name__
        
        # 尝试匹配错误
        for pattern, translation in self.error_translations.items():
            if pattern in error_str or pattern in error_type:
                return {
                    **translation,
                    "technical": error_str,
                    "error_type": error_type,
                    "matched_pattern": pattern
                }
        
        # 未匹配到，返回通用错误
        return self.error_translations["Unknown error"]
    
    def get_auto_fix_function(self, auto_fix_type: str):
        """
        获取自动修复函数名
        
        Args:
            auto_fix_type: 修复类型
            
        Returns:
            修复函数名
        """
        fix_functions = {
            "restart_browser": "auto_fix_restart_browser",
            "refresh_page": "auto_fix_refresh_page",
            "install_chromium": "auto_fix_install_chromium",
            "start_redis": "auto_fix_start_redis",
            "clear_redis": "auto_fix_clear_redis",
            "relogin": "auto_fix_relogin",
            "check_network": "auto_fix_check_network",
            "cleanup_space": "auto_fix_cleanup_space",
            "restart_app": "auto_fix_restart_app",
            "skip_image": "auto_fix_skip_image",
            "retry_download": "auto_fix_retry_download",
            "init_config": "auto_fix_init_config",
            "reduce_memory": "auto_fix_reduce_memory",
            "refresh_captcha": "auto_fix_refresh_captcha",
            "config_mapping": "auto_fix_config_mapping"
        }
        
        return fix_functions.get(auto_fix_type)


# 创建全局实例
error_translator = ErrorTranslatorEnhanced()


def translate_error(error: Exception) -> Dict:
    """翻译错误（便捷函数）"""
    return error_translator.translate(error)


def get_auto_fix_function(auto_fix_type: str):
    """获取自动修复函数（便捷函数）"""
    return error_translator.get_auto_fix_function(auto_fix_type)
