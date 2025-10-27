"""
✅ P0-5优化: 智能映射规则增强
扩展到60+中英文映射规则，提升自动匹配准确率
"""
from typing import Dict, List, Tuple
from ..utils.logger import logger


class SmartMappingRulesEnhanced:
    """增强版智能映射规则（60+规则）"""
    
    def __init__(self):
        self.channel_translations = self._init_channel_translations()
        self.fuzzy_patterns = self._init_fuzzy_patterns()
        logger.info(f"✅ 智能映射规则已初始化：{len(self.channel_translations)}个翻译规则，{len(self.fuzzy_patterns)}个模糊匹配模式")
    
    def _init_channel_translations(self) -> Dict[str, List[str]]:
        """
        初始化频道名称中英文翻译映射（60+规则）
        
        Returns:
            翻译映射字典
        """
        return {
            # 1-10: 公告和通知类
            "公告": ["announcements", "announcement", "news", "notice", "notices"],
            "通知": ["notifications", "notification", "alerts", "alert"],
            "新闻": ["news", "press", "media"],
            "更新": ["updates", "update", "changelog", "changes", "releases", "release"],
            "说明": ["readme", "info", "information", "about"],
            "声明": ["statement", "declaration", "notice"],
            "须知": ["notes", "tips", "important"],
            "必读": ["must-read", "important", "required"],
            "重要": ["important", "critical", "urgent"],
            "置顶": ["pinned", "sticky", "top"],
            
            # 11-20: 活动和社交类
            "活动": ["events", "event", "activities", "activity"],
            "赛事": ["tournament", "competition", "contest", "matches"],
            "比赛": ["match", "game", "competition"],
            "抽奖": ["lottery", "raffle", "giveaway", "draw"],
            "福利": ["benefits", "welfare", "rewards", "perks"],
            "奖励": ["rewards", "reward", "prizes", "prize"],
            "签到": ["check-in", "daily", "attendance"],
            "打卡": ["check-in", "clock-in", "sign-in"],
            "投票": ["poll", "vote", "voting"],
            "问卷": ["survey", "questionnaire", "poll"],
            
            # 21-30: 技术和开发类
            "技术": ["tech", "technical", "technology", "development", "dev"],
            "开发": ["dev", "development", "coding", "programming"],
            "代码": ["code", "coding", "programming", "source"],
            "编程": ["programming", "coding", "development"],
            "测试": ["test", "testing", "qa", "quality"],
            "bug": ["bugs", "bug-report", "issues", "issue"],
            "反馈": ["feedback", "suggestions", "reports"],
            "建议": ["suggestions", "ideas", "proposals"],
            "讨论": ["discussion", "discuss", "talk", "chat"],
            "分享": ["share", "sharing", "showcase"],
            
            # 31-40: 帮助和支持类
            "帮助": ["help", "support", "assistance"],
            "支持": ["support", "help", "service"],
            "客服": ["customer-service", "support", "help"],
            "教程": ["tutorial", "tutorials", "guide", "guides", "howto"],
            "指南": ["guide", "manual", "handbook"],
            "文档": ["docs", "documentation", "wiki"],
            "FAQ": ["faq", "questions", "q-a", "qa"],
            "问答": ["q-a", "qa", "questions", "ask"],
            "新手": ["newbie", "beginner", "starter", "newcomer"],
            "入门": ["getting-started", "intro", "introduction"],
            
            # 41-50: 游戏相关类
            "游戏": ["game", "gaming", "play"],
            "攻略": ["guide", "strategy", "walkthrough", "tips"],
            "组队": ["team", "party", "group", "squad"],
            "公会": ["guild", "clan", "alliance"],
            "交易": ["trade", "trading", "market", "exchange"],
            "拍卖": ["auction", "marketplace"],
            "副本": ["dungeon", "instance", "raid"],
            "PVP": ["pvp", "arena", "battle", "combat"],
            "PVE": ["pve", "quest", "mission"],
            "任务": ["quest", "mission", "task", "quests"],
            
            # 51-60: 其他常用类
            "闲聊": ["chat", "general", "off-topic", "casual"],
            "水区": ["off-topic", "random", "general", "lounge"],
            "吐槽": ["complaints", "rant", "feedback"],
            "日常": ["daily", "everyday", "casual"],
            "音乐": ["music", "songs", "playlist"],
            "视频": ["video", "videos", "media"],
            "图片": ["images", "pics", "pictures", "gallery"],
            "资源": ["resources", "materials", "files"],
            "下载": ["downloads", "download", "files"],
            "链接": ["links", "urls", "bookmarks"],
            
            # 61-70: 额外补充
            "官方": ["official", "admin", "staff"],
            "管理": ["admin", "management", "moderator", "mod"],
            "规则": ["rules", "regulations", "guidelines"],
            "介绍": ["introduction", "intro", "about"],
            "展示": ["showcase", "gallery", "display"],
            "作品": ["works", "creations", "projects"],
            "交流": ["communication", "exchange", "interact"],
            "合作": ["cooperation", "collaboration", "partner"],
            "招募": ["recruitment", "hiring", "recruit"],
            "建设": ["construction", "building", "development"]
        }
    
    def _init_fuzzy_patterns(self) -> List[Tuple[str, str]]:
        """
        初始化模糊匹配模式
        
        Returns:
            模糊匹配模式列表 [(中文模式, 英文模式), ...]
        """
        return [
            # 匹配带数字的频道
            (r"(\d+)号?公告", r"announcement-\1"),
            (r"(\d+)号?活动", r"event-\1"),
            (r"第(\d+)区", r"zone-\1"),
            
            # 匹配带前缀的频道
            (r"官方-(.+)", r"official-\1"),
            (r"玩家-(.+)", r"player-\1"),
            
            # 匹配带后缀的频道
            (r"(.+)-公告", r"\1-announcements"),
            (r"(.+)-讨论", r"\1-discussion"),
        ]
    
    def find_best_match(self, kook_channel_name: str, 
                        target_channels: List[Dict]) -> List[Tuple[Dict, float]]:
        """
        为KOOK频道找到最佳匹配的目标频道
        
        Args:
            kook_channel_name: KOOK频道名称
            target_channels: 目标频道列表
            
        Returns:
            匹配结果列表 [(频道, 置信度分数), ...]，按分数降序排列
        """
        results = []
        
        for target_channel in target_channels:
            target_name = target_channel.get('name', '').lower()
            kook_name = kook_channel_name.lower()
            
            # 计算相似度分数
            score = self._calculate_similarity(kook_name, target_name)
            
            if score > 0.3:  # 置信度阈值30%
                results.append((target_channel, score))
        
        # 按分数降序排列
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def _calculate_similarity(self, kook_name: str, target_name: str) -> float:
        """
        计算两个频道名称的相似度
        
        Args:
            kook_name: KOOK频道名（小写）
            target_name: 目标频道名（小写）
            
        Returns:
            相似度分数 0.0-1.0
        """
        # 1. 完全匹配（去除特殊字符后）
        clean_kook = self._clean_name(kook_name)
        clean_target = self._clean_name(target_name)
        
        if clean_kook == clean_target:
            return 1.0
        
        # 2. 翻译匹配
        for chinese, english_list in self.channel_translations.items():
            chinese_lower = chinese.lower()
            
            # KOOK是中文，目标是英文
            if chinese_lower in kook_name:
                for english in english_list:
                    if english.lower() in target_name:
                        return 0.9  # 高置信度
            
            # KOOK是英文，目标是中文
            if chinese_lower in target_name:
                for english in english_list:
                    if english.lower() in kook_name:
                        return 0.9
        
        # 3. 包含关系
        if clean_kook in clean_target or clean_target in clean_kook:
            return 0.7
        
        # 4. Levenshtein距离（编辑距离）
        distance = self._levenshtein_distance(clean_kook, clean_target)
        max_len = max(len(clean_kook), len(clean_target))
        
        if max_len == 0:
            return 0.0
        
        # 编辑距离越小，相似度越高
        similarity = 1.0 - (distance / max_len)
        
        # 5. 字符集相似度
        char_similarity = self._character_similarity(kook_name, target_name)
        
        # 综合评分：70%编辑距离 + 30%字符集相似度
        final_score = similarity * 0.7 + char_similarity * 0.3
        
        return final_score
    
    def _clean_name(self, name: str) -> str:
        """
        清理频道名称（去除特殊字符）
        
        Args:
            name: 频道名
            
        Returns:
            清理后的名称
        """
        # 去除常见前缀符号
        name = name.lstrip('#＃*﹡-—_·・|丨｜ ')
        
        # 去除空格
        name = name.replace(' ', '').replace('　', '')
        
        return name
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算Levenshtein距离（编辑距离）
        
        Args:
            s1: 字符串1
            s2: 字符串2
            
        Returns:
            编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # 插入、删除、替换的代价
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _character_similarity(self, s1: str, s2: str) -> float:
        """
        计算字符集相似度
        
        Args:
            s1: 字符串1
            s2: 字符串2
            
        Returns:
            相似度 0.0-1.0
        """
        set1 = set(s1)
        set2 = set(s2)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = set1 & set2
        union = set1 | set2
        
        return len(intersection) / len(union)
    
    def get_confidence_level(self, score: float) -> str:
        """
        获取置信度等级
        
        Args:
            score: 相似度分数
            
        Returns:
            置信度等级：high/medium/low
        """
        if score >= 0.8:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def get_confidence_label(self, score: float) -> str:
        """
        获取置信度标签（中文）
        
        Args:
            score: 相似度分数
            
        Returns:
            置信度标签
        """
        level = self.get_confidence_level(score)
        labels = {
            'high': '高（推荐使用）',
            'medium': '中（可能正确）',
            'low': '低（需要确认）'
        }
        return labels.get(level, '未知')
    
    def batch_match(self, kook_channels: List[Dict], 
                    target_channels: List[Dict],
                    min_confidence: float = 0.5) -> Dict[str, List[Dict]]:
        """
        批量匹配频道
        
        Args:
            kook_channels: KOOK频道列表
            target_channels: 目标频道列表
            min_confidence: 最小置信度阈值
            
        Returns:
            匹配结果 {kook_channel_id: [匹配的目标频道列表]}
        """
        results = {}
        
        for kook_channel in kook_channels:
            kook_id = kook_channel.get('id')
            kook_name = kook_channel.get('name', '')
            
            # 找到所有匹配
            matches = self.find_best_match(kook_name, target_channels)
            
            # 过滤低置信度匹配
            filtered_matches = [
                {
                    'target_channel': match[0],
                    'confidence_score': match[1],
                    'confidence_level': self.get_confidence_level(match[1]),
                    'confidence_label': self.get_confidence_label(match[1])
                }
                for match in matches
                if match[1] >= min_confidence
            ]
            
            if filtered_matches:
                results[kook_id] = filtered_matches
        
        return results
    
    def suggest_mappings(self, kook_channels: List[Dict],
                         discord_channels: List[Dict],
                         telegram_chats: List[Dict],
                         feishu_chats: List[Dict],
                         min_confidence: float = 0.6) -> List[Dict]:
        """
        智能推荐映射关系（跨平台）
        
        Args:
            kook_channels: KOOK频道列表
            discord_channels: Discord频道列表
            telegram_chats: Telegram群组列表
            feishu_chats: 飞书群组列表
            min_confidence: 最小置信度
            
        Returns:
            推荐的映射列表
        """
        suggestions = []
        
        for kook_channel in kook_channels:
            kook_id = kook_channel.get('id')
            kook_name = kook_channel.get('name', '')
            
            # Discord匹配
            discord_matches = self.find_best_match(kook_name, discord_channels)
            for match, score in discord_matches:
                if score >= min_confidence:
                    suggestions.append({
                        'kook_channel_id': kook_id,
                        'kook_channel_name': kook_name,
                        'target_platform': 'discord',
                        'target_channel': match,
                        'confidence_score': score,
                        'confidence_level': self.get_confidence_level(score),
                        'confidence_label': self.get_confidence_label(score)
                    })
            
            # Telegram匹配
            telegram_matches = self.find_best_match(kook_name, telegram_chats)
            for match, score in telegram_matches:
                if score >= min_confidence:
                    suggestions.append({
                        'kook_channel_id': kook_id,
                        'kook_channel_name': kook_name,
                        'target_platform': 'telegram',
                        'target_channel': match,
                        'confidence_score': score,
                        'confidence_level': self.get_confidence_level(score),
                        'confidence_label': self.get_confidence_label(score)
                    })
            
            # 飞书匹配
            feishu_matches = self.find_best_match(kook_name, feishu_chats)
            for match, score in feishu_matches:
                if score >= min_confidence:
                    suggestions.append({
                        'kook_channel_id': kook_id,
                        'kook_channel_name': kook_name,
                        'target_platform': 'feishu',
                        'target_channel': match,
                        'confidence_score': score,
                        'confidence_level': self.get_confidence_level(score),
                        'confidence_label': self.get_confidence_label(score)
                    })
        
        # 按置信度降序排列
        suggestions.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return suggestions


# 创建全局实例
smart_mapping_rules = SmartMappingRulesEnhanced()


def find_best_match(kook_channel_name: str, target_channels: List[Dict]) -> List[Tuple[Dict, float]]:
    """找到最佳匹配（便捷函数）"""
    return smart_mapping_rules.find_best_match(kook_channel_name, target_channels)


def suggest_mappings(kook_channels, discord_channels, telegram_chats, feishu_chats, min_confidence=0.6):
    """智能推荐映射（便捷函数）"""
    return smart_mapping_rules.suggest_mappings(
        kook_channels, discord_channels, telegram_chats, feishu_chats, min_confidence
    )
