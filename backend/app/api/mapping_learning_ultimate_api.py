"""
🧠 P1-2优化: AI映射学习引擎API（终极版）

作者: KOOK Forwarder Team
版本: 11.0.0
日期: 2025-10-28
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..utils.mapping_learning_engine_ultimate import mapping_learning_engine
from ..utils.logger import logger

router = APIRouter(prefix="/api/mapping-learning", tags=["AI映射学习"])


@router.post("/recommend")
async def recommend_mappings(
    kook_channel: Dict,
    target_channels: List[Dict]
):
    """
    获取AI推荐的频道映射
    
    Body:
    {
      "kook_channel": {"id": "xxx", "name": "公告频道"},
      "target_channels": [
        {"id": "123", "name": "announcements", "platform": "discord"},
        {"id": "456", "name": "updates", "platform": "telegram"}
      ]
    }
    
    Response:
    [
      {
        "target_channel": {...},
        "confidence": 0.95,
        "reason": "完全匹配 | 翻译匹配"
      },
      ...
    ]
    """
    try:
        logger.info(f"推荐映射: {kook_channel['name']}")
        
        recommendations = mapping_learning_engine.recommend_mappings(
            kook_channel, target_channels
        )
        
        return [
            {
                'target_channel': target,
                'confidence': round(confidence, 3),
                'reason': reason
            }
            for target, confidence, reason in recommendations
        ]
    
    except Exception as e:
        logger.error(f"推荐失败: {str(e)}")
        raise HTTPException(500, f"推荐失败: {str(e)}")


@router.post("/record")
async def record_mapping(
    kook_channel_id: str,
    target_channel_id: str
):
    """
    记录用户的映射选择（用于学习）
    
    每次用户创建或使用映射时调用
    
    Args:
        kook_channel_id: KOOK频道ID
        target_channel_id: 目标频道ID
    """
    try:
        mapping_learning_engine.record_mapping(
            kook_channel_id, target_channel_id
        )
        
        return {"success": True, "message": "已记录"}
    
    except Exception as e:
        logger.error(f"记录失败: {str(e)}")
        raise HTTPException(500, f"记录失败: {str(e)}")


@router.get("/stats")
async def get_stats():
    """
    获取学习引擎统计信息
    
    Returns:
        {
            "total_mappings_learned": 50,
            "total_uses": 235,
            "most_used_mapping": {...},
            "translation_table_size": 15
        }
    """
    try:
        stats = mapping_learning_engine.get_stats()
        return stats
    except Exception as e:
        logger.error(f"获取统计失败: {str(e)}")
        raise HTTPException(500, f"获取统计失败: {str(e)}")


@router.get("/translation-table")
async def get_translation_table():
    """
    获取翻译表
    
    Returns:
        {
            "公告": ["announcement", "announce", ...],
            ...
        }
    """
    try:
        table = mapping_learning_engine.export_translation_table()
        return table
    except Exception as e:
        logger.error(f"获取翻译表失败: {str(e)}")
        raise HTTPException(500, f"获取翻译表失败: {str(e)}")


@router.post("/translation-table")
async def update_translation_table(table: Dict[str, List[str]]):
    """
    更新自定义翻译表
    
    Body:
    {
        "新词": ["new", "word"],
        ...
    }
    """
    try:
        mapping_learning_engine.import_translation_table(table)
        return {
            "success": True,
            "message": f"已导入{len(table)}个自定义词"
        }
    except Exception as e:
        logger.error(f"导入翻译表失败: {str(e)}")
        raise HTTPException(500, f"导入翻译表失败: {str(e)}")
