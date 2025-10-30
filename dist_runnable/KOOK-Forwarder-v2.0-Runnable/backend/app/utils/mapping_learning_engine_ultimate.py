"""
🧠 P1-2优化: AI映射学习引擎（终极版）

功能：
1. 三重匹配算法（完全+相似+关键词）
2. 中英文翻译表（10+常用词）
3. 历史频率学习（带时间衰减）
4. 持续优化推荐准确度

作者: KOOK Forwarder Team
版本: 11.0.0
日期: 2025-10-28
"""
import difflib
import re
import time
import math
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from ..utils.logger import logger
from ..database import db


class MappingLearningEngine:
    """AI映射学习引擎（v2.0增强版）"""
    
    def __init__(self):
        # 中英文翻译表
        self.translation_table = {
            '公告': ['announcement', 'announce', 'notice', 'news'],
            '活动': ['event', 'activity', 'campaign'],
            '更新': ['update', 'changelog', 'release', 'patch'],
            '技术': ['tech', 'technical', 'dev', 'development'],
            '讨论': ['discuss', 'discussion', 'talk', 'chat'],
            '帮助': ['help', 'support', 'faq', 'question'],
            '反馈': ['feedback', 'suggestion', 'report'],
            '闲聊': ['general', 'off-topic', 'chat', 'random'],
            '规则': ['rule', 'guideline', 'policy'],
            '资源': ['resource', 'link', 'material'],
            '教程': ['tutorial', 'guide', 'howto'],
            '测试': ['test', 'testing', 'beta'],
            '开发': ['dev', 'development', 'coding'],
            '设计': ['design', 'art', 'creative'],
            '音乐': ['music', 'audio', 'sound'],
        }
        
        # 反向翻译表（英文→中文）
        self.reverse_translation = {}
        for cn, en_list in self.translation_table.items():
            for en in en_list:
                self.reverse_translation[en] = cn
        
        # 映射历史记录 {(kook_channel_id, target_channel_id): count}
        self.mapping_history = defaultdict(int)
        
        # 映射时间戳 {(kook_channel_id, target_channel_id): timestamp}
        self.mapping_timestamps = {}
        
        # 从数据库加载历史
        self.load_history()
        
        logger.info(f"✅ AI映射学习引擎已初始化（翻译表:{len(self.translation_table)}词）")
    
    def load_history(self):
        """从数据库加载历史映射记录"""
        try:
            history = db.get_mapping_learning_history()
            
            for record in history:
                key = (record['kook_channel_id'], record['target_channel_id'])
                self.mapping_history[key] = record['use_count']
                self.mapping_timestamps[key] = record['last_used_timestamp']
            
            if history:
                logger.info(f"✅ 已加载{len(history)}条映射历史记录")
        except Exception as e:
            logger.warning(f"⚠️  加载映射历史失败: {str(e)}")
    
    def recommend_mappings(
        self, 
        kook_channel: Dict, 
        target_channels: List[Dict]
    ) -> List[Tuple[Dict, float, str]]:
        """
        推荐映射（三重算法 + 历史频率）
        
        Args:
            kook_channel: KOOK频道信息 {'id', 'name', 'type'}
            target_channels: 目标频道列表 [{'id', 'name', 'platform'}, ...]
            
        Returns:
            推荐列表 [(target_channel, confidence, reason), ...]
            按置信度降序排列
        """
        kook_name = kook_channel['name'].lower()
        kook_id = kook_channel['id']
        
        recommendations = []
        
        logger.debug(f"🔍 为KOOK频道'{kook_channel['name']}'推荐映射...")
        
        for target in target_channels:
            target_name = target['name'].lower()
            target_id = target['id']
            
            # 1. 完全匹配（40%权重）
            exact_match = self._exact_match_score(kook_name, target_name)
            
            # 2. 相似匹配（30%权重）
            similarity = self._similarity_score(kook_name, target_name)
            
            # 3. 关键词匹配（20%权重）
            keyword_match = self._keyword_match_score(kook_name, target_name)
            
            # 4. 历史频率（10%权重）
            history_score = self._history_score(kook_id, target_id)
            
            # 综合置信度
            confidence = (
                exact_match * 0.4 +
                similarity * 0.3 +
                keyword_match * 0.2 +
                history_score * 0.1
            )
            
            # 生成推荐原因
            reason = self._generate_reason(
                exact_match, similarity, keyword_match, history_score
            )
            
            recommendations.append((target, confidence, reason))
            
            logger.debug(
                f"  {target['platform']} - {target['name']}: "
                f"置信度={confidence:.2f} ({reason})"
            )
        
        # 按置信度排序
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(
            f"✅ 生成{len(recommendations)}个推荐，"
            f"最高置信度={recommendations[0][1]:.2f if recommendations else 0}"
        )
        
        return recommendations
    
    def _exact_match_score(self, name1: str, name2: str) -> float:
        """
        完全匹配评分（考虑翻译）
        
        Returns:
            1.0 = 完全匹配
            0.8 = 翻译匹配
            0.0 = 不匹配
        """
        # 去除特殊字符
        clean1 = re.sub(r'[#\-_\s]+', '', name1)
        clean2 = re.sub(r'[#\-_\s]+', '', name2)
        
        # 直接匹配
        if clean1 == clean2:
            return 1.0
        
        # 检查翻译匹配 - 中文 → 英文
        for cn_word, en_words in self.translation_table.items():
            if cn_word in name1:
                for en_word in en_words:
                    if en_word in name2:
                        return 0.8
        
        # 检查翻译匹配 - 英文 → 中文
        for en_word, cn_word in self.reverse_translation.items():
            if en_word in name1 and cn_word in name2:
                return 0.8
        
        return 0.0
    
    def _similarity_score(self, name1: str, name2: str) -> float:
        """
        相似度评分（编辑距离）
        
        使用SequenceMatcher计算字符串相似度
        
        Returns:
            0.0 - 1.0
        """
        # 去除特殊字符
        clean1 = re.sub(r'[#\-_\s]+', '', name1)
        clean2 = re.sub(r'[#\-_\s]+', '', name2)
        
        # 使用difflib计算相似度
        similarity = difflib.SequenceMatcher(None, clean1, clean2).ratio()
        
        return similarity
    
    def _keyword_match_score(self, name1: str, name2: str) -> float:
        """
        关键词匹配评分
        
        提取关键词，计算匹配比例
        
        Returns:
            0.0 - 1.0
        """
        # 提取中文关键词
        cn_keywords1 = re.findall(r'[\u4e00-\u9fa5]+', name1)
        cn_keywords2 = re.findall(r'[\u4e00-\u9fa5]+', name2)
        
        # 提取英文关键词
        en_keywords1 = re.findall(r'[a-z]+', name1)
        en_keywords2 = re.findall(r'[a-z]+', name2)
        
        # 合并
        keywords1 = set(cn_keywords1 + en_keywords1)
        keywords2 = set(cn_keywords2 + en_keywords2)
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # 计算交集占比（Jaccard相似度）
        intersection = keywords1 & keywords2
        union = keywords1 | keywords2
        
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # 考虑翻译匹配
        translated_matches = 0
        for kw1 in keywords1:
            # 检查中文→英文翻译
            if kw1 in self.translation_table:
                en_words = self.translation_table[kw1]
                if any(en in keywords2 for en in en_words):
                    translated_matches += 1
            
            # 检查英文→中文翻译
            if kw1 in self.reverse_translation:
                cn_word = self.reverse_translation[kw1]
                if cn_word in keywords2:
                    translated_matches += 1
        
        # 翻译匹配加分（每个匹配+0.2，最多+0.5）
        translation_bonus = min(0.5, translated_matches * 0.2)
        
        return min(1.0, jaccard + translation_bonus)
    
    def _history_score(self, kook_channel_id: str, target_channel_id: str) -> float:
        """
        历史频率评分（带时间衰减）
        
        公式: score = (use_count / max_count) * time_decay
        
        时间衰减: decay = e^(-λt)，其中t为天数，λ=0.01
        
        Returns:
            0.0 - 1.0
        """
        key = (kook_channel_id, target_channel_id)
        
        use_count = self.mapping_history.get(key, 0)
        
        if use_count == 0:
            return 0.0
        
        # 找到最大使用次数（归一化）
        max_count = max(self.mapping_history.values()) if self.mapping_history else 1
        
        normalized_count = use_count / max_count
        
        # 时间衰减
        if key in self.mapping_timestamps:
            last_used = self.mapping_timestamps[key]
            days_ago = (time.time() - last_used) / 86400
            
            # 指数衰减: e^(-0.01 * days)
            # 100天后衰减到37%，200天后衰减到14%
            time_decay = math.exp(-0.01 * days_ago)
        else:
            time_decay = 1.0
        
        return normalized_count * time_decay
    
    def _generate_reason(
        self, 
        exact: float, 
        similarity: float, 
        keyword: float, 
        history: float
    ) -> str:
        """生成推荐原因"""
        reasons = []
        
        if exact >= 0.8:
            reasons.append("完全匹配" if exact == 1.0 else "翻译匹配")
        
        if similarity >= 0.7:
            reasons.append(f"名称相似度{similarity*100:.0f}%")
        
        if keyword >= 0.5:
            reasons.append("关键词匹配")
        
        if history >= 0.5:
            reasons.append("历史记录")
        
        if not reasons:
            # 找出最高的分数
            scores = {
                '名称相似': similarity,
                '关键词': keyword,
                '历史': history
            }
            best = max(scores.items(), key=lambda x: x[1])
            reasons.append(f"{best[0]}({best[1]*100:.0f}%)")
        
        return " | ".join(reasons)
    
    def record_mapping(
        self, 
        kook_channel_id: str, 
        target_channel_id: str
    ):
        """记录用户的映射选择（用于学习）"""
        key = (kook_channel_id, target_channel_id)
        
        # 增加使用次数
        self.mapping_history[key] += 1
        
        # 更新时间戳
        self.mapping_timestamps[key] = time.time()
        
        # 保存到数据库
        try:
            db.save_mapping_learning_record(
                kook_channel_id=kook_channel_id,
                target_channel_id=target_channel_id,
                use_count=self.mapping_history[key],
                last_used_timestamp=self.mapping_timestamps[key]
            )
            
            logger.debug(f"✅ 已记录映射学习: {kook_channel_id} -> {target_channel_id}")
        except Exception as e:
            logger.error(f"❌ 保存映射学习记录失败: {str(e)}")
    
    def get_stats(self) -> Dict:
        """获取学习引擎统计信息"""
        if not self.mapping_history:
            most_used = None
        else:
            most_used_key = max(self.mapping_history.items(), key=lambda x: x[1])
            most_used = {
                'kook_channel_id': most_used_key[0][0],
                'target_channel_id': most_used_key[0][1],
                'use_count': most_used_key[1]
            }
        
        return {
            'total_mappings_learned': len(self.mapping_history),
            'total_uses': sum(self.mapping_history.values()),
            'most_used_mapping': most_used,
            'translation_table_size': len(self.translation_table),
            'reverse_translation_size': len(self.reverse_translation)
        }
    
    def export_translation_table(self) -> Dict:
        """导出翻译表（供用户自定义）"""
        return self.translation_table.copy()
    
    def import_translation_table(self, table: Dict):
        """导入自定义翻译表"""
        self.translation_table.update(table)
        
        # 更新反向表
        for cn, en_list in table.items():
            for en in en_list:
                self.reverse_translation[en] = cn
        
        logger.info(f"✅ 已导入自定义翻译表，当前共{len(self.translation_table)}词")


# 创建全局实例
mapping_learning_engine = MappingLearningEngine()
