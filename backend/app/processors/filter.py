"""
消息过滤模块
"""
import json
from typing import Dict, List, Any, Optional
from ..database import db
from ..utils.logger import logger


class MessageFilter:
    """消息过滤器"""
    
    def __init__(self):
        self.rules_cache = None
    
    def load_rules(self, scope: str = "global", channel_id: Optional[str] = None) -> Dict:
        """
        加载过滤规则
        
        Args:
            scope: 应用范围（global/channel）
            channel_id: 频道ID（当scope为channel时必需）
            
        Returns:
            过滤规则字典
        """
        try:
            # 从数据库加载规则
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # 查询规则
            if scope == "channel" and channel_id:
                cursor.execute(
                    "SELECT rule_value FROM filter_rules WHERE scope = ? AND enabled = 1",
                    (channel_id,)
                )
            else:
                cursor.execute(
                    "SELECT rule_value FROM filter_rules WHERE scope = 'global' AND enabled = 1"
                )
            
            rows = cursor.fetchall()
            
            # 合并所有规则
            rules = {
                "scope": scope,
                "channel_id": channel_id,
                "keyword_blacklist": [],
                "keyword_whitelist": [],
                "keyword_filter_enabled": False,
                "user_blacklist": [],
                "user_whitelist": [],
                "user_filter_enabled": False,
                "message_types": ["text", "image", "link", "file"],
                "only_mention_all": False
            }
            
            for row in rows:
                try:
                    rule_data = json.loads(row[0])
                    # 合并规则数据
                    for key, value in rule_data.items():
                        if isinstance(value, list):
                            rules[key].extend(value)
                        else:
                            rules[key] = value
                except json.JSONDecodeError:
                    logger.error(f"解析规则失败: {row[0]}")
            
            self.rules_cache = rules
            return rules
            
        except Exception as e:
            logger.error(f"加载过滤规则失败: {str(e)}")
            # 返回默认规则
            return {
                "keyword_blacklist": [],
                "keyword_whitelist": [],
                "keyword_filter_enabled": False,
                "user_blacklist": [],
                "user_whitelist": [],
                "user_filter_enabled": False,
                "message_types": ["text", "image", "link", "file"],
                "only_mention_all": False
            }
    
    def should_forward(self, message: Dict[str, Any]) -> tuple[bool, str]:
        """
        判断消息是否应该转发
        
        Args:
            message: 消息数据
            
        Returns:
            (是否转发, 原因)
        """
        if not self.rules_cache:
            self.load_rules()
        
        content = message.get("content", "")
        sender_id = message.get("sender_id", "")
        sender_name = message.get("sender_name", "")
        message_type = message.get("message_type", "text")
        
        # 检查消息类型
        if message_type not in self.rules_cache["message_types"]:
            return False, f"消息类型 {message_type} 不在转发范围内"
        
        # 检查@全体成员选项
        if self.rules_cache.get("only_mention_all", False):
            # 检查消息是否包含@全体成员
            if "@all" not in content.lower() and "@everyone" not in content.lower():
                return False, "消息不包含@全体成员"
        
        # 检查用户过滤（如果启用）
        if self.rules_cache.get("user_filter_enabled", False):
            # 检查用户黑名单
            for user in self.rules_cache["user_blacklist"]:
                if user.get("id") == sender_id or user.get("name") == sender_name:
                    return False, f"用户 {sender_name} 在黑名单中"
            
            # 检查用户白名单（如果有白名单）
            if self.rules_cache["user_whitelist"]:
                found = False
                for user in self.rules_cache["user_whitelist"]:
                    if user.get("id") == sender_id or user.get("name") == sender_name:
                        found = True
                        break
                if not found:
                    return False, f"用户 {sender_name} 不在白名单中"
        
        # 检查关键词过滤（如果启用）
        if self.rules_cache.get("keyword_filter_enabled", False):
            # 检查关键词黑名单
            for keyword in self.rules_cache["keyword_blacklist"]:
                if keyword.lower() in content.lower():
                    return False, f"包含黑名单关键词: {keyword}"
            
            # 检查关键词白名单（如果有白名单）
            if self.rules_cache["keyword_whitelist"]:
                found = False
                for keyword in self.rules_cache["keyword_whitelist"]:
                    if keyword.lower() in content.lower():
                        found = True
                        break
                if not found:
                    return False, "不包含白名单关键词"
        
        return True, "通过过滤"
    
    def save_rules(self, rules: Dict) -> bool:
        """
        保存过滤规则到数据库
        
        Args:
            rules: 规则字典
            
        Returns:
            是否成功
        """
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            scope = rules.get("scope", "global")
            channel_id = rules.get("channel_id")
            
            # 删除旧规则
            if scope == "channel" and channel_id:
                cursor.execute("DELETE FROM filter_rules WHERE scope = ?", (channel_id,))
            else:
                cursor.execute("DELETE FROM filter_rules WHERE scope = 'global'")
            
            # 插入新规则（将整个规则作为JSON存储）
            rule_value = json.dumps({
                "keyword_blacklist": rules.get("keyword_blacklist", []),
                "keyword_whitelist": rules.get("keyword_whitelist", []),
                "keyword_filter_enabled": rules.get("keyword_filter_enabled", False),
                "user_blacklist": rules.get("user_blacklist", []),
                "user_whitelist": rules.get("user_whitelist", []),
                "user_filter_enabled": rules.get("user_filter_enabled", False),
                "message_types": rules.get("message_types", ["text", "image", "file", "link"]),
                "only_mention_all": rules.get("only_mention_all", False)
            }, ensure_ascii=False)
            
            cursor.execute(
                """INSERT INTO filter_rules (rule_type, rule_value, scope, enabled)
                   VALUES (?, ?, ?, ?)""",
                ("combined", rule_value, scope if scope == "global" else channel_id, 1)
            )
            
            conn.commit()
            
            # 更新缓存
            self.rules_cache = rules
            
            logger.info(f"过滤规则保存成功: scope={scope}")
            return True
            
        except Exception as e:
            logger.error(f"保存过滤规则失败: {str(e)}")
            return False
    
    def get_rules(self) -> Dict:
        """获取当前规则"""
        if not self.rules_cache:
            self.load_rules()
        return self.rules_cache


# 创建全局过滤器实例
message_filter = MessageFilter()
