"""
消息过滤器（增强版）
P1-5~8: 完善过滤规则

新增功能：
1. 白名单支持
2. 正则表达式支持
3. 规则优先级管理
4. 复杂条件组合
"""
import re
from typing import Dict, Any, List, Optional
from ..database import db
from ..utils.logger import logger


class MessageFilterEnhanced:
    """消息过滤器（增强版）"""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """加载所有过滤规则"""
        try:
            rules_data = db.get_all_filter_rules()
            
            rules = {
                'keyword_blacklist': [],
                'keyword_whitelist': [],
                'user_blacklist': [],
                'user_whitelist': [],
                'regex_blacklist': [],
                'regex_whitelist': [],
                'message_types': [],
                'mention_only': False,
            }
            
            for rule in rules_data:
                if not rule.get('enabled'):
                    continue
                
                rule_type = rule['rule_type']
                rule_value = rule['rule_value']
                
                if rule_type in rules:
                    if isinstance(rules[rule_type], list):
                        # JSON 数组
                        import json
                        try:
                            values = json.loads(rule_value)
                            rules[rule_type].extend(values)
                        except:
                            rules[rule_type].append(rule_value)
                    else:
                        # 布尔值
                        rules[rule_type] = rule_value == 'true'
            
            logger.info(f"已加载过滤规则: {len(rules_data)} 条")
            return rules
            
        except Exception as e:
            logger.error(f"加载过滤规则失败: {str(e)}")
            return {}
    
    def should_forward(self, message: Dict[str, Any]) -> tuple[bool, str]:
        """
        判断消息是否应该转发（增强版）
        
        优先级顺序：
        1. 白名单（最高优先级）
        2. 黑名单
        3. 消息类型
        4. 其他规则
        
        Args:
            message: 消息对象
            
        Returns:
            (是否转发, 原因)
        """
        content = message.get('content', '')
        sender_id = message.get('sender_id', '')
        sender_name = message.get('sender_name', '')
        message_type = message.get('message_type', 'text')
        mentions = message.get('mentions', [])
        
        # 1. 优先级最高：用户白名单
        if self.rules.get('user_whitelist'):
            if sender_id not in self.rules['user_whitelist'] and sender_name not in self.rules['user_whitelist']:
                return False, f"用户不在白名单中: {sender_name}"
            logger.debug(f"✅ 用户白名单匹配: {sender_name}")
        
        # 2. 关键词白名单
        if self.rules.get('keyword_whitelist'):
            matched = False
            for keyword in self.rules['keyword_whitelist']:
                if keyword in content:
                    matched = True
                    logger.debug(f"✅ 关键词白名单匹配: {keyword}")
                    break
            
            if not matched:
                return False, "内容不包含白名单关键词"
        
        # 3. 正则白名单
        if self.rules.get('regex_whitelist'):
            matched = False
            for pattern in self.rules['regex_whitelist']:
                try:
                    if re.search(pattern, content, re.IGNORECASE):
                        matched = True
                        logger.debug(f"✅ 正则白名单匹配: {pattern}")
                        break
                except re.error as e:
                    logger.error(f"正则表达式错误: {pattern}, {e}")
            
            if not matched:
                return False, "内容不匹配白名单正则"
        
        # 4. 用户黑名单
        if self.rules.get('user_blacklist'):
            if sender_id in self.rules['user_blacklist'] or sender_name in self.rules['user_blacklist']:
                return False, f"用户在黑名单中: {sender_name}"
        
        # 5. 关键词黑名单
        if self.rules.get('keyword_blacklist'):
            for keyword in self.rules['keyword_blacklist']:
                if keyword in content:
                    return False, f"内容包含黑名单关键词: {keyword}"
        
        # 6. 正则黑名单
        if self.rules.get('regex_blacklist'):
            for pattern in self.rules['regex_blacklist']:
                try:
                    if re.search(pattern, content, re.IGNORECASE):
                        return False, f"内容匹配黑名单正则: {pattern}"
                except re.error as e:
                    logger.error(f"正则表达式错误: {pattern}, {e}")
        
        # 7. 消息类型过滤
        if self.rules.get('message_types'):
            if message_type not in self.rules['message_types']:
                return False, f"消息类型不在允许列表: {message_type}"
        
        # 8. @提及过滤（仅转发@全体成员）
        if self.rules.get('mention_only'):
            if not message.get('mention_all', False):
                return False, "仅转发@全体成员的消息"
        
        # 所有规则通过
        return True, "通过所有过滤规则"
    
    def reload_rules(self):
        """重新加载规则"""
        logger.info("🔄 重新加载过滤规则...")
        self.rules = self._load_rules()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取过滤规则统计"""
        return {
            'keyword_blacklist_count': len(self.rules.get('keyword_blacklist', [])),
            'keyword_whitelist_count': len(self.rules.get('keyword_whitelist', [])),
            'user_blacklist_count': len(self.rules.get('user_blacklist', [])),
            'user_whitelist_count': len(self.rules.get('user_whitelist', [])),
            'regex_blacklist_count': len(self.rules.get('regex_blacklist', [])),
            'regex_whitelist_count': len(self.rules.get('regex_whitelist', [])),
            'allowed_message_types': self.rules.get('message_types', []),
            'mention_only': self.rules.get('mention_only', False),
        }


# 全局实例
message_filter_enhanced = MessageFilterEnhanced()
