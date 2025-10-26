"""
✅ P1-3新增：智能映射匹配算法模块
包含多种匹配策略：
1. 编辑距离算法
2. 中英翻译映射
3. 相似度计算
4. 模糊匹配
"""

from typing import List, Dict, Any, Tuple
import re


class SmartMatcher:
    """智能匹配器"""
    
    def __init__(self):
        # 中英文翻译映射表（扩展版）
        self.translation_map = {
            # 中文 -> 英文
            '公告': ['announcement', 'announcements', 'notice', 'notices', 'news'],
            '活动': ['event', 'events', 'activity', 'activities', 'campaign'],
            '讨论': ['discussion', 'discuss', 'chat', 'talk', 'conversation'],
            '通知': ['notification', 'notice', 'info', 'information', 'alert'],
            '更新': ['update', 'updates', 'changelog', 'release', 'patch'],
            '技术': ['tech', 'technology', 'technical', 'dev', 'development'],
            '支持': ['support', 'help', 'assistance'],
            '问答': ['qa', 'q&a', 'question', 'faq', 'ask'],
            '反馈': ['feedback', 'suggestion', 'opinion'],
            '闲聊': ['chat', 'offtopic', 'general', 'casual', 'random'],
            '新手': ['newbie', 'beginner', 'newcomer', 'starter'],
            '规则': ['rule', 'rules', 'regulation', 'guideline'],
            '游戏': ['game', 'games', 'gaming', 'play'],
            '音乐': ['music', 'song', 'audio'],
            '视频': ['video', 'movie', 'film'],
            '图片': ['image', 'picture', 'photo', 'gallery'],
            '资源': ['resource', 'resources', 'material'],
            '分享': ['share', 'sharing'],
            '投诉': ['complaint', 'report'],
            '建议': ['suggestion', 'advice', 'propose'],
            '管理': ['admin', 'management', 'mod', 'moderator'],
            '开发': ['dev', 'development', 'developer'],
            '测试': ['test', 'testing', 'beta'],
            '发布': ['release', 'publish', 'launch'],
            # 英文 -> 中文
            'announcement': ['公告', '通知', '声明'],
            'event': ['活动', '事件'],
            'discussion': ['讨论', '聊天'],
            'update': ['更新', '升级'],
            'tech': ['技术', '科技'],
            'support': ['支持', '帮助'],
            'chat': ['闲聊', '聊天'],
            'general': ['综合', '通用', '一般'],
            'news': ['新闻', '消息', '公告'],
            'game': ['游戏'],
            'help': ['帮助', '支持'],
            'admin': ['管理', '管理员'],
            'dev': ['开发', '开发者'],
        }
        
        # 常见缩写映射
        self.abbreviation_map = {
            'ann': 'announcement',
            'disc': 'discussion',
            'gen': 'general',
            'tech': 'technology',
            'dev': 'development',
            'mod': 'moderator',
            'qa': 'question and answer',
            'faq': 'frequently asked questions',
        }
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算两个字符串的编辑距离（Levenshtein距离）
        
        Args:
            s1: 字符串1
            s2: 字符串2
            
        Returns:
            编辑距离（需要的最少编辑操作次数）
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        计算两个字符串的相似度（0.0-1.0）
        
        Args:
            str1: 字符串1
            str2: 字符串2
            
        Returns:
            相似度分数（1.0表示完全相同）
        """
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        # 完全匹配
        if str1 == str2:
            return 1.0
        
        # 包含关系
        if str1 in str2 or str2 in str1:
            return 0.85
        
        # 编辑距离相似度
        distance = self.levenshtein_distance(str1, str2)
        max_len = max(len(str1), len(str2))
        
        if max_len == 0:
            return 0.0
        
        edit_similarity = 1.0 - (distance / max_len)
        
        # 字符集相似度
        common_chars = set(str1) & set(str2)
        total_chars = set(str1) | set(str2)
        char_similarity = len(common_chars) / len(total_chars) if total_chars else 0
        
        # 综合计算：70%编辑距离 + 30%字符相似度
        final_similarity = 0.7 * edit_similarity + 0.3 * char_similarity
        
        return round(final_similarity, 3)
    
    def check_translation_match(self, source: str, target: str) -> Tuple[bool, float]:
        """
        检查翻译匹配
        
        Args:
            source: 源字符串
            target: 目标字符串
            
        Returns:
            (是否匹配, 匹配分数)
        """
        source_lower = source.lower()
        target_lower = target.lower()
        
        for key, translations in self.translation_map.items():
            if key in source_lower:
                for trans in translations:
                    if trans in target_lower:
                        return True, 0.9
        
        return False, 0.0
    
    def normalize_channel_name(self, name: str) -> str:
        """
        标准化频道名称
        - 移除特殊字符
        - 替换缩写
        - 转小写
        
        Args:
            name: 原始频道名称
            
        Returns:
            标准化后的名称
        """
        # 移除特殊字符
        name = re.sub(r'[^\w\s-]', '', name)
        
        # 替换缩写
        name_lower = name.lower()
        for abbr, full in self.abbreviation_map.items():
            name_lower = name_lower.replace(abbr, full)
        
        return name_lower.strip()
    
    def match_channels(
        self, 
        source_channels: List[Dict[str, Any]], 
        target_channels: List[Dict[str, Any]],
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        智能匹配频道
        
        Args:
            source_channels: 源频道列表 [{'id': xxx, 'name': xxx}, ...]
            target_channels: 目标频道列表 [{'id': xxx, 'name': xxx}, ...]
            threshold: 相似度阈值（0.0-1.0）
            
        Returns:
            匹配结果列表
        """
        matches = []
        
        for source in source_channels:
            source_name = source['name']
            source_normalized = self.normalize_channel_name(source_name)
            
            best_matches = []
            
            for target in target_channels:
                target_name = target['name']
                target_normalized = self.normalize_channel_name(target_name)
                
                # 直接相似度
                direct_similarity = self.calculate_similarity(
                    source_normalized, 
                    target_normalized
                )
                
                # 翻译匹配
                is_translation, translation_score = self.check_translation_match(
                    source_name, 
                    target_name
                )
                
                # 取最高分数
                final_score = max(direct_similarity, translation_score)
                
                if final_score >= threshold:
                    best_matches.append({
                        'source_id': source['id'],
                        'source_name': source_name,
                        'target_id': target['id'],
                        'target_name': target_name,
                        'similarity': final_score,
                        'match_type': 'translation' if is_translation else 'direct',
                        'confidence': self._calculate_confidence(final_score)
                    })
            
            # 按相似度排序
            best_matches.sort(key=lambda x: x['similarity'], reverse=True)
            
            # 添加最佳匹配（可能有多个高分匹配）
            if best_matches:
                matches.extend(best_matches[:3])  # 最多返回前3个匹配
        
        return matches
    
    def _calculate_confidence(self, similarity: float) -> str:
        """
        根据相似度计算置信度等级
        
        Args:
            similarity: 相似度分数
            
        Returns:
            置信度等级：high/medium/low
        """
        if similarity >= 0.85:
            return 'high'
        elif similarity >= 0.7:
            return 'medium'
        else:
            return 'low'


# 全局实例
smart_matcher = SmartMatcher()
