"""
✅ P0-2优化: KOOK服务器/频道自动发现API
提供自动获取KOOK服务器和频道列表的接口
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..kook.scraper import scraper_manager
from ..kook.server_fetcher import KookServerFetcher, get_servers_and_channels_from_db
from ..database import db
from ..utils.logger import logger
import asyncio


router = APIRouter(prefix="/api/server-discovery", tags=["服务器发现"])


class ServerDiscoveryResponse(BaseModel):
    """服务器发现响应"""
    success: bool
    message: str
    servers: List[Dict] = []


class ChannelInfo(BaseModel):
    """频道信息"""
    id: str
    name: str
    type: str  # text/voice
    category: Optional[str] = ''
    position: int = 0


class ServerInfo(BaseModel):
    """服务器信息"""
    id: str
    name: str
    icon: str = ''
    owner_id: str = ''
    member_count: int = 0
    channels: List[ChannelInfo] = []


@router.post("/fetch/{account_id}", response_model=ServerDiscoveryResponse)
async def fetch_servers_and_channels(
    account_id: int,
    background_tasks: BackgroundTasks
):
    """
    自动获取KOOK服务器和频道列表
    
    Args:
        account_id: 账号ID
        
    Returns:
        服务器和频道列表
        
    流程：
    1. 检查账号是否在线（有活跃的scraper）
    2. 使用scraper的page对象获取服务器/频道
    3. 保存到数据库
    4. 返回结果
    """
    try:
        logger.info(f"[API] 开始获取账号 {account_id} 的服务器/频道列表...")
        
        # 1. 获取账号的scraper
        scraper = scraper_manager.get_scraper(account_id)
        
        if not scraper:
            # 账号未登录，尝试从数据库获取缓存数据
            logger.warning(f"[API] 账号 {account_id} 未登录，尝试从数据库获取缓存数据...")
            cached_data = get_servers_and_channels_from_db(account_id)
            
            if cached_data and cached_data.get('servers'):
                return ServerDiscoveryResponse(
                    success=True,
                    message="从缓存获取服务器/频道列表成功",
                    servers=cached_data['servers']
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="账号未登录且无缓存数据，请先登录KOOK"
                )
        
        if not scraper.page or scraper.page.is_closed():
            raise HTTPException(
                status_code=400,
                detail="浏览器页面未初始化或已关闭"
            )
        
        # 2. 创建服务器获取器
        fetcher = KookServerFetcher(scraper.page)
        
        # 3. 获取所有服务器和频道
        logger.info(f"[API] 正在获取服务器列表...")
        data = await fetcher.fetch_all_servers_and_channels()
        
        if not data or not data.get('servers'):
            # 尝试从数据库获取
            logger.warning("[API] 未获取到新数据，从数据库获取...")
            cached_data = get_servers_and_channels_from_db(account_id)
            
            return ServerDiscoveryResponse(
                success=True,
                message="未获取到新数据，返回缓存数据",
                servers=cached_data.get('servers', [])
            )
        
        # 4. 在后台任务中保存到数据库（不阻塞响应）
        background_tasks.add_task(fetcher.save_to_database, account_id)
        
        logger.info(f"[API] 成功获取 {len(data['servers'])} 个服务器")
        
        return ServerDiscoveryResponse(
            success=True,
            message=f"成功获取 {len(data['servers'])} 个服务器",
            servers=data['servers']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] 获取服务器/频道失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取服务器/频道失败: {str(e)}"
        )


@router.get("/cached/{account_id}", response_model=ServerDiscoveryResponse)
async def get_cached_servers_and_channels(account_id: int):
    """
    从数据库获取缓存的服务器/频道列表
    
    Args:
        account_id: 账号ID
        
    Returns:
        缓存的服务器和频道列表
    """
    try:
        data = get_servers_and_channels_from_db(account_id)
        
        return ServerDiscoveryResponse(
            success=True,
            message=f"获取缓存数据成功，共 {len(data.get('servers', []))} 个服务器",
            servers=data.get('servers', [])
        )
        
    except Exception as e:
        logger.error(f"[API] 获取缓存数据失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取缓存数据失败: {str(e)}"
        )


@router.delete("/cache/{account_id}")
async def clear_cached_servers(account_id: int):
    """
    清除账号的服务器/频道缓存
    
    Args:
        account_id: 账号ID
    """
    try:
        # 删除服务器缓存
        db.execute("DELETE FROM kook_servers WHERE account_id = ?", (account_id,))
        
        # 删除频道缓存
        db.execute("DELETE FROM kook_channels WHERE account_id = ?", (account_id,))
        
        db.commit()
        
        return {
            "success": True,
            "message": "缓存清除成功"
        }
        
    except Exception as e:
        logger.error(f"[API] 清除缓存失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"清除缓存失败: {str(e)}"
        )


@router.get("/refresh/{account_id}", response_model=ServerDiscoveryResponse)
async def refresh_servers_and_channels(
    account_id: int,
    background_tasks: BackgroundTasks
):
    """
    强制刷新服务器/频道列表
    
    先清除缓存，再重新获取
    
    Args:
        account_id: 账号ID
    """
    try:
        # 1. 清除缓存
        await clear_cached_servers(account_id)
        
        # 2. 重新获取
        return await fetch_servers_and_channels(account_id, background_tasks)
        
    except Exception as e:
        logger.error(f"[API] 刷新失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"刷新失败: {str(e)}"
        )


@router.post("/test-fetch")
async def test_fetch_servers():
    """
    测试服务器获取功能（使用第一个在线账号）
    """
    try:
        # 获取第一个在线的账号
        accounts = db.execute(
            "SELECT id FROM accounts WHERE status = 'online' LIMIT 1"
        ).fetchall()
        
        if not accounts:
            return {
                "success": False,
                "message": "没有在线的账号，请先登录"
            }
        
        account_id = accounts[0]['id']
        
        # 获取scraper
        scraper = scraper_manager.get_scraper(account_id)
        
        if not scraper or not scraper.page:
            return {
                "success": False,
                "message": "账号scraper未初始化"
            }
        
        # 创建fetcher并获取数据
        fetcher = KookServerFetcher(scraper.page)
        data = await fetcher.fetch_all_servers_and_channels()
        
        return {
            "success": True,
            "message": f"测试成功，获取到 {len(data.get('servers', []))} 个服务器",
            "data": data
        }
        
    except Exception as e:
        logger.error(f"[API] 测试失败: {str(e)}")
        return {
            "success": False,
            "message": f"测试失败: {str(e)}"
        }
