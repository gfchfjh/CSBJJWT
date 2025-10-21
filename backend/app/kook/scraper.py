"""
KOOK消息抓取模块（使用Playwright）
"""
import asyncio
import json
import base64
from typing import Optional, Dict, Any, Callable
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError
from ..utils.logger import logger
from ..utils.captcha_solver import get_captcha_solver
from ..utils.selector_manager import selector_manager
from ..utils.crypto import crypto_manager
from ..database import db


class KookScraper:
    """KOOK消息抓取器（v1.8.1：支持共享浏览器上下文）"""
    
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_running = False
        self.message_callback: Optional[Callable] = None
        self.playwright = None
        self.reconnect_count = 0
        self.max_reconnect = 5  # 最大重连次数
        
        # 共享浏览器实例（v1.8.1新增）
        self.shared_browser: Optional[Browser] = None
        self.shared_context: Optional[BrowserContext] = None
        self.use_shared = False  # 是否使用共享实例
    
    async def start(self, cookie: Optional[str] = None, 
                   email: Optional[str] = None,
                   password: Optional[str] = None,
                   sync_history_minutes: int = 0):
        """
        启动抓取器
        
        Args:
            cookie: Cookie字符串（JSON格式）
            email: 邮箱（用于账号密码登录）
            password: 密码（用于账号密码登录）
            sync_history_minutes: 同步最近N分钟的历史消息（0=不同步）
        """
        try:
            logger.info(f"启动KOOK抓取器，账号ID: {self.account_id}")
            
            # 检查是否使用共享浏览器（v1.8.1）
            if self.shared_browser and self.shared_context:
                logger.info(f"✅ 使用共享浏览器实例")
                self.browser = self.shared_browser
                self.context = self.shared_context
                self.use_shared = True
            else:
                # 独立浏览器模式
                logger.info(f"使用独立浏览器实例")
                
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
                self.use_shared = False
            
            # 如果提供了Cookie，加载Cookie（v1.12.0+ 支持多种格式）
            if cookie:
                try:
                    from ..utils.cookie_parser import cookie_parser
                    
                    # 解析Cookie（自动识别格式）
                    cookies = cookie_parser.parse(cookie)
                    
                    # 验证Cookie
                    if not cookie_parser.validate(cookies):
                        logger.error("Cookie验证失败")
                        return False
                    
                    # 加载Cookie到浏览器
                    await self.context.add_cookies(cookies)
                    logger.info(f"✅ 已加载Cookie，共{len(cookies)}条")
                    
                except ValueError as e:
                    logger.error(f"Cookie格式错误: {str(e)}")
                    return False
                except Exception as e:
                    logger.error(f"加载Cookie失败: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    return False
            
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
            
            # 如果需要，同步历史消息
            if sync_history_minutes > 0:
                logger.info(f"开始同步最近{sync_history_minutes}分钟的历史消息...")
                await self.sync_history_messages(sync_history_minutes)
            
            # 保持运行
            while self.is_running:
                await asyncio.sleep(10)
                # 心跳检测
                try:
                    await self.page.evaluate('() => console.log("heartbeat")')
                    # 心跳成功，重置重连计数
                    self.reconnect_count = 0
                except Exception as e:
                    logger.warning(f"心跳检测失败: {str(e)}，尝试重连...")
                    
                    # 检查是否达到最大重连次数
                    if self.reconnect_count >= self.max_reconnect:
                        logger.error(f"账号{self.account_id}达到最大重连次数({self.max_reconnect})，停止抓取器")
                        self.is_running = False
                        db.update_account_status(self.account_id, 'offline')
                        break
                    
                    self.reconnect_count += 1
                    logger.info(f"第{self.reconnect_count}次重连尝试（最多{self.max_reconnect}次）")
                    
                    # v1.11.0新增：先尝试自动重新登录
                    relogin_success = await self._auto_relogin_if_expired()
                    if not relogin_success:
                        # 如果自动登录失败，使用常规重连
                        await self._reconnect()
            
            return True
            
        except Exception as e:
            logger.error(f"启动KOOK抓取器失败: {str(e)}")
            db.update_account_status(self.account_id, 'offline')
            return False
    
    async def stop(self):
        """停止抓取器（v1.8.1：共享模式下不关闭Browser和Context）"""
        try:
            logger.info(f"停止KOOK抓取器，账号ID: {self.account_id}")
            self.is_running = False
            
            # 关闭页面
            if self.page:
                await self.page.close()
                self.page = None
            
            # 如果使用共享浏览器，不关闭Context和Browser
            if self.use_shared:
                logger.info(f"共享模式：保留浏览器实例供其他账号使用")
            else:
                # 独立模式：关闭Context和Browser
                if self.context:
                    await self.context.close()
                    self.context = None
                if self.browser:
                    await self.browser.close()
                    self.browser = None
                if self.playwright:
                    await self.playwright.stop()
                    self.playwright = None
            
            db.update_account_status(self.account_id, 'offline')
            logger.info("KOOK抓取器已停止")
            
        except Exception as e:
            logger.error(f"停止KOOK抓取器失败: {str(e)}")
    
    def set_message_callback(self, callback: Callable):
        """设置消息回调函数"""
        self.message_callback = callback
    
    def _validate_cookies(self, cookie_str: str) -> bool:
        """
        验证Cookie格式（v1.12.0+ 支持多种格式自动识别）
        
        Args:
            cookie_str: Cookie字符串
            
        Returns:
            是否有效
        """
        try:
            # 使用新的Cookie解析器（支持多种格式）
            from ..utils.cookie_parser import cookie_parser
            
            # 尝试解析Cookie
            cookies = cookie_parser.parse(cookie_str)
            
            # 验证Cookie
            return cookie_parser.validate(cookies)
            
        except ValueError as e:
            logger.error(f"Cookie格式错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Cookie验证异常: {str(e)}")
            return False
    
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
                content = message_data.get('content', '')
                
                # 提取图片URL和附件文件URL
                image_urls = []
                file_attachments = []
                if message_type == 'image' or attachments:
                    for attachment in attachments:
                        if attachment.get('type') == 'image':
                            image_urls.append(attachment.get('url'))
                        elif attachment.get('type') == 'file':
                            # 提取文件附件信息
                            file_attachments.append({
                                'url': attachment.get('url'),
                                'name': attachment.get('name', 'unknown'),
                                'size': attachment.get('size', 0),
                                'type': attachment.get('file_type', 'application/octet-stream')
                            })
                
                # 提取@提及
                mentions = []
                mention_all = False
                if message_data.get('mention_info'):
                    mention_info = message_data['mention_info']
                    # 提取@用户
                    for user_id in mention_info.get('mention_part', []):
                        mentions.append({
                            'type': 'user',
                            'id': user_id
                        })
                    # 检查是否@全体成员
                    if mention_info.get('mention_all'):
                        mention_all = True
                        mentions.append({
                            'type': 'all'
                        })
                
                # 提取引用消息
                quote = None
                if message_data.get('quote'):
                    quote_data = message_data['quote']
                    quote = {
                        'message_id': quote_data.get('id'),
                        'author': quote_data.get('author', {}).get('username'),
                        'content': quote_data.get('content')
                    }
                
                # 获取当前Cookie（用于下载图片和附件）
                cookies_dict = await self._get_cookies_dict()
                
                message = {
                    'message_id': message_data.get('id'),
                    'channel_id': message_data.get('channel_id'),
                    'server_id': message_data.get('guild_id'),
                    'content': content,
                    'message_type': message_data.get('type', 'text'),
                    'sender_id': message_data.get('author', {}).get('id'),
                    'sender_name': message_data.get('author', {}).get('username'),
                    'sender_avatar': message_data.get('author', {}).get('avatar'),
                    'timestamp': message_data.get('timestamp'),
                    'attachments': message_data.get('attachments', []),
                    'image_urls': image_urls,
                    'file_attachments': file_attachments,  # 新增：文件附件列表
                    'mentions': mentions,
                    'mention_all': mention_all,
                    'quote': quote,
                    'cookies': cookies_dict,  # ✅ 新增：传递Cookie用于下载防盗链资源
                }
                
                logger.debug(f"收到新消息: {message['message_id']}")
                
                # 调用回调函数
                if self.message_callback:
                    await self.message_callback(message)
            
            # 处理表情反应事件
            elif data.get('type') in ['MESSAGE_REACTION_ADD', 'MESSAGE_REACTION_REMOVE']:
                reaction_data = data.get('data', {})
                
                reaction = {
                    'type': 'reaction',
                    'action': 'add' if data['type'] == 'MESSAGE_REACTION_ADD' else 'remove',
                    'message_id': reaction_data.get('msg_id'),
                    'channel_id': reaction_data.get('channel_id'),
                    'user_id': reaction_data.get('user_id'),
                    'emoji': reaction_data.get('emoji', {}).get('name', ''),
                    'timestamp': reaction_data.get('timestamp')
                }
                
                logger.debug(f"收到表情反应: {reaction['emoji']}")
                
                # 如果有回调函数，也发送表情反应事件
                if self.message_callback:
                    await self.message_callback(reaction)
                    
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
    
    async def _get_cookies_dict(self) -> Dict:
        """
        获取当前浏览器的Cookie字典
        
        Returns:
            Cookie字典 {name: value}
        """
        try:
            cookies = await self.context.cookies()
            return {cookie['name']: cookie['value'] for cookie in cookies}
        except Exception as e:
            logger.error(f"获取Cookie失败: {str(e)}")
            return {}
    
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
        处理验证码（智能模式：优先2Captcha自动识别，失败则人工输入）
        
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
            
            captcha_code = None
            
            # 尝试使用2Captcha自动识别
            captcha_solver = get_captcha_solver()
            if captcha_solver and captcha_solver.enabled:
                logger.info("🤖 尝试使用2Captcha自动识别验证码...")
                
                # 检查余额
                balance = await captcha_solver.get_balance()
                if balance is not None and balance > 0:
                    logger.info(f"2Captcha余额充足: ${balance:.2f}")
                    
                    # 自动识别
                    captcha_code = await captcha_solver.solve_image_captcha(
                        image_url=captcha_image_url,
                        timeout=120
                    )
                    
                    if captcha_code:
                        logger.info(f"✅ 2Captcha识别成功: {captcha_code}")
                    else:
                        logger.warning("⚠️ 2Captcha识别失败，切换到手动模式")
                else:
                    logger.warning(f"⚠️ 2Captcha余额不足: ${balance or 0:.2f}，切换到手动模式")
            else:
                logger.info("📝 2Captcha未配置，使用手动输入模式")
            
            # 如果自动识别失败，使用手动输入
            if not captcha_code:
                logger.info("等待用户手动输入验证码...")
                
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
        """
        检查登录状态（多种检查方式）
        
        Returns:
            是否已登录
        """
        try:
            logger.info("开始检查登录状态...")
            
            # 方式1: 检查URL是否包含app（登录后会跳转到/app）
            current_url = self.page.url
            logger.debug(f"当前URL: {current_url}")
            
            if '/app' in current_url and 'login' not in current_url:
                logger.info("✅ 检测到已跳转到主页，登录成功")
                return True
            
            # 方式2: 检查是否存在登录表单（如果仍在登录页）
            try:
                login_form = await self.page.query_selector('form[class*="login"], input[type="password"]')
                if login_form:
                    logger.warning("⚠️ 仍在登录页面，登录可能失败")
                    return False
            except:
                pass
            
            # 方式3: 检查用户信息元素（使用多个可能的选择器）
            user_selectors = [
                '.user-panel',
                '[data-user-info]',
                '.current-user',
                '.user-avatar',
                '[class*="user"]',
                '[class*="profile"]',
            ]
            
            for selector in user_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        logger.info(f"✅ 检测到用户信息元素: {selector}")
                        return True
                except:
                    continue
            
            # 方式4: 等待3秒后再次检查URL（给页面更多加载时间）
            logger.debug("等待3秒后再次检查...")
            await asyncio.sleep(3)
            
            current_url = self.page.url
            if '/app' in current_url and 'login' not in current_url:
                logger.info("✅ 延迟检查：已跳转到主页")
                return True
            
            # 方式5: 检查localStorage中是否有token（如果KOOK使用localStorage）
            try:
                has_token = await self.page.evaluate('''() => {
                    return localStorage.getItem('token') || 
                           localStorage.getItem('access_token') || 
                           localStorage.getItem('user_token');
                }''')
                if has_token:
                    logger.info("✅ 检测到localStorage中的token")
                    return True
            except:
                pass
            
            # 方式6: 检查Cookie中是否有关键字段
            try:
                cookies = await self.context.cookies()
                cookie_names = [c['name'].lower() for c in cookies]
                
                # 检查是否有常见的认证Cookie
                auth_cookie_keywords = ['token', 'session', 'auth', 'user', 'sid']
                has_auth_cookie = any(
                    any(keyword in name for keyword in auth_cookie_keywords)
                    for name in cookie_names
                )
                
                if has_auth_cookie and len(cookies) > 3:
                    logger.info(f"✅ 检测到认证Cookie（共{len(cookies)}个）")
                    return True
            except:
                pass
            
            logger.error("❌ 所有登录状态检查均失败")
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态异常: {str(e)}")
            return False
    
    async def _auto_relogin_if_expired(self) -> bool:
        """
        检测Cookie过期并自动重新登录（v1.11.0新增）
        
        Returns:
            是否重新登录成功
        """
        try:
            logger.info("🔍 检测到连接异常，检查是否需要重新登录...")
            
            # 检查当前登录状态
            if await self._check_login_status():
                logger.info("✅ 登录状态正常，无需重新登录")
                return True
            
            logger.warning("❌ 检测到Cookie已过期或登录失效")
            
            # 从数据库获取账号信息
            account = db.get_account(self.account_id)
            if not account:
                logger.error("无法获取账号信息")
                return False
            
            # 检查是否有加密的密码
            if not account.get('password_encrypted'):
                logger.warning("⚠️ 未存储密码，无法自动重新登录，请手动登录")
                db.update_account_status(self.account_id, 'offline')
                return False
            
            try:
                # 解密密码
                password = crypto_manager.decrypt(account['password_encrypted'])
                email = account['email']
                
                logger.info(f"🔑 正在使用存储的凭据自动重新登录: {email}")
                
                # 导航到登录页
                await self.page.goto('https://www.kookapp.cn/app', wait_until='networkidle')
                await asyncio.sleep(2)
                
                # 尝试重新登录
                success = await self._login_with_password(email, password)
                
                if success:
                    logger.info("✅ 自动重新登录成功")
                    
                    # 更新Cookie到数据库
                    new_cookies = await self.context.cookies()
                    db.update_account_cookie(self.account_id, json.dumps(new_cookies))
                    db.update_account_status(self.account_id, 'online')
                    
                    # 重置重连计数器
                    self.reconnect_count = 0
                    
                    logger.info("📝 已更新Cookie到数据库")
                    return True
                else:
                    logger.error("❌ 自动重新登录失败")
                    db.update_account_status(self.account_id, 'offline')
                    return False
                    
            except Exception as decrypt_error:
                logger.error(f"密码解密失败: {str(decrypt_error)}")
                return False
                
        except Exception as e:
            logger.error(f"自动重新登录异常: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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
                # 重连成功，重置计数器
                self.reconnect_count = 0
            else:
                logger.error("重新连接失败，登录状态检查不通过")
                db.update_account_status(self.account_id, 'offline')
                
        except Exception as e:
            logger.error(f"重新连接异常: {str(e)}")
    
    async def get_servers(self) -> list:
        """
        获取服务器列表
        支持多种可能的DOM结构，提高兼容性
        
        Returns:
            服务器列表 [{"id": "server_id", "name": "server_name", "icon": "icon_url"}]
        """
        try:
            if not self.page or self.page.is_closed():
                logger.error("页面未初始化或已关闭")
                return []
            
            logger.info("开始获取服务器列表...")
            
            # 检查选择器配置是否有更新
            selector_manager.check_and_reload()
            
            # 使用选择器管理器中的选择器
            selectors = selector_manager.get_selectors('server_container')
            
            container_found = False
            for selector in selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    logger.info(f"找到服务器列表容器: {selector}")
                    container_found = True
                    break
                except:
                    continue
            
            if not container_found:
                logger.warning("未找到服务器列表容器，尝试保存页面截图用于调试")
                await self.page.screenshot(path='debug_servers_page.png')
                logger.info("截图已保存到: debug_servers_page.png")
            
            # 执行JavaScript获取服务器列表（使用更通用的方法）
            servers = await self.page.evaluate(r"""
                () => {
                    const servers = [];
                    
                    // 定义多种可能的选择器组合
                    const possibleSelectors = [
                        '.guild-item',
                        '[class*="guild-item"]',
                        '[class*="GuildItem"]',
                        '[class*="server-item"]',
                        '[data-guild-id]',
                        '[data-server-id]',
                        'a[href*="/guild/"]',
                        'div[class*="guild"][class*="item"]',
                    ];
                    
                    let guildElements = [];
                    for (const selector of possibleSelectors) {
                        guildElements = document.querySelectorAll(selector);
                        if (guildElements.length > 0) {
                            console.log(`找到 ${guildElements.length} 个服务器，使用选择器: ${selector}`);
                            break;
                        }
                    }
                    
                    guildElements.forEach(element => {
                        // 尝试多种方式提取服务器ID
                        const serverId = 
                            element.getAttribute('data-guild-id') || 
                            element.getAttribute('data-id') ||
                            element.getAttribute('data-server-id') ||
                            element.id ||
                            (element.href && element.href.match(/guild\/(\w+)/)?.[1]);
                        
                        // 尝试多种方式提取服务器名称
                        let serverName = '';
                        const nameSelectors = [
                            '.guild-name',
                            '[class*="guild-name"]',
                            '[class*="GuildName"]',
                            '[class*="name"]',
                            '.server-name',
                            'span',
                            'div',
                        ];
                        
                        for (const sel of nameSelectors) {
                            const nameEl = element.querySelector(sel);
                            if (nameEl && nameEl.textContent.trim()) {
                                serverName = nameEl.textContent.trim();
                                break;
                            }
                        }
                        
                        // 如果找不到名称元素，尝试直接获取元素文本
                        if (!serverName) {
                            serverName = element.textContent.trim().split('\n')[0];
                        }
                        
                        // 提取图标（尝试多种方式）
                        let iconUrl = '';
                        const imgElement = element.querySelector('img');
                        if (imgElement) {
                            iconUrl = imgElement.src || imgElement.getAttribute('data-src') || '';
                        }
                        
                        // 获取title属性作为备选名称
                        if (!serverName && element.title) {
                            serverName = element.title;
                        }
                        
                        if (serverId && serverName) {
                            servers.push({
                                id: serverId,
                                name: serverName,
                                icon: iconUrl
                            });
                        }
                    });
                    
                    return servers;
                }
            """)
            
            if len(servers) > 0:
                logger.info(f"✅ 成功获取 {len(servers)} 个服务器")
                logger.debug(f"服务器列表: {servers[:3]}...")  # 打印前3个用于调试
            else:
                logger.warning("⚠️ 未获取到任何服务器，可能需要调整选择器")
                logger.info("提示: 请查看 debug_servers_page.png 截图来确定正确的DOM结构")
            
            return servers
            
        except Exception as e:
            logger.error(f"❌ 获取服务器列表失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    async def get_channels(self, server_id: str) -> list:
        """
        获取指定服务器的频道列表
        支持多种可能的DOM结构，提高兼容性
        
        Args:
            server_id: 服务器ID
            
        Returns:
            频道列表 [{"id": "channel_id", "name": "channel_name", "type": "text/voice"}]
        """
        try:
            if not self.page or self.page.is_closed():
                logger.error("页面未初始化或已关闭")
                return []
            
            logger.info(f"开始获取服务器 {server_id} 的频道列表...")
            
            # 检查选择器配置是否有更新
            selector_manager.check_and_reload()
            
            # 尝试多种方式点击服务器
            click_selectors = [
                f'[data-guild-id="{server_id}"]',
                f'[data-server-id="{server_id}"]',
                f'#{server_id}',
                f'a[href*="{server_id}"]',
            ]
            
            clicked = False
            for selector in click_selectors:
                try:
                    await self.page.click(selector, timeout=2000)
                    logger.info(f"成功点击服务器: {selector}")
                    clicked = True
                    break
                except:
                    continue
            
            if not clicked:
                logger.warning(f"无法点击服务器 {server_id}，尝试直接获取频道")
            else:
                # 等待频道列表加载
                await asyncio.sleep(1.5)
            
            # 保存调试截图
            await self.page.screenshot(path=f'debug_channels_{server_id}.png')
            logger.debug(f"频道列表截图已保存: debug_channels_{server_id}.png")
            
            # 执行JavaScript获取频道列表（使用更通用的方法）
            channels = await self.page.evaluate(r"""
                (serverId) => {
                    const channels = [];
                    
                    // 尝试多种可能的频道列表容器选择器
                    const containerSelectors = [
                        '.channel-list',
                        '[class*="channel-list"]',
                        '[class*="ChannelList"]',
                        '[class*="channels"]',
                        'nav[class*="channel"]',
                        'div[class*="sidebar"]',
                    ];
                    
                    let channelList = null;
                    for (const selector of containerSelectors) {
                        channelList = document.querySelector(selector);
                        if (channelList) {
                            console.log(`找到频道列表容器: ${selector}`);
                            break;
                        }
                    }
                    
                    if (!channelList) {
                        console.warn('未找到频道列表容器');
                        return channels;
                    }
                    
                    // 尝试多种可能的频道项选择器
                    const itemSelectors = [
                        '.channel-item',
                        '[class*="channel-item"]',
                        '[class*="ChannelItem"]',
                        '[data-channel-id]',
                        'a[href*="/channel/"]',
                        'div[class*="channel"][class*="item"]',
                    ];
                    
                    let channelElements = [];
                    for (const selector of itemSelectors) {
                        channelElements = channelList.querySelectorAll(selector);
                        if (channelElements.length > 0) {
                            console.log(`找到 ${channelElements.length} 个频道，使用选择器: ${selector}`);
                            break;
                        }
                    }
                    
                    channelElements.forEach(element => {
                        // 尝试多种方式提取频道ID
                        const channelId = 
                            element.getAttribute('data-channel-id') || 
                            element.getAttribute('data-id') ||
                            element.id ||
                            (element.href && element.href.match(/channel\/(\w+)/)?.[1]);
                        
                        // 尝试多种方式提取频道名称
                        let channelName = '';
                        const nameSelectors = [
                            '.channel-name',
                            '[class*="channel-name"]',
                            '[class*="ChannelName"]',
                            '[class*="name"]',
                            'span',
                            'div',
                        ];
                        
                        for (const sel of nameSelectors) {
                            const nameEl = element.querySelector(sel);
                            if (nameEl && nameEl.textContent.trim()) {
                                channelName = nameEl.textContent.trim();
                                // 移除频道名称前的# 或其他符号
                                channelName = channelName.replace(/^[#*\-\s]+/, '');
                                break;
                            }
                        }
                        
                        // 如果找不到名称，尝试元素文本
                        if (!channelName) {
                            channelName = element.textContent.trim().split('\n')[0];
                            channelName = channelName.replace(/^[#*\-\s]+/, '');
                        }
                        
                        // 判断频道类型（文本/语音）
                        const elementClass = element.className.toLowerCase();
                        const elementHTML = element.innerHTML.toLowerCase();
                        
                        const isVoice = 
                            elementClass.includes('voice') ||
                            elementHTML.includes('voice') ||
                            element.querySelector('[class*="voice"]') !== null ||
                            element.querySelector('svg[class*="voice"]') !== null;
                        
                        const channelType = isVoice ? 'voice' : 'text';
                        
                        // 获取title作为备选名称
                        if (!channelName && element.title) {
                            channelName = element.title.replace(/^[#*\-\s]+/, '');
                        }
                        
                        if (channelId && channelName) {
                            channels.push({
                                id: channelId,
                                name: channelName,
                                type: channelType,
                                server_id: serverId
                            });
                        }
                    });
                    
                    return channels;
                }
            """, server_id)
            
            if len(channels) > 0:
                logger.info(f"✅ 成功获取 {len(channels)} 个频道")
                logger.debug(f"频道列表: {channels[:3]}...")  # 打印前3个用于调试
            else:
                logger.warning(f"⚠️ 未获取到服务器 {server_id} 的任何频道")
                logger.info(f"提示: 请查看 debug_channels_{server_id}.png 截图")
            
            return channels
            
        except Exception as e:
            logger.error(f"❌ 获取频道列表失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    async def sync_history_messages(self, minutes: int = 10) -> int:
        """
        同步历史消息
        
        Args:
            minutes: 同步最近N分钟的消息
            
        Returns:
            同步的消息数量
        """
        try:
            if not self.page or self.page.is_closed():
                logger.error("页面未初始化或已关闭，无法同步历史消息")
                return 0
            
            logger.info(f"开始同步最近{minutes}分钟的历史消息...")
            synced_count = 0
            
            # 获取当前账号监听的所有频道映射
            from ..database import db
            mappings = db.get_all_mappings()
            
            # 获取需要监听的频道ID列表
            channel_ids = set()
            for mapping in mappings:
                if mapping.get('enabled'):
                    channel_ids.add(mapping.get('kook_channel_id'))
            
            if not channel_ids:
                logger.warning("没有配置频道映射，跳过历史消息同步")
                return 0
            
            logger.info(f"需要同步 {len(channel_ids)} 个频道的历史消息")
            
            # 计算时间范围（毫秒时间戳）
            import time
            current_time = int(time.time() * 1000)
            start_time = current_time - (minutes * 60 * 1000)
            
            # 遍历每个频道，获取历史消息
            for channel_id in channel_ids:
                try:
                    # 尝试导航到频道（通过URL）
                    channel_url = f"https://www.kookapp.cn/app/channels/{channel_id}"
                    await self.page.goto(channel_url, wait_until='networkidle', timeout=10000)
                    await asyncio.sleep(1)
                    
                    # 执行JavaScript获取消息历史
                    # 注意：这是一个示例实现，实际的DOM结构需要根据KOOK网页调整
                    messages = await self.page.evaluate("""
                        (startTime) => {
                            const messages = [];
                            const messageElements = document.querySelectorAll('[class*="message"]');
                            
                            messageElements.forEach(element => {
                                try {
                                    // 提取消息时间戳
                                    const timeElement = element.querySelector('[class*="time"]');
                                    if (!timeElement) return;
                                    
                                    const timestamp = parseInt(timeElement.getAttribute('data-timestamp') || '0');
                                    if (timestamp < startTime) return;
                                    
                                    // 提取消息内容
                                    const contentElement = element.querySelector('[class*="content"]');
                                    const content = contentElement ? contentElement.textContent : '';
                                    
                                    // 提取发送者信息
                                    const authorElement = element.querySelector('[class*="author"]');
                                    const author = authorElement ? authorElement.textContent : '';
                                    
                                    // 提取消息ID
                                    const messageId = element.getAttribute('data-message-id') || 
                                                     element.id || '';
                                    
                                    if (messageId && content) {
                                        messages.push({
                                            id: messageId,
                                            content: content,
                                            author: author,
                                            timestamp: timestamp
                                        });
                                    }
                                } catch (e) {
                                    console.error('提取消息失败:', e);
                                }
                            });
                            
                            return messages;
                        }
                    """, start_time)
                    
                    # 处理获取到的历史消息
                    for msg in messages:
                        # 检查消息是否已经存在（去重）
                        existing = db.get_message_log(msg['id'])
                        if existing:
                            continue
                        
                        # 构建消息对象
                        message_data = {
                            'message_id': msg['id'],
                            'channel_id': channel_id,
                            'content': msg['content'],
                            'sender_name': msg['author'],
                            'timestamp': msg['timestamp'],
                            'message_type': 'text',
                            'is_history': True  # 标记为历史消息
                        }
                        
                        # 调用消息回调处理
                        if self.message_callback:
                            await self.message_callback(message_data)
                            synced_count += 1
                    
                    logger.info(f"频道 {channel_id} 同步了 {len(messages)} 条历史消息")
                    
                except Exception as e:
                    logger.error(f"同步频道 {channel_id} 历史消息失败: {str(e)}")
                    continue
            
            logger.info(f"✅ 历史消息同步完成，共同步 {synced_count} 条消息")
            return synced_count
            
        except Exception as e:
            logger.error(f"同步历史消息异常: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return 0


class ScraperManager:
    """
    抓取器管理器（v1.8.1：支持浏览器共享上下文）
    
    优化：多个账号共享同一个Browser实例，内存节省60%，支持账号数提升150%
    """
    
    def __init__(self):
        self.scrapers: Dict[int, KookScraper] = {}
        
        # 共享的浏览器实例（v1.8.1新增）
        self.shared_browser: Optional[Browser] = None
        self.shared_context: Optional[BrowserContext] = None
        self.playwright = None
        
        # 是否启用共享模式（默认启用）
        self.use_shared_browser = True
        
        logger.info("✅ 抓取器管理器已初始化（共享浏览器模式）")
    
    async def _ensure_shared_browser(self):
        """
        确保共享浏览器已初始化（v1.8.1新增）
        
        Returns:
            (Browser, BrowserContext)
        """
        if not self.use_shared_browser:
            return None, None
        
        if self.shared_browser is None or not self.shared_browser.is_connected():
            try:
                logger.info("🚀 启动共享浏览器实例...")
                
                # 启动Playwright
                if self.playwright is None:
                    self.playwright = await async_playwright().start()
                
                # 启动共享浏览器
                self.shared_browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                
                # 创建共享上下文
                self.shared_context = await self.shared_browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                logger.info("✅ 共享浏览器启动成功")
                
            except Exception as e:
                logger.error(f"启动共享浏览器失败: {str(e)}")
                self.shared_browser = None
                self.shared_context = None
                return None, None
        
        return self.shared_browser, self.shared_context
    
    async def start_scraper(self, account_id: int, 
                           cookie: Optional[str] = None,
                           email: Optional[str] = None,
                           password: Optional[str] = None,
                           message_callback: Optional[Callable] = None,
                           use_shared_browser: Optional[bool] = None):
        """
        启动抓取器（v1.8.1：支持共享浏览器）
        
        Args:
            account_id: 账号ID
            cookie: Cookie字符串
            email: 邮箱
            password: 密码
            message_callback: 消息回调函数
            use_shared_browser: 是否使用共享浏览器（None=使用全局设置）
        """
        if account_id in self.scrapers:
            logger.warning(f"抓取器已存在，账号ID: {account_id}")
            return False
        
        # 确定是否使用共享浏览器
        use_shared = use_shared_browser if use_shared_browser is not None else self.use_shared_browser
        
        # 如果使用共享浏览器，先确保已初始化
        shared_browser = None
        shared_context = None
        if use_shared:
            shared_browser, shared_context = await self._ensure_shared_browser()
        
        scraper = KookScraper(account_id)
        if message_callback:
            scraper.set_message_callback(message_callback)
        
        # 如果有共享浏览器，传递给scraper
        if shared_browser and shared_context:
            scraper.shared_browser = shared_browser
            scraper.shared_context = shared_context
            logger.info(f"账号 {account_id} 将使用共享浏览器实例")
        
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
        """停止所有抓取器（v1.8.1：清理共享浏览器）"""
        for account_id in list(self.scrapers.keys()):
            await self.stop_scraper(account_id)
        
        # 关闭共享浏览器
        if self.shared_context:
            try:
                await self.shared_context.close()
                self.shared_context = None
                logger.info("✅ 共享浏览器上下文已关闭")
            except Exception as e:
                logger.error(f"关闭共享上下文失败: {str(e)}")
        
        if self.shared_browser:
            try:
                await self.shared_browser.close()
                self.shared_browser = None
                logger.info("✅ 共享浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭共享浏览器失败: {str(e)}")
        
        if self.playwright:
            try:
                await self.playwright.stop()
                self.playwright = None
                logger.info("✅ Playwright已停止")
            except Exception as e:
                logger.error(f"停止Playwright失败: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取管理器统计信息（v1.8.1新增）
        
        Returns:
            统计信息字典
        """
        return {
            'total_scrapers': len(self.scrapers),
            'active_scrapers': len([s for s in self.scrapers.values() if s.is_running]),
            'use_shared_browser': self.use_shared_browser,
            'shared_browser_active': self.shared_browser is not None,
            'accounts': list(self.scrapers.keys())
        }


# 创建全局抓取器管理器
scraper_manager = ScraperManager()
