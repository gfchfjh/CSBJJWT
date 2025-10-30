"""
🔔 P2-2优化: 通知系统API

作者: KOOK Forwarder Team
版本: 11.0.0
日期: 2025-10-28
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from ..utils.notification_manager_ultimate import notification_manager
from ..utils.logger import logger

router = APIRouter(prefix="/api/notifications", tags=["通知系统"])


@router.post("/send")
async def send_notification(
    notification_type: str,
    title: str,
    body: str,
    action: Optional[str] = None
):
    """
    发送通知
    
    Args:
        notification_type: 通知类型（success/warning/error/info）
        title: 标题
        body: 内容
        action: 点击操作（可选）
    """
    try:
        success = notification_manager.send(
            notification_type, title, body, action
        )
        
        return {
            'success': success,
            'message': '通知已发送' if success else '通知已抑制'
        }
    
    except Exception as e:
        logger.error(f"发送通知失败: {str(e)}")
        raise HTTPException(500, f"发送通知失败: {str(e)}")


@router.get("/history")
async def get_history(
    limit: int = 100,
    notification_type: Optional[str] = None
):
    """
    获取通知历史
    
    Args:
        limit: 返回数量限制（默认100）
        notification_type: 过滤类型（可选）
    """
    try:
        history = notification_manager.get_history(limit, notification_type)
        return history
    
    except Exception as e:
        logger.error(f"获取通知历史失败: {str(e)}")
        raise HTTPException(500, f"获取通知历史失败: {str(e)}")


@router.delete("/history")
async def clear_history():
    """清空通知历史"""
    try:
        notification_manager.clear_history()
        return {'success': True, 'message': '通知历史已清空'}
    
    except Exception as e:
        logger.error(f"清空通知历史失败: {str(e)}")
        raise HTTPException(500, f"清空通知历史失败: {str(e)}")


@router.post("/history/{notification_id}/click")
async def mark_clicked(notification_id: int):
    """标记通知为已点击"""
    try:
        notification_manager.mark_as_clicked(notification_id)
        return {'success': True}
    
    except Exception as e:
        logger.error(f"标记通知失败: {str(e)}")
        raise HTTPException(500, f"标记通知失败: {str(e)}")


@router.get("/stats")
async def get_stats():
    """
    获取通知统计
    
    Returns:
        {
            "total": 1000,
            "success": 800,
            "warning": 150,
            "error": 50,
            "info": 0,
            "suppressed": 25,
            "history_count": 100
        }
    """
    try:
        stats = notification_manager.get_stats()
        return stats
    
    except Exception as e:
        logger.error(f"获取通知统计失败: {str(e)}")
        raise HTTPException(500, f"获取通知统计失败: {str(e)}")


@router.get("/settings")
async def get_settings():
    """
    获取通知设置
    
    Returns:
        {
            "enable_success": false,
            "enable_warning": true,
            "enable_error": true,
            "enable_info": true,
            "quiet_start": "22:00",
            "quiet_end": "08:00",
            "enable_quiet_time": true
        }
    """
    try:
        settings = notification_manager.get_settings()
        return settings
    
    except Exception as e:
        logger.error(f"获取通知设置失败: {str(e)}")
        raise HTTPException(500, f"获取通知设置失败: {str(e)}")


@router.post("/settings")
async def update_settings(settings: dict):
    """
    更新通知设置
    
    Body:
    {
        "enable_warning": true,
        "quiet_start": "22:00",
        "quiet_end": "08:00"
    }
    """
    try:
        notification_manager.update_settings(settings)
        return {
            'success': True,
            'message': '通知设置已更新'
        }
    
    except Exception as e:
        logger.error(f"更新通知设置失败: {str(e)}")
        raise HTTPException(500, f"更新通知设置失败: {str(e)}")
