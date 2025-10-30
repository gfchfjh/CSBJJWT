"""
环境检查API - ✅ P0-5优化: 首次启动环境自动检查和配置
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
import subprocess
import os
import asyncio
import time
import uuid
from pathlib import Path
from ..utils.logger import logger
from ..config import settings

router = APIRouter(prefix="/api/system", tags=["environment"])

# 下载进度存储
download_progress_storage: Dict[str, Dict[str, Any]] = {}


@router.get("/check-python")
async def check_python():
    """
    检查Python环境
    
    Returns:
        {
            "installed": bool,
            "version": str,
            "executable": str
        }
    """
    try:
        # 获取Python版本
        version = sys.version
        executable = sys.executable
        
        # 检查版本是否符合要求（3.11+）
        version_info = sys.version_info
        min_version = (3, 11)
        
        is_valid = version_info >= min_version
        
        return {
            "installed": True,
            "version": f"{version_info.major}.{version_info.minor}.{version_info.micro}",
            "executable": executable,
            "is_valid": is_valid,
            "min_version": f"{min_version[0]}.{min_version[1]}"
        }
    except Exception as e:
        logger.error(f"检查Python环境失败: {str(e)}")
        return {
            "installed": False,
            "version": None,
            "executable": None,
            "is_valid": False
        }


@router.get("/check-chromium")
async def check_chromium():
    """
    检查Chromium是否已安装
    
    Returns:
        {
            "installed": bool,
            "path": str,
            "version": str
        }
    """
    try:
        # 检查Playwright Chromium是否已安装
        from playwright.sync_api import sync_playwright
        
        try:
            with sync_playwright() as p:
                # 尝试获取浏览器路径
                browser_type = p.chromium
                # 如果能启动，说明已安装
                browser = browser_type.launch(headless=True)
                browser.close()
                
                return {
                    "installed": True,
                    "path": "playwright-chromium",
                    "version": "latest"
                }
        except Exception:
            # Chromium未安装
            return {
                "installed": False,
                "path": None,
                "version": None
            }
    except ImportError:
        # Playwright未安装
        logger.error("Playwright未安装")
        return {
            "installed": False,
            "path": None,
            "version": None,
            "error": "Playwright未安装"
        }


@router.post("/download-chromium")
async def download_chromium():
    """
    下载Chromium浏览器
    
    Returns:
        {
            "download_id": str,
            "message": str
        }
    """
    try:
        # 生成下载ID
        download_id = str(uuid.uuid4())
        
        # 初始化进度
        download_progress_storage[download_id] = {
            "percentage": 0,
            "speed": "0 KB/s",
            "downloaded_size": "0 MB",
            "total_size": "~ 170 MB",
            "estimated_time": "计算中...",
            "status": "downloading",
            "start_time": time.time()
        }
        
        # 在后台执行下载
        asyncio.create_task(
            _download_chromium_background(download_id)
        )
        
        return {
            "download_id": download_id,
            "message": "开始下载Chromium"
        }
    except Exception as e:
        logger.error(f"启动Chromium下载失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"下载失败: {str(e)}"
        )


async def _download_chromium_background(download_id: str):
    """
    后台下载Chromium
    
    Args:
        download_id: 下载任务ID
    """
    try:
        logger.info(f"开始下载Chromium (ID: {download_id})")
        
        # 使用Playwright安装Chromium
        process = await asyncio.create_subprocess_exec(
            'playwright', 'install', 'chromium',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 模拟进度更新（实际应该解析playwright的输出）
        for i in range(10, 101, 10):
            if download_id in download_progress_storage:
                elapsed = time.time() - download_progress_storage[download_id]['start_time']
                speed = (170 * i / 100) / max(elapsed, 1)  # MB/s
                remaining_mb = 170 * (100 - i) / 100
                remaining_time = remaining_mb / max(speed, 0.1)
                
                download_progress_storage[download_id].update({
                    "percentage": i,
                    "speed": f"{speed:.1f} MB/s",
                    "downloaded_size": f"{(170 * i / 100):.1f} MB",
                    "estimated_time": f"{int(remaining_time)}秒"
                })
                
                await asyncio.sleep(2)  # 模拟下载时间
        
        # 等待进程完成
        await process.wait()
        
        if process.returncode == 0:
            download_progress_storage[download_id].update({
                "percentage": 100,
                "status": "completed",
                "message": "下载完成"
            })
            logger.info(f"Chromium下载完成 (ID: {download_id})")
        else:
            stderr = await process.stderr.read()
            error_msg = stderr.decode()
            download_progress_storage[download_id].update({
                "status": "failed",
                "error": error_msg
            })
            logger.error(f"Chromium下载失败: {error_msg}")
    except Exception as e:
        logger.error(f"Chromium下载异常: {str(e)}")
        if download_id in download_progress_storage:
            download_progress_storage[download_id].update({
                "status": "failed",
                "error": str(e)
            })


@router.get("/download-progress/{download_id}")
async def get_download_progress(download_id: str):
    """
    获取下载进度
    
    Args:
        download_id: 下载任务ID
        
    Returns:
        下载进度信息
    """
    if download_id not in download_progress_storage:
        raise HTTPException(
            status_code=404,
            detail="下载任务不存在"
        )
    
    return download_progress_storage[download_id]


@router.get("/check-redis")
async def check_redis():
    """
    检查Redis是否运行
    
    Returns:
        {
            "running": bool,
            "host": str,
            "port": int
        }
    """
    try:
        from ..queue.redis_client import redis_queue
        
        # 尝试连接Redis
        is_connected = await redis_queue.ping()
        
        return {
            "running": is_connected,
            "host": settings.redis_host,
            "port": settings.redis_port
        }
    except Exception as e:
        logger.error(f"检查Redis失败: {str(e)}")
        return {
            "running": False,
            "host": settings.redis_host,
            "port": settings.redis_port,
            "error": str(e)
        }


@router.post("/start-redis")
async def start_redis():
    """
    启动Redis服务
    
    Returns:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        from ..utils.redis_manager_enhanced import redis_manager
        
        # 尝试启动Redis
        success, message = await redis_manager.start()
        
        if success:
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=message
            )
    except Exception as e:
        logger.error(f"启动Redis失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"启动失败: {str(e)}"
        )


@router.get("/check-network")
async def check_network():
    """
    检查网络连接
    
    Returns:
        {
            "connected": bool,
            "latency": int (ms)
        }
    """
    try:
        import aiohttp
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://www.kookapp.cn',
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    latency = int((time.time() - start_time) * 1000)
                    return {
                        "connected": True,
                        "latency": latency
                    }
                else:
                    return {
                        "connected": False,
                        "latency": None,
                        "error": f"HTTP {response.status}"
                    }
    except asyncio.TimeoutError:
        return {
            "connected": False,
            "latency": None,
            "error": "连接超时"
        }
    except Exception as e:
        logger.error(f"检查网络失败: {str(e)}")
        return {
            "connected": False,
            "latency": None,
            "error": str(e)
        }


@router.get("/environment-summary")
async def get_environment_summary():
    """
    获取环境检查摘要
    
    Returns:
        所有环境检查结果的摘要
    """
    try:
        python_check = await check_python()
        chromium_check = await check_chromium()
        redis_check = await check_redis()
        network_check = await check_network()
        
        # 计算整体状态
        all_ok = (
            python_check.get('installed', False) and
            python_check.get('is_valid', False) and
            chromium_check.get('installed', False) and
            redis_check.get('running', False) and
            network_check.get('connected', False)
        )
        
        return {
            "all_ok": all_ok,
            "python": python_check,
            "chromium": chromium_check,
            "redis": redis_check,
            "network": network_check
        }
    except Exception as e:
        logger.error(f"获取环境摘要失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取摘要失败: {str(e)}"
        )
