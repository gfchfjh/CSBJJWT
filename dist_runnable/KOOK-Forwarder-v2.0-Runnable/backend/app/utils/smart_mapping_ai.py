"""
AI智能映射引擎 - P1-2优化
特性:
- 三重匹配算法（完全匹配+相似度+关键词）
- 历史学习（从用户的历史映射中学习模式）
- 时间衰减（最近的映射权重更高）
- 多语言支持（中英文互译）
"""
import re
import math
import time
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from collections import defaultdict
from ..database import db
from ..utils.logger import logger


class SmartMappingAI:
    """AI智能映射引擎"""
    
    def __init__(self):
        # 关键词映射表（中英文）
        self.keyword_mappings = {
            # 公告类
            '公告': ['announcement', 'notice', 'news', 'updates'],
            'announcement': ['公告', '通知', '新闻', '更新'],
            '通知': ['notice', 'notification', 'announcement'],
            'notice': ['通知', '公告'],
            
            # 聊天类
            '闲聊': ['chat', 'general', 'casual', 'off-topic'],
            'general': ['闲聊', '综合', '杂谈', '通用'],
            'chat': ['闲聊', '聊天', '对话'],
            
            # 游戏类
            '游戏': ['game', 'gaming', 'play'],
            'game': ['游戏'],
            'gaming': ['游戏', '电竞'],
            
            # 娱乐类
            '娱乐': ['entertainment', 'fun', 'meme', 'media'],
            'meme': ['表情包', '梗', '娱乐'],
            
            # 技术类
            '技术': ['tech', 'development', 'dev', 'coding'],
            'dev': ['开发', '技术', '编程'],
            'tech': ['技术', '科技'],
            
            # 帮助类
            '帮助': ['help', 'support', 'question', 'faq'],
            'help': ['帮助', '支持', '求助'],
            'support': ['支持', '帮助', '客服'],
            
            # 规则类
            '规则': ['rules', 'guidelines', 'policy'],
            'rules': ['规则', '守则', '条款'],
            
            # 活动类
            '活动': ['events', 'activities', 'event'],
            'events': ['活动', '事件'],
            
            # 媒体类
            '图片': ['images', 'pics', 'photos', 'media'],
            '视频': ['videos', 'clips', 'media'],
            '音乐': ['music', 'audio', 'songs'],
            
            # 其他常见
            '新手': ['newbie', 'beginner', 'new'],
            'welcome': ['欢迎', '新人'],
            'bot': ['机器人', 'bot'],
            'voice': ['语音', '频道'],
        }
        
        # 加载历史学习数据
        self.historical_patterns = self.load_historical_patterns()
    
    def recommend_mappings(self, 
                          kook_channels: List[Dict],
                          target_channels: List[Dict],
                          user_id: Optional[int] = None,
                          top_n: int = 3) -> Dict[str, List[Dict]]:
        """
        推荐映射关系
        
        Args:
            kook_channels: KOOK频道列表 [{'id': ..., 'name': ..., 'server_name': ...}, ...]
            target_channels: 目标平台频道列表 [{'id': ..., 'name': ..., 'platform': ...}, ...]
            user_id: 用户ID（用于个性化推荐）
            top_n: 每个KOOK频道推荐top_n个目标频道
            
        Returns:
            {
                'kook_channel_id': [
                    {'target_channel': ..., 'confidence': 0.95, 'reason': ...},
                    ...
                ]
            }
        """
        logger.info(f"🧠 开始AI智能映射推荐...")
        logger.info(f"  KOOK频道数: {len(kook_channels)}")
        logger.info(f"  目标频道数: {len(target_channels)}")
        
        recommendations = {}
        
        # 加载用户的历史映射模式
        user_patterns = {}
        if user_id:
            user_patterns = self.get_user_patterns(user_id)
        
        for kook_channel in kook_channels:
            kook_id = kook_channel['id']
            kook_name = kook_channel['name']
            kook_server = kook_channel.get('server_name', '')
            
            # 计算每个目标频道的匹配分数
            scores = []
            
            for target_channel in target_channels:
                target_id = target_channel['id']
                target_name = target_channel['name']
                target_platform = target_channel.get('platform', 'unknown')
                
                # 计算综合分数
                score, reason = self.calculate_match_score(
                    kook_name, target_name, 
                    kook_server=kook_server,
                    target_platform=target_platform,
                    user_patterns=user_patterns
                )
                
                if score > 0.3:  # 只保留分数>0.3的推荐
                    scores.append({
                        'target_channel': target_channel,
                        'confidence': round(score, 3),
                        'reason': reason,
                        'score_breakdown': {
                            'exact_match': 0,  # 会在calculate_match_score中填充
                            'similarity': 0,
                            'keyword_match': 0,
                            'historical': 0,
                        }
                    })
            
            # 按分数排序，取top_n
            scores.sort(key=lambda x: x['confidence'], reverse=True)
            recommendations[kook_id] = scores[:top_n]
            
            if scores:
                logger.info(f"  ✅ {kook_name} -> {len(scores[:top_n])} 个推荐")
            else:
                logger.info(f"  ℹ️  {kook_name} -> 无高置信度推荐")
        
        logger.info(f"🎉 推荐完成！")
        return recommendations
    
    def calculate_match_score(self, 
                             kook_name: str, 
                             target_name: str,
                             kook_server: str = "",
                             target_platform: str = "",
                             user_patterns: Dict = None) -> Tuple[float, str]:
        """
        计算匹配分数（三重算法 + 历史学习）
        
        Args:
            kook_name: KOOK频道名称
            target_name: 目标频道名称
            kook_server: KOOK服务器名称
            target_platform: 目标平台
            user_patterns: 用户的历史映射模式
            
        Returns:
            (分数, 原因说明)
        """
        kook_name_clean = self.clean_channel_name(kook_name)
        target_name_clean = self.clean_channel_name(target_name)
        
        scores = []
        reasons = []
        
        # 1. 完全匹配（权重40%）
        exact_score = 0
        if kook_name_clean == target_name_clean:
            exact_score = 1.0
            reasons.append("完全匹配")
        elif kook_name_clean.lower() == target_name_clean.lower():
            exact_score = 0.95
            reasons.append("忽略大小写匹配")
        
        # 2. 相似度匹配（权重30%）
        similarity = SequenceMatcher(None, kook_name_clean, target_name_clean).ratio()
        if similarity > 0.8:
            reasons.append(f"高相似度({int(similarity*100)}%)")
        
        # 3. 关键词匹配（权重20%）
        keyword_score = self.keyword_match_score(kook_name_clean, target_name_clean)
        if keyword_score > 0.6:
            reasons.append(f"关键词匹配")
        
        # 4. 历史学习匹配（权重10%）
        historical_score = 0
        if user_patterns:
            pattern_key = f"{kook_server}_{kook_name_clean}_{target_platform}"
            if pattern_key in user_patterns:
                pattern = user_patterns[pattern_key]
                # 时间衰减：最近的映射权重更高
                time_decay = self.calculate_time_decay(pattern['last_used'])
                historical_score = pattern['frequency'] * time_decay
                if historical_score > 0.5:
                    reasons.append(f"历史习惯({int(historical_score*100)}%)")
        
        # 加权计算最终分数
        final_score = (
            exact_score * 0.4 +
            similarity * 0.3 +
            keyword_score * 0.2 +
            historical_score * 0.1
        )
        
        # 生成原因说明
        if not reasons:
            reasons.append("低匹配度")
        
        return final_score, ", ".join(reasons)
    
    def clean_channel_name(self, name: str) -> str:
        """
        清理频道名称
        
        Args:
            name: 原始名称
            
        Returns:
            清理后的名称
        """
        # 移除特殊字符
        name = re.sub(r'[#️⃣\-_•·|【】\[\]（）()]', ' ', name)
        
        # 移除多余空格
        name = ' '.join(name.split())
        
        return name.strip()
    
    def keyword_match_score(self, kook_name: str, target_name: str) -> float:
        """
        关键词匹配分数（支持中英文互译）
        
        Args:
            kook_name: KOOK频道名称
            target_name: 目标频道名称
            
        Returns:
            匹配分数 (0.0-1.0)
        """
        kook_words = set(kook_name.lower().split())
        target_words = set(target_name.lower().split())
        
        match_count = 0
        total_checks = max(len(kook_words), len(target_words), 1)
        
        # 检查每个KOOK词
        for kook_word in kook_words:
            # 直接匹配
            if kook_word in target_words:
                match_count += 1
                continue
            
            # 关键词映射匹配
            if kook_word in self.keyword_mappings:
                translations = self.keyword_mappings[kook_word]
                if any(trans.lower() in target_words for trans in translations):
                    match_count += 0.8  # 翻译匹配权重稍低
                    continue
            
            # 部分匹配
            for target_word in target_words:
                if kook_word in target_word or target_word in kook_word:
                    match_count += 0.5
                    break
        
        return min(match_count / total_checks, 1.0)
    
    def calculate_time_decay(self, last_used_timestamp: float, half_life_days: float = 30) -> float:
        """
        计算时间衰减因子
        
        使用指数衰减模型：最近使用的映射权重更高
        
        Args:
            last_used_timestamp: 上次使用时间（Unix时间戳）
            half_life_days: 半衰期（天）
            
        Returns:
            衰减因子 (0.0-1.0)
        """
        current_time = time.time()
        days_passed = (current_time - last_used_timestamp) / 86400  # 秒转天
        
        # 指数衰减公式
        decay_factor = math.exp(-0.693 * days_passed / half_life_days)  # 0.693 ≈ ln(2)
        
        return decay_factor
    
    def get_user_patterns(self, user_id: int) -> Dict:
        """
        获取用户的历史映射模式
        
        Args:
            user_id: 用户ID
            
        Returns:
            {
                'pattern_key': {
                    'frequency': 0.8,  # 使用频率（归一化）
                    'last_used': timestamp,
                    'count': 10
                }
            }
        """
        try:
            # 从数据库查询用户的历史映射
            mappings = db.execute("""
                SELECT 
                    kook_channel_name,
                    kook_server_name,
                    target_channel_name,
                    target_platform,
                    COUNT(*) as count,
                    MAX(created_at) as last_used
                FROM channel_mappings
                WHERE user_id = ? AND status = 'active'
                GROUP BY kook_channel_name, target_channel_name
            """, (user_id,)).fetchall()
            
            if not mappings:
                return {}
            
            # 构建模式字典
            patterns = {}
            max_count = max(m['count'] for m in mappings)
            
            for mapping in mappings:
                pattern_key = f"{mapping['kook_server_name']}_{mapping['kook_channel_name']}_{mapping['target_platform']}"
                
                # 将last_used转为时间戳
                last_used = time.mktime(time.strptime(mapping['last_used'], '%Y-%m-%d %H:%M:%S'))
                
                patterns[pattern_key] = {
                    'frequency': mapping['count'] / max_count,  # 归一化频率
                    'last_used': last_used,
                    'count': mapping['count']
                }
            
            logger.info(f"  📚 加载用户历史模式: {len(patterns)} 个")
            return patterns
            
        except Exception as e:
            logger.error(f"获取用户模式失败: {e}")
            return {}
    
    def load_historical_patterns(self) -> Dict:
        """
        加载全局历史映射模式
        
        Returns:
            全局模式字典
        """
        try:
            # 查询所有用户的映射统计
            mappings = db.execute("""
                SELECT 
                    kook_channel_name,
                    target_channel_name,
                    target_platform,
                    COUNT(*) as count
                FROM channel_mappings
                WHERE status = 'active'
                GROUP BY kook_channel_name, target_channel_name
                HAVING count > 1
                ORDER BY count DESC
                LIMIT 1000
            """).fetchall()
            
            patterns = {}
            
            for mapping in mappings:
                key = f"{mapping['kook_channel_name']}_{mapping['target_channel_name']}"
                patterns[key] = {
                    'count': mapping['count'],
                    'platform': mapping['target_platform']
                }
            
            if patterns:
                logger.info(f"📚 加载全局历史模式: {len(patterns)} 个")
            
            return patterns
            
        except Exception as e:
            logger.debug(f"加载历史模式失败: {e}")
            return {}
    
    def learn_from_mapping(self, 
                          kook_channel_name: str,
                          target_channel_name: str,
                          target_platform: str,
                          user_id: Optional[int] = None):
        """
        从用户的映射中学习
        
        Args:
            kook_channel_name: KOOK频道名称
            target_channel_name: 目标频道名称
            target_platform: 目标平台
            user_id: 用户ID
        """
        # 更新历史模式
        key = f"{kook_channel_name}_{target_channel_name}"
        
        if key in self.historical_patterns:
            self.historical_patterns[key]['count'] += 1
        else:
            self.historical_patterns[key] = {
                'count': 1,
                'platform': target_platform
            }
        
        logger.info(f"📚 学习新映射: {kook_channel_name} -> {target_channel_name}")
    
    def batch_recommend(self, 
                       kook_channels: List[Dict],
                       target_channels: List[Dict],
                       confidence_threshold: float = 0.8) -> List[Dict]:
        """
        批量推荐高置信度映射
        
        Args:
            kook_channels: KOOK频道列表
            target_channels: 目标频道列表
            confidence_threshold: 置信度阈值
            
        Returns:
            [
                {
                    'kook_channel': ...,
                    'target_channel': ...,
                    'confidence': 0.95,
                    'reason': ...
                },
                ...
            ]
        """
        recommendations = self.recommend_mappings(kook_channels, target_channels)
        
        high_confidence = []
        
        for kook_id, recs in recommendations.items():
            if recs and recs[0]['confidence'] >= confidence_threshold:
                # 只取最高分的推荐
                best_rec = recs[0]
                
                kook_channel = next((c for c in kook_channels if c['id'] == kook_id), None)
                
                if kook_channel:
                    high_confidence.append({
                        'kook_channel': kook_channel,
                        'target_channel': best_rec['target_channel'],
                        'confidence': best_rec['confidence'],
                        'reason': best_rec['reason']
                    })
        
        logger.info(f"🎯 高置信度推荐: {len(high_confidence)}/{len(kook_channels)}")
        
        return high_confidence


# 全局实例
smart_mapping_ai = SmartMappingAI()


if __name__ == "__main__":
    # 测试
    kook_channels = [
        {'id': '1', 'name': '公告频道', 'server_name': '测试服务器'},
        {'id': '2', 'name': '闲聊', 'server_name': '测试服务器'},
        {'id': '3', 'name': '游戏讨论', 'server_name': '测试服务器'},
    ]
    
    target_channels = [
        {'id': 'a', 'name': 'announcements', 'platform': 'discord'},
        {'id': 'b', 'name': 'general', 'platform': 'discord'},
        {'id': 'c', 'name': 'gaming', 'platform': 'discord'},
        {'id': 'd', 'name': '通知群', 'platform': 'telegram'},
    ]
    
    recs = smart_mapping_ai.recommend_mappings(kook_channels, target_channels)
    
    print("\n推荐结果:")
    for kook_id, recommendations in recs.items():
        kook = next(c for c in kook_channels if c['id'] == kook_id)
        print(f"\n{kook['name']}:")
        for rec in recommendations:
            target = rec['target_channel']
            print(f"  -> {target['name']} ({target['platform']})")
            print(f"     置信度: {rec['confidence']:.1%}")
            print(f"     原因: {rec['reason']}")
