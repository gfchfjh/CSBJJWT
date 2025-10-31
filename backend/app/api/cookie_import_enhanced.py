"""
Cookie导入API增强版
版本: v6.0.0
作者: KOOK Forwarder Team

新增功能:
1. 增强Cookie解析（10+种格式）
2. 自动错误修复
3. 实时验证
4. 详细错误提示
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from ..utils.cookie_parser_enhanced import cookie_parser_enhanced
from ..utils.auth import verify_api_token
from ..utils.logger import logger

router = APIRouter(prefix="/api/cookie-enhanced", tags=["Cookie增强"])


class CookieImportRequest(BaseModel):
    """Cookie导入请求"""
    cookie: str
    validate_only: bool = False  # 仅验证，不保存


class CookieImportResponse(BaseModel):
    """Cookie导入响应"""
    success: bool
    cookies: Optional[List[Dict]] = None
    cookie_count: int = 0
    format_detected: Optional[str] = None
    auto_fixes: List[str] = []
    warnings: List[str] = []
    valid: bool = False
    validation_message: str = ""
    error: Optional[str] = None
    suggestions: List[str] = []


@router.post("/parse", response_model=CookieImportResponse)
async def parse_cookie_enhanced(
    request: CookieImportRequest,
    token: str = Depends(verify_api_token)
):
    """
    解析Cookie（增强版）
    
    支持格式:
    1. JSON数组: [{"name": "...", "value": "..."}]
    2. JSON对象: {"cookie1": "value1"}
    3. Netscape格式
    4. HTTP Header: Cookie: name=value
    5. 键值对行: name=value\\nname2=value2
    6. JavaScript: document.cookie = "..."
    7. Python字典: {'name': 'value'}
    8. EditThisCookie格式
    9. 单行: name=value
    10. 其他自动识别格式
    
    自动修复:
    - 单引号转双引号
    - 移除尾随逗号
    - Python关键字转换
    - BOM标记移除
    - 等等...
    """
    try:
        cookie_str = request.cookie
        
        if not cookie_str or not cookie_str.strip():
            return CookieImportResponse(
                success=False,
                error="Cookie为空",
                suggestions=[
                    "请粘贴从浏览器导出的Cookie",
                    "推荐使用Chrome扩展一键导出"
                ]
            )
        
        # 解析Cookie
        try:
            cookies = cookie_parser_enhanced.parse(cookie_str)
        except ValueError as e:
            logger.error(f"Cookie解析失败: {str(e)}")
            return CookieImportResponse(
                success=False,
                error=str(e),
                suggestions=[
                    "请检查Cookie格式是否正确",
                    "支持的格式：JSON数组、JSON对象、Netscape、HTTP Header等",
                    "推荐使用Chrome扩展一键导出：更准确、更方便",
                    "或查看教程：如何手动导出Cookie"
                ]
            )
        
        # 验证Cookie
        valid, validation_message = cookie_parser_enhanced.validate(cookies)
        
        # 获取解析信息
        parse_info = cookie_parser_enhanced.get_parse_info()
        
        response = CookieImportResponse(
            success=True,
            cookies=cookies if not request.validate_only else None,
            cookie_count=len(cookies),
            format_detected="auto",
            auto_fixes=parse_info['fixes'],
            warnings=parse_info['warnings'],
            valid=valid,
            validation_message=validation_message
        )
        
        # 如果仅验证，不保存
        if request.validate_only:
            logger.info(f"Cookie验证完成: {len(cookies)}个, 有效={valid}")
        
        return response
        
    except Exception as e:
        logger.error(f"Cookie导入API异常: {str(e)}")
        return CookieImportResponse(
            success=False,
            error=f"服务器错误: {str(e)}",
            suggestions=["请稍后重试或联系支持"]
        )


@router.post("/validate")
async def validate_cookie(
    request: CookieImportRequest,
    token: str = Depends(verify_api_token)
):
    """
    仅验证Cookie（不保存）
    """
    request.validate_only = True
    return await parse_cookie_enhanced(request, token)


@router.get("/supported-formats")
async def get_supported_formats():
    """
    获取支持的Cookie格式列表
    """
    return {
        "formats": [
            {
                "name": "JSON数组",
                "description": '[{"name": "...", "value": "..."}]',
                "example": '[{"name": "session", "value": "abc123", "domain": ".kookapp.cn"}]',
                "recommended": True
            },
            {
                "name": "JSON对象",
                "description": '{"cookie1": "value1", "cookie2": "value2"}',
                "example": '{"session": "abc123", "token": "xyz789"}',
                "recommended": False
            },
            {
                "name": "HTTP Cookie头",
                "description": 'Cookie: name1=value1; name2=value2',
                "example": 'Cookie: session=abc123; token=xyz789',
                "recommended": False
            },
            {
                "name": "Netscape格式",
                "description": '浏览器导出格式（Tab分隔）',
                "example": '.kookapp.cn\tTRUE\t/\tTRUE\t1735660800\tsession\tabc123',
                "recommended": False
            },
            {
                "name": "键值对行",
                "description": 'name=value（每行一个）',
                "example": 'session=abc123\ntoken=xyz789',
                "recommended": False
            }
        ],
        "auto_fixes": [
            "单引号转双引号",
            "移除尾随逗号",
            "Python关键字转换（True/False/None）",
            "BOM标记移除",
            "URL解码",
            "空白字符清理"
        ],
        "tips": [
            "推荐使用Chrome扩展一键导出（准确率100%）",
            "确保Cookie包含完整的登录信息",
            "Cookie通常有效期7-30天，过期后需重新导出",
            "不要将Cookie分享给他人（包含登录凭证）"
        ]
    }


@router.get("/chrome-extension")
async def get_chrome_extension_info():
    """
    获取Chrome扩展信息
    """
    return {
        "name": "KOOK Cookie导出工具",
        "version": "1.0.0",
        "description": "一键导出KOOK Cookie到剪贴板",
        "install_url": "https://github.com/gfchfjh/CSBJJWT/releases/download/v6.0.0/kook-cookie-exporter.zip",
        "install_steps": [
            "1. 下载扩展压缩包",
            "2. 解压到任意目录",
            "3. 打开Chrome，访问 chrome://extensions/",
            "4. 打开右上角的\"开发者模式\"",
            "5. 点击\"加载已解压的扩展程序\"",
            "6. 选择解压后的文件夹",
            "7. 完成安装！"
        ],
        "usage_steps": [
            "1. 打开KOOK网页版并登录",
            "2. 点击浏览器工具栏的扩展图标 🍪",
            "3. 点击\"导出Cookie到剪贴板\"",
            "4. 在软件中粘贴Cookie（Ctrl+V）",
            "5. 点击\"验证并添加\""
        ],
        "features": [
            "✅ 一键导出Cookie到剪贴板",
            "✅ 自动验证Cookie有效性",
            "✅ 智能识别当前页面",
            "✅ 显示Cookie数量和状态",
            "✅ 使用统计（导出次数等）",
            "✅ 现代化UI设计"
        ]
    }
