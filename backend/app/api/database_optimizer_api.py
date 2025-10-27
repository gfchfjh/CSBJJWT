"""
数据库优化API接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..utils.database_optimizer import db_optimizer
from ..utils.logger import logger

router = APIRouter(prefix="/api/database", tags=["数据库优化"])


class OptimizeRequest(BaseModel):
    """优化请求"""
    full: bool = False  # 是否完整优化（包括归档和压缩）


class ArchiveRequest(BaseModel):
    """归档请求"""
    days: int = 30  # 归档多少天前的数据


@router.post("/optimize")
async def optimize_database(request: OptimizeRequest):
    """
    优化数据库
    
    Args:
        request.full: 是否完整优化（包括归档+压缩）
        
    Returns:
        {
            "success": True,
            "message": "优化完成",
            "stats": {...}
        }
    """
    try:
        logger.info(f"开始数据库优化（full={request.full}）...")
        
        db_optimizer.optimize_database(full=request.full)
        
        stats = db_optimizer.get_database_stats()
        
        return {
            "success": True,
            "message": "数据库优化完成",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"数据库优化失败: {str(e)}")
        raise HTTPException(500, f"优化失败: {str(e)}")


@router.post("/archive")
async def archive_logs(request: ArchiveRequest):
    """
    归档旧日志
    
    Args:
        request.days: 归档多少天前的数据
        
    Returns:
        {
            "success": True,
            "archived_count": 12345
        }
    """
    try:
        archived_count = db_optimizer.archive_old_logs(days=request.days)
        
        return {
            "success": True,
            "archived_count": archived_count,
            "message": f"已归档 {archived_count} 条记录"
        }
    except Exception as e:
        logger.error(f"归档失败: {str(e)}")
        raise HTTPException(500, f"归档失败: {str(e)}")


@router.post("/vacuum")
async def vacuum_database():
    """
    压缩数据库（回收空间）
    
    Returns:
        {
            "success": True,
            "message": "压缩完成"
        }
    """
    try:
        db_optimizer.vacuum_database()
        
        return {
            "success": True,
            "message": "数据库压缩完成"
        }
    except Exception as e:
        logger.error(f"压缩失败: {str(e)}")
        raise HTTPException(500, f"压缩失败: {str(e)}")


@router.get("/stats")
async def get_database_stats():
    """
    获取数据库统计信息
    
    Returns:
        {
            "file_size_mb": 12.5,
            "table_counts": {...},
            "index_count": 15,
            "tables": [...]
        }
    """
    try:
        stats = db_optimizer.get_database_stats()
        return stats
    except Exception as e:
        logger.error(f"获取统计失败: {str(e)}")
        raise HTTPException(500, f"获取统计失败: {str(e)}")


@router.post("/analyze-query")
async def analyze_query(query: str):
    """
    分析查询性能
    
    Args:
        query: SQL查询语句
        
    Returns:
        {
            "query": "...",
            "execution_plan": [...],
            "has_index": True/False,
            "suggestions": [...]
        }
    """
    try:
        analysis = db_optimizer.analyze_query_performance(query)
        return analysis
    except Exception as e:
        logger.error(f"查询分析失败: {str(e)}")
        raise HTTPException(500, f"分析失败: {str(e)}")
