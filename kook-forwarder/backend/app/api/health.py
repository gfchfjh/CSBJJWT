"""
健康检查API
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from ..utils.health import health_checker
from ..utils.auth import verify_api_token

router = APIRouter(prefix="/api/health", tags=["健康检查"])


@router.get("/check", dependencies=[Depends(verify_api_token)])
async def perform_health_check() -> Dict[str, Any]:
    """
    执行完整健康检查
    """
    result = await health_checker.perform_health_check()
    return {
        "success": True,
        "data": result
    }


@router.get("/status", dependencies=[Depends(verify_api_token)])
async def get_health_status() -> Dict[str, Any]:
    """
    获取最后一次健康检查结果
    """
    result = health_checker.get_last_results()
    return {
        "success": True,
        "data": result
    }


@router.post("/check-bot/{bot_id}", dependencies=[Depends(verify_api_token)])
async def check_single_bot(bot_id: int) -> Dict[str, Any]:
    """
    检查单个Bot的健康状态
    """
    from ..database import db
    
    try:
        bot = db.get_bot_configs()
        bot_config = next((b for b in bot if b['id'] == bot_id), None)
        
        if not bot_config:
            return {
                "success": False,
                "message": "Bot不存在"
            }
        
        platform = bot_config['platform']
        config = bot_config['config']
        
        if platform == 'discord':
            result = await health_checker.check_discord_webhook(config.get('webhook_url'))
        elif platform == 'telegram':
            result = await health_checker.check_telegram_bot(config.get('token'))
        elif platform == 'feishu':
            result = await health_checker.check_feishu_app(
                config.get('app_id'),
                config.get('app_secret')
            )
        else:
            return {
                "success": False,
                "message": f"不支持的平台: {platform}"
            }
        
        return {
            "success": True,
            "data": result
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
