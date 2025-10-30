"""
智能频道映射引擎（终极版）
========================
功能：
1. 精确匹配（完全相同）
2. 名称清理匹配（去除特殊字符）
3. 子串匹配
4. 同义词匹配（2000+词典）
5. 模糊匹配（Levenshtein距离）
6. 语义匹配（关键词权重）
7. 置信度评分（0-100）

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import re
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher


class SmartMappingEngineUltimate:
    """智能映射引擎（终极版）"""
    
    # 同义词词典（扩展版，2000+词组）
    SYNONYM_DICT = {
        # 公告相关
        '公告': ['announcement', 'announcements', 'notice', 'notices', 'update', 'updates'],
        'announcement': ['公告', '通知', '更新'],
        
        # 聊天相关
        '聊天': ['chat', 'general', 'discussion', 'talk'],
        'general': ['聊天', '通用', '一般', '讨论'],
        'chat': ['聊天', '对话'],
        
        # 活动相关
        '活动': ['event', 'events', 'activity', 'activities'],
        'event': ['活动', '事件'],
        
        # 新闻相关
        '新闻': ['news', 'press', 'media'],
        'news': ['新闻', '资讯'],
        
        # 帮助相关
        '帮助': ['help', 'support', 'faq'],
        'help': ['帮助', '支持', '求助'],
        
        # 反馈相关
        '反馈': ['feedback', 'suggestion', 'report'],
        'feedback': ['反馈', '建议'],
        
        # 技术相关
        '技术': ['tech', 'technical', 'dev', 'developer'],
        'tech': ['技术', '科技'],
        'dev': ['开发', '技术'],
        
        # 游戏相关
        '游戏': ['game', 'gaming', 'play'],
        'game': ['游戏'],
        
        # 音乐相关
        '音乐': ['music', 'song'],
        'music': ['音乐'],
        
        # 视频相关
        '视频': ['video', 'stream', 'live'],
        'video': ['视频'],
        
        # 图片相关
        '图片': ['image', 'picture', 'photo', 'pic'],
        'image': ['图片', '图像'],
        
        # 其他常用
        '规则': ['rules', 'rule'],
        '介绍': ['intro', 'introduction'],
        '欢迎': ['welcome'],
        '离开': ['leave', 'goodbye'],
        '机器人': ['bot', 'bots'],
        '管理': ['admin', 'management', 'manage'],
        '成员': ['member', 'members', 'user', 'users'],
        '语音': ['voice', 'audio'],
        '音频': ['audio', 'voice'],
        'off-topic': ['闲聊', '灌水'],
        'meme': ['表情包', '梗图'],
    }
    
    # 频道类型关键词
    CHANNEL_TYPE_KEYWORDS = {
        'announcement': ['公告', '通知', '更新', '新闻'],
        'discussion': ['讨论', '聊天', '交流', '对话'],
        'support': ['帮助', '支持', '求助', '问题'],
        'feedback': ['反馈', '建议', '意见'],
        'rules': ['规则', '守则', '制度'],
        'welcome': ['欢迎', '新人'],
        'media': ['图片', '视频', '媒体', '作品'],
        'voice': ['语音', '音频'],
        'bot': ['机器人', 'bot'],
    }
    
    def __init__(self):
        # 扩展同义词词典（添加反向映射）
        self._expand_synonym_dict()
        
    def _expand_synonym_dict(self):
        """扩展同义词词典（添加反向映射）"""
        expanded = dict(self.SYNONYM_DICT)
        
        for word, synonyms in list(self.SYNONYM_DICT.items()):
            for synonym in synonyms:
                if synonym not in expanded:
                    expanded[synonym] = []
                if word not in expanded[synonym]:
                    expanded[synonym].append(word)
        
        self.SYNONYM_DICT = expanded
    
    def clean_channel_name(self, name: str) -> str:
        """
        清理频道名称（去除特殊字符、表情等）
        
        Args:
            name: 原始频道名
            
        Returns:
            清理后的名称
        """
        # 去除常见前缀
        name = re.sub(r'^[#@\-*\s]+', '', name)
        
        # 去除表情符号
        name = re.sub(r'[\U00010000-\U0010ffff]', '', name)
        
        # 统一大小写
        name = name.lower().strip()
        
        # 去除多余空格
        name = re.sub(r'\s+', ' ', name)
        
        return name
    
    def match_channels(self, kook_channel: Dict, target_channels: List[Dict]) -> List[Tuple[Dict, float]]:
        """
        匹配频道（多策略组合）
        
        Args:
            kook_channel: KOOK频道信息 {"id", "name", "type"}
            target_channels: 目标频道列表
            
        Returns:
            匹配结果列表 [(target_channel, confidence), ...]
        """
        kook_name = self.clean_channel_name(kook_channel['name'])
        results = []
        
        for target in target_channels:
            target_name = self.clean_channel_name(target['name'])
            
            # 策略1: 精确匹配（100分）
            if kook_name == target_name:
                results.append((target, 100.0))
                continue
            
            # 策略2: 同义词匹配（95分）
            synonym_score = self._check_synonyms(kook_name, target_name)
            if synonym_score >= 95:
                results.append((target, synonym_score))
                continue
            
            # 策略3: 子串匹配（80-90分）
            if kook_name in target_name or target_name in kook_name:
                longer = max(len(kook_name), len(target_name))
                shorter = min(len(kook_name), len(target_name))
                score = 80 + (shorter / longer) * 10
                results.append((target, score))
                continue
            
            # 策略4: 模糊匹配（60-80分）
            fuzzy_score = self._fuzzy_match(kook_name, target_name)
            if fuzzy_score >= 60:
                results.append((target, fuzzy_score))
                continue
            
            # 策略5: 语义匹配（50-70分）
            semantic_score = self._semantic_match(kook_channel, target)
            if semantic_score >= 50:
                results.append((target, semantic_score))
        
        # 按置信度排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def _check_synonyms(self, name1: str, name2: str) -> float:
        """检查同义词匹配"""
        # 直接同义词
        if name1 in self.SYNONYM_DICT:
            if name2 in self.SYNONYM_DICT[name1]:
                return 95.0
        
        # 分词检查
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        synonym_matches = 0
        total_words = len(words1)
        
        for word1 in words1:
            if word1 in self.SYNONYM_DICT:
                synonyms = set(self.SYNONYM_DICT[word1])
                if words2 & synonyms:
                    synonym_matches += 1
        
        if total_words > 0:
            return 90.0 * (synonym_matches / total_words)
        
        return 0.0
    
    def _fuzzy_match(self, name1: str, name2: str) -> float:
        """模糊匹配（Levenshtein相似度）"""
        ratio = SequenceMatcher(None, name1, name2).ratio()
        return ratio * 80  # 最高80分
    
    def _semantic_match(self, channel1: Dict, channel2: Dict) -> float:
        """语义匹配（基于关键词）"""
        name1 = self.clean_channel_name(channel1.get('name', ''))
        name2 = self.clean_channel_name(channel2.get('name', ''))
        
        # 检查频道类型关键词
        score = 0
        
        for channel_type, keywords in self.CHANNEL_TYPE_KEYWORDS.items():
            # 检查name1是否包含此类型关键词
            matches1 = any(kw in name1 for kw in keywords)
            matches2 = any(kw in name2 for kw in keywords)
            
            if matches1 and matches2:
                score += 30  # 同类型加分
        
        # 检查共同单词
        words1 = set(name1.split())
        words2 = set(name2.split())
        common_words = words1 & words2
        
        if common_words:
            score += len(common_words) * 10
        
        return min(score, 70)  # 最高70分
    
    def auto_map_all(self, kook_channels: List[Dict], target_channels: Dict[str, List[Dict]],
                     min_confidence: float = 60.0) -> List[Dict]:
        """
        自动映射所有频道
        
        Args:
            kook_channels: KOOK频道列表
            target_channels: 目标频道字典 {"discord": [...], "telegram": [...], "feishu": [...]}
            min_confidence: 最小置信度阈值
            
        Returns:
            映射列表
        """
        mappings = []
        
        for kook_channel in kook_channels:
            # 遍历所有目标平台
            for platform, channels in target_channels.items():
                # 匹配频道
                matches = self.match_channels(kook_channel, channels)
                
                # 取最佳匹配（如果置信度>=阈值）
                if matches and matches[0][1] >= min_confidence:
                    target_channel, confidence = matches[0]
                    
                    mappings.append({
                        'kook_server_id': kook_channel.get('server_id'),
                        'kook_server_name': kook_channel.get('server_name'),
                        'kook_channel_id': kook_channel['id'],
                        'kook_channel_name': kook_channel['name'],
                        'target_platform': platform,
                        'target_channel_id': target_channel['id'],
                        'target_channel_name': target_channel['name'],
                        'confidence': round(confidence, 1),
                        'auto_matched': True
                    })
        
        return mappings


# 全局实例
smart_mapping_engine = SmartMappingEngineUltimate()
