"""
KOOK消息抓取模块（使用Playwright）
"""
import asyncio
import json
import base64
from typing import Optional, Dict, Any, Callable
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError
from ..utils.logger import logger
from ..database import db


class KookScraper:
    """KOOK消息抓取器"""
    
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_running = False
        self.message_callback: Optional[Callable] = None
        self.playwright = None
    
    async def start(self, cookie: Optional[str] = None, 
                   email: Optional[str] = None,
                   password: Optional[str] = None):
        """
        启动抓取器
        
        Args:
            cookie: Cookie字符串（JSON格式）
            email: 邮箱（用于账号密码登录）
            password: 密码（用于账号密码登录）
        """
        try:
            logger.info(f"启动KOOK抓取器，账号ID: {self.account_id}")
            
            # 启动Playwright
            self.playwright = await async_playwright().start()
            
            # 启动浏览器（无头模式）
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            # 创建浏览器上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # 如果提供了Cookie，加载Cookie
            if cookie:
                try:
                    cookies = json.loads(cookie)
                    await self.context.add_cookies(cookies)
                    logger.info("已加载Cookie")
                except Exception as e:
                    logger.error(f"加载Cookie失败: {str(e)}")
            
            # 创建页面
            self.page = await self.context.new_page()
            
            # 监听WebSocket消息
            self.page.on('websocket', self._handle_websocket)
            
            # 导航到KOOK
            await self.page.goto('https://www.kookapp.cn/app', wait_until='networkidle')
            
            # 如果没有Cookie，尝试账号密码登录
            if not cookie and email and password:
                success = await self._login_with_password(email, password)
                if not success:
                    logger.error("账号密码登录失败")
                    return False
            
            # 检查是否登录成功
            await asyncio.sleep(3)
            if not await self._check_login_status():
                logger.error("登录状态检查失败")
                return False
            
            self.is_running = True
            db.update_account_status(self.account_id, 'online')
            logger.info("KOOK抓取器启动成功")
            
            # 保持运行
            while self.is_running:
                await asyncio.sleep(10)
                # 心跳检测
                try:
                    await self.page.evaluate('() => console.log("heartbeat")')
                except:
                    logger.warning("心跳检测失败，尝试重连...")
                    await self._reconnect()
            
            return True
            
        except Exception as e:
            logger.error(f"启动KOOK抓取器失败: {str(e)}")
            db.update_account_status(self.account_id, 'offline')
            return False
    
    async def stop(self):
        """停止抓取器"""
        try:
            logger.info(f"停止KOOK抓取器，账号ID: {self.account_id}")
            self.is_running = False
            
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            db.update_account_status(self.account_id, 'offline')
            logger.info("KOOK抓取器已停止")
            
        except Exception as e:
            logger.error(f"停止KOOK抓取器失败: {str(e)}")
    
    def set_message_callback(self, callback: Callable):
        """设置消息回调函数"""
        self.message_callback = callback
    
    async def _handle_websocket(self, ws):
        """处理WebSocket消息"""
        try:
            ws.on('framereceived', lambda payload: asyncio.create_task(
                self._process_websocket_message(payload)
            ))
        except Exception as e:
            logger.error(f"WebSocket处理异常: {str(e)}")
    
    async def _process_websocket_message(self, payload):
        """处理WebSocket消息"""
        try:
            # 解析消息
            data = json.loads(payload)
            
            # 检查是否是新消息事件
            if data.get('type') == 'MESSAGE_CREATE':
                message_data = data.get('data', {})
                
                # 提取消息信息
                message_type = message_data.get('type', 'text')
                attachments = message_data.get('attachments', [])
                
                # 提取图片URL
                image_urls = []
                if message_type == 'image' or attachments:
                    for attachment in attachments:
                        if attachment.get('type') == 'image':
                            image_urls.append(attachment.get('url'))
                
                message = {
                    'message_id': message_data.get('id'),
                    'channel_id': message_data.get('channel_id'),
                    'server_id': message_data.get('guild_id'),
                    'content': message_data.get('content'),
                    'message_type': message_data.get('type', 'text'),
                    'sender_id': message_data.get('author', {}).get('id'),
                    'sender_name': message_data.get('author', {}).get('username'),
                    'sender_avatar': message_data.get('author', {}).get('avatar'),
                    'timestamp': message_data.get('timestamp'),
                    'attachments': message_data.get('attachments', []),
                    'image_urls': image_urls,
                }
                
                logger.debug(f"收到新消息: {message['message_id']}")
                
                # 调用回调函数
                if self.message_callback:
                    await self.message_callback(message)
                    
        except json.JSONDecodeError:
            pass  # 非JSON消息，忽略
        except Exception as e:
            logger.error(f"处理WebSocket消息异常: {str(e)}")
    
    async def _login_with_password(self, email: str, password: str) -> bool:
        """
        使用账号密码登录
        
        Args:
            email: 邮箱
            password: 密码
            
        Returns:
            是否成功
        """
        try:
            # 等待登录表单出现
            await self.page.wait_for_selector('input[type="email"]', timeout=10000)
            
            # 填写邮箱
            await self.page.fill('input[type="email"]', email)
            
            # 填写密码
            await self.page.fill('input[type="password"]', password)
            
            # 点击登录按钮
            await self.page.click('button[type="submit"]')
            
            # 等待登录完成或验证码出现
            await asyncio.sleep(3)
            
            # 检查是否需要验证码
            captcha_required = await self._check_captcha_required()
            
            if captcha_required:
                logger.info("检测到需要验证码")
                success = await self._handle_captcha()
                if not success:
                    logger.error("验证码处理失败")
                    return False
            
            # 再次等待登录完成
            await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"账号密码登录失败: {str(e)}")
            return False
    
    async def _check_captcha_required(self) -> bool:
        """
        检查是否需要验证码
        
        Returns:
            是否需要验证码
        """
        try:
            # 尝试查找验证码输入框或验证码图片
            # 注意：实际选择器需要根据KOOK网页的实际结构调整
            captcha_selectors = [
                'input[name="captcha"]',
                'input[placeholder*="验证码"]',
                'img.captcha-image',
                '.captcha-container'
            ]
            
            for selector in captcha_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=2000)
                    if element:
                        return True
                except TimeoutError:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"检查验证码异常: {str(e)}")
            return False
    
    async def _handle_captcha(self) -> bool:
        """
        处理验证码（需要用户输入）
        
        Returns:
            是否成功
        """
        try:
            # 获取验证码图片
            captcha_image_url = await self._get_captcha_image()
            
            if not captcha_image_url:
                logger.error("无法获取验证码图片")
                return False
            
            logger.info(f"验证码图片URL: {captcha_image_url}")
            
            # TODO: 这里需要通过WebSocket或其他方式通知前端显示验证码对话框
            # 由于当前架构限制，暂时使用等待方式
            # 在实际应用中，应该建立前后端实时通信机制
            
            # 存储验证码信息到数据库，让前端轮询获取
            db.set_system_config(
                f"captcha_required_{self.account_id}",
                json.dumps({
                    "image_url": captcha_image_url,
                    "timestamp": asyncio.get_event_loop().time()
                })
            )
            
            # 等待用户输入验证码（最多2分钟）
            captcha_code = await self._wait_for_captcha_input(timeout=120)
            
            if not captcha_code:
                logger.error("验证码输入超时")
                return False
            
            # 填写验证码
            await self.page.fill('input[name="captcha"]', captcha_code)
            
            # 再次提交
            await self.page.click('button[type="submit"]')
            await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"处理验证码异常: {str(e)}")
            return False
    
    async def _get_captcha_image(self) -> Optional[str]:
        """
        获取验证码图片
        
        Returns:
            图片URL或base64数据
        """
        try:
            # 查找验证码图片元素
            img_element = await self.page.query_selector('img.captcha-image')
            
            if not img_element:
                # 尝试其他可能的选择器
                img_element = await self.page.query_selector('img[alt*="验证码"]')
            
            if img_element:
                # 获取图片URL
                src = await img_element.get_attribute('src')
                
                if src:
                    # 如果是完整URL，直接返回
                    if src.startswith('http'):
                        return src
                    
                    # 如果是base64，也返回
                    if src.startswith('data:image'):
                        return src
                    
                    # 如果是相对路径，拼接完整URL
                    return f"https://www.kookapp.cn{src}"
            
            return None
            
        except Exception as e:
            logger.error(f"获取验证码图片异常: {str(e)}")
            return None
    
    async def _wait_for_captcha_input(self, timeout: int = 120) -> Optional[str]:
        """
        等待用户输入验证码
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            验证码字符串
        """
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            # 从数据库检查用户是否已输入验证码
            captcha_data = db.get_system_config(f"captcha_input_{self.account_id}")
            
            if captcha_data:
                try:
                    data = json.loads(captcha_data)
                    code = data.get('code')
                    
                    if code:
                        # 清除已使用的验证码
                        db.delete_system_config(f"captcha_input_{self.account_id}")
                        db.delete_system_config(f"captcha_required_{self.account_id}")
                        
                        return code
                except:
                    pass
            
            # 每秒检查一次
            await asyncio.sleep(1)
        
        # 超时，清除验证码请求
        db.delete_system_config(f"captcha_required_{self.account_id}")
        
        return None
    
    async def _check_login_status(self) -> bool:
        """检查登录状态"""
        try:
            # 检查页面URL是否包含/app
            current_url = self.page.url
            if '/app' in current_url:
                return True
            
            # 或者检查特定元素是否存在
            # TODO: 根据实际页面调整选择器
            
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {str(e)}")
            return False
    
    async def _reconnect(self):
        """重新连接"""
        try:
            logger.info("尝试重新连接...")
            
            # 刷新页面
            await self.page.reload()
            await asyncio.sleep(3)
            
            # 检查登录状态
            if await self._check_login_status():
                logger.info("重新连接成功")
                db.update_account_status(self.account_id, 'online')
            else:
                logger.error("重新连接失败")
                db.update_account_status(self.account_id, 'offline')
                
        except Exception as e:
            logger.error(f"重新连接异常: {str(e)}")
    
    async def get_servers(self) -> list:
        """获取服务器列表"""
        try:
            # TODO: 实现获取服务器列表的逻辑
            # 这需要根据KOOK的实际页面结构来实现
            return []
        except Exception as e:
            logger.error(f"获取服务器列表失败: {str(e)}")
            return []
    
    async def get_channels(self, server_id: str) -> list:
        """获取频道列表"""
        try:
            # TODO: 实现获取频道列表的逻辑
            return []
        except Exception as e:
            logger.error(f"获取频道列表失败: {str(e)}")
            return []


class ScraperManager:
    """抓取器管理器"""
    
    def __init__(self):
        self.scrapers: Dict[int, KookScraper] = {}
    
    async def start_scraper(self, account_id: int, 
                           cookie: Optional[str] = None,
                           email: Optional[str] = None,
                           password: Optional[str] = None,
                           message_callback: Optional[Callable] = None):
        """启动抓取器"""
        if account_id in self.scrapers:
            logger.warning(f"抓取器已存在，账号ID: {account_id}")
            return False
        
        scraper = KookScraper(account_id)
        if message_callback:
            scraper.set_message_callback(message_callback)
        
        self.scrapers[account_id] = scraper
        
        # 在后台任务中启动
        asyncio.create_task(scraper.start(cookie, email, password))
        
        return True
    
    async def stop_scraper(self, account_id: int):
        """停止抓取器"""
        if account_id not in self.scrapers:
            logger.warning(f"抓取器不存在，账号ID: {account_id}")
            return False
        
        scraper = self.scrapers[account_id]
        await scraper.stop()
        del self.scrapers[account_id]
        
        return True
    
    async def stop_all(self):
        """停止所有抓取器"""
        for account_id in list(self.scrapers.keys()):
            await self.stop_scraper(account_id)


# 创建全局抓取器管理器
scraper_manager = ScraperManager()
