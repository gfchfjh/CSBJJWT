"""
消息过滤模块
支持关键词过滤、用户过滤、消息类型过滤
"""
import re
import json
from typing import Dict, Any, List, Optional
from ..database import db
from ..utils.logger import logger


class MessageFilter:
    """消息过滤器"""
    
    def __init__(self):
        self.rules_cache = {}  # 缓存过滤规则
        self.cache_time = 0
    
    def _load_rules(self) -> Dict[str, Any]:
        """
        加载过滤规则
        
        Returns:
            规则字典
        """
        import time
        
        # 使用缓存（5分钟有效期）
        current_time = time.time()
        if self.rules_cache and (current_time - self.cache_time) < 300:
            return self.rules_cache
        
        try:
            # 从数据库加载规则
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM filter_rules WHERE enabled = 1")
                rows = cursor.fetchall()
            
            rules = {
                'keyword_blacklist': [],
                'keyword_whitelist': [],
                'user_blacklist': [],
                'user_whitelist': [],
                'message_types': [],
                'mention_all_only': False
            }
            
            for row in rows:
                rule_type = row['rule_type']
                
                # 安全地解析JSON（替换eval）
                try:
                    rule_value = json.loads(row['rule_value'])
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"规则值JSON解析失败: {row['rule_value']}, 错误: {e}")
                    continue
                
                if rule_type == 'keyword_blacklist':
                    rules['keyword_blacklist'] = rule_value
                elif rule_type == 'keyword_whitelist':
                    rules['keyword_whitelist'] = rule_value
                elif rule_type == 'user_blacklist':
                    rules['user_blacklist'] = rule_value
                elif rule_type == 'user_whitelist':
                    rules['user_whitelist'] = rule_value
                elif rule_type == 'message_type':
                    rules['message_types'] = rule_value
                elif rule_type == 'mention_all_only':
                    rules['mention_all_only'] = rule_value[0] if rule_value else False
            
            self.rules_cache = rules
            self.cache_time = current_time
            
            return rules
            
        except Exception as e:
            logger.error(f"加载过滤规则失败: {str(e)}")
            return {
                'keyword_blacklist': [],
                'keyword_whitelist': [],
                'user_blacklist': [],
                'user_whitelist': [],
                'message_types': [],
                'mention_all_only': False
            }
    
    def should_forward(self, message: Dict[str, Any]) -> tuple[bool, str]:
        """
        判断消息是否应该转发
        
        Args:
            message: 消息字典
            
        Returns:
            (是否转发, 原因)
        """
        rules = self._load_rules()
        
        # 1. 检查消息类型过滤
        if rules['message_types']:
            message_type = message.get('message_type', 'text')
            if message_type not in rules['message_types']:
                return False, f"消息类型不在允许列表: {message_type}"
        
        # 2. 检查@全体成员过滤
        if rules['mention_all_only']:
            mention_all = message.get('mention_all', False)
            if not mention_all:
                return False, "未@全体成员"
        
        # 3. 检查用户黑名单
        sender_id = message.get('sender_id', '')
        sender_name = message.get('sender_name', '')
        
        if rules['user_blacklist']:
            for user in rules['user_blacklist']:
                if user in [sender_id, sender_name]:
                    return False, f"发送者在黑名单: {sender_name}"
        
        # 4. 检查用户白名单
        if rules['user_whitelist']:
            user_in_whitelist = False
            for user in rules['user_whitelist']:
                if user in [sender_id, sender_name]:
                    user_in_whitelist = True
                    break
            
            if not user_in_whitelist:
                return False, f"发送者不在白名单: {sender_name}"
        
        # 5. 检查关键词黑名单
        content = message.get('content', '')
        
        if rules['keyword_blacklist']:
            for keyword in rules['keyword_blacklist']:
                if self._match_keyword(keyword, content):
                    return False, f"包含黑名单关键词: {keyword}"
        
        # 6. 检查关键词白名单
        if rules['keyword_whitelist']:
            keyword_matched = False
            for keyword in rules['keyword_whitelist']:
                if self._match_keyword(keyword, content):
                    keyword_matched = True
                    break
            
            if not keyword_matched:
                return False, "不包含白名单关键词"
        
        # 所有规则通过
        return True, "通过所有过滤规则"
    
    def _match_keyword(self, keyword: str, content: str) -> bool:
        """
        匹配关键词（支持正则表达式）
        
        Args:
            keyword: 关键词（可能是正则表达式）
            content: 内容
            
        Returns:
            是否匹配
        """
        try:
            # 尝试作为正则表达式匹配
            if re.search(keyword, content, re.IGNORECASE):
                return True
        except re.error:
            # 如果不是有效的正则，当作普通字符串
            if keyword.lower() in content.lower():
                return True
        
        return False
    
    def add_rule(self, rule_type: str, rule_value: List[str], 
                 scope: str = 'global', enabled: bool = True) -> bool:
        """
        添加过滤规则
        
        Args:
            rule_type: 规则类型
            rule_value: 规则值（列表）
            scope: 作用范围（global/channel_id）
            enabled: 是否启用
            
        Returns:
            是否成功
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 检查规则是否已存在
                cursor.execute("""
                    SELECT id FROM filter_rules 
                    WHERE rule_type = ? AND scope = ?
                """, (rule_type, scope))
                
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有规则
                    cursor.execute("""
                        UPDATE filter_rules 
                        SET rule_value = ?, enabled = ?
                        WHERE id = ?
                    """, (json.dumps(rule_value, ensure_ascii=False), 1 if enabled else 0, existing['id']))
                else:
                    # 插入新规则
                    cursor.execute("""
                        INSERT INTO filter_rules (rule_type, rule_value, scope, enabled)
                        VALUES (?, ?, ?, ?)
                    """, (rule_type, json.dumps(rule_value, ensure_ascii=False), scope, 1 if enabled else 0))
            
            # 清空缓存
            self.rules_cache = {}
            
            logger.info(f"添加过滤规则成功: {rule_type}")
            return True
            
        except Exception as e:
            logger.error(f"添加过滤规则失败: {str(e)}")
            return False
    
    def remove_rule(self, rule_id: int) -> bool:
        """
        删除过滤规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            是否成功
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM filter_rules WHERE id = ?", (rule_id,))
            
            # 清空缓存
            self.rules_cache = {}
            
            logger.info(f"删除过滤规则成功: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除过滤规则失败: {str(e)}")
            return False
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """
        获取所有过滤规则
        
        Returns:
            规则列表
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM filter_rules ORDER BY id DESC")
                rows = cursor.fetchall()
            
            rules = []
            for row in rows:
                try:
                    rule_value = json.loads(row['rule_value'])
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"规则值JSON解析失败: {row['rule_value']}, 错误: {e}")
                    rule_value = []
                
                rules.append({
                    'id': row['id'],
                    'rule_type': row['rule_type'],
                    'rule_value': rule_value,
                    'scope': row['scope'],
                    'enabled': bool(row['enabled'])
                })
            
            return rules
            
        except Exception as e:
            logger.error(f"获取过滤规则失败: {str(e)}")
            return []
    
    def update_rule_status(self, rule_id: int, enabled: bool) -> bool:
        """
        更新规则启用状态
        
        Args:
            rule_id: 规则ID
            enabled: 是否启用
            
        Returns:
            是否成功
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE filter_rules 
                    SET enabled = ?
                    WHERE id = ?
                """, (1 if enabled else 0, rule_id))
            
            # 清空缓存
            self.rules_cache = {}
            
            logger.info(f"更新规则状态成功: {rule_id} -> {enabled}")
            return True
            
        except Exception as e:
            logger.error(f"更新规则状态失败: {str(e)}")
            return False


# 全局单例
message_filter = MessageFilter()
