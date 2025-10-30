"""
日志清理工具
✅ P0-28: 自动清理过期日志
"""
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict
from ..utils.logger import logger
from ..config import settings
from ..database import get_database


class LogCleaner:
    """日志清理器"""
    
    def __init__(self):
        self.log_dir = Path('logs')
        self.retention_days = getattr(settings, 'log_retention_days', 7)
        self.db_log_retention_days = getattr(settings, 'db_log_retention_days', 30)
        
        # 统计
        self.stats = {
            'last_cleanup': None,
            'total_cleaned_files': 0,
            'total_cleaned_size': 0,
            'total_cleaned_db_records': 0
        }
    
    async def cleanup_all(self) -> Dict:
        """执行完整清理"""
        result = {
            'file_logs': await self.cleanup_file_logs(),
            'db_logs': await self.cleanup_db_logs(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.stats['last_cleanup'] = datetime.now()
        
        return result
    
    async def cleanup_file_logs(self) -> Dict:
        """清理文件日志"""
        try:
            if not self.log_dir.exists():
                return {'cleaned_count': 0, 'cleaned_size': 0}
            
            cutoff_time = datetime.now() - timedelta(days=self.retention_days)
            
            cleaned_count = 0
            cleaned_size = 0
            
            # 遍历日志文件
            for log_file in self.log_dir.glob('*.log'):
                try:
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if mtime < cutoff_time:
                        size = log_file.stat().st_size
                        log_file.unlink()
                        
                        cleaned_count += 1
                        cleaned_size += size
                        
                except Exception as e:
                    logger.error(f"删除日志文件失败 {log_file}: {str(e)}")
                    continue
            
            self.stats['total_cleaned_files'] += cleaned_count
            self.stats['total_cleaned_size'] += cleaned_size
            
            if cleaned_count > 0:
                logger.info(
                    f"清理文件日志: 删除{cleaned_count}个文件，"
                    f"释放{cleaned_size / 1024 / 1024:.1f}MB空间"
                )
            
            return {
                'cleaned_count': cleaned_count,
                'cleaned_size': cleaned_size
            }
            
        except Exception as e:
            logger.error(f"清理文件日志失败: {str(e)}")
            return {'error': str(e)}
    
    async def cleanup_db_logs(self) -> Dict:
        """清理数据库日志"""
        db = get_database()
        
        try:
            cutoff_time = datetime.now() - timedelta(days=self.db_log_retention_days)
            cutoff_timestamp = int(cutoff_time.timestamp() * 1000)
            
            # 统计要删除的记录数
            count_result = db.execute(
                "SELECT COUNT(*) FROM message_logs WHERE created_at < ?",
                (cutoff_timestamp,)
            ).fetchone()
            
            count = count_result[0] if count_result else 0
            
            if count > 0:
                # 删除过期记录
                db.execute(
                    "DELETE FROM message_logs WHERE created_at < ?",
                    (cutoff_timestamp,)
                )
                
                # 同时删除对应的失败消息记录
                db.execute(
                    "DELETE FROM failed_messages WHERE message_log_id NOT IN (SELECT id FROM message_logs)"
                )
                
                db.commit()
                
                self.stats['total_cleaned_db_records'] += count
                
                logger.info(f"清理数据库日志: 删除{count}条记录")
            
            # 优化数据库
            db.execute("VACUUM")
            
            return {
                'cleaned_count': count
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"清理数据库日志失败: {str(e)}")
            return {'error': str(e)}
    
    async def schedule_cleanup(self, interval_hours: int = 24):
        """
        定时清理任务
        
        Args:
            interval_hours: 清理间隔（小时）
        """
        try:
            while True:
                logger.info("开始执行定时清理...")
                
                result = await self.cleanup_all()
                
                logger.info(f"定时清理完成: {result}")
                
                # 等待下次清理
                await asyncio.sleep(interval_hours * 3600)
                
        except asyncio.CancelledError:
            logger.info("定时清理任务已取消")
        except Exception as e:
            logger.error(f"定时清理任务异常: {str(e)}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'retention_days': self.retention_days,
            'db_retention_days': self.db_log_retention_days
        }
    
    async def get_log_size_stats(self) -> Dict:
        """获取日志大小统计"""
        try:
            # 文件日志大小
            file_log_size = 0
            file_count = 0
            
            if self.log_dir.exists():
                for log_file in self.log_dir.glob('*.log'):
                    file_log_size += log_file.stat().st_size
                    file_count += 1
            
            # 数据库日志大小
            db = get_database()
            db_count = db.execute("SELECT COUNT(*) FROM message_logs").fetchone()[0]
            
            # SQLite数据库文件大小
            db_file_size = settings.database_path.stat().st_size if settings.database_path.exists() else 0
            
            return {
                'file_logs': {
                    'count': file_count,
                    'size_mb': file_log_size / 1024 / 1024
                },
                'db_logs': {
                    'count': db_count,
                    'db_size_mb': db_file_size / 1024 / 1024
                },
                'total_size_mb': (file_log_size + db_file_size) / 1024 / 1024
            }
            
        except Exception as e:
            logger.error(f"获取日志大小统计失败: {str(e)}")
            return {}


# 全局实例
log_cleaner = LogCleaner()
