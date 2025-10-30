"""
多账号并发管理器
✅ P0-19: 支持多账号同时监听，互不干扰
"""
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from ..utils.logger import logger
from ..kook.scraper_optimized import ScraperOptimized


@dataclass
class AccountStatus:
    """账号状态"""
    account_id: int
    email: str
    online: bool
    scraper: Optional[ScraperOptimized]
    server_count: int
    channel_count: int
    message_count: int
    error_count: int
    last_active: datetime
    connection_quality: float
    

class MultiAccountManager:
    """多账号管理器"""
    
    def __init__(self):
        self.accounts: Dict[int, AccountStatus] = {}
        self.scrapers: Dict[int, ScraperOptimized] = {}
        self.tasks: Dict[int, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        self._running = False
        
    async def start(self):
        """启动管理器"""
        self._running = True
        logger.info("多账号管理器已启动")
        
    async def stop(self):
        """停止管理器"""
        self._running = False
        
        # 停止所有scraper
        tasks = []
        for account_id, scraper in self.scrapers.items():
            tasks.append(self.stop_account(account_id))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("多账号管理器已停止")
        
    async def add_account(self, account_id: int, account_data: dict) -> bool:
        """
        添加账号并启动监听
        
        Args:
            account_id: 账号ID
            account_data: 账号数据（包含email, cookie等）
            
        Returns:
            是否成功添加
        """
        async with self._lock:
            if account_id in self.accounts:
                logger.warning(f"账号{account_id}已存在")
                return False
            
            try:
                # 创建账号状态
                status = AccountStatus(
                    account_id=account_id,
                    email=account_data['email'],
                    online=False,
                    scraper=None,
                    server_count=0,
                    channel_count=0,
                    message_count=0,
                    error_count=0,
                    last_active=datetime.now(),
                    connection_quality=0.0
                )
                
                self.accounts[account_id] = status
                
                # 启动scraper
                await self.start_account(account_id, account_data)
                
                logger.info(f"账号{account_id}({account_data['email']})已添加")
                return True
                
            except Exception as e:
                logger.error(f"添加账号{account_id}失败: {str(e)}")
                return False
    
    async def remove_account(self, account_id: int) -> bool:
        """
        移除账号并停止监听
        
        Args:
            account_id: 账号ID
            
        Returns:
            是否成功移除
        """
        async with self._lock:
            if account_id not in self.accounts:
                logger.warning(f"账号{account_id}不存在")
                return False
            
            try:
                # 停止scraper
                await self.stop_account(account_id)
                
                # 移除账号
                del self.accounts[account_id]
                
                logger.info(f"账号{account_id}已移除")
                return True
                
            except Exception as e:
                logger.error(f"移除账号{account_id}失败: {str(e)}")
                return False
    
    async def start_account(self, account_id: int, account_data: dict):
        """启动账号的scraper"""
        try:
            # 创建scraper
            scraper = ScraperOptimized(
                account_id=account_id,
                cookie=account_data.get('cookie'),
                email=account_data.get('email'),
                password=account_data.get('password')
            )
            
            self.scrapers[account_id] = scraper
            
            # 创建后台任务
            task = asyncio.create_task(self._run_scraper(account_id, scraper))
            self.tasks[account_id] = task
            
            # 更新状态
            if account_id in self.accounts:
                self.accounts[account_id].scraper = scraper
                self.accounts[account_id].online = True
            
            logger.info(f"账号{account_id}的scraper已启动")
            
        except Exception as e:
            logger.error(f"启动账号{account_id}的scraper失败: {str(e)}")
            raise
    
    async def stop_account(self, account_id: int):
        """停止账号的scraper"""
        try:
            # 取消任务
            if account_id in self.tasks:
                task = self.tasks[account_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.tasks[account_id]
            
            # 停止scraper
            if account_id in self.scrapers:
                scraper = self.scrapers[account_id]
                await scraper.stop()
                del self.scrapers[account_id]
            
            # 更新状态
            if account_id in self.accounts:
                self.accounts[account_id].scraper = None
                self.accounts[account_id].online = False
            
            logger.info(f"账号{account_id}的scraper已停止")
            
        except Exception as e:
            logger.error(f"停止账号{account_id}的scraper失败: {str(e)}")
    
    async def restart_account(self, account_id: int, account_data: dict) -> bool:
        """
        重启账号的scraper
        
        Args:
            account_id: 账号ID
            account_data: 账号数据
            
        Returns:
            是否成功重启
        """
        try:
            await self.stop_account(account_id)
            await asyncio.sleep(2)  # 等待2秒
            await self.start_account(account_id, account_data)
            return True
        except Exception as e:
            logger.error(f"重启账号{account_id}失败: {str(e)}")
            return False
    
    async def _run_scraper(self, account_id: int, scraper: ScraperOptimized):
        """运行scraper的后台任务"""
        try:
            await scraper.start()
            
            while self._running:
                # 更新账号状态
                if account_id in self.accounts:
                    status = self.accounts[account_id]
                    status.last_active = datetime.now()
                    status.connection_quality = scraper.get_connection_quality()
                    status.message_count = scraper.get_message_count()
                    status.error_count = scraper.get_error_count()
                
                await asyncio.sleep(5)  # 每5秒更新一次
                
        except asyncio.CancelledError:
            logger.info(f"账号{account_id}的scraper任务已取消")
            raise
        except Exception as e:
            logger.error(f"账号{account_id}的scraper运行异常: {str(e)}")
            
            # 标记为离线
            if account_id in self.accounts:
                self.accounts[account_id].online = False
                self.accounts[account_id].error_count += 1
    
    def get_account_status(self, account_id: int) -> Optional[AccountStatus]:
        """获取账号状态"""
        return self.accounts.get(account_id)
    
    def get_all_accounts(self) -> List[AccountStatus]:
        """获取所有账号状态"""
        return list(self.accounts.values())
    
    def get_online_count(self) -> int:
        """获取在线账号数"""
        return sum(1 for status in self.accounts.values() if status.online)
    
    def get_total_count(self) -> int:
        """获取总账号数"""
        return len(self.accounts)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'total': self.get_total_count(),
            'online': self.get_online_count(),
            'offline': self.get_total_count() - self.get_online_count(),
            'total_servers': sum(s.server_count for s in self.accounts.values()),
            'total_channels': sum(s.channel_count for s in self.accounts.values()),
            'total_messages': sum(s.message_count for s in self.accounts.values()),
            'total_errors': sum(s.error_count for s in self.accounts.values())
        }


# 全局实例
multi_account_manager = MultiAccountManager()
