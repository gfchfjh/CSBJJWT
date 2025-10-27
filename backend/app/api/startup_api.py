"""
启动检测相关API
✅ P0-2优化: 提供环境检测和自动修复接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
from ..utils.startup_checker import startup_checker
from ..utils.logger import logger


router = APIRouter(prefix="/api/startup", tags=["startup"])


class AutoFixRequest(BaseModel):
    """自动修复请求"""
    checks: Dict[str, Any]


class ChromiumDownloadResponse(BaseModel):
    """Chromium下载响应"""
    download_id: str
    message: str


@router.get("/check-all")
async def check_all_environment():
    """
    检查所有环境依赖
    
    Returns:
        {
            'overall_status': 'ok' | 'warning' | 'error',
            'checks': {...},
            'auto_fixable': bool,
            'recommendations': [...]
        }
    """
    try:
        results = await startup_checker.check_all()
        return results
    except Exception as e:
        logger.error(f"环境检测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-chromium")
async def check_chromium():
    """
    检查Chromium是否已安装
    
    Returns:
        {
            'installed': bool,
            'path': str | None,
            'message': str
        }
    """
    try:
        from playwright.sync_api import sync_playwright
        
        try:
            with sync_playwright() as p:
                executable_path = p.chromium.executable_path
                
                import os
                if os.path.exists(executable_path):
                    return {
                        'installed': True,
                        'path': executable_path,
                        'message': 'Chromium已安装'
                    }
                else:
                    return {
                        'installed': False,
                        'path': None,
                        'message': 'Chromium未安装，需要下载'
                    }
        except Exception as e:
            return {
                'installed': False,
                'path': None,
                'message': f'Chromium检测失败: {str(e)}'
            }
            
    except ImportError:
        raise HTTPException(status_code=500, detail="Playwright未安装")


@router.post("/download-chromium")
async def download_chromium():
    """
    下载Chromium浏览器
    
    Returns:
        {
            'download_id': str,
            'message': str
        }
    """
    import uuid
    download_id = str(uuid.uuid4())
    
    # 后台下载任务
    asyncio.create_task(_download_chromium_task(download_id))
    
    return {
        'download_id': download_id,
        'message': '开始下载Chromium'
    }


# 下载进度存储
_download_progress = {}


async def _download_chromium_task(download_id: str):
    """后台下载Chromium任务"""
    try:
        _download_progress[download_id] = {'progress': 0, 'status': 'downloading'}
        
        # 使用Playwright CLI下载
        import sys
        process = await asyncio.create_subprocess_exec(
            sys.executable, '-m', 'playwright', 'install', 'chromium',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 模拟进度（实际应该解析stdout）
        for i in range(0, 101, 10):
            _download_progress[download_id]['progress'] = i
            await asyncio.sleep(2)
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            _download_progress[download_id] = {'progress': 100, 'status': 'completed'}
            logger.info("✅ Chromium下载完成")
        else:
            _download_progress[download_id] = {
                'progress': 0,
                'status': 'failed',
                'error': stderr.decode()
            }
            logger.error(f"❌ Chromium下载失败: {stderr.decode()}")
            
    except Exception as e:
        _download_progress[download_id] = {
            'progress': 0,
            'status': 'failed',
            'error': str(e)
        }
        logger.error(f"Chromium下载异常: {str(e)}")


@router.get("/download-progress/{download_id}")
async def get_download_progress(download_id: str):
    """
    获取Chromium下载进度
    
    Returns:
        {
            'progress': int (0-100),
            'status': 'downloading' | 'completed' | 'failed',
            'error': str | None
        }
    """
    if download_id not in _download_progress:
        raise HTTPException(status_code=404, detail="下载任务不存在")
    
    return _download_progress[download_id]


@router.post("/start-redis")
async def start_redis():
    """
    启动Redis服务
    
    Returns:
        {
            'success': bool,
            'message': str
        }
    """
    try:
        # 尝试启动Redis
        from ..queue.redis_client import redis_queue
        
        # 检查Redis是否已运行
        try:
            redis_queue.redis_client.ping()
            return {
                'success': True,
                'message': 'Redis已在运行中'
            }
        except:
            pass
        
        # 启动Redis
        import subprocess
        import platform
        
        redis_path = None
        system = platform.system().lower()
        
        if system == 'windows':
            redis_path = 'redis/redis-server.exe'
        else:
            redis_path = 'redis/redis-server'
        
        import os
        if not os.path.exists(redis_path):
            raise Exception("未找到Redis可执行文件")
        
        if system == 'windows':
            subprocess.Popen([redis_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen([redis_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 等待启动
        await asyncio.sleep(2)
        
        # 验证
        redis_queue.redis_client.ping()
        
        return {
            'success': True,
            'message': 'Redis启动成功'
        }
        
    except Exception as e:
        logger.error(f"Redis启动失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Redis启动失败: {str(e)}")


@router.post("/auto-fix")
async def auto_fix_environment(request: AutoFixRequest):
    """
    自动修复环境问题
    
    Request Body:
        {
            'checks': {...}  # check_all()的返回结果
        }
    
    Returns:
        {
            'fixed': [...],
            'failed': [...],
            'skipped': [...]
        }
    """
    try:
        results = await startup_checker.auto_fix(request.dict())
        return results
    except Exception as e:
        logger.error(f"自动修复失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    健康检查（简化版）
    
    Returns:
        {
            'status': 'ok' | 'error',
            'timestamp': str
        }
    """
    from datetime import datetime
    
    return {
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }
