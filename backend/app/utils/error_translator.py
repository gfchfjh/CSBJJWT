"""
错误翻译器 - 将技术错误转换为用户友好的提示
✅ P0-2优化：友好错误提示系统
"""

from typing import Dict, List, Optional, Any
from ..utils.logger import logger

# 错误翻译字典
ERROR_TRANSLATIONS = {
    'chromium_not_installed': {
        'title': '🌐 浏览器组件未安装',
        'message': '系统需要Chromium浏览器来监听KOOK消息',
        'solution': [
            '1️⃣ 点击下方"自动安装"按钮',
            '2️⃣ 等待下载完成（约150MB，需要几分钟）',
            '3️⃣ 安装完成后会自动重启应用'
        ],
        'auto_fix': 'install_chromium',
        'severity': 'error',
        'category': 'environment'
    },
    
    'redis_connection_failed': {
        'title': '💾 数据库服务未运行',
        'message': 'Redis数据库服务未启动，无法处理消息队列',
        'solution': [
            '1️⃣ 点击下方"自动启动"按钮',
            '2️⃣ 等待3-5秒让服务完全启动',
            '3️⃣ 如果仍然失败，请重启应用'
        ],
        'auto_fix': 'start_redis',
        'severity': 'error',
        'category': 'service'
    },
    
    'cookie_expired': {
        'title': '🔐 KOOK登录已过期',
        'message': '您的KOOK账号Cookie已失效，需要重新登录才能继续转发消息',
        'solution': [
            '1️⃣ 进入"账号管理"页面',
            '2️⃣ 找到过期的账号，点击"重新登录"按钮',
            '3️⃣ 重新导入Cookie或使用账号密码登录'
        ],
        'auto_fix': None,
        'severity': 'warning',
        'category': 'auth'
    },
    
    'webhook_invalid': {
        'title': '🤖 Discord配置错误',
        'message': 'Discord Webhook地址无效或已被删除',
        'solution': [
            '1️⃣ 检查Webhook地址是否完整（https://discord.com/api/webhooks/...）',
            '2️⃣ 确认该Webhook在Discord服务器中没有被删除',
            '3️⃣ 如需重新创建，查看"帮助中心 → Discord配置教程"'
        ],
        'auto_fix': None,
        'severity': 'error',
        'category': 'config'
    },
    
    'telegram_unauthorized': {
        'title': '✈️ Telegram配置错误',
        'message': 'Telegram Bot Token无效或Bot未加入目标群组',
        'solution': [
            '1️⃣ 检查Bot Token是否正确',
            '2️⃣ 确认Bot已被添加到目标群组',
            '3️⃣ 确认Bot在群组中有发送消息的权限',
            '4️⃣ 查看"帮助中心 → Telegram配置教程"获取详细指导'
        ],
        'auto_fix': None,
        'severity': 'error',
        'category': 'config'
    },
    
    'feishu_auth_failed': {
        'title': '🏢 飞书配置错误',
        'message': '飞书应用凭证无效或权限不足',
        'solution': [
            '1️⃣ 检查App ID和App Secret是否正确',
            '2️⃣ 确认飞书应用已开启"机器人"能力',
            '3️⃣ 确认机器人已被添加到目标群组',
            '4️⃣ 查看"帮助中心 → 飞书配置教程"'
        ],
        'auto_fix': None,
        'severity': 'error',
        'category': 'config'
    },
    
    'network_timeout': {
        'title': '🌐 网络连接超时',
        'message': '无法连接到目标服务器，可能是网络问题',
        'solution': [
            '1️⃣ 检查您的网络连接是否正常',
            '2️⃣ 如果使用了代理，请检查代理配置',
            '3️⃣ 尝试稍后重试',
            '4️⃣ 检查目标平台是否正常运行（Discord/Telegram/飞书）'
        ],
        'auto_fix': None,
        'severity': 'warning',
        'category': 'network'
    },
    
    'rate_limit_exceeded': {
        'title': '⏱️ 发送频率过快',
        'message': '发送消息速度过快，触发了目标平台的限流保护',
        'solution': [
            '1️⃣ 这是正常现象，系统会自动排队处理',
            '2️⃣ 消息不会丢失，会在限流解除后继续发送',
            '3️⃣ 如果经常出现，可以在"设置"中调低转发频率',
            '4️⃣ 查看"实时日志"了解队列状态'
        ],
        'auto_fix': None,
        'severity': 'info',
        'category': 'rate_limit'
    },
    
    'image_download_failed': {
        'title': '🖼️ 图片下载失败',
        'message': '无法下载图片，可能是图片已过期或网络问题',
        'solution': [
            '1️⃣ 检查网络连接',
            '2️⃣ 如果是KOOK图片，可能已被删除或过期',
            '3️⃣ 系统会自动重试3次',
            '4️⃣ 如果持续失败，该条消息会被跳过'
        ],
        'auto_fix': None,
        'severity': 'warning',
        'category': 'media'
    },
    
    'image_too_large': {
        'title': '🖼️ 图片文件过大',
        'message': '图片超过目标平台限制（Discord: 8MB, Telegram: 10MB, 飞书: 20MB）',
        'solution': [
            '1️⃣ 系统会自动压缩图片',
            '2️⃣ 如果仍然过大，会使用图床链接',
            '3️⃣ 您可以在"设置 → 图片处理"中调整压缩质量',
            '4️⃣ 如果需要保留原图，可启用"仅使用图床"模式'
        ],
        'auto_fix': 'compress_image',
        'severity': 'info',
        'category': 'media'
    },
    
    'disk_space_low': {
        'title': '💽 磁盘空间不足',
        'message': '图床存储空间不足，可能影响图片转发',
        'solution': [
            '1️⃣ 进入"设置 → 图床管理"',
            '2️⃣ 点击"清理旧图片"释放空间',
            '3️⃣ 建议清理7天前的图片',
            '4️⃣ 或者调整"最大占用空间"限制'
        ],
        'auto_fix': 'cleanup_old_images',
        'severity': 'warning',
        'category': 'storage'
    },
    
    'mapping_not_found': {
        'title': '🔀 未配置映射关系',
        'message': '该KOOK频道未配置转发映射，消息无法转发',
        'solution': [
            '1️⃣ 进入"频道映射"页面',
            '2️⃣ 为该频道添加映射关系',
            '3️⃣ 或使用"智能映射"自动创建',
            '4️⃣ 查看"帮助中心 → 频道映射教程"'
        ],
        'auto_fix': None,
        'severity': 'info',
        'category': 'config'
    },
    
    'bot_not_configured': {
        'title': '🤖 未配置转发Bot',
        'message': '没有可用的Bot配置，无法转发消息',
        'solution': [
            '1️⃣ 进入"机器人配置"页面',
            '2️⃣ 添加至少一个Bot（Discord/Telegram/飞书）',
            '3️⃣ 测试Bot连接是否正常',
            '4️⃣ 查看"帮助中心"了解如何创建Bot'
        ],
        'auto_fix': None,
        'severity': 'error',
        'category': 'config'
    },
    
    'message_too_long': {
        'title': '📝 消息内容过长',
        'message': '消息超过目标平台限制（Discord: 2000字符, Telegram: 4096字符）',
        'solution': [
            '1️⃣ 系统会自动分割消息',
            '2️⃣ 长消息会被分成多条发送',
            '3️⃣ 不会丢失任何内容',
            '4️⃣ 如果不希望分割，可以在过滤规则中设置长度限制'
        ],
        'auto_fix': 'split_message',
        'severity': 'info',
        'category': 'content'
    },
    
    'permission_denied': {
        'title': '🚫 权限不足',
        'message': 'Bot没有足够的权限执行操作',
        'solution': [
            '1️⃣ 检查Bot在目标群组/频道的权限',
            '2️⃣ Discord: 确保Bot有"发送消息"和"嵌入链接"权限',
            '3️⃣ Telegram: 确保Bot不是受限模式',
            '4️⃣ 飞书: 检查应用权限配置'
        ],
        'auto_fix': None,
        'severity': 'error',
        'category': 'permission'
    },
    
    'database_locked': {
        'title': '🔒 数据库被锁定',
        'message': '数据库文件被其他进程占用，无法写入',
        'solution': [
            '1️⃣ 检查是否有其他KOOK转发程序正在运行',
            '2️⃣ 关闭其他可能使用数据库的程序',
            '3️⃣ 重启应用通常可以解决此问题',
            '4️⃣ 如果问题持续，可能需要删除.lock文件'
        ],
        'auto_fix': 'restart_app',
        'severity': 'error',
        'category': 'database'
    },
    
    'port_already_in_use': {
        'title': '🔌 端口已被占用',
        'message': '应用需要的端口（9527）已被其他程序使用',
        'solution': [
            '1️⃣ 检查是否有其他KOOK转发程序正在运行',
            '2️⃣ 使用任务管理器关闭占用端口的程序',
            '3️⃣ 可以在设置中更改应用端口',
            '4️⃣ 重启计算机可以释放所有端口'
        ],
        'auto_fix': 'kill_port_process',
        'severity': 'error',
        'category': 'service'
    },
    
    'python_missing_dependency': {
        'title': '📦 缺少依赖包',
        'message': '缺少必要的Python依赖包，应用无法正常运行',
        'solution': [
            '1️⃣ 通常是安装包损坏导致',
            '2️⃣ 建议重新下载完整的安装包',
            '3️⃣ 开发者可以运行：pip install -r requirements.txt',
            '4️⃣ 查看"帮助中心 → 故障排查"获取详细指导'
        ],
        'auto_fix': None,
        'severity': 'error',
        'category': 'environment'
    },
    
    'json_parse_error': {
        'title': '📄 配置文件格式错误',
        'message': '配置文件损坏或格式不正确',
        'solution': [
            '1️⃣ 配置文件可能被意外修改',
            '2️⃣ 进入"设置 → 备份恢复"恢复之前的配置',
            '3️⃣ 或删除配置文件，重新配置（会丢失所有设置）',
            '4️⃣ 配置文件位置：用户文档/KookForwarder/config.json'
        ],
        'auto_fix': 'restore_config',
        'severity': 'error',
        'category': 'config'
    },
    
    'ssl_certificate_error': {
        'title': '🔐 SSL证书错误',
        'message': '无法验证服务器的SSL证书，可能是网络问题或证书过期',
        'solution': [
            '1️⃣ 检查系统时间是否正确',
            '2️⃣ 检查网络连接是否稳定',
            '3️⃣ 如果使用代理，请检查代理配置',
            '4️⃣ 尝试临时禁用防火墙或杀毒软件'
        ],
        'auto_fix': None,
        'severity': 'warning',
        'category': 'network'
    },
    
    'memory_error': {
        'title': '🧠 内存不足',
        'message': '系统可用内存不足，可能导致应用崩溃',
        'solution': [
            '1️⃣ 关闭其他占用内存的程序',
            '2️⃣ 减少同时监听的KOOK账号数量',
            '3️⃣ 在"设置"中降低图片缓存大小',
            '4️⃣ 建议电脑至少有4GB可用内存'
        ],
        'auto_fix': 'reduce_cache',
        'severity': 'warning',
        'category': 'system'
    },
    
    'file_not_found': {
        'title': '📂 文件未找到',
        'message': '程序需要的文件不存在或被删除',
        'solution': [
            '1️⃣ 可能是安装不完整',
            '2️⃣ 重新下载并安装应用',
            '3️⃣ 确保杀毒软件没有隔离文件',
            '4️⃣ 检查文件路径是否正确'
        ],
        'auto_fix': None,
        'severity': 'error',
        'category': 'system'
    },
    
    'encoding_error': {
        'title': '🔤 字符编码错误',
        'message': '消息包含无法处理的特殊字符',
        'solution': [
            '1️⃣ 这通常是表情符号或特殊字符导致',
            '2️⃣ 系统会自动尝试转换字符',
            '3️⃣ 如果持续失败，可以在过滤规则中排除此类消息',
            '4️⃣ 查看技术详情了解具体是哪个字符'
        ],
        'auto_fix': 'clean_text',
        'severity': 'info',
        'category': 'content'
    },
    
    'proxy_error': {
        'title': '🌐 代理连接失败',
        'message': '配置的代理服务器无法连接',
        'solution': [
            '1️⃣ 检查代理地址和端口是否正确',
            '2️⃣ 确认代理服务器正在运行',
            '3️⃣ 尝试禁用代理，直接连接',
            '4️⃣ 进入"设置 → 网络"修改代理配置'
        ],
        'auto_fix': 'disable_proxy',
        'severity': 'warning',
        'category': 'network'
    },
    
    'account_banned': {
        'title': '⚠️ KOOK账号被封禁',
        'message': '您的KOOK账号可能因违规被封禁或限制',
        'solution': [
            '1️⃣ 尝试在KOOK官方网站登录验证',
            '2️⃣ 联系KOOK客服了解封禁原因',
            '3️⃣ 频繁使用自动化工具可能导致封号',
            '4️⃣ 建议遵守KOOK服务条款，谨慎使用'
        ],
        'auto_fix': None,
        'severity': 'error',
        'category': 'auth'
    },
    
    'channel_deleted': {
        'title': '🗑️ 频道已被删除',
        'message': 'KOOK频道或Discord/Telegram群组已被删除',
        'solution': [
            '1️⃣ 确认频道/群组是否真的被删除',
            '2️⃣ 进入"频道映射"删除无效的映射',
            '3️⃣ 重新配置映射关系',
            '4️⃣ 系统会自动跳过已删除的频道'
        ],
        'auto_fix': 'remove_mapping',
        'severity': 'warning',
        'category': 'config'
    },
    
    'captcha_failed': {
        'title': '🔢 验证码识别失败',
        'message': '自动验证码识别失败，需要人工输入',
        'solution': [
            '1️⃣ 手动输入验证码继续登录',
            '2️⃣ 如果使用2Captcha，检查API Key和余额',
            '3️⃣ 可以安装ddddocr库启用本地OCR识别',
            '4️⃣ 查看"帮助中心 → 验证码处理"了解更多'
        ],
        'auto_fix': None,
        'severity': 'info',
        'category': 'auth'
    },
    
    'update_available': {
        'title': '🆕 有新版本可用',
        'message': '发现新版本，建议更新以获得最新功能和修复',
        'solution': [
            '1️⃣ 进入"设置 → 关于"查看更新内容',
            '2️⃣ 点击"立即更新"自动下载安装',
            '3️⃣ 或访问GitHub下载最新版本',
            '4️⃣ 更新前建议备份当前配置'
        ],
        'auto_fix': 'download_update',
        'severity': 'info',
        'category': 'system'
    },
    
    'backup_corrupted': {
        'title': '💾 备份文件损坏',
        'message': '无法恢复配置，备份文件可能已损坏',
        'solution': [
            '1️⃣ 尝试恢复更早的备份文件',
            '2️⃣ 检查备份文件是否完整（.zip或.json）',
            '3️⃣ 如果所有备份都无效，需要重新配置',
            '4️⃣ 建议定期备份配置到云端'
        ],
        'auto_fix': None,
        'severity': 'error',
        'category': 'backup'
    }
}

# 错误关键词匹配表
ERROR_KEYWORDS = {
    'chromium_not_installed': ['chromium', 'playwright', 'browser', 'executable', "doesn't exist"],
    'redis_connection_failed': ['redis', 'connection refused', 'econnrefused', '6379'],
    'cookie_expired': ['cookie', 'expired', 'unauthorized', '401', 'invalid token'],
    'webhook_invalid': ['webhook', 'invalid', '404', 'not found'],
    'telegram_unauthorized': ['telegram', 'unauthorized', '401', 'bot'],
    'feishu_auth_failed': ['feishu', 'lark', 'authorization', '401'],
    'network_timeout': ['timeout', 'timed out', 'econnreset', 'etimedout'],
    'rate_limit_exceeded': ['rate limit', '429', 'too many requests'],
    'image_download_failed': ['image', 'download', 'failed', 'not found'],
    'image_too_large': ['image', 'too large', 'file size', 'maximum'],
    'disk_space_low': ['disk space', 'no space', 'storage'],
    'mapping_not_found': ['mapping', 'not found', 'no mapping'],
    'bot_not_configured': ['bot', 'not configured', 'no bot'],
    'message_too_long': ['message', 'too long', 'exceeds', 'maximum length'],
    'permission_denied': ['permission', 'denied', 'forbidden', '403'],
    'database_locked': ['database', 'locked', 'database is locked'],
    'port_already_in_use': ['port', 'already in use', 'address already in use', 'eaddrinuse'],
    'python_missing_dependency': ['modulenotfounderror', 'importerror', 'no module named'],
    'json_parse_error': ['json', 'parse', 'decode', 'expecting value'],
    'ssl_certificate_error': ['ssl', 'certificate', 'cert', 'https'],
    'memory_error': ['memory', 'out of memory', 'memoryerror'],
    'file_not_found': ['file not found', 'filenotfounderror', 'no such file'],
    'encoding_error': ['encoding', 'unicode', 'decode', 'encode'],
    'proxy_error': ['proxy', 'proxyerror', 'socks'],
    'account_banned': ['banned', 'suspended', 'account disabled'],
    'channel_deleted': ['channel', 'deleted', 'not found', 'no longer exists'],
    'captcha_failed': ['captcha', 'verification', 'recaptcha'],
    'update_available': ['update', 'new version', 'newer version'],
    'backup_corrupted': ['backup', 'corrupted', 'damaged', 'invalid backup']
}


def translate_error(technical_error: str, error_type: Optional[str] = None) -> Dict[str, Any]:
    """
    将技术错误转换为友好提示
    
    Args:
        technical_error: 技术性错误消息
        error_type: 错误类型（可选，用于精确匹配）
        
    Returns:
        友好的错误信息字典
    """
    try:
        technical_error_lower = technical_error.lower()
        
        # 如果指定了错误类型，直接返回
        if error_type and error_type in ERROR_TRANSLATIONS:
            translation = ERROR_TRANSLATIONS[error_type].copy()
            translation['technical_error'] = technical_error
            logger.debug(f"错误翻译（类型匹配）: {error_type} -> {translation['title']}")
            return translation
        
        # 关键词匹配
        for error_key, keywords in ERROR_KEYWORDS.items():
            if any(keyword in technical_error_lower for keyword in keywords):
                translation = ERROR_TRANSLATIONS[error_key].copy()
                translation['technical_error'] = technical_error
                logger.debug(f"错误翻译（关键词匹配）: {error_key} -> {translation['title']}")
                return translation
        
        # 未找到匹配，返回默认友好提示
        logger.warning(f"未找到错误翻译: {technical_error}")
        return {
            'title': '😕 发生了一个错误',
            'message': '系统遇到了一个问题，我们正在尝试解决',
            'solution': [
                '1️⃣ 请查看下方的技术详情',
                '2️⃣ 如果问题持续，请重启应用',
                '3️⃣ 仍未解决可查看帮助中心或联系技术支持',
                '4️⃣ 复制错误信息有助于快速诊断问题'
            ],
            'auto_fix': None,
            'severity': 'error',
            'category': 'unknown',
            'technical_error': technical_error
        }
        
    except Exception as e:
        logger.error(f"错误翻译失败: {str(e)}")
        return {
            'title': '系统错误',
            'message': technical_error,
            'solution': ['请联系技术支持'],
            'auto_fix': None,
            'severity': 'error',
            'category': 'system',
            'technical_error': technical_error
        }


def get_fix_action(fix_type: str) -> Optional[str]:
    """
    获取自动修复动作的描述
    
    Args:
        fix_type: 修复类型
        
    Returns:
        修复动作描述
    """
    fix_actions = {
        'install_chromium': '自动下载并安装Chromium浏览器',
        'start_redis': '自动启动Redis数据库服务',
        'compress_image': '自动压缩图片到合适大小',
        'cleanup_old_images': '自动清理7天前的旧图片',
        'split_message': '自动分割长消息'
    }
    
    return fix_actions.get(fix_type)


def get_error_severity_color(severity: str) -> str:
    """
    获取错误严重程度对应的颜色
    
    Args:
        severity: 严重程度（error/warning/info）
        
    Returns:
        颜色代码
    """
    colors = {
        'error': '#F56C6C',    # 红色
        'warning': '#E6A23C',  # 橙色
        'info': '#409EFF',     # 蓝色
        'success': '#67C23A'   # 绿色
    }
    
    return colors.get(severity, '#909399')


def format_solution_html(solution: List[str]) -> str:
    """
    将解决方案列表格式化为HTML
    
    Args:
        solution: 解决方案步骤列表
        
    Returns:
        HTML格式的解决方案
    """
    html_steps = []
    for step in solution:
        html_steps.append(f'<li>{step}</li>')
    
    return f'<ol>{"".join(html_steps)}</ol>'


def get_all_error_types() -> List[str]:
    """获取所有支持的错误类型"""
    return list(ERROR_TRANSLATIONS.keys())


def get_errors_by_category(category: str) -> List[str]:
    """
    获取指定类别的所有错误
    
    Args:
        category: 错误类别
        
    Returns:
        错误类型列表
    """
    return [
        error_type 
        for error_type, error_info in ERROR_TRANSLATIONS.items()
        if error_info.get('category') == category
    ]


# 导出
__all__ = [
    'translate_error',
    'get_fix_action',
    'get_error_severity_color',
    'format_solution_html',
    'get_all_error_types',
    'get_errors_by_category',
    'ERROR_TRANSLATIONS'
]
