"""KOOK消息抓取模块"""
import asyncio
import json
from typing import Dict, Any, Optional, Callable
from playwright.async_api import async_playwright, Browser, Page, WebSocket

from app.utils.logger import logger
from app.kook.auth import KookAuth
from app.kook.parser import parser
from app.database import db


class KookScraper:
    """KOOK消息抓取器"""
    
    def __init__(self, account_id: int):
        """初始化抓取器
        
        Args:
            account_id: 账号ID
        """
        self.account_id = account_id
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.auth = KookAuth()
        self.is_running = False
        self.reconnect_count = 0
        self.max_reconnect = 5
        self.message_callback: Optional[Callable] = None
    
    async def start(self, message_callback: Callable[[Dict[str, Any]], None]):
        """启动消息监听
        
        Args:
            message_callback: 收到消息时的回调函数
        """
        self.message_callback = message_callback
        self.is_running = True
        
        try:
            async with async_playwright() as p:
                # 启动浏览器
                self.browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                
                context = await self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                self.page = await context.new_page()
                
                # 登录
                if not await self._login():
                    logger.error("登录失败，无法启动监听")
                    return
                
                # 设置WebSocket监听
                self.page.on('websocket', self._handle_websocket)
                
                # 访问主页面
                await self.page.goto('https://www.kookapp.cn/app')
                await self.page.wait_for_load_state('networkidle')
                
                logger.info("开始监听KOOK消息")
                db.update_account_status(self.account_id, 'online')
                
                # 保持运行
                while self.is_running:
                    await asyncio.sleep(10)
                    
                    # 心跳检测
                    try:
                        await self.page.evaluate('() => console.log("heartbeat")')
                    except Exception as e:
                        logger.warning(f"心跳检测失败: {e}")
                        if self.reconnect_count < self.max_reconnect:
                            await self._reconnect()
                        else:
                            logger.error("重连次数超过限制，停止监听")
                            break
                
        except Exception as e:
            logger.error(f"抓取器异常: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """停止监听"""
        self.is_running = False
        
        if self.page:
            await self.page.close()
        
        if self.browser:
            await self.browser.close()
        
        db.update_account_status(self.account_id, 'offline')
        logger.info("已停止监听")
    
    async def _login(self) -> bool:
        """登录KOOK
        
        Returns:
            是否登录成功
        """
        # 获取账号信息
        accounts = db.get_accounts()
        account = next((a for a in accounts if a['id'] == self.account_id), None)
        
        if not account:
            logger.error(f"账号不存在: {self.account_id}")
            return False
        
        # 尝试使用Cookie登录
        if account.get('cookie'):
            cookies = json.loads(account['cookie'])
            if await self.auth.login_with_cookies(self.page, cookies):
                return True
        
        # Cookie失效，尝试账号密码登录
        if account.get('password_encrypted'):
            from app.utils.crypto import crypto
            password = crypto.decrypt(account['password_encrypted'])
            if await self.auth.login_with_password(self.page, account['email'], password):
                return True
        
        logger.error("所有登录方式都失败")
        return False
    
    async def _reconnect(self):
        """重新连接"""
        self.reconnect_count += 1
        logger.info(f"尝试重新连接 ({self.reconnect_count}/{self.max_reconnect})")
        
        await asyncio.sleep(30)  # 等待30秒后重连
        
        try:
            await self.page.reload()
            await self.page.wait_for_load_state('networkidle')
            logger.info("重连成功")
            self.reconnect_count = 0
        except Exception as e:
            logger.error(f"重连失败: {e}")
    
    def _handle_websocket(self, ws: WebSocket):
        """处理WebSocket连接"""
        logger.info(f"WebSocket连接建立: {ws.url}")
        
        async def on_message(message: str):
            """处理WebSocket消息"""
            try:
                data = json.loads(message)
                
                # 解析消息
                parsed = parser.parse_message(data)
                if parsed and self.message_callback:
                    await self.message_callback(parsed)
                    
            except Exception as e:
                logger.error(f"处理WebSocket消息失败: {e}")
        
        ws.on('framereceived', lambda payload: asyncio.create_task(on_message(payload)))
        ws.on('close', lambda: logger.warning("WebSocket连接关闭"))
        ws.on('socketerror', lambda error: logger.error(f"WebSocket错误: {error}"))


class ScraperManager:
    """抓取器管理器"""
    
    def __init__(self):
        self.scrapers: Dict[int, KookScraper] = {}
        self.tasks: Dict[int, asyncio.Task] = {}
    
    async def start_scraper(self, account_id: int, message_callback: Callable):
        """启动指定账号的抓取器"""
        if account_id in self.scrapers:
            logger.warning(f"账号 {account_id} 的抓取器已在运行")
            return
        
        scraper = KookScraper(account_id)
        self.scrapers[account_id] = scraper
        
        # 在后台任务中运行
        task = asyncio.create_task(scraper.start(message_callback))
        self.tasks[account_id] = task
        
        logger.info(f"已启动账号 {account_id} 的抓取器")
    
    async def stop_scraper(self, account_id: int):
        """停止指定账号的抓取器"""
        if account_id not in self.scrapers:
            logger.warning(f"账号 {account_id} 的抓取器不存在")
            return
        
        scraper = self.scrapers[account_id]
        await scraper.stop()
        
        # 取消任务
        if account_id in self.tasks:
            self.tasks[account_id].cancel()
            del self.tasks[account_id]
        
        del self.scrapers[account_id]
        logger.info(f"已停止账号 {account_id} 的抓取器")
    
    async def stop_all(self):
        """停止所有抓取器"""
        for account_id in list(self.scrapers.keys()):
            await self.stop_scraper(account_id)


# 全局抓取器管理器
scraper_manager = ScraperManager()
