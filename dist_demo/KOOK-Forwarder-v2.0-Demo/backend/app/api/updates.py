"""
更新检查API
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional
from ..utils.update_checker import update_checker
from ..utils.auth import verify_api_token

router = APIRouter(prefix="/api/updates", tags=["更新检查"])


@router.get("/check", dependencies=[Depends(verify_api_token)])
async def check_for_updates() -> Dict[str, Any]:
    """
    手动检查更新
    """
    result = await update_checker.manual_check()
    
    if result:
        return {
            "success": True,
            "data": result
        }
    else:
        return {
            "success": False,
            "message": "无法检查更新，请稍后重试"
        }


@router.get("/status", dependencies=[Depends(verify_api_token)])
async def get_update_status() -> Dict[str, Any]:
    """
    获取更新检查状态
    """
    status = update_checker.get_status()
    return {
        "success": True,
        "data": status
    }


@router.get("/latest", dependencies=[Depends(verify_api_token)])
async def get_latest_version() -> Dict[str, Any]:
    """
    获取最新版本信息
    """
    version_info = update_checker.get_latest_version_info()
    
    if version_info:
        return {
            "success": True,
            "data": version_info
        }
    else:
        return {
            "success": False,
            "message": "暂无版本信息，请先检查更新"
        }


@router.get("/download/{platform}", dependencies=[Depends(verify_api_token)])
async def get_download_url(platform: str) -> Dict[str, Any]:
    """
    获取指定平台的下载链接
    
    Args:
        platform: windows/macos/linux
    """
    url = update_checker.get_download_url(platform)
    
    if url:
        return {
            "success": True,
            "data": {
                "platform": platform,
                "download_url": url
            }
        }
    else:
        return {
            "success": False,
            "message": f"未找到{platform}平台的下载链接"
        }
