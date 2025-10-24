"""
Cookie导入API - 接收浏览器扩展发送的Cookie
✅ P0-2优化: 支持浏览器扩展直接导入
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from ..utils.logger import logger

router = APIRouter(prefix="/api/cookie-import", tags=["cookie-import"])


class CookieItem(BaseModel):
    """单个Cookie项"""
    name: str
    value: str
    domain: str
    path: str = "/"
    expires: float = None
    httpOnly: bool = False
    secure: bool = False
    sameSite: str = "no_restriction"


@router.post("/")
async def import_cookies(cookies: List[CookieItem], request: Request):
    """
    接收浏览器扩展发送的Cookie
    
    Args:
        cookies: Cookie列表
        request: 请求对象
        
    Returns:
        导入结果
    """
    try:
        # 仅允许本地请求
        client_host = request.client.host
        if client_host not in ['127.0.0.1', 'localhost', '::1']:
            raise HTTPException(
                status_code=403, 
                detail="仅允许本地访问"
            )
        
        if not cookies or len(cookies) == 0:
            raise HTTPException(
                status_code=400,
                detail="Cookie列表为空"
            )
        
        # 验证Cookie
        required_cookies = ['token', 'session']  # KOOK可能需要的关键Cookie
        cookie_names = [c.name for c in cookies]
        
        has_required = any(name in cookie_names for name in required_cookies)
        
        if not has_required:
            logger.warning(f"Cookie中未找到关键字段: {required_cookies}")
        
        # 将Cookie格式化为JSON字符串（用于存储）
        cookie_dict_list = [c.dict() for c in cookies]
        cookie_json = json.dumps(cookie_dict_list)
        
        logger.info(f"成功接收来自浏览器扩展的 {len(cookies)} 个Cookie")
        
        # 返回格式化的Cookie JSON（前端可以直接使用）
        return {
            "success": True,
            "message": f"成功导入 {len(cookies)} 个Cookie",
            "cookie_count": len(cookies),
            "cookie_json": cookie_json,
            "has_required_cookies": has_required,
            "cookie_names": cookie_names[:5]  # 返回前5个Cookie名称
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导入Cookie失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"导入失败: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    健康检查 - 供浏览器扩展检测应用是否运行
    """
    return {
        "status": "ok",
        "message": "KOOK消息转发系统正在运行"
    }
