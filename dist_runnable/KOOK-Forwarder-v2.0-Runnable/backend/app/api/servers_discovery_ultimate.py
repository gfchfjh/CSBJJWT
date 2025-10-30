"""
服务器自动发现API - 终极版
✅ P0-2优化：使用KOOK官方API获取服务器和频道，不再依赖页面DOM
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..database import db
from ..utils.logger import logger
from ..kook.kook_api_client import get_api_client_from_account, KookAPIClient
import json

router = APIRouter(prefix="/api/servers", tags=["服务器发现"])


class ChannelInfo(BaseModel):
    """频道信息"""
    id: str
    name: str
    type: int  # 1=文字, 2=语音
    topic: Optional[str] = ""
    parent_id: Optional[str] = ""


class ServerInfo(BaseModel):
    """服务器信息"""
    id: str
    name: str
    icon: Optional[str] = ""
    topic: Optional[str] = ""
    channels: List[ChannelInfo]


class ServerDiscoveryResponse(BaseModel):
    """服务器发现响应"""
    success: bool
    servers: List[ServerInfo]
    total_servers: int
    total_channels: int
    message: str


@router.get("/discover/{account_id}", response_model=ServerDiscoveryResponse)
async def discover_servers(account_id: int):
    """
    自动发现账号的所有服务器和频道
    
    ✅ P0-2优化：使用KOOK官方REST API，不再依赖Playwright
    
    Args:
        account_id: 账号ID
        
    Returns:
        服务器和频道的完整列表
    """
    try:
        logger.info(f"开始为账号 {account_id} 发现服务器...")
        
        # 检查账号是否存在
        account = db.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (account_id,)
        ).fetchone()
        
        if not account:
            raise HTTPException(status_code=404, detail=f"账号 {account_id} 不存在")
        
        # 创建API客户端
        try:
            api_client = await get_api_client_from_account(account_id)
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"无法创建API客户端: {str(e)}。请确保Cookie或Token有效。"
            )
        
        # 获取所有服务器和频道
        try:
            async with api_client:
                guilds_data = await api_client.get_all_guilds_with_channels()
            
            # 转换为响应格式
            servers = []
            total_channels = 0
            
            for guild in guilds_data:
                channels = [
                    ChannelInfo(
                        id=ch['id'],
                        name=ch['name'],
                        type=ch['type'],
                        topic=ch.get('topic', ''),
                        parent_id=ch.get('parent_id', '')
                    )
                    for ch in guild['channels']
                ]
                
                servers.append(ServerInfo(
                    id=guild['id'],
                    name=guild['name'],
                    icon=guild.get('icon', ''),
                    topic=guild.get('topic', ''),
                    channels=channels
                ))
                
                total_channels += len(channels)
            
            logger.info(f"✅ 成功发现 {len(servers)} 个服务器，共 {total_channels} 个频道")
            
            # 缓存到数据库（可选，用于离线访问）
            try:
                await cache_servers_to_db(account_id, guilds_data)
            except Exception as e:
                logger.warning(f"缓存服务器数据失败: {str(e)}")
            
            return ServerDiscoveryResponse(
                success=True,
                servers=servers,
                total_servers=len(servers),
                total_channels=total_channels,
                message=f"成功获取 {len(servers)} 个服务器"
            )
            
        except Exception as e:
            logger.error(f"获取服务器列表失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取服务器列表失败: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"服务器发现失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cached/{account_id}")
async def get_cached_servers(account_id: int):
    """
    获取缓存的服务器列表（离线可用）
    
    Args:
        account_id: 账号ID
        
    Returns:
        缓存的服务器列表
    """
    try:
        result = db.execute(
            "SELECT * FROM server_cache WHERE account_id = ? ORDER BY cached_at DESC LIMIT 1",
            (account_id,)
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="没有缓存数据，请先执行服务器发现")
        
        servers_data = json.loads(result['servers_data'])
        
        return {
            "success": True,
            "servers": servers_data,
            "cached_at": result['cached_at'],
            "message": "从缓存加载"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-selection")
async def save_channel_selection(
    account_id: int,
    channels: List[Dict[str, str]]
):
    """
    保存用户选择的频道
    
    Args:
        account_id: 账号ID
        channels: 选中的频道列表
            [
                {
                    "server_id": "服务器ID",
                    "channel_id": "频道ID",
                    "channel_name": "频道名称"
                }
            ]
            
    Returns:
        保存结果
    """
    try:
        # 先删除该账号的旧配置
        db.execute(
            "DELETE FROM account_channels WHERE account_id = ?",
            (account_id,)
        )
        
        # 创建表（如果不存在）
        db.execute("""
            CREATE TABLE IF NOT EXISTS account_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                server_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                channel_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            )
        """)
        
        # 插入新配置
        for channel in channels:
            db.execute(
                """
                INSERT INTO account_channels (account_id, server_id, channel_id, channel_name)
                VALUES (?, ?, ?, ?)
                """,
                (
                    account_id,
                    channel['server_id'],
                    channel['channel_id'],
                    channel['channel_name']
                )
            )
        
        db.commit()
        
        logger.info(f"✅ 为账号 {account_id} 保存了 {len(channels)} 个频道配置")
        
        return {
            "success": True,
            "message": f"成功保存 {len(channels)} 个频道配置"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"保存频道配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/selection/{account_id}")
async def get_channel_selection(account_id: int):
    """
    获取用户已选择的频道
    
    Args:
        account_id: 账号ID
        
    Returns:
        已选择的频道列表
    """
    try:
        results = db.execute(
            "SELECT * FROM account_channels WHERE account_id = ?",
            (account_id,)
        ).fetchall()
        
        channels = [
            {
                "server_id": row['server_id'],
                "channel_id": row['channel_id'],
                "channel_name": row['channel_name']
            }
            for row in results
        ]
        
        return {
            "success": True,
            "channels": channels,
            "count": len(channels)
        }
        
    except Exception as e:
        logger.error(f"获取频道配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def cache_servers_to_db(account_id: int, servers_data: List[Dict]):
    """
    缓存服务器数据到数据库
    
    Args:
        account_id: 账号ID
        servers_data: 服务器数据
    """
    try:
        # 创建缓存表（如果不存在）
        db.execute("""
            CREATE TABLE IF NOT EXISTS server_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                servers_data TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            )
        """)
        
        # 删除旧缓存
        db.execute(
            "DELETE FROM server_cache WHERE account_id = ?",
            (account_id,)
        )
        
        # 插入新缓存
        db.execute(
            "INSERT INTO server_cache (account_id, servers_data) VALUES (?, ?)",
            (account_id, json.dumps(servers_data, ensure_ascii=False))
        )
        
        db.commit()
        logger.info(f"✅ 缓存服务器数据成功")
        
    except Exception as e:
        logger.error(f"缓存服务器数据失败: {str(e)}")
        raise


@router.post("/validate-cookie")
async def validate_cookie(cookie: Dict):
    """
    验证Cookie是否有效
    
    Args:
        cookie: Cookie数据（JSON格式）
        
    Returns:
        验证结果
    """
    try:
        # 尝试创建API客户端
        if isinstance(cookie, list):
            # Cookie列表格式 [{"name": "xxx", "value": "yyy"}]
            cookie_dict = {c['name']: c['value'] for c in cookie}
        elif isinstance(cookie, dict):
            cookie_dict = cookie
        else:
            raise HTTPException(status_code=400, detail="Cookie格式错误")
        
        async with KookAPIClient(cookies=cookie_dict) as client:
            # 尝试获取用户信息
            user_info = await client.get_user_me()
            
            return {
                "valid": True,
                "user": {
                    "id": user_info['id'],
                    "username": user_info['username'],
                    "identify_num": user_info.get('identify_num', ''),
                    "avatar": user_info.get('avatar', '')
                },
                "message": "Cookie有效"
            }
            
    except Exception as e:
        logger.error(f"Cookie验证失败: {str(e)}")
        return {
            "valid": False,
            "error": str(e),
            "message": "Cookie无效或已过期"
        }


@router.get("/test-api")
async def test_kook_api():
    """
    测试KOOK API连接
    
    这是一个测试端点，用于验证API客户端是否正常工作
    """
    try:
        # 创建一个测试客户端（无需认证，仅测试连通性）
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.kookapp.cn/api/v3/guild/list') as response:
                status = response.status
                
        return {
            "success": status == 401,  # 401表示API可用但未授权（正常）
            "status_code": status,
            "message": "API连接正常" if status == 401 else "API可能不可用",
            "note": "返回401表示API可用（需要认证）"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "API连接失败"
        }
