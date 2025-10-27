"""
映射学习引擎API接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..utils.mapping_learning_engine import mapping_learning_engine
from ..utils.logger import logger

router = APIRouter(prefix="/api/mapping/learning", tags=["映射学习"])


class LearnMappingRequest(BaseModel):
    """学习映射请求"""
    kook_channel_name: str
    target_channel_name: str
    target_platform: str
    confidence: float = 1.0  # 置信度（0-1）


class SuggestionRequest(BaseModel):
    """获取建议请求"""
    kook_channel_name: str
    target_platform: str
    top_k: int = 5


class ImportRequest(BaseModel):
    """导入学习数据请求"""
    data: str  # JSON字符串


@router.post("/learn")
async def learn_mapping(request: LearnMappingRequest):
    """
    学习用户映射
    
    Args:
        request: 映射信息
        
    Returns:
        {"success": True, "message": "已学习映射"}
    """
    try:
        mapping_learning_engine.learn_from_mapping(
            kook_channel_name=request.kook_channel_name,
            target_channel_name=request.target_channel_name,
            target_platform=request.target_platform,
            confidence=request.confidence
        )
        
        return {
            "success": True,
            "message": f"已学习映射: {request.kook_channel_name} → {request.target_channel_name}"
        }
    except Exception as e:
        logger.error(f"学习映射失败: {str(e)}")
        raise HTTPException(500, f"学习失败: {str(e)}")


@router.post("/suggest")
async def get_suggestions(request: SuggestionRequest):
    """
    获取智能映射建议
    
    Args:
        request: 频道信息
        
    Returns:
        {
            "suggestions": [
                {
                    "name": "建议频道名",
                    "confidence": 0.95,
                    "source": "learned",
                    "reason": "...",
                    "count": 5
                },
                ...
            ]
        }
    """
    try:
        suggestions = mapping_learning_engine.get_learned_suggestions(
            kook_channel_name=request.kook_channel_name,
            target_platform=request.target_platform,
            top_k=request.top_k
        )
        
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"获取建议失败: {str(e)}")
        raise HTTPException(500, f"获取建议失败: {str(e)}")


@router.get("/analyze")
async def analyze_quality():
    """
    分析映射质量
    
    Returns:
        {
            "total_patterns": 123,
            "high_confidence_patterns": 89,
            "platforms": {...},
            "avg_confidence": 0.75,
            "total_mappings": 567,
            "most_common_mappings": [...]
        }
    """
    try:
        analysis = mapping_learning_engine.analyze_mapping_quality()
        return analysis
    except Exception as e:
        logger.error(f"分析质量失败: {str(e)}")
        raise HTTPException(500, f"分析失败: {str(e)}")


@router.get("/export")
async def export_learning_data():
    """
    导出学习数据
    
    Returns:
        {
            "success": True,
            "data": "...",  # JSON字符串
            "stats": {...}
        }
    """
    try:
        data = mapping_learning_engine.export_learning_data()
        
        return {
            "success": True,
            "data": data,
            "stats": mapping_learning_engine.analyze_mapping_quality()
        }
    except Exception as e:
        logger.error(f"导出学习数据失败: {str(e)}")
        raise HTTPException(500, f"导出失败: {str(e)}")


@router.post("/import")
async def import_learning_data(request: ImportRequest):
    """
    导入学习数据
    
    Args:
        request.data: JSON字符串
        
    Returns:
        {"success": True, "message": "导入成功"}
    """
    try:
        success = mapping_learning_engine.import_learning_data(request.data)
        
        if success:
            return {
                "success": True,
                "message": "学习数据导入成功"
            }
        else:
            raise ValueError("导入失败：数据格式错误")
    except Exception as e:
        logger.error(f"导入学习数据失败: {str(e)}")
        raise HTTPException(500, f"导入失败: {str(e)}")
