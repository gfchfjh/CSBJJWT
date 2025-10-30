"""
KOOK页面选择器配置

提供多种可能的DOM选择器，以适应KOOK页面结构变化
"""

# 服务器列表容器选择器（按优先级排序）
SERVER_CONTAINER_SELECTORS = [
    '.guild-list',
    '[class*="guild-list"]',
    '[class*="server-list"]',
    '[class*="GuildList"]',
    'nav[class*="guild"]',
    'aside[class*="guild"]',
    '[role="navigation"][aria-label*="服务器"]',
    '[role="navigation"][aria-label*="guild"]',
]

# 服务器项选择器
SERVER_ITEM_SELECTORS = [
    '.guild-item',
    '[class*="guild-item"]',
    '[class*="GuildItem"]',
    '[class*="server-item"]',
    '[data-guild-id]',
    '[data-server-id]',
    'a[href*="/guild/"]',
    'div[class*="guild"][class*="item"]',
    '[role="button"][aria-label*="服务器"]',
]

# 服务器ID提取方法
SERVER_ID_ATTRIBUTES = [
    'data-guild-id',
    'data-id',
    'data-server-id',
    'id',
]

# 服务器名称选择器
SERVER_NAME_SELECTORS = [
    '.guild-name',
    '[class*="guild-name"]',
    '[class*="GuildName"]',
    '[class*="name"]',
    '.server-name',
    'span',
    'div',
    '[aria-label]',
]

# 频道列表容器选择器
CHANNEL_CONTAINER_SELECTORS = [
    '.channel-list',
    '[class*="channel-list"]',
    '[class*="ChannelList"]',
    '[class*="channels"]',
    'nav[class*="channel"]',
    'div[class*="sidebar"]',
    '[role="navigation"][aria-label*="频道"]',
    '[role="navigation"][aria-label*="channel"]',
]

# 频道项选择器
CHANNEL_ITEM_SELECTORS = [
    '.channel-item',
    '[class*="channel-item"]',
    '[class*="ChannelItem"]',
    '[data-channel-id]',
    'a[href*="/channel/"]',
    'div[class*="channel"][class*="item"]',
    '[role="link"][aria-label*="频道"]',
    '[role="button"][href*="/channel/"]',
]

# 频道ID提取方法
CHANNEL_ID_ATTRIBUTES = [
    'data-channel-id',
    'data-id',
    'id',
]

# 频道名称选择器
CHANNEL_NAME_SELECTORS = [
    '.channel-name',
    '[class*="channel-name"]',
    '[class*="ChannelName"]',
    '[class*="name"]',
    'span',
    'div',
    '[aria-label]',
]

# 频道类型标识（语音频道）
VOICE_CHANNEL_INDICATORS = [
    'voice',
    'audio',
    'speaker',
    'microphone',
    '语音',
]

# 登录表单选择器
LOGIN_FORM_SELECTORS = {
    'email_input': [
        'input[type="email"]',
        'input[name="email"]',
        'input[placeholder*="邮箱"]',
        'input[placeholder*="Email"]',
    ],
    'password_input': [
        'input[type="password"]',
        'input[name="password"]',
        'input[placeholder*="密码"]',
        'input[placeholder*="Password"]',
    ],
    'submit_button': [
        'button[type="submit"]',
        'button:contains("登录")',
        'button:contains("Login")',
        '.login-button',
        '[class*="submit"]',
    ],
}

# 验证码选择器
CAPTCHA_SELECTORS = {
    'input': [
        'input[name="captcha"]',
        'input[placeholder*="验证码"]',
        'input[placeholder*="Captcha"]',
        '.captcha-input',
    ],
    'image': [
        'img.captcha-image',
        'img[alt*="验证码"]',
        'img[alt*="Captcha"]',
        '.captcha-image',
        '[class*="captcha"] img',
    ],
}

# WebSocket消息类型
WEBSOCKET_MESSAGE_TYPES = {
    'MESSAGE_CREATE': 'MESSAGE_CREATE',
    'MESSAGE_UPDATE': 'MESSAGE_UPDATE',
    'MESSAGE_DELETE': 'MESSAGE_DELETE',
    'MESSAGE_REACTION_ADD': 'MESSAGE_REACTION_ADD',
    'MESSAGE_REACTION_REMOVE': 'MESSAGE_REACTION_REMOVE',
}

# 消息类型
MESSAGE_TYPES = {
    'TEXT': 'text',
    'IMAGE': 'image',
    'VIDEO': 'video',
    'AUDIO': 'audio',
    'FILE': 'file',
    'CARD': 'card',
}


def get_selector_by_priority(selectors: list, element_type: str = "element") -> str:
    """
    获取优先级最高的选择器（用于日志提示）
    
    Args:
        selectors: 选择器列表
        element_type: 元素类型描述
        
    Returns:
        选择器字符串
    """
    if not selectors:
        return f"未定义{element_type}选择器"
    return selectors[0]


def build_combined_selector(selectors: list) -> str:
    """
    将多个选择器组合成一个（用于querySelectorAll）
    
    Args:
        selectors: 选择器列表
        
    Returns:
        组合后的选择器
    """
    return ', '.join(selectors)


# 预定义的组合选择器
COMBINED_SELECTORS = {
    'servers': build_combined_selector(SERVER_ITEM_SELECTORS),
    'channels': build_combined_selector(CHANNEL_ITEM_SELECTORS),
}
