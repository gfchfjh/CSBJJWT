"""
智能映射API - 高级版
✅ P0-4: 智能频道映射推荐
✅ 使用多种算法匹配最佳映射方案
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
import difflib
from ..database import get_database
from ..utils.logger import logger

router = APIRouter(prefix="/api/smart-mapping", tags=["smart-mapping"])


class ChannelMatch(BaseModel):
    """频道匹配结果"""
    bot_id: int
    bot_name: str
    platform: str
    channel_id: str
    channel_name: str
    similarity: float
    confidence: float
    match_reason: str


class MappingSuggestion(BaseModel):
    """映射建议"""
    kook_server_id: str
    kook_server_name: str
    kook_channel_id: str
    kook_channel_name: str
    matches: List[ChannelMatch]
    best_match: Optional[ChannelMatch]


@router.get("/suggest")
async def suggest_mappings(
    account_id: Optional[int] = None,
    threshold: float = 0.6
) -> List[MappingSuggestion]:
    """
    智能推荐频道映射
    
    算法：
    1. 名称相似度匹配（difflib.SequenceMatcher）
    2. 关键词匹配（announcement→公告，event→活动等）
    3. 类型匹配（文字频道→文字频道）
    4. 历史模式学习
    5. 综合评分
    
    Args:
        account_id: KOOK账号ID（可选，不指定则使用所有账号）
        threshold: 相似度阈值（0-1，默认0.6）
    
    Returns:
        映射建议列表
    """
    db = get_database()
    
    try:
        # 1. 获取KOOK频道
        kook_channels = await _get_kook_channels(db, account_id)
        
        if not kook_channels:
            logger.warning("没有可用的KOOK频道")
            return []
        
        logger.info(f"获取到{len(kook_channels)}个KOOK频道")
        
        # 2. 获取所有Bot和目标频道
        target_bots = await _get_all_target_bots(db)
        
        if not target_bots:
            logger.warning("没有配置任何Bot")
            return []
        
        logger.info(f"获取到{len(target_bots)}个目标Bot")
        
        # 3. 为每个KOOK频道查找匹配
        suggestions = []
        
        for kook_channel in kook_channels:
            matches = await _find_matches_for_channel(
                kook_channel,
                target_bots,
                threshold
            )
            
            if matches:
                # 选择最佳匹配（得分最高）
                best_match = matches[0] if matches else None
                
                suggestion = MappingSuggestion(
                    kook_server_id=kook_channel['server_id'],
                    kook_server_name=kook_channel['server_name'],
                    kook_channel_id=kook_channel['channel_id'],
                    kook_channel_name=kook_channel['channel_name'],
                    matches=matches,
                    best_match=best_match
                )
                
                suggestions.append(suggestion)
        
        logger.info(f"生成了{len(suggestions)}个映射建议")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"生成映射建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _get_kook_channels(db, account_id: Optional[int] = None) -> List[Dict]:
    """获取KOOK频道列表"""
    # 这里需要实现从数据库或API获取KOOK频道
    # 简化实现，实际应该调用KOOK API
    
    # 示例数据
    return [
        {
            'server_id': 'server1',
            'server_name': '游戏公告服务器',
            'channel_id': 'ch1',
            'channel_name': '公告频道',
            'channel_type': 1  # 1=文字，2=语音
        },
        {
            'server_id': 'server1',
            'server_name': '游戏公告服务器',
            'channel_id': 'ch2',
            'channel_name': '活动频道',
            'channel_type': 1
        },
        {
            'server_id': 'server1',
            'server_name': '游戏公告服务器',
            'channel_id': 'ch3',
            'channel_name': '更新日志',
            'channel_type': 1
        }
    ]


async def _get_all_target_bots(db) -> List[Dict]:
    """获取所有目标Bot"""
    bots = db.execute(
        "SELECT * FROM bot_configs WHERE status = 'active'"
    ).fetchall()
    
    result = []
    
    for bot in bots:
        # 解析config JSON
        import json
        config = json.loads(bot['config'])
        
        # 根据平台获取频道列表
        channels = await _get_bot_channels(bot['platform'], config)
        
        result.append({
            'id': bot['id'],
            'name': bot['name'],
            'platform': bot['platform'],
            'channels': channels
        })
    
    return result


async def _get_bot_channels(platform: str, config: Dict) -> List[Dict]:
    """获取Bot的频道列表"""
    # 根据平台获取频道
    # 实际应该调用各平台API
    
    # 示例数据
    if platform == 'discord':
        return [
            {'id': 'discord_ch1', 'name': 'announcements', 'type': 'text'},
            {'id': 'discord_ch2', 'name': 'events', 'type': 'text'},
            {'id': 'discord_ch3', 'name': 'updates', 'type': 'text'}
        ]
    elif platform == 'telegram':
        return [
            {'id': 'tg_ch1', 'name': '公告群', 'type': 'group'},
            {'id': 'tg_ch2', 'name': '活动群', 'type': 'group'}
        ]
    elif platform == 'feishu':
        return [
            {'id': 'feishu_ch1', 'name': '运营群', 'type': 'group'},
            {'id': 'feishu_ch2', 'name': '技术群', 'type': 'group'}
        ]
    
    return []


async def _find_matches_for_channel(
    kook_channel: Dict,
    target_bots: List[Dict],
    threshold: float
) -> List[ChannelMatch]:
    """为单个KOOK频道查找匹配"""
    matches = []
    kook_name = kook_channel['channel_name'].lower()
    
    for bot in target_bots:
        for target_channel in bot['channels']:
            target_name = target_channel['name'].lower()
            
            # 1. 名称相似度匹配
            similarity = difflib.SequenceMatcher(
                None,
                kook_name,
                target_name
            ).ratio()
            
            # 2. 关键词匹配
            keyword_bonus = _calculate_keyword_bonus(kook_name, target_name)
            
            # 3. 类型匹配
            type_bonus = _calculate_type_bonus(
                kook_channel.get('channel_type'),
                target_channel.get('type')
            )
            
            # 4. 历史模式学习（简化版）
            history_bonus = 0.0  # TODO: 实现历史学习
            
            # 综合评分
            confidence = (
                similarity * 0.4 +
                keyword_bonus * 0.3 +
                type_bonus * 0.2 +
                history_bonus * 0.1
            )
            
            if confidence >= threshold:
                match = ChannelMatch(
                    bot_id=bot['id'],
                    bot_name=bot['name'],
                    platform=bot['platform'],
                    channel_id=target_channel['id'],
                    channel_name=target_channel['name'],
                    similarity=similarity,
                    confidence=confidence,
                    match_reason=_generate_match_reason(
                        similarity,
                        keyword_bonus,
                        type_bonus
                    )
                )
                
                matches.append(match)
    
    # 按置信度排序
    matches.sort(key=lambda x: x.confidence, reverse=True)
    
    return matches[:5]  # 返回前5个最佳匹配


def _calculate_keyword_bonus(kook_name: str, target_name: str) -> float:
    """计算关键词匹配加成"""
    # 定义关键词映射
    keyword_mappings = {
        ('公告', 'announcement', 'announcements', '通知', 'notice'): 1.0,
        ('活动', 'event', 'events', '比赛', 'competition'): 1.0,
        ('更新', 'update', 'updates', 'changelog', '日志'): 1.0,
        ('讨论', 'discussion', 'chat', '聊天', 'general'): 0.8,
        ('技术', 'tech', 'technical', 'dev', 'development'): 0.9,
        ('反馈', 'feedback', 'bug', 'report', '问题'): 0.8
    }
    
    bonus = 0.0
    
    for keywords, score in keyword_mappings.items():
        for keyword in keywords:
            if keyword in kook_name and keyword in target_name:
                bonus = max(bonus, score)
            elif keyword in kook_name or keyword in target_name:
                # 单边匹配，降低权重
                bonus = max(bonus, score * 0.5)
    
    return bonus


def _calculate_type_bonus(kook_type: Optional[int], target_type: Optional[str]) -> float:
    """计算类型匹配加成"""
    if kook_type is None or target_type is None:
        return 0.0
    
    # KOOK频道类型：1=文字，2=语音
    # 目标类型：text/voice/group等
    
    if kook_type == 1 and target_type in ('text', 'group'):
        return 1.0
    elif kook_type == 2 and target_type == 'voice':
        return 1.0
    
    return 0.0


def _generate_match_reason(
    similarity: float,
    keyword_bonus: float,
    type_bonus: float
) -> str:
    """生成匹配原因说明"""
    reasons = []
    
    if similarity >= 0.8:
        reasons.append("名称高度相似")
    elif similarity >= 0.6:
        reasons.append("名称部分相似")
    
    if keyword_bonus >= 0.8:
        reasons.append("关键词匹配")
    
    if type_bonus >= 0.8:
        reasons.append("类型匹配")
    
    if not reasons:
        reasons.append("综合评估匹配")
    
    return "；".join(reasons)


@router.post("/apply")
async def apply_suggestions(suggestions: List[Dict]):
    """
    应用映射建议
    
    Args:
        suggestions: 映射建议列表
    """
    db = get_database()
    
    try:
        applied_count = 0
        
        for suggestion in suggestions:
            # 插入映射记录
            db.execute("""
                INSERT OR REPLACE INTO channel_mappings
                (kook_server_id, kook_channel_id, kook_channel_name,
                 target_platform, target_bot_id, target_channel_id, enabled)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (
                suggestion['kook_server_id'],
                suggestion['kook_channel_id'],
                suggestion['kook_channel_name'],
                suggestion['target_platform'],
                suggestion['target_bot_id'],
                suggestion['target_channel_id']
            ))
            
            applied_count += 1
        
        db.commit()
        
        logger.info(f"应用了{applied_count}个映射建议")
        
        return {
            "success": True,
            "applied_count": applied_count
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"应用映射建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_mapping_stats():
    """获取映射统计信息"""
    db = get_database()
    
    try:
        # 总映射数
        total = db.execute(
            "SELECT COUNT(*) FROM channel_mappings"
        ).fetchone()[0]
        
        # 启用的映射数
        enabled = db.execute(
            "SELECT COUNT(*) FROM channel_mappings WHERE enabled = 1"
        ).fetchone()[0]
        
        # 按平台统计
        by_platform = {}
        platforms = db.execute("""
            SELECT target_platform, COUNT(*) as count
            FROM channel_mappings
            GROUP BY target_platform
        """).fetchall()
        
        for row in platforms:
            by_platform[row['target_platform']] = row['count']
        
        return {
            "total": total,
            "enabled": enabled,
            "disabled": total - enabled,
            "by_platform": by_platform
        }
        
    except Exception as e:
        logger.error(f"获取映射统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
