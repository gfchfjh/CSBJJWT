"""
✅ P0-2优化: KOOK服务器/频道自动获取模块
自动从已登录的KOOK账号获取用户加入的所有服务器和频道
"""
import asyncio
import json
from typing import Dict, List, Optional
from playwright.async_api import Page, BrowserContext
from ..utils.logger import logger
from ..database import db


class KookServerFetcher:
    """KOOK服务器/频道获取器"""
    
    def __init__(self, page: Page):
        """
        初始化
        
        Args:
            page: Playwright页面实例（已登录KOOK）
        """
        self.page = page
        self.servers = []
        self.channels = {}
    
    async def fetch_all_servers(self) -> List[Dict]:
        """
        获取用户加入的所有服务器
        
        Returns:
            服务器列表，格式：
            [
                {
                    "id": "server_id",
                    "name": "服务器名称",
                    "icon": "服务器图标URL",
                    "owner_id": "创建者ID",
                    "member_count": 100
                },
                ...
            ]
        """
        try:
            logger.info("[ServerFetcher] 开始获取服务器列表...")
            
            # 方法1: 通过执行JS获取KOOK的全局状态
            servers_data = await self._fetch_servers_from_js()
            
            if servers_data:
                logger.info(f"[ServerFetcher] 通过JS获取到 {len(servers_data)} 个服务器")
                self.servers = servers_data
                return servers_data
            
            # 方法2: 通过DOM元素获取
            logger.info("[ServerFetcher] JS方法失败，尝试通过DOM获取...")
            servers_data = await self._fetch_servers_from_dom()
            
            if servers_data:
                logger.info(f"[ServerFetcher] 通过DOM获取到 {len(servers_data)} 个服务器")
                self.servers = servers_data
                return servers_data
            
            # 方法3: 通过API请求获取（需要token）
            logger.info("[ServerFetcher] DOM方法失败，尝试通过API获取...")
            servers_data = await self._fetch_servers_from_api()
            
            if servers_data:
                logger.info(f"[ServerFetcher] 通过API获取到 {len(servers_data)} 个服务器")
                self.servers = servers_data
                return servers_data
            
            logger.warning("[ServerFetcher] 所有获取方法都失败")
            return []
            
        except Exception as e:
            logger.error(f"[ServerFetcher] 获取服务器列表失败: {str(e)}")
            return []
    
    async def _fetch_servers_from_js(self) -> Optional[List[Dict]]:
        """
        方法1: 通过执行JS获取服务器列表
        KOOK可能在window.__INITIAL_STATE__或Redux Store中存储服务器数据
        """
        try:
            # 尝试从window对象获取服务器数据
            servers_js = await self.page.evaluate('''() => {
                // 方法1: 从__INITIAL_STATE__获取
                if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.guilds) {
                    return window.__INITIAL_STATE__.guilds;
                }
                
                // 方法2: 从Redux Store获取
                if (window.__KOOK_STORE__ && window.__KOOK_STORE__.guilds) {
                    return Object.values(window.__KOOK_STORE__.guilds);
                }
                
                // 方法3: 从localStorage获取缓存
                try {
                    const cachedGuilds = localStorage.getItem('guilds');
                    if (cachedGuilds) {
                        return JSON.parse(cachedGuilds);
                    }
                } catch (e) {
                    console.error('Failed to parse guilds from localStorage:', e);
                }
                
                // 方法4: 从全局变量获取
                if (window.guilds) {
                    return window.guilds;
                }
                
                return null;
            }''')
            
            if not servers_js:
                return None
            
            # 转换为标准格式
            servers = []
            for server in servers_js:
                servers.append({
                    'id': server.get('id'),
                    'name': server.get('name', '未命名服务器'),
                    'icon': server.get('icon', ''),
                    'owner_id': server.get('user_id', ''),
                    'member_count': server.get('member_count', 0),
                })
            
            return servers if servers else None
            
        except Exception as e:
            logger.debug(f"[ServerFetcher] JS方法失败: {str(e)}")
            return None
    
    async def _fetch_servers_from_dom(self) -> Optional[List[Dict]]:
        """
        方法2: 通过DOM元素获取服务器列表
        解析页面上的服务器列表元素
        """
        try:
            # 等待服务器列表加载
            await self.page.wait_for_selector('[class*="guild-list"], [class*="server-list"]', timeout=5000)
            
            # 获取所有服务器元素
            servers_data = await self.page.evaluate('''() => {
                const servers = [];
                
                // 尝试查找服务器列表容器
                const serverListSelectors = [
                    '[class*="guild-list"]',
                    '[class*="server-list"]',
                    '[class*="guilds"]',
                    '[data-list-id="guildsnav"]'
                ];
                
                let serverList = null;
                for (const selector of serverListSelectors) {
                    serverList = document.querySelector(selector);
                    if (serverList) break;
                }
                
                if (!serverList) {
                    console.log('未找到服务器列表容器');
                    return null;
                }
                
                // 获取服务器元素
                const serverElements = serverList.querySelectorAll('[class*="guild-"], [class*="server-"]');
                
                serverElements.forEach(element => {
                    // 尝试提取服务器信息
                    const serverId = element.getAttribute('data-guild-id') || 
                                     element.getAttribute('data-server-id') ||
                                     element.getAttribute('id');
                    
                    const serverName = element.getAttribute('data-guild-name') ||
                                       element.getAttribute('aria-label') ||
                                       element.querySelector('[class*="name"]')?.textContent ||
                                       '未命名服务器';
                    
                    const serverIcon = element.querySelector('img')?.src || '';
                    
                    if (serverId) {
                        servers.push({
                            id: serverId,
                            name: serverName.trim(),
                            icon: serverIcon,
                            owner_id: '',
                            member_count: 0
                        });
                    }
                });
                
                return servers.length > 0 ? servers : null;
            }''')
            
            return servers_data
            
        except Exception as e:
            logger.debug(f"[ServerFetcher] DOM方法失败: {str(e)}")
            return None
    
    async def _fetch_servers_from_api(self) -> Optional[List[Dict]]:
        """
        方法3: 通过KOOK API获取服务器列表
        需要从页面获取token
        """
        try:
            # 获取token
            token = await self.page.evaluate('''() => {
                return localStorage.getItem('token') || 
                       localStorage.getItem('access_token') ||
                       sessionStorage.getItem('token');
            }''')
            
            if not token:
                logger.debug("[ServerFetcher] 未找到token")
                return None
            
            # 发送API请求获取服务器列表
            # 注意：这需要知道KOOK的API端点，可能需要抓包分析
            servers_data = await self.page.evaluate('''async (token) => {
                try {
                    const response = await fetch('https://www.kookapp.cn/api/v3/guild/list', {
                        headers: {
                            'Authorization': token,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (!response.ok) {
                        console.error('API请求失败:', response.status);
                        return null;
                    }
                    
                    const data = await response.json();
                    
                    if (data && data.data && data.data.guilds) {
                        return data.data.guilds.map(guild => ({
                            id: guild.id,
                            name: guild.name,
                            icon: guild.icon,
                            owner_id: guild.user_id,
                            member_count: guild.member_count || 0
                        }));
                    }
                    
                    return null;
                } catch (error) {
                    console.error('API调用失败:', error);
                    return null;
                }
            }''', token)
            
            return servers_data
            
        except Exception as e:
            logger.debug(f"[ServerFetcher] API方法失败: {str(e)}")
            return None
    
    async def fetch_channels_for_server(self, server_id: str) -> List[Dict]:
        """
        获取指定服务器的所有频道
        
        Args:
            server_id: 服务器ID
            
        Returns:
            频道列表，格式：
            [
                {
                    "id": "channel_id",
                    "name": "#频道名称",
                    "type": "text",  # text/voice
                    "category": "分类名称",
                    "position": 0
                },
                ...
            ]
        """
        try:
            logger.info(f"[ServerFetcher] 获取服务器 {server_id} 的频道列表...")
            
            # 方法1: 通过JS获取
            channels_data = await self._fetch_channels_from_js(server_id)
            
            if channels_data:
                logger.info(f"[ServerFetcher] 通过JS获取到 {len(channels_data)} 个频道")
                self.channels[server_id] = channels_data
                return channels_data
            
            # 方法2: 通过DOM获取
            logger.info("[ServerFetcher] JS方法失败，尝试通过DOM获取...")
            channels_data = await self._fetch_channels_from_dom(server_id)
            
            if channels_data:
                logger.info(f"[ServerFetcher] 通过DOM获取到 {len(channels_data)} 个频道")
                self.channels[server_id] = channels_data
                return channels_data
            
            # 方法3: 通过API获取
            logger.info("[ServerFetcher] DOM方法失败，尝试通过API获取...")
            channels_data = await self._fetch_channels_from_api(server_id)
            
            if channels_data:
                logger.info(f"[ServerFetcher] 通过API获取到 {len(channels_data)} 个频道")
                self.channels[server_id] = channels_data
                return channels_data
            
            logger.warning(f"[ServerFetcher] 获取服务器 {server_id} 的频道失败")
            return []
            
        except Exception as e:
            logger.error(f"[ServerFetcher] 获取频道列表失败: {str(e)}")
            return []
    
    async def _fetch_channels_from_js(self, server_id: str) -> Optional[List[Dict]]:
        """通过JS获取频道列表"""
        try:
            channels_js = await self.page.evaluate('''(serverId) => {
                // 方法1: 从全局状态获取
                if (window.__KOOK_STORE__ && window.__KOOK_STORE__.channels) {
                    const channels = Object.values(window.__KOOK_STORE__.channels)
                        .filter(ch => ch.guild_id === serverId);
                    return channels;
                }
                
                // 方法2: 从localStorage获取
                try {
                    const cachedChannels = localStorage.getItem(`channels_${serverId}`);
                    if (cachedChannels) {
                        return JSON.parse(cachedChannels);
                    }
                } catch (e) {
                    console.error('Failed to parse channels:', e);
                }
                
                return null;
            }''', server_id)
            
            if not channels_js:
                return None
            
            # 转换为标准格式
            channels = []
            for channel in channels_js:
                channels.append({
                    'id': channel.get('id'),
                    'name': channel.get('name', '未命名频道'),
                    'type': 'text' if channel.get('type') == 1 else 'voice',
                    'category': channel.get('parent_id', ''),
                    'position': channel.get('position', 0),
                })
            
            return channels if channels else None
            
        except Exception as e:
            logger.debug(f"[ServerFetcher] 频道JS方法失败: {str(e)}")
            return None
    
    async def _fetch_channels_from_dom(self, server_id: str) -> Optional[List[Dict]]:
        """通过DOM获取频道列表"""
        try:
            # 先点击服务器，加载频道列表
            await self.page.click(f'[data-guild-id="{server_id}"], [data-server-id="{server_id}"]')
            await asyncio.sleep(1)  # 等待频道列表加载
            
            channels_data = await self.page.evaluate('''() => {
                const channels = [];
                
                // 查找频道列表
                const channelListSelectors = [
                    '[class*="channel-list"]',
                    '[class*="channels"]',
                    '[data-list-id="channels"]'
                ];
                
                let channelList = null;
                for (const selector of channelListSelectors) {
                    channelList = document.querySelector(selector);
                    if (channelList) break;
                }
                
                if (!channelList) {
                    return null;
                }
                
                // 获取频道元素
                const channelElements = channelList.querySelectorAll('[class*="channel-"]');
                
                channelElements.forEach((element, index) => {
                    const channelId = element.getAttribute('data-channel-id') ||
                                      element.getAttribute('id');
                    
                    const channelName = element.getAttribute('data-channel-name') ||
                                        element.querySelector('[class*="name"]')?.textContent ||
                                        '未命名频道';
                    
                    const channelType = element.getAttribute('data-channel-type') ||
                                        (element.querySelector('[class*="voice"]') ? 'voice' : 'text');
                    
                    if (channelId) {
                        channels.push({
                            id: channelId,
                            name: channelName.trim(),
                            type: channelType,
                            category: '',
                            position: index
                        });
                    }
                });
                
                return channels.length > 0 ? channels : null;
            }''')
            
            return channels_data
            
        except Exception as e:
            logger.debug(f"[ServerFetcher] 频道DOM方法失败: {str(e)}")
            return None
    
    async def _fetch_channels_from_api(self, server_id: str) -> Optional[List[Dict]]:
        """通过API获取频道列表"""
        try:
            token = await self.page.evaluate('''() => {
                return localStorage.getItem('token');
            }''')
            
            if not token:
                return None
            
            channels_data = await self.page.evaluate('''async (serverId, token) => {
                try {
                    const response = await fetch(`https://www.kookapp.cn/api/v3/channel/list?guild_id=${serverId}`, {
                        headers: {
                            'Authorization': token,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (!response.ok) {
                        return null;
                    }
                    
                    const data = await response.json();
                    
                    if (data && data.data && data.data.channels) {
                        return data.data.channels.map(channel => ({
                            id: channel.id,
                            name: channel.name,
                            type: channel.type === 1 ? 'text' : 'voice',
                            category: channel.parent_id || '',
                            position: channel.position || 0
                        }));
                    }
                    
                    return null;
                } catch (error) {
                    console.error('频道API调用失败:', error);
                    return null;
                }
            }''', server_id, token)
            
            return channels_data
            
        except Exception as e:
            logger.debug(f"[ServerFetcher] 频道API方法失败: {str(e)}")
            return None
    
    async def fetch_all_servers_and_channels(self) -> Dict[str, any]:
        """
        获取所有服务器及其频道的完整数据
        
        Returns:
            {
                "servers": [
                    {
                        "id": "xxx",
                        "name": "游戏公告服务器",
                        "icon": "...",
                        "channels": [
                            {"id": "yyy", "name": "#公告频道", "type": "text"},
                            {"id": "zzz", "name": "#活动频道", "type": "text"}
                        ]
                    }
                ]
            }
        """
        try:
            # 1. 获取所有服务器
            servers = await self.fetch_all_servers()
            
            if not servers:
                return {"servers": []}
            
            # 2. 为每个服务器获取频道
            result = []
            for server in servers:
                channels = await self.fetch_channels_for_server(server['id'])
                
                result.append({
                    **server,
                    'channels': channels
                })
                
                # 避免请求过快
                await asyncio.sleep(0.5)
            
            return {"servers": result}
            
        except Exception as e:
            logger.error(f"[ServerFetcher] 获取完整数据失败: {str(e)}")
            return {"servers": []}
    
    def save_to_database(self, account_id: int):
        """
        将获取的服务器/频道数据保存到数据库
        
        Args:
            account_id: 账号ID
        """
        try:
            logger.info("[ServerFetcher] 保存服务器/频道数据到数据库...")
            
            # 创建服务器表（如果不存在）
            db.execute("""
                CREATE TABLE IF NOT EXISTS kook_servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    server_id TEXT NOT NULL,
                    server_name TEXT NOT NULL,
                    server_icon TEXT,
                    owner_id TEXT,
                    member_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(account_id, server_id)
                )
            """)
            
            # 创建频道表（如果不存在）
            db.execute("""
                CREATE TABLE IF NOT EXISTS kook_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    server_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    channel_name TEXT NOT NULL,
                    channel_type TEXT DEFAULT 'text',
                    category TEXT,
                    position INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(account_id, server_id, channel_id)
                )
            """)
            
            # 保存服务器
            for server in self.servers:
                db.execute("""
                    INSERT OR REPLACE INTO kook_servers 
                    (account_id, server_id, server_name, server_icon, owner_id, member_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    account_id,
                    server['id'],
                    server['name'],
                    server.get('icon', ''),
                    server.get('owner_id', ''),
                    server.get('member_count', 0)
                ))
            
            # 保存频道
            for server_id, channels in self.channels.items():
                for channel in channels:
                    db.execute("""
                        INSERT OR REPLACE INTO kook_channels
                        (account_id, server_id, channel_id, channel_name, channel_type, category, position)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        account_id,
                        server_id,
                        channel['id'],
                        channel['name'],
                        channel['type'],
                        channel.get('category', ''),
                        channel.get('position', 0)
                    ))
            
            db.commit()
            logger.info(f"[ServerFetcher] 已保存 {len(self.servers)} 个服务器和 {sum(len(c) for c in self.channels.values())} 个频道")
            
        except Exception as e:
            logger.error(f"[ServerFetcher] 保存数据库失败: {str(e)}")


# 辅助函数
async def get_servers_and_channels_from_db(account_id: int) -> Dict:
    """
    从数据库获取已保存的服务器/频道数据
    
    Args:
        account_id: 账号ID
        
    Returns:
        服务器和频道数据
    """
    try:
        # 获取服务器
        servers_rows = db.execute("""
            SELECT server_id, server_name, server_icon, owner_id, member_count
            FROM kook_servers
            WHERE account_id = ?
            ORDER BY server_name
        """, (account_id,)).fetchall()
        
        servers = []
        for row in servers_rows:
            server_id = row['server_id']
            
            # 获取该服务器的频道
            channels_rows = db.execute("""
                SELECT channel_id, channel_name, channel_type, category, position
                FROM kook_channels
                WHERE account_id = ? AND server_id = ?
                ORDER BY position, channel_name
            """, (account_id, server_id)).fetchall()
            
            channels = [dict(row) for row in channels_rows]
            
            servers.append({
                'id': row['server_id'],
                'name': row['server_name'],
                'icon': row['server_icon'],
                'owner_id': row['owner_id'],
                'member_count': row['member_count'],
                'channels': channels
            })
        
        return {"servers": servers}
        
    except Exception as e:
        logger.error(f"从数据库获取服务器/频道失败: {str(e)}")
        return {"servers": []}
