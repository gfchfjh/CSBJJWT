"""
🗄️ P2-1优化: 数据库优化API

作者: KOOK Forwarder Team
版本: 11.0.0
日期: 2025-10-28
"""
from fastapi import APIRouter, HTTPException
from ..utils.database_optimizer_ultimate import database_optimizer
from ..utils.logger import logger

router = APIRouter(prefix="/api/database", tags=["数据库优化"])


@router.post("/optimize")
async def optimize_database():
    """
    执行所有数据库优化
    
    包括：
    1. 归档30天前的日志
    2. VACUUM压缩
    3. 分析统计信息
    4. 完整性检查
    
    Returns:
        {
            "archive": {...},
            "vacuum": {...},
            "analyze": {...},
            "integrity": {...},
            "elapsed": 15.5
        }
    """
    try:
        logger.info("开始数据库优化...")
        result = database_optimizer.optimize_all()
        return result
    except Exception as e:
        logger.error(f"数据库优化失败: {str(e)}")
        raise HTTPException(500, f"数据库优化失败: {str(e)}")


@router.post("/archive")
async def archive_old_logs():
    """
    归档30天前的日志
    
    Returns:
        {
            "success": true,
            "archived_count": 1234,
            "deleted_count": 1234,
            "message": "已归档1234条日志"
        }
    """
    try:
        result = database_optimizer.archive_old_logs()
        return result
    except Exception as e:
        logger.error(f"归档失败: {str(e)}")
        raise HTTPException(500, f"归档失败: {str(e)}")


@router.post("/vacuum")
async def vacuum_database():
    """
    VACUUM压缩数据库
    
    Returns:
        {
            "success": true,
            "size_before_bytes": 104857600,
            "size_after_bytes": 73400320,
            "saved_bytes": 31457280,
            "saved_percent": 30.0,
            "message": "节省30.00 MB (30.0%)"
        }
    """
    try:
        result = database_optimizer.vacuum_database()
        return result
    except Exception as e:
        logger.error(f"压缩失败: {str(e)}")
        raise HTTPException(500, f"压缩失败: {str(e)}")


@router.post("/analyze")
async def analyze_database():
    """
    分析数据库（更新统计信息）
    
    Returns:
        {
            "success": true,
            "stats": {...},
            "message": "分析完成"
        }
    """
    try:
        result = database_optimizer.analyze_database()
        return result
    except Exception as e:
        logger.error(f"分析失败: {str(e)}")
        raise HTTPException(500, f"分析失败: {str(e)}")


@router.get("/info")
async def get_database_info():
    """
    获取数据库基本信息
    
    Returns:
        {
            "path": "/path/to/config.db",
            "size_bytes": 104857600,
            "size_formatted": "100.00 MB",
            "modified_at": "2025-10-28T10:00:00",
            "total_records": 10000,
            "tables": {
                "message_logs": 8500,
                "accounts": 5,
                ...
            }
        }
    """
    try:
        info = database_optimizer.get_database_info()
        return info
    except Exception as e:
        logger.error(f"获取信息失败: {str(e)}")
        raise HTTPException(500, f"获取信息失败: {str(e)}")


@router.get("/slow-queries")
async def get_slow_queries():
    """
    获取慢查询和优化建议
    
    Returns:
        [
            {
                "table": "message_logs",
                "recommendation": "定期归档旧数据",
                "reason": "表数据量大"
            },
            ...
        ]
    """
    try:
        queries = database_optimizer.get_slow_queries()
        return queries
    except Exception as e:
        logger.error(f"获取慢查询失败: {str(e)}")
        raise HTTPException(500, f"获取慢查询失败: {str(e)}")
