"""
选择器配置API
"""
from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, List
from pydantic import BaseModel
from ..utils.selector_manager import selector_manager
from ..utils.auth import verify_api_token

router = APIRouter(prefix="/api/selectors", tags=["选择器配置"])


class SelectorUpdate(BaseModel):
    """选择器更新请求"""
    category: str
    selectors: List[str]


class SelectorAdd(BaseModel):
    """选择器添加请求"""
    category: str
    selector: str
    position: int = 0


class SelectorRemove(BaseModel):
    """选择器删除请求"""
    category: str
    selector: str


class ConfigImport(BaseModel):
    """配置导入请求"""
    config_str: str
    format: str = 'json'


@router.get("/config", dependencies=[Depends(verify_api_token)])
async def get_selector_config() -> Dict[str, Any]:
    """
    获取完整选择器配置
    """
    return {
        "success": True,
        "data": selector_manager.config
    }


@router.get("/category/{category}", dependencies=[Depends(verify_api_token)])
async def get_category_selectors(category: str) -> Dict[str, Any]:
    """
    获取指定类别的选择器
    """
    selectors = selector_manager.get_selectors(category)
    
    if selectors:
        return {
            "success": True,
            "data": {
                "category": category,
                "selectors": selectors
            }
        }
    else:
        # 尝试获取字典类型
        selector_dict = selector_manager.get_selector_dict(category)
        if selector_dict:
            return {
                "success": True,
                "data": {
                    "category": category,
                    "selectors": selector_dict
                }
            }
        
        return {
            "success": False,
            "message": f"类别不存在: {category}"
        }


@router.post("/update", dependencies=[Depends(verify_api_token)])
async def update_selectors(data: SelectorUpdate) -> Dict[str, Any]:
    """
    更新选择器配置
    """
    success = selector_manager.update_selector(data.category, data.selectors)
    
    if success:
        return {
            "success": True,
            "message": "选择器已更新"
        }
    else:
        return {
            "success": False,
            "message": "更新选择器失败"
        }


@router.post("/add", dependencies=[Depends(verify_api_token)])
async def add_selector(data: SelectorAdd) -> Dict[str, Any]:
    """
    添加选择器
    """
    success = selector_manager.add_selector(
        data.category,
        data.selector,
        data.position
    )
    
    if success:
        return {
            "success": True,
            "message": "选择器已添加"
        }
    else:
        return {
            "success": False,
            "message": "添加选择器失败"
        }


@router.post("/remove", dependencies=[Depends(verify_api_token)])
async def remove_selector(data: SelectorRemove) -> Dict[str, Any]:
    """
    删除选择器
    """
    success = selector_manager.remove_selector(data.category, data.selector)
    
    if success:
        return {
            "success": True,
            "message": "选择器已删除"
        }
    else:
        return {
            "success": False,
            "message": "删除选择器失败"
        }


@router.post("/reload", dependencies=[Depends(verify_api_token)])
async def reload_config() -> Dict[str, Any]:
    """
    重新加载配置文件
    """
    success = selector_manager.reload()
    
    if success:
        return {
            "success": True,
            "message": "配置已重新加载"
        }
    else:
        return {
            "success": False,
            "message": "重新加载配置失败"
        }


@router.get("/export", dependencies=[Depends(verify_api_token)])
async def export_config() -> Dict[str, Any]:
    """
    导出配置为JSON
    """
    config_str = selector_manager.export_config()
    
    return {
        "success": True,
        "data": config_str
    }


@router.post("/import", dependencies=[Depends(verify_api_token)])
async def import_config(data: ConfigImport) -> Dict[str, Any]:
    """
    导入配置
    """
    success = selector_manager.import_config(data.config_str, data.format)
    
    if success:
        return {
            "success": True,
            "message": "配置已导入"
        }
    else:
        return {
            "success": False,
            "message": "导入配置失败"
        }


@router.get("/file-info", dependencies=[Depends(verify_api_token)])
async def get_file_info() -> Dict[str, Any]:
    """
    获取配置文件信息
    """
    return {
        "success": True,
        "data": {
            "path": str(selector_manager.config_path),
            "exists": selector_manager.config_path.exists(),
            "last_modified": selector_manager.last_modified.isoformat() if selector_manager.last_modified else None
        }
    }
