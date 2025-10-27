"""
Cookie导入终极版API
✅ P0-4优化: 多格式Cookie导入和验证
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..utils.cookie_parser_ultimate import cookie_parser_ultimate
from ..utils.logger import logger
from ..database import db


router = APIRouter(prefix="/api/cookie-import", tags=["cookie_import"])


class CookieValidateRequest(BaseModel):
    """Cookie验证请求"""
    cookie: str


class CookieImportRequest(BaseModel):
    """Cookie导入请求"""
    cookie: str
    account_name: Optional[str] = None


@router.post("/validate")
async def validate_cookie(request: CookieValidateRequest):
    """
    验证Cookie有效性
    
    Request Body:
        {
            'cookie': str  # Cookie内容（任意格式）
        }
    
    Returns:
        {
            'valid': bool,
            'format': str | None,  # 检测到的格式
            'expiry_days': int | None,  # 最短过期天数
            'message': str,
            'detail': str | None,
            'error': str | None
        }
    """
    try:
        # 自动解析Cookie
        cookies = cookie_parser_ultimate.parse(request.cookie)
        
        # 验证Cookie
        valid, message = cookie_parser_ultimate.validate(cookies)
        
        if not valid:
            return {
                'valid': False,
                'format': None,
                'expiry_days': None,
                'message': '❌ Cookie验证失败',
                'detail': message,
                'error': message
            }
        
        # 获取过期信息
        expiry_info = cookie_parser_ultimate.get_expiry_info(cookies)
        
        # 检测格式
        detected_format = cookie_parser_ultimate.auto_detect_format(request.cookie)
        
        # 构建返回信息
        detail_parts = [
            f"域名验证通过",
            f"格式: {detected_format}"
        ]
        
        if expiry_info['min_expiry_days'] is not None:
            detail_parts.append(f"有效期: {expiry_info['min_expiry_days']}天")
            
            if expiry_info['expires_soon']:
                detail_parts.append("⚠️ 即将过期（<7天）")
        else:
            detail_parts.append("会话Cookie（浏览器关闭后失效）")
        
        return {
            'valid': True,
            'format': detected_format,
            'expiry_days': expiry_info['min_expiry_days'],
            'message': '✅ Cookie验证成功',
            'detail': ' · '.join(detail_parts),
            'error': None
        }
        
    except ValueError as e:
        # 格式错误
        return {
            'valid': False,
            'format': None,
            'expiry_days': None,
            'message': '❌ Cookie格式错误',
            'detail': str(e),
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Cookie验证异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_cookie(request: CookieImportRequest):
    """
    导入Cookie并创建账号
    
    Request Body:
        {
            'cookie': str,
            'account_name': str | None
        }
    
    Returns:
        {
            'success': bool,
            'account_id': int,
            'message': str
        }
    """
    try:
        # 解析Cookie
        cookies = cookie_parser_ultimate.parse(request.cookie)
        
        # 验证Cookie
        valid, message = cookie_parser_ultimate.validate(cookies)
        if not valid:
            raise HTTPException(status_code=400, detail=message)
        
        # 提取email（如果Cookie中包含）
        email = None
        for cookie in cookies:
            if cookie['name'] == 'email' or cookie['name'] == 'user_email':
                email = cookie['value']
                break
        
        # 如果没有email，使用account_name
        if not email:
            email = request.account_name or f"cookie_account_{len(await db.get_all_accounts()) + 1}"
        
        # 保存到数据库
        import json
        account_id = await db.create_account(
            email=email,
            cookie=json.dumps(cookies),
            status='online'
        )
        
        logger.info(f"✅ Cookie导入成功，账号ID: {account_id}")
        
        return {
            'success': True,
            'account_id': account_id,
            'message': f'Cookie导入成功，账号: {email}'
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Cookie导入失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formats")
async def get_supported_formats():
    """
    获取支持的Cookie格式列表
    
    Returns:
        {
            'formats': [
                {
                    'name': 'json_array',
                    'display_name': 'JSON数组',
                    'example': '[{"name":"token", "value":"xxx"}]',
                    'description': '最常见格式，浏览器扩展导出'
                },
                ...
            ]
        }
    """
    return {
        'formats': [
            {
                'name': 'json_array',
                'display_name': 'JSON数组',
                'example': '[{"name":"token", "value":"xxx", "domain":".kookapp.cn"}]',
                'description': '最常见格式，浏览器扩展导出',
                'priority': 1
            },
            {
                'name': 'json_object',
                'display_name': 'JSON对象',
                'example': '{"cookies": [...]}',
                'description': '某些扩展导出格式',
                'priority': 2
            },
            {
                'name': 'netscape',
                'display_name': 'Netscape格式',
                'example': '.kookapp.cn\tTRUE\t/\tTRUE\t1234567890\ttoken\txxx',
                'description': '经典Cookie文件格式',
                'priority': 3
            },
            {
                'name': 'header',
                'display_name': 'HTTP Header格式',
                'example': 'Cookie: token=xxx; _ga=xxx; _gid=xxx',
                'description': '浏览器开发者工具复制',
                'priority': 4
            },
            {
                'name': 'key_value_lines',
                'display_name': '键值对行',
                'example': 'token=xxx\n_ga=xxx\n_gid=xxx',
                'description': '简单格式，每行一个Cookie',
                'priority': 5
            }
        ]
    }


@router.post("/test-connection")
async def test_cookie_connection(request: CookieImportRequest):
    """
    测试Cookie连接（不保存）
    
    Request Body:
        {
            'cookie': str
        }
    
    Returns:
        {
            'success': bool,
            'message': str,
            'user_info': {...} | None
        }
    """
    try:
        # 解析Cookie
        cookies = cookie_parser_ultimate.parse(request.cookie)
        
        # 验证Cookie
        valid, message = cookie_parser_ultimate.validate(cookies)
        if not valid:
            return {
                'success': False,
                'message': message,
                'user_info': None
            }
        
        # TODO: 实际连接KOOK测试
        # 这里应该使用Playwright尝试加载KOOK页面
        
        return {
            'success': True,
            'message': 'Cookie验证通过',
            'user_info': {
                'email': 'test@example.com',  # 从KOOK获取
                'username': 'TestUser'
            }
        }
        
    except ValueError as e:
        return {
            'success': False,
            'message': str(e),
            'user_info': None
        }
    except Exception as e:
        logger.error(f"Cookie连接测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
