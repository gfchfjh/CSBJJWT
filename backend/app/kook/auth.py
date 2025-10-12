"""KOOK认证模块"""
import json
from typing import Dict, Optional, List
from playwright.async_api import Page, Browser

from app.utils.logger import logger
from app.utils.crypto import crypto
from app.database import db


class KookAuth:
    """KOOK认证管理类"""
    
    async def login_with_password(self, page: Page, email: str, password: str) -> bool:
        """使用账号密码登录
        
        Args:
            page: Playwright页面对象
            email: 邮箱
            password: 密码
            
        Returns:
            是否登录成功
        """
        try:
            logger.info(f"开始使用账号密码登录: {email}")
            
            # 访问登录页面
            await page.goto('https://www.kookapp.cn/app/login')
            await page.wait_for_load_state('networkidle')
            
            # 填写表单
            await page.fill('input[type="email"]', email)
            await page.fill('input[type="password"]', password)
            
            # 点击登录按钮
            await page.click('button[type="submit"]')
            
            # 等待登录完成或验证码出现
            try:
                # 等待跳转到主页面
                await page.wait_for_url('**/app/channels/**', timeout=10000)
                logger.info("登录成功")
                
                # 保存Cookie
                cookies = await page.context.cookies()
                return await self.save_cookies(email, cookies)
                
            except Exception as e:
                # 可能需要验证码
                logger.warning(f"登录可能需要验证码: {e}")
                # TODO: 实现验证码处理
                return False
                
        except Exception as e:
            logger.error(f"登录失败: {e}")
            return False
    
    async def login_with_cookies(self, page: Page, cookies: List[Dict]) -> bool:
        """使用Cookie登录
        
        Args:
            page: Playwright页面对象
            cookies: Cookie列表
            
        Returns:
            是否登录成功
        """
        try:
            logger.info("开始使用Cookie登录")
            
            # 添加Cookie
            await page.context.add_cookies(cookies)
            
            # 访问主页面
            await page.goto('https://www.kookapp.cn/app')
            await page.wait_for_load_state('networkidle')
            
            # 检查是否登录成功（查找特定元素）
            try:
                await page.wait_for_selector('[class*="user-panel"]', timeout=5000)
                logger.info("Cookie登录成功")
                return True
            except:
                logger.error("Cookie已失效")
                return False
                
        except Exception as e:
            logger.error(f"Cookie登录失败: {e}")
            return False
    
    async def save_cookies(self, email: str, cookies: List[Dict]) -> bool:
        """保存Cookie到数据库
        
        Args:
            email: 邮箱
            cookies: Cookie列表
            
        Returns:
            是否保存成功
        """
        try:
            cookie_str = json.dumps(cookies)
            
            # 更新或插入账号
            accounts = db.get_accounts()
            account = next((a for a in accounts if a['email'] == email), None)
            
            if account:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE accounts 
                        SET cookie = ?, status = 'online', last_active = datetime('now')
                        WHERE email = ?
                    """, (cookie_str, email))
            else:
                db.add_account(email=email, cookie=cookie_str)
            
            logger.info(f"Cookie已保存: {email}")
            return True
            
        except Exception as e:
            logger.error(f"保存Cookie失败: {e}")
            return False
    
    def load_cookies(self, email: str) -> Optional[List[Dict]]:
        """从数据库加载Cookie
        
        Args:
            email: 邮箱
            
        Returns:
            Cookie列表，如果不存在返回None
        """
        try:
            accounts = db.get_accounts()
            account = next((a for a in accounts if a['email'] == email), None)
            
            if account and account['cookie']:
                return json.loads(account['cookie'])
            
            return None
            
        except Exception as e:
            logger.error(f"加载Cookie失败: {e}")
            return None
