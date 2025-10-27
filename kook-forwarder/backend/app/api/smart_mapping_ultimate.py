"""
智能映射终极版API（✨ P0-6优化：60+映射规则 + Levenshtein距离）
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from ..utils.logger import logger


router = APIRouter(prefix="/api/smart-mapping-ultimate", tags=["智能映射终极版"])


# ✨ P0-6核心: 60+智能映射规则
MAPPING_RULES = {
    # 中文→英文映射（30对）
    "公告": ["announcements", "announcement", "news", "notice", "updates"],
    "活动": ["events", "event", "activity", "activities", "campaigns"],
    "更新": ["updates", "update", "changelog", "changes", "release"],
    "讨论": ["discussion", "discuss", "chat", "talk", "forum"],
    "技术": ["tech", "technical", "technology", "dev", "development"],
    "帮助": ["help", "support", "助手", "question", "faq"],
    "反馈": ["feedback", "建议", "suggestion", "ideas"],
    "Bug": ["bugs", "issues", "问题", "defects"],
    "闲聊": ["chat", "off-topic", "random", "general", "casual"],
    "新手": ["newbie", "新人", "beginner", "starter", "welcome"],
    "规则": ["rules", "guidelines", "规定", "regulations"],
    "通知": ["notifications", "alerts", "通告", "inform"],
    "投票": ["polls", "vote", "survey", "voting"],
    "分享": ["share", "sharing", "showcase", "展示"],
    "教程": ["tutorial", "guide", "教学", "howto"],
    "资源": ["resources", "materials", "素材", "assets"],
    "下载": ["download", "downloads", "files"],
    "链接": ["links", "urls", "连接"],
    "媒体": ["media", "gallery", "图库"],
    "音乐": ["music", "audio", "songs"],
    "视频": ["video", "videos", "clips"],
    "图片": ["images", "photos", "pictures", "pics"],
    "表情": ["emojis", "stickers", "表情包"],
    "语音": ["voice", "audio", "voice-chat"],
    "直播": ["live", "stream", "streaming"],
    "录播": ["vod", "replay", "录像"],
    "竞赛": ["competition", "contest", "比赛"],
    "排行": ["leaderboard", "ranking", "榜单"],
    "成就": ["achievements", "awards", "奖励"],
    "商店": ["shop", "store", "市场"],
    
    # 英文→中文映射（30对）
    "general": ["综合", "通用", "一般", "常规", "总"],
    "development": ["开发", "研发", "dev", "编程"],
    "community": ["社区", "交流", "群组"],
    "showcase": ["展示", "作品", "分享", "成果"],
    "announcements": ["公告", "通知", "消息"],
    "off-topic": ["闲聊", "水区", "随便聊"],
    "introductions": ["介绍", "自我介绍", "新人"],
    "suggestions": ["建议", "反馈", "意见"],
    "support": ["支持", "帮助", "客服"],
    "feedback": ["反馈", "意见", "建议"],
    "bugs": ["问题", "bug", "错误"],
    "features": ["功能", "特性", "需求"],
    "documentation": ["文档", "说明", "手册"],
    "wiki": ["百科", "知识库", "文档"],
    "games": ["游戏", "gaming", "play"],
    "guild": ["公会", "战队", "clan"],
    "recruitment": ["招募", "招人", "组队"],
    "trading": ["交易", "市场", "trade"],
    "pvp": ["竞技", "对战", "pk"],
    "pve": ["副本", "任务", "挑战"],
    "guides": ["攻略", "指南", "教程"],
    "builds": ["配置", "build", "方案"],
    "meta": ["meta", "强势", "主流"],
    "tier-list": ["榜单", "排行", "评级"],
    "patch-notes": ["更新日志", "补丁", "版本"],
    "events": ["活动", "赛事", "event"],
    "tournaments": ["锦标赛", "比赛", "竞赛"],
    "streams": ["直播", "stream", "实况"],
    "clips": ["精彩片段", "剪辑", "高光"],
    "memes": ["梗图", "表情包", "meme"],
}


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    计算Levenshtein编辑距离
    
    Args:
        s1: 字符串1
        s2: 字符串2
    
    Returns:
        编辑距离
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # 插入、删除、替换的成本
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def calculate_confidence(source: str, target: str) -> float:
    """
    计算映射置信度（✨ P0-6核心算法）
    
    算法:
    1. 完全匹配: 1.0
    2. 包含关系: 0.9
    3. 规则匹配: 0.8
    4. Levenshtein相似度 > 0.8: 0.7-0.8
    5. Levenshtein相似度 > 0.6: 0.5-0.6
    6. 无匹配: 0.0
    
    Args:
        source: KOOK频道名
        target: 目标频道名
    
    Returns:
        置信度 (0.0 - 1.0)
    """
    source_lower = source.lower().strip()
    target_lower = target.lower().strip()
    
    # 规则1: 完全匹配
    if source_lower == target_lower:
        return 1.0
    
    # 规则2: 包含关系
    if source_lower in target_lower or target_lower in source_lower:
        return 0.9
    
    # 规则3: 规则匹配
    for cn, en_list in MAPPING_RULES.items():
        source_matches = source_lower in cn.lower() or any(
            source_lower in en.lower() for en in en_list
        )
        target_matches = target_lower in cn.lower() or any(
            target_lower in en.lower() for en in en_list
        )
        
        if source_matches and target_matches:
            return 0.8
    
    # 规则4: Levenshtein距离
    distance = levenshtein_distance(source_lower, target_lower)
    max_len = max(len(source_lower), len(target_lower))
    
    if max_len == 0:
        return 0.0
    
    similarity = 1 - (distance / max_len)
    
    if similarity >= 0.8:
        return 0.7
    elif similarity >= 0.6:
        return 0.5
    elif similarity >= 0.4:
        return 0.3
    
    return 0.0


class MappingSuggestion(BaseModel):
    """映射建议"""
    source_channel_id: str
    source_channel_name: str
    target_channel_id: str
    target_channel_name: str
    target_bot_id: int
    confidence: float
    confidence_level: str  # 'high' | 'medium' | 'low'


class SmartMappingRequest(BaseModel):
    """智能映射请求"""
    kook_channels: List[Dict]  # [{"id": "...", "name": "..."}]
    target_channels: List[Dict]  # [{"id": "...", "name": "...", "bot_id": 1}]


@router.post("/suggest", response_model=List[MappingSuggestion])
async def suggest_mappings(request: SmartMappingRequest):
    """
    智能映射建议（✨ P0-6核心功能）
    
    Args:
        kook_channels: KOOK频道列表
        target_channels: 目标频道列表
    
    Returns:
        映射建议列表（按置信度排序）
    """
    try:
        suggestions = []
        
        for kook_channel in request.kook_channels:
            best_matches = []
            
            for target_channel in request.target_channels:
                confidence = calculate_confidence(
                    kook_channel['name'],
                    target_channel['name']
                )
                
                if confidence > 0:
                    # 分级
                    if confidence >= 0.8:
                        level = 'high'
                    elif confidence >= 0.5:
                        level = 'medium'
                    else:
                        level = 'low'
                    
                    best_matches.append({
                        'target': target_channel,
                        'confidence': confidence,
                        'level': level
                    })
            
            # 按置信度排序
            best_matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            # 只保留置信度 >= 0.5 的匹配
            for match in best_matches:
                if match['confidence'] >= 0.5:
                    suggestions.append(MappingSuggestion(
                        source_channel_id=kook_channel['id'],
                        source_channel_name=kook_channel['name'],
                        target_channel_id=match['target']['id'],
                        target_channel_name=match['target']['name'],
                        target_bot_id=match['target']['bot_id'],
                        confidence=match['confidence'],
                        confidence_level=match['level']
                    ))
        
        logger.info(f"✅ 生成了 {len(suggestions)} 条智能映射建议")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"生成智能映射建议失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules")
async def get_mapping_rules():
    """
    获取所有映射规则
    
    Returns:
        60+映射规则字典
    """
    return {
        "rules": MAPPING_RULES,
        "total_rules": len(MAPPING_RULES),
        "description": "中英文频道名称映射规则库"
    }
