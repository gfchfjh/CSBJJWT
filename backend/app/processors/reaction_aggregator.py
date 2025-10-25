"""
表情反应聚合器
✅ P0-5优化：完善表情反应转发
"""
import time
from typing import Dict, List, Optional
from collections import defaultdict
from ..utils.logger import logger


class ReactionAggregator:
    """表情反应聚合器 - 汇总和格式化表情反应"""
    
    def __init__(self):
        # 存储消息的表情反应
        # 格式: {message_id: {emoji: [{'user_id': str, 'user_name': str, 'timestamp': int}]}}
        self.reactions: Dict[str, Dict[str, List[Dict]]] = defaultdict(lambda: defaultdict(list))
        
        # 最后更新时间（用于决定何时发送汇总）
        self.last_update_time: Dict[str, float] = {}
        
        # 配置
        self.update_interval = 3.0  # 3秒汇总一次
        self.max_users_display = 10  # 最多显示10个用户名
        
        logger.info("✅ 表情反应聚合器已初始化")
    
    def add_reaction(self, message_id: str, emoji: str, user_id: str, 
                     user_name: str, timestamp: Optional[int] = None):
        """
        添加表情反应
        
        Args:
            message_id: 消息ID
            emoji: 表情符号
            user_id: 用户ID
            user_name: 用户名
            timestamp: 时间戳
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        # 检查是否已存在（避免重复）
        existing_users = [r['user_id'] for r in self.reactions[message_id][emoji]]
        if user_id in existing_users:
            logger.debug(f"表情反应已存在: {message_id} {emoji} {user_name}")
            return
        
        # 添加反应
        self.reactions[message_id][emoji].append({
            'user_id': user_id,
            'user_name': user_name,
            'timestamp': timestamp
        })
        
        # 更新最后更新时间
        self.last_update_time[message_id] = time.time()
        
        logger.debug(f"添加表情反应: {message_id} {emoji} {user_name}")
    
    def remove_reaction(self, message_id: str, emoji: str, user_id: str):
        """
        移除表情反应
        
        Args:
            message_id: 消息ID
            emoji: 表情符号
            user_id: 用户ID
        """
        if message_id not in self.reactions:
            return
        
        if emoji not in self.reactions[message_id]:
            return
        
        # 移除该用户的反应
        self.reactions[message_id][emoji] = [
            r for r in self.reactions[message_id][emoji] 
            if r['user_id'] != user_id
        ]
        
        # 如果该表情没有用户了，删除表情
        if not self.reactions[message_id][emoji]:
            del self.reactions[message_id][emoji]
        
        # 如果该消息没有表情了，删除消息记录
        if not self.reactions[message_id]:
            del self.reactions[message_id]
            if message_id in self.last_update_time:
                del self.last_update_time[message_id]
        else:
            # 更新最后更新时间
            self.last_update_time[message_id] = time.time()
        
        logger.debug(f"移除表情反应: {message_id} {emoji} {user_id}")
    
    def should_send_update(self, message_id: str, force: bool = False) -> bool:
        """
        判断是否应该发送反应更新
        
        Args:
            message_id: 消息ID
            force: 强制发送
            
        Returns:
            是否应该发送
        """
        if force:
            return True
        
        if message_id not in self.last_update_time:
            return False
        
        # 检查是否超过更新间隔
        elapsed = time.time() - self.last_update_time[message_id]
        return elapsed >= self.update_interval
    
    def format_reactions(self, message_id: str, platform: str = "discord") -> str:
        """
        格式化表情反应为文本
        
        Args:
            message_id: 消息ID
            platform: 目标平台（discord/telegram/feishu）
            
        Returns:
            格式化后的文本
        """
        if message_id not in self.reactions:
            return ""
        
        reactions_dict = self.reactions[message_id]
        
        if not reactions_dict:
            return ""
        
        # 按表情分组格式化
        parts = []
        
        for emoji, users in reactions_dict.items():
            if not users:
                continue
            
            # 按时间戳排序用户
            sorted_users = sorted(users, key=lambda x: x['timestamp'])
            
            # 获取用户名列表
            user_names = [u['user_name'] for u in sorted_users]
            
            # 格式化用户列表
            if len(user_names) <= self.max_users_display:
                users_str = "、".join(user_names)
            else:
                # 超过最大显示数，显示前N个+总数
                displayed_names = "、".join(user_names[:self.max_users_display])
                remaining = len(user_names) - self.max_users_display
                users_str = f"{displayed_names} 等{len(user_names)}人"
            
            # 根据平台格式化
            if platform == "discord":
                parts.append(f"{emoji} {users_str} ({len(users)})")
            elif platform == "telegram":
                parts.append(f"{emoji} {users_str} ({len(users)})")
            elif platform == "feishu":
                parts.append(f"{emoji} {users_str} ({len(users)})")
            else:
                parts.append(f"{emoji} {users_str}")
        
        if not parts:
            return ""
        
        # 组合所有表情反应
        if platform == "discord":
            header = "**表情反应：**\n"
        elif platform == "telegram":
            header = "<b>表情反应：</b>\n"
        elif platform == "feishu":
            header = "**表情反应：**\n"
        else:
            header = "表情反应：\n"
        
        return header + " | ".join(parts)
    
    def format_reactions_embed(self, message_id: str) -> Optional[Dict]:
        """
        格式化为Discord Embed格式
        
        Args:
            message_id: 消息ID
            
        Returns:
            Embed字典，如果没有反应返回None
        """
        if message_id not in self.reactions:
            return None
        
        reactions_dict = self.reactions[message_id]
        
        if not reactions_dict:
            return None
        
        # 统计总反应数
        total_reactions = sum(len(users) for users in reactions_dict.values())
        
        # 构建字段列表
        fields = []
        
        for emoji, users in reactions_dict.items():
            if not users:
                continue
            
            user_names = [u['user_name'] for u in users]
            
            if len(user_names) <= 10:
                value = "\n".join(user_names)
            else:
                value = "\n".join(user_names[:10])
                value += f"\n...等{len(user_names)}人"
            
            fields.append({
                "name": f"{emoji} ({len(users)})",
                "value": value,
                "inline": True
            })
        
        return {
            "title": "表情反应",
            "description": f"共 {total_reactions} 个反应",
            "fields": fields,
            "color": 0x5865F2  # Discord蓝色
        }
    
    def get_reaction_summary(self, message_id: str) -> Dict:
        """
        获取反应摘要统计
        
        Args:
            message_id: 消息ID
            
        Returns:
            统计信息字典
        """
        if message_id not in self.reactions:
            return {
                "total_reactions": 0,
                "unique_emojis": 0,
                "unique_users": 0,
                "top_emoji": None
            }
        
        reactions_dict = self.reactions[message_id]
        
        # 统计
        total_reactions = sum(len(users) for users in reactions_dict.values())
        unique_emojis = len(reactions_dict)
        
        # 统计唯一用户
        all_user_ids = set()
        for users in reactions_dict.values():
            for user in users:
                all_user_ids.add(user['user_id'])
        unique_users = len(all_user_ids)
        
        # 找到最多的表情
        top_emoji = None
        max_count = 0
        for emoji, users in reactions_dict.items():
            if len(users) > max_count:
                max_count = len(users)
                top_emoji = emoji
        
        return {
            "total_reactions": total_reactions,
            "unique_emojis": unique_emojis,
            "unique_users": unique_users,
            "top_emoji": top_emoji,
            "top_emoji_count": max_count
        }
    
    def cleanup_old_messages(self, max_age_seconds: int = 3600):
        """
        清理旧消息的反应记录（释放内存）
        
        Args:
            max_age_seconds: 最大保留时间（秒），默认1小时
        """
        current_time = time.time()
        old_messages = []
        
        for message_id, last_time in self.last_update_time.items():
            if current_time - last_time > max_age_seconds:
                old_messages.append(message_id)
        
        for message_id in old_messages:
            if message_id in self.reactions:
                del self.reactions[message_id]
            if message_id in self.last_update_time:
                del self.last_update_time[message_id]
        
        if old_messages:
            logger.info(f"清理了 {len(old_messages)} 条旧消息的反应记录")
    
    def get_all_pending_updates(self) -> List[str]:
        """
        获取所有待发送更新的消息ID
        
        Returns:
            消息ID列表
        """
        pending = []
        current_time = time.time()
        
        for message_id, last_time in self.last_update_time.items():
            if current_time - last_time >= self.update_interval:
                pending.append(message_id)
        
        return pending
    
    def clear_message_reactions(self, message_id: str):
        """
        清除特定消息的所有反应
        
        Args:
            message_id: 消息ID
        """
        if message_id in self.reactions:
            del self.reactions[message_id]
        if message_id in self.last_update_time:
            del self.last_update_time[message_id]
        
        logger.debug(f"清除消息反应: {message_id}")


# 创建全局实例
reaction_aggregator = ReactionAggregator()
