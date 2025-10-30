"""
验证码处理API
✅ P0-4优化：友好的验证码输入界面
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..database import db
from ..utils.logger import logger
import json
import time

router = APIRouter(prefix="/api/captcha", tags=["captcha"])


class CaptchaSubmitRequest(BaseModel):
    """验证码提交请求"""
    account_id: int
    code: str


class CaptchaStatusResponse(BaseModel):
    """验证码状态响应"""
    required: bool
    image_url: Optional[str] = None
    has_2captcha: bool = False
    captcha_balance: float = 0.0
    timestamp: Optional[float] = None


@router.get("/required/{account_id}", response_model=CaptchaStatusResponse)
async def check_captcha_required(account_id: int):
    """
    检查账号是否需要输入验证码
    
    Args:
        account_id: 账号ID
        
    Returns:
        验证码状态信息
    """
    try:
        # 从数据库获取验证码请求信息
        captcha_data = db.get_system_config(f"captcha_required_{account_id}")
        
        if captcha_data:
            try:
                data = json.loads(captcha_data)
                
                # 检查是否配置了2Captcha
                from ..config import settings
                has_2captcha = bool(settings.captcha_2captcha_api_key)
                
                # 获取2Captcha余额（如果已配置）
                balance = 0.0
                if has_2captcha:
                    try:
                        from ..utils.captcha_solver import get_captcha_solver
                        solver = get_captcha_solver()
                        if solver:
                            balance = await solver.get_balance() or 0.0
                    except Exception as e:
                        logger.warning(f"获取2Captcha余额失败: {str(e)}")
                
                return CaptchaStatusResponse(
                    required=True,
                    image_url=data.get("image_url"),
                    has_2captcha=has_2captcha,
                    captcha_balance=balance,
                    timestamp=data.get("timestamp")
                )
            except json.JSONDecodeError:
                logger.error(f"验证码数据格式错误: {captcha_data}")
                return CaptchaStatusResponse(required=False)
        
        return CaptchaStatusResponse(required=False)
        
    except Exception as e:
        logger.error(f"检查验证码状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit")
async def submit_captcha(request: CaptchaSubmitRequest):
    """
    提交验证码
    
    Args:
        request: 包含账号ID和验证码的请求
        
    Returns:
        提交结果
    """
    try:
        # 验证验证码格式（通常4-6位字母数字）
        if not request.code or len(request.code) < 3:
            raise HTTPException(status_code=400, detail="验证码格式不正确")
        
        # 将验证码存储到数据库，供scraper读取
        captcha_input_data = {
            "code": request.code,
            "timestamp": time.time()
        }
        
        db.set_system_config(
            f"captcha_input_{request.account_id}",
            json.dumps(captcha_input_data)
        )
        
        logger.info(f"验证码已提交，账号ID: {request.account_id}")
        
        return {
            "success": True,
            "message": "验证码已提交，请等待验证..."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交验证码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh/{account_id}")
async def refresh_captcha(account_id: int):
    """
    请求刷新验证码（重新获取验证码图片）
    
    Args:
        account_id: 账号ID
        
    Returns:
        刷新结果
    """
    try:
        # 设置刷新标志
        refresh_flag = {
            "refresh": True,
            "timestamp": time.time()
        }
        
        db.set_system_config(
            f"captcha_refresh_{account_id}",
            json.dumps(refresh_flag)
        )
        
        logger.info(f"请求刷新验证码，账号ID: {account_id}")
        
        return {
            "success": True,
            "message": "验证码刷新请求已发送"
        }
        
    except Exception as e:
        logger.error(f"刷新验证码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cancel/{account_id}")
async def cancel_captcha(account_id: int):
    """
    取消验证码输入（用户取消登录）
    
    Args:
        account_id: 账号ID
        
    Returns:
        取消结果
    """
    try:
        # 清除验证码请求和输入数据
        db.delete_system_config(f"captcha_required_{account_id}")
        db.delete_system_config(f"captcha_input_{account_id}")
        db.delete_system_config(f"captcha_refresh_{account_id}")
        
        logger.info(f"已取消验证码输入，账号ID: {account_id}")
        
        return {
            "success": True,
            "message": "已取消验证码输入"
        }
        
    except Exception as e:
        logger.error(f"取消验证码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/2captcha/balance")
async def get_2captcha_balance():
    """
    获取2Captcha账户余额
    
    Returns:
        余额信息
    """
    try:
        from ..config import settings
        
        if not settings.captcha_2captcha_api_key:
            return {
                "configured": False,
                "balance": 0.0,
                "message": "2Captcha未配置"
            }
        
        from ..utils.captcha_solver import get_captcha_solver
        solver = get_captcha_solver()
        
        if not solver:
            return {
                "configured": True,
                "balance": 0.0,
                "message": "2Captcha初始化失败"
            }
        
        balance = await solver.get_balance()
        
        return {
            "configured": True,
            "balance": balance or 0.0,
            "message": "余额获取成功"
        }
        
    except Exception as e:
        logger.error(f"获取2Captcha余额失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
