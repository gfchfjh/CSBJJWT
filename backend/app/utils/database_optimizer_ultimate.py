"""
数据库优化工具
✅ P2-1深度优化: 自动归档 + VACUUM压缩
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from ..config import settings
from ..utils.logger import logger


class DatabaseOptimizer:
    """数据库优化工具"""
    
    def __init__(self):
        self.db_path = str(settings.data_dir / "config.db")
    
    def archive_old_logs(self, days: int = 30) -> int:
        """
        归档旧日志（移动到归档表）
        
        Args:
            days: 归档天数阈值
        
        Returns:
            归档的记录数
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).timestamp()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建归档表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS message_logs_archive (
                    id INTEGER PRIMARY KEY,
                    kook_message_id TEXT,
                    kook_channel_id TEXT,
                    content TEXT,
                    message_type TEXT,
                    sender_name TEXT,
                    target_platform TEXT,
                    target_channel TEXT,
                    status TEXT,
                    error_message TEXT,
                    latency_ms INTEGER,
                    created_at TIMESTAMP,
                    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 移动旧记录到归档表
            cursor.execute('''
                INSERT INTO message_logs_archive
                SELECT *, CURRENT_TIMESTAMP FROM message_logs
                WHERE created_at < ?
            ''', (cutoff_date,))
            
            archived_count = cursor.rowcount
            
            # 删除主表中的旧记录
            cursor.execute('DELETE FROM message_logs WHERE created_at < ?', (cutoff_date,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📦 归档了 {archived_count} 条旧日志（{days}天前）")
            
            return archived_count
        
        except Exception as e:
            logger.error(f"❌ 归档日志失败: {e}")
            return 0
    
    def vacuum_database(self) -> dict:
        """
        执行VACUUM压缩数据库
        
        Returns:
            压缩结果 {"before": bytes, "after": bytes, "saved_percent": float}
        """
        try:
            db_path = Path(self.db_path)
            
            # 获取压缩前大小
            size_before = db_path.stat().st_size
            
            # 执行VACUUM
            conn = sqlite3.connect(str(db_path))
            conn.execute('VACUUM')
            conn.close()
            
            # 获取压缩后大小
            size_after = db_path.stat().st_size
            
            saved_percent = ((size_before - size_after) / size_before) * 100 if size_before > 0 else 0
            
            logger.info(f"🗜️ 数据库压缩完成: {self._format_size(size_before)} → {self._format_size(size_after)} (节省 {saved_percent:.1f}%)")
            
            return {
                "before": size_before,
                "after": size_after,
                "saved": size_before - size_after,
                "saved_percent": round(saved_percent, 2)
            }
        
        except Exception as e:
            logger.error(f"❌ 数据库压缩失败: {e}")
            return {"error": str(e)}
    
    def analyze_database(self) -> dict:
        """
        分析数据库统计信息
        
        Returns:
            统计信息
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            stats = {}
            
            for table in tables:
                # 获取记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                stats[table] = {
                    "record_count": count
                }
            
            # 数据库文件大小
            db_size = Path(self.db_path).stat().st_size
            
            conn.close()
            
            return {
                "db_size": db_size,
                "db_size_formatted": self._format_size(db_size),
                "tables": stats
            }
        
        except Exception as e:
            logger.error(f"❌ 分析数据库失败: {e}")
            return {"error": str(e)}
    
    def _format_size(self, bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} TB"
    
    def optimize_all(self) -> dict:
        """
        执行完整优化流程
        
        Returns:
            优化结果
        """
        logger.info("🔧 开始数据库完整优化...")
        
        results = {}
        
        # 1. 归档旧日志
        archived = self.archive_old_logs(days=30)
        results['archived_logs'] = archived
        
        # 2. 压缩数据库
        vacuum_result = self.vacuum_database()
        results['vacuum'] = vacuum_result
        
        # 3. 分析统计
        stats = self.analyze_database()
        results['stats'] = stats
        
        logger.info("✅ 数据库优化完成")
        
        return results


# 创建全局实例
database_optimizer = DatabaseOptimizer()
