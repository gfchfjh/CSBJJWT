"""
定时任务调度器
使用APScheduler实现定时任务
"""
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from typing import Callable, Optional
from .logger import logger


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone='Asia/Shanghai')
        self.tasks = {}
        
    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ 任务调度器已启动")
    
    def shutdown(self, wait: bool = True):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("✅ 任务调度器已停止")
    
    def add_daily_task(self, 
                       task_id: str,
                       func: Callable,
                       hour: int = 3,
                       minute: int = 0,
                       args: tuple = (),
                       kwargs: dict = None):
        """
        添加每日定时任务
        
        Args:
            task_id: 任务ID
            func: 任务函数
            hour: 小时（0-23）
            minute: 分钟（0-59）
            args: 位置参数
            kwargs: 关键字参数
        """
        if task_id in self.tasks:
            logger.warning(f"任务 {task_id} 已存在，将被覆盖")
            self.remove_task(task_id)
        
        trigger = CronTrigger(hour=hour, minute=minute)
        
        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            args=args,
            kwargs=kwargs or {},
            id=task_id,
            name=task_id,
            replace_existing=True,
            max_instances=1  # 同一任务不允许并发
        )
        
        self.tasks[task_id] = job
        logger.info(f"✅ 已添加每日任务: {task_id} (执行时间: {hour:02d}:{minute:02d})")
        
        return job
    
    def add_interval_task(self,
                          task_id: str,
                          func: Callable,
                          seconds: Optional[int] = None,
                          minutes: Optional[int] = None,
                          hours: Optional[int] = None,
                          args: tuple = (),
                          kwargs: dict = None):
        """
        添加间隔执行任务
        
        Args:
            task_id: 任务ID
            func: 任务函数
            seconds: 间隔秒数
            minutes: 间隔分钟数
            hours: 间隔小时数
            args: 位置参数
            kwargs: 关键字参数
        """
        if task_id in self.tasks:
            logger.warning(f"任务 {task_id} 已存在，将被覆盖")
            self.remove_task(task_id)
        
        trigger = IntervalTrigger(
            seconds=seconds or 0,
            minutes=minutes or 0,
            hours=hours or 0
        )
        
        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            args=args,
            kwargs=kwargs or {},
            id=task_id,
            name=task_id,
            replace_existing=True,
            max_instances=1
        )
        
        self.tasks[task_id] = job
        
        interval_str = []
        if hours:
            interval_str.append(f"{hours}小时")
        if minutes:
            interval_str.append(f"{minutes}分钟")
        if seconds:
            interval_str.append(f"{seconds}秒")
        
        logger.info(f"✅ 已添加间隔任务: {task_id} (间隔: {' '.join(interval_str)})")
        
        return job
    
    def remove_task(self, task_id: str) -> bool:
        """
        移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功移除
        """
        if task_id in self.tasks:
            try:
                self.scheduler.remove_job(task_id)
                del self.tasks[task_id]
                logger.info(f"✅ 已移除任务: {task_id}")
                return True
            except Exception as e:
                logger.error(f"移除任务失败: {task_id}, 错误: {str(e)}")
                return False
        else:
            logger.warning(f"任务不存在: {task_id}")
            return False
    
    def pause_task(self, task_id: str) -> bool:
        """
        暂停任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功暂停
        """
        if task_id in self.tasks:
            try:
                self.scheduler.pause_job(task_id)
                logger.info(f"⏸️ 已暂停任务: {task_id}")
                return True
            except Exception as e:
                logger.error(f"暂停任务失败: {task_id}, 错误: {str(e)}")
                return False
        else:
            logger.warning(f"任务不存在: {task_id}")
            return False
    
    def resume_task(self, task_id: str) -> bool:
        """
        恢复任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功恢复
        """
        if task_id in self.tasks:
            try:
                self.scheduler.resume_job(task_id)
                logger.info(f"▶️ 已恢复任务: {task_id}")
                return True
            except Exception as e:
                logger.error(f"恢复任务失败: {task_id}, 错误: {str(e)}")
                return False
        else:
            logger.warning(f"任务不存在: {task_id}")
            return False
    
    def get_task_info(self, task_id: str) -> Optional[dict]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息字典
        """
        if task_id not in self.tasks:
            return None
        
        job = self.tasks[task_id]
        
        return {
            'id': job.id,
            'name': job.name,
            'next_run_time': str(job.next_run_time) if job.next_run_time else None,
            'trigger': str(job.trigger),
            'pending': job.pending if hasattr(job, 'pending') else None,
        }
    
    def get_all_tasks(self) -> list:
        """
        获取所有任务信息
        
        Returns:
            任务信息列表
        """
        return [self.get_task_info(task_id) for task_id in self.tasks.keys()]
    
    def execute_now(self, task_id: str) -> bool:
        """
        立即执行任务（不等待下次调度）
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功执行
        """
        if task_id not in self.tasks:
            logger.warning(f"任务不存在: {task_id}")
            return False
        
        try:
            job = self.tasks[task_id]
            job.modify(next_run_time=datetime.now())
            logger.info(f"🚀 立即执行任务: {task_id}")
            return True
        except Exception as e:
            logger.error(f"执行任务失败: {task_id}, 错误: {str(e)}")
            return False


# 全局调度器实例
task_scheduler = TaskScheduler()


# ========== 预定义任务 ==========

async def daily_backup_task():
    """每日备份任务（凌晨3点）"""
    from ..database import db
    from ..config import settings
    from pathlib import Path
    import shutil
    
    try:
        logger.info("🔄 开始每日自动备份...")
        
        # 备份目录
        backup_dir = Path(settings.data_dir) / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成备份文件名（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"config_backup_{timestamp}.db"
        
        # 复制数据库文件
        db_path = Path(settings.data_dir) / "config.db"
        if db_path.exists():
            shutil.copy2(db_path, backup_file)
            logger.info(f"✅ 数据库备份成功: {backup_file}")
        
        # 清理旧备份（保留最近30个）
        backups = sorted(backup_dir.glob("config_backup_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old_backup in backups[30:]:
            old_backup.unlink()
            logger.info(f"🗑️ 删除旧备份: {old_backup.name}")
        
        logger.info(f"✅ 每日备份完成，当前保留 {min(len(backups), 30)} 个备份")
        
    except Exception as e:
        logger.error(f"❌ 每日备份失败: {str(e)}")


async def hourly_cleanup_task():
    """每小时清理任务"""
    from ..processors.image import image_processor
    
    try:
        logger.info("🧹 开始每小时清理任务...")
        
        # 1. 清理过期Token
        cleaned_tokens = image_processor.cleanup_expired_tokens()
        if cleaned_tokens > 0:
            logger.info(f"🗑️ 清理了 {cleaned_tokens} 个过期Token")
        
        # 2. 检查存储空间
        storage_gb = image_processor.get_storage_size()
        from ..config import settings
        if storage_gb > settings.image_max_size_gb * 0.9:  # 超过90%
            logger.warning(f"⚠️ 存储空间即将不足: {storage_gb:.2f}GB / {settings.image_max_size_gb}GB")
            # 清理3天前的图片
            await image_processor.cleanup_old_images(days=3)
        
        logger.info("✅ 每小时清理任务完成")
        
    except Exception as e:
        logger.error(f"❌ 每小时清理任务失败: {str(e)}")


async def health_check_task():
    """健康检查任务（每5分钟）"""
    from ..utils.health import health_checker
    
    try:
        logger.debug("💓 执行健康检查...")
        
        health_status = await health_checker.check_all()
        
        # 检查是否有异常
        if not health_status['healthy']:
            logger.warning(f"⚠️ 系统健康检查发现问题:")
            for check, status in health_status['checks'].items():
                if not status.get('healthy', False):
                    logger.warning(f"  - {check}: {status.get('message', '未知错误')}")
            
            # 发送通知（如果配置了）
            # TODO: 集成通知系统
        
    except Exception as e:
        logger.error(f"❌ 健康检查任务失败: {str(e)}")


def setup_scheduled_tasks():
    """
    设置所有预定义任务
    在应用启动时调用
    """
    logger.info("🚀 正在设置定时任务...")
    
    # 1. 每日备份（凌晨3点）
    task_scheduler.add_daily_task(
        'daily_backup',
        daily_backup_task,
        hour=3,
        minute=0
    )
    
    # 2. 每小时清理
    task_scheduler.add_interval_task(
        'hourly_cleanup',
        hourly_cleanup_task,
        hours=1
    )
    
    # 3. 每5分钟健康检查
    task_scheduler.add_interval_task(
        'health_check',
        health_check_task,
        minutes=5
    )
    
    # 启动调度器
    task_scheduler.start()
    
    logger.info("✅ 定时任务设置完成")


def shutdown_scheduled_tasks():
    """
    停止所有定时任务
    在应用关闭时调用
    """
    logger.info("🛑 正在停止定时任务...")
    task_scheduler.shutdown(wait=True)
    logger.info("✅ 定时任务已停止")
