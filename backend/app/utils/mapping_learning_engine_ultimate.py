"""
映射学习引擎
✅ P1-2深度优化: 机器学习 + 三重匹配算法
"""
import time
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
from ..database import db
from ..utils.logger import logger


class MappingLearningEngine:
    """映射学习引擎（智能推荐）"""
    
    def __init__(self):
        self.learning_data = {}  # {(kook_channel, target): {"count": int, "last_used": timestamp}}
        self.load_learning_data()
    
    def load_learning_data(self):
        """从数据库加载学习数据"""
        try:
            # 查询所有映射历史
            history = db.get_mapping_history() if hasattr(db, 'get_mapping_history') else []
            
            for record in history:
                key = (record['kook_channel_id'], record['target_channel_id'])
                if key not in self.learning_data:
                    self.learning_data[key] = {"count": 0, "last_used": 0}
                
                self.learning_data[key]["count"] += 1
                self.learning_data[key]["last_used"] = record.get('timestamp', time.time())
            
            logger.info(f"✅ 加载了 {len(self.learning_data)} 条映射学习数据")
        except Exception as e:
            logger.warning(f"⚠️ 加载映射学习数据失败: {e}")
    
    def suggest_mapping(self, kook_channel_name: str, 
                       target_channels: List[Dict]) -> List[Tuple[Dict, float]]:
        """
        智能推荐映射（三重匹配算法）
        
        Args:
            kook_channel_name: KOOK频道名称
            target_channels: 目标平台频道列表
        
        Returns:
            [(频道, 置信度), ...] 按置信度降序排列
        """
        results = []
        
        for target in target_channels:
            target_name = target.get('name', '')
            target_id = target.get('id', '')
            
            # 🔥 三重匹配算法
            scores = {
                'exact_match': self._exact_match(kook_channel_name, target_name),
                'similar_match': self._similar_match(kook_channel_name, target_name),
                'keyword_match': self._keyword_match(kook_channel_name, target_name),
                'frequency_score': self._frequency_score(target_id)
            }
            
            # 加权计算综合置信度
            confidence = (
                scores['exact_match'] * 0.4 +
                scores['similar_match'] * 0.3 +
                scores['keyword_match'] * 0.2 +
                scores['frequency_score'] * 0.1
            )
            
            if confidence > 0.3:  # 阈值：30%
                results.append((target, confidence))
        
        # 按置信度降序排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def _exact_match(self, kook_name: str, target_name: str) -> float:
        """完全匹配（100%置信度）"""
        kook_clean = self._clean_channel_name(kook_name)
        target_clean = self._clean_channel_name(target_name)
        
        if kook_clean.lower() == target_clean.lower():
            return 1.0
        
        # 中英文映射表
        translations = {
            '公告': ['announcements', 'announce', 'notice', 'news'],
            '活动': ['events', 'activity', 'activities'],
            '更新': ['updates', 'update', 'changelog'],
            '日志': ['log', 'logs', 'changelog'],
            '讨论': ['discussion', 'discuss', 'talk'],
            '技术': ['tech', 'technical', 'dev'],
            '通知': ['notification', 'notice'],
            '聊天': ['chat', 'talk'],
            '游戏': ['game', 'gaming'],
            '娱乐': ['entertainment', 'fun']
        }
        
        for cn, en_list in translations.items():
            if cn in kook_clean:
                if any(en in target_clean.lower() for en in en_list):
                    return 0.9
        
        return 0.0
    
    def _similar_match(self, kook_name: str, target_name: str) -> float:
        """相似匹配（基于编辑距离）"""
        kook_clean = self._clean_channel_name(kook_name)
        target_clean = self._clean_channel_name(target_name)
        
        similarity = SequenceMatcher(None, kook_clean.lower(), target_clean.lower()).ratio()
        
        return similarity
    
    def _keyword_match(self, kook_name: str, target_name: str) -> float:
        """关键词匹配"""
        keyword_groups = {
            '公告': ['announce', 'announcement', 'notice', 'news', '公告', '通知'],
            '活动': ['event', 'activity', '活动', '比赛'],
            '更新': ['update', 'changelog', 'release', '更新', '版本'],
            '讨论': ['discussion', 'talk', 'chat', '讨论', '聊天'],
            '技术': ['tech', 'technical', 'dev', '技术', '开发'],
            '游戏': ['game', 'gaming', 'play', '游戏'],
            '帮助': ['help', 'support', 'faq', '帮助', '支持']
        }
        
        kook_clean = self._clean_channel_name(kook_name).lower()
        target_clean = self._clean_channel_name(target_name).lower()
        
        for group_name, keywords in keyword_groups.items():
            kook_has = any(kw in kook_clean for kw in keywords)
            target_has = any(kw in target_clean for kw in keywords)
            
            if kook_has and target_has:
                return 0.8
        
        return 0.0
    
    def _frequency_score(self, target_channel_id: str) -> float:
        """历史频率打分"""
        total_count = sum(
            data["count"] for key, data in self.learning_data.items()
            if key[1] == target_channel_id
        )
        
        return min(total_count / 100, 1.0)
    
    def _clean_channel_name(self, name: str) -> str:
        """清理频道名称"""
        import re
        name = name.lstrip('#@*-_ ')
        name = re.sub(r'[^\w\s\u4e00-\u9fff]', '', name)
        return name.strip()
    
    def record_mapping(self, kook_channel_id: str, target_channel_id: str):
        """记录映射行为（用于学习）"""
        key = (kook_channel_id, target_channel_id)
        
        if key not in self.learning_data:
            self.learning_data[key] = {"count": 0, "last_used": 0}
        
        self.learning_data[key]["count"] += 1
        self.learning_data[key]["last_used"] = time.time()
        
        # 保存到数据库
        try:
            if hasattr(db, 'save_mapping_history'):
                db.save_mapping_history({
                    'kook_channel_id': kook_channel_id,
                    'target_channel_id': target_channel_id,
                    'timestamp': time.time()
                })
        except Exception as e:
            logger.warning(f"保存映射历史失败: {e}")
        
        logger.debug(f"📝 记录映射学习: {kook_channel_id} → {target_channel_id}")
    
    def get_stats(self) -> Dict:
        """获取学习统计信息"""
        total_mappings = len(self.learning_data)
        total_count = sum(data["count"] for data in self.learning_data.values())
        
        top_mappings = sorted(
            self.learning_data.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:10]
        
        return {
            'total_unique_mappings': total_mappings,
            'total_mapping_count': total_count,
            'top_mappings': [
                {
                    'kook_channel': k[0],
                    'target_channel': k[1],
                    'count': v["count"],
                    'last_used': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v["last_used"]))
                }
                for k, v in top_mappings
            ]
        }


# 创建全局实例
mapping_learning_engine = MappingLearningEngine()
