"""
服务器/频道自动发现API - 增强版
功能：Cookie导入后自动拉取KOOK服务器和频道列表
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import json
from ..database import db
from ..utils.logger import logger
from ..kook.scraper import scraper_manager

router = APIRouter(prefix="/api/servers", tags=["服务器发现"])


class ChannelInfo(BaseModel):
    """频道信息"""
    id: str
    name: str
    type: int  # 1=文本频道, 2=语音频道
    parent_id: Optional[str] = None
    position: int = 0


class ServerInfo(BaseModel):
    """服务器信息"""
    id: str
    name: str
    icon: Optional[str] = None
    channels: List[ChannelInfo] = []
    member_count: int = 0


class DiscoveryRequest(BaseModel):
    """发现请求"""
    account_id: int
    force_refresh: bool = False


class DiscoveryResponse(BaseModel):
    """发现响应"""
    servers: List[ServerInfo]
    total_servers: int
    total_channels: int
    cached: bool = False


@router.get("/discover", response_model=DiscoveryResponse)
async def discover_servers_and_channels_get(account_id: Optional[int] = None):
    """
    GET方法：自动发现服务器和频道（兼容前端GET调用）
    如果不指定account_id，则使用第一个可用账号
    """
    if account_id is None:
        # 获取第一个账号
        accounts = db.get_all_accounts()
        if not accounts:
            return DiscoveryResponse(servers=[], total_servers=0, total_channels=0)
        account_id = accounts[0]['id']
    
    # 调用POST方法的实现
    return await discover_servers_and_channels_post(DiscoveryRequest(account_id=account_id))


@router.post("/discover", response_model=DiscoveryResponse)
async def discover_servers_and_channels_post(request: DiscoveryRequest):
    """
    POST方法：自动发现账号的所有服务器和频道
    
    工作流程：
    1. 检查账号是否存在且有有效Cookie
    2. 启动Playwright抓取器
    3. 通过JS获取页面中的服务器和频道数据
    4. 缓存到数据库
    5. 返回结构化数据
    """
    try:
        logger.info(f"[ServerDiscovery] 开始发现账号{request.account_id}的服务器...")
        
        # 1. 检查账号
        account = db.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (request.account_id,)
        ).fetchone()
        
        if not account:
            raise HTTPException(404, "账号不存在")
        
        if not account['cookie']:
            raise HTTPException(400, "账号未配置Cookie，请先导入Cookie")
        
        # 2. 检查缓存（如果不强制刷新）
        if not request.force_refresh:
            cached_data = get_cached_servers(request.account_id)
            if cached_data:
                logger.info(f"[ServerDiscovery] 使用缓存数据")
                return DiscoveryResponse(
                    servers=cached_data['servers'],
                    total_servers=len(cached_data['servers']),
                    total_channels=sum(len(s['channels']) for s in cached_data['servers']),
                    cached=True
                )
        
        # 3. 获取或创建抓取器
        scraper = scraper_manager.get_scraper(request.account_id)
        
        if not scraper:
            # 需要启动抓取器
            logger.info(f"[ServerDiscovery] 启动抓取器...")
            await scraper_manager.start_scraper(request.account_id)
            # 等待抓取器启动
            await asyncio.sleep(5)
            scraper = scraper_manager.get_scraper(request.account_id)
        
        if not scraper or not scraper.page:
            raise HTTPException(503, "抓取器未就绪，请稍后重试")
        
        # 4. 从页面获取服务器和频道数据
        servers_data = await extract_servers_from_page(scraper)
        
        if not servers_data:
            raise HTTPException(500, "无法获取服务器数据，请确保已登录KOOK")
        
        # 5. 转换为结构化数据
        servers = []
        for server in servers_data:
            channels = [
                ChannelInfo(
                    id=ch['id'],
                    name=ch['name'],
                    type=ch.get('type', 1),
                    parent_id=ch.get('parent_id'),
                    position=ch.get('position', 0)
                )
                for ch in server.get('channels', [])
            ]
            
            servers.append(ServerInfo(
                id=server['id'],
                name=server['name'],
                icon=server.get('icon'),
                channels=channels,
                member_count=server.get('member_count', 0)
            ))
        
        # 6. 缓存到数据库
        cache_servers_data(request.account_id, servers)
        
        total_channels = sum(len(s.channels) for s in servers)
        
        logger.info(f"[ServerDiscovery] 发现完成: {len(servers)}个服务器, {total_channels}个频道")
        
        return DiscoveryResponse(
            servers=servers,
            total_servers=len(servers),
            total_channels=total_channels,
            cached=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ServerDiscovery] 发现失败: {str(e)}", exc_info=True)
        raise HTTPException(500, f"服务器发现失败: {str(e)}")


async def extract_servers_from_page(scraper) -> List[Dict]:
    """
    从KOOK页面提取服务器和频道数据
    
    通过执行JavaScript获取KOOK应用的内部状态
    """
    try:
        # 执行JS获取服务器数据
        servers_data = await scraper.page.evaluate('''() => {
            // 尝试从KOOK的全局状态获取数据
            // KOOK可能使用Vue或React，数据存储在window对象或DOM中
            
            const servers = [];
            
            // 方法1: 尝试从DOM元素获取
            const serverElements = document.querySelectorAll('[data-server-id], .guild-item, .server-item');
            
            for (const elem of serverElements) {
                const serverId = elem.getAttribute('data-server-id') || 
                                elem.getAttribute('data-guild-id') ||
                                elem.id;
                
                if (!serverId) continue;
                
                const serverName = elem.getAttribute('data-server-name') || 
                                  elem.querySelector('.server-name, .guild-name')?.textContent?.trim() ||
                                  '未知服务器';
                
                const serverIcon = elem.querySelector('img')?.src || null;
                
                // 获取该服务器的频道
                const channels = [];
                const channelElements = elem.querySelectorAll('[data-channel-id], .channel-item');
                
                for (const chElem of channelElements) {
                    const channelId = chElem.getAttribute('data-channel-id') || chElem.id;
                    const channelName = chElem.getAttribute('data-channel-name') ||
                                       chElem.textContent?.trim() || '未知频道';
                    const channelType = parseInt(chElem.getAttribute('data-channel-type') || '1');
                    
                    if (channelId) {
                        channels.push({
                            id: channelId,
                            name: channelName,
                            type: channelType,
                            position: channels.length
                        });
                    }
                }
                
                servers.push({
                    id: serverId,
                    name: serverName,
                    icon: serverIcon,
                    channels: channels,
                    member_count: 0
                });
            }
            
            // 方法2: 尝试从全局变量获取（如果KOOK有暴露）
            if (servers.length === 0 && window.__KOOK_DATA__) {
                // 尝试从KOOK的内部数据结构获取
                const kookData = window.__KOOK_DATA__;
                if (kookData.guilds) {
                    for (const guild of kookData.guilds) {
                        servers.push({
                            id: guild.id,
                            name: guild.name,
                            icon: guild.icon,
                            channels: guild.channels || [],
                            member_count: guild.member_count || 0
                        });
                    }
                }
            }
            
            // 方法3: 从localStorage获取缓存数据
            if (servers.length === 0) {
                try {
                    const cachedGuilds = localStorage.getItem('kook_guilds') || 
                                        localStorage.getItem('guilds');
                    if (cachedGuilds) {
                        const parsed = JSON.parse(cachedGuilds);
                        if (Array.isArray(parsed)) {
                            return parsed.map(g => ({
                                id: g.id,
                                name: g.name,
                                icon: g.icon,
                                channels: g.channels || [],
                                member_count: g.member_count || 0
                            }));
                        }
                    }
                } catch (e) {
                    console.error('Failed to parse cached guilds:', e);
                }
            }
            
            return servers;
        }''')
        
        logger.debug(f"[ServerDiscovery] 从页面提取到 {len(servers_data)} 个服务器")
        
        return servers_data if servers_data else []
        
    except Exception as e:
        logger.error(f"[ServerDiscovery] 提取服务器数据失败: {str(e)}")
        return []


def get_cached_servers(account_id: int) -> Optional[Dict]:
    """从数据库获取缓存的服务器数据"""
    try:
        # 创建缓存表（如果不存在）
        db.execute("""
            CREATE TABLE IF NOT EXISTS server_cache (
                account_id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()
        
        # 查询缓存（24小时内有效）
        result = db.execute("""
            SELECT data FROM server_cache 
            WHERE account_id = ? 
            AND updated_at > datetime('now', '-24 hours')
        """, (account_id,)).fetchone()
        
        if result:
            return json.loads(result['data'])
        
        return None
        
    except Exception as e:
        logger.error(f"[ServerDiscovery] 读取缓存失败: {str(e)}")
        return None


def cache_servers_data(account_id: int, servers: List[ServerInfo]):
    """缓存服务器数据到数据库"""
    try:
        # 转换为可序列化的字典
        data = {
            'servers': [
                {
                    'id': s.id,
                    'name': s.name,
                    'icon': s.icon,
                    'channels': [
                        {
                            'id': ch.id,
                            'name': ch.name,
                            'type': ch.type,
                            'parent_id': ch.parent_id,
                            'position': ch.position
                        }
                        for ch in s.channels
                    ],
                    'member_count': s.member_count
                }
                for s in servers
            ]
        }
        
        # 插入或更新缓存
        db.execute("""
            INSERT OR REPLACE INTO server_cache (account_id, data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (account_id, json.dumps(data, ensure_ascii=False)))
        db.commit()
        
        logger.info(f"[ServerDiscovery] 缓存已更新: 账号{account_id}")
        
    except Exception as e:
        logger.error(f"[ServerDiscovery] 缓存失败: {str(e)}")


@router.get("/{account_id}/cached")
async def get_cached_server_list(account_id: int):
    """获取缓存的服务器列表（快速访问）"""
    cached = get_cached_servers(account_id)
    
    if not cached:
        return {
            "cached": False,
            "message": "无缓存数据，请先执行discover"
        }
    
    return {
        "cached": True,
        **cached
    }


@router.delete("/{account_id}/cache")
async def clear_server_cache(account_id: int):
    """清除服务器缓存"""
    try:
        db.execute("DELETE FROM server_cache WHERE account_id = ?", (account_id,))
        db.commit()
        return {"message": "缓存已清除"}
    except Exception as e:
        logger.error(f"[ServerDiscovery] 清除缓存失败: {str(e)}")
        raise HTTPException(500, "清除缓存失败")
