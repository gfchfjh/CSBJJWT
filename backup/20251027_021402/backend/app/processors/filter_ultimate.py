"""
消息过滤器（终极版）
==================
功能：
1. 关键词过滤（黑名单/白名单）
2. 用户过滤（黑白名单）
3. 正则表达式过滤（高级）
4. 消息类型过滤
5. 优先级管理
6. 批量导入规则

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import re
from typing import List, Dict, Tuple, Optional
from ..utils.logger import logger


class MessageFilterUltimate:
    """消息过滤器（终极版）"""
    
    def __init__(self):
        # 关键词规则
        self.keyword_blacklist: List[str] = []
        self.keyword_whitelist: List[str] = []
        
        # 正则表达式规则
        self.regex_blacklist: List[re.Pattern] = []
        self.regex_whitelist: List[re.Pattern] = []
        
        # 用户规则
        self.user_blacklist: List[str] = []
        self.user_whitelist: List[str] = []
        
        # 消息类型规则
        self.allowed_message_types: List[str] = ['text', 'image', 'file']
        
        # 规则启用状态
        self.keyword_filter_enabled = False
        self.regex_filter_enabled = False
        self.user_filter_enabled = False
        self.type_filter_enabled = False
        
        # 白名单优先（启用后，仅转发白名单匹配的消息）
        self.whitelist_priority = True
    
    def load_rules_from_db(self):
        """从数据库加载过滤规则"""
        from ..database import db
        
        try:
            # 加载关键词规则
            keyword_blacklist_rule = db.get_config('filter_keyword_blacklist')
            if keyword_blacklist_rule:
                import json
                self.keyword_blacklist = json.loads(keyword_blacklist_rule)
                self.keyword_filter_enabled = True
            
            keyword_whitelist_rule = db.get_config('filter_keyword_whitelist')
            if keyword_whitelist_rule:
                import json
                self.keyword_whitelist = json.loads(keyword_whitelist_rule)
            
            # 加载正则表达式规则
            regex_blacklist_rule = db.get_config('filter_regex_blacklist')
            if regex_blacklist_rule:
                import json
                patterns = json.loads(regex_blacklist_rule)
                self.regex_blacklist = [re.compile(p, re.IGNORECASE) for p in patterns]
                self.regex_filter_enabled = True
            
            regex_whitelist_rule = db.get_config('filter_regex_whitelist')
            if regex_whitelist_rule:
                import json
                patterns = json.loads(regex_whitelist_rule)
                self.regex_whitelist = [re.compile(p, re.IGNORECASE) for p in patterns]
            
            # 加载用户规则
            user_blacklist_rule = db.get_config('filter_user_blacklist')
            if user_blacklist_rule:
                import json
                self.user_blacklist = json.loads(user_blacklist_rule)
                self.user_filter_enabled = True
            
            user_whitelist_rule = db.get_config('filter_user_whitelist')
            if user_whitelist_rule:
                import json
                self.user_whitelist = json.loads(user_whitelist_rule)
            
            # 加载消息类型规则
            allowed_types_rule = db.get_config('filter_allowed_types')
            if allowed_types_rule:
                import json
                self.allowed_message_types = json.loads(allowed_types_rule)
                self.type_filter_enabled = True
            
            logger.info("✅ 过滤规则已加载")
            
        except Exception as e:
            logger.error(f"加载过滤规则失败: {e}")
    
    def should_forward(self, message: Dict) -> Tuple[bool, str]:
        """
        判断消息是否应该转发（终极版：支持正则表达式）
        
        Args:
            message: 消息数据
            
        Returns:
            (是否转发, 原因)
        """
        content = message.get('content', '')
        sender = message.get('sender_name', '')
        message_type = message.get('message_type', 'text')
        
        # 优先级1: 用户白名单（最高优先级）
        if self.user_filter_enabled and self.user_whitelist:
            if sender in self.user_whitelist:
                return True, "用户白名单"
            elif self.whitelist_priority:
                # 白名单优先模式：不在白名单中的用户直接拒绝
                return False, f"用户不在白名单中: {sender}"
        
        # 优先级2: 用户黑名单
        if self.user_filter_enabled and sender in self.user_blacklist:
            return False, f"用户在黑名单中: {sender}"
        
        # 优先级3: 关键词白名单
        if self.keyword_filter_enabled and self.keyword_whitelist:
            whitelist_matched = any(kw in content for kw in self.keyword_whitelist)
            if whitelist_matched:
                return True, "关键词白名单匹配"
            elif self.whitelist_priority:
                # 白名单优先模式：不匹配白名单的消息直接拒绝
                return False, "未匹配关键词白名单"
        
        # 优先级4: 正则表达式白名单（新增）
        if self.regex_filter_enabled and self.regex_whitelist:
            whitelist_matched = any(pattern.search(content) for pattern in self.regex_whitelist)
            if whitelist_matched:
                return True, "正则表达式白名单匹配"
            elif self.whitelist_priority:
                return False, "未匹配正则表达式白名单"
        
        # 优先级5: 关键词黑名单
        if self.keyword_filter_enabled and self.keyword_blacklist:
            for keyword in self.keyword_blacklist:
                if keyword in content:
                    return False, f"包含黑名单关键词: {keyword}"
        
        # 优先级6: 正则表达式黑名单（新增）
        if self.regex_filter_enabled and self.regex_blacklist:
            for pattern in self.regex_blacklist:
                if pattern.search(content):
                    return False, f"匹配黑名单正则: {pattern.pattern}"
        
        # 优先级7: 消息类型过滤
        if self.type_filter_enabled:
            if message_type not in self.allowed_message_types:
                return False, f"消息类型不允许: {message_type}"
        
        # 全部检查通过
        return True, "通过所有过滤规则"
    
    def add_keyword_blacklist(self, keywords: List[str]):
        """添加关键词黑名单"""
        self.keyword_blacklist.extend(keywords)
        self.keyword_blacklist = list(set(self.keyword_blacklist))  # 去重
        self._save_to_db('filter_keyword_blacklist', self.keyword_blacklist)
    
    def add_keyword_whitelist(self, keywords: List[str]):
        """添加关键词白名单"""
        self.keyword_whitelist.extend(keywords)
        self.keyword_whitelist = list(set(self.keyword_whitelist))
        self._save_to_db('filter_keyword_whitelist', self.keyword_whitelist)
    
    def add_regex_blacklist(self, patterns: List[str]):
        """添加正则表达式黑名单（新增）"""
        for pattern_str in patterns:
            try:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                self.regex_blacklist.append(pattern)
            except re.error as e:
                logger.error(f"正则表达式错误: {pattern_str} - {e}")
        
        # 保存到数据库
        pattern_strs = [p.pattern for p in self.regex_blacklist]
        self._save_to_db('filter_regex_blacklist', pattern_strs)
    
    def add_regex_whitelist(self, patterns: List[str]):
        """添加正则表达式白名单（新增）"""
        for pattern_str in patterns:
            try:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                self.regex_whitelist.append(pattern)
            except re.error as e:
                logger.error(f"正则表达式错误: {pattern_str} - {e}")
        
        # 保存到数据库
        pattern_strs = [p.pattern for p in self.regex_whitelist]
        self._save_to_db('filter_regex_whitelist', pattern_strs)
    
    def add_user_blacklist(self, users: List[str]):
        """添加用户黑名单"""
        self.user_blacklist.extend(users)
        self.user_blacklist = list(set(self.user_blacklist))
        self._save_to_db('filter_user_blacklist', self.user_blacklist)
    
    def add_user_whitelist(self, users: List[str]):
        """添加用户白名单"""
        self.user_whitelist.extend(users)
        self.user_whitelist = list(set(self.user_whitelist))
        self._save_to_db('filter_user_whitelist', self.user_whitelist)
    
    def set_allowed_message_types(self, types: List[str]):
        """设置允许的消息类型"""
        self.allowed_message_types = types
        self._save_to_db('filter_allowed_types', types)
    
    def _save_to_db(self, key: str, value: List):
        """保存规则到数据库"""
        from ..database import db
        import json
        
        db.set_config(key, json.dumps(value, ensure_ascii=False))
    
    def get_stats(self) -> Dict:
        """获取过滤器统计信息"""
        return {
            'keyword_blacklist_count': len(self.keyword_blacklist),
            'keyword_whitelist_count': len(self.keyword_whitelist),
            'regex_blacklist_count': len(self.regex_blacklist),
            'regex_whitelist_count': len(self.regex_whitelist),
            'user_blacklist_count': len(self.user_blacklist),
            'user_whitelist_count': len(self.user_whitelist),
            'allowed_types': self.allowed_message_types,
            'keyword_filter_enabled': self.keyword_filter_enabled,
            'regex_filter_enabled': self.regex_filter_enabled,
            'user_filter_enabled': self.user_filter_enabled,
            'type_filter_enabled': self.type_filter_enabled,
            'whitelist_priority': self.whitelist_priority
        }


# 全局过滤器实例
message_filter_ultimate = MessageFilterUltimate()
