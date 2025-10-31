"""
转发器模块
支持Discord、Telegram、飞书、企业微信、钉钉
"""
from .discord import discord_forwarder
from .telegram import telegram_forwarder
from .feishu import feishu_forwarder
from .wechatwork import wechatwork_forwarder
from .dingtalk import dingtalk_forwarder

__all__ = [
    'discord_forwarder',
    'telegram_forwarder',
    'feishu_forwarder',
    'wechatwork_forwarder',
    'dingtalk_forwarder',
]
