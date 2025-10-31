"""
统一配置向导API - 支持3步流程
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..database import db
from ..utils.logger import logger
import json

router = APIRouter(prefix="/api/wizard", tags=["wizard"])


class WizardProgressModel(BaseModel):
    step: int


class ChannelSelection(BaseModel):
    server_id: str
    channel_id: str
    channel_name: str


class WizardCompleteModel(BaseModel):
    account_id: int
    channels: List[ChannelSelection]


@router.get("/progress")
async def get_wizard_progress():
    """
    获取向导进度
    
    Returns:
        向导进度信息
    """
    try:
        # 检查是否已完成
        completed = db.get_config("wizard_completed") == "true"
        
        if completed:
            return {
                "completed": True,
                "step": 3
            }
        
        # 获取当前步骤
        step_str = db.get_config("wizard_step")
        step = int(step_str) if step_str else 1
        
        return {
            "completed": False,
            "step": step
        }
    except Exception as e:
        logger.error(f"获取向导进度失败: {str(e)}")
        return {
            "completed": False,
            "step": 1
        }


@router.post("/progress")
async def save_wizard_progress(progress: WizardProgressModel):
    """
    保存向导进度
    
    Args:
        progress: 进度信息
    """
    try:
        db.set_config("wizard_step", str(progress.step))
        return {"success": True}
    except Exception as e:
        logger.error(f"保存向导进度失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete")
async def complete_wizard(data: WizardCompleteModel):
    """
    完成向导配置
    
    Args:
        data: 完整配置数据
    """
    try:
        # 1. 验证账号存在
        account = db.get_account(data.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="账号不存在")
        
        # 2. 保存频道选择（作为频道映射的基础）
        for channel in data.channels:
            try:
                # 检查是否已存在映射
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id FROM channel_mappings 
                        WHERE kook_channel_id = ? AND enabled = 1
                    """, (channel.channel_id,))
                    result = cursor.fetchone()
                
                if not result:
                    # 创建基础映射（暂时不指定目标，等用户配置Bot后再设置）
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO channel_mappings 
                            (kook_server_id, kook_channel_id, kook_channel_name, 
                             target_platform, target_bot_id, target_channel_id, enabled)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            channel.server_id,
                            channel.channel_id,
                            channel.channel_name,
                            'pending',  # 待配置
                            0,  # 暂无Bot
                            '',  # 暂无目标频道
                            1  # 启用
                        ))
                        conn.commit()
            except Exception as e:
                logger.warning(f"保存频道映射失败: {str(e)}")
                continue
        
        # 3. 标记向导完成
        db.set_config("wizard_completed", "true")
        db.set_config("wizard_completed_at", str(int(time.time())))
        
        # 4. 更新账号状态为已配置
        db.update_account_status(data.account_id, "configured")
        
        logger.info(f"用户完成配置向导，选择了 {len(data.channels)} 个频道")
        
        return {
            "success": True,
            "message": "配置完成",
            "channels_configured": len(data.channels)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"完成向导失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_wizard():
    """
    重置向导（用于重新配置）
    """
    try:
        db.delete_config("wizard_completed")
        db.delete_config("wizard_step")
        db.delete_config("wizard_completed_at")
        
        return {"success": True, "message": "向导已重置"}
    except Exception as e:
        logger.error(f"重置向导失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_wizard_status():
    """
    获取向导状态概览
    """
    try:
        completed = db.get_config("wizard_completed") == "true"
        step = int(db.get_config("wizard_step") or "1")
        
        # 统计配置情况
        accounts_count = len(db.get_accounts())
        bots_count = len(db.get_bot_configs())
        mappings_count = len(db.get_channel_mappings())
        
        return {
            "wizard_completed": completed,
            "current_step": step,
            "statistics": {
                "accounts": accounts_count,
                "bots": bots_count,
                "mappings": mappings_count
            },
            "needs_configuration": {
                "accounts": accounts_count == 0,
                "bots": bots_count == 0,
                "mappings": mappings_count == 0
            }
        }
    except Exception as e:
        logger.error(f"获取向导状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


import time
