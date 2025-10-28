"""
✅ P2-9优化: 数据库定期维护和归档
自动清理旧数据、优化数据库性能、归档历史消息
"""
import time
from pathlib import Path
from ..database import db
from ..utils.logger import logger
from ..config import settings


class DatabaseMaintenance:
    """数据库维护工具"""
    
    def __init__(self):
        self.archive_db_path = Path(settings.data_dir) / "message_archive.db"
    
    def vacuum_database(self) -> bool:
        """
        执行VACUUM优化
        
        功能：
        - 回收碎片空间
        - 重建索引
        - 优化查询性能
        
        建议：每周执行一次
        """
        try:
            logger.info("[DBMaintenance] 开始VACUUM优化...")
            start_time = time.time()
            
            # 先执行ANALYZE更新统计信息
            db.execute("ANALYZE")
            logger.info("[DBMaintenance] ANALYZE完成")
            
            # 执行VACUUM
            db.execute("VACUUM")
            
            elapsed = time.time() - start_time
            logger.info(f"[DBMaintenance] VACUUM优化完成，耗时 {elapsed:.2f}秒")
            
            return True
            
        except Exception as e:
            logger.error(f"[DBMaintenance] VACUUM失败: {str(e)}")
            return False
    
    def archive_old_messages(self, days: int = 7) -> int:
        """
        归档旧消息日志
        
        Args:
            days: 归档多少天前的消息，默认7天
            
        Returns:
            归档的消息数量
            
        流程：
        1. 查询N天前的消息
        2. 导出到归档数据库
        3. 从主数据库删除
        """
        try:
            cutoff_timestamp = int(time.time()) - (days * 86400)
            
            logger.info(f"[DBMaintenance] 开始归档 {days} 天前的消息...")
            
            # 查询需要归档的消息
            messages = db.execute("""
                SELECT * FROM message_logs
                WHERE created_at < datetime('now', ?)
            """, (f'-{days} days',)).fetchall()
            
            if not messages or len(messages) == 0:
                logger.info("[DBMaintenance] 没有需要归档的消息")
                return 0
            
            logger.info(f"[DBMaintenance] 找到 {len(messages)} 条待归档消息")
            
            # 创建归档数据库（如果不存在）
            self._init_archive_db()
            
            # 连接归档数据库
            import sqlite3
            archive_conn = sqlite3.connect(self.archive_db_path)
            archive_conn.row_factory = sqlite3.Row
            archive_cursor = archive_conn.cursor()
            
            # 插入到归档数据库
            for message in messages:
                try:
                    archive_cursor.execute("""
                        INSERT OR IGNORE INTO message_logs_archive
                        (kook_message_id, kook_channel_id, content, message_type,
                         sender_name, target_platform, target_channel, status,
                         error_message, latency_ms, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        message['kook_message_id'],
                        message['kook_channel_id'],
                        message['content'],
                        message['message_type'],
                        message['sender_name'],
                        message['target_platform'],
                        message['target_channel'],
                        message['status'],
                        message['error_message'],
                        message['latency_ms'],
                        message['created_at']
                    ))
                except Exception as e:
                    logger.warning(f"归档单条消息失败: {e}")
                    continue
            
            archive_conn.commit()
            archive_conn.close()
            
            # 从主数据库删除已归档的消息
            db.execute("""
                DELETE FROM message_logs
                WHERE created_at < datetime('now', ?)
            """, (f'-{days} days',))
            
            db.commit()
            
            logger.info(f"[DBMaintenance] 成功归档 {len(messages)} 条消息")
            
            return len(messages)
            
        except Exception as e:
            logger.error(f"[DBMaintenance] 归档消息失败: {str(e)}")
            return 0
    
    def _init_archive_db(self):
        """初始化归档数据库"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.archive_db_path)
            cursor = conn.cursor()
            
            # 创建归档表（结构与主表相同）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_logs_archive (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kook_message_id TEXT NOT NULL UNIQUE,
                    kook_channel_id TEXT NOT NULL,
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
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_archive_created
                ON message_logs_archive(created_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_archive_kook_id
                ON message_logs_archive(kook_message_id)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"[DBMaintenance] 归档数据库已初始化: {self.archive_db_path}")
            
        except Exception as e:
            logger.error(f"[DBMaintenance] 归档数据库初始化失败: {str(e)}")
    
    def cleanup_old_data(self, retention_days: Dict[str, int]) -> Dict[str, int]:
        """
        清理过期数据
        
        Args:
            retention_days: 各表的保留天数配置
                {
                    "message_logs": 7,
                    "captcha_queue": 1,
                    "cookie_import_queue": 1
                }
        
        Returns:
            各表清理的记录数
        """
        try:
            results = {}
            
            # 清理消息日志
            if 'message_logs' in retention_days:
                days = retention_days['message_logs']
                # 先归档
                archived = self.archive_old_messages(days)
                results['message_logs'] = archived
            
            # 清理验证码队列
            if 'captcha_queue' in retention_days:
                days = retention_days['captcha_queue']
                result = db.execute("""
                    DELETE FROM captcha_queue
                    WHERE created_at < datetime('now', ?)
                """, (f'-{days} days',))
                results['captcha_queue'] = result.rowcount
                logger.info(f"[DBMaintenance] 清理 {result.rowcount} 条验证码记录")
            
            # 清理Cookie导入队列
            if 'cookie_import_queue' in retention_days:
                days = retention_days['cookie_import_queue']
                result = db.execute("""
                    DELETE FROM cookie_import_queue
                    WHERE created_at < datetime('now', ?) AND imported = 1
                """, (f'-{days} days',))
                results['cookie_import_queue'] = result.rowcount
                logger.info(f"[DBMaintenance] 清理 {result.rowcount} 条Cookie导入记录")
            
            db.commit()
            
            return results
            
        except Exception as e:
            logger.error(f"[DBMaintenance] 清理数据失败: {str(e)}")
            return {}
    
    def get_database_size(self) -> Dict[str, int]:
        """
        获取数据库大小信息
        
        Returns:
            {
                "main_db_size_mb": float,
                "archive_db_size_mb": float,
                "total_size_mb": float
            }
        """
        try:
            main_db_path = Path(settings.data_dir) / "kook_forwarder.db"
            
            main_size = main_db_path.stat().st_size if main_db_path.exists() else 0
            archive_size = self.archive_db_path.stat().st_size if self.archive_db_path.exists() else 0
            
            return {
                "main_db_size_mb": round(main_size / (1024 * 1024), 2),
                "archive_db_size_mb": round(archive_size / (1024 * 1024), 2),
                "total_size_mb": round((main_size + archive_size) / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"[DBMaintenance] 获取数据库大小失败: {str(e)}")
            return {
                "main_db_size_mb": 0,
                "archive_db_size_mb": 0,
                "total_size_mb": 0
            }
    
    def get_table_stats(self) -> Dict[str, int]:
        """
        获取各表的记录数统计
        
        Returns:
            各表的记录数
        """
        try:
            stats = {}
            
            tables = [
                'accounts',
                'bot_configs',
                'channel_mappings',
                'filter_rules',
                'message_logs',
                'failed_messages',
                'system_config'
            ]
            
            for table in tables:
                try:
                    result = db.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                    stats[table] = result['count'] if result else 0
                except Exception:
                    stats[table] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"[DBMaintenance] 获取表统计失败: {str(e)}")
            return {}
    
    def run_full_maintenance(self) -> Dict[str, any]:
        """
        执行完整的数据库维护
        
        流程：
        1. 归档旧消息（7天前）
        2. 清理临时数据
        3. 执行VACUUM优化
        4. 更新统计信息
        
        Returns:
            维护报告
        """
        try:
            logger.info("[DBMaintenance] ========== 开始完整数据库维护 ==========")
            start_time = time.time()
            
            report = {
                "start_time": time.time(),
                "operations": []
            }
            
            # 1. 归档旧消息
            logger.info("[DBMaintenance] 步骤1: 归档旧消息...")
            archived = self.archive_old_messages(days=7)
            report["operations"].append({
                "name": "归档消息",
                "result": f"归档 {archived} 条消息"
            })
            
            # 2. 清理临时数据
            logger.info("[DBMaintenance] 步骤2: 清理临时数据...")
            cleaned = self.cleanup_old_data({
                "captcha_queue": 1,
                "cookie_import_queue": 1
            })
            report["operations"].append({
                "name": "清理临时数据",
                "result": f"验证码: {cleaned.get('captcha_queue', 0)}, Cookie: {cleaned.get('cookie_import_queue', 0)}"
            })
            
            # 3. VACUUM优化
            logger.info("[DBMaintenance] 步骤3: VACUUM优化...")
            vacuum_success = self.vacuum_database()
            report["operations"].append({
                "name": "VACUUM优化",
                "result": "成功" if vacuum_success else "失败"
            })
            
            # 4. 获取最终统计
            db_size = self.get_database_size()
            table_stats = self.get_table_stats()
            
            report["database_size"] = db_size
            report["table_stats"] = table_stats
            report["duration_seconds"] = round(time.time() - start_time, 2)
            
            logger.info(f"[DBMaintenance] ========== 维护完成，耗时 {report['duration_seconds']}秒 ==========")
            
            return report
            
        except Exception as e:
            logger.error(f"[DBMaintenance] 完整维护失败: {str(e)}")
            return {
                "error": str(e),
                "duration_seconds": time.time() - start_time if 'start_time' in locals() else 0
            }


# 全局实例
db_maintenance = DatabaseMaintenance()
