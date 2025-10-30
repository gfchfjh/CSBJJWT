"""
✅ P2-10优化: 多账号并行抓取优化
限制同时运行的Playwright实例数量，防止资源耗尽
"""
import asyncio
from typing import Dict, Set
from ..utils.logger import logger


class AccountLimiter:
    """
    账号并行抓取限制器
    
    功能：
    1. 限制最大并行抓取数（默认3个）
    2. 超过限制时排队等待
    3. 资源释放后自动启动下一个
    """
    
    def __init__(self, max_parallel: int = 3):
        """
        初始化
        
        Args:
            max_parallel: 最大并行抓取数，默认3
        """
        self.max_parallel = max_parallel
        self.running_accounts: Set[int] = set()
        self.waiting_queue: asyncio.Queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_parallel)
        
        logger.info(f"[AccountLimiter] 初始化完成，最大并行数: {max_parallel}")
    
    async def acquire(self, account_id: int) -> bool:
        """
        获取执行许可
        
        Args:
            account_id: 账号ID
            
        Returns:
            是否成功获取
        """
        try:
            # 检查是否已在运行
            if account_id in self.running_accounts:
                logger.warning(f"[AccountLimiter] 账号 {account_id} 已在运行")
                return False
            
            # 等待获取信号量
            logger.info(f"[AccountLimiter] 账号 {account_id} 等待获取执行许可...")
            
            await self.semaphore.acquire()
            
            # 添加到运行集合
            self.running_accounts.add(account_id)
            
            logger.info(
                f"[AccountLimiter] 账号 {account_id} 获得执行许可 "
                f"(当前运行: {len(self.running_accounts)}/{self.max_parallel})"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"[AccountLimiter] 获取许可失败: {str(e)}")
            return False
    
    def release(self, account_id: int):
        """
        释放执行许可
        
        Args:
            account_id: 账号ID
        """
        try:
            if account_id not in self.running_accounts:
                logger.warning(f"[AccountLimiter] 账号 {account_id} 不在运行列表中")
                return
            
            # 从运行集合移除
            self.running_accounts.discard(account_id)
            
            # 释放信号量
            self.semaphore.release()
            
            logger.info(
                f"[AccountLimiter] 账号 {account_id} 释放执行许可 "
                f"(当前运行: {len(self.running_accounts)}/{self.max_parallel})"
            )
            
        except Exception as e:
            logger.error(f"[AccountLimiter] 释放许可失败: {str(e)}")
    
    def get_status(self) -> Dict:
        """
        获取限制器状态
        
        Returns:
            {
                "max_parallel": int,
                "running_count": int,
                "running_accounts": List[int],
                "available_slots": int
            }
        """
        return {
            "max_parallel": self.max_parallel,
            "running_count": len(self.running_accounts),
            "running_accounts": list(self.running_accounts),
            "available_slots": self.max_parallel - len(self.running_accounts)
        }
    
    def is_running(self, account_id: int) -> bool:
        """检查账号是否正在运行"""
        return account_id in self.running_accounts
    
    def can_start_new(self) -> bool:
        """检查是否可以启动新的抓取器"""
        return len(self.running_accounts) < self.max_parallel


# 全局实例（默认最多3个并行）
account_limiter = AccountLimiter(max_parallel=3)
