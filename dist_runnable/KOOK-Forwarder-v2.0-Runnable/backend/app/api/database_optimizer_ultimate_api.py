"""
数据库优化API
✅ P2-1深度优化
"""
from fastapi import APIRouter, HTTPException, Query
from ..utils.database_optimizer_ultimate import database_optimizer
from ..utils.logger import logger

router = APIRouter(prefix="/api/database", tags=["database"])


@router.post("/archive")
async def archive_old_logs(days: int = Query(default=30, ge=1, le=365)):
    """
    归档旧日志
    
    Args:
        days: 归档多少天前的日志（默认30天）
    
    Returns:
        归档结果
    """
    try:
        logger.info(f"📦 开始归档 {days} 天前的日志...")
        
        archived_count = database_optimizer.archive_old_logs(days)
        
        return {
            "success": True,
            "archived_count": archived_count,
            "message": f"已归档 {archived_count} 条旧日志"
        }
    
    except Exception as e:
        logger.error(f"❌ 归档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vacuum")
async def vacuum_database():
    """
    执行VACUUM压缩数据库
    
    Returns:
        压缩结果
    """
    try:
        logger.info("🗜️ 开始压缩数据库...")
        
        result = database_optimizer.vacuum_database()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "result": result,
            "message": f"压缩完成，节省 {result.get('saved_percent', 0):.1f}%"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 压缩失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze")
async def analyze_database():
    """
    分析数据库统计信息
    
    Returns:
        统计信息
    """
    try:
        stats = database_optimizer.analyze_database()
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return {
            "success": True,
            "stats": stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_database():
    """
    执行完整优化流程（归档 + 压缩 + 分析）
    
    Returns:
        优化结果
    """
    try:
        logger.info("🚀 开始数据库完整优化...")
        
        result = database_optimizer.optimize_all()
        
        return {
            "success": True,
            "result": result,
            "message": "数据库优化完成"
        }
    
    except Exception as e:
        logger.error(f"❌ 优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
