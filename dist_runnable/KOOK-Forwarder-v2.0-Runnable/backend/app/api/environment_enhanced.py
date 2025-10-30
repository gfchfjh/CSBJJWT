"""
环境检查 API（增强版）
提供环境检查和自动修复的 API 接口
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..utils.environment_checker_enhanced import environment_checker
from ..utils.logger import logger


router = APIRouter(prefix="/api/environment", tags=["环境检查"])


@router.get("/check")
async def check_environment() -> Dict[str, Any]:
    """
    执行完整的环境检查
    
    Returns:
        检查结果
    """
    try:
        logger.info("开始环境检查...")
        results = await environment_checker.check_all()
        logger.info(f"环境检查完成: {results['summary']}")
        return results
    except Exception as e:
        logger.error(f"环境检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"环境检查失败: {str(e)}")


@router.post("/fix/{issue_name}")
async def auto_fix_issue(issue_name: str) -> Dict[str, Any]:
    """
    自动修复指定问题
    
    Args:
        issue_name: 问题名称（如 "Playwright 浏览器"）
    
    Returns:
        修复结果
    """
    try:
        logger.info(f"开始自动修复: {issue_name}")
        success, message = await environment_checker.auto_fix(issue_name)
        
        return {
            'success': success,
            'message': message
        }
    except Exception as e:
        logger.error(f"自动修复失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"自动修复失败: {str(e)}")


@router.get("/check/playwright")
async def check_playwright() -> Dict[str, Any]:
    """快速检查 Playwright 浏览器"""
    try:
        success, message, fixable = await environment_checker.check_playwright_browser()
        return {
            'success': success,
            'message': message,
            'fixable': fixable
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/redis")
async def check_redis() -> Dict[str, Any]:
    """快速检查 Redis 连接"""
    try:
        success, message, fixable = await environment_checker.check_redis_connection()
        return {
            'success': success,
            'message': message,
            'fixable': fixable
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/network")
async def check_network() -> Dict[str, Any]:
    """快速检查网络连通性"""
    try:
        success, message, fixable = await environment_checker.check_network_connectivity()
        return {
            'success': success,
            'message': message,
            'fixable': fixable
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/ports")
async def check_ports() -> Dict[str, Any]:
    """快速检查端口占用"""
    try:
        success, message, fixable = await environment_checker.check_ports()
        return {
            'success': success,
            'message': message,
            'fixable': fixable
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
