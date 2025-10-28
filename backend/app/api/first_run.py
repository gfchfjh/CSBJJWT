"""
首次运行检测API
检查系统是否首次启动，引导用户进入配置向导
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
from ..database import db
from ..utils.logger import logger

router = APIRouter(prefix="/api/first-run", tags=["首次运行"])


class FirstRunStatus(BaseModel):
    """首次运行状态"""
    is_first_run: bool
    has_accounts: bool
    has_bots: bool
    has_mappings: bool
    needs_setup: bool
    setup_progress: int  # 0-100


@router.get("/check", response_model=FirstRunStatus)
async def check_first_run():
    """
    检查是否首次启动
    
    判断标准：
    1. 没有账号 → 需要配置
    2. 没有Bot → 需要配置
    3. 没有映射 → 需要配置
    
    Returns:
        首次运行状态信息
    """
    try:
        # 检查账号
        accounts = db.get_accounts()
        has_accounts = len(accounts) > 0
        
        # 检查Bot配置
        bots = db.get_bot_configs()
        has_bots = len(bots) > 0
        
        # 检查频道映射
        mappings = db.get_channel_mappings()
        has_mappings = len(mappings) > 0
        
        # 判断是否首次运行
        is_first_run = not (has_accounts and has_bots and has_mappings)
        
        # 计算设置进度
        setup_progress = 0
        if has_accounts:
            setup_progress += 33
        if has_bots:
            setup_progress += 33
        if has_mappings:
            setup_progress += 34
        
        # 判断是否需要设置
        needs_setup = setup_progress < 100
        
        logger.info(
            f"首次运行检测: is_first_run={is_first_run}, "
            f"accounts={len(accounts)}, bots={len(bots)}, "
            f"mappings={len(mappings)}, progress={setup_progress}%"
        )
        
        return FirstRunStatus(
            is_first_run=is_first_run,
            has_accounts=has_accounts,
            has_bots=has_bots,
            has_mappings=has_mappings,
            needs_setup=needs_setup,
            setup_progress=setup_progress
        )
        
    except Exception as e:
        logger.error(f"首次运行检测失败: {e}")
        # 出错时默认认为需要设置
        return FirstRunStatus(
            is_first_run=True,
            has_accounts=False,
            has_bots=False,
            has_mappings=False,
            needs_setup=True,
            setup_progress=0
        )


@router.post("/mark-completed")
async def mark_setup_completed():
    """
    标记设置已完成
    
    在用户完成配置向导后调用
    """
    try:
        # 写入标记到系统配置
        db.set_config("setup_completed", "true")
        db.set_config("setup_completed_at", str(datetime.now()))
        
        logger.info("用户已完成首次设置")
        
        return {
            "success": True,
            "message": "设置已完成"
        }
        
    except Exception as e:
        logger.error(f"标记设置完成失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/setup-guide")
async def get_setup_guide() -> Dict[str, Any]:
    """
    获取设置指南
    
    返回当前应该进行的下一步设置
    """
    try:
        # 检查当前状态
        accounts = db.get_accounts()
        bots = db.get_bot_configs()
        mappings = db.get_channel_mappings()
        
        # 确定下一步
        if len(accounts) == 0:
            next_step = {
                "step": 1,
                "title": "连接KOOK账号",
                "description": "首先需要添加您的KOOK账号",
                "action": "goto_accounts",
                "url": "/accounts"
            }
        elif len(bots) == 0:
            next_step = {
                "step": 2,
                "title": "配置转发Bot",
                "description": "添加Discord/Telegram/飞书Bot",
                "action": "goto_bots",
                "url": "/bots"
            }
        elif len(mappings) == 0:
            next_step = {
                "step": 3,
                "title": "设置频道映射",
                "description": "建立KOOK频道到目标平台的映射关系",
                "action": "goto_mapping",
                "url": "/mapping"
            }
        else:
            next_step = {
                "step": 4,
                "title": "配置完成",
                "description": "所有基础配置已完成，可以开始使用了",
                "action": "goto_home",
                "url": "/"
            }
        
        return {
            "success": True,
            "next_step": next_step,
            "progress": {
                "accounts": len(accounts) > 0,
                "bots": len(bots) > 0,
                "mappings": len(mappings) > 0
            }
        }
        
    except Exception as e:
        logger.error(f"获取设置指南失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


from datetime import datetime
