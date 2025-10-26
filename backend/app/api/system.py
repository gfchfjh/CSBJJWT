"""
系统控制API
✅ P1-1新增：服务启动/停止/重启控制
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
import psutil
from ..utils.logger import logger

router = APIRouter(prefix="/system", tags=["system"])

# 全局服务状态
service_status = {
    "running": False,
    "start_time": None,
    "active_accounts": 0,
    "configured_bots": 0,
    "active_mappings": 0,
}


@router.post("/start")
async def start_service() -> Dict[str, Any]:
    """
    ✅ P1-1新增：启动服务
    """
    try:
        if service_status["running"]:
            return {
                "success": False,
                "message": "服务已在运行中"
            }
        
        # TODO: 实际启动逻辑（启动所有Scraper）
        # 这里需要与 scraper_manager 集成
        
        service_status["running"] = True
        service_status["start_time"] = time.time()
        
        logger.info("✅ 服务已启动")
        
        return {
            "success": True,
            "message": "服务启动成功",
            "start_time": service_status["start_time"]
        }
        
    except Exception as e:
        logger.error(f"❌ 启动服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_service() -> Dict[str, Any]:
    """
    ✅ P1-1新增：停止服务
    """
    try:
        if not service_status["running"]:
            return {
                "success": False,
                "message": "服务未运行"
            }
        
        # TODO: 实际停止逻辑（停止所有Scraper）
        
        service_status["running"] = False
        service_status["start_time"] = None
        
        logger.info("✅ 服务已停止")
        
        return {
            "success": True,
            "message": "服务停止成功"
        }
        
    except Exception as e:
        logger.error(f"❌ 停止服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restart")
async def restart_service() -> Dict[str, Any]:
    """
    ✅ P1-1新增：重启服务
    """
    try:
        # 先停止
        await stop_service()
        
        # 等待一秒
        import asyncio
        await asyncio.sleep(1)
        
        # 再启动
        result = await start_service()
        
        return {
            "success": True,
            "message": "服务重启成功",
            **result
        }
        
    except Exception as e:
        logger.error(f"❌ 重启服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_service_status() -> Dict[str, Any]:
    """
    获取服务状态
    """
    try:
        uptime = None
        if service_status["running"] and service_status["start_time"]:
            uptime = time.time() - service_status["start_time"]
        
        # 获取系统资源使用情况
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            "service_running": service_status["running"],
            "uptime": uptime,
            "active_accounts": service_status["active_accounts"],
            "configured_bots": service_status["configured_bots"],
            "active_mappings": service_status["active_mappings"],
            "queue_size": 0,  # TODO: 从Redis获取
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used": memory.used,
            "memory_total": memory.total,
        }
        
    except Exception as e:
        logger.error(f"❌ 获取状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    健康检查
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    }
