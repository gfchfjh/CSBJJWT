"""
关键词自动回复插件
根据预设的关键词自动回复消息
"""
import re
from typing import Dict, List, Optional
from .plugin_system import PluginBase, PluginInfo, PluginHook, plugin_manager
from ..utils.logger import logger
from ..config import settings


class KeywordReplyPlugin(PluginBase):
    """关键词自动回复插件"""
    
    def __init__(self):
        super().__init__()
        
        # 默认关键词回复规则
        self.reply_rules: List[Dict] = [
            {
                'keywords': ['帮助', 'help', '使用教程'],
                'reply': '📖 使用帮助：\n1. 配置KOOK账号\n2. 配置目标平台Bot\n3. 设置频道映射\n4. 启动转发服务\n\n更多信息请访问帮助中心。',
                'match_type': 'contains',  # contains/exact/regex
                'enabled': True
            },
            {
                'keywords': ['状态', 'status', '运行状态'],
                'reply': '🟢 系统运行正常\n当前版本: {version}\n运行时长: {uptime}',
                'match_type': 'contains',
                'enabled': True
            },
            {
                'keywords': ['版本', 'version'],
                'reply': f'📦 当前版本: {settings.app_version}\n🔄 检查更新: /api/updates/check',
                'match_type': 'contains',
                'enabled': True
            },
            {
                'keywords': ['功能', 'features', '支持什么'],
                'reply': '✨ 主要功能：\n• Discord消息转发\n• Telegram消息转发\n• 飞书消息转发\n• 企业微信消息转发\n• 钉钉消息转发\n• 智能频道映射\n• 消息过滤规则\n• 图片处理策略',
                'match_type': 'contains',
                'enabled': True
            },
            {
                'keywords': ['联系', 'contact', '反馈'],
                'reply': '📧 联系我们：\nGitHub: https://github.com/gfchfjh/CSBJJWT\nEmail: support@kook-forwarder.com',
                'match_type': 'contains',
                'enabled': True
            }
        ]
        
        # 统计
        self.stats = {
            'total_matched': 0,
            'total_replied': 0,
            'failed': 0
        }
        
        # 从配置加载自定义规则
        self._load_custom_rules()
    
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        return PluginInfo(
            id='keyword_reply',
            name='关键词自动回复',
            version='1.0.0',
            author='KOOK Forwarder Team',
            description='根据关键词自动回复预设消息'
        )
    
    async def on_load(self):
        """插件加载"""
        # 注册钩子 - 在消息处理前检查关键词
        plugin_manager.register_hook(
            PluginHook.AFTER_MESSAGE_PROCESS,
            self.check_and_reply
        )
        
        logger.info(f"关键词自动回复插件已加载，规则数: {len(self.reply_rules)}")
    
    def _load_custom_rules(self):
        """从配置加载自定义规则"""
        try:
            from ..database import db
            
            # 从system_config表加载自定义规则
            rules_json = db.get_config('keyword_reply_rules')
            
            if rules_json:
                import json
                custom_rules = json.loads(rules_json)
                
                # 合并自定义规则（自定义规则优先）
                self.reply_rules = custom_rules + self.reply_rules
                
                logger.info(f"已加载 {len(custom_rules)} 条自定义关键词规则")
                
        except Exception as e:
            logger.warning(f"加载自定义关键词规则失败: {str(e)}")
    
    async def check_and_reply(self, message: Dict) -> Dict:
        """
        检查消息并自动回复
        
        Args:
            message: 消息对象
            
        Returns:
            处理后的消息对象
        """
        content = message.get('content', '').strip()
        
        if not content:
            return message
        
        # 检查每条规则
        for rule in self.reply_rules:
            if not rule.get('enabled', True):
                continue
            
            keywords = rule.get('keywords', [])
            match_type = rule.get('match_type', 'contains')
            
            matched = False
            
            if match_type == 'exact':
                # 精确匹配
                matched = content.lower() in [kw.lower() for kw in keywords]
            elif match_type == 'contains':
                # 包含匹配
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        matched = True
                        break
            elif match_type == 'regex':
                # 正则匹配
                for pattern in keywords:
                    if re.search(pattern, content, re.IGNORECASE):
                        matched = True
                        break
            
            if matched:
                self.stats['total_matched'] += 1
                
                # 获取回复内容
                reply = rule.get('reply', '')
                
                # 支持变量替换
                reply = self._format_reply(reply, message)
                
                # 添加自动回复标记到消息
                message['auto_reply'] = reply
                message['auto_reply_rule'] = rule.get('keywords')[0] if keywords else '未知'
                
                logger.info(f"触发关键词自动回复: {rule.get('keywords')[0]} -> {reply[:50]}...")
                self.stats['total_replied'] += 1
                
                # 只匹配第一条规则
                break
        
        return message
    
    def _format_reply(self, reply: str, message: Dict) -> str:
        """
        格式化回复内容（支持变量替换）
        
        Args:
            reply: 回复模板
            message: 消息对象
            
        Returns:
            格式化后的回复
        """
        # 替换变量
        replacements = {
            '{version}': settings.app_version,
            '{uptime}': self._get_uptime(),
            '{sender}': message.get('sender_name', '未知用户'),
            '{channel}': message.get('channel_name', '未知频道')
        }
        
        for key, value in replacements.items():
            reply = reply.replace(key, str(value))
        
        return reply
    
    def _get_uptime(self) -> str:
        """获取系统运行时间"""
        try:
            from ..utils.system_info import get_uptime
            return get_uptime()
        except:
            return "未知"
    
    def add_rule(self, keywords: List[str], reply: str, 
                 match_type: str = 'contains') -> bool:
        """
        添加新规则
        
        Args:
            keywords: 关键词列表
            reply: 回复内容
            match_type: 匹配类型
            
        Returns:
            是否成功
        """
        try:
            rule = {
                'keywords': keywords,
                'reply': reply,
                'match_type': match_type,
                'enabled': True
            }
            
            self.reply_rules.insert(0, rule)  # 插入到最前面（优先匹配）
            
            # 保存到配置
            self._save_rules()
            
            logger.info(f"已添加关键词回复规则: {keywords}")
            return True
            
        except Exception as e:
            logger.error(f"添加规则失败: {str(e)}")
            return False
    
    def remove_rule(self, keywords: List[str]) -> bool:
        """
        删除规则
        
        Args:
            keywords: 关键词列表
            
        Returns:
            是否成功
        """
        try:
            # 查找并删除规则
            self.reply_rules = [
                rule for rule in self.reply_rules
                if rule.get('keywords') != keywords
            ]
            
            # 保存到配置
            self._save_rules()
            
            logger.info(f"已删除关键词回复规则: {keywords}")
            return True
            
        except Exception as e:
            logger.error(f"删除规则失败: {str(e)}")
            return False
    
    def _save_rules(self):
        """保存规则到数据库"""
        try:
            import json
            from ..database import db
            
            # 只保存自定义规则（排除默认规则）
            default_keywords = [
                ['帮助', 'help', '使用教程'],
                ['状态', 'status', '运行状态'],
                ['版本', 'version'],
                ['功能', 'features', '支持什么'],
                ['联系', 'contact', '反馈']
            ]
            
            custom_rules = [
                rule for rule in self.reply_rules
                if rule.get('keywords') not in default_keywords
            ]
            
            db.set_config('keyword_reply_rules', json.dumps(custom_rules, ensure_ascii=False))
            
        except Exception as e:
            logger.error(f"保存规则失败: {str(e)}")
    
    def get_rules(self) -> List[Dict]:
        """获取所有规则"""
        return self.reply_rules
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'total_rules': len(self.reply_rules),
            'match_rate': (
                self.stats['total_matched'] / max(self.stats['total_replied'], 1) * 100
                if self.stats['total_replied'] > 0 else 0
            )
        }


# 自动注册插件
keyword_reply_plugin = KeywordReplyPlugin()
