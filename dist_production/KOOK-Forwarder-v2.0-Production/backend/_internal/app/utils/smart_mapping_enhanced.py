"""
智能映射引擎（增强版）
P1-2: 优化智能匹配算法

功能：
1. 模糊匹配（fuzzywuzzy）
2. 同义词词典
3. 多语言支持（中英文）
4. 置信度评分
"""
from typing import List, Dict, Any, Optional
from ..utils.logger import logger

# 尝试导入 fuzzywuzzy
try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
    logger.info("✅ fuzzywuzzy 可用，使用增强智能匹配")
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    logger.warning("⚠️ fuzzywuzzy 未安装，使用基础匹配（pip install fuzzywuzzy python-Levenshtein 以获得更好效果）")


# 同义词词典（中英文双向）
SYNONYMS = {
    # 中文 -> 英文
    "公告": ["announcement", "announcements", "news", "notice", "通知"],
    "活动": ["event", "events", "activity", "activities"],
    "更新": ["update", "updates", "changelog", "release", "releases"],
    "讨论": ["discussion", "chat", "talk", "general", "聊天"],
    "帮助": ["help", "support", "question", "ask", "questions"],
    "技术": ["tech", "technical", "developer", "dev", "开发"],
    "闲聊": ["off-topic", "random", "chat", "casual"],
    "反馈": ["feedback", "suggestion", "suggestions"],
    "投诉": ["complaint", "report"],
    "规则": ["rules", "rule", "guidelines"],
    "介绍": ["introduction", "intro", "welcome"],
    "资源": ["resources", "resource", "links"],
    "媒体": ["media", "gallery", "images"],
    "视频": ["video", "videos", "stream"],
    "音乐": ["music", "audio"],
    "游戏": ["game", "games", "gaming"],
    
    # 英文 -> 中文
    "announcement": ["公告", "通知", "新闻"],
    "event": ["活动", "事件"],
    "update": ["更新", "升级"],
    "discussion": ["讨论", "聊天"],
    "help": ["帮助", "支持"],
    "tech": ["技术", "开发"],
    "general": ["综合", "通用", "一般"],
}


class SmartMappingEngine:
    """智能映射引擎（增强版）"""
    
    def __init__(self):
        self.synonyms = SYNONYMS
        self.use_fuzzy = FUZZYWUZZY_AVAILABLE
    
    def match_channel(self, kook_name: str, target_channels: List[Dict]) -> List[Dict]:
        """
        智能匹配频道
        
        Args:
            kook_name: KOOK 频道名称
            target_channels: 目标频道列表 [{"id": "xxx", "name": "xxx"}]
            
        Returns:
            匹配结果列表（按分数降序）
            [{"channel": {...}, "score": 95, "confidence": "high", "reason": "同义词匹配"}]
        """
        if not target_channels:
            return []
        
        results = []
        
        for channel in target_channels:
            score = self._calculate_score(kook_name, channel['name'])
            
            if score >= 60:  # 阈值：60 分以上认为匹配
                results.append({
                    'channel': channel,
                    'score': score,
                    'confidence': self._get_confidence_level(score),
                    'reason': self._get_match_reason(score)
                })
        
        # 按分数降序排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"智能匹配 '{kook_name}': 找到 {len(results)} 个候选频道")
        if results:
            logger.debug(f"最佳匹配: {results[0]['channel']['name']} (分数: {results[0]['score']})")
        
        return results
    
    def _calculate_score(self, kook_name: str, target_name: str) -> int:
        """
        计算匹配分数
        
        Args:
            kook_name: KOOK 频道名
            target_name: 目标频道名
            
        Returns:
            匹配分数（0-100）
        """
        kook_lower = kook_name.lower().strip()
        target_lower = target_name.lower().strip()
        
        # 1. 精确匹配（100 分）
        if kook_lower == target_lower:
            return 100
        
        # 2. 去除符号后精确匹配（98 分）
        kook_clean = self._clean_channel_name(kook_lower)
        target_clean = self._clean_channel_name(target_lower)
        if kook_clean == target_clean:
            return 98
        
        # 3. 包含关系（90 分）
        if kook_lower in target_lower or target_lower in kook_lower:
            return 90
        
        # 4. 同义词匹配（85-95 分）
        synonym_score = self._check_synonyms(kook_lower, target_lower)
        if synonym_score > 0:
            return synonym_score
        
        # 5. 模糊匹配（60-89 分）
        if self.use_fuzzy:
            fuzzy_score = fuzz.ratio(kook_clean, target_clean)
            return fuzzy_score
        else:
            # 简单相似度计算（备选方案）
            return self._simple_similarity(kook_clean, target_clean)
    
    def _clean_channel_name(self, name: str) -> str:
        """清理频道名（移除符号）"""
        # 移除常见前缀符号
        name = name.lstrip('#*-_•·~`')
        
        # 移除空格和下划线
        name = name.replace(' ', '').replace('_', '').replace('-', '')
        
        return name
    
    def _check_synonyms(self, kook_name: str, target_name: str) -> int:
        """检查同义词匹配"""
        # 中文 -> 英文
        for cn, en_list in self.synonyms.items():
            if cn in kook_name:
                for en in en_list:
                    if en in target_name:
                        # 完全匹配同义词（95 分）
                        if en == target_name:
                            return 95
                        # 包含同义词（85 分）
                        return 85
        
        # 英文 -> 中文
        for en, cn_list in self.synonyms.items():
            if en in kook_name:
                for cn in cn_list:
                    if cn in target_name:
                        if cn == target_name:
                            return 95
                        return 85
        
        return 0
    
    def _simple_similarity(self, str1: str, str2: str) -> int:
        """简单相似度计算（不依赖 fuzzywuzzy）"""
        # 使用 Jaccard 相似度
        set1 = set(str1)
        set2 = set(str2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0
        
        similarity = (intersection / union) * 100
        return int(similarity)
    
    def _get_confidence_level(self, score: int) -> str:
        """获取置信度等级"""
        if score >= 90:
            return "high"  # 高置信度（建议自动应用）
        elif score >= 75:
            return "medium"  # 中等置信度（建议用户确认）
        else:
            return "low"  # 低置信度（仅作为候选）
    
    def _get_match_reason(self, score: int) -> str:
        """获取匹配原因"""
        if score == 100:
            return "精确匹配"
        elif score >= 98:
            return "清理符号后精确匹配"
        elif score >= 90:
            return "同义词匹配或包含关系"
        elif score >= 85:
            return "同义词匹配"
        elif score >= 75:
            return "高度相似"
        else:
            return "部分相似"
    
    def batch_match(self, kook_channels: List[Dict], 
                   target_channels: List[Dict],
                   auto_apply_threshold: int = 90) -> Dict[str, Any]:
        """
        批量匹配（整个服务器）
        
        Args:
            kook_channels: KOOK 频道列表
            target_channels: 目标频道列表
            auto_apply_threshold: 自动应用阈值（默认 90 分以上）
            
        Returns:
            匹配结果
        """
        results = {
            'total': len(kook_channels),
            'matched': 0,
            'auto_applied': 0,
            'needs_review': 0,
            'unmatched': 0,
            'mappings': []
        }
        
        for kook_channel in kook_channels:
            matches = self.match_channel(kook_channel['name'], target_channels)
            
            if not matches:
                # 未匹配
                results['unmatched'] += 1
                results['mappings'].append({
                    'kook_channel': kook_channel,
                    'target_channel': None,
                    'score': 0,
                    'confidence': 'none'
                })
            else:
                # 找到匹配
                best_match = matches[0]
                results['matched'] += 1
                
                if best_match['score'] >= auto_apply_threshold:
                    # 高置信度，可自动应用
                    results['auto_applied'] += 1
                    results['mappings'].append({
                        'kook_channel': kook_channel,
                        'target_channel': best_match['channel'],
                        'score': best_match['score'],
                        'confidence': best_match['confidence'],
                        'auto_applied': True,
                        'reason': best_match['reason']
                    })
                else:
                    # 中低置信度，需要用户确认
                    results['needs_review'] += 1
                    results['mappings'].append({
                        'kook_channel': kook_channel,
                        'target_channel': best_match['channel'],
                        'score': best_match['score'],
                        'confidence': best_match['confidence'],
                        'auto_applied': False,
                        'reason': best_match['reason'],
                        'alternatives': matches[1:4]  # 提供 3 个备选
                    })
        
        logger.info(f"批量匹配完成: 总计 {results['total']}, "
                   f"匹配 {results['matched']}, "
                   f"自动应用 {results['auto_applied']}, "
                   f"需审核 {results['needs_review']}, "
                   f"未匹配 {results['unmatched']}")
        
        return results


# 全局实例
smart_mapping_engine = SmartMappingEngine()
