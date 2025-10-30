"""
错误翻译API
✅ P0-2优化：友好错误提示系统
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from ..utils.error_translator import (
    translate_error, 
    get_fix_action, 
    get_all_error_types,
    get_errors_by_category,
    ERROR_TRANSLATIONS
)
from ..utils.logger import logger

router = APIRouter(prefix="/api/error-translator", tags=["error-translator"])


class ErrorTranslateRequest(BaseModel):
    """错误翻译请求"""
    technical_error: str
    error_type: Optional[str] = None


class ErrorTranslateResponse(BaseModel):
    """错误翻译响应"""
    title: str
    message: str
    solution: List[str]
    auto_fix: Optional[str] = None
    fix_description: Optional[str] = None
    severity: str
    category: str
    technical_error: str


@router.post("/translate", response_model=ErrorTranslateResponse)
async def translate_error_endpoint(request: ErrorTranslateRequest):
    """
    翻译技术错误为友好提示
    
    Args:
        request: 包含技术错误信息的请求
        
    Returns:
        友好的错误提示
    """
    try:
        # 翻译错误
        translation = translate_error(
            technical_error=request.technical_error,
            error_type=request.error_type
        )
        
        # 获取自动修复描述
        fix_description = None
        if translation.get('auto_fix'):
            fix_description = get_fix_action(translation['auto_fix'])
        
        translation['fix_description'] = fix_description
        
        logger.info(f"错误翻译成功: {translation['title']}")
        
        return translation
        
    except Exception as e:
        logger.error(f"错误翻译失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types", response_model=List[str])
async def get_error_types():
    """获取所有支持的错误类型"""
    return get_all_error_types()


@router.get("/category/{category}", response_model=List[str])
async def get_errors_by_category_endpoint(category: str):
    """
    获取指定类别的错误列表
    
    Args:
        category: 错误类别（environment/service/auth/config/network等）
        
    Returns:
        该类别的所有错误类型
    """
    return get_errors_by_category(category)


@router.get("/info/{error_type}", response_model=Dict[str, Any])
async def get_error_info(error_type: str):
    """
    获取指定错误类型的详细信息
    
    Args:
        error_type: 错误类型
        
    Returns:
        错误详细信息
    """
    if error_type not in ERROR_TRANSLATIONS:
        raise HTTPException(status_code=404, detail=f"未找到错误类型: {error_type}")
    
    error_info = ERROR_TRANSLATIONS[error_type].copy()
    
    # 添加修复描述
    if error_info.get('auto_fix'):
        error_info['fix_description'] = get_fix_action(error_info['auto_fix'])
    
    return error_info


@router.get("/categories", response_model=List[str])
async def get_all_categories():
    """获取所有错误类别"""
    categories = set()
    for error_info in ERROR_TRANSLATIONS.values():
        categories.add(error_info.get('category', 'unknown'))
    
    return sorted(list(categories))
