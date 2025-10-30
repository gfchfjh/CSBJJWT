"""
友好化错误提示系统
==================
将技术性错误转换为普通用户可理解的友好提示

作者：KOOK Forwarder Team
日期：2025-10-25
"""

from typing import Dict, Optional, List
import re


class FriendlyErrorMessages:
    """友好错误消息管理器"""
    
    # 错误映射表：技术错误 → 用户友好提示
    ERROR_MAPPINGS = {
        # 网络错误
        'ConnectionRefusedError': {
            'title': '无法连接到服务',
            'message': '服务器拒绝连接，可能原因：',
            'suggestions': [
                '1. 检查服务是否已启动',
                '2. 检查防火墙是否阻止了连接',
                '3. 检查端口是否被其他程序占用'
            ],
            'icon': '🔌'
        },
        'TimeoutError': {
            'title': '连接超时',
            'message': '操作超时，可能原因：',
            'suggestions': [
                '1. 网络连接不稳定，请检查网络',
                '2. 服务器响应缓慢，请稍后重试',
                '3. 防火墙可能阻止了连接'
            ],
            'icon': '⏱️'
        },
        'NetworkError': {
            'title': '网络错误',
            'message': '网络连接出现问题，请检查：',
            'suggestions': [
                '1. 是否已连接到互联网',
                '2. 是否可以访问目标网站',
                '3. 是否需要使用代理'
            ],
            'icon': '🌐'
        },
        
        # Redis错误
        'ConnectionError.*redis': {
            'title': 'Redis服务未启动',
            'message': 'Redis数据库连接失败，请：',
            'suggestions': [
                '1. 检查Redis服务是否已启动',
                '2. 检查Redis端口（默认6379）是否被占用',
                '3. 点击"设置"→"服务管理"→"启动Redis"'
            ],
            'icon': '💾',
            'auto_fix': 'start_redis'
        },
        
        # Playwright错误
        'Playwright.*not.*installed': {
            'title': '浏览器组件缺失',
            'message': 'Chromium浏览器未安装，请：',
            'suggestions': [
                '1. 等待自动安装完成（约300MB）',
                '2. 或手动点击"一键修复"按钮',
                '3. 网络不好可能需要几分钟'
            ],
            'icon': '🌐',
            'auto_fix': 'install_chromium'
        },
        
        # Cookie错误
        'Invalid.*cookie|Cookie.*invalid': {
            'title': 'Cookie无效或已过期',
            'message': 'KOOK登录凭证无效，请：',
            'suggestions': [
                '1. 重新登录KOOK获取新Cookie',
                '2. 检查Cookie格式是否正确',
                '3. 确保Cookie来自www.kookapp.cn域名'
            ],
            'icon': '🍪'
        },
        
        # API错误
        '401.*Unauthorized': {
            'title': '认证失败',
            'message': 'API认证失败，请：',
            'suggestions': [
                '1. 检查API Token是否正确',
                '2. 检查Token是否过期',
                '3. 重新登录或重启应用'
            ],
            'icon': '🔐'
        },
        '403.*Forbidden': {
            'title': '权限不足',
            'message': '没有权限执行此操作，可能原因：',
            'suggestions': [
                '1. KOOK账号权限不足',
                '2. Bot未被添加到目标频道',
                '3. 需要管理员权限'
            ],
            'icon': '🚫'
        },
        '429.*Too Many Requests': {
            'title': '请求过于频繁',
            'message': '操作太快了，请：',
            'suggestions': [
                '1. 等待60秒后重试',
                '2. 减少同时转发的频道数量',
                '3. 系统会自动排队处理，请耐心等待'
            ],
            'icon': '⏰',
            'auto_fix': 'wait_and_retry'
        },
        
        # Discord错误
        'discord.*webhook.*invalid': {
            'title': 'Discord Webhook无效',
            'message': 'Discord Webhook配置有问题，请：',
            'suggestions': [
                '1. 检查Webhook URL是否正确',
                '2. 检查Webhook是否已被删除',
                '3. 重新创建Webhook并更新配置'
            ],
            'icon': '💬'
        },
        
        # Telegram错误
        'telegram.*bot.*invalid': {
            'title': 'Telegram Bot配置错误',
            'message': 'Telegram Bot配置有问题，请：',
            'suggestions': [
                '1. 检查Bot Token是否正确',
                '2. 检查Bot是否已被@BotFather禁用',
                '3. 检查Chat ID是否正确'
            ],
            'icon': '✈️'
        },
        
        # 文件错误
        'PermissionError': {
            'title': '文件权限错误',
            'message': '没有文件操作权限，请：',
            'suggestions': [
                '1. 以管理员身份运行程序',
                '2. 检查文件夹权限设置',
                '3. 更改安装目录到有权限的位置'
            ],
            'icon': '📁'
        },
        'FileNotFoundError': {
            'title': '文件不存在',
            'message': '找不到必需的文件，请：',
            'suggestions': [
                '1. 检查文件是否被误删',
                '2. 重新安装应用',
                '3. 检查安装是否完整'
            ],
            'icon': '📄'
        },
        
        # 数据库错误
        'sqlite3.*database.*locked': {
            'title': '数据库被锁定',
            'message': '数据库文件被其他程序占用，请：',
            'suggestions': [
                '1. 关闭其他运行中的KOOK转发实例',
                '2. 检查是否有数据库备份程序在运行',
                '3. 重启应用'
            ],
            'icon': '🔒'
        },
        
        # 其他常见错误
        'ModuleNotFoundError': {
            'title': '依赖库缺失',
            'message': '程序缺少必要的组件，请：',
            'suggestions': [
                '1. 重新安装应用',
                '2. 使用完整安装包而非精简版',
                '3. 联系技术支持'
            ],
            'icon': '📦',
            'auto_fix': 'reinstall_dependencies'
        }
    }
    
    @classmethod
    def translate(cls, error: Exception, context: Dict = None) -> Dict:
        """
        将技术错误转换为友好提示
        
        Args:
            error: 异常对象
            context: 错误上下文（可选）
            
        Returns:
            友好错误字典
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # 尝试匹配错误类型或错误消息
        matched_template = None
        
        for pattern, template in cls.ERROR_MAPPINGS.items():
            # 精确匹配错误类型
            if pattern == error_type:
                matched_template = template
                break
            
            # 正则匹配错误类型或消息
            if re.search(pattern, error_type, re.IGNORECASE) or \
               re.search(pattern, error_message, re.IGNORECASE):
                matched_template = template
                break
        
        # 如果没有匹配，使用通用模板
        if not matched_template:
            matched_template = {
                'title': '发生了错误',
                'message': '程序遇到了问题：',
                'suggestions': [
                    '1. 请尝试重启应用',
                    '2. 查看日志文件了解详情',
                    '3. 如果问题持续，请联系技术支持'
                ],
                'icon': '❌'
            }
        
        # 构建友好错误对象
        friendly_error = {
            'icon': matched_template.get('icon', '❌'),
            'title': matched_template.get('title', '错误'),
            'message': matched_template.get('message', ''),
            'suggestions': matched_template.get('suggestions', []),
            'auto_fix': matched_template.get('auto_fix'),
            
            # 技术细节（可折叠显示）
            'technical_details': {
                'error_type': error_type,
                'error_message': error_message,
                'context': context or {}
            }
        }
        
        return friendly_error
    
    @classmethod
    def get_quick_solution(cls, error: Exception) -> Optional[str]:
        """
        获取快速解决方案
        
        Args:
            error: 异常对象
            
        Returns:
            解决方案文本（一句话）
        """
        quick_solutions = {
            'ConnectionRefusedError': '请检查服务是否已启动',
            'TimeoutError': '请检查网络连接',
            'ConnectionError.*redis': '请启动Redis服务',
            'Playwright.*not.*installed': '请等待浏览器自动安装',
            'Invalid.*cookie': '请重新登录KOOK获取Cookie',
            '429.*Too Many': '请等待60秒后重试',
            'PermissionError': '请以管理员身份运行',
        }
        
        error_str = f"{type(error).__name__}: {str(error)}"
        
        for pattern, solution in quick_solutions.items():
            if re.search(pattern, error_str, re.IGNORECASE):
                return solution
        
        return '请重启应用或查看帮助文档'


# 全局实例
friendly_errors = FriendlyErrorMessages()
