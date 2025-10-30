"""
智能映射API
✅ P0-8优化: 提供智能频道映射接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..processors.smart_mapping_ultimate import smart_mapping_engine
from ..utils.logger import logger
from ..database import db


router = APIRouter(prefix="/api/smart-mapping", tags=["smart_mapping"])


class AutoMatchRequest(BaseModel):
    """自动匹配请求"""
    account_id: int
    bot_ids: List[int]


class MappingSaveRequest(BaseModel):
    """批量保存映射请求"""
    mappings: List[Dict[str, Any]]


@router.post("/auto-match")
async def auto_match_channels(request: AutoMatchRequest):
    """
    智能自动匹配频道
    
    Request Body:
        {
            'account_id': int,  # KOOK账号ID
            'bot_ids': [int, ...]  # 目标Bot ID列表
        }
    
    Returns:
        {
            'mappings': [
                {
                    'kook_channel_id': str,
                    'kook_channel': str,
                    'kook_server': str,
                    'target': str,
                    'target_name': str,
                    'bot_id': int,
                    'bot_name': str,
                    'confidence': float,
                    'match_reason': str
                },
                ...
            ],
            'available_targets': [...],
            'stats': {
                'total_kook_channels': int,
                'total_target_channels': int,
                'matched_count': int,
                'match_rate': float
            }
        }
    """
    try:
        # 获取KOOK频道列表
        kook_channels = await _get_kook_channels(request.account_id)
        
        if not kook_channels:
            raise HTTPException(status_code=400, detail="未找到KOOK频道，请先登录账号")
        
        # 获取目标平台频道列表
        target_channels = await _get_target_channels(request.bot_ids)
        
        if not target_channels:
            raise HTTPException(status_code=400, detail="未找到目标频道，请先配置Bot")
        
        # 智能匹配
        mappings = await smart_mapping_engine.auto_match(
            kook_channels,
            target_channels,
            platform='auto'  # 自动识别平台
        )
        
        # 统计信息
        stats = {
            'total_kook_channels': len(kook_channels),
            'total_target_channels': len(target_channels),
            'matched_count': len(mappings),
            'match_rate': round(len(mappings) / len(kook_channels) * 100, 1) if kook_channels else 0
        }
        
        logger.info(f"智能匹配完成: {stats['matched_count']}/{stats['total_kook_channels']} ({stats['match_rate']}%)")
        
        return {
            'mappings': mappings,
            'available_targets': target_channels,
            'stats': stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"智能匹配失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest")
async def suggest_mappings(kook_channels: List[Dict], target_channels: List[Dict]):
    """
    为未匹配的频道提供建议
    
    Request Body:
        {
            'kook_channels': [...],  # 未匹配的KOOK频道
            'target_channels': [...]  # 所有可用目标频道
        }
    
    Returns:
        {
            'suggestions': [
                {
                    'kook_channel': {...},
                    'suggestions': [
                        {'target': {...}, 'confidence': 0.5, 'reason': '...'},
                        ...
                    ]
                },
                ...
            ]
        }
    """
    try:
        suggestions = smart_mapping_engine.suggest_mapping(
            kook_channels,
            target_channels
        )
        
        return {
            'suggestions': suggestions
        }
        
    except Exception as e:
        logger.error(f"映射建议生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-save")
async def batch_save_mappings(request: MappingSaveRequest):
    """
    批量保存映射
    
    Request Body:
        {
            'mappings': [
                {
                    'kook_channel_id': str,
                    'target': str,
                    'bot_id': int,
                    ...
                },
                ...
            ]
        }
    
    Returns:
        {
            'success': bool,
            'saved_count': int,
            'message': str
        }
    """
    try:
        saved_count = 0
        
        for mapping in request.mappings:
            try:
                # 保存映射到数据库
                await db.create_mapping(
                    kook_channel_id=mapping['kook_channel_id'],
                    target_channel_id=mapping['target'],
                    bot_id=mapping['bot_id'],
                    enabled=True
                )
                saved_count += 1
            except Exception as e:
                logger.error(f"保存映射失败: {mapping}, 错误: {str(e)}")
        
        logger.info(f"批量保存映射完成: {saved_count}/{len(request.mappings)}")
        
        return {
            'success': True,
            'saved_count': saved_count,
            'message': f'成功保存 {saved_count} 个映射'
        }
        
    except Exception as e:
        logger.error(f"批量保存映射失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _get_kook_channels(account_id: int) -> List[Dict]:
    """
    获取KOOK频道列表
    
    TODO: 实际应该从scraper获取
    """
    # 模拟数据（实际应该从数据库或scraper获取）
    return [
        {
            'id': 'kook_ch_1',
            'name': '公告频道',
            'server_name': '游戏公告服务器',
            'server_id': 'server_1'
        },
        {
            'id': 'kook_ch_2',
            'name': '活动频道',
            'server_name': '游戏公告服务器',
            'server_id': 'server_1'
        },
        {
            'id': 'kook_ch_3',
            'name': '更新日志',
            'server_name': '游戏公告服务器',
            'server_id': 'server_1'
        },
        {
            'id': 'kook_ch_4',
            'name': '技术讨论',
            'server_name': '技术交流服务器',
            'server_id': 'server_2'
        }
    ]


async def _get_target_channels(bot_ids: List[int]) -> List[Dict]:
    """
    获取目标平台频道列表
    
    TODO: 实际应该从配置的Bot获取
    """
    # 模拟数据（实际应该从数据库获取Bot配置）
    return [
        {
            'id': 'discord_ch_1',
            'name': 'announcements',
            'bot_id': bot_ids[0] if bot_ids else 1,
            'bot_name': 'Discord Bot',
            'platform': 'discord'
        },
        {
            'id': 'discord_ch_2',
            'name': 'events',
            'bot_id': bot_ids[0] if bot_ids else 1,
            'bot_name': 'Discord Bot',
            'platform': 'discord'
        },
        {
            'id': 'telegram_ch_1',
            'name': '公告群',
            'bot_id': bot_ids[1] if len(bot_ids) > 1 else 2,
            'bot_name': 'Telegram Bot',
            'platform': 'telegram'
        },
        {
            'id': 'telegram_ch_2',
            'name': '技术讨论群',
            'bot_id': bot_ids[1] if len(bot_ids) > 1 else 2,
            'bot_name': 'Telegram Bot',
            'platform': 'telegram'
        }
    ]
