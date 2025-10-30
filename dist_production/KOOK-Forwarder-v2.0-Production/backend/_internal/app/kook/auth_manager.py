"""
KOOK认证管理模块
处理账号密码登录、Cookie验证等认证相关功能
"""
import asyncio
from typing import Optional, Dict
from playwright.async_api import Page, TimeoutError
from ..utils.logger import logger
from ..utils.captcha_solver import get_captcha_solver
from ..database import db


class AuthManager:
    """KOOK认证管理器"""
    
    def __init__(self, account_id: int, page: Page):
        self.account_id = account_id
        self.page = page
    
    async def login_with_password(self, email: str, password: str) -> bool:
        """
        使用账号密码登录
        
        Args:
            email: 邮箱
            password: 密码
            
        Returns:
            是否成功
        """
        try:
            logger.info(f"开始账号密码登录: {email}")
            
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
            if await self._check_captcha_required():
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
                logger.info("📝 2Captcha未配置，将尝试本地OCR识别")
            
            # 如果2Captcha失败，尝试本地OCR
            if not captcha_code:
                captcha_code = await self._try_local_ocr(captcha_image_url)
            
            # 如果自动识别和本地OCR都失败，使用手动输入
            if not captcha_code:
                logger.info("等待用户手动输入验证码...")
                captcha_code = await self._wait_for_manual_captcha_input(captcha_image_url)
                
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
    
    async def _try_local_ocr(self, image_url: str) -> Optional[str]:
        """
        尝试使用本地OCR识别验证码
        
        Args:
            image_url: 验证码图片URL
            
        Returns:
            识别结果，失败返回None
        """
        try:
            logger.info("🔍 尝试使用本地OCR识别验证码...")
            
            import ddddocr
            import aiohttp
            
            # 下载验证码图片到内存
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        image_bytes = await resp.read()
                        
                        # 使用ddddocr识别
                        ocr = ddddocr.DdddOcr(show_ad=False)
                        captcha_code = ocr.classification(image_bytes)
                        
                        if captcha_code and len(captcha_code) > 0:
                            logger.info(f"✅ 本地OCR识别成功: {captcha_code}")
                            return captcha_code
                        else:
                            logger.warning("⚠️ 本地OCR识别结果为空")
                    else:
                        logger.warning(f"⚠️ 下载验证码图片失败: HTTP {resp.status}")
            
            return None
            
        except ImportError:
            logger.warning("⚠️ ddddocr未安装，跳过本地OCR识别")
            logger.info("💡 提示：可以通过 pip install ddddocr 安装本地OCR支持")
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ 本地OCR识别失败: {str(e)}")
            return None
    
    async def _wait_for_manual_captcha_input(self, image_url: str, timeout: int = 120) -> Optional[str]:
        """
        等待用户手动输入验证码
        
        Args:
            image_url: 验证码图片URL
            timeout: 超时时间（秒）
            
        Returns:
            验证码字符串
        """
        import json
        
        # 存储验证码信息到数据库，让前端轮询获取
        db.set_system_config(
            f"captcha_required_{self.account_id}",
            json.dumps({
                "image_url": image_url,
                "timestamp": asyncio.get_event_loop().time()
            })
        )
        
        # 等待用户输入验证码
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
                    # 安全验证: 验证域名，防止钓鱼攻击
                    if src.startswith('http'):
                        from urllib.parse import urlparse
                        parsed = urlparse(src)
                        allowed_domains = ['kookapp.cn', 'kaiheila.cn', 'www.kookapp.cn', 'www.kaiheila.cn']
                        
                        if parsed.netloc not in allowed_domains:
                            logger.error(f"⚠️ 安全警告：验证码图片来自不安全的域名: {parsed.netloc}")
                            return None
                        
                        logger.info(f"✅ 验证码图片域名验证通过: {parsed.netloc}")
                        return src
                    
                    # 如果是base64，直接返回
                    if src.startswith('data:image'):
                        return src
                    
                    # 如果是相对路径，拼接完整URL
                    full_url = f"https://www.kookapp.cn{src}"
                    return full_url
            
            return None
            
        except Exception as e:
            logger.error(f"获取验证码图片异常: {str(e)}")
            return None
    
    async def check_login_status(self) -> bool:
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
            
            # 方式3: 检查用户信息元素
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
            
            # 方式4: 等待3秒后再次检查URL
            logger.debug("等待3秒后再次检查...")
            await asyncio.sleep(3)
            
            current_url = self.page.url
            if '/app' in current_url and 'login' not in current_url:
                logger.info("✅ 延迟检查：已跳转到主页")
                return True
            
            # 方式5: 检查localStorage中是否有token
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
            
            logger.error("❌ 所有登录状态检查均失败")
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态异常: {str(e)}")
            return False
