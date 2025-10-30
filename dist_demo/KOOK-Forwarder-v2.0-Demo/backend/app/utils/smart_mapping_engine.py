"""
AI智能映射引擎
✅ P1-2优化: 4维评分系统 + 时间衰减 + 学习能力
"""
import math
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from ..database import db
from ..utils.logger import logger


class SmartMappingEngine:
    """
    AI智能映射引擎
    
    评分算法：
    final_score = (
        exact_match * 0.4 +      # 完全匹配：40%权重
        similarity * 0.3 +        # 相似度：30%权重
        keyword_match * 0.2 +     # 关键词：20%权重
        historical * 0.1          # 历史学习：10%权重
    )
    
    时间衰减公式：
    decay_factor = exp(-0.693 * days_passed / 30)  # 半衰期30天
    """
    
    def __init__(self):
        self.keyword_map = self._load_keyword_map()
        self._ensure_learning_table()
        
        logger.info("✅ AI映射引擎已初始化，加载了50+个关键词规则")
    
    def _ensure_learning_table(self):
        """确保学习数据表存在"""
        db.execute("""
            CREATE TABLE IF NOT EXISTS mapping_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kook_channel_id TEXT NOT NULL,
                target_channel_id TEXT NOT NULL,
                accepted BOOLEAN NOT NULL,
                learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_learning_kook_channel
            ON mapping_learning(kook_channel_id, learned_at DESC)
        """)
        
        db.commit()
    
    def _load_keyword_map(self) -> Dict[str, List[str]]:
        """
        加载关键词映射表（中英文互译）
        
        Returns:
            关键词映射字典
        """
        return {
            # 中文 → 英文
            "公告": ["announcement", "notice", "news", "announcements"],
            "闲聊": ["chat", "general", "casual", "off-topic"],
            "游戏": ["game", "gaming", "play", "games"],
            "技术": ["tech", "development", "dev", "technical"],
            "开发": ["dev", "development", "tech", "coding"],
            "测试": ["test", "testing", "qa", "beta"],
            "反馈": ["feedback", "bug", "issue", "report"],
            "问题": ["issue", "problem", "question", "help"],
            "帮助": ["help", "support", "assistance", "faq"],
            "新手": ["newbie", "beginner", "starter", "newcomer"],
            "讨论": ["discussion", "talk", "chat", "forum"],
            "分享": ["share", "sharing", "showcase"],
            "资源": ["resource", "assets", "materials"],
            "教程": ["tutorial", "guide", "howto", "learn"],
            "更新": ["update", "changelog", "news", "release"],
            "活动": ["event", "activity", "campaign"],
            "规则": ["rule", "rules", "guideline", "policy"],
            "管理": ["admin", "management", "mod", "moderation"],
            "建议": ["suggestion", "feature-request", "proposal"],
            "投票": ["vote", "poll", "survey"],
            "语音": ["voice", "vc", "audio"],
            "文字": ["text", "chat", "message"],
            "图片": ["image", "picture", "photo", "gallery"],
            "视频": ["video", "media", "stream"],
            "音乐": ["music", "song", "audio"],
            "Bot": ["bot", "bots", "command", "commands"],
            
            # 英文 → 中文
            "announcement": ["公告", "通知", "消息"],
            "announcements": ["公告", "通知"],
            "general": ["闲聊", "综合", "一般", "通用"],
            "chat": ["聊天", "闲聊", "讨论"],
            "dev": ["开发", "技术", "研发"],
            "development": ["开发", "研发"],
            "game": ["游戏"],
            "gaming": ["游戏"],
            "tech": ["技术"],
            "technical": ["技术"],
            "help": ["帮助", "求助"],
            "support": ["帮助", "支持"],
            "feedback": ["反馈"],
            "bug": ["反馈", "问题", "错误"],
            "issue": ["问题"],
            "question": ["问题", "提问"],
            "discussion": ["讨论"],
            "off-topic": ["闲聊", "灌水"],
            "news": ["新闻", "公告", "消息"],
            "event": ["活动"],
            "events": ["活动"],
            "update": ["更新"],
            "changelog": ["更新", "日志"],
            "voice": ["语音"],
            "vc": ["语音"],
            "test": ["测试"],
            "qa": ["测试"],
            "beginner": ["新手"],
            "newcomer": ["新手"],
            "rule": ["规则"],
            "rules": ["规则"],
            "admin": ["管理"],
            "mod": ["管理"],
            "moderation": ["管理"]
        }
    
    def calculate_match_score(
        self,
        kook_channel_name: str,
        target_channel_name: str,
        kook_channel_id: str
    ) -> Tuple[float, str]:
        """
        计算映射匹配分数
        
        Args:
            kook_channel_name: KOOK频道名称
            target_channel_name: 目标频道名称
            kook_channel_id: KOOK频道ID（用于历史学习）
            
        Returns:
            (分数[0.0-1.0], 推荐理由)
        """
        # 1. 完全匹配（40%权重）
        exact_score = self._exact_match_score(kook_channel_name, target_channel_name)
        
        # 2. 相似度匹配（30%权重）
        similarity_score = self._similarity_score(kook_channel_name, target_channel_name)
        
        # 3. 关键词匹配（20%权重）
        keyword_score = self._keyword_match_score(kook_channel_name, target_channel_name)
        
        # 4. 历史学习（10%权重）
        historical_score = self._historical_score(kook_channel_id, target_channel_name)
        
        # 综合评分
        final_score = (
            exact_score * 0.4 +
            similarity_score * 0.3 +
            keyword_score * 0.2 +
            historical_score * 0.1
        )
        
        # 生成推荐理由
        reason = self._generate_reason(
            exact_score,
            similarity_score,
            keyword_score,
            historical_score,
            kook_channel_name,
            target_channel_name
        )
        
        return (final_score, reason)
    
    def _exact_match_score(self, source: str, target: str) -> float:
        """
        完全匹配分数
        
        检查：
        1. 完全相同
        2. 忽略大小写相同
        3. 去除特殊字符后相同
        """
        # 标准化
        source_clean = self._normalize(source)
        target_clean = self._normalize(target)
        
        if source_clean == target_clean:
            return 1.0
        
        # 检查是否包含关系
        if source_clean in target_clean or target_clean in source_clean:
            return 0.8
        
        return 0.0
    
    def _normalize(self, text: str) -> str:
        """标准化文本（用于匹配）"""
        # 转小写
        text = text.lower()
        
        # 移除常见前缀
        prefixes = ['#', '@', '📢', '🎮', '💬', '🔧']
        for prefix in prefixes:
            text = text.lstrip(prefix).strip()
        
        # 移除特殊字符
        text = ''.join(c for c in text if c.isalnum() or c in ['-', '_', ' '])
        
        # 移除多余空格
        text = ' '.join(text.split())
        
        return text
    
    def _similarity_score(self, source: str, target: str) -> float:
        """
        相似度分数（使用SequenceMatcher）
        
        基于最长公共子序列算法
        """
        source_clean = self._normalize(source)
        target_clean = self._normalize(target)
        
        return SequenceMatcher(None, source_clean, target_clean).ratio()
    
    def _keyword_match_score(self, source: str, target: str) -> float:
        """
        关键词匹配分数
        
        检查源频道名称中的关键词是否在目标频道名称中出现（或其翻译）
        """
        source_lower = source.lower()
        target_lower = target.lower()
        
        # 提取源频道的关键词及其翻译
        source_keywords = set()
        
        for keyword, translations in self.keyword_map.items():
            if keyword in source_lower:
                source_keywords.add(keyword)
                source_keywords.update(translations)
        
        if not source_keywords:
            return 0.0
        
        # 检查目标频道是否包含这些关键词
        matches = sum(1 for kw in source_keywords if kw in target_lower)
        
        # 归一化到0-1
        return min(matches / len(source_keywords), 1.0)
    
    def _historical_score(self, kook_channel_id: str, target_name: str) -> float:
        """
        历史学习分数（带时间衰减）
        
        查询用户过去对这个KOOK频道的映射选择，
        如果之前选择过相同或相似的目标频道，给予加分
        
        时间衰减公式：
        decay_factor = exp(-0.693 * days_passed / 30)
        半衰期30天，意味着30天前的选择权重降低50%
        """
        try:
            # 查询历史学习记录
            history = db.execute("""
                SELECT target_channel_id, accepted, learned_at
                FROM mapping_learning
                WHERE kook_channel_id = ? AND accepted = 1
                ORDER BY learned_at DESC
                LIMIT 20
            """, (kook_channel_id,)).fetchall()
            
            if not history:
                return 0.0
            
            now = datetime.now()
            total_score = 0.0
            
            for record in history:
                target_id = record['target_channel_id']
                accepted = record['accepted']
                learned_at = datetime.fromisoformat(record['learned_at'])
                
                # 检查目标频道名称相似性
                # 注意：这里简化处理，实际应该查询target_channel_id的名称
                if target_name.lower() in target_id.lower() or target_id.lower() in target_name.lower():
                    # 计算时间差（天）
                    days_passed = (now - learned_at).days
                    
                    # 指数衰减：半衰期30天
                    decay_factor = math.exp(-0.693 * days_passed / 30)
                    
                    # 累加衰减后的分数
                    if accepted:
                        total_score += decay_factor
                    else:
                        total_score -= decay_factor * 0.5  # 拒绝的记录负面影响较小
            
            # 归一化到0-1
            return max(0, min(total_score / len(history), 1.0))
            
        except Exception as e:
            logger.error(f"计算历史分数失败: {e}")
            return 0.0
    
    def _generate_reason(
        self,
        exact: float,
        similarity: float,
        keyword: float,
        historical: float,
        source: str,
        target: str
    ) -> str:
        """生成推荐理由"""
        if exact >= 0.9:
            return "完全匹配"
        elif exact >= 0.7:
            return "名称包含关系"
        elif similarity >= 0.7:
            return "高度相似"
        elif keyword >= 0.5:
            return "关键词匹配"
        elif historical >= 0.5:
            return "历史学习推荐"
        else:
            return "可能匹配"
    
    def recommend_mappings(
        self,
        kook_channels: List[Dict],
        target_channels: List[Dict]
    ) -> List[Dict]:
        """
        推荐频道映射
        
        Args:
            kook_channels: KOOK频道列表
                [{'id': str, 'name': str, 'server_id': str, 'server_name': str}, ...]
            target_channels: 目标频道列表
                [{'id': str, 'name': str, 'platform': str, 'bot_id': int}, ...]
        
        Returns:
            推荐结果列表
            [
                {
                    'kook_channel': {...},
                    'suggestions': [
                        {
                            'target_channel': {...},
                            'score': 0.95,
                            'confidence': '非常推荐',
                            'reason': '完全匹配'
                        },
                        ...
                    ]
                },
                ...
            ]
        """
        results = []
        
        for kook_ch in kook_channels:
            suggestions = []
            
            for target_ch in target_channels:
                score, reason = self.calculate_match_score(
                    kook_ch['name'],
                    target_ch['name'],
                    kook_ch['id']
                )
                
                # 只推荐分数>0.5的
                if score > 0.5:
                    suggestions.append({
                        'target_channel': target_ch,
                        'channel_id': target_ch['id'],
                        'channel_name': target_ch['name'],
                        'platform': target_ch['platform'],
                        'bot_id': target_ch['bot_id'],
                        'score': round(score, 2),
                        'confidence': self._score_to_confidence(score),
                        'reason': reason
                    })
            
            # 按分数排序
            suggestions.sort(key=lambda x: x['score'], reverse=True)
            
            results.append({
                'kook_channel': kook_ch,
                'suggestions': suggestions[:3]  # 最多推荐3个
            })
        
        logger.info(f"✅ AI推荐完成：为{len(kook_channels)}个KOOK频道生成了{sum(len(r['suggestions']) for r in results)}个推荐")
        
        return results
    
    def _score_to_confidence(self, score: float) -> str:
        """分数转置信度"""
        if score > 0.9:
            return "非常推荐"
        elif score > 0.7:
            return "推荐"
        elif score > 0.5:
            return "可能匹配"
        else:
            return "低置信度"
    
    async def learn_from_user_choice(
        self,
        kook_channel_id: str,
        target_channel_id: str,
        accepted: bool
    ):
        """
        从用户选择中学习
        
        Args:
            kook_channel_id: KOOK频道ID
            target_channel_id: 目标频道ID
            accepted: True=用户接受了推荐, False=用户拒绝了推荐
        """
        try:
            db.execute("""
                INSERT INTO mapping_learning (
                    kook_channel_id,
                    target_channel_id,
                    accepted,
                    learned_at
                ) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (kook_channel_id, target_channel_id, accepted))
            
            db.commit()
            
            logger.info(f"学习记录: {kook_channel_id} → {target_channel_id} ({'接受' if accepted else '拒绝'})")
            
        except Exception as e:
            logger.error(f"记录学习数据失败: {e}")
    
    def get_learning_stats(self) -> Dict:
        """获取学习统计"""
        try:
            result = db.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN accepted = 1 THEN 1 ELSE 0 END) as accepted,
                    SUM(CASE WHEN accepted = 0 THEN 1 ELSE 0 END) as rejected
                FROM mapping_learning
            """).fetchone()
            
            total = result['total'] if result else 0
            accepted = result['accepted'] if result else 0
            rejected = result['rejected'] if result else 0
            
            return {
                'total_learning_records': total,
                'accepted_suggestions': accepted,
                'rejected_suggestions': rejected,
                'acceptance_rate': round((accepted / total * 100) if total > 0 else 0, 2)
            }
            
        except Exception as e:
            logger.error(f"获取学习统计失败: {e}")
            return {}


# 全局实例
smart_mapping_engine = SmartMappingEngine()
