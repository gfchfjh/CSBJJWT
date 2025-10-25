"""
Cookie导入API - 接收浏览器扩展发送的Cookie
✅ P0-2优化: 支持浏览器扩展直接导入
✅ P0-3优化: 友好的Cookie验证和错误提示
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from ..utils.logger import logger
from ..utils.cookie_validator_friendly import friendly_cookie_validator

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


class CookieValidateRequest(BaseModel):
    """Cookie验证请求"""
    cookie_string: str


@router.post("/validate")
async def validate_cookie(request: CookieValidateRequest) -> Dict[str, Any]:
    """
    ✅ P0-3优化：验证Cookie并返回友好的错误提示
    
    Args:
        request: Cookie字符串
        
    Returns:
        验证结果，包含友好的错误提示和修复建议
    """
    try:
        result = friendly_cookie_validator.validate_and_explain(request.cookie_string)
        
        logger.info(f"Cookie验证结果: valid={result.get('valid')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Cookie验证异常: {str(e)}")
        return {
            "valid": False,
            "error": "验证过程发生异常",
            "suggestion": "请重新复制Cookie或使用Chrome扩展一键导出",
            "tutorial_link": "/help/cookie-export",
            "details": str(e)
        }


class CookieAutoFixRequest(BaseModel):
    """Cookie自动修复请求"""
    cookie_string: str
    fix_method: str


@router.post("/auto-fix")
async def auto_fix_cookie(request: CookieAutoFixRequest) -> Dict[str, Any]:
    """
    ✅ P0-3优化：尝试自动修复Cookie格式问题
    
    Args:
        request: Cookie字符串和修复方法
        
    Returns:
        修复结果
    """
    try:
        fixed_cookie = friendly_cookie_validator.auto_fix(
            request.cookie_string,
            request.fix_method
        )
        
        if fixed_cookie:
            # 验证修复后的Cookie
            result = friendly_cookie_validator.validate_and_explain(fixed_cookie)
            
            if result["valid"]:
                logger.info("✅ Cookie自动修复成功")
                return {
                    "success": True,
                    "fixed_cookie": fixed_cookie,
                    "message": "Cookie已自动修复并验证通过"
                }
            else:
                logger.warning("⚠️ Cookie修复后仍然无效")
                return {
                    "success": False,
                    "message": "修复后的Cookie仍然无效",
                    "details": result
                }
        else:
            logger.warning("⚠️ Cookie无法自动修复")
            return {
                "success": False,
                "message": "无法自动修复该Cookie格式",
                "suggestion": "请使用Chrome扩展一键导出，可以避免格式问题"
            }
            
    except Exception as e:
        logger.error(f"Cookie自动修复异常: {str(e)}")
        return {
            "success": False,
            "message": f"修复失败: {str(e)}"
        }


@router.get("/help/{topic}")
async def get_cookie_help(topic: str) -> Dict[str, Any]:
    """
    获取Cookie相关帮助信息
    
    支持的主题：
    - export: 如何导出Cookie
    - format: Cookie格式说明
    - troubleshooting: 常见问题排查
    """
    help_content = {
        "export": {
            "title": "如何导出Cookie",
            "methods": [
                {
                    "name": "方法一：使用Chrome扩展（推荐）",
                    "steps": [
                        "安装KOOK Cookie Exporter扩展",
                        "访问并登录KOOK网页版",
                        "点击扩展图标",
                        "点击"导出Cookie"按钮",
                        "Cookie已自动复制到剪贴板"
                    ],
                    "pros": "最简单，不会出错",
                    "difficulty": "简单"
                },
                {
                    "name": "方法二：使用浏览器开发者工具",
                    "steps": [
                        "访问并登录KOOK网页版（www.kookapp.cn）",
                        "按F12打开开发者工具",
                        "切换到"Application"（应用）标签页",
                        "左侧找到"Cookies" → "https://www.kookapp.cn"",
                        "选中所有Cookie，右键"复制"",
                        "粘贴到本应用的Cookie导入框"
                    ],
                    "pros": "无需安装扩展",
                    "difficulty": "中等"
                }
            ],
            "video_tutorial": "/tutorials/cookie-export.mp4"
        },
        "format": {
            "title": "Cookie格式说明",
            "supported_formats": [
                {
                    "name": "JSON数组格式（推荐）",
                    "example": '[{"name":"token","value":"abc123","domain":".kookapp.cn"}]',
                    "description": "最标准的格式，Chrome扩展和开发者工具导出的都是这种格式"
                },
                {
                    "name": "Netscape格式",
                    "example": "token=abc123; domain=.kookapp.cn; path=/",
                    "description": "部分浏览器导出的Cookie文件格式"
                }
            ],
            "required_fields": ["name", "value", "domain"],
            "notes": [
                "Cookie必须包含name、value、domain三个字段",
                "domain必须是.kookapp.cn或kookapp.cn",
                "必须包含认证相关的Cookie（如token、session等）"
            ]
        },
        "troubleshooting": {
            "title": "常见问题排查",
            "issues": [
                {
                    "problem": "提示"Cookie格式不正确"",
                    "causes": [
                        "复制了控制台的输出（包含document.cookie=等代码）",
                        "复制了网页HTML内容",
                        "JSON格式不完整（缺少括号或引号）"
                    ],
                    "solutions": [
                        "使用Chrome扩展一键导出（最简单）",
                        "重新从开发者工具复制，只复制Cookie内容",
                        "使用"自动修复"功能尝试修复格式"
                    ]
                },
                {
                    "problem": "提示"Cookie已过期"",
                    "causes": [
                        "导出的Cookie时间太久",
                        "已在其他设备登出"
                    ],
                    "solutions": [
                        "重新登录KOOK",
                        "导出新的Cookie",
                        "Cookie有效期一般为7-30天"
                    ]
                },
                {
                    "problem": "提示"缺少关键Cookie"",
                    "causes": [
                        "未登录就导出Cookie",
                        "Cookie导出不完整"
                    ],
                    "solutions": [
                        "确保已登录KOOK网页版",
                        "使用Chrome扩展或开发者工具导出完整Cookie",
                        "不要只复制部分Cookie"
                    ]
                }
            ]
        }
    }
    
    if topic not in help_content:
        return {
            "error": "未知的帮助主题",
            "available_topics": list(help_content.keys())
        }
    
    return help_content[topic]
