"""
选择器配置API

提供选择器配置的读取、更新和测试功能
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import yaml
from pathlib import Path
from ..config import settings
from ..utils.logger import logger
from ..utils.selector_manager import selector_manager

router = APIRouter(prefix="/api/selectors", tags=["selectors"])


class SelectorsConfig(BaseModel):
    """选择器配置模型"""
    # 服务器相关
    server_container: List[str] = []
    server_item: List[str] = []
    server_name: List[str] = []
    
    # 频道相关
    channel_container: List[str] = []
    channel_item: List[str] = []
    channel_name: List[str] = []
    
    # 登录相关
    login_email_input: List[str] = []
    login_password_input: List[str] = []
    login_submit_button: List[str] = []
    captcha_input: List[str] = []
    captcha_image: List[str] = []
    
    # 用户信息
    user_panel: List[str] = []
    user_avatar: List[str] = []


@router.get("")
async def get_selectors():
    """
    获取当前选择器配置
    
    Returns:
        选择器配置对象
    """
    try:
        # 从选择器管理器获取配置
        config = selector_manager.get_all_selectors()
        
        return {
            "success": True,
            "data": config
        }
        
    except Exception as e:
        logger.error(f"获取选择器配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def update_selectors(config: SelectorsConfig):
    """
    更新选择器配置
    
    Args:
        config: 新的选择器配置
        
    Returns:
        操作结果
    """
    try:
        # 验证配置
        if not config.server_container or len(config.server_container) == 0:
            raise ValueError("服务器列表容器选择器不能为空")
        
        if not config.server_item or len(config.server_item) == 0:
            raise ValueError("服务器项选择器不能为空")
        
        if not config.channel_container or len(config.channel_container) == 0:
            raise ValueError("频道列表容器选择器不能为空")
        
        if not config.channel_item or len(config.channel_item) == 0:
            raise ValueError("频道项选择器不能为空")
        
        # 构建完整的选择器配置
        selectors_dict = {
            "selectors": {
                "server_container": config.server_container,
                "server_item": config.server_item,
                "server_name": config.server_name,
                "channel_container": config.channel_container,
                "channel_item": config.channel_item,
                "channel_name": config.channel_name,
                "login_email_input": config.login_email_input,
                "login_password_input": config.login_password_input,
                "login_submit_button": config.login_submit_button,
                "captcha_input": config.captcha_input,
                "captcha_image": config.captcha_image,
                "user_panel": config.user_panel,
                "user_avatar": config.user_avatar
            }
        }
        
        # 保存到YAML文件
        config_path = settings.selector_config_path
        
        # 确保目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入YAML文件
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(selectors_dict, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"选择器配置已保存到: {config_path}")
        
        # 重新加载选择器管理器
        selector_manager.reload()
        logger.info("选择器管理器已重新加载")
        
        return {
            "success": True,
            "message": "选择器配置已保存并生效"
        }
        
    except ValueError as e:
        logger.warning(f"选择器配置验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新选择器配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.post("/test")
async def test_selectors(config: SelectorsConfig):
    """
    测试选择器配置
    
    在真实的KOOK页面中测试选择器是否有效
    
    Args:
        config: 要测试的选择器配置
        
    Returns:
        测试结果
    """
    try:
        from playwright.async_api import async_playwright
        
        results = {}
        
        # 启动浏览器测试
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 访问KOOK网页
                await page.goto('https://www.kookapp.cn/app', wait_until='networkidle', timeout=30000)
                
                # 测试每个选择器
                
                # 服务器相关
                results['server_container'] = await _test_selector_list(
                    page, config.server_container, "服务器列表容器"
                )
                results['server_item'] = await _test_selector_list(
                    page, config.server_item, "服务器项"
                )
                results['server_name'] = await _test_selector_list(
                    page, config.server_name, "服务器名称"
                )
                
                # 频道相关
                results['channel_container'] = await _test_selector_list(
                    page, config.channel_container, "频道列表容器"
                )
                results['channel_item'] = await _test_selector_list(
                    page, config.channel_item, "频道项"
                )
                results['channel_name'] = await _test_selector_list(
                    page, config.channel_name, "频道名称"
                )
                
                # 登录相关（可能不存在，因为已登录）
                results['login_email_input'] = await _test_selector_list(
                    page, config.login_email_input, "邮箱输入框", required=False
                )
                results['login_password_input'] = await _test_selector_list(
                    page, config.login_password_input, "密码输入框", required=False
                )
                results['login_submit_button'] = await _test_selector_list(
                    page, config.login_submit_button, "登录按钮", required=False
                )
                
                # 验证码相关（可能不存在）
                results['captcha_input'] = await _test_selector_list(
                    page, config.captcha_input, "验证码输入框", required=False
                )
                results['captcha_image'] = await _test_selector_list(
                    page, config.captcha_image, "验证码图片", required=False
                )
                
                # 用户信息（如果已登录）
                results['user_panel'] = await _test_selector_list(
                    page, config.user_panel, "用户面板", required=False
                )
                results['user_avatar'] = await _test_selector_list(
                    page, config.user_avatar, "用户头像", required=False
                )
                
            finally:
                await page.close()
                await context.close()
                await browser.close()
        
        return {
            "success": True,
            "data": results
        }
        
    except Exception as e:
        logger.error(f"测试选择器失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


async def _test_selector_list(page, selectors: List[str], name: str, required: bool = True) -> Dict[str, Any]:
    """
    测试一组选择器
    
    Args:
        page: Playwright页面对象
        selectors: 选择器列表
        name: 选择器名称
        required: 是否必须找到元素
        
    Returns:
        测试结果字典
    """
    if not selectors or len(selectors) == 0:
        return {
            "success": False,
            "error": "未配置选择器",
            "matched_selector": None
        }
    
    # 依次尝试每个选择器
    for selector in selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                return {
                    "success": True,
                    "matched_selector": selector,
                    "error": None
                }
        except Exception as e:
            logger.debug(f"选择器 {selector} 测试失败: {str(e)}")
            continue
    
    # 所有选择器都失败
    if required:
        return {
            "success": False,
            "error": f"所有选择器均无法找到元素（共{len(selectors)}个）",
            "matched_selector": None
        }
    else:
        return {
            "success": True,  # 非必需元素，找不到也算成功
            "matched_selector": None,
            "error": f"元素不存在（这是正常的，因为{name}可能不显示）"
        }


@router.get("/default")
async def get_default_selectors():
    """
    获取默认选择器配置
    
    Returns:
        默认选择器配置
    """
    default_config = {
        "server_container": [
            ".guild-list",
            "[class*='guild-list']",
            "[class*='GuildList']",
            "[data-guild-list]"
        ],
        "server_item": [
            ".guild-item",
            "[class*='guild-item']",
            "[class*='GuildItem']",
            "[data-guild-id]"
        ],
        "server_name": [
            ".guild-name",
            "[class*='guild-name']",
            "[class*='name']"
        ],
        "channel_container": [
            ".channel-list",
            "[class*='channel-list']",
            "[class*='ChannelList']",
            "nav[class*='channel']"
        ],
        "channel_item": [
            ".channel-item",
            "[class*='channel-item']",
            "[class*='ChannelItem']",
            "[data-channel-id]"
        ],
        "channel_name": [
            ".channel-name",
            "[class*='channel-name']",
            "[class*='name']"
        ],
        "login_email_input": [
            "input[type='email']",
            "input[name='email']",
            "input[placeholder*='邮箱']"
        ],
        "login_password_input": [
            "input[type='password']",
            "input[name='password']"
        ],
        "login_submit_button": [
            "button[type='submit']",
            "button[class*='login']",
            ".login-button"
        ],
        "captcha_input": [
            "input[name='captcha']",
            "input[placeholder*='验证码']",
            ".captcha-input"
        ],
        "captcha_image": [
            "img.captcha-image",
            "img[alt*='验证码']",
            ".captcha-container img"
        ],
        "user_panel": [
            ".user-panel",
            "[data-user-info]",
            ".current-user",
            ".user-avatar"
        ],
        "user_avatar": [
            ".user-avatar img",
            "[class*='avatar'] img",
            ".current-user img"
        ]
    }
    
    return {
        "success": True,
        "data": default_config
    }


@router.post("/reload")
async def reload_selectors():
    """
    重新加载选择器配置
    
    从YAML文件重新加载选择器配置
    
    Returns:
        操作结果
    """
    try:
        selector_manager.reload()
        logger.info("选择器配置已重新加载")
        
        return {
            "success": True,
            "message": "选择器配置已重新加载"
        }
        
    except Exception as e:
        logger.error(f"重新加载选择器配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
