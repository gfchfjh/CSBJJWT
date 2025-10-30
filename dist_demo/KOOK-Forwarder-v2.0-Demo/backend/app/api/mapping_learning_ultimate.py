"""
映射学习引擎API
✅ P1-2深度优化
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from ..utils.mapping_learning_engine_ultimate import mapping_learning_engine
from ..utils.logger import logger

router = APIRouter(prefix="/api/mapping/learning", tags=["mapping-learning"])


class SuggestMappingRequest(BaseModel):
    """推荐映射请求"""
    kook_channel_name: str
    target_channels: List[Dict]


@router.post("/suggest")
async def suggest_mappings(request: SuggestMappingRequest):
    """
    智能推荐映射
    
    Args:
        request: 包含KOOK频道名称和目标频道列表
    
    Returns:
        推荐结果（按置信度排序）
    """
    try:
        suggestions = mapping_learning_engine.suggest_mapping(
            request.kook_channel_name,
            request.target_channels
        )
        
        logger.info(f"💡 为频道 '{request.kook_channel_name}' 生成了 {len(suggestions)} 个映射推荐")
        
        return {
            "success": True,
            "kook_channel": request.kook_channel_name,
            "suggestions": [
                {
                    "channel": channel,
                    "confidence": round(confidence * 100, 2),
                    "confidence_level": "高" if confidence > 0.7 else "中" if confidence > 0.5 else "低",
                    "recommended": confidence > 0.7  # 置信度>70%才推荐
                }
                for channel, confidence in suggestions
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ 生成映射推荐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record")
async def record_mapping(kook_channel_id: str, target_channel_id: str):
    """
    记录用户映射行为（用于学习）
    
    Args:
        kook_channel_id: KOOK频道ID
        target_channel_id: 目标频道ID
    """
    try:
        mapping_learning_engine.record_mapping(kook_channel_id, target_channel_id)
        
        return {
            "success": True,
            "message": "映射已记录到学习引擎"
        }
    
    except Exception as e:
        logger.error(f"❌ 记录映射失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_learning_stats():
    """
    获取学习引擎统计信息
    
    Returns:
        统计信息
    """
    try:
        stats = mapping_learning_engine.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    
    except Exception as e:
        logger.error(f"❌ 获取统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_learning_data():
    """
    重置学习数据（用于测试或重新开始）
    
    Returns:
        操作结果
    """
    try:
        mapping_learning_engine.learning_data.clear()
        mapping_learning_engine.load_learning_data()
        
        logger.info("🔄 学习数据已重置")
        
        return {
            "success": True,
            "message": "学习数据已重置"
        }
    
    except Exception as e:
        logger.error(f"❌ 重置学习数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
