"""
KOOK连接管理模块
处理连接、重连、心跳检测等
"""
import asyncio
from typing import Optional
from playwright.async_api import Page
from ..utils.logger import logger
from ..database import db


class ConnectionManager:
    """KOOK连接管理器"""
    
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.reconnect_count = 0
        self.max_reconnect = 5  # 最大重连次数
        self.is_connected = False
    
    async def maintain_connection(self, page: Page) -> bool:
        """
        维护连接（心跳检测+自动重连）
        
        Args:
            page: Playwright页面实例
            
        Returns:
            连接是否正常
        """
        try:
            # 心跳检测
            await page.evaluate('() => console.log("heartbeat")')
            
            # 心跳成功，重置重连计数
            self.reconnect_count = 0
            self.is_connected = True
            return True
            
        except Exception as heartbeat_error:
            logger.warning(f"心跳检测失败: {str(heartbeat_error)}")
            
            # 检查是否达到最大重连次数
            if self.reconnect_count >= self.max_reconnect:
                logger.error(f"账号{self.account_id}达到最大重连次数({self.max_reconnect})，停止重连")
                self.is_connected = False
                db.update_account_status(self.account_id, 'offline')
                return False
            
            self.reconnect_count += 1
            logger.info(f"第{self.reconnect_count}次重连尝试（最多{self.max_reconnect}次）")
            
            # 尝试重新连接
            return await self._reconnect(page)
    
    async def _reconnect(self, page: Page) -> bool:
        """
        重新连接
        
        Args:
            page: Playwright页面实例
            
        Returns:
            重连是否成功
        """
        try:
            logger.info("尝试重新连接...")
            
            # 刷新页面
            await page.reload()
            await asyncio.sleep(3)
            
            # 检查登录状态
            from .auth_manager import AuthManager
            auth_manager = AuthManager(self.account_id, page)
            
            if await auth_manager.check_login_status():
                logger.info("重新连接成功")
                db.update_account_status(self.account_id, 'online')
                # 重连成功，重置计数器
                self.reconnect_count = 0
                self.is_connected = True
                return True
            else:
                logger.error("重新连接失败，登录状态检查不通过")
                db.update_account_status(self.account_id, 'offline')
                self.is_connected = False
                return False
                
        except Exception as e:
            logger.error(f"重新连接异常: {str(e)}")
            self.is_connected = False
            return False
    
    async def auto_relogin_if_expired(self, page: Page) -> bool:
        """
        检测Cookie过期并自动重新登录
        
        Args:
            page: Playwright页面实例
            
        Returns:
            是否重新登录成功
        """
        try:
            logger.info("🔍 检测到连接异常，检查是否需要重新登录...")
            
            from .auth_manager import AuthManager
            from ..utils.crypto import crypto_manager
            
            auth_manager = AuthManager(self.account_id, page)
            
            # 检查当前登录状态
            if await auth_manager.check_login_status():
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
                await page.goto('https://www.kookapp.cn/app', wait_until='networkidle')
                await asyncio.sleep(2)
                
                # 尝试重新登录
                success = await auth_manager.login_with_password(email, password)
                
                if success:
                    logger.info("✅ 自动重新登录成功")
                    
                    # 更新Cookie到数据库
                    import json
                    new_cookies = await page.context.cookies()
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
