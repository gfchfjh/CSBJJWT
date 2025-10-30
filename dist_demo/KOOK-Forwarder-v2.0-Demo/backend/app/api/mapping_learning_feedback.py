"""
✅ P1-6优化: 映射学习反馈API
提供用户反馈接口，优化智能映射推荐
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..utils.mapping_learner import mapping_learner
from ..utils.logger import logger


router = APIRouter(prefix="/api/mapping-learning", tags=["映射学习"])


class FeedbackRequest(BaseModel):
    """反馈请求"""
    kook_channel_id: str
    kook_channel_name: str
    target_platform: str
    target_channel_id: str
    target_channel_name: str
    accepted: bool
    confidence_score: float = 0.0


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    提交用户反馈
    
    当用户接受或拒绝推荐时调用此接口
    """
    try:
        success = mapping_learner.record_user_feedback(
            kook_channel_id=request.kook_channel_id,
            kook_channel_name=request.kook_channel_name,
            target_platform=request.target_platform,
            target_channel_id=request.target_channel_id,
            target_channel_name=request.target_channel_name,
            accepted=request.accepted,
            confidence_score=request.confidence_score
        )
        
        if success:
            action = "接受" if request.accepted else "拒绝"
            return {
                "success": True,
                "message": f"已记录您的反馈（{action}），系统将持续优化推荐"
            }
        else:
            raise HTTPException(status_code=500, detail="记录反馈失败")
            
    except Exception as e:
        logger.error(f"提交反馈失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_learning_statistics():
    """
    获取学习统计信息
    
    Returns:
        学习效果统计、接受率、热门映射等
    """
    try:
        stats = mapping_learner.get_learning_statistics()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-old")
async def clear_old_feedbacks(days: int = 90):
    """
    清理旧的反馈记录
    
    Args:
        days: 保留最近多少天，默认90天
    """
    try:
        deleted_count = mapping_learner.clear_old_feedbacks(days)
        return {
            "success": True,
            "message": f"已清理 {deleted_count} 条{days}天前的记录"
        }
    except Exception as e:
        logger.error(f"清理旧反馈失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
