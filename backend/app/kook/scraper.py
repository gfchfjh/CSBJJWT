"""
KOOK消息抓取器 - 完整实现版
使用Playwright监听KOOK WebSocket消息
"""
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import asyncio
import json
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
            
            async with async_playwright() as p:
                # 启动浏览器
                self.browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled'
                    ]
                )
                
                # 创建浏览器上下文
                self.context = await self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                # 加载Cookie（如果有）
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
                
                # 访问KOOK
                logger.info(f"[Scraper-{self.account_id}] 正在访问KOOK...")
                await self.page.goto('https://www.kookapp.cn/app', wait_until='networkidle')
                
                # 等待页面加载
                await asyncio.sleep(2)
                
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
                while self.is_running:
                    await asyncio.sleep(1)
                    
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
                message = self.parse_message(data)
                
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
    
    def parse_message(self, data: Dict) -> Optional[Dict]:
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
                channel_info = self.get_channel_info(d.get('target_id'))
                if channel_info:
                    message['channel_name'] = channel_info.get('name')
                    message['server_name'] = channel_info.get('server_name')
            except Exception:
                pass
            
            return message
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 消息解析失败: {str(e)}")
            return None
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """获取频道信息（从缓存或数据库）"""
        # TODO: 实现频道信息缓存
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
        # TODO: 实现密码解密
        from ..utils.crypto import decrypt
        return decrypt(encrypted)
    
    def register_message_handler(self, handler: Callable):
        """注册消息处理器"""
        self.message_handlers.append(handler)
    
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
    """抓取器管理器"""
    
    def __init__(self):
        self.scrapers: Dict[int, KookScraper] = {}
        self.tasks: Dict[int, asyncio.Task] = {}
    
    async def start_scraper(self, account_id: int):
        """启动指定账号的抓取器"""
        if account_id in self.scrapers:
            logger.warning(f"账号{account_id}的抓取器已在运行")
            return
        
        scraper = KookScraper(account_id)
        self.scrapers[account_id] = scraper
        
        # 创建任务
        task = asyncio.create_task(scraper.start())
        self.tasks[account_id] = task
        
        logger.info(f"账号{account_id}的抓取器已启动")
    
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
