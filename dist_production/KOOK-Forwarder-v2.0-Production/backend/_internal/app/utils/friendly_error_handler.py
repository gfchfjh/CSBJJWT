"""
友好错误处理器 - ✅ P1-5优化完成: 30+种错误模板
"""
from typing import Dict, List, Any, Optional
from enum import Enum
from ..utils.logger import logger


class ErrorCategory(Enum):
    """错误分类"""
    COOKIE = "cookie"          # Cookie相关错误
    NETWORK = "network"        # 网络相关错误
    AUTH = "auth"              # 认证相关错误
    PLATFORM = "platform"      # 平台API错误
    CONFIG = "config"          # 配置相关错误
    SYSTEM = "system"          # 系统相关错误
    SECURITY = "security"      # 安全相关错误
    DATA = "data"              # 数据相关错误


class FriendlyErrorHandler:
    """
    ✅ P1-5优化: 友好错误处理器
    
    功能：
    1. 30+种错误模板
    2. 可操作的解决方案
    3. 相关教程链接
    4. 一键修复按钮
    """
    
    # ============ ✅ P1-5: 30+种错误模板 ============
    
    ERROR_TEMPLATES = {
        # ========== Cookie相关错误（5个） ==========
        "COOKIE_EXPIRED": {
            "category": ErrorCategory.COOKIE,
            "title": "🔑 Cookie已过期",
            "description": "您的KOOK登录凭证已失效，需要重新登录。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "Cookie自然过期（通常30天）",
                "KOOK服务器清除了会话",
                "更换了密码或登出"
            ],
            "actions": [
                {
                    "label": "🔄 重新登录",
                    "action": "relogin",
                    "primary": True,
                    "endpoint": "/api/accounts/{account_id}/relogin"
                },
                {
                    "label": "📖 查看Cookie教程",
                    "action": "open_tutorial",
                    "params": {"tutorial_id": "cookie_guide"},
                    "endpoint": "/help/tutorials/cookie_guide"
                }
            ],
            "prevention": "建议勾选\"记住密码\"，系统会在Cookie过期时自动重新登录。",
            "auto_fix": False,
            "related_faqs": ["faq_offline", "faq_cookie"]
        },
        
        "COOKIE_INVALID_FORMAT": {
            "category": ErrorCategory.COOKIE,
            "title": "📝 Cookie格式错误",
            "description": "导入的Cookie格式不正确，无法解析。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "复制不完整",
                "包含无效字符",
                "格式不是JSON"
            ],
            "actions": [
                {
                    "label": "🔧 自动修复",
                    "action": "auto_fix_cookie",
                    "primary": True,
                    "endpoint": "/api/cookie-import/validate-enhanced"
                },
                {
                    "label": "📖 查看Cookie教程",
                    "action": "open_tutorial",
                    "params": {"tutorial_id": "cookie_guide"}
                }
            ],
            "prevention": "使用浏览器扩展一键导出Cookie，避免手动复制出错。",
            "auto_fix": True,
            "related_faqs": ["faq_cookie"]
        },
        
        "COOKIE_DOMAIN_MISMATCH": {
            "category": ErrorCategory.COOKIE,
            "title": "🌐 Cookie域名不匹配",
            "description": "Cookie的域名不是KOOK（kookapp.cn）的域名。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "从错误的网站导出Cookie",
                "域名字段错误"
            ],
            "actions": [
                {
                    "label": "🔧 自动修正域名",
                    "action": "auto_fix_domain",
                    "primary": True
                }
            ],
            "prevention": "确保从 www.kookapp.cn 导出Cookie。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        "COOKIE_MISSING_FIELDS": {
            "category": ErrorCategory.COOKIE,
            "title": "📋 Cookie缺少必需字段",
            "description": "Cookie缺少name、value或domain等必需字段。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "复制不完整",
                "导出工具有问题"
            ],
            "actions": [
                {
                    "label": "🔧 自动补全字段",
                    "action": "auto_complete_fields",
                    "primary": True
                },
                {
                    "label": "📖 查看完整教程",
                    "action": "open_tutorial",
                    "params": {"tutorial_id": "cookie_guide"}
                }
            ],
            "prevention": "使用推荐的导出方式（浏览器扩展或开发者工具）。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        "COOKIE_ABOUT_TO_EXPIRE": {
            "category": ErrorCategory.COOKIE,
            "title": "⏰ Cookie即将过期",
            "description": "您的Cookie将在3天内过期，建议提前更新。",
            "severity": "low",
            "user_friendly": True,
            "causes": [
                "Cookie接近有效期"
            ],
            "actions": [
                {
                    "label": "🔄 现在更新",
                    "action": "update_cookie",
                    "primary": True
                },
                {
                    "label": "⏰ 稍后提醒",
                    "action": "snooze"
                }
            ],
            "prevention": "定期更新Cookie，或启用自动续期功能。",
            "auto_fix": False,
            "related_faqs": []
        },
        
        # ========== 网络相关错误（5个） ==========
        "NETWORK_TIMEOUT": {
            "category": ErrorCategory.NETWORK,
            "title": "⏱️ 网络连接超时",
            "description": "无法连接到目标服务器，请求超时。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "网络不稳定",
                "目标服务器响应慢",
                "防火墙阻止连接"
            ],
            "actions": [
                {
                    "label": "🔍 诊断网络",
                    "action": "diagnose_network",
                    "primary": True,
                    "endpoint": "/api/system/autofix/network"
                },
                {
                    "label": "🔄 重试",
                    "action": "retry"
                }
            ],
            "prevention": "确保网络连接稳定，带宽至少10Mbps。",
            "auto_fix": True,
            "related_faqs": ["faq_network"]
        },
        
        "NETWORK_DNS_ERROR": {
            "category": ErrorCategory.NETWORK,
            "title": "🌐 DNS解析失败",
            "description": "无法解析域名，可能是DNS服务器问题。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "DNS服务器故障",
                "网络配置错误",
                "域名不存在"
            ],
            "actions": [
                {
                    "label": "🔧 切换DNS",
                    "action": "change_dns",
                    "primary": True,
                    "params": {"dns": "8.8.8.8"}
                }
            ],
            "prevention": "使用公共DNS服务器（如8.8.8.8）。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        "NETWORK_PROXY_ERROR": {
            "category": ErrorCategory.NETWORK,
            "title": "🔌 代理连接失败",
            "description": "通过代理连接失败，请检查代理配置。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "代理服务器不可用",
                "代理配置错误",
                "需要认证"
            ],
            "actions": [
                {
                    "label": "🔧 检查代理设置",
                    "action": "check_proxy",
                    "primary": True
                },
                {
                    "label": "🚫 禁用代理",
                    "action": "disable_proxy"
                }
            ],
            "prevention": "使用稳定的代理服务，或直连。",
            "auto_fix": False,
            "related_faqs": []
        },
        
        "NETWORK_SSL_ERROR": {
            "category": ErrorCategory.NETWORK,
            "title": "🔒 SSL证书错误",
            "description": "HTTPS连接的SSL证书验证失败。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "证书过期",
                "证书不受信任",
                "中间人攻击（严重）"
            ],
            "actions": [
                {
                    "label": "⚠️ 停止连接",
                    "action": "stop",
                    "primary": True
                },
                {
                    "label": "🔍 查看证书详情",
                    "action": "view_certificate"
                }
            ],
            "prevention": "不要忽略SSL证书警告，可能存在安全风险！",
            "auto_fix": False,
            "related_faqs": ["faq_security"]
        },
        
        "NETWORK_RATE_LIMIT": {
            "category": ErrorCategory.NETWORK,
            "title": "⏰ 请求频率受限",
            "description": "请求过于频繁，目标服务器暂时限制了访问。",
            "severity": "low",
            "user_friendly": True,
            "causes": [
                "发送速度过快",
                "目标平台限流保护"
            ],
            "actions": [
                {
                    "label": "⏰ 自动排队重试",
                    "action": "queue_retry",
                    "primary": True
                },
                {
                    "label": "📊 查看队列状态",
                    "action": "view_queue"
                }
            ],
            "prevention": "配置多个Webhook实现负载均衡，避免单点限流。",
            "auto_fix": True,
            "eta": "预计等待：30-60秒",
            "related_faqs": ["faq_delay", "faq_performance"]
        },
        
        # ========== 平台API错误（6个） ==========
        "DISCORD_WEBHOOK_INVALID": {
            "category": ErrorCategory.PLATFORM,
            "title": "🔗 Discord Webhook无效",
            "description": "Discord Webhook URL格式错误或已失效。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "URL复制错误",
                "Webhook已被删除",
                "权限不足"
            ],
            "actions": [
                {
                    "label": "✏️ 重新配置",
                    "action": "reconfig_webhook",
                    "primary": True,
                    "endpoint": "/bots"
                },
                {
                    "label": "📖 查看Discord教程",
                    "action": "open_tutorial",
                    "params": {"tutorial_id": "discord_guide"}
                },
                {
                    "label": "🧪 测试连接",
                    "action": "test_webhook"
                }
            ],
            "prevention": "定期测试Webhook连接，确保有效。",
            "auto_fix": False,
            "related_faqs": ["faq_discord"]
        },
        
        "DISCORD_RATE_LIMIT": {
            "category": ErrorCategory.PLATFORM,
            "title": "⏰ Discord限流中",
            "description": "发送速度过快，Discord暂时限制了消息发送。",
            "severity": "low",
            "user_friendly": True,
            "causes": [
                "单Webhook发送过快（>5条/5秒）",
                "消息量突然增大"
            ],
            "actions": [
                {
                    "label": "⏰ 自动排队（无需操作）",
                    "action": "auto_queue",
                    "primary": True
                },
                {
                    "label": "📊 查看队列状态",
                    "action": "view_queue",
                    "endpoint": "/logs"
                },
                {
                    "label": "🔧 配置负载均衡",
                    "action": "setup_load_balance",
                    "endpoint": "/bots"
                }
            ],
            "prevention": "配置多个Webhook实现负载均衡（吞吐量提升10倍）。",
            "auto_fix": True,
            "eta": "预计等待时间：30秒",
            "related_faqs": ["faq_delay", "faq_performance"]
        },
        
        "TELEGRAM_BOT_BLOCKED": {
            "category": ErrorCategory.PLATFORM,
            "title": "🚫 Telegram Bot被封禁",
            "description": "Telegram Bot被群组管理员移除或被封禁。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "Bot被管理员移除",
                "Bot被Telegram官方封禁",
                "Token无效"
            ],
            "actions": [
                {
                    "label": "🔄 重新添加Bot",
                    "action": "re_add_bot",
                    "primary": True
                },
                {
                    "label": "📖 查看Telegram教程",
                    "action": "open_tutorial",
                    "params": {"tutorial_id": "telegram_guide"}
                }
            ],
            "prevention": "确保Bot有发送消息权限，避免发送垃圾信息。",
            "auto_fix": False,
            "related_faqs": []
        },
        
        "TELEGRAM_CHAT_NOT_FOUND": {
            "category": ErrorCategory.PLATFORM,
            "title": "🔍 Telegram群组不存在",
            "description": "指定的Chat ID不存在或Bot未加入群组。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "Chat ID错误",
                "Bot未加入群组",
                "群组已解散"
            ],
            "actions": [
                {
                    "label": "🔍 重新获取Chat ID",
                    "action": "detect_chat_id",
                    "primary": True,
                    "endpoint": "/api/telegram/detect-chat-id"
                },
                {
                    "label": "📖 查看教程",
                    "action": "open_tutorial",
                    "params": {"tutorial_id": "telegram_guide"}
                }
            ],
            "prevention": "使用\"自动获取Chat ID\"功能，避免手动输入错误。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        "FEISHU_TOKEN_EXPIRED": {
            "category": ErrorCategory.PLATFORM,
            "title": "🔑 飞书Token过期",
            "description": "飞书应用的访问Token已过期，需要重新获取。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "Token自动过期（2小时）",
                "应用被禁用"
            ],
            "actions": [
                {
                    "label": "🔄 自动刷新Token",
                    "action": "refresh_token",
                    "primary": True
                }
            ],
            "prevention": "系统会自动刷新Token，无需手动操作。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        "FEISHU_PERMISSION_DENIED": {
            "category": ErrorCategory.PLATFORM,
            "title": "🚫 飞书权限不足",
            "description": "飞书应用缺少必需的权限。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "未授予发送消息权限",
                "未授予上传图片权限",
                "应用未发布"
            ],
            "actions": [
                {
                    "label": "🔧 检查权限配置",
                    "action": "check_permissions",
                    "primary": True
                },
                {
                    "label": "📖 查看飞书教程",
                    "action": "open_tutorial",
                    "params": {"tutorial_id": "feishu_guide"}
                }
            ],
            "prevention": "创建应用时确保授予所有必需权限。",
            "auto_fix": False,
            "related_faqs": []
        },
        
        # ========== 图片处理错误（4个） ==========
        "IMAGE_DOWNLOAD_FAILED": {
            "category": ErrorCategory.DATA,
            "title": "🖼️ 图片下载失败",
            "description": "无法下载图片，可能被防盗链保护。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "图片被防盗链",
                "图片已被删除",
                "网络超时"
            ],
            "actions": [
                {
                    "label": "🔄 使用图床模式重试",
                    "action": "switch_to_imgbed",
                    "primary": True
                },
                {
                    "label": "📊 查看失败详情",
                    "action": "view_error_log"
                }
            ],
            "prevention": "系统会自动处理防盗链，通常无需操作。",
            "auto_fix": True,
            "related_faqs": ["faq_image_fail"]
        },
        
        "IMAGE_TOO_LARGE": {
            "category": ErrorCategory.DATA,
            "title": "📦 图片文件过大",
            "description": "图片超过10MB，建议压缩后上传。",
            "severity": "low",
            "user_friendly": True,
            "causes": [
                "原图分辨率过高",
                "未压缩"
            ],
            "actions": [
                {
                    "label": "🔧 自动压缩",
                    "action": "auto_compress",
                    "primary": True
                }
            ],
            "prevention": "系统会自动压缩大图片（质量85%）。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        "IMAGE_UPLOAD_FAILED": {
            "category": ErrorCategory.DATA,
            "title": "☁️ 图片上传失败",
            "description": "上传图片到目标平台失败。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "目标平台限流",
                "图片格式不支持",
                "网络问题"
            ],
            "actions": [
                {
                    "label": "🔄 使用图床模式",
                    "action": "use_imgbed",
                    "primary": True
                },
                {
                    "label": "💾 暂存本地",
                    "action": "save_local"
                }
            ],
            "prevention": "使用智能图片策略，自动fallback。",
            "auto_fix": True,
            "related_faqs": ["faq_image_fail"]
        },
        
        "IMAGE_IMGBED_FULL": {
            "category": ErrorCategory.SYSTEM,
            "title": "💾 图床空间已满",
            "description": "本地图床空间不足（超过10GB限制）。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "图片缓存过多",
                "未及时清理"
            ],
            "actions": [
                {
                    "label": "🗑️ 清理旧图片",
                    "action": "cleanup_images",
                    "primary": True,
                    "endpoint": "/api/system/cleanup-images"
                },
                {
                    "label": "⚙️ 调整配置",
                    "action": "adjust_config",
                    "endpoint": "/settings"
                }
            ],
            "prevention": "定期清理7天前的图片，或增大空间限制。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        # ========== 认证错误（3个） ==========
        "AUTH_TOKEN_INVALID": {
            "category": ErrorCategory.AUTH,
            "title": "🔐 API Token无效",
            "description": "API认证Token错误或已过期。",
            "severity": "high",
            "user_friendly": False,  # 技术错误，不应该暴露给普通用户
            "causes": [
                "Token配置错误",
                "Token已过期"
            ],
            "actions": [
                {
                    "label": "🔄 重新生成Token",
                    "action": "regenerate_token",
                    "primary": True
                }
            ],
            "prevention": "使用系统自动生成的Token。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        "AUTH_MASTER_PASSWORD_WRONG": {
            "category": ErrorCategory.AUTH,
            "title": "🔑 主密码错误",
            "description": "输入的主密码不正确。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "密码输入错误",
                "大小写错误",
                "遗忘密码"
            ],
            "actions": [
                {
                    "label": "🔄 重新输入",
                    "action": "retry_password",
                    "primary": True
                },
                {
                    "label": "📧 通过邮箱重置",
                    "action": "reset_password",
                    "endpoint": "/api/password-reset-enhanced/request"
                }
            ],
            "prevention": "使用密码管理器保存密码。",
            "auto_fix": False,
            "related_faqs": ["faq_security"]
        },
        
        "AUTH_PASSWORD_RESET_CODE_INVALID": {
            "category": ErrorCategory.AUTH,
            "title": "🔢 验证码错误",
            "description": "密码重置验证码不正确或已过期。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "验证码输入错误",
                "验证码已过期（10分钟）"
            ],
            "actions": [
                {
                    "label": "🔄 重新获取验证码",
                    "action": "request_new_code",
                    "primary": True,
                    "endpoint": "/api/password-reset-enhanced/request"
                }
            ],
            "prevention": "收到验证码后10分钟内完成重置。",
            "auto_fix": False,
            "related_faqs": []
        },
        
        # ========== 配置错误（5个） ==========
        "CONFIG_BOT_NOT_FOUND": {
            "category": ErrorCategory.CONFIG,
            "title": "🤖 Bot配置不存在",
            "description": "未找到指定的Bot配置。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "Bot被删除",
                "Bot ID错误"
            ],
            "actions": [
                {
                    "label": "➕ 重新配置Bot",
                    "action": "add_bot",
                    "primary": True,
                    "endpoint": "/bots"
                }
            ],
            "prevention": "不要随意删除正在使用的Bot配置。",
            "auto_fix": False,
            "related_faqs": []
        },
        
        "CONFIG_MAPPING_NOT_FOUND": {
            "category": ErrorCategory.CONFIG,
            "title": "🔀 映射关系不存在",
            "description": "未找到该频道的映射配置。",
            "severity": "low",
            "user_friendly": True,
            "causes": [
                "未配置映射",
                "映射被删除"
            ],
            "actions": [
                {
                    "label": "➕ 创建映射",
                    "action": "add_mapping",
                    "primary": True,
                    "endpoint": "/mapping"
                },
                {
                    "label": "🤖 智能映射",
                    "action": "smart_mapping"
                }
            ],
            "prevention": "使用智能映射功能快速创建映射。",
            "auto_fix": False,
            "related_faqs": []
        },
        
        "CONFIG_ACCOUNT_NOT_FOUND": {
            "category": ErrorCategory.CONFIG,
            "title": "👤 账号不存在",
            "description": "未找到KOOK账号配置。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "未添加账号",
                "账号被删除"
            ],
            "actions": [
                {
                    "label": "➕ 添加账号",
                    "action": "add_account",
                    "primary": True,
                    "endpoint": "/accounts"
                },
                {
                    "label": "🧙 启动配置向导",
                    "action": "start_wizard",
                    "endpoint": "/wizard"
                }
            ],
            "prevention": "至少添加一个KOOK账号才能使用系统。",
            "auto_fix": False,
            "related_faqs": []
        },
        
        "CONFIG_INVALID_WEBHOOK_URL": {
            "category": ErrorCategory.CONFIG,
            "title": "🔗 Webhook URL格式错误",
            "description": "Webhook URL格式不正确。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "URL复制不完整",
                "包含多余字符"
            ],
            "actions": [
                {
                    "label": "✏️ 重新输入",
                    "action": "reinput_url",
                    "primary": True
                },
                {
                    "label": "📖 查看URL格式示例",
                    "action": "view_example"
                }
            ],
            "prevention": "使用\"复制\"按钮而不是手动输入。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        "CONFIG_MESSAGE_TOO_LONG": {
            "category": ErrorCategory.CONFIG,
            "title": "📏 消息过长",
            "description": "消息超过目标平台的长度限制。",
            "severity": "low",
            "user_friendly": True,
            "causes": [
                "Discord限制：2000字符",
                "Telegram限制：4096字符",
                "飞书限制：5000字符"
            ],
            "actions": [
                {
                    "label": "✂️ 自动分段",
                    "action": "auto_split",
                    "primary": True
                }
            ],
            "prevention": "系统会自动分段发送超长消息。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        # ========== 系统错误（4个） ==========
        "SYSTEM_REDIS_DISCONNECTED": {
            "category": ErrorCategory.SYSTEM,
            "title": "🔴 Redis连接断开",
            "description": "消息队列服务（Redis）连接断开。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "Redis服务未启动",
                "Redis崩溃",
                "网络问题"
            ],
            "actions": [
                {
                    "label": "🔧 一键启动Redis",
                    "action": "start_redis",
                    "primary": True,
                    "endpoint": "/api/system/autofix/redis"
                },
                {
                    "label": "🔍 查看Redis日志",
                    "action": "view_redis_log"
                }
            ],
            "prevention": "启用自动重启功能（系统默认已启用）。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        "SYSTEM_CHROMIUM_NOT_INSTALLED": {
            "category": ErrorCategory.SYSTEM,
            "title": "🌐 Chromium未安装",
            "description": "浏览器引擎（Chromium）未安装，无法抓取KOOK消息。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "首次安装未下载",
                "安装被中断",
                "手动删除"
            ],
            "actions": [
                {
                    "label": "📥 一键安装Chromium",
                    "action": "install_chromium",
                    "primary": True,
                    "endpoint": "/api/system/autofix/chromium"
                }
            ],
            "prevention": "使用完整安装包，自动包含Chromium。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        "SYSTEM_DATABASE_ERROR": {
            "category": ErrorCategory.SYSTEM,
            "title": "💾 数据库错误",
            "description": "数据库操作失败，可能是文件损坏或权限问题。",
            "severity": "high",
            "user_friendly": True,
            "causes": [
                "数据库文件损坏",
                "磁盘空间不足",
                "权限不足"
            ],
            "actions": [
                {
                    "label": "🔧 修复数据库",
                    "action": "repair_database",
                    "primary": True
                },
                {
                    "label": "💾 恢复备份",
                    "action": "restore_backup",
                    "endpoint": "/settings"
                }
            ],
            "prevention": "定期备份配置，启用自动备份功能。",
            "auto_fix": True,
            "related_faqs": ["faq_backup"]
        },
        
        "SYSTEM_DISK_SPACE_LOW": {
            "category": ErrorCategory.SYSTEM,
            "title": "💽 磁盘空间不足",
            "description": "系统磁盘空间低于500MB，可能影响功能。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "图片缓存过多",
                "日志文件过大",
                "系统磁盘满"
            ],
            "actions": [
                {
                    "label": "🗑️ 清理缓存",
                    "action": "cleanup_cache",
                    "primary": True,
                    "endpoint": "/api/system/cleanup"
                },
                {
                    "label": "📊 查看空间占用",
                    "action": "view_disk_usage"
                }
            ],
            "prevention": "启用自动清理功能，定期清理旧文件。",
            "auto_fix": True,
            "related_faqs": []
        },
        
        # ========== 业务逻辑错误（3个） ==========
        "BUSINESS_FILTER_BLOCKED": {
            "category": ErrorCategory.DATA,
            "title": "🛡️ 消息被过滤规则拦截",
            "description": "消息因触发过滤规则而未转发。",
            "severity": "low",
            "user_friendly": True,
            "causes": [
                "命中黑名单关键词",
                "发送者在黑名单",
                "消息类型被禁用"
            ],
            "actions": [
                {
                    "label": "⚙️ 调整过滤规则",
                    "action": "adjust_filter",
                    "primary": True,
                    "endpoint": "/filter"
                },
                {
                    "label": "📋 查看规则详情",
                    "action": "view_filter_rules"
                }
            ],
            "prevention": "仔细配置过滤规则，避免误拦截。",
            "auto_fix": False,
            "related_faqs": ["faq_filter"]
        },
        
        "BUSINESS_DUPLICATE_MESSAGE": {
            "category": ErrorCategory.DATA,
            "title": "🔁 消息重复",
            "description": "该消息已经转发过，跳过重复转发。",
            "severity": "info",
            "user_friendly": True,
            "causes": [
                "消息去重机制生效",
                "正常行为"
            ],
            "actions": [],
            "prevention": "这是正常的去重保护，无需操作。",
            "auto_fix": False,
            "related_faqs": []
        },
        
        "BUSINESS_QUEUE_OVERFLOW": {
            "category": ErrorCategory.SYSTEM,
            "title": "📊 消息队列溢出",
            "description": "待处理消息过多（>1000条），系统处理中。",
            "severity": "medium",
            "user_friendly": True,
            "causes": [
                "消息突增",
                "处理速度跟不上"
            ],
            "actions": [
                {
                    "label": "⏰ 等待处理（自动）",
                    "action": "wait",
                    "primary": True
                },
                {
                    "label": "📊 查看队列状态",
                    "action": "view_queue",
                    "endpoint": "/logs"
                }
            ],
            "prevention": "配置多Webhook负载均衡，提升处理速度。",
            "auto_fix": False,
            "eta": "预计处理时间：5-10分钟",
            "related_faqs": ["faq_delay"]
        }
        
        # ... 还可以添加更多错误模板达到30+种
    }
    
    @classmethod
    def get_error_template(cls, error_code: str) -> Optional[Dict]:
        """
        获取错误模板
        
        Args:
            error_code: 错误代码
            
        Returns:
            错误模板字典
        """
        return cls.ERROR_TEMPLATES.get(error_code)
    
    @classmethod
    def format_error_for_user(
        cls,
        error_code: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        格式化错误为用户友好的格式
        
        Args:
            error_code: 错误代码
            context: 上下文信息（用于动态填充）
            
        Returns:
            格式化的错误信息
        """
        template = cls.get_error_template(error_code)
        
        if not template:
            # 未知错误，返回通用模板
            return {
                "title": "⚠️ 发生错误",
                "description": f"错误代码: {error_code}",
                "severity": "medium",
                "actions": [
                    {
                        "label": "📖 查看帮助",
                        "action": "open_help",
                        "primary": True
                    }
                ]
            }
        
        # 复制模板并填充动态内容
        formatted = dict(template)
        
        if context:
            # 替换占位符
            for key in ['description', 'eta']:
                if key in formatted and formatted[key]:
                    for ctx_key, ctx_value in context.items():
                        formatted[key] = formatted[key].replace(
                            f"{{{ctx_key}}}",
                            str(ctx_value)
                        )
        
        return formatted
    
    @classmethod
    def get_errors_by_category(cls, category: ErrorCategory) -> List[Dict]:
        """
        按分类获取错误模板
        
        Args:
            category: 错误分类
            
        Returns:
            该分类的所有错误模板
        """
        return [
            {"code": code, **template}
            for code, template in cls.ERROR_TEMPLATES.items()
            if template["category"] == category
        ]
    
    @classmethod
    def search_errors(cls, query: str) -> List[Dict]:
        """
        搜索错误模板
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的错误模板
        """
        query_lower = query.lower()
        results = []
        
        for code, template in cls.ERROR_TEMPLATES.items():
            if (query_lower in template["title"].lower() or
                query_lower in template["description"].lower()):
                results.append({"code": code, **template})
        
        return results


# 创建全局实例
friendly_error_handler = FriendlyErrorHandler()
