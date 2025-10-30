"""
文件安全API - ✅ P0-4优化：文件安全检查和白名单管理
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..utils.logger import logger
from ..processors.file_security import file_security_checker

router = APIRouter(prefix="/api/file-security", tags=["file-security"])


class FileCheckRequest(BaseModel):
    """文件检查请求"""
    filename: str


class WhitelistRequest(BaseModel):
    """白名单操作请求"""
    extension: str
    admin_password: Optional[str] = None


# ============ 文件安全检查接口 ============

@router.post("/check")
async def check_file(request: FileCheckRequest):
    """
    检查文件是否安全
    
    Args:
        request: 文件检查请求
        
    Returns:
        {
            "safe": bool,
            "reason": str,
            "details": Dict,
            "action_required": bool
        }
    """
    try:
        safe, reason, details = file_security_checker.check_file_safe(request.filename)
        
        return {
            "safe": safe,
            "reason": reason,
            "details": details,
            "action_required": not safe and details.get("risk_level") == "dangerous"
        }
    except Exception as e:
        logger.error(f"文件安全检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dangerous-types")
async def get_dangerous_types():
    """
    获取所有危险文件类型
    
    Returns:
        危险文件类型列表
    """
    try:
        return {
            "dangerous_extensions": file_security_checker.get_dangerous_extensions(),
            "total": len(file_security_checker.DANGEROUS_EXTENSIONS)
        }
    except Exception as e:
        logger.error(f"获取危险类型失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_security_statistics():
    """
    获取文件安全统计信息
    
    Returns:
        统计信息
    """
    try:
        stats = file_security_checker.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 白名单管理接口 ============

@router.get("/whitelist")
async def get_whitelist():
    """
    获取白名单列表
    
    Returns:
        白名单扩展名列表
    """
    try:
        return {
            "whitelist": file_security_checker.get_whitelist(),
            "total": len(file_security_checker.user_whitelist)
        }
    except Exception as e:
        logger.error(f"获取白名单失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whitelist/add")
async def add_to_whitelist(request: WhitelistRequest):
    """
    添加扩展名到白名单
    
    Args:
        request: 白名单请求
        
    Returns:
        操作结果
    """
    try:
        success, message = file_security_checker.add_to_whitelist(
            request.extension,
            request.admin_password
        )
        
        if success:
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(status_code=400, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加白名单失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whitelist/remove")
async def remove_from_whitelist(request: WhitelistRequest):
    """
    从白名单移除扩展名
    
    Args:
        request: 白名单请求
        
    Returns:
        操作结果
    """
    try:
        success, message = file_security_checker.remove_from_whitelist(request.extension)
        
        if success:
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(status_code=400, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移除白名单失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
