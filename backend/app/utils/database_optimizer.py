"""
数据库优化工具
功能：
1. 添加复合索引
2. 查询性能分析
3. 数据归档
4. 数据库维护
"""
import sqlite3
from typing import List, Dict
from pathlib import Path
from datetime import datetime, timedelta
from ..config import DB_PATH
from ..utils.logger import logger


class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
    
    def create_optimized_indexes(self):
        """
        创建优化的索引
        
        复合索引可以显著提升联合查询性能
        """
        logger.info("开始创建优化索引...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 已存在的索引会自动跳过（IF NOT EXISTS）
            indexes = [
                # message_logs表复合索引
                """CREATE INDEX IF NOT EXISTS idx_logs_status_time 
                   ON message_logs(status, created_at DESC)""",
                
                """CREATE INDEX IF NOT EXISTS idx_logs_channel_status 
                   ON message_logs(kook_channel_id, status, created_at DESC)""",
                
                """CREATE INDEX IF NOT EXISTS idx_logs_platform_status 
                   ON message_logs(target_platform, status, created_at DESC)""",
                
                # channel_mappings表复合索引
                """CREATE INDEX IF NOT EXISTS idx_mapping_channel_enabled 
                   ON channel_mappings(kook_channel_id, enabled)""",
                
                """CREATE INDEX IF NOT EXISTS idx_mapping_platform_bot 
                   ON channel_mappings(target_platform, target_bot_id)""",
                
                # accounts表索引
                """CREATE INDEX IF NOT EXISTS idx_accounts_status 
                   ON accounts(status, last_active DESC)""",
                
                # bot_configs表索引
                """CREATE INDEX IF NOT EXISTS idx_bots_platform_status 
                   ON bot_configs(platform, status)""",
            ]
            
            for idx_sql in indexes:
                try:
                    cursor.execute(idx_sql)
                    idx_name = idx_sql.split()[5]  # 提取索引名
                    logger.info(f"  ✅ 创建索引: {idx_name}")
                except Exception as e:
                    logger.error(f"  ❌ 创建索引失败: {str(e)}")
            
            conn.commit()
        
        logger.info("✅ 索引创建完成")
    
    def analyze_query_performance(self, query: str) -> Dict:
        """
        分析查询性能
        
        使用EXPLAIN QUERY PLAN查看执行计划
        
        Args:
            query: SQL查询语句
            
        Returns:
            {
                'query': '...',
                'execution_plan': [...],
                'has_index': True/False,
                'suggestions': [...]
            }
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取执行计划
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            plan = cursor.fetchall()
            
            # 分析计划
            has_index = any('INDEX' in str(row) for row in plan)
            
            suggestions = []
            if not has_index:
                suggestions.append("建议添加索引以提升查询性能")
            
            return {
                'query': query,
                'execution_plan': [str(row) for row in plan],
                'has_index': has_index,
                'suggestions': suggestions
            }
    
    def archive_old_logs(self, days: int = 30) -> int:
        """
        归档旧日志数据
        
        将超过指定天数的日志移动到归档表
        
        Args:
            days: 保留天数
            
        Returns:
            归档的记录数
        """
        logger.info(f"开始归档 {days} 天前的日志...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建归档表（如果不存在）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_logs_archive (
                    id INTEGER PRIMARY KEY,
                    kook_message_id TEXT NOT NULL,
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
            
            # 计算截止日期
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # 移动数据到归档表
            cursor.execute("""
                INSERT INTO message_logs_archive 
                SELECT *, NULL FROM message_logs 
                WHERE created_at < ?
            """, (cutoff_str,))
            
            archived_count = cursor.rowcount
            
            # 从主表删除
            cursor.execute("DELETE FROM message_logs WHERE created_at < ?", (cutoff_str,))
            
            conn.commit()
        
        logger.info(f"✅ 已归档 {archived_count} 条日志记录")
        return archived_count
    
    def vacuum_database(self):
        """
        压缩数据库
        
        回收已删除数据占用的空间
        """
        logger.info("开始压缩数据库...")
        
        with sqlite3.connect(self.db_path) as conn:
            # 获取压缩前大小
            before_size = Path(self.db_path).stat().st_size / (1024 * 1024)
            
            conn.execute("VACUUM")
            
            # 获取压缩后大小
            after_size = Path(self.db_path).stat().st_size / (1024 * 1024)
            saved = before_size - after_size
        
        logger.info(f"✅ 数据库压缩完成，节省 {saved:.2f}MB 空间")
    
    def get_database_stats(self) -> Dict:
        """
        获取数据库统计信息
        
        Returns:
            {
                'file_size_mb': 12.5,
                'table_counts': {...},
                'index_count': 15,
                'tables': [...]
            }
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 数据库文件大小
            file_size = Path(self.db_path).stat().st_size / (1024 * 1024)
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # 统计每个表的记录数
            table_counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                table_counts[table] = cursor.fetchone()[0]
            
            # 索引数量
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
            index_count = cursor.fetchone()[0]
            
            return {
                'file_size_mb': round(file_size, 2),
                'table_counts': table_counts,
                'index_count': index_count,
                'tables': tables
            }
    
    def optimize_database(self, full: bool = False):
        """
        全面优化数据库
        
        Args:
            full: 是否执行完整优化（包括归档和压缩）
        """
        logger.info("🔧 开始数据库优化...")
        
        # 1. 创建索引
        self.create_optimized_indexes()
        
        # 2. 分析统计信息（SQLite自动）
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("ANALYZE")
        logger.info("✅ 已更新统计信息")
        
        if full:
            # 3. 归档旧数据
            self.archive_old_logs(days=30)
            
            # 4. 压缩数据库
            self.vacuum_database()
        
        # 5. 显示优化后的统计
        stats = self.get_database_stats()
        logger.info(f"✅ 数据库优化完成")
        logger.info(f"   文件大小: {stats['file_size_mb']}MB")
        logger.info(f"   索引数量: {stats['index_count']}")
        logger.info(f"   表记录数: {stats['table_counts']}")


# 创建全局实例
db_optimizer = DatabaseOptimizer()
