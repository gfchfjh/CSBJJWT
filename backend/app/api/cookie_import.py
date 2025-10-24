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


class ExtensionCookieImport(BaseModel):
    """浏览器扩展Cookie导入（✅ P0-2优化）"""
    cookies: List[Dict[str, Any]]
    source: str = "chrome-extension"
    auto_login: bool = True
    timestamp: int


@router.post("/extension")
async def import_from_extension(data: ExtensionCookieImport, request: Request):
    """
    接收浏览器扩展发送的Cookie并自动登录（✅ P0-2优化）
    
    Args:
        data: 扩展发送的数据
        request: 请求对象
        
    Returns:
        导入和登录结果
    """
    try:
        # 仅允许本地请求
        client_host = request.client.host
        if client_host not in ['127.0.0.1', 'localhost', '::1']:
            raise HTTPException(status_code=403, detail="仅允许本地访问")
        
        logger.info(f"✅ 接收到浏览器扩展Cookie: {len(data.cookies)} 个")
        
        # 格式化Cookie
        cookie_json = json.dumps(data.cookies)
        
        # 如果启用自动登录，创建新账号并登录
        if data.auto_login:
            from ..database import db
            from ..kook.scraper import scraper_manager
            
            # 检查是否已有账号
            accounts = db.get_all_accounts()
            
            if len(accounts) == 0:
                # 创建新账号
                account_id = db.add_account(
                    email="扩展导入账号",  # 临时邮箱
                    cookie=cookie_json,
                    password_encrypted=None
                )
                logger.info(f"✅ 创建新账号: ID={account_id}")
            else:
                # 更新第一个账号的Cookie
                account_id = accounts[0]['id']
                db.update_account_cookie(account_id, cookie_json)
                logger.info(f"✅ 更新账号 {account_id} 的Cookie")
            
            # 启动抓取器（自动登录）
            from ..queue.worker import message_worker
            
            def message_callback(message):
                import asyncio
                from ..queue.redis_client import redis_queue
                asyncio.create_task(redis_queue.enqueue(message))
            
            success = await scraper_manager.start_scraper(
                account_id=account_id,
                cookie=cookie_json,
                message_callback=message_callback
            )
            
            if success:
                return {
                    "success": True,
                    "message": "Cookie导入成功并已自动登录",
                    "account_id": account_id,
                    "cookie_count": len(data.cookies),
                    "auto_login": True
                }
            else:
                return {
                    "success": False,
                    "message": "Cookie导入成功但自动登录失败，请手动启动账号",
                    "account_id": account_id,
                    "cookie_count": len(data.cookies),
                    "auto_login": False
                }
        else:
            # 仅导入，不自动登录
            return {
                "success": True,
                "message": f"成功导入 {len(data.cookies)} 个Cookie",
                "cookie_count": len(data.cookies),
                "cookie_json": cookie_json
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"扩展Cookie导入失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    健康检查 - 供浏览器扩展检测应用是否运行（✅ P0-2优化）
    """
    return {
        "status": "ok",
        "message": "KOOK消息转发系统正在运行",
        "version": "1.17.0",  # 添加版本号
        "ready": True
    }
