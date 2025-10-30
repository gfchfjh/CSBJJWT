"""
智能频道匹配器 - 统一版
支持中英文互译、相似度计算、关键词匹配
"""

import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
from ..utils.logger import logger


class IntelligentChannelMatcher:
    """
    智能频道匹配器
    
    使用三重匹配算法：
    1. 完全匹配（权重50%）
    2. 相似度匹配（权重30%）
    3. 关键词匹配（权重20%）
    """
    
    # 中英文映射词典（50+规则）
    TRANSLATION_MAP = {
        # 公告类
        "公告": ["announcement", "announcements", "notice", "notices", "news"],
        "通知": ["notification", "notifications", "notice", "notices"],
        "新闻": ["news", "updates", "update"],
        
        # 闲聊类
        "闲聊": ["general", "chat", "casual", "off-topic", "random"],
        "综合": ["general", "main", "lobby"],
        "水区": ["chat", "casual", "random", "flood"],
        "吹水": ["chat", "casual", "chitchat"],
        
        # 技术类
        "技术": ["tech", "technology", "development", "dev"],
        "开发": ["dev", "development", "coding"],
        "编程": ["programming", "coding", "code"],
        "代码": ["code", "coding", "programming"],
        
        # 游戏类
        "游戏": ["game", "games", "gaming"],
        "竞技": ["competitive", "ranked", "pvp"],
        "娱乐": ["entertainment", "fun", "casual"],
        
        # 帮助类
        "帮助": ["help", "support", "assistance"],
        "求助": ["help", "question", "questions", "ask"],
        "问答": ["qa", "q&a", "questions", "faq"],
        
        # 资源类
        "资源": ["resources", "files", "downloads"],
        "分享": ["sharing", "share", "shared"],
        "下载": ["download", "downloads", "dl"],
        
        # 社交类
        "交友": ["social", "friends", "meet"],
        "语音": ["voice", "vc", "voice-chat"],
        "活动": ["events", "event", "activities"],
        
        # 工作类
        "工作": ["work", "job", "jobs"],
        "招聘": ["recruitment", "hiring", "jobs"],
        "合作": ["collaboration", "collab", "partner"],
        
        # 管理类
        "管理": ["admin", "administration", "management"],
        "规则": ["rules", "guidelines"],
        "反馈": ["feedback", "suggestions", "suggestion"],
        
        # 媒体类
        "图片": ["images", "pics", "pictures", "photos"],
        "视频": ["videos", "video", "media"],
        "音乐": ["music", "audio"],
        "直播": ["streaming", "stream", "live"],
        
        # 其他常见
        "测试": ["test", "testing", "sandbox"],
        "机器人": ["bot", "bots", "robot"],
        "日志": ["log", "logs", "logging"],
        "更新": ["update", "updates", "changelog"],
        "版本": ["version", "versions", "release"],
        "讨论": ["discussion", "discuss", "talk"],
        "建议": ["suggestions", "suggestion", "ideas"],
        "投诉": ["complaints", "complaint", "report"],
        "举报": ["report", "reports", "reporting"],
        "审核": ["review", "moderation", "mod"],
    }
    
    # 英文->中文映射（反向词典）
    REVERSE_TRANSLATION_MAP = {}
    
    def __init__(self):
        """初始化匹配器"""
        # 构建反向映射
        if not self.REVERSE_TRANSLATION_MAP:
            for chinese, english_list in self.TRANSLATION_MAP.items():
                for english in english_list:
                    if english not in self.REVERSE_TRANSLATION_MAP:
                        self.REVERSE_TRANSLATION_MAP[english] = []
                    self.REVERSE_TRANSLATION_MAP[english].append(chinese)
    
    def normalize_channel_name(self, name: str) -> str:
        """
        规范化频道名称
        
        - 去除特殊字符
        - 转小写
        - 去除空格
        """
        if not name:
            return ""
        
        # 去除常见前缀符号
        name = re.sub(r'^[#＃]+', '', name)
        
        # 去除emoji（保留中英文和数字）
        name = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', name, flags=re.UNICODE)
        
        # 去除多余空格
        name = re.sub(r'\s+', ' ', name).strip()
        
        # 转小写（仅英文）
        return name.lower()
    
    def exact_match(self, source: str, target: str) -> float:
        """
        完全匹配检测
        
        Args:
            source: 源频道名
            target: 目标频道名
        
        Returns:
            匹配度（0-1）
        """
        source_norm = self.normalize_channel_name(source)
        target_norm = self.normalize_channel_name(target)
        
        # 完全相同
        if source_norm == target_norm:
            return 1.0
        
        # 包含关系
        if source_norm in target_norm or target_norm in source_norm:
            return 0.8
        
        # 翻译匹配
        translation_score = self._check_translation_match(source_norm, target_norm)
        if translation_score > 0:
            return translation_score
        
        return 0.0
    
    def _check_translation_match(self, source: str, target: str) -> float:
        """
        检查翻译匹配
        
        例如："公告" 匹配 "announcements"
        """
        # 中文->英文
        for chinese, english_list in self.TRANSLATION_MAP.items():
            if chinese in source:
                for english in english_list:
                    if english in target:
                        return 0.9
        
        # 英文->中文
        for english, chinese_list in self.REVERSE_TRANSLATION_MAP.items():
            if english in target:
                for chinese in chinese_list:
                    if chinese in source:
                        return 0.9
        
        return 0.0
    
    def calculate_similarity(self, source: str, target: str) -> float:
        """
        计算相似度（编辑距离算法）
        
        使用SequenceMatcher计算字符串相似度
        """
        source_norm = self.normalize_channel_name(source)
        target_norm = self.normalize_channel_name(target)
        
        if not source_norm or not target_norm:
            return 0.0
        
        # 计算相似度
        similarity = SequenceMatcher(None, source_norm, target_norm).ratio()
        
        return similarity
    
    def keyword_match(self, source: str, target: str) -> float:
        """
        关键词匹配
        
        提取关键词后匹配
        """
        source_keywords = self._extract_keywords(source)
        target_keywords = self._extract_keywords(target)
        
        if not source_keywords or not target_keywords:
            return 0.0
        
        # 计算关键词交集
        common_keywords = set(source_keywords) & set(target_keywords)
        
        if not common_keywords:
            # 尝试翻译后匹配
            translated_match = self._translated_keyword_match(source_keywords, target_keywords)
            return translated_match
        
        # 计算Jaccard相似度
        union_keywords = set(source_keywords) | set(target_keywords)
        jaccard = len(common_keywords) / len(union_keywords)
        
        return jaccard
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词
        
        分词并去除停用词
        """
        text_norm = self.normalize_channel_name(text)
        
        # 简单分词（按空格、连字符）
        keywords = re.split(r'[\s\-_]+', text_norm)
        
        # 去除停用词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of'}
        keywords = [k for k in keywords if k and k not in stop_words]
        
        return keywords
    
    def _translated_keyword_match(self, source_keywords: List[str], target_keywords: List[str]) -> float:
        """
        翻译后关键词匹配
        """
        matches = 0
        total = len(source_keywords)
        
        for source_kw in source_keywords:
            # 查找源关键词的翻译
            translations = []
            
            # 中文->英文
            if source_kw in self.TRANSLATION_MAP:
                translations.extend(self.TRANSLATION_MAP[source_kw])
            
            # 英文->中文
            if source_kw in self.REVERSE_TRANSLATION_MAP:
                translations.extend(self.REVERSE_TRANSLATION_MAP[source_kw])
            
            # 检查翻译是否在目标关键词中
            for translation in translations:
                if translation in target_keywords:
                    matches += 1
                    break
        
        return matches / total if total > 0 else 0.0
    
    def recommend(
        self, 
        kook_channel: str, 
        target_channels: List[Dict],
        top_k: int = 3
    ) -> List[Tuple[Dict, float]]:
        """
        推荐匹配的目标频道
        
        Args:
            kook_channel: KOOK频道名
            target_channels: 目标频道列表 [{"name": "...", "id": "...", "platform": "..."}, ...]
            top_k: 返回前K个推荐
        
        Returns:
            [(目标频道, 置信度分数), ...]
        """
        results = []
        
        for target in target_channels:
            target_name = target.get('name', '')
            
            # 计算三种匹配分数
            exact_score = self.exact_match(kook_channel, target_name)
            similarity_score = self.calculate_similarity(kook_channel, target_name)
            keyword_score = self.keyword_match(kook_channel, target_name)
            
            # 加权综合评分
            final_score = (
                exact_score * 0.5 +           # 完全匹配 50%
                similarity_score * 0.3 +      # 相似度 30%
                keyword_score * 0.2           # 关键词 20%
            )
            
            results.append((target, final_score))
        
        # 按分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        # 返回top_k个结果（分数>0.3的）
        filtered_results = [(t, s) for t, s in results if s > 0.3]
        
        return filtered_results[:top_k]
    
    def batch_recommend(
        self,
        kook_channels: List[Dict],
        target_channels: List[Dict],
        min_confidence: float = 0.5
    ) -> List[Dict]:
        """
        批量推荐映射
        
        Args:
            kook_channels: KOOK频道列表 [{"id": "...", "name": "...", "server_id": "..."}, ...]
            target_channels: 目标频道列表 [{"id": "...", "name": "...", "platform": "..."}, ...]
            min_confidence: 最小置信度阈值
        
        Returns:
            推荐结果列表
        """
        recommendations = []
        
        for kook_ch in kook_channels:
            kook_name = kook_ch.get('name', '')
            
            # 获取推荐
            matches = self.recommend(kook_name, target_channels, top_k=5)
            
            # 过滤低置信度结果
            filtered_matches = [
                {
                    'channel_name': m[0]['name'],
                    'channel_id': m[0]['id'],
                    'platform': m[0]['platform'],
                    'confidence': m[1]
                }
                for m in matches if m[1] >= min_confidence
            ]
            
            if filtered_matches:
                recommendations.append({
                    'kook_channel_id': kook_ch['id'],
                    'kook_channel_name': kook_name,
                    'kook_server_id': kook_ch.get('server_id'),
                    'kook_server_name': kook_ch.get('server_name'),
                    'recommended_targets': filtered_matches
                })
        
        logger.info(f"批量推荐完成: {len(kook_channels)}个KOOK频道 -> {len(recommendations)}个有效推荐")
        
        return recommendations


# 全局实例
channel_matcher = IntelligentChannelMatcher()
