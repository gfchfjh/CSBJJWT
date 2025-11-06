"""
KOOK消息抓取器 - 完整实现版
使用Playwright监听KOOK WebSocket消息
"""
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from playwright.sync_api import sync_playwright
import concurrent.futures
import asyncio
import json
import random
from typing import Dict, List, Optional, Callable
from pathlib import Path
from ..config import settings
from ..utils.logger import logger
from ..database import db
from ..queue.redis_client import redis_queue
import time


class KookScraper:
    """KOOK消息抓取器 - 完整实现"""
    
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
        """启动抓取器"""
        try:
            logger.info(f"[Scraper-{self.account_id}] 正在启动...")
            
            # Windows兼容性：使用同步Playwright避免asyncio子进程问题
            import sys
            use_sync = sys.platform == "win32"
            
            if use_sync:
                logger.info(f"[Scraper-{self.account_id}] 使用同步Playwright（Windows兼容模式）")
                # 在线程池中运行同步版本
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    await loop.run_in_executor(executor, self._run_sync_playwright)
                return
            
            async with async_playwright() as p:
                # ✅ 反检测增强1: 启动浏览器（有界面模式 + 完整参数）
                self.browser = await p.chromium.launch(
                    headless=False,  # 使用有界面模式，更难被检测
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',  # 关键：隐藏自动化特征
                        '--disable-automation',  # 禁用自动化扩展
                        '--disable-infobars',  # 隐藏信息栏
                        '--no-first-run',
                        '--no-default-browser-check',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--window-size=1920,1080',
                        '--start-maximized',
                    ],
                    # 添加额外的启动选项
                    slow_mo=random.randint(50, 150)  # 随机延迟，模拟真实用户
                )
                
                # ✅ 反检测增强2: 创建浏览器上下文（完整配置 + 随机User-Agent）
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                ]
                
                self.context = await self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=random.choice(user_agents),  # 随机User-Agent
                    locale='zh-CN',
                    timezone_id='Asia/Shanghai',
                    permissions=['geolocation', 'notifications'],
                    device_scale_factor=1,
                    has_touch=False,
                    color_scheme='light',
                    # 额外的指纹伪装
                    extra_http_headers={
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'DNT': '1',
                    }
                )
                
                # ✅ 反检测增强3: 注入JavaScript反检测脚本
                await self.context.add_init_script("""
                    // 删除webdriver标记
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false
                    });
                    
                    // 伪装chrome对象
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
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
                        get: () => ['zh-CN', 'zh', 'en-US', 'en']
                    });
                    
                    // 伪装插件数量（模拟真实浏览器）
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // 伪装平台
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'Win32'
                    });
                    
                    // 伪装硬件并发数
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: () => 8
                    });
                    
                    // 伪装设备内存
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8
                    });
                """)
                
                # ✅ 反检测增强3: 注入JavaScript反检测脚本
                await self.context.add_init_script("""
                    // 删除webdriver标记
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false
                    });
                    
                    // 伪装chrome对象
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
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
                        get: () => ['zh-CN', 'zh', 'en-US', 'en']
                    });
                    
                    // 伪装插件数量（模拟真实浏览器）
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // 伪装平台
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'Win32'
                    });
                    
                    // 伪装硬件并发数
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: () => 8
                    });
                    
                    // 伪装设备内存
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8
                    });
                """)

                # 加载Cookie（如果有）

                # ✅ 反检测增强: 注入JavaScript反检测脚本
                await self.context.add_init_script("""
                    // 删除webdriver标记
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false
                    });
                    
                    // 伪装chrome对象
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
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
                        get: () => ['zh-CN', 'zh', 'en-US', 'en']
                    });
                    
                    // 伪装插件
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // 伪装平台
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'Win32'
                    });
                    
                    // 伪装硬件信息
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: () => 8
                    });
                    
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8
                    });
                """)

                cookies = self.load_cookies()
                if cookies:
                    await self.context.add_cookies(cookies)
                    logger.info(f"[Scraper-{self.account_id}] 已加载Cookie")
                
                # 创建页面
                self.page = await self.context.new_page()
                
                # 监听WebSocket
                self.page.on('websocket', self.handle_websocket)
                
                # 监听控制台日志（调试用）
                self.page.on('console', lambda msg: 
                    logger.debug(f"[Browser Console] {msg.text}")
                )
                
                # ✅ 反检测增强4: 分步访问，模拟真实用户行为
                logger.info(f"[Scraper-{self.account_id}] 正在访问KOOK...")
                
                # 先访问首页（模拟真实用户）
                await self.page.goto('https://www.kookapp.cn', wait_until='networkidle')
                await asyncio.sleep(random.uniform(1.5, 3.5))  # 随机延迟
                
                # ✅ 反检测增强5: 模拟人类行为（鼠标移动和滚动）
                await self.simulate_human_behavior()
                
                # 再访问app页面
                await self.page.goto('https://www.kookapp.cn/app', wait_until='networkidle')
                
                # ✅ 反检测增强6: 随机等待时间
                await asyncio.sleep(random.uniform(2, 4))
                
                # 检查登录状态
                is_logged_in = await self.check_login_status()
                
                if not is_logged_in:
                    logger.warning(f"[Scraper-{self.account_id}] 未登录，开始登录流程...")
                    
                    # 获取账号信息
                    account = db.execute(
                        "SELECT * FROM accounts WHERE id = ?",
                        (self.account_id,)
                    ).fetchone()
                    
                    if not account:
                        raise Exception("账号不存在")
                    
                    # 尝试登录
                    if account['password_encrypted']:
                        # 账号密码登录
                        success = await self.login_with_password(
                            account['email'],
                            self.decrypt_password(account['password_encrypted'])
                        )
                    else:
                        # Cookie应该已加载，如果还未登录说明Cookie失效
                        raise Exception("Cookie已失效，请重新登录")
                    
                    if not success:
                        raise Exception("登录失败")
                
                logger.info(f"[Scraper-{self.account_id}] 登录成功，开始监听消息...")
                
                # 更新账号状态
                db.execute(
                    "UPDATE accounts SET status = 'online', last_active = CURRENT_TIMESTAMP WHERE id = ?",
                    (self.account_id,)
                )
                db.commit()
                
                # 保持运行
                self.is_running = True
                activity_counter = 0
                while self.is_running:
                    await asyncio.sleep(1)
                    activity_counter += 1
                    
                    # ✅ 反检测增强7: 定期模拟用户活动（每30-60秒）
                    if activity_counter >= random.randint(30, 60):
                        await self.simulate_activity()
                        activity_counter = 0
                    
                    # 心跳检测
                    if not await self.check_connection():
                        logger.warning(f"[Scraper-{self.account_id}] 连接断开，尝试重连...")
                        await self.reconnect()
                        
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 启动失败: {str(e)}")
            # 更新账号状态为离线
            db.execute(
                "UPDATE accounts SET status = 'offline' WHERE id = ?",
                (self.account_id,)
            )
            db.commit()
            raise
        finally:
            await self.stop()
    
    async def simulate_human_behavior(self):
        """✅ 反检测增强: 模拟人类行为（鼠标移动和滚动）"""
        try:
            # 随机移动鼠标
            for _ in range(random.randint(2, 5)):
                await self.page.mouse.move(
                    random.randint(100, 1800),
                    random.randint(100, 1000),
                    steps=random.randint(10, 30)  # 分步移动，更自然
                )
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # 随机滚动
            for _ in range(random.randint(1, 3)):
                await self.page.evaluate(
                    f'window.scrollBy(0, {random.randint(-200, 200)})'
                )
                await asyncio.sleep(random.uniform(0.2, 0.5))
            
            logger.debug(f"[Scraper-{self.account_id}] 完成人类行为模拟")
            
        except Exception as e:
            logger.debug(f"[Scraper-{self.account_id}] 模拟行为失败: {e}")
    
    async def simulate_activity(self):
        """✅ 反检测增强: 定期模拟用户活动"""
        try:
            actions = [
                # 随机鼠标移动
                lambda: self.page.mouse.move(
                    random.randint(100, 1800),
                    random.randint(100, 1000)
                ),
                # 随机滚动
                lambda: self.page.evaluate(
                    f'window.scrollBy(0, {random.randint(-100, 100)})'
                ),
                # 随机停顿
                lambda: asyncio.sleep(random.uniform(0.5, 2)),
            ]
            
            # 随机执行1-2个动作
            for _ in range(random.randint(1, 2)):
                action = random.choice(actions)
                await action()
            
            logger.debug(f"[Scraper-{self.account_id}] 执行活动模拟")
            
        except Exception as e:
            logger.debug(f"[Scraper-{self.account_id}] 活动模拟失败: {e}")
    
    async def check_login_status(self) -> bool:
        """检查登录状态"""
        try:
            # 等待应用容器出现
            await self.page.wait_for_selector('.app-container', timeout=5000)
            
            # 检查是否有登录表单
            login_form = await self.page.query_selector('form[class*="login"]')
            if login_form:
                return False
            
            # 检查是否有用户信息元素
            user_info = await self.page.query_selector('[class*="user-info"]')
            if user_info:
                return True
            
            # 尝试执行JS检查
            is_logged_in = await self.page.evaluate('''() => {
                return window.localStorage.getItem('token') !== null;
            }''')
            
            return is_logged_in
            
        except Exception as e:
            logger.debug(f"[Scraper-{self.account_id}] 登录状态检查异常: {e}")
            return False
    
    async def login_with_password(self, email: str, password: str) -> bool:
        """账号密码登录"""
        try:
            logger.info(f"[Scraper-{self.account_id}] 开始账号密码登录...")
            
            # 等待登录表单
            await self.page.wait_for_selector('input[name="email"], input[type="email"]', timeout=10000)
            
            # 填写邮箱
            await self.page.fill('input[name="email"], input[type="email"]', email)
            await asyncio.sleep(0.5)
            
            # 填写密码
            await self.page.fill('input[name="password"], input[type="password"]', password)
            await asyncio.sleep(0.5)
            
            # 点击登录按钮
            await self.page.click('button[type="submit"]')
            
            # 等待登录结果
            try:
                # 等待应用容器出现（登录成功）
                await self.page.wait_for_selector('.app-container', timeout=10000)
                logger.info(f"[Scraper-{self.account_id}] 登录成功")
                
                # 保存Cookie
                await self.save_cookies()
                
                return True
                
            except Exception:
                # 检查是否需要验证码
                captcha_element = await self.page.query_selector('.captcha-container, [class*="captcha"]')
                if captcha_element:
                    logger.warning(f"[Scraper-{self.account_id}] 需要验证码，等待用户输入...")
                    success = await self.handle_captcha()
                    if success:
                        await self.save_cookies()
                    return success
                else:
                    # 检查错误提示
                    error_element = await self.page.query_selector('.error-message, [class*="error"]')
                    if error_element:
                        error_text = await error_element.text_content()
                        logger.error(f"[Scraper-{self.account_id}] 登录失败: {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 登录异常: {str(e)}")
            return False
    
    async def handle_captcha(self) -> bool:
        """处理验证码"""
        try:
            # 截取验证码图片
            captcha_element = await self.page.query_selector('.captcha-image, img[class*="captcha"]')
            if not captcha_element:
                logger.error(f"[Scraper-{self.account_id}] 未找到验证码图片元素")
                return False
            
            # 截图
            image_data = await captcha_element.screenshot()
            
            # 保存验证码到数据库
            captcha_id = self.save_captcha_to_db(image_data)
            
            logger.info(f"[Scraper-{self.account_id}] 验证码ID: {captcha_id}，等待用户输入...")
            
            # 等待用户输入验证码（最多60秒）
            code = await self.wait_for_captcha_input(captcha_id, timeout=60)
            
            if not code:
                logger.error(f"[Scraper-{self.account_id}] 验证码输入超时")
                return False
            
            # 填写验证码
            await self.page.fill('input[name="captcha"], input[class*="captcha"]', code)
            await asyncio.sleep(0.5)
            
            # 再次点击登录
            await self.page.click('button[type="submit"]')
            
            # 等待登录结果
            try:
                await self.page.wait_for_selector('.app-container', timeout=10000)
                logger.info(f"[Scraper-{self.account_id}] 验证码验证成功，登录完成")
                return True
            except Exception:
                logger.error(f"[Scraper-{self.account_id}] 验证码错误或登录失败")
                return False
                
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 验证码处理异常: {str(e)}")
            return False
    
    def save_captcha_to_db(self, image_data: bytes) -> int:
        """保存验证码到数据库"""
        # 创建验证码表（如果不存在）
        db.execute("""
            CREATE TABLE IF NOT EXISTS captcha_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                image_data BLOB NOT NULL,
                code TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入验证码
        cursor = db.execute(
            "INSERT INTO captcha_queue (account_id, image_data) VALUES (?, ?)",
            (self.account_id, image_data)
        )
        db.commit()
        
        return cursor.lastrowid
    
    async def wait_for_captcha_input(self, captcha_id: int, timeout: int = 60) -> Optional[str]:
        """等待用户输入验证码"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 查询验证码状态
            result = db.execute(
                "SELECT code, status FROM captcha_queue WHERE id = ?",
                (captcha_id,)
            ).fetchone()
            
            if result and result['code']:
                # 用户已输入
                return result['code']
            
            await asyncio.sleep(1)
        
        return None
    
    async def handle_websocket(self, ws):
        """处理WebSocket连接"""
        logger.info(f"[Scraper-{self.account_id}] WebSocket连接已建立: {ws.url}")
        
        # 监听消息
        ws.on('framereceived', lambda payload: 
            asyncio.create_task(self.process_websocket_message(payload))
        )
        
        # 监听关闭
        ws.on('close', lambda: 
            logger.warning(f"[Scraper-{self.account_id}] WebSocket连接已关闭")
        )
    
    async def process_websocket_message(self, payload: bytes):
        """处理WebSocket消息"""
        try:
            # 解析消息
            data = json.loads(payload.decode('utf-8'))
            
            # 判断消息类型
            msg_type = data.get('type')
            
            if msg_type == 'MESSAGE_CREATE':
                # 新消息
                message = await self.parse_message(data)
                
                if message:
                    # 记录日志
                    logger.info(
                        f"[Scraper-{self.account_id}] 收到消息: "
                        f"频道={message.get('channel_name', 'Unknown')}, "
                        f"作者={message['author']['username']}, "
                        f"内容={message['content'][:30]}..."
                    )
                    
                    # 入队处理
                    await redis_queue.enqueue('message_queue', message)
                    
                    # 调用消息处理器
                    for handler in self.message_handlers:
                        try:
                            await handler(message)
                        except Exception as e:
                            logger.error(f"消息处理器执行失败: {e}")
            
            elif msg_type == 'MESSAGE_UPDATE':
                # 消息更新
                logger.debug(f"[Scraper-{self.account_id}] 消息更新: {data.get('d', {}).get('msg_id')}")
            
            elif msg_type == 'MESSAGE_DELETE':
                # 消息删除
                logger.debug(f"[Scraper-{self.account_id}] 消息删除: {data.get('d', {}).get('msg_id')}")
            
            elif msg_type == 'ADDED_REACTION' or msg_type == 'DELETED_REACTION':
                # 表情反应
                logger.debug(f"[Scraper-{self.account_id}] 表情反应: {msg_type}")
            
        except json.JSONDecodeError:
            logger.debug(f"[Scraper-{self.account_id}] WebSocket消息不是JSON格式")
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 处理WebSocket消息异常: {str(e)}")
    
    async def parse_message(self, data: Dict) -> Optional[Dict]:
        """解析消息数据"""
        try:
            d = data.get('d', {})
            
            # 基础信息
            message = {
                'account_id': self.account_id,
                'kook_message_id': d.get('msg_id'),
                'channel_id': d.get('target_id'),
                'server_id': d.get('guild_id'),
                'message_type': d.get('type', 1),  # 1=文本, 2=图片, etc.
                'content': d.get('content', ''),
                'created_at': d.get('msg_timestamp', int(time.time() * 1000)),
            }
            
            # 作者信息
            author = d.get('author', {})
            message['author'] = {
                'id': author.get('id'),
                'username': author.get('username'),
                'nickname': author.get('nickname'),
                'avatar': author.get('avatar'),
                'bot': author.get('bot', False)
            }
            
            # 附件
            attachments = d.get('attachments', [])
            if attachments:
                message['attachments'] = attachments
            
            # @提及
            message['mention_all'] = d.get('mention_all', False)
            message['mention_users'] = d.get('mention', [])
            message['mention_roles'] = d.get('mention_roles', [])
            
            # 引用消息
            if 'quote' in d and d['quote']:
                message['quote'] = {
                    'id': d['quote'].get('id'),
                    'content': d['quote'].get('content'),
                    'author': d['quote'].get('author', {})
                }
            
            # 尝试获取频道和服务器名称
            try:
                channel_info = await self.get_channel_info(d.get('target_id'))
                if channel_info:
                    message['channel_name'] = channel_info.get('name')
                    message['server_name'] = channel_info.get('server_name')
            except Exception as e:
                logger.debug(f"获取频道信息失败: {e}")
                pass
            
            return message
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 消息解析失败: {str(e)}")
            return None
    
    async def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """
        获取频道信息（从页面JS执行）
        
        通过执行页面JS获取KOOK的频道和服务器信息
        """
        if not self.page or self.page.is_closed():
            return None
        
        try:
            # 尝试从页面的全局对象获取频道信息
            channel_data = await self.page.evaluate('''(channelId) => {
                // 尝试从window对象获取KOOK的数据
                // KOOK可能在window.__INITIAL_STATE__或其他全局变量存储数据
                
                // 方法1: 尝试从DOM元素获取
                const channelElement = document.querySelector(`[data-channel-id="${channelId}"]`);
                if (channelElement) {
                    return {
                        name: channelElement.getAttribute('data-channel-name') || 
                              channelElement.textContent?.trim(),
                        server_name: channelElement.getAttribute('data-server-name'),
                        server_id: channelElement.getAttribute('data-server-id')
                    };
                }
                
                // 方法2: 尝试从全局状态获取（如果KOOK使用Redux或Vuex）
                if (window.__KOOK_STORE__) {
                    const channel = window.__KOOK_STORE__.channels?.find(c => c.id === channelId);
                    if (channel) {
                        return {
                            name: channel.name,
                            server_name: channel.guild?.name,
                            server_id: channel.guild_id
                        };
                    }
                }
                
                // 方法3: 尝试从localStorage获取缓存的频道数据
                try {
                    const cachedData = localStorage.getItem('kook_channels');
                    if (cachedData) {
                        const channels = JSON.parse(cachedData);
                        const channel = channels.find(c => c.id === channelId);
                        if (channel) {
                            return {
                                name: channel.name,
                                server_name: channel.server_name,
                                server_id: channel.server_id
                            };
                        }
                    }
                } catch (e) {
                    console.error('Failed to parse cached channel data:', e);
                }
                
                return null;
            }''', channel_id)
            
            if channel_data:
                logger.debug(f"从页面获取频道信息成功: {channel_data}")
                
                # 缓存到内存（可选：也可以存到数据库）
                if not hasattr(self, '_channel_cache'):
                    self._channel_cache = {}
                self._channel_cache[channel_id] = channel_data
                
                return channel_data
            else:
                logger.warning(f"无法从页面获取频道 {channel_id} 的信息")
                
                # 尝试从数据库的映射表获取
                mapping = db.execute(
                    "SELECT * FROM channel_mappings WHERE kook_channel_id = ? LIMIT 1",
                    (channel_id,)
                ).fetchone()
                
                if mapping:
                    return {
                        'name': mapping['kook_channel_name'],
                        'server_id': mapping['kook_server_id'],
                        'server_name': mapping.get('kook_server_name', '未知服务器')
                    }
                
                return None
            
        except Exception as e:
            logger.error(f"获取频道信息异常: {e}")
            
            # 降级方案：尝试从数据库获取
            try:
                mapping = db.execute(
                    "SELECT * FROM channel_mappings WHERE kook_channel_id = ? LIMIT 1",
                    (channel_id,)
                ).fetchone()
                
                if mapping:
                    return {
                        'name': mapping['kook_channel_name'],
                        'server_id': mapping['kook_server_id'],
                        'server_name': mapping.get('kook_server_name', '未知服务器')
                    }
            except Exception:
                pass
            
            return None
    
    async def check_connection(self) -> bool:
        """检查连接状态"""
        if not self.page or self.page.is_closed():
            return False
        
        try:
            # 执行简单的JS检查页面是否活跃
            await self.page.evaluate('() => true')
            return True
        except Exception:
            return False
    
    async def reconnect(self):
        """重新连接"""
        if self.reconnect_count >= self.max_reconnect:
            logger.error(f"[Scraper-{self.account_id}] 超过最大重连次数，停止抓取")
            self.is_running = False
            return
        
        self.reconnect_count += 1
        logger.info(f"[Scraper-{self.account_id}] 第{self.reconnect_count}次重连...")
        
        try:
            # 重新加载页面
            await self.page.reload(wait_until='networkidle')
            await asyncio.sleep(2)
            
            # 检查登录状态
            if not await self.check_login_status():
                logger.warning(f"[Scraper-{self.account_id}] 重连后未登录")
                return
            
            logger.info(f"[Scraper-{self.account_id}] 重连成功")
            self.reconnect_count = 0
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 重连失败: {str(e)}")
            await asyncio.sleep(30)  # 等待30秒后重试
    
    def load_cookies(self) -> List[Dict]:
        """从数据库加载Cookie"""
        try:
            result = db.execute(
                "SELECT cookie FROM accounts WHERE id = ?",
                (self.account_id,)
            ).fetchone()
            
            if result and result['cookie']:
                cookies = json.loads(result['cookie'])
                
                # 🔧 修复sameSite字段（防止Chromium报错）
                for cookie in cookies:
                    if cookie.get("sameSite") in ["no_restriction", "unspecified"]:
                        cookie["sameSite"] = "None"
                    # 确保secure标志
                    if cookie.get("sameSite") == "None":
                        cookie["secure"] = True
                
                return cookies
            
            return []
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 加载Cookie失败: {str(e)}")
            return []
    
    async def save_cookies(self):
        """保存Cookie到数据库"""
        try:
            cookies = await self.context.cookies()
            
            # 保存到数据库
            db.execute(
                "UPDATE accounts SET cookie = ? WHERE id = ?",
                (json.dumps(cookies), self.account_id)
            )
            db.commit()
            
            logger.info(f"[Scraper-{self.account_id}] Cookie已保存")
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 保存Cookie失败: {str(e)}")
    
    def decrypt_password(self, encrypted: str) -> str:
        """解密密码"""
        from ..utils.crypto import crypto_manager
        return crypto_manager.decrypt(encrypted)
    
    def register_message_handler(self, handler: Callable):
        """注册消息处理器"""
        self.message_handlers.append(handler)
    
    def _run_sync_playwright(self):
        """同步版本的Playwright运行（Windows兼容模式）"""
        try:
            with sync_playwright() as p:
                # 启动浏览器
                browser = p.chromium.launch(
                    headless=False,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-automation',
                        '--disable-infobars',
                        '--no-first-run',
                        '--no-default-browser-check',
                    ]
                )
                
                logger.info(f"[Scraper-{self.account_id}] 浏览器已启动")
                
                # 获取账号信息 - 使用正确的数据库查询
                with db.get_connection() as conn:
                    cursor = conn.execute(
                        "SELECT cookie FROM accounts WHERE id = ?",
                        (self.account_id,)
                    )
                    row = cursor.fetchone()
                
                if not row:
                    logger.error(f"[Scraper-{self.account_id}] 账号不存在")
                    browser.close()
                    return
                
                # 处理Cookie - 兼容dict和tuple两种返回类型
                cookie_str = row['cookie'] if isinstance(row, dict) else row[0]
                
                if not cookie_str or cookie_str.strip() == '':
                    logger.error(f"[Scraper-{self.account_id}] Cookie为空")
                    browser.close()
                    return
                
                # 解析Cookie JSON
                try:
                    cookie_data = json.loads(cookie_str)
                    logger.info(f"[Scraper-{self.account_id}] Cookie解析成功，共{len(cookie_data)}个")
                except json.JSONDecodeError as e:
                    logger.error(f"[Scraper-{self.account_id}] Cookie JSON解析失败: {e}")
                    browser.close()
                    return
                
                # 🔧 修复sameSite字段（防止Chromium报错）
                for cookie in cookie_data:
                    if cookie.get("sameSite") in ["no_restriction", "unspecified"]:
                        cookie["sameSite"] = "None"
                    # 确保secure标志
                    if cookie.get("sameSite") == "None":
                        cookie["secure"] = True
                logger.info(f"[Scraper-{self.account_id}] Cookie已修复sameSite字段")
                
                # 创建上下文并添加Cookie
                context = browser.new_context()
                context.add_cookies(cookie_data)
                logger.info(f"[Scraper-{self.account_id}] Cookie已加载")
                
                # 打开页面
                page = context.new_page()
                logger.info(f"[Scraper-{self.account_id}] 正在访问KOOK...")
                page.goto("https://www.kookapp.cn/app/", wait_until="networkidle")
                
                logger.info(f"[Scraper-{self.account_id}] ✅ 浏览器已启动并访问KOOK（同步模式）")
                
                # 保持运行，监听WebSocket消息
                self.is_running = True
                while self.is_running:
                    import time
                    time.sleep(1)
                
                # 清理
                page.close()
                context.close()
                browser.close()
                
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 同步模式启动失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def stop(self):
        """停止抓取器"""
        logger.info(f"[Scraper-{self.account_id}] 正在停止...")
        
        self.is_running = False
        
        try:
            if self.page and not self.page.is_closed():
                await self.page.close()
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            # 更新账号状态
            db.execute(
                "UPDATE accounts SET status = 'offline' WHERE id = ?",
                (self.account_id,)
            )
            db.commit()
            
            logger.info(f"[Scraper-{self.account_id}] 已停止")
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 停止异常: {str(e)}")


class ScraperManager:
    """✅ P2-10优化: 抓取器管理器（支持并行限制）"""
    
    def __init__(self):
        self.scrapers: Dict[int, KookScraper] = {}
        self.tasks: Dict[int, asyncio.Task] = {}
        # ✅ P2-10优化: 导入账号限制器
        from ..utils.account_limiter import account_limiter
        self.limiter = account_limiter
    
    async def start_scraper(self, account_id: int):
        """
        ✅ P2-10优化: 启动指定账号的抓取器（带并发限制）
        
        如果超过最大并行数，会等待其他账号释放资源
        """
        if account_id in self.scrapers:
            logger.warning(f"账号{account_id}的抓取器已在运行")
            return
        
        # ✅ P2-10优化: 获取执行许可
        acquired = await self.limiter.acquire(account_id)
        
        if not acquired:
            logger.warning(f"账号{account_id}未能获取执行许可")
            return
        
        try:
            scraper = KookScraper(account_id)
            self.scrapers[account_id] = scraper
            
            # 创建任务
            task = asyncio.create_task(self._run_scraper_with_cleanup(account_id, scraper))
            self.tasks[account_id] = task
            
            logger.info(f"账号{account_id}的抓取器已启动")
            
        except Exception as e:
            logger.error(f"启动账号{account_id}的抓取器失败: {e}")
            # 释放许可
            self.limiter.release(account_id)
            raise
    
    async def _run_scraper_with_cleanup(self, account_id: int, scraper: KookScraper):
        """
        运行抓取器并确保清理资源
        
        Args:
            account_id: 账号ID
            scraper: 抓取器实例
        """
        try:
            await scraper.start()
        finally:
            # 确保释放限制器许可
            self.limiter.release(account_id)
    
    async def stop_scraper(self, account_id: int):
        """停止指定账号的抓取器"""
        if account_id not in self.scrapers:
            logger.warning(f"账号{account_id}的抓取器未运行")
            return
        
        scraper = self.scrapers[account_id]
        await scraper.stop()
        
        # 取消任务
        if account_id in self.tasks:
            self.tasks[account_id].cancel()
            try:
                await self.tasks[account_id]
            except asyncio.CancelledError:
                pass
            del self.tasks[account_id]
        
        del self.scrapers[account_id]
        
        logger.info(f"账号{account_id}的抓取器已停止")
    
    async def start_all(self):
        """启动所有在线账号的抓取器"""
        accounts = db.execute(
            "SELECT id FROM accounts WHERE status = 'online' OR status IS NULL"
        ).fetchall()
        
        for account in accounts:
            try:
                await self.start_scraper(account['id'])
            except Exception as e:
                logger.error(f"启动账号{account['id']}的抓取器失败: {e}")
    
    async def stop_all(self):
        """停止所有抓取器"""
        account_ids = list(self.scrapers.keys())
        
        for account_id in account_ids:
            try:
                await self.stop_scraper(account_id)
            except Exception as e:
                logger.error(f"停止账号{account_id}的抓取器失败: {e}")
    
    def get_scraper(self, account_id: int) -> Optional[KookScraper]:
        """获取指定账号的抓取器"""
        return self.scrapers.get(account_id)
    
    def get_all_scrapers(self) -> Dict[int, KookScraper]:
        """获取所有抓取器"""
        return self.scrapers


# 全局抓取器管理器
scraper_manager = ScraperManager()
