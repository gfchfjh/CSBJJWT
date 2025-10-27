"""
智能映射引擎终极版
✅ P0-8优化: 增强的频道匹配算法
"""
import difflib
import re
from typing import List, Dict, Tuple, Optional
from ..utils.logger import logger


class SmartMappingEngine:
    """智能映射引擎"""
    
    # 中英文映射规则
    MAPPING_RULES = {
        # 公告相关
        '公告': ['announcement', 'announcements', 'notice', 'notices', 'news'],
        '通知': ['notification', 'notifications', 'notice', 'notices'],
        '新闻': ['news', 'update', 'updates'],
        
        # 活动相关
        '活动': ['event', 'events', 'activity', 'activities'],
        '比赛': ['contest', 'competition', 'tournament'],
        '竞赛': ['competition', 'contest', 'challenge'],
        
        # 更新相关
        '更新': ['update', 'updates', 'changelog', 'release'],
        '日志': ['log', 'logs', 'changelog'],
        '版本': ['version', 'release'],
        
        # 讨论相关
        '讨论': ['discussion', 'chat', 'talk', 'general'],
        '聊天': ['chat', 'chatting', 'general'],
        '交流': ['communication', 'chat', 'discussion'],
        
        # 技术相关
        '技术': ['tech', 'technology', 'dev', 'development'],
        '开发': ['dev', 'development', 'developer'],
        '编程': ['programming', 'coding', 'dev'],
        
        # 帮助相关
        '帮助': ['help', 'support', 'assistance'],
        '支持': ['support', 'help', 'assist'],
        '问题': ['question', 'questions', 'qa', 'faq'],
        
        # 游戏相关
        '游戏': ['game', 'games', 'gaming'],
        '战队': ['team', 'squad', 'guild'],
        '公会': ['guild', 'clan', 'alliance'],
        
        # 其他常见
        '介绍': ['introduction', 'intro', 'about'],
        '规则': ['rule', 'rules', 'regulation'],
        '资源': ['resource', 'resources', 'materials'],
        '分享': ['share', 'sharing', 'showcase'],
        '反馈': ['feedback', 'suggestion', 'suggestions'],
        '建议': ['suggestion', 'suggestions', 'feedback'],
        '测试': ['test', 'testing', 'beta'],
        '官方': ['official', 'staff', 'admin']
    }
    
    # 常见频道名称变体
    CHANNEL_VARIANTS = {
        'general': ['通用', '综合', '大厅'],
        'off-topic': ['闲聊', '水区', '灌水'],
        'memes': ['表情包', '梗图', '搞笑'],
        'voice': ['语音', '聊天室'],
        'music': ['音乐', '点歌'],
        'bot-commands': ['机器人', 'bot', '命令']
    }
    
    def __init__(self):
        # 合并双向规则
        self.cn_to_en = self.MAPPING_RULES.copy()
        self.en_to_cn = {}
        
        for cn, en_list in self.MAPPING_RULES.items():
            for en in en_list:
                if en not in self.en_to_cn:
                    self.en_to_cn[en] = []
                self.en_to_cn[en].append(cn)
    
    async def auto_match(self,
                         kook_channels: List[Dict],
                         target_channels: List[Dict],
                         platform: str) -> List[Dict]:
        """
        自动匹配频道
        
        Args:
            kook_channels: KOOK频道列表
                [{'id': '123', 'name': '公告频道', 'server_name': '游戏服务器'}, ...]
            target_channels: 目标平台频道列表
                [{'id': '456', 'name': 'announcements', 'bot_id': 1, 'bot_name': 'Bot1'}, ...]
            platform: 目标平台 (discord/telegram/feishu)
        
        Returns:
            匹配结果列表
            [{
                'kook_channel_id': '123',
                'kook_channel': '公告频道',
                'kook_server': '游戏服务器',
                'target': '456',  # target_channel_id
                'confidence': 0.95,
                'match_reason': '规则匹配: 公告 → announcement'
            }, ...]
        """
        logger.info(f"开始智能映射: {len(kook_channels)} KOOK频道 → {len(target_channels)} {platform}频道")
        
        matches = []
        
        for kook_ch in kook_channels:
            best_match = self.find_best_match(
                kook_ch['name'],
                target_channels,
                platform
            )
            
            if best_match and best_match['score'] > 0.6:  # 相似度阈值60%
                matches.append({
                    'kook_channel_id': kook_ch['id'],
                    'kook_channel': kook_ch['name'],
                    'kook_server': kook_ch.get('server_name', ''),
                    'target': best_match['channel']['id'],
                    'target_name': best_match['channel']['name'],
                    'bot_id': best_match['channel']['bot_id'],
                    'bot_name': best_match['channel']['bot_name'],
                    'confidence': best_match['score'],
                    'match_reason': best_match['reason']
                })
                
                logger.info(f"✓ 匹配成功: {kook_ch['name']} → {best_match['channel']['name']} ({best_match['score']:.0%})")
            else:
                logger.warning(f"✗ 未找到匹配: {kook_ch['name']}")
        
        logger.info(f"映射完成: 成功匹配 {len(matches)}/{len(kook_channels)} 个频道")
        
        return matches
    
    def find_best_match(self,
                        kook_name: str,
                        target_channels: List[Dict],
                        platform: str) -> Optional[Dict]:
        """
        找到最佳匹配
        
        Returns:
            {
                'channel': {...},  # 目标频道信息
                'score': 0.95,  # 相似度得分
                'reason': '规则匹配'  # 匹配理由
            }
        """
        scores = []
        
        for target_ch in target_channels:
            score, reason = self.calculate_similarity(
                kook_name,
                target_ch['name'],
                platform
            )
            
            if score > 0:
                scores.append({
                    'channel': target_ch,
                    'score': score,
                    'reason': reason
                })
        
        if not scores:
            return None
        
        # 返回得分最高的
        return max(scores, key=lambda x: x['score'])
    
    def calculate_similarity(self,
                             kook_name: str,
                             target_name: str,
                             platform: str) -> Tuple[float, str]:
        """
        计算相似度
        
        Returns:
            (相似度得分 0-1, 匹配理由)
        """
        kook_name_lower = kook_name.lower()
        target_name_lower = target_name.lower()
        
        # 1. 完全匹配（100%）
        if kook_name_lower == target_name_lower:
            return 1.0, "完全匹配"
        
        # 2. 去除特殊字符后完全匹配（98%）
        kook_clean = self._clean_channel_name(kook_name_lower)
        target_clean = self._clean_channel_name(target_name_lower)
        
        if kook_clean == target_clean:
            return 0.98, "去除特殊字符后完全匹配"
        
        # 3. 中英文规则匹配（95%）
        rule_score, rule_reason = self._check_rule_match(kook_name_lower, target_name_lower)
        if rule_score > 0:
            return rule_score, rule_reason
        
        # 4. 包含关系（90%）
        if kook_clean in target_clean or target_clean in kook_clean:
            return 0.90, "名称包含"
        
        # 5. 常见变体匹配（85%）
        variant_score, variant_reason = self._check_variant_match(kook_name_lower, target_name_lower)
        if variant_score > 0:
            return variant_score, variant_reason
        
        # 6. 字符串相似度（基于Levenshtein距离）
        similarity = difflib.SequenceMatcher(None, kook_clean, target_clean).ratio()
        
        if similarity >= 0.8:
            return similarity, f"字符串相似度: {int(similarity * 100)}%"
        elif similarity >= 0.6:
            return similarity, f"部分相似: {int(similarity * 100)}%"
        
        # 7. 模糊匹配（使用分词）
        fuzzy_score = self._fuzzy_match(kook_name_lower, target_name_lower)
        if fuzzy_score >= 0.6:
            return fuzzy_score, f"模糊匹配: {int(fuzzy_score * 100)}%"
        
        return 0, "无匹配"
    
    def _check_rule_match(self, kook_name: str, target_name: str) -> Tuple[float, str]:
        """检查规则匹配"""
        # 中文 → 英文
        for cn_word, en_words in self.cn_to_en.items():
            if cn_word in kook_name:
                for en_word in en_words:
                    if en_word in target_name:
                        return 0.95, f"规则匹配: {cn_word} → {en_word}"
        
        # 英文 → 中文
        for en_word, cn_words in self.en_to_cn.items():
            if en_word in kook_name:
                for cn_word in cn_words:
                    if cn_word in target_name:
                        return 0.95, f"规则匹配: {en_word} → {cn_word}"
        
        return 0, ""
    
    def _check_variant_match(self, kook_name: str, target_name: str) -> Tuple[float, str]:
        """检查常见变体匹配"""
        for en, cn_list in self.CHANNEL_VARIANTS.items():
            if en in target_name:
                for cn in cn_list:
                    if cn in kook_name:
                        return 0.85, f"变体匹配: {cn} ↔ {en}"
        
        return 0, ""
    
    def _fuzzy_match(self, kook_name: str, target_name: str) -> float:
        """模糊匹配（基于分词）"""
        # 分词
        kook_words = set(self._tokenize(kook_name))
        target_words = set(self._tokenize(target_name))
        
        if not kook_words or not target_words:
            return 0
        
        # 计算Jaccard相似度
        intersection = len(kook_words & target_words)
        union = len(kook_words | target_words)
        
        return intersection / union if union > 0 else 0
    
    def _clean_channel_name(self, name: str) -> str:
        """清理频道名称（去除特殊字符）"""
        # 去除常见前缀和后缀
        name = re.sub(r'^(频道|channel|ch)[-_\s]*', '', name)
        name = re.sub(r'[-_\s]*(频道|channel|ch)$', '', name)
        
        # 去除特殊字符
        name = re.sub(r'[#\-_\s]+', '', name)
        
        return name.strip()
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 按非字母数字字符分割
        tokens = re.split(r'[^a-zA-Z0-9\u4e00-\u9fff]+', text)
        # 过滤空字符串
        return [t for t in tokens if t]
    
    def suggest_mapping(self, unmatched_channels: List[Dict], all_targets: List[Dict]) -> List[Dict]:
        """
        为未匹配的频道建议可能的目标
        
        Returns:
            [{
                'kook_channel': {...},
                'suggestions': [
                    {'target': {...}, 'confidence': 0.5, 'reason': '...'},
                    ...
                ]
            }, ...]
        """
        suggestions = []
        
        for kook_ch in unmatched_channels:
            channel_suggestions = []
            
            for target_ch in all_targets:
                score, reason = self.calculate_similarity(
                    kook_ch['name'],
                    target_ch['name'],
                    target_ch.get('platform', 'unknown')
                )
                
                if score > 0.3:  # 降低阈值，显示更多建议
                    channel_suggestions.append({
                        'target': target_ch,
                        'confidence': score,
                        'reason': reason
                    })
            
            # 按得分排序
            channel_suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            
            # 只保留前3个建议
            suggestions.append({
                'kook_channel': kook_ch,
                'suggestions': channel_suggestions[:3]
            })
        
        return suggestions


# 全局实例
smart_mapping_engine = SmartMappingEngine()
