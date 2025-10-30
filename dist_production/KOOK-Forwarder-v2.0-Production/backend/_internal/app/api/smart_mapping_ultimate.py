"""
智能映射API - 终极版
AI自动匹配KOOK频道到目标平台
使用三重匹配算法：完全匹配 + 关键词匹配 + 相似度匹配
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..database import db
from ..utils.logger import logger
from difflib import SequenceMatcher
import re

router = APIRouter(prefix="/api/smart-mapping", tags=["智能映射"])


class AutoMatchRequest(BaseModel):
    """自动匹配请求"""
    account_id: int
    bot_ids: List[int]


class MappingRecommendation(BaseModel):
    """映射推荐"""
    kook_server: str
    kook_server_id: str
    kook_channel: str
    kook_channel_id: str
    target: str  # bot_id:channel_id
    target_name: str
    target_bot_name: str
    target_platform: str
    confidence: float  # 0.0-1.0
    match_reason: str  # "完全匹配"/"关键词匹配"/"相似度匹配"


class TargetChannel(BaseModel):
    """目标频道"""
    id: str  # bot_id:channel_id
    bot_id: int
    bot_name: str
    platform: str
    channel_id: str
    channel_name: str


# 关键词映射表（中英文互译）
KEYWORD_MAPPING = {
    "公告": ["announcement", "notice", "news", "公告", "通知", "消息"],
    "闲聊": ["chat", "general", "casual", "闲聊", "综合", "杂谈", "水群"],
    "游戏": ["game", "gaming", "play", "游戏", "玩家"],
    "技术": ["tech", "development", "dev", "技术", "开发", "程序"],
    "活动": ["event", "activity", "活动", "比赛"],
    "更新": ["update", "changelog", "更新", "日志", "变更"],
    "帮助": ["help", "support", "帮助", "支持", "客服"],
    "反馈": ["feedback", "suggest", "反馈", "建议", "意见"],
    "测试": ["test", "beta", "测试", "内测"],
    "社区": ["community", "社区", "论坛"],
    "音乐": ["music", "音乐", "歌曲"],
    "图片": ["image", "photo", "图片", "照片", "gallery"],
    "视频": ["video", "视频", "影片"],
    "直播": ["live", "stream", "直播", "streaming"],
    "创作": ["creative", "创作", "作品"],
    "交易": ["trade", "market", "交易", "市场"],
    "招募": ["recruit", "招募", "招聘"],
    "管理": ["admin", "mod", "管理", "moderator"],
    "VIP": ["vip", "premium", "member", "会员"],
    "新手": ["newbie", "beginner", "新手", "入门"],
}


@router.post("/auto-match")
async def auto_match_channels(request: AutoMatchRequest) -> Dict[str, Any]:
    """
    智能自动匹配频道
    
    Args:
        request: 包含account_id和bot_ids
    
    Returns:
        映射推荐列表和可用目标列表
    """
    try:
        # 1. 获取KOOK频道列表
        kook_channels = await get_kook_channels(request.account_id)
        
        if not kook_channels:
            return {
                "success": False,
                "error": "未找到KOOK频道，请确保账号已登录",
                "mappings": [],
                "available_targets": []
            }
        
        # 2. 获取目标平台频道列表
        target_channels = await get_target_channels(request.bot_ids)
        
        if not target_channels:
            return {
                "success": False,
                "error": "未找到目标频道，请先配置Bot",
                "mappings": [],
                "available_targets": []
            }
        
        # 3. AI智能匹配
        mappings = []
        
        for kook_channel in kook_channels:
            kook_name = kook_channel['name'].lower()
            
            best_match = None
            best_score = 0.0
            match_reason = ""
            
            for target in target_channels:
                target_name = target['channel_name'].lower()
                
                # 三重匹配算法
                score, reason = calculate_match_score(kook_name, target_name)
                
                if score > best_score:
                    best_score = score
                    best_match = target
                    match_reason = reason
            
            # 只推荐置信度 > 0.5 的匹配
            if best_match and best_score >= 0.5:
                mappings.append({
                    "kook_server": kook_channel['server_name'],
                    "kook_server_id": kook_channel['server_id'],
                    "kook_channel": kook_channel['name'],
                    "kook_channel_id": kook_channel['id'],
                    "target": f"{best_match['bot_id']}:{best_match['channel_id']}",
                    "target_name": best_match['channel_name'],
                    "target_bot_name": best_match['bot_name'],
                    "target_platform": best_match['platform'],
                    "confidence": round(best_score, 2),
                    "match_reason": match_reason
                })
        
        logger.info(
            f"智能匹配完成: {len(kook_channels)}个KOOK频道, "
            f"匹配到{len(mappings)}个目标频道"
        )
        
        return {
            "success": True,
            "mappings": sorted(mappings, key=lambda x: x['confidence'], reverse=True),
            "available_targets": target_channels,
            "total_kook_channels": len(kook_channels),
            "matched_count": len(mappings)
        }
        
    except Exception as e:
        logger.error(f"智能匹配失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_match_score(kook_name: str, target_name: str) -> tuple[float, str]:
    """
    计算匹配分数（三重算法）
    
    返回: (score, reason)
    """
    # 1. 完全匹配（权重40%）
    if kook_name == target_name:
        return 1.0, "完全匹配"
    
    # 2. 包含匹配（权重30%）
    if kook_name in target_name or target_name in kook_name:
        score = 0.8 + 0.1 * (len(kook_name) / max(len(kook_name), len(target_name)))
        return min(score, 0.95), "包含匹配"
    
    # 3. 关键词匹配（权重20%）
    keyword_score = keyword_match_score(kook_name, target_name)
    if keyword_score >= 0.7:
        return keyword_score, "关键词匹配"
    
    # 4. 相似度匹配（权重10%）- 使用Levenshtein距离
    similarity = SequenceMatcher(None, kook_name, target_name).ratio()
    
    # 综合评分
    final_score = (
        similarity * 0.5 +  # 字符串相似度
        keyword_score * 0.5  # 关键词匹配度
    )
    
    if final_score >= 0.6:
        return final_score, "高相似度"
    elif final_score >= 0.5:
        return final_score, "中等相似度"
    else:
        return final_score, "低相似度"


def keyword_match_score(kook_name: str, target_name: str) -> float:
    """
    关键词匹配评分
    
    检查KOOK频道名是否包含某个关键词，
    以及目标频道名是否包含对应的翻译词
    """
    max_score = 0.0
    
    for cn_keyword, en_keywords in KEYWORD_MAPPING.items():
        # 检查KOOK频道是否包含中文关键词
        if cn_keyword in kook_name:
            # 检查目标频道是否包含对应的英文关键词
            for en_keyword in en_keywords:
                if en_keyword in target_name:
                    # 计算匹配度（关键词越长，权重越高）
                    keyword_weight = len(cn_keyword) / len(kook_name)
                    score = 0.7 + keyword_weight * 0.3
                    max_score = max(max_score, score)
        
        # 反向检查（KOOK可能用英文，目标用中文）
        for en_keyword in en_keywords:
            if en_keyword in kook_name:
                if cn_keyword in target_name or any(k in target_name for k in en_keywords):
                    keyword_weight = len(en_keyword) / len(kook_name)
                    score = 0.7 + keyword_weight * 0.3
                    max_score = max(max_score, score)
    
    return max_score


async def get_kook_channels(account_id: int) -> List[Dict[str, Any]]:
    """
    获取KOOK频道列表
    
    TODO: 实际实现应该从scraper获取，这里使用模拟数据
    """
    # 从数据库查询已存在的映射，提取KOOK频道信息
    mappings = db.get_channel_mappings()
    
    if mappings:
        # 从映射中提取唯一的KOOK频道
        channels_dict = {}
        for mapping in mappings:
            ch_id = mapping['kook_channel_id']
            if ch_id not in channels_dict:
                channels_dict[ch_id] = {
                    'id': ch_id,
                    'name': mapping['kook_channel_name'],
                    'server_id': mapping['kook_server_id'],
                    'server_name': mapping.get('kook_server_name', '未知服务器')
                }
        
        return list(channels_dict.values())
    
    # 如果没有映射，返回示例数据（仅用于演示）
    return [
        {
            'id': 'ch_001',
            'name': '公告频道',
            'server_id': 'srv_001',
            'server_name': '游戏公告服务器'
        },
        {
            'id': 'ch_002',
            'name': '闲聊',
            'server_id': 'srv_001',
            'server_name': '游戏公告服务器'
        },
        {
            'id': 'ch_003',
            'name': '技术讨论',
            'server_id': 'srv_002',
            'server_name': '技术交流服务器'
        },
        {
            'id': 'ch_004',
            'name': '活动频道',
            'server_id': 'srv_001',
            'server_name': '游戏公告服务器'
        },
    ]


async def get_target_channels(bot_ids: List[int]) -> List[Dict[str, Any]]:
    """
    获取目标平台频道列表
    
    TODO: 实际实现应该从各平台API获取，这里使用模拟数据
    """
    # 从数据库获取Bot配置
    target_channels = []
    
    for bot_id in bot_ids:
        bot_configs = db.execute(
            "SELECT * FROM bot_configs WHERE id = ?",
            (bot_id,)
        ).fetchone()
        
        if not bot_configs:
            continue
        
        bot_name = bot_configs['name']
        platform = bot_configs['platform']
        
        # 生成示例频道（实际应从API获取）
        if platform == 'discord':
            channels = [
                {'channel_id': 'announcements', 'channel_name': 'announcements'},
                {'channel_id': 'general', 'channel_name': 'general'},
                {'channel_id': 'tech', 'channel_name': 'tech'},
                {'channel_id': 'events', 'channel_name': 'events'},
            ]
        elif platform == 'telegram':
            channels = [
                {'channel_id': '-1001234567890', 'channel_name': '公告群'},
                {'channel_id': '-1001234567891', 'channel_name': '闲聊群'},
                {'channel_id': '-1001234567892', 'channel_name': '技术群'},
            ]
        elif platform == 'feishu':
            channels = [
                {'channel_id': 'oc_xxx1', 'channel_name': '运营群'},
                {'channel_id': 'oc_xxx2', 'channel_name': '综合群'},
                {'channel_id': 'oc_xxx3', 'channel_name': '开发群'},
            ]
        else:
            channels = []
        
        for ch in channels:
            target_channels.append({
                'id': f"{bot_id}:{ch['channel_id']}",
                'bot_id': bot_id,
                'bot_name': bot_name,
                'platform': platform,
                'channel_id': ch['channel_id'],
                'channel_name': ch['channel_name']
            })
    
    return target_channels


@router.get("/keyword-suggestions")
async def get_keyword_suggestions(query: str) -> Dict[str, Any]:
    """
    获取关键词建议
    
    用于帮助用户理解AI如何匹配频道
    """
    query = query.lower()
    suggestions = []
    
    for cn_keyword, en_keywords in KEYWORD_MAPPING.items():
        if cn_keyword in query or any(en in query for en in en_keywords):
            suggestions.append({
                "keyword": cn_keyword,
                "translations": en_keywords,
                "example": f"'{cn_keyword}' 可以匹配到 '{en_keywords[0]}'"
            })
    
    return {
        "success": True,
        "query": query,
        "suggestions": suggestions
    }
