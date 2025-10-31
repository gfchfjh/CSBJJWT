"""
插件系统
提供消息翻译、关键词自动回复、URL预览等扩展功能
"""
from .plugin_system import plugin_manager, PluginBase, PluginInfo, PluginHook
from .translator_plugin import translator_plugin
from .keyword_reply_plugin import keyword_reply_plugin
from .url_preview_plugin import url_preview_plugin
from .sensitive_word_filter import sensitive_word_filter

__all__ = [
    'plugin_manager',
    'PluginBase',
    'PluginInfo',
    'PluginHook',
    'translator_plugin',
    'keyword_reply_plugin',
    'url_preview_plugin',
    'sensitive_word_filter',
]
