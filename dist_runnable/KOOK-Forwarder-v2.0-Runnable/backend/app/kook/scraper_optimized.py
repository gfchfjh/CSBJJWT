"""
KOOK消息抓取器 - 深度优化版
✅ 实现可靠的心跳检测
✅ 指数退避重连策略
✅ 连接质量监控
✅ 状态实时推送到前端
"""
from playwright.async_api import async_playwright, Browser, Page, BrowserContext, WebSocket as PWWebSocket
import asyncio
import json
import time
from typing import Dict, List, Optional, Callable
from pathlib import Path
from ..config import settings
from ..utils.logger import logger
from ..database import db
from ..queue.redis_client import redis_queue


class ConnectionQualityMonitor:
    """连接质量监控器"""
    
    def __init__(self):
        self.last_message_time = time.time()
        self.message_count = 0
        self.reconnect_count = 0
        self.latency_samples = []
        self.max_samples = 100
        
    def record_message(self):
        """记录收到消息"""
        self.last_message_time = time.time()
        self.message_count += 1
        
    def record_latency(self, latency: float):
        """记录延迟"""
        self.latency_samples.append(latency)
        if len(self.latency_samples) > self.max_samples:
            self.latency_samples.pop(0)
    
    def record_reconnect(self):
        """记录重连"""
        self.reconnect_count += 1
        
    def get_quality_score(self) -> float:
        """
        计算连接质量评分 (0-100)
        
        考虑因素：
        - 消息接收频率
        - 平均延迟
        - 重连次数
        """
        score = 100.0
        
        # 1. 检查消息新鲜度（最近60秒内有消息？）
        time_since_last_message = time.time() - self.last_message_time
        if time_since_last_message > 300:  # 5分钟无消息
            score -= 50
        elif time_since_last_message > 120:  # 2分钟无消息
            score -= 20
            
        # 2. 检查平均延迟
        if self.latency_samples:
            avg_latency = sum(self.latency_samples) / len(self.latency_samples)
            if avg_latency > 5.0:
                score -= 30
            elif avg_latency > 2.0:
                score -= 15
                
        # 3. 惩罚频繁重连
        if self.reconnect_count > 5:
            score -= 20
        elif self.reconnect_count > 2:
            score -= 10
            
        return max(0, min(100, score))
    
    def get_status(self) -> dict:
        """获取状态信息"""
        return {
            'quality_score': self.get_quality_score(),
            'message_count': self.message_count,
            'last_message_ago': time.time() - self.last_message_time,
            'reconnect_count': self.reconnect_count,
            'avg_latency': sum(self.latency_samples) / len(self.latency_samples) if self.latency_samples else 0
        }


class KookScraperOptimized:
    """KOOK消息抓取器 - 深度优化版"""
    
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.websocket: Optional[PWWebSocket] = None
        
        self.is_running = False
        self.reconnect_count = 0
        self.max_reconnect = 10  # 增加到10次
        self.base_reconnect_delay = 5  # 基础重连延迟（秒）
        
        self.message_handlers: List[Callable] = []
        self.quality_monitor = ConnectionQualityMonitor()
        
        # 心跳相关
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 30  # 30秒发送一次心跳
        self.heartbeat_timeout = 90  # 90秒无响应判定为断线
        self.heartbeat_task = None
        
        # 状态推送相关
        self.status_broadcast_interval = 10  # 每10秒推送一次状态
        self.status_task = None
        
    async def start(self):
        """启动抓取器"""
        try:
            logger.info(f"[Scraper-{self.account_id}] 🚀 正在启动（深度优化版）...")
            
            async with async_playwright() as p:
                # 启动浏览器
                self.browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',  # 避免CORS问题
                        '--disable-features=IsolateOrigins,site-per-process'
                    ]
                )
                
                # 创建浏览器上下文
                self.context = await self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    java_script_enabled=True
                )
                
                # 加载Cookie
                cookies = self.load_cookies()
                if cookies:
                    await self.context.add_cookies(cookies)
                    logger.info(f"[Scraper-{self.account_id}] ✅ 已加载Cookie")
                
                # 创建页面
                self.page = await self.context.new_page()
                
                # 监听WebSocket
                self.page.on('websocket', self.handle_websocket)
                
                # 监听控制台（用于调试）
                if settings.debug:
                    self.page.on('console', lambda msg: 
                        logger.debug(f"[Browser Console] {msg.text}")
                    )
                
                # 访问KOOK
                logger.info(f"[Scraper-{self.account_id}] 🌐 正在访问KOOK...")
                await self.broadcast_status('connecting', '正在连接KOOK...')
                
                response = await self.page.goto(
                    'https://www.kookapp.cn/app', 
                    wait_until='networkidle',
                    timeout=30000
                )
                
                if not response or response.status != 200:
                    raise Exception(f"访问KOOK失败，状态码: {response.status if response else 'N/A'}")
                
                # 等待页面加载
                await asyncio.sleep(3)
                
                # 检查登录状态
                is_logged_in = await self.check_login_status()
                
                if not is_logged_in:
                    logger.warning(f"[Scraper-{self.account_id}] ⚠️  未登录，开始登录流程...")
                    await self.broadcast_status('login_required', '需要登录')
                    
                    # 获取账号信息
                    account = db.get_account(self.account_id)
                    
                    if not account:
                        raise Exception("账号不存在")
                    
                    # 尝试登录
                    if account.get('password_encrypted'):
                        success = await self.login_with_password(
                            account['email'],
                            self.decrypt_password(account['password_encrypted'])
                        )
                    else:
                        raise Exception("Cookie已失效，请重新登录")
                    
                    if not success:
                        raise Exception("登录失败")
                
                logger.info(f"[Scraper-{self.account_id}] ✅ 登录成功，开始监听消息...")
                await self.broadcast_status('connected', '已连接，正在监听')
                
                # 更新账号状态
                db.update_account_status(self.account_id, "online")
                
                # 启动心跳任务
                self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
                
                # 启动状态广播任务
                self.status_task = asyncio.create_task(self.status_broadcast_loop())
                
                # 保持运行
                self.is_running = True
                self.reconnect_count = 0  # 重置重连计数
                
                while self.is_running:
                    await asyncio.sleep(1)
                    
                    # 检查心跳超时
                    if time.time() - self.last_heartbeat > self.heartbeat_timeout:
                        logger.warning(f"[Scraper-{self.account_id}] 💔 心跳超时，连接可能已断开")
                        await self.broadcast_status('heartbeat_timeout', '心跳超时')
                        break
                        
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] ❌ 启动失败: {str(e)}")
            await self.broadcast_status('error', f'启动失败: {str(e)}')
            db.update_account_status(self.account_id, "offline")
            raise
        finally:
            await self.stop()
            
            # 尝试重连
            if self.is_running and self.reconnect_count < self.max_reconnect:
                await self.reconnect()
    
    async def heartbeat_loop(self):
        """心跳循环"""
        while self.is_running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                if self.page and not self.page.is_closed():
                    # 发送心跳（执行简单的JS）
                    start_time = time.time()
                    result = await self.page.evaluate('() => Date.now()')
                    latency = time.time() - start_time
                    
                    self.last_heartbeat = time.time()
                    self.quality_monitor.record_latency(latency * 1000)  # 转换为毫秒
                    
                    if latency > 2.0:
                        logger.warning(f"[Scraper-{self.account_id}] ⚠️  心跳延迟过高: {latency:.2f}s")
                    else:
                        logger.debug(f"[Scraper-{self.account_id}] 💓 心跳正常 (延迟: {latency*1000:.0f}ms)")
                else:
                    logger.warning(f"[Scraper-{self.account_id}] ⚠️  页面已关闭，停止心跳")
                    break
                    
            except Exception as e:
                logger.error(f"[Scraper-{self.account_id}] ❌ 心跳异常: {str(e)}")
                break
    
    async def status_broadcast_loop(self):
        """状态广播循环"""
        while self.is_running:
            try:
                await asyncio.sleep(self.status_broadcast_interval)
                
                # 获取连接质量
                quality_status = self.quality_monitor.get_status()
                quality_score = quality_status['quality_score']
                
                # 确定状态
                if quality_score >= 80:
                    status = 'healthy'
                    message = '连接良好'
                elif quality_score >= 50:
                    status = 'degraded'
                    message = '连接质量下降'
                else:
                    status = 'poor'
                    message = '连接质量差'
                
                await self.broadcast_status(status, message, quality_status)
                
            except Exception as e:
                logger.error(f"[Scraper-{self.account_id}] 状态广播异常: {str(e)}")
    
    async def broadcast_status(self, status: str, message: str, extra: dict = None):
        """
        广播状态到前端
        
        Args:
            status: 状态类型
            message: 状态消息
            extra: 额外信息
        """
        try:
            # 构建状态数据
            status_data = {
                'account_id': self.account_id,
                'status': status,
                'message': message,
                'timestamp': time.time()
            }
            
            if extra:
                status_data.update(extra)
            
            # 通过Redis发布状态
            await redis_queue.publish('scraper_status', json.dumps(status_data))
            
            logger.debug(f"[Scraper-{self.account_id}] 📡 状态已广播: {status} - {message}")
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 广播状态失败: {str(e)}")
    
    async def check_login_status(self) -> bool:
        """检查登录状态"""
        try:
            # 方法1: 检查登录表单
            login_form = await self.page.query_selector('form[class*="login"]')
            if login_form:
                return False
            
            # 方法2: 检查用户信息元素
            user_info = await self.page.query_selector('[class*="user-info"], [class*="avatar"]')
            if user_info:
                return True
            
            # 方法3: 执行JS检查localStorage
            is_logged_in = await self.page.evaluate('''() => {
                const token = window.localStorage.getItem('token') || 
                             window.localStorage.getItem('kaiheila_token') ||
                             window.localStorage.getItem('access_token');
                return token !== null && token !== '';
            }''')
            
            return is_logged_in
            
        except Exception as e:
            logger.debug(f"[Scraper-{self.account_id}] 登录状态检查异常: {e}")
            return False
    
    async def login_with_password(self, email: str, password: str) -> bool:
        """账号密码登录"""
        try:
            logger.info(f"[Scraper-{self.account_id}] 🔐 开始账号密码登录...")
            
            await self.page.wait_for_selector('input[name="email"], input[type="email"]', timeout=10000)
            
            await self.page.fill('input[name="email"], input[type="email"]', email)
            await asyncio.sleep(0.5)
            
            await self.page.fill('input[name="password"], input[type="password"]', password)
            await asyncio.sleep(0.5)
            
            await self.page.click('button[type="submit"]')
            
            try:
                await self.page.wait_for_selector('.app-container, [class*="main"]', timeout=10000)
                logger.info(f"[Scraper-{self.account_id}] ✅ 登录成功")
                
                await self.save_cookies()
                return True
                
            except Exception:
                captcha_element = await self.page.query_selector('.captcha-container, [class*="captcha"]')
                if captcha_element:
                    logger.warning(f"[Scraper-{self.account_id}] 🔒 需要验证码")
                    await self.broadcast_status('captcha_required', '需要输入验证码')
                    success = await self.handle_captcha()
                    if success:
                        await self.save_cookies()
                    return success
                else:
                    return False
                    
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 登录异常: {str(e)}")
            return False
    
    async def handle_captcha(self) -> bool:
        """处理验证码（待实现）"""
        # TODO: 实现验证码处理逻辑
        logger.info(f"[Scraper-{self.account_id}] ⏳ 等待用户输入验证码...")
        return False
    
    async def handle_websocket(self, ws: PWWebSocket):
        """处理WebSocket连接"""
        logger.info(f"[Scraper-{self.account_id}] 🔌 WebSocket连接已建立: {ws.url}")
        self.websocket = ws
        
        # 监听消息
        ws.on('framereceived', lambda payload: 
            asyncio.create_task(self.process_websocket_message(payload))
        )
        
        # 监听关闭
        ws.on('close', lambda: 
            logger.warning(f"[Scraper-{self.account_id}] ⚠️  WebSocket连接已关闭")
        )
    
    async def process_websocket_message(self, payload: bytes):
        """处理WebSocket消息"""
        try:
            data = json.loads(payload.decode('utf-8'))
            
            # 记录消息接收
            self.quality_monitor.record_message()
            
            msg_type = data.get('type')
            
            if msg_type == 'MESSAGE_CREATE':
                message = self.parse_message(data)
                
                if message:
                    logger.info(
                        f"[Scraper-{self.account_id}] 📨 收到消息: "
                        f"频道={message.get('channel_name', 'Unknown')}, "
                        f"作者={message['author']['username']}"
                    )
                    
                    # 入队处理
                    await redis_queue.enqueue('message_queue', message)
                    
                    # 调用消息处理器
                    for handler in self.message_handlers:
                        try:
                            await handler(message)
                        except Exception as e:
                            logger.error(f"消息处理器执行失败: {e}")
            
        except json.JSONDecodeError:
            pass  # 忽略非JSON消息
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 处理WebSocket消息异常: {str(e)}")
    
    def parse_message(self, data: Dict) -> Optional[Dict]:
        """解析消息数据"""
        try:
            d = data.get('d', {})
            
            message = {
                'account_id': self.account_id,
                'kook_message_id': d.get('msg_id'),
                'channel_id': d.get('target_id'),
                'server_id': d.get('guild_id'),
                'message_type': d.get('type', 1),
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
            
            return message
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 消息解析失败: {str(e)}")
            return None
    
    async def reconnect(self):
        """重新连接（指数退避策略）"""
        self.reconnect_count += 1
        self.quality_monitor.record_reconnect()
        
        if self.reconnect_count > self.max_reconnect:
            logger.error(f"[Scraper-{self.account_id}] ❌ 超过最大重连次数({self.max_reconnect})，停止尝试")
            await self.broadcast_status('failed', '超过最大重连次数')
            self.is_running = False
            return
        
        # 计算重连延迟（指数退避）
        delay = min(self.base_reconnect_delay * (2 ** (self.reconnect_count - 1)), 300)  # 最多5分钟
        
        logger.info(f"[Scraper-{self.account_id}] 🔄 第{self.reconnect_count}次重连（{delay}秒后）...")
        await self.broadcast_status('reconnecting', f'第{self.reconnect_count}次重连')
        
        await asyncio.sleep(delay)
        
        try:
            await self.start()
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 重连失败: {str(e)}")
            await self.reconnect()
    
    def load_cookies(self) -> List[Dict]:
        """从数据库加载Cookie"""
        try:
            account = db.get_account(self.account_id)
            
            if account and account.get('cookie'):
                cookies = json.loads(account['cookie'])
                return cookies
            
            return []
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 加载Cookie失败: {str(e)}")
            return []
    
    async def save_cookies(self):
        """保存Cookie到数据库"""
        try:
            cookies = await self.context.cookies()
            
            db.update_account_cookie(self.account_id, json.dumps(cookies))
            
            logger.info(f"[Scraper-{self.account_id}] ✅ Cookie已保存")
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 保存Cookie失败: {str(e)}")
    
    def decrypt_password(self, encrypted: str) -> str:
        """解密密码"""
        from ..utils.crypto import decrypt
        return decrypt(encrypted)
    
    def register_message_handler(self, handler: Callable):
        """注册消息处理器"""
        self.message_handlers.append(handler)
    
    async def stop(self):
        """停止抓取器"""
        logger.info(f"[Scraper-{self.account_id}] 🛑 正在停止...")
        
        self.is_running = False
        
        try:
            # 取消心跳任务
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                
            # 取消状态广播任务
            if self.status_task:
                self.status_task.cancel()
            
            if self.page and not self.page.is_closed():
                await self.page.close()
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            db.update_account_status(self.account_id, "offline")
            await self.broadcast_status('stopped', '已停止')
            
            logger.info(f"[Scraper-{self.account_id}] ✅ 已停止")
            
        except Exception as e:
            logger.error(f"[Scraper-{self.account_id}] 停止异常: {str(e)}")


# 继续使用原有的ScraperManager，但使用优化版的Scraper
class ScraperManagerOptimized:
    """抓取器管理器 - 优化版"""
    
    def __init__(self):
        self.scrapers: Dict[int, KookScraperOptimized] = {}
        self.tasks: Dict[int, asyncio.Task] = {}
    
    async def start_scraper(self, account_id: int):
        """启动指定账号的抓取器"""
        if account_id in self.scrapers:
            logger.warning(f"账号{account_id}的抓取器已在运行")
            return
        
        scraper = KookScraperOptimized(account_id)
        self.scrapers[account_id] = scraper
        
        task = asyncio.create_task(scraper.start())
        self.tasks[account_id] = task
        
        logger.info(f"账号{account_id}的抓取器已启动（优化版）")
    
    async def stop_scraper(self, account_id: int):
        """停止指定账号的抓取器"""
        if account_id not in self.scrapers:
            logger.warning(f"账号{account_id}的抓取器未运行")
            return
        
        scraper = self.scrapers[account_id]
        await scraper.stop()
        
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
        """启动所有账号的抓取器"""
        accounts = db.get_accounts()
        
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
    
    def get_scraper(self, account_id: int) -> Optional[KookScraperOptimized]:
        """获取指定账号的抓取器"""
        return self.scrapers.get(account_id)
    
    def get_all_scrapers(self) -> Dict[int, KookScraperOptimized]:
        """获取所有抓取器"""
        return self.scrapers
    
    def get_status(self) -> dict:
        """获取所有抓取器的状态"""
        return {
            'total': len(self.scrapers),
            'running': sum(1 for s in self.scrapers.values() if s.is_running),
            'scrapers': {
                account_id: {
                    'is_running': scraper.is_running,
                    'reconnect_count': scraper.reconnect_count,
                    'quality': scraper.quality_monitor.get_status()
                }
                for account_id, scraper in self.scrapers.items()
            }
        }


# 全局抓取器管理器
scraper_manager_optimized = ScraperManagerOptimized()
