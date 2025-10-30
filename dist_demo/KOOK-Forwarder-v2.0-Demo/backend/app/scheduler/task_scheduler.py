"""
定时任务调度器
✅ P1-10: Cron表达式定时任务
"""
import asyncio
from typing import Dict, Callable, Optional, List
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from ..utils.logger import logger


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.tasks: Dict[str, Dict] = {}
        
        # 统计
        self.stats = {
            'total_tasks': 0,
            'running_tasks': 0,
            'total_executions': 0,
            'failed_executions': 0
        }
    
    async def start(self):
        """启动调度器"""
        self.scheduler.start()
        logger.info("任务调度器已启动")
    
    async def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("任务调度器已停止")
    
    def add_cron_task(
        self,
        task_id: str,
        func: Callable,
        cron_expression: str,
        args: tuple = (),
        kwargs: dict = None,
        description: str = ''
    ):
        """
        添加Cron任务
        
        Args:
            task_id: 任务ID
            func: 任务函数
            cron_expression: Cron表达式
            args: 位置参数
            kwargs: 关键字参数
            description: 任务描述
            
        Cron表达式格式:
        秒 分 时 日 月 周
        
        示例:
        - "0 0 * * *" - 每天0点
        - "0 */5 * * *" - 每5分钟
        - "0 0 12 * * 0" - 每周日12点
        """
        try:
            kwargs = kwargs or {}
            
            # 解析Cron表达式
            parts = cron_expression.split()
            
            if len(parts) == 5:
                # 标准cron格式（无秒）
                minute, hour, day, month, day_of_week = parts
                second = '0'
            elif len(parts) == 6:
                # 扩展cron格式（带秒）
                second, minute, hour, day, month, day_of_week = parts
            else:
                raise ValueError(f"Invalid cron expression: {cron_expression}")
            
            # 创建触发器
            trigger = CronTrigger(
                second=second,
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            )
            
            # 添加任务
            job = self.scheduler.add_job(
                self._wrap_task(func, task_id),
                trigger=trigger,
                args=args,
                kwargs=kwargs,
                id=task_id,
                replace_existing=True
            )
            
            # 记录任务信息
            self.tasks[task_id] = {
                'id': task_id,
                'type': 'cron',
                'cron_expression': cron_expression,
                'function': func.__name__,
                'description': description,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'created_at': datetime.now().isoformat()
            }
            
            self.stats['total_tasks'] += 1
            
            logger.info(f"Cron任务已添加: {task_id}, 表达式: {cron_expression}")
            
        except Exception as e:
            logger.error(f"添加Cron任务失败: {str(e)}")
            raise
    
    def add_interval_task(
        self,
        task_id: str,
        func: Callable,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        args: tuple = (),
        kwargs: dict = None,
        description: str = ''
    ):
        """
        添加间隔任务
        
        Args:
            task_id: 任务ID
            func: 任务函数
            seconds: 间隔秒数
            minutes: 间隔分钟数
            hours: 间隔小时数
            args: 位置参数
            kwargs: 关键字参数
            description: 任务描述
        """
        try:
            kwargs = kwargs or {}
            
            # 创建触发器
            trigger = IntervalTrigger(
                seconds=seconds,
                minutes=minutes,
                hours=hours
            )
            
            # 添加任务
            job = self.scheduler.add_job(
                self._wrap_task(func, task_id),
                trigger=trigger,
                args=args,
                kwargs=kwargs,
                id=task_id,
                replace_existing=True
            )
            
            # 记录任务信息
            self.tasks[task_id] = {
                'id': task_id,
                'type': 'interval',
                'interval': f"{hours}h {minutes}m {seconds}s",
                'function': func.__name__,
                'description': description,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'created_at': datetime.now().isoformat()
            }
            
            self.stats['total_tasks'] += 1
            
            logger.info(f"间隔任务已添加: {task_id}, 间隔: {hours}h {minutes}m {seconds}s")
            
        except Exception as e:
            logger.error(f"添加间隔任务失败: {str(e)}")
            raise
    
    def _wrap_task(self, func: Callable, task_id: str):
        """包装任务函数以添加统计"""
        async def wrapper(*args, **kwargs):
            self.stats['total_executions'] += 1
            
            try:
                if asyncio.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
                
                logger.debug(f"任务执行成功: {task_id}")
                
            except Exception as e:
                self.stats['failed_executions'] += 1
                logger.error(f"任务执行失败 {task_id}: {str(e)}")
        
        return wrapper
    
    def remove_task(self, task_id: str):
        """移除任务"""
        try:
            self.scheduler.remove_job(task_id)
            
            if task_id in self.tasks:
                del self.tasks[task_id]
            
            self.stats['total_tasks'] -= 1
            
            logger.info(f"任务已移除: {task_id}")
            
        except Exception as e:
            logger.error(f"移除任务失败: {str(e)}")
    
    def pause_task(self, task_id: str):
        """暂停任务"""
        try:
            self.scheduler.pause_job(task_id)
            logger.info(f"任务已暂停: {task_id}")
            
        except Exception as e:
            logger.error(f"暂停任务失败: {str(e)}")
    
    def resume_task(self, task_id: str):
        """恢复任务"""
        try:
            self.scheduler.resume_job(task_id)
            logger.info(f"任务已恢复: {task_id}")
            
        except Exception as e:
            logger.error(f"恢复任务失败: {str(e)}")
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict]:
        """获取所有任务"""
        return list(self.tasks.values())
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'success_rate': (
                (self.stats['total_executions'] - self.stats['failed_executions']) 
                / self.stats['total_executions'] * 100
                if self.stats['total_executions'] > 0 else 0
            )
        }


# 全局实例
task_scheduler = TaskScheduler()


# 装饰器：定时任务
def scheduled_task(cron_expression: str, task_id: Optional[str] = None):
    """
    定时任务装饰器
    
    用法:
    @scheduled_task("0 0 * * *")  # 每天0点执行
    async def my_daily_task():
        # 执行任务
        pass
    """
    def decorator(func):
        _task_id = task_id or func.__name__
        
        task_scheduler.add_cron_task(
            task_id=_task_id,
            func=func,
            cron_expression=cron_expression,
            description=f"定时任务: {func.__name__}"
        )
        
        return func
    
    return decorator
