"""
账号管理API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
from ..database import db
from ..utils.crypto import crypto_manager
from ..kook.scraper import scraper_manager
from ..queue.redis_client import redis_queue


router = APIRouter(prefix="/api/accounts", tags=["accounts"])


class AccountCreate(BaseModel):
    email: str
    password: Optional[str] = None
    cookie: Optional[str] = None


class AccountResponse(BaseModel):
    id: int
    email: str
    status: str
    last_active: Optional[str]
    created_at: str


@router.get("/", response_model=List[AccountResponse])
async def get_accounts():
    """获取所有账号"""
    accounts = db.get_accounts()
    return accounts


@router.post("/", response_model=AccountResponse)
async def add_account(account: AccountCreate):
    """添加账号"""
    # 加密密码
    password_encrypted = None
    if account.password:
        password_encrypted = crypto_manager.encrypt(account.password)
    
    # 添加到数据库
    account_id = db.add_account(
        email=account.email,
        password_encrypted=password_encrypted,
        cookie=account.cookie
    )
    
    # 返回账号信息
    accounts = db.get_accounts()
    new_account = next((a for a in accounts if a['id'] == account_id), None)
    
    if not new_account:
        raise HTTPException(status_code=500, detail="添加账号失败")
    
    return new_account


@router.delete("/{account_id}")
async def delete_account(account_id: int):
    """删除账号"""
    # 停止抓取器
    await scraper_manager.stop_scraper(account_id)
    
    # 从数据库删除
    db.delete_account(account_id)
    
    return {"message": "账号已删除"}


@router.post("/{account_id}/start")
async def start_account(account_id: int):
    """启动账号抓取器"""
    # 获取账号信息
    accounts = db.get_accounts()
    account = next((a for a in accounts if a['id'] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    # 解密密码
    password = None
    if account.get('password_encrypted'):
        password = crypto_manager.decrypt(account['password_encrypted'])
    
    # 消息回调函数
    async def message_callback(message):
        await redis_queue.enqueue(message)
    
    # 启动抓取器
    success = await scraper_manager.start_scraper(
        account_id=account_id,
        cookie=account.get('cookie'),
        email=account.get('email'),
        password=password,
        message_callback=message_callback
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="启动抓取器失败")
    
    return {"message": "抓取器已启动"}


@router.post("/{account_id}/stop")
async def stop_account(account_id: int):
    """停止账号抓取器"""
    success = await scraper_manager.stop_scraper(account_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="抓取器不存在")
    
    return {"message": "抓取器已停止"}


class CaptchaInput(BaseModel):
    code: str


@router.get("/{account_id}/captcha")
async def get_captcha_status(account_id: int):
    """获取验证码状态"""
    captcha_data = db.get_system_config(f"captcha_required_{account_id}")
    
    if not captcha_data:
        return {"required": False}
    
    try:
        data = json.loads(captcha_data)
        return {
            "required": True,
            "image_url": data.get("image_url"),
            "timestamp": data.get("timestamp")
        }
    except:
        return {"required": False}


@router.post("/{account_id}/captcha")
async def submit_captcha(account_id: int, captcha: CaptchaInput):
    """提交验证码"""
    # 保存用户输入的验证码
    db.set_system_config(
        f"captcha_input_{account_id}",
        json.dumps({
            "code": captcha.code,
            "timestamp": "now"
        })
    )
    
    return {"message": "验证码已提交"}


@router.get("/{account_id}/servers")
async def get_servers(account_id: int):
    """获取账号的服务器列表"""
    # 获取抓取器实例
    scraper = scraper_manager.scrapers.get(account_id)
    
    if not scraper:
        raise HTTPException(status_code=404, detail="账号未启动或不存在")
    
    # 获取服务器列表
    servers = await scraper.get_servers()
    
    return {"servers": servers}


@router.get("/{account_id}/servers/{server_id}/channels")
async def get_channels(account_id: int, server_id: str):
    """获取指定服务器的频道列表"""
    # 获取抓取器实例
    scraper = scraper_manager.scrapers.get(account_id)
    
    if not scraper:
        raise HTTPException(status_code=404, detail="账号未启动或不存在")
    
    # 获取频道列表
    channels = await scraper.get_channels(server_id)
    
    return {"channels": channels}
