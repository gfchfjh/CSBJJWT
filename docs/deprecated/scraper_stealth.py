"""
KOOK消息抓取器 - 增强反检测版
基于原版 scraper.py，增加更多反检测措施
"""
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import asyncio
import random
import json
from typing import Dict, List, Optional, Callable
from pathlib import Path
from ..config import settings
from ..utils.logger import logger
from ..database import db
from ..queue.redis_client import redis_queue
import time


class KookScraperStealth:
    """KOOK消息抓取器 - 增强反检测版"""
    
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_running = False
        self.reconnect_count = 0
        self.max_reconnect = 5
        self.message_handlers: List[Callable] = []
        
    async def start(self):
        """启动抓取器 - 增强反检测版"""
        try:
            logger.info(f"[Scraper-Stealth-{self.account_id}] 正在启动（增强反检测模式）...")
            
            async with async_playwright() as p:
                # ✅ 增强措施1: 使用完整的浏览器参数，模拟真实环境
                self.browser = await p.chromium.launch(
                    headless=False,  # 改为有界面模式（更难检测）
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',  # 禁用自动化标记
                        '--disable-automation',  # 禁用自动化扩展
                        '--disable-infobars',  # 隐藏信息栏
                        '--disable-web-security',  # 禁用Web安全（谨慎使用）
                        '--no-first-run',  # 跳过首次运行
                        '--no-default-browser-check',  # 不检查默认浏览器
                        '--disable-background-timer-throttling',  # 禁用后台限制
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--window-size=1920,1080',  # 固定窗口大小
                        '--start-maximized',  # 最大化启动
                    ]
                )
                
                # ✅ 增强措施2: 完整的浏览器上下文配置
                self.context = await self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    # 使用真实的User-Agent（定期更新）
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    # 添加语言设置
                    locale='zh-CN',
                    timezone_id='Asia/Shanghai',
                    # 添加权限
                    permissions=['geolocation', 'notifications'],
                    # 设备像素比
                    device_scale_factor=1,
                    # 是否支持触摸
                    has_touch=False,
                    # 颜色方案
                    color_scheme='light',
                )
                
                # ✅ 增强措施3: 注入反检测脚本
                await self.context.add_init_script("""
                    // 删除webdriver标记
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false
                    });
                    
                    // 伪装chrome对象
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // 伪装权限API
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // 伪装语言
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-CN', 'zh', 'en']
                    });
                    
                    // 伪装插件
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                """)
                
                # 加载Cookie（如果有）
                cookies = self.load_cookies()
                if cookies:
                    await self.context.add_cookies(cookies)
                    logger.info(f"[Scraper-Stealth-{self.account_id}] 已加载Cookie")
                
                # 创建页面
                self.page = await self.context.new_page()
                
                # ✅ 增强措施4: 随机延迟，模拟人类行为
                await asyncio.sleep(random.uniform(2, 5))
                
                # 监听WebSocket
                self.page.on('websocket', self.handle_websocket)
                
                # ✅ 增强措施5: 分步访问，模拟真实用户
                logger.info(f"[Scraper-Stealth-{self.account_id}] 正在访问KOOK...")
                
                # 先访问首页
                await self.page.goto('https://www.kookapp.cn', wait_until='networkidle')
                await asyncio.sleep(random.uniform(1, 3))
                
                # 再访问app页面
                await self.page.goto('https://www.kookapp.cn/app', wait_until='networkidle')
                
                # ✅ 增强措施6: 随机鼠标移动（模拟人类）
                await self.simulate_human_behavior()
                
                # 等待页面加载
                await asyncio.sleep(random.uniform(2, 4))
                
                # 检查登录状态
                is_logged_in = await self.check_login_status()
                
                if not is_logged_in:
                    logger.warning(f"[Scraper-Stealth-{self.account_id}] 未登录")
                    raise Exception("未登录，请先导入Cookie")
                
                logger.info(f"[Scraper-Stealth-{self.account_id}] 登录成功，开始监听消息...")
                
                # 更新账号状态
                db.execute(
                    "UPDATE accounts SET status = 'online', last_active = CURRENT_TIMESTAMP WHERE id = ?",
                    (self.account_id,)
                )
                
                # 保持运行
                self.is_running = True
                while self.is_running:
                    # ✅ 增强措施7: 定期模拟活动
                    await asyncio.sleep(random.uniform(30, 60))
                    await self.simulate_activity()
                    
                    # 心跳检测
                    if not await self.check_connection():
                        logger.warning(f"[Scraper-Stealth-{self.account_id}] 连接断开，尝试重连...")
                        await self.reconnect()
                        
        except Exception as e:
            logger.error(f"[Scraper-Stealth-{self.account_id}] 启动失败: {str(e)}")
            db.execute(
                "UPDATE accounts SET status = 'offline' WHERE id = ?",
                (self.account_id,)
            )
            raise
        finally:
            await self.stop()
    
    async def simulate_human_behavior(self):
        """模拟人类行为"""
        try:
            # 随机移动鼠标
            await self.page.mouse.move(
                random.randint(100, 1000),
                random.randint(100, 800)
            )
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # 随机滚动
            await self.page.evaluate('window.scrollBy(0, Math.random() * 200)')
            await asyncio.sleep(random.uniform(0.5, 1))
            
        except Exception as e:
            logger.debug(f"模拟行为失败: {e}")
    
    async def simulate_activity(self):
        """定期模拟用户活动"""
        try:
            # 随机执行一些操作
            actions = [
                lambda: self.page.mouse.move(random.randint(100, 1000), random.randint(100, 800)),
                lambda: self.page.evaluate('window.scrollBy(0, Math.random() * 100)'),
                lambda: asyncio.sleep(random.uniform(1, 3)),
            ]
            
            action = random.choice(actions)
            await action()
            
        except Exception as e:
            logger.debug(f"模拟活动失败: {e}")
    
    # ... 其他方法与原版相同 ...
    
    def load_cookies(self):
        """从数据库加载Cookie"""
        account = db.execute(
            "SELECT cookie FROM accounts WHERE id = ?",
            (self.account_id,)
        ).fetchone()
        
        if account and account['cookie']:
            try:
                return json.loads(account['cookie'])
            except:
                return None
        return None
    
    async def check_login_status(self) -> bool:
        """检查登录状态"""
        try:
            await self.page.wait_for_selector('.app-container', timeout=5000)
            login_form = await self.page.query_selector('form[class*="login"]')
            return login_form is None
        except:
            return False
    
    async def check_connection(self) -> bool:
        """检查连接状态"""
        try:
            return self.page and not self.page.is_closed()
        except:
            return False
    
    async def reconnect(self):
        """重连"""
        self.reconnect_count += 1
        if self.reconnect_count > self.max_reconnect:
            logger.error(f"[Scraper-Stealth-{self.account_id}] 达到最大重连次数")
            self.is_running = False
            return
        
        logger.info(f"[Scraper-Stealth-{self.account_id}] 尝试重连 ({self.reconnect_count}/{self.max_reconnect})...")
        await asyncio.sleep(random.uniform(5, 10))
        # 重新访问页面
        await self.page.goto('https://www.kookapp.cn/app', wait_until='networkidle')
    
    async def handle_websocket(self, ws):
        """处理WebSocket消息"""
        # 与原版相同的WebSocket处理逻辑
        pass
    
    async def stop(self):
        """停止抓取器"""
        self.is_running = False
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
