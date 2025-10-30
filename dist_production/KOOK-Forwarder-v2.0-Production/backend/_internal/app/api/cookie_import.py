"""
Cookie导入API - ✅ P0-2优化完成: 智能Cookie验证+10种错误类型+自动修复
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from ..utils.logger import logger
from ..utils.cookie_validator_friendly import friendly_cookie_validator
from ..utils.cookie_validator_enhanced import cookie_validator  # ✅ P0-2新增

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


class ManualCookieImport(BaseModel):
    """手动Cookie导入请求（✅ P0-2新增）"""
    cookie_data: str  # 可以是JSON、文本、Netscape格式等
    format: Optional[str] = "auto"  # auto, json, netscape, key-value


# ============ ✅ P0-2新增: 智能Cookie验证API ============

@router.post("/validate-enhanced")
async def validate_cookie_enhanced(request: ManualCookieImport):
    """
    ✅ P0-2新增: 智能Cookie验证（10种错误类型+自动修复）
    
    功能：
    1. 自动识别Cookie格式（JSON/Netscape/键值对）
    2. 10种错误类型检测
    3. 自动修复常见错误
    4. 友好的错误提示
    5. 可操作的修复建议
    
    Returns:
        {
            "valid": bool,              # 是否有效
            "cookies": List[Dict],      # 修复后的Cookie列表
            "errors": List[Dict],       # 错误详情
            "auto_fixed": bool,         # 是否自动修复
            "warnings": List[str],      # 警告信息
            "suggestions": List[str],   # 修复建议
            "cookie_count": int,        # Cookie数量
            "format": str               # 识别的格式
        }
    """
    try:
        logger.info(f"✅ P0-2: 开始智能Cookie验证，数据长度: {len(request.cookie_data)}")
        
        # 使用增强验证器
        validation_result = cookie_validator.validate_and_fix(request.cookie_data)
        
        # 添加额外信息
        validation_result["cookie_count"] = len(validation_result["cookies"])
        validation_result["format"] = request.format
        
        # 记录验证结果
        if validation_result["valid"]:
            logger.info(
                f"✅ Cookie验证成功: {validation_result['cookie_count']}条, "
                f"自动修复: {validation_result['auto_fixed']}"
            )
        else:
            logger.warning(
                f"❌ Cookie验证失败: {len(validation_result['errors'])}个错误"
            )
        
        return validation_result
            
    except Exception as e:
        logger.error(f"Cookie验证异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"验证失败: {str(e)}"
        )


@router.post("/import-with-validation")
async def import_cookie_with_validation(request: ManualCookieImport):
    """
    ✅ P0-2新增: 导入Cookie并验证（验证+保存）
    
    Returns:
        {
            "success": bool,
            "account_id": int,
            "validation": Dict,  # 验证结果
            "message": str
        }
    """
    try:
        # 1. 验证Cookie
        validation_result = cookie_validator.validate_and_fix(request.cookie_data)
        
        if not validation_result["valid"]:
            # 验证失败，返回错误详情
            return {
                "success": False,
                "account_id": None,
                "validation": validation_result,
                "message": "Cookie验证失败，请查看错误详情"
            }
        
        # 2. 保存到数据库
        from ..database import db
        from ..utils.crypto import crypto_manager
        
        # 将Cookie列表转为JSON字符串
        cookie_json = json.dumps(validation_result["cookies"])
        
        # 检查是否已有账号
        accounts = db.get_all_accounts()
        
        if len(accounts) == 0:
            # 创建新账号
            account_id = db.add_account(
                email="手动导入账号",
                cookie=cookie_json,
                password_encrypted=None
            )
            logger.info(f"✅ 创建新账号: ID={account_id}")
        else:
            # 更新第一个账号的Cookie
            account_id = accounts[0]['id']
            db.update_account_cookie(account_id, cookie_json)
            logger.info(f"✅ 更新账号 {account_id} 的Cookie")
        
        # 3. 返回结果
        return {
            "success": True,
            "account_id": account_id,
            "validation": validation_result,
            "message": f"✅ Cookie导入成功！{validation_result['suggestions'][0] if validation_result['suggestions'] else ''}"
        }
        
    except Exception as e:
        logger.error(f"导入Cookie失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"导入失败: {str(e)}"
        )


# ============ 原有API（浏览器扩展导入） ============

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
    """浏览器扩展Cookie导入"""
    cookies: List[Dict[str, Any]]
    source: str = "chrome-extension"
    auto_login: bool = True
    timestamp: int


@router.post("/extension")
async def import_from_extension(data: ExtensionCookieImport, request: Request):
    """
    接收浏览器扩展发送的Cookie并自动登录
    
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
                    "message": "✅ Cookie导入成功，正在自动登录KOOK...",
                    "account_id": account_id,
                    "cookie_count": len(data.cookies),
                    "auto_login": True
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Cookie导入成功，但自动登录失败",
                    "account_id": account_id,
                    "cookie_count": len(data.cookies),
                    "auto_login": False
                }
        else:
            # 仅保存Cookie，不自动登录
            return {
                "success": True,
                "message": f"✅ 成功接收 {len(data.cookies)} 个Cookie",
                "cookie_count": len(data.cookies),
                "auto_login": False,
                "cookie_json": cookie_json
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理扩展Cookie失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"处理失败: {str(e)}"
        )


# ============ 友好Cookie验证（原有API） ============

class CookieValidateRequest(BaseModel):
    """Cookie验证请求"""
    cookie_text: str


@router.post("/validate-friendly")
async def validate_cookie_friendly(request: CookieValidateRequest):
    """
    友好的Cookie验证（原有API）
    """
    try:
        result = friendly_cookie_validator.validate(request.cookie_text)
        return result
    except Exception as e:
        logger.error(f"Cookie验证异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"验证失败: {str(e)}"
        )


# ============ ✅ P0-3优化: Chrome扩展自动发送Cookie ============

class AutoImportRequest(BaseModel):
    """✅ P0-3优化: 自动导入请求"""
    cookies: List[Dict]
    source: str = 'chrome-extension'
    extension_version: str = ''
    timestamp: int = 0


@router.post("/auto")
async def auto_import_cookie(request: AutoImportRequest, req: Request):
    """
    ✅ P0-3优化: 自动接收Chrome扩展发送的Cookie
    
    Chrome扩展会尝试POST Cookie到这个端点
    如果成功，Cookie将被保存到临时表，前端可以轮询获取
    
    Args:
        request: Cookie数据
        
    Returns:
        成功响应
    """
    try:
        from ..database import db
        
        logger.info(f"[CookieImport] 收到来自 {request.source} 的Cookie自动导入请求")
        logger.info(f"[CookieImport] IP: {req.client.host}, 扩展版本: {request.extension_version}")
        logger.info(f"[CookieImport] Cookie数量: {len(request.cookies)}")
        
        # 验证Cookie
        if not request.cookies or len(request.cookies) == 0:
            raise HTTPException(status_code=400, detail="Cookie列表为空")
        
        # 保存到临时表（用于前端轮询获取）
        db.execute("""
            CREATE TABLE IF NOT EXISTS cookie_import_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cookies TEXT NOT NULL,
                source TEXT DEFAULT 'chrome-extension',
                extension_version TEXT,
                ip_address TEXT,
                imported BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入Cookie数据
        db.execute("""
            INSERT INTO cookie_import_queue 
            (cookies, source, extension_version, ip_address)
            VALUES (?, ?, ?, ?)
        """, (
            json.dumps(request.cookies),
            request.source,
            request.extension_version,
            req.client.host
        ))
        
        db.commit()
        
        logger.info("[CookieImport] Cookie已保存到导入队列")
        
        return {
            "success": True,
            "message": "Cookie自动导入成功",
            "cookie_count": len(request.cookies),
            "source": request.source
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CookieImport] 自动导入失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/poll")
async def poll_imported_cookies():
    """
    前端轮询检测是否有新导入的Cookie
    
    Returns:
        最新的未导入Cookie数据
    """
    try:
        from ..database import db
        
        # 查询最新的未导入Cookie
        result = db.execute("""
            SELECT id, cookies, source, extension_version, created_at
            FROM cookie_import_queue
            WHERE imported = 0
            ORDER BY created_at DESC
            LIMIT 1
        """).fetchone()
        
        if not result:
            return {
                "has_new": False,
                "message": "没有新的Cookie"
            }
        
        # 解析Cookie
        cookies = json.loads(result['cookies'])
        
        return {
            "has_new": True,
            "cookie_id": result['id'],
            "cookies": cookies,
            "source": result['source'],
            "extension_version": result['extension_version'],
            "created_at": result['created_at']
        }
        
    except Exception as e:
        logger.error(f"[CookieImport] 轮询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"轮询失败: {str(e)}")


@router.post("/confirm/{cookie_id}")
async def confirm_import(cookie_id: int):
    """
    确认导入Cookie
    
    前端在用户确认后调用此接口，标记Cookie已导入
    
    Args:
        cookie_id: Cookie记录ID
    """
    try:
        from ..database import db
        
        db.execute("""
            UPDATE cookie_import_queue
            SET imported = 1
            WHERE id = ?
        """, (cookie_id,))
        
        db.commit()
        
        return {
            "success": True,
            "message": "已确认导入"
        }
        
    except Exception as e:
        logger.error(f"[CookieImport] 确认导入失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"确认失败: {str(e)}")
