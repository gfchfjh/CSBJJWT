"""
KOOK官方API客户端 - 完整实现
支持获取服务器、频道、用户等信息
✅ P0-2优化：真正的API调用，不依赖页面DOM
"""
import aiohttp
import asyncio
import json
from typing import Dict, List, Optional, Any
from ..utils.logger import logger


class KookAPIClient:
    """
    KOOK官方REST API客户端
    
    API文档: https://developer.kookapp.cn/doc/http/
    """
    
    BASE_URL = "https://www.kookapp.cn/api/v3"
    
    def __init__(self, token: Optional[str] = None, cookies: Optional[Dict] = None):
        """
        初始化API客户端
        
        Args:
            token: KOOK Bot Token（如果有）
            cookies: Cookie字典（从浏览器获取）
        """
        self.token = token
        self.cookies = cookies
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.create_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close_session()
        
    async def create_session(self):
        """创建HTTP会话"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json'
        }
        
        if self.token:
            headers['Authorization'] = f'Bot {self.token}'
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            cookies=self.cookies
        )
        
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送API请求
        
        Args:
            method: HTTP方法（GET/POST/PUT/DELETE）
            endpoint: API端点（例如：/guild/list）
            **kwargs: 其他参数（params, json, data等）
            
        Returns:
            API响应数据
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        if not self.session:
            await self.create_session()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('code') == 0:
                    return data.get('data', {})
                else:
                    error_msg = data.get('message', 'Unknown error')
                    logger.error(f"KOOK API错误: {error_msg} (状态码: {response.status})")
                    raise Exception(f"API请求失败: {error_msg}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"KOOK API请求异常: {str(e)}")
            raise Exception(f"网络请求失败: {str(e)}")
    
    async def get_user_guilds(self, page: int = 1, page_size: int = 100) -> List[Dict]:
        """
        获取用户加入的所有服务器（Guild）
        
        API: GET /guild/list
        
        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            服务器列表
            [
                {
                    "id": "服务器ID",
                    "name": "服务器名称",
                    "topic": "服务器主题",
                    "user_id": "服务器主ID",
                    "icon": "图标URL",
                    "notify_type": 通知类型,
                    "region": "区域",
                    "enable_open": 是否公开,
                    "open_id": 公开ID,
                    "default_channel_id": "默认频道ID",
                    "welcome_channel_id": "欢迎频道ID"
                }
            ]
        """
        try:
            result = await self._request(
                'GET',
                '/guild/list',
                params={
                    'page': page,
                    'page_size': page_size
                }
            )
            
            guilds = result.get('items', [])
            logger.info(f"✅ 获取到 {len(guilds)} 个服务器")
            return guilds
            
        except Exception as e:
            logger.error(f"获取服务器列表失败: {str(e)}")
            raise
    
    async def get_guild_channels(self, guild_id: str, page: int = 1, page_size: int = 100) -> List[Dict]:
        """
        获取服务器的所有频道
        
        API: GET /channel/list
        
        Args:
            guild_id: 服务器ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            频道列表
            [
                {
                    "id": "频道ID",
                    "name": "频道名称",
                    "user_id": "创建者ID",
                    "guild_id": "服务器ID",
                    "topic": "频道主题",
                    "is_category": 是否分组,
                    "parent_id": "父分组ID",
                    "level": 频道层级,
                    "slow_mode": 慢速模式,
                    "type": 频道类型（1=文字,2=语音）,
                    "permission_overwrites": [],
                    "permission_users": [],
                    "permission_sync": 1
                }
            ]
        """
        try:
            result = await self._request(
                'GET',
                '/channel/list',
                params={
                    'guild_id': guild_id,
                    'page': page,
                    'page_size': page_size
                }
            )
            
            channels = result.get('items', [])
            logger.info(f"✅ 服务器 {guild_id} 有 {len(channels)} 个频道")
            return channels
            
        except Exception as e:
            logger.error(f"获取频道列表失败: {str(e)}")
            raise
    
    async def get_guild_detail(self, guild_id: str) -> Dict:
        """
        获取服务器详情
        
        API: GET /guild/view
        
        Args:
            guild_id: 服务器ID
            
        Returns:
            服务器详细信息
        """
        try:
            result = await self._request(
                'GET',
                '/guild/view',
                params={'guild_id': guild_id}
            )
            return result
        except Exception as e:
            logger.error(f"获取服务器详情失败: {str(e)}")
            raise
    
    async def get_channel_detail(self, channel_id: str) -> Dict:
        """
        获取频道详情
        
        API: GET /channel/view
        
        Args:
            channel_id: 频道ID
            
        Returns:
            频道详细信息
        """
        try:
            result = await self._request(
                'GET',
                '/channel/view',
                params={'target_id': channel_id}
            )
            return result
        except Exception as e:
            logger.error(f"获取频道详情失败: {str(e)}")
            raise
    
    async def get_user_me(self) -> Dict:
        """
        获取当前用户信息
        
        API: GET /user/me
        
        Returns:
            用户信息
            {
                "id": "用户ID",
                "username": "用户名",
                "identify_num": "识别码",
                "online": 是否在线,
                "status": 状态,
                "avatar": "头像URL",
                "vip_avatar": "VIP头像URL",
                "mobile_verified": 是否验证手机,
                "roles": []
            }
        """
        try:
            result = await self._request('GET', '/user/me')
            logger.info(f"✅ 当前用户: {result.get('username')}#{result.get('identify_num')}")
            return result
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            raise
    
    async def get_all_guilds_with_channels(self) -> List[Dict]:
        """
        获取所有服务器及其频道（完整结构）
        
        这是一个便捷方法，会自动获取所有服务器和每个服务器的频道
        
        Returns:
            完整的服务器-频道树形结构
            [
                {
                    "id": "服务器ID",
                    "name": "服务器名称",
                    "icon": "图标URL",
                    "channels": [
                        {
                            "id": "频道ID",
                            "name": "频道名称",
                            "type": 1 or 2,  # 1=文字, 2=语音
                            "is_category": False,
                            "parent_id": "父分组ID"
                        }
                    ]
                }
            ]
        """
        try:
            # 1. 获取所有服务器
            guilds = await self.get_user_guilds()
            
            # 2. 为每个服务器获取频道
            result = []
            for guild in guilds:
                try:
                    channels = await self.get_guild_channels(guild['id'])
                    
                    # 过滤掉分组，只保留实际频道
                    actual_channels = [
                        {
                            'id': ch['id'],
                            'name': ch['name'],
                            'type': ch['type'],
                            'is_category': ch.get('is_category', False),
                            'parent_id': ch.get('parent_id', ''),
                            'topic': ch.get('topic', '')
                        }
                        for ch in channels
                        if not ch.get('is_category', False)  # 排除分组
                    ]
                    
                    result.append({
                        'id': guild['id'],
                        'name': guild['name'],
                        'icon': guild.get('icon', ''),
                        'topic': guild.get('topic', ''),
                        'channels': actual_channels
                    })
                    
                    logger.info(f"✅ 服务器 [{guild['name']}] 有 {len(actual_channels)} 个频道")
                    
                except Exception as e:
                    logger.warning(f"获取服务器 {guild['name']} 的频道失败: {str(e)}")
                    # 即使某个服务器失败，也继续处理其他服务器
                    continue
            
            logger.info(f"✅ 成功获取 {len(result)} 个服务器的完整信息")
            return result
            
        except Exception as e:
            logger.error(f"获取服务器和频道失败: {str(e)}")
            raise
    
    async def validate_token(self) -> bool:
        """
        验证Token是否有效
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            await self.get_user_me()
            return True
        except:
            return False
    
    @staticmethod
    async def from_cookie(cookies: Dict) -> 'KookAPIClient':
        """
        从Cookie创建API客户端
        
        Args:
            cookies: Cookie字典
            
        Returns:
            配置好的API客户端实例
        """
        client = KookAPIClient(cookies=cookies)
        await client.create_session()
        
        # 验证Cookie是否有效
        try:
            await client.get_user_me()
            logger.info("✅ Cookie验证成功")
            return client
        except Exception as e:
            logger.error(f"❌ Cookie无效: {str(e)}")
            raise Exception("Cookie无效或已过期")
    
    @staticmethod
    async def from_token(token: str) -> 'KookAPIClient':
        """
        从Bot Token创建API客户端
        
        Args:
            token: KOOK Bot Token
            
        Returns:
            配置好的API客户端实例
        """
        client = KookAPIClient(token=token)
        await client.create_session()
        
        # 验证Token是否有效
        if not await client.validate_token():
            raise Exception("Token无效")
        
        logger.info("✅ Token验证成功")
        return client


# 辅助函数：从账号获取API客户端
async def get_api_client_from_account(account_id: int) -> KookAPIClient:
    """
    从数据库账号创建API客户端
    
    Args:
        account_id: 账号ID
        
    Returns:
        配置好的API客户端
    """
    from ..database import db
    
    account = db.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (account_id,)
    ).fetchone()
    
    if not account:
        raise Exception(f"账号 {account_id} 不存在")
    
    # 尝试从Cookie创建
    if account['cookie']:
        try:
            cookies_list = json.loads(account['cookie'])
            # 转换为字典格式
            cookies_dict = {c['name']: c['value'] for c in cookies_list}
            return await KookAPIClient.from_cookie(cookies_dict)
        except Exception as e:
            logger.warning(f"使用Cookie创建客户端失败: {str(e)}")
    
    # 如果有Bot Token
    if account.get('bot_token'):
        return await KookAPIClient.from_token(account['bot_token'])
    
    raise Exception("账号没有有效的认证信息（Cookie或Token）")
