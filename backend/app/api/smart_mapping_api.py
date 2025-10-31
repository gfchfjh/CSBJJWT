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
    
    从数据库的channel_mappings表获取已配置的KOOK频道，
    如果没有数据，则尝试从server_discovery API获取
    """
    try:
        # 首先尝试从数据库获取已映射的频道
        mappings = db.get_channel_mappings()
        
        if mappings:
            # 去重并格式化
            channels = []
            seen = set()
            
            for mapping in mappings:
                channel_id = mapping['kook_channel_id']
                if channel_id not in seen:
                    seen.add(channel_id)
                    channels.append({
                        'id': channel_id,
                        'name': mapping['kook_channel_name'],
                        'server_name': mapping.get('kook_server_name', '未知服务器'),
                        'server_id': mapping['kook_server_id']
                    })
            
            if channels:
                logger.info(f"从数据库获取到 {len(channels)} 个KOOK频道")
                return channels
        
        # 如果数据库没有数据，尝试从server_discovery获取
        from ..kook.server_fetcher import get_cached_servers
        cached = get_cached_servers(account_id)
        
        if cached and 'servers' in cached:
            channels = []
            for server in cached['servers']:
                server_id = server.get('id')
                server_name = server.get('name')
                for channel in server.get('channels', []):
                    channels.append({
                        'id': channel['id'],
                        'name': channel['name'],
                        'server_name': server_name,
                        'server_id': server_id
                    })
            
            if channels:
                logger.info(f"从缓存获取到 {len(channels)} 个KOOK频道")
                return channels
        
        # 如果都没有，返回空列表（而不是mock数据）
        logger.warning("未找到KOOK频道数据，请先配置账号并获取服务器列表")
        return []
        
    except Exception as e:
        logger.error(f"获取KOOK频道失败: {str(e)}")
        return []


async def _get_target_channels(bot_ids: List[int]) -> List[Dict]:
    """
    获取目标平台频道列表
    
    从已映射的配置中获取目标频道
    """
    try:
        channels = []
        
        # 从数据库获取已配置的Bot
        for bot_id in bot_ids:
            bot_configs = db.get_bot_configs()
            bot = next((b for b in bot_configs if b['id'] == bot_id), None)
            
            if not bot:
                continue
            
            platform = bot['platform']
            config = bot.get('config', {})
            
            # 根据平台类型，从映射中获取目标频道
            # 注意：实际的频道ID/名称来自用户配置的映射
            mappings = db.get_channel_mappings()
            
            for mapping in mappings:
                if mapping['target_bot_id'] == bot_id:
                    channels.append({
                        'id': mapping['target_channel_id'],
                        'name': mapping.get('target_channel_name', mapping['target_channel_id']),
                        'bot_id': bot_id,
                        'bot_name': bot['name'],
                        'platform': platform
                    })
        
        if channels:
            logger.info(f"从数据库获取到 {len(channels)} 个目标频道")
            return channels
        
        # 如果没有映射数据，返回空列表
        logger.warning("未找到目标频道数据，请先配置Bot和频道映射")
        return []
        
    except Exception as e:
        logger.error(f"获取目标频道失败: {str(e)}")
        return []
