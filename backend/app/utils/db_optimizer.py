"""
数据库优化工具 - 性能优化
提供查询优化、索引管理、数据清理等功能
"""
from ..database import db
from ..utils.logger import logger
from datetime import datetime, timedelta


class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self):
        pass
    
    def analyze_performance(self) -> dict:
        """分析数据库性能"""
        stats = {}
        
        try:
            # 表大小统计
            tables = ['accounts', 'bot_configs', 'channel_mappings', 
                     'message_logs', 'filter_rules', 'failed_messages']
            
            for table in tables:
                result = db.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                stats[table] = result['count']
            
            # 索引统计
            result = db.execute("""
                SELECT name, tbl_name FROM sqlite_master 
                WHERE type = 'index' AND name NOT LIKE 'sqlite_%'
            """)
            stats['indexes'] = [dict(row) for row in result.fetchall()]
            
            # 数据库大小
            result = db.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()").fetchone()
            stats['db_size_bytes'] = result['size']
            stats['db_size_mb'] = round(result['size'] / 1024 / 1024, 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"分析数据库性能失败: {str(e)}")
            return {}
    
    def optimize_tables(self) -> bool:
        """优化所有表"""
        try:
            # SQLite的VACUUM命令
            with db.get_connection() as conn:
                conn.execute("VACUUM")
            
            logger.info("数据库VACUUM完成")
            
            # 分析统计信息
            with db.get_connection() as conn:
                conn.execute("ANALYZE")
            
            logger.info("数据库ANALYZE完成")
            
            return True
            
        except Exception as e:
            logger.error(f"优化表失败: {str(e)}")
            return False
    
    def clean_old_logs(self, days: int = 7) -> int:
        """清理旧日志"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM message_logs WHERE created_at < ?",
                    (cutoff_date,)
                )
                deleted_count = cursor.rowcount
            
            logger.info(f"清理了 {deleted_count} 条旧日志（{days}天前）")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧日志失败: {str(e)}")
            return 0
    
    def rebuild_indexes(self) -> bool:
        """重建索引"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 获取所有索引
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type = 'index' AND name NOT LIKE 'sqlite_%'
                """)
                indexes = [row['name'] for row in cursor.fetchall()]
                
                # 重建每个索引
                for index_name in indexes:
                    cursor.execute(f"REINDEX {index_name}")
                    logger.debug(f"重建索引: {index_name}")
            
            logger.info(f"重建了 {len(indexes)} 个索引")
            return True
            
        except Exception as e:
            logger.error(f"重建索引失败: {str(e)}")
            return False
    
    def archive_old_data(self, days: int = 30) -> dict:
        """归档旧数据"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 创建归档表（如果不存在）
                cursor.execute("""
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
                """)
                
                # 移动旧数据到归档表
                cursor.execute(f"""
                    INSERT INTO message_logs_archive 
                    SELECT *, NULL FROM message_logs 
                    WHERE created_at < ? AND status = 'success'
                """, (cutoff_date,))
                
                archived_count = cursor.rowcount
                
                # 删除已归档的数据
                cursor.execute(
                    "DELETE FROM message_logs WHERE created_at < ? AND status = 'success'",
                    (cutoff_date,)
                )
            
            logger.info(f"归档了 {archived_count} 条数据（{days}天前）")
            
            return {
                'archived_count': archived_count,
                'cutoff_date': cutoff_date
            }
            
        except Exception as e:
            logger.error(f"归档数据失败: {str(e)}")
            return {'archived_count': 0}
    
    def get_slow_queries(self) -> list:
        """获取慢查询（需要开启SQLite查询日志）"""
        # SQLite没有内置的慢查询日志，这里返回一些常见的可能慢的查询模式
        recommendations = [
            {
                'query': 'SELECT * FROM message_logs ORDER BY created_at DESC',
                'optimization': '添加created_at索引（已存在）',
                'impact': 'low'
            },
            {
                'query': 'SELECT * FROM channel_mappings WHERE enabled = 1',
                'optimization': '添加enabled索引（已存在）',
                'impact': 'low'
            },
            {
                'query': 'JOIN查询',
                'optimization': '确保JOIN字段都有索引',
                'impact': 'medium'
            }
        ]
        
        return recommendations
    
    def get_optimization_report(self) -> dict:
        """获取优化报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'performance': self.analyze_performance(),
            'recommendations': []
        }
        
        stats = report['performance']
        
        # 基于统计数据给出建议
        if stats.get('message_logs', 0) > 100000:
            report['recommendations'].append({
                'type': 'cleanup',
                'priority': 'high',
                'description': 'message_logs表超过10万条记录，建议清理或归档',
                'action': 'clean_old_logs或archive_old_data'
            })
        
        if stats.get('db_size_mb', 0) > 1000:
            report['recommendations'].append({
                'type': 'optimization',
                'priority': 'medium',
                'description': '数据库文件超过1GB，建议执行VACUUM',
                'action': 'optimize_tables'
            })
        
        return report


# 全局数据库优化器实例
db_optimizer = DatabaseOptimizer()
