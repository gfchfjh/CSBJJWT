"""
智能映射 API v2（增强版）
使用优化后的匹配算法
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from ..utils.smart_mapping_enhanced import smart_mapping_engine
from ..utils.logger import logger
from ..database import db


router = APIRouter(prefix="/api/smart-mapping/v2", tags=["智能映射 V2"])


class ChannelMatchRequest(BaseModel):
    """频道匹配请求"""
    kook_channel_name: str
    target_channels: List[Dict[str, str]]  # [{"id": "xxx", "name": "xxx"}]


class BatchMatchRequest(BaseModel):
    """批量匹配请求"""
    kook_channels: List[Dict[str, Any]]
    target_channels: List[Dict[str, str]]
    auto_apply_threshold: int = 90


@router.post("/match")
async def match_single_channel(request: ChannelMatchRequest) -> Dict[str, Any]:
    """
    智能匹配单个频道
    
    Args:
        request: 包含 KOOK 频道名和目标频道列表
        
    Returns:
        匹配结果列表
    """
    try:
        logger.info(f"智能匹配频道: {request.kook_channel_name}")
        
        results = smart_mapping_engine.match_channel(
            request.kook_channel_name,
            request.target_channels
        )
        
        return {
            'success': True,
            'kook_channel': request.kook_channel_name,
            'matches': results,
            'count': len(results)
        }
        
    except Exception as e:
        logger.error(f"智能匹配失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"匹配失败: {str(e)}")


@router.post("/batch-match")
async def batch_match_channels(request: BatchMatchRequest) -> Dict[str, Any]:
    """
    批量智能匹配（整个服务器）
    
    Args:
        request: 包含 KOOK 频道列表和目标频道列表
        
    Returns:
        批量匹配结果
    """
    try:
        logger.info(f"批量智能匹配: {len(request.kook_channels)} 个 KOOK 频道")
        
        results = smart_mapping_engine.batch_match(
            request.kook_channels,
            request.target_channels,
            request.auto_apply_threshold
        )
        
        return {
            'success': True,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"批量匹配失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量匹配失败: {str(e)}")


@router.post("/apply-mapping")
async def apply_smart_mapping(mapping_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    应用智能映射结果
    
    Args:
        mapping_data: 映射数据
        
    Returns:
        应用结果
    """
    try:
        logger.info("应用智能映射结果...")
        
        # 验证数据
        if 'kook_channel' not in mapping_data or 'target_channel' not in mapping_data:
            raise HTTPException(status_code=400, detail="缺少必需字段")
        
        kook_channel = mapping_data['kook_channel']
        target_channel = mapping_data['target_channel']
        
        # 保存到数据库
        mapping_id = db.add_mapping(
            kook_server_id=kook_channel.get('server_id', ''),
            kook_channel_id=kook_channel['id'],
            kook_channel_name=kook_channel['name'],
            target_platform=mapping_data.get('target_platform', 'discord'),
            target_bot_id=mapping_data.get('target_bot_id', 1),
            target_channel_id=target_channel['id']
        )
        
        logger.info(f"✅ 映射已保存: {kook_channel['name']} → {target_channel['name']}")
        
        return {
            'success': True,
            'mapping_id': mapping_id,
            'message': '映射已保存'
        }
        
    except Exception as e:
        logger.error(f"应用映射失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"应用映射失败: {str(e)}")


@router.post("/batch-apply")
async def batch_apply_mappings(mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    批量应用映射
    
    Args:
        mappings: 映射列表
        
    Returns:
        应用结果
    """
    try:
        logger.info(f"批量应用映射: {len(mappings)} 条")
        
        success_count = 0
        failed_count = 0
        errors = []
        
        for mapping in mappings:
            try:
                # 如果是自动应用的高置信度映射，直接保存
                if mapping.get('auto_applied', False):
                    kook_channel = mapping['kook_channel']
                    target_channel = mapping['target_channel']
                    
                    db.add_mapping(
                        kook_server_id=kook_channel.get('server_id', ''),
                        kook_channel_id=kook_channel['id'],
                        kook_channel_name=kook_channel['name'],
                        target_platform=mapping.get('target_platform', 'discord'),
                        target_bot_id=mapping.get('target_bot_id', 1),
                        target_channel_id=target_channel['id']
                    )
                    
                    success_count += 1
                    
            except Exception as e:
                failed_count += 1
                errors.append({
                    'kook_channel': mapping.get('kook_channel', {}).get('name', '未知'),
                    'error': str(e)
                })
        
        logger.info(f"✅ 批量应用完成: 成功 {success_count}, 失败 {failed_count}")
        
        return {
            'success': True,
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors
        }
        
    except Exception as e:
        logger.error(f"批量应用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量应用失败: {str(e)}")


@router.get("/synonyms")
async def get_synonyms() -> Dict[str, List[str]]:
    """
    获取同义词词典
    
    Returns:
        同义词词典
    """
    return {
        'synonyms': SYNONYMS,
        'count': len(SYNONYMS)
    }


@router.post("/test-match")
async def test_match(kook_name: str, target_name: str) -> Dict[str, Any]:
    """
    测试匹配（用于调试）
    
    Args:
        kook_name: KOOK 频道名
        target_name: 目标频道名
        
    Returns:
        匹配得分和详情
    """
    try:
        score = smart_mapping_engine._calculate_score(kook_name, target_name)
        confidence = smart_mapping_engine._get_confidence_level(score)
        reason = smart_mapping_engine._get_match_reason(score)
        
        return {
            'kook_name': kook_name,
            'target_name': target_name,
            'score': score,
            'confidence': confidence,
            'reason': reason,
            'would_match': score >= 60
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
