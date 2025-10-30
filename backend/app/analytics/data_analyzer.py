"""
数据分析引擎
✅ P1-12: 数据分析和报表生成
"""
from typing import Dict, List
from datetime import datetime, timedelta
from ..utils.logger import logger
from ..database import get_database


class DataAnalyzer:
    """数据分析器"""
    
    async def get_overview_stats(self, days: int = 7) -> Dict:
        """获取概览统计"""
        db = get_database()
        
        try:
            # 时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # 总消息数
            total_messages = db.execute(
                "SELECT COUNT(*) FROM message_logs WHERE created_at >= ?",
                (start_time.timestamp() * 1000,)
            ).fetchone()[0]
            
            # 成功消息数
            success_messages = db.execute(
                "SELECT COUNT(*) FROM message_logs WHERE status = 'success' AND created_at >= ?",
                (start_time.timestamp() * 1000,)
            ).fetchone()[0]
            
            # 失败消息数
            failed_messages = db.execute(
                "SELECT COUNT(*) FROM message_logs WHERE status = 'failed' AND created_at >= ?",
                (start_time.timestamp() * 1000,)
            ).fetchone()[0]
            
            # 平均延迟
            avg_latency = db.execute(
                "SELECT AVG(latency_ms) FROM message_logs WHERE status = 'success' AND created_at >= ?",
                (start_time.timestamp() * 1000,)
            ).fetchone()[0] or 0
            
            return {
                'total_messages': total_messages,
                'success_messages': success_messages,
                'failed_messages': failed_messages,
                'success_rate': success_messages / total_messages * 100 if total_messages > 0 else 0,
                'avg_latency_ms': round(avg_latency, 2),
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'days': days
                }
            }
            
        except Exception as e:
            logger.error(f"获取概览统计失败: {str(e)}")
            return {}
    
    async def get_platform_distribution(self, days: int = 7) -> List[Dict]:
        """获取平台分布"""
        db = get_database()
        
        try:
            start_time = (datetime.now() - timedelta(days=days)).timestamp() * 1000
            
            results = db.execute("""
                SELECT target_platform, COUNT(*) as count
                FROM message_logs
                WHERE created_at >= ?
                GROUP BY target_platform
                ORDER BY count DESC
            """, (start_time,)).fetchall()
            
            return [{'platform': row[0], 'count': row[1]} for row in results]
            
        except Exception as e:
            logger.error(f"获取平台分布失败: {str(e)}")
            return []
    
    async def get_hourly_trend(self, days: int = 1) -> List[Dict]:
        """获取小时级趋势"""
        db = get_database()
        
        try:
            start_time = (datetime.now() - timedelta(days=days)).timestamp() * 1000
            
            # 简化版：按小时统计
            results = db.execute("""
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', datetime(created_at/1000, 'unixepoch')) as hour,
                    COUNT(*) as count
                FROM message_logs
                WHERE created_at >= ?
                GROUP BY hour
                ORDER BY hour
            """, (start_time,)).fetchall()
            
            return [{'hour': row[0], 'count': row[1]} for row in results]
            
        except Exception as e:
            logger.error(f"获取趋势失败: {str(e)}")
            return []


# 全局实例
data_analyzer = DataAnalyzer()
