"""
内存统计API
提供内存使用情况查询接口
"""
from fastapi import APIRouter, HTTPException
from ..utils.memory_monitor import memory_monitor
from ..utils.logger import logger

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.get("/stats")
async def get_memory_stats():
    """
    获取内存统计信息
    
    Returns:
        内存使用详情
    """
    try:
        stats = memory_monitor.get_memory_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"获取内存统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_memory_recommendations():
    """
    获取内存优化建议
    
    Returns:
        优化建议列表
    """
    try:
        recommendations = memory_monitor.get_recommendations()
        return {
            "success": True,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"获取优化建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def manual_cleanup():
    """
    手动触发内存清理
    
    Returns:
        清理结果
    """
    try:
        logger.info("用户触发手动内存清理")
        await memory_monitor.cleanup_all()
        
        # 获取清理后的内存状态
        stats = memory_monitor.get_memory_stats()
        
        return {
            "success": True,
            "message": "内存清理完成",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"内存清理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_memory_history():
    """
    获取内存使用历史
    
    Returns:
        历史记录
    """
    try:
        history = list(memory_monitor.memory_history.items())
        return {
            "success": True,
            "history": history
        }
    except Exception as e:
        logger.error(f"获取内存历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
