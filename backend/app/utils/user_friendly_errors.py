"""
✅ P1-4优化：用户友好错误翻译器
将技术错误信息转换为普通用户能理解的语言
"""

import re
from typing import Dict, Any, Optional


class UserFriendlyErrorTranslator:
    """用户友好错误翻译器"""
    
    # 错误映射规则
    ERROR_MAPPINGS = {
        # Playwright/Chromium错误
        r'playwright.*not.*installed|chromium.*not.*found': {
            'title': '🌐 浏览器组件未安装',
            'message': '程序需要Chromium浏览器才能运行',
            'solution': '不用担心！点击"自动安装"按钮，程序会自动为您下载安装Chromium浏览器。\n\n预计需要2-5分钟，请耐心等待。',
            'action': 'auto_install_chromium',
            'action_label': '自动安装Chromium',
            'severity': 'error',
            'can_auto_fix': True
        },
        
        # Redis错误
        r'redis.*connection.*refused|redis.*not.*running': {
            'title': '💾 数据库服务未运行',
            'message': 'Redis是消息队列服务，程序需要它才能工作',
            'solution': '不用担心！点击"自动启动"按钮，程序会自动为您启动Redis服务。',
            'action': 'auto_start_redis',
            'action_label': '自动启动Redis',
            'severity': 'error',
            'can_auto_fix': True
        },
        
        # Cookie过期
        r'cookie.*expired|unauthorized|401.*status|authentication.*failed': {
            'title': '🔑 KOOK登录已过期',
            'message': '您的KOOK账号登录凭证已失效，需要重新登录',
            'solution': '请选择以下方式重新登录：\n\n1. 重新输入账号密码\n2. 重新导入Cookie\n3. 使用浏览器扩展自动导入',
            'action': 'relogin_kook',
            'action_label': '重新登录',
            'severity': 'warning',
            'can_auto_fix': False
        },
        
        # Discord Webhook错误
        r'discord.*webhook.*invalid|discord.*404|webhook.*not.*found': {
            'title': '💬 Discord配置错误',
            'message': '您提供的Discord Webhook地址无效或已失效',
            'solution': '请检查：\n\n1. Webhook地址是否完整复制\n2. Discord中该Webhook是否被删除\n3. 您是否有权限使用该Webhook\n\n建议：重新创建一个Webhook',
            'action': 'reconfigure_discord',
            'action_label': '重新配置Discord',
            'severity': 'error',
            'can_auto_fix': False
        },
        
        # Telegram错误
        r'telegram.*token.*invalid|telegram.*401|bot.*token.*incorrect': {
            'title': '✈️ Telegram配置错误',
            'message': '您提供的Telegram Bot Token无效',
            'solution': '请检查：\n\n1. Token是否完整复制（格式类似：1234567890:ABCdef...）\n2. Bot是否被@BotFather禁用\n\n建议：与@BotFather对话，重新获取Token',
            'action': 'reconfigure_telegram',
            'action_label': '重新配置Telegram',
            'severity': 'error',
            'can_auto_fix': False
        },
        
        # 网络错误
        r'connection.*timeout|network.*error|timeout.*error|connection.*reset': {
            'title': '🌐 网络连接超时',
            'message': '无法连接到服务器，可能是网络问题',
            'solution': '请检查：\n\n1. 网络连接是否正常\n2. 是否需要使用代理/VPN\n3. 防火墙是否拦截\n4. DNS是否正常\n\n建议：尝试重启路由器或切换网络',
            'action': 'check_network',
            'action_label': '网络诊断',
            'severity': 'error',
            'can_auto_fix': False
        },
        
        # 磁盘空间
        r'no.*space|disk.*full|insufficient.*storage': {
            'title': '💿 磁盘空间不足',
            'message': '存储空间即将用完，可能影响程序运行',
            'solution': '请选择以下操作：\n\n1. 清理不需要的文件\n2. 在设置中清理图床缓存\n3. 清理系统临时文件\n4. 删除旧的日志文件',
            'action': 'cleanup_storage',
            'action_label': '清理存储',
            'severity': 'warning',
            'can_auto_fix': True
        },
        
        # 权限错误
        r'permission.*denied|access.*denied|forbidden|403.*status': {
            'title': '🔒 权限不足',
            'message': '程序没有足够的权限执行此操作',
            'solution': '可能的原因：\n\n1. 文件或文件夹权限不足\n2. 需要管理员权限运行\n3. 被安全软件拦截\n\n建议：以管理员身份运行程序',
            'action': 'request_permission',
            'action_label': '请求权限',
            'severity': 'error',
            'can_auto_fix': False
        },
        
        # 端口占用
        r'port.*in.*use|address.*already.*in.*use|port.*9527.*occupied': {
            'title': '⚠️ 端口被占用',
            'message': '程序需要的端口已被其他程序占用',
            'solution': '解决方法：\n\n1. 关闭其他可能占用端口的程序\n2. 重启电脑释放端口\n3. 在设置中更改程序端口\n\n如果问题持续，可能是程序未正常关闭',
            'action': 'change_port',
            'action_label': '更改端口',
            'severity': 'error',
            'can_auto_fix': False
        },
        
        # 配置错误
        r'config.*invalid|configuration.*error|invalid.*config': {
            'title': '⚙️ 配置文件错误',
            'message': '配置文件格式不正确或包含无效值',
            'solution': '解决方法：\n\n1. 重置配置为默认值\n2. 检查最近的配置更改\n3. 手动编辑配置文件\n\n建议：备份当前配置后重置',
            'action': 'reset_config',
            'action_label': '重置配置',
            'severity': 'error',
            'can_auto_fix': True
        },
        
        # 依赖缺失
        r'module.*not.*found|import.*error|no.*module.*named': {
            'title': '📦 程序组件缺失',
            'message': '程序缺少必要的组件或依赖库',
            'solution': '这通常是安装不完整导致的。\n\n解决方法：\n1. 重新安装程序\n2. 检查安装包是否完整\n3. 联系技术支持\n\n建议：下载完整安装包重新安装',
            'action': 'reinstall',
            'action_label': '重新安装',
            'severity': 'error',
            'can_auto_fix': False
        },
        
        # 数据库错误
        r'database.*error|sqlite.*error|sql.*error': {
            'title': '🗄️ 数据库错误',
            'message': '数据库操作失败，可能是数据损坏',
            'solution': '解决方法：\n\n1. 重启程序\n2. 备份数据后修复数据库\n3. 恢复最近的备份\n\n如果问题持续，可能需要重建数据库',
            'action': 'repair_database',
            'action_label': '修复数据库',
            'severity': 'error',
            'can_auto_fix': True
        },
        
        # 消息格式错误
        r'message.*format.*error|invalid.*message|parse.*error': {
            'title': '📝 消息格式错误',
            'message': '收到的消息格式不符合预期，无法处理',
            'solution': '这可能是：\n\n1. KOOK消息格式发生变化\n2. 特殊字符导致解析失败\n3. 程序版本过旧\n\n建议：更新到最新版本',
            'action': 'check_update',
            'action_label': '检查更新',
            'severity': 'warning',
            'can_auto_fix': False
        },
        
        # 限流错误
        r'rate.*limit|too.*many.*requests|429.*status': {
            'title': '⏳ 请求过于频繁',
            'message': '触发了平台的限流保护，请求被暂时限制',
            'solution': '这是正常的保护机制。\n\n程序会自动：\n1. 等待限流解除\n2. 降低请求频率\n3. 排队发送消息\n\n无需担心，消息不会丢失',
            'action': 'wait_rate_limit',
            'action_label': '等待恢复',
            'severity': 'warning',
            'can_auto_fix': True
        }
    }
    
    def translate(self, error: Exception) -> Dict[str, Any]:
        """
        将技术错误转换为用户友好的错误信息
        
        Args:
            error: 异常对象
            
        Returns:
            用户友好的错误信息字典
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # 尝试匹配错误模式
        for pattern, friendly_info in self.ERROR_MAPPINGS.items():
            if re.search(pattern, error_str, re.IGNORECASE):
                return {
                    **friendly_info,
                    'original_error': str(error),
                    'error_type': error_type
                }
        
        # 默认友好错误（无法匹配时）
        return {
            'title': '😕 出现了一个问题',
            'message': '程序遇到了意外情况',
            'solution': '您可以尝试：\n\n1. 重启程序\n2. 查看日志了解详情\n3. 记录错误信息并联系技术支持\n\n如果问题持续出现，请提交Bug报告',
            'action': 'show_logs',
            'action_label': '查看日志',
            'severity': 'error',
            'can_auto_fix': False,
            'original_error': str(error),
            'error_type': error_type
        }
    
    def translate_http_error(self, status_code: int, message: str = '') -> Dict[str, Any]:
        """
        翻译HTTP错误
        
        Args:
            status_code: HTTP状态码
            message: 错误消息
            
        Returns:
            用户友好的错误信息
        """
        error_map = {
            400: {
                'title': '❌ 请求参数错误',
                'message': '发送的请求格式不正确',
                'solution': '这通常是程序Bug。\n\n建议：\n1. 重启程序\n2. 更新到最新版本\n3. 联系技术支持',
                'severity': 'error'
            },
            401: {
                'title': '🔑 需要登录',
                'message': '您的登录凭证已失效',
                'solution': '请重新登录账号',
                'severity': 'warning'
            },
            403: {
                'title': '🔒 权限不足',
                'message': '您没有权限执行此操作',
                'solution': '请检查账号权限设置',
                'severity': 'error'
            },
            404: {
                'title': '🔍 资源不存在',
                'message': '请求的资源未找到',
                'solution': '可能是配置错误或资源已被删除',
                'severity': 'error'
            },
            429: {
                'title': '⏳ 请求过于频繁',
                'message': '触发了限流保护',
                'solution': '程序会自动等待并重试，请稍候',
                'severity': 'warning'
            },
            500: {
                'title': '💥 服务器错误',
                'message': '服务器遇到内部错误',
                'solution': '这通常是临时问题，请稍后重试',
                'severity': 'error'
            },
            502: {
                'title': '🔌 网关错误',
                'message': '无法连接到上游服务器',
                'solution': '请检查网络连接或稍后重试',
                'severity': 'error'
            },
            503: {
                'title': '🚧 服务不可用',
                'message': '服务器暂时无法处理请求',
                'solution': '可能是服务器维护，请稍后重试',
                'severity': 'warning'
            }
        }
        
        if status_code in error_map:
            return {
                **error_map[status_code],
                'action': None,
                'action_label': None,
                'can_auto_fix': False,
                'original_error': f'HTTP {status_code}: {message}'
            }
        
        return {
            'title': f'⚠️ 网络错误 ({status_code})',
            'message': message or '发生了未知的网络错误',
            'solution': '请检查网络连接并重试',
            'action': None,
            'action_label': None,
            'severity': 'error',
            'can_auto_fix': False,
            'original_error': f'HTTP {status_code}: {message}'
        }


# 全局实例
error_translator = UserFriendlyErrorTranslator()


# 便捷函数
def translate_error(error: Exception) -> Dict[str, Any]:
    """翻译错误为用户友好格式"""
    return error_translator.translate(error)


def translate_http_error(status_code: int, message: str = '') -> Dict[str, Any]:
    """翻译HTTP错误"""
    return error_translator.translate_http_error(status_code, message)
