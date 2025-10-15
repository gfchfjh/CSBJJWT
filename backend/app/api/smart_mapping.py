"""
智能频道映射API
自动匹配KOOK频道与目标平台频道
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import re
from ..database import db
from ..utils.logger import logger


router = APIRouter(prefix="/api/smart-mapping", tags=["smart-mapping"])


class SmartMappingRequest(BaseModel):
    account_id: int
    kook_servers: List[Dict[str, Any]]  # KOOK服务器和频道列表
    target_bots: List[Dict[str, Any]]   # 目标平台Bot配置


class MappingSuggestion(BaseModel):
    kook_server_id: str
    kook_server_name: str
    kook_channel_id: str
    kook_channel_name: str
    target_platform: str
    target_bot_id: int
    target_channel_id: str
    target_channel_name: str
    confidence: float  # 匹配置信度 0-1
    reason: str  # 匹配原因


def normalize_name(name: str) -> str:
    """
    标准化频道名称（用于匹配）
    
    Args:
        name: 原始名称
        
    Returns:
        标准化后的名称
    """
    # 移除前缀符号
    name = re.sub(r'^[#*\-\s]+', '', name)
    
    # 转为小写
    name = name.lower()
    
    # 移除空格
    name = name.replace(' ', '')
    name = name.replace('-', '')
    name = name.replace('_', '')
    
    return name


def calculate_similarity(name1: str, name2: str) -> float:
    """
    计算两个名称的相似度
    
    Args:
        name1: 名称1
        name2: 名称2
        
    Returns:
        相似度 0-1
    """
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    # 完全匹配
    if norm1 == norm2:
        return 1.0
    
    # 包含关系
    if norm1 in norm2 or norm2 in norm1:
        # 计算包含程度
        min_len = min(len(norm1), len(norm2))
        max_len = max(len(norm1), len(norm2))
        return min_len / max_len * 0.8
    
    # Levenshtein距离（简化版）
    # 计算相同字符的比例
    set1 = set(norm1)
    set2 = set(norm2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    if union == 0:
        return 0.0
    
    return intersection / union * 0.6


def match_channel_name(kook_channel_name: str, 
                       target_channel_candidates: List[str]) -> tuple[Optional[str], float]:
    """
    从候选频道中匹配最佳目标频道
    
    Args:
        kook_channel_name: KOOK频道名称
        target_channel_candidates: 目标平台候选频道名称列表
        
    Returns:
        (最佳匹配频道名, 置信度)
    """
    best_match = None
    best_score = 0.0
    
    for candidate in target_channel_candidates:
        score = calculate_similarity(kook_channel_name, candidate)
        if score > best_score:
            best_score = score
            best_match = candidate
    
    # 只返回置信度>0.5的匹配
    if best_score >= 0.5:
        return best_match, best_score
    
    return None, 0.0


# 常见频道名称映射规则
COMMON_MAPPINGS = {
    # 中文 -> 英文
    "公告": ["announcements", "announcement", "news", "公告"],
    "活动": ["events", "event", "活动"],
    "更新": ["updates", "update", "changelog", "更新", "更新日志"],
    "讨论": ["discussion", "chat", "general", "讨论"],
    "技术": ["tech", "technology", "dev", "技术"],
    "闲聊": ["off-topic", "random", "chat", "闲聊"],
    "帮助": ["help", "support", "帮助", "支持"],
    "规则": ["rules", "rule", "规则"],
    "欢迎": ["welcome", "欢迎"],
    
    # 游戏相关
    "组队": ["lfg", "team", "组队"],
    "交易": ["trading", "trade", "交易"],
    "攻略": ["guide", "guides", "攻略"],
    
    # 多媒体
    "图片": ["images", "pics", "screenshots", "图片"],
    "视频": ["videos", "video", "视频"],
    "音乐": ["music", "音乐"],
}


def get_semantic_matches(kook_channel_name: str) -> List[str]:
    """
    获取语义相关的频道名称
    
    Args:
        kook_channel_name: KOOK频道名称
        
    Returns:
        可能匹配的频道名称列表
    """
    matches = []
    norm_name = normalize_name(kook_channel_name)
    
    for chinese, english_list in COMMON_MAPPINGS.items():
        if chinese in norm_name or norm_name in chinese:
            matches.extend(english_list)
    
    return matches


@router.post("/suggest", response_model=List[MappingSuggestion])
async def suggest_mappings(request: SmartMappingRequest):
    """
    智能建议频道映射
    
    根据频道名称相似度和语义匹配，自动建议映射关系
    """
    try:
        suggestions = []
        
        # 遍历KOOK服务器和频道
        for server in request.kook_servers:
            server_id = server.get('id')
            server_name = server.get('name')
            channels = server.get('channels', [])
            
            for channel in channels:
                channel_id = channel.get('id')
                channel_name = channel.get('name')
                channel_type = channel.get('type', 'text')
                
                # 只处理文本频道
                if channel_type != 'text':
                    continue
                
                # 对每个目标平台Bot进行匹配
                for bot in request.target_bots:
                    platform = bot.get('platform')
                    bot_id = bot.get('id')
                    bot_name = bot.get('name')
                    
                    # 模拟目标平台频道列表（实际应该从目标平台API获取）
                    # 这里使用预定义的常见频道名
                    target_channels = _get_target_platform_channels(platform)
                    
                    # 1. 直接名称匹配
                    best_match, confidence = match_channel_name(
                        channel_name,
                        [ch['name'] for ch in target_channels]
                    )
                    
                    if best_match and confidence >= 0.7:
                        # 找到对应的频道ID
                        target_ch = next((ch for ch in target_channels if ch['name'] == best_match), None)
                        if target_ch:
                            suggestions.append(MappingSuggestion(
                                kook_server_id=server_id,
                                kook_server_name=server_name,
                                kook_channel_id=channel_id,
                                kook_channel_name=channel_name,
                                target_platform=platform,
                                target_bot_id=bot_id,
                                target_channel_id=target_ch['id'],
                                target_channel_name=target_ch['name'],
                                confidence=confidence,
                                reason=f"名称匹配: '{channel_name}' ≈ '{best_match}'"
                            ))
                            continue
                    
                    # 2. 语义匹配
                    semantic_matches = get_semantic_matches(channel_name)
                    if semantic_matches:
                        for target_ch in target_channels:
                            if any(sm in normalize_name(target_ch['name']) for sm in semantic_matches):
                                suggestions.append(MappingSuggestion(
                                    kook_server_id=server_id,
                                    kook_server_name=server_name,
                                    kook_channel_id=channel_id,
                                    kook_channel_name=channel_name,
                                    target_platform=platform,
                                    target_bot_id=bot_id,
                                    target_channel_id=target_ch['id'],
                                    target_channel_name=target_ch['name'],
                                    confidence=0.6,
                                    reason=f"语义匹配: '{channel_name}' 可能对应 '{target_ch['name']}'"
                                ))
                                break
        
        # 按置信度排序
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        logger.info(f"智能映射建议: 生成了 {len(suggestions)} 条建议")
        return suggestions
        
    except Exception as e:
        logger.error(f"生成智能映射建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _get_target_platform_channels(platform: str) -> List[Dict[str, str]]:
    """
    获取目标平台的频道列表（模拟）
    实际应该通过API从目标平台获取
    
    Args:
        platform: 平台名称
        
    Returns:
        频道列表
    """
    # 这里返回常见的频道名称作为示例
    # 实际使用时应该从Discord/Telegram/飞书API获取真实频道
    common_channels = [
        {"id": "announcements", "name": "announcements"},
        {"id": "events", "name": "events"},
        {"id": "general", "name": "general"},
        {"id": "updates", "name": "updates"},
        {"id": "tech", "name": "tech"},
        {"id": "help", "name": "help"},
        {"id": "off-topic", "name": "off-topic"},
    ]
    
    return common_channels


@router.post("/apply")
async def apply_smart_mappings(suggestions: List[MappingSuggestion]):
    """
    应用智能映射建议
    
    批量创建频道映射关系
    """
    try:
        created_count = 0
        
        for suggestion in suggestions:
            # 检查映射是否已存在
            existing_mappings = db.get_channel_mappings(suggestion.kook_channel_id)
            
            # 检查是否有完全相同的映射
            duplicate = any(
                m['target_platform'] == suggestion.target_platform and
                m['target_bot_id'] == suggestion.target_bot_id and
                m['target_channel_id'] == suggestion.target_channel_id
                for m in existing_mappings
            )
            
            if duplicate:
                logger.info(f"跳过重复映射: {suggestion.kook_channel_name} -> {suggestion.target_channel_name}")
                continue
            
            # 创建映射
            db.add_channel_mapping(
                kook_server_id=suggestion.kook_server_id,
                kook_channel_id=suggestion.kook_channel_id,
                kook_channel_name=suggestion.kook_channel_name,
                target_platform=suggestion.target_platform,
                target_bot_id=suggestion.target_bot_id,
                target_channel_id=suggestion.target_channel_id
            )
            
            created_count += 1
            logger.info(f"创建映射: {suggestion.kook_channel_name} -> {suggestion.target_channel_name}")
        
        return {
            "message": f"成功创建 {created_count} 条映射",
            "created_count": created_count
        }
        
    except Exception as e:
        logger.error(f"应用智能映射失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview/{account_id}")
async def preview_smart_mapping(account_id: int):
    """
    预览智能映射（简化版）
    
    快速查看某个账号可以创建哪些智能映射
    """
    try:
        # 获取Bot配置
        bots = db.get_bot_configs()
        
        if not bots:
            return {
                "message": "请先配置至少一个Bot",
                "suggestions": []
            }
        
        # 模拟KOOK频道数据
        # 实际应该从scraper获取
        kook_servers = [
            {
                "id": "server1",
                "name": "示例服务器",
                "channels": [
                    {"id": "ch1", "name": "公告", "type": "text"},
                    {"id": "ch2", "name": "活动", "type": "text"},
                    {"id": "ch3", "name": "讨论", "type": "text"},
                ]
            }
        ]
        
        # 生成建议
        request = SmartMappingRequest(
            account_id=account_id,
            kook_servers=kook_servers,
            target_bots=bots
        )
        
        suggestions = await suggest_mappings(request)
        
        return {
            "message": f"找到 {len(suggestions)} 条映射建议",
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"预览智能映射失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
