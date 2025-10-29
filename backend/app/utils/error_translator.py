"""
用户友好错误处理系统
将技术错误翻译为普通用户能理解的消息
"""

import re
from typing import Dict, List, Optional, Any
from ..utils.logger import logger


class UserFriendlyErrorTranslator:
    """
    用户友好错误翻译器
    
    将技术错误信息翻译为用户能理解的自然语言描述
    并提供解决建议
    """
    
    # 错误消息模板库
    ERROR_TEMPLATES = {
        # ========== Playwright相关错误 ==========
        "PlaywrightError": {
            "timeout": {
                "title": "KOOK登录超时",
                "message": """
登录KOOK时发生超时。可能的原因：
1. 网络连接不稳定或速度较慢
2. Cookie已过期，需要重新获取
3. KOOK服务器响应缓慢
4. 防火墙或代理设置阻止了连接

建议解决方案：
• 检查网络连接是否正常
• 重新获取Cookie并导入
• 稍后再试
• 如果使用代理，请检查代理设置
                """,
                "actions": ["重新获取Cookie", "检查网络", "稍后重试"],
                "severity": "warning"
            },
            "navigation": {
                "title": "无法访问KOOK网站",
                "message": """
无法打开KOOK网页。可能的原因：
1. 网络连接中断
2. KOOK网站正在维护
3. DNS解析失败
4. 本地防火墙阻止访问

建议解决方案：
• 检查网络连接
• 尝试在浏览器中手动访问 www.kookapp.cn
• 检查系统防火墙设置
• 如果问题持续，可能是KOOK网站维护中
                """,
                "actions": ["检查网络", "访问KOOK网站", "检查防火墙"],
                "severity": "error"
            },
            "browser": {
                "title": "浏览器启动失败",
                "message": """
无法启动内置浏览器。可能的原因：
1. Chromium浏览器未正确安装
2. 系统资源不足
3. 浏览器文件损坏

建议解决方案：
• 重新安装系统（会自动安装浏览器）
• 检查磁盘空间是否充足
• 关闭其他占用资源的程序
                """,
                "actions": ["重新安装", "检查磁盘空间", "关闭其他程序"],
                "severity": "error"
            }
        },
        
        # ========== 网络相关错误 ==========
        "ConnectionError": {
            "refused": {
                "title": "服务未启动",
                "message": """
无法连接到服务。可能的原因：
1. Redis服务未启动
2. 后端API服务未运行
3. 端口被其他程序占用

建议解决方案：
• 检查Redis是否正在运行
• 重启后端服务
• 检查端口9527和6379是否被占用
                """,
                "actions": ["启动Redis", "重启服务", "检查端口"],
                "severity": "error"
            },
            "timeout": {
                "title": "连接超时",
                "message": """
连接服务超时。可能的原因：
1. 网络连接不稳定
2. 服务器响应缓慢
3. 防火墙阻止连接

建议解决方案：
• 检查网络连接
• 稍后重试
• 检查防火墙设置
                """,
                "actions": ["检查网络", "稍后重试", "检查防火墙"],
                "severity": "warning"
            }
        },
        
        # ========== 数据库相关错误 ==========
        "sqlite3.OperationalError": {
            "locked": {
                "title": "数据库被占用",
                "message": """
数据库文件被占用，无法访问。可能的原因：
1. 另一个程序实例正在运行
2. 数据库文件被其他程序打开
3. 系统异常关闭导致锁未释放

建议解决方案：
• 关闭其他运行中的程序实例
• 重启系统
• 如果问题持续，可能需要删除数据库锁文件
                """,
                "actions": ["关闭其他实例", "重启系统", "删除锁文件"],
                "severity": "warning"
            },
            "readonly": {
                "title": "数据库只读",
                "message": """
数据库文件为只读状态，无法写入。可能的原因：
1. 文件权限设置为只读
2. 磁盘空间已满
3. 文件所在分区为只读挂载

建议解决方案：
• 检查数据库文件权限
• 检查磁盘空间是否充足
• 使用管理员权限运行程序
                """,
                "actions": ["检查权限", "检查磁盘空间", "以管理员运行"],
                "severity": "error"
            }
        },
        
        # ========== Discord相关错误 ==========
        "DiscordWebhookError": {
            "invalid_url": {
                "title": "Discord Webhook URL无效",
                "message": """
提供的Webhook URL格式不正确。

正确的URL格式示例：
https://discord.com/api/webhooks/123456789/abcdefghijklmnop

建议解决方案：
• 重新从Discord服务器设置中复制Webhook URL
• 确保复制了完整的URL
• 检查URL中是否有多余的空格
                """,
                "actions": ["重新复制URL", "检查格式", "查看教程"],
                "severity": "error"
            },
            "rate_limit": {
                "title": "Discord API限流",
                "message": """
发送消息过于频繁，触发Discord API限流。

Discord限制：
• 每个Webhook每5秒最多发送5条消息

建议解决方案：
• 系统会自动排队重试
• 减少频道映射数量
• 等待几分钟后恢复正常
                """,
                "actions": ["等待恢复", "减少映射", "查看队列"],
                "severity": "warning"
            },
            "not_found": {
                "title": "Webhook不存在",
                "message": """
Discord Webhook已被删除或不存在。

可能的原因：
1. Webhook已在Discord中被删除
2. URL复制错误
3. 服务器权限变更

建议解决方案：
• 在Discord服务器中重新创建Webhook
• 更新系统中的Webhook配置
                """,
                "actions": ["重新创建Webhook", "更新配置", "查看教程"],
                "severity": "error"
            }
        },
        
        # ========== Telegram相关错误 ==========
        "TelegramError": {
            "invalid_token": {
                "title": "Telegram Bot Token无效",
                "message": """
提供的Bot Token不正确。

正确的Token格式示例：
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

建议解决方案：
• 从@BotFather处重新获取Token
• 确保复制了完整的Token
• 检查Token中是否有多余字符
                """,
                "actions": ["重新获取Token", "检查格式", "查看教程"],
                "severity": "error"
            },
            "chat_not_found": {
                "title": "Telegram群组不存在",
                "message": """
找不到指定的Telegram群组。

可能的原因：
1. Chat ID错误
2. Bot未被添加到群组
3. Bot没有发送消息的权限

建议解决方案：
• 确保Bot已被添加到目标群组
• 使用"自动获取Chat ID"功能重新获取
• 给Bot管理员权限（推荐）
                """,
                "actions": ["添加Bot到群组", "重新获取Chat ID", "授予权限"],
                "severity": "error"
            },
            "flood_wait": {
                "title": "Telegram限流",
                "message": """
发送消息过于频繁，Telegram要求等待。

Telegram限制：
• 每个Bot每秒最多发送30条消息
• 向同一群组发送过多消息会触发限流

建议解决方案：
• 系统会自动等待并重试
• 这是正常的保护机制
• 无需手动操作
                """,
                "actions": ["等待自动恢复", "查看队列"],
                "severity": "info"
            }
        },
        
        # ========== 飞书相关错误 ==========
        "FeishuError": {
            "invalid_credentials": {
                "title": "飞书应用凭证无效",
                "message": """
App ID或App Secret不正确。

建议解决方案：
• 登录飞书开放平台检查凭证
• 确保复制了正确的App ID和Secret
• 检查应用状态是否为"已启用"
                """,
                "actions": ["检查凭证", "查看应用状态", "查看教程"],
                "severity": "error"
            },
            "permission_denied": {
                "title": "飞书权限不足",
                "message": """
应用没有足够的权限发送消息。

需要的权限：
• im:message
• im:message:send_as_bot

建议解决方案：
• 在飞书开放平台为应用添加所需权限
• 重新发布应用版本
• 确保机器人已被添加到群组
                """,
                "actions": ["添加权限", "重新发布", "添加到群组"],
                "severity": "error"
            }
        },
        
        # ========== 通用错误 ==========
        "ValueError": {
            "invalid_format": {
                "title": "数据格式错误",
                "message": """
提供的数据格式不正确。

建议解决方案：
• 检查输入的数据格式
• 参考示例重新输入
• 查看帮助文档
                """,
                "actions": ["检查格式", "查看示例", "查看文档"],
                "severity": "error"
            }
        },
        
        "FileNotFoundError": {
            "missing_file": {
                "title": "文件不存在",
                "message": """
找不到所需的文件。

可能的原因：
1. 文件已被删除
2. 文件路径错误
3. 权限不足无法访问

建议解决方案：
• 检查文件是否存在
• 确认文件路径正确
• 检查文件权限
                """,
                "actions": ["检查文件", "检查路径", "检查权限"],
                "severity": "error"
            }
        },
        
        "PermissionError": {
            "access_denied": {
                "title": "权限不足",
                "message": """
没有权限执行此操作。

建议解决方案：
• 以管理员身份运行程序
• 检查文件/目录权限
• 关闭可能占用文件的其他程序
                """,
                "actions": ["以管理员运行", "检查权限", "关闭其他程序"],
                "severity": "error"
            }
        }
    }
    
    # 关键词匹配规则
    KEYWORD_PATTERNS = {
        # Playwright错误
        r"timeout.*exceeded": ("PlaywrightError", "timeout"),
        r"navigation.*failed": ("PlaywrightError", "navigation"),
        r"browser.*not.*found": ("PlaywrightError", "browser"),
        
        # 连接错误
        r"connection.*refused": ("ConnectionError", "refused"),
        r"connection.*timeout": ("ConnectionError", "timeout"),
        
        # 数据库错误
        r"database.*locked": ("sqlite3.OperationalError", "locked"),
        r"readonly.*database": ("sqlite3.OperationalError", "readonly"),
        
        # Discord错误
        r"invalid.*webhook": ("DiscordWebhookError", "invalid_url"),
        r"rate.*limit": ("DiscordWebhookError", "rate_limit"),
        r"webhook.*not.*found": ("DiscordWebhookError", "not_found"),
        
        # Telegram错误
        r"invalid.*token": ("TelegramError", "invalid_token"),
        r"chat.*not.*found": ("TelegramError", "chat_not_found"),
        r"flood.*wait": ("TelegramError", "flood_wait"),
        
        # 飞书错误
        r"invalid.*app": ("FeishuError", "invalid_credentials"),
        r"permission.*denied": ("FeishuError", "permission_denied"),
        
        # 通用错误
        r"invalid.*format": ("ValueError", "invalid_format"),
        r"file.*not.*found": ("FileNotFoundError", "missing_file"),
        r"permission.*denied": ("PermissionError", "access_denied"),
    }
    
    def translate_error(self, error: Exception) -> Dict[str, Any]:
        """
        翻译错误为用户友好的消息
        
        Args:
            error: 异常对象
        
        Returns:
            {
                "title": "错误标题",
                "message": "详细说明",
                "actions": ["建议操作1", "建议操作2"],
                "severity": "error|warning|info",
                "technical_detail": "技术细节",
                "show_technical": False
            }
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        logger.debug(f"翻译错误: {error_type} - {error_msg[:100]}")
        
        # 1. 尝试精确匹配错误类型
        if error_type in self.ERROR_TEMPLATES:
            template_group = self.ERROR_TEMPLATES[error_type]
            
            # 2. 在该类型下匹配关键词
            for key, template in template_group.items():
                if key in error_msg:
                    return self._format_error_response(error, template)
        
        # 3. 使用正则模式匹配
        for pattern, (err_type, err_key) in self.KEYWORD_PATTERNS.items():
            if re.search(pattern, error_msg, re.IGNORECASE):
                if err_type in self.ERROR_TEMPLATES:
                    if err_key in self.ERROR_TEMPLATES[err_type]:
                        template = self.ERROR_TEMPLATES[err_type][err_key]
                        return self._format_error_response(error, template)
        
        # 4. 默认通用错误消息
        return self._default_error_response(error)
    
    def _format_error_response(self, error: Exception, template: Dict) -> Dict[str, Any]:
        """格式化错误响应"""
        return {
            "title": template["title"],
            "message": template["message"].strip(),
            "actions": template.get("actions", []),
            "severity": template.get("severity", "error"),
            "technical_detail": f"{type(error).__name__}: {str(error)}",
            "show_technical": False
        }
    
    def _default_error_response(self, error: Exception) -> Dict[str, Any]:
        """默认错误响应"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        return {
            "title": "发生错误",
            "message": f"""
系统遇到了一个问题，正在尝试恢复...

如果问题持续出现，请：
• 重启系统
• 查看帮助文档
• 联系技术支持并提供错误详情
            """.strip(),
            "actions": ["重启系统", "查看文档", "联系支持"],
            "severity": "error",
            "technical_detail": f"{error_type}: {error_msg}",
            "show_technical": False
        }
    
    def suggest_actions(self, error: Exception) -> List[str]:
        """
        为错误提供建议操作
        
        Args:
            error: 异常对象
        
        Returns:
            建议操作列表
        """
        error_info = self.translate_error(error)
        return error_info.get("actions", [])


# 全局实例
error_translator = UserFriendlyErrorTranslator()
