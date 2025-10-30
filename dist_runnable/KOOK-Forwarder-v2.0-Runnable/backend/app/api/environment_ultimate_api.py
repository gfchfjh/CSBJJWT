"""
🔍 P0-5优化: 环境检测API（终极版）

作者: KOOK Forwarder Team
版本: 11.0.0
日期: 2025-10-28
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
from ..utils.environment_checker_ultimate import environment_checker
from ..utils.logger import logger

router = APIRouter(prefix="/api/environment", tags=["环境检测"])


@router.get("/check")
async def check_environment():
    """
    并发检测所有环境（5-10秒完成）
    
    Returns:
        {
            "elapsed": 8.5,
            "all_passed": true,
            "python": {...},
            "chromium": {...},
            "redis": {...},
            "network": {...},
            "ports": {...},
            "disk": {...}
        }
    """
    try:
        result = await environment_checker.check_all_concurrent()
        return result
    except Exception as e:
        logger.error(f"环境检测失败: {str(e)}")
        raise HTTPException(500, f"环境检测失败: {str(e)}")


@router.post("/fix/{check_name}")
async def auto_fix(check_name: str):
    """
    自动修复指定的环境问题
    
    Args:
        check_name: 检查项名称（chromium/redis/ports）
        
    Returns:
        {
            "success": true,
            "message": "修复成功"
        }
    """
    try:
        result = await environment_checker.auto_fix(check_name)
        return result
    except Exception as e:
        logger.error(f"自动修复失败: {str(e)}")
        raise HTTPException(500, f"自动修复失败: {str(e)}")


@router.get("/system-info")
async def get_system_info():
    """
    获取系统信息
    
    Returns:
        {
            "os": "Windows",
            "os_version": "10.0.19045",
            "architecture": "AMD64",
            "python_version": "3.11.5",
            ...
        }
    """
    try:
        info = environment_checker.get_system_info()
        return info
    except Exception as e:
        logger.error(f"获取系统信息失败: {str(e)}")
        raise HTTPException(500, f"获取系统信息失败: {str(e)}")
