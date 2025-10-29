"""
系统健康度评分系统
基于多个指标计算0-100分的健康度评分
"""

import redis
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..config import settings
from ..database import db
from ..utils.logger import logger


class HealthScorer:
    """系统健康度评分器"""
    
    # 评分权重
    WEIGHTS = {
        'redis_health': 0.15,          # Redis健康度 15%
        'database_health': 0.15,       # 数据库健康度 15%
        'message_success_rate': 0.25,  # 消息成功率 25%
        'queue_health': 0.15,          # 队列健康度 15%
        'account_health': 0.15,        # 账号健康度 15%
        'system_resource': 0.15        # 系统资源 15%
    }
    
    def __init__(self):
        self.redis_client = None
        
    async def calculate_score(self) -> Dict[str, Any]:
        """
        计算系统总体健康度评分
        
        Returns:
            {
                "overall_score": 85,
                "status": "healthy",  # healthy/warning/critical
                "details": {...},
                "recommendations": [...]
            }
        """
        try:
            # 连接Redis
            await self._connect_redis()
            
            # 计算各项指标
            scores = {
                'redis_health': await self._check_redis_health(),
                'database_health': await self._check_database_health(),
                'message_success_rate': await self._check_message_success_rate(),
                'queue_health': await self._check_queue_health(),
                'account_health': await self._check_account_health(),
                'system_resource': await self._check_system_resource()
            }
            
            # 计算加权总分
            overall_score = sum(
                scores[key] * self.WEIGHTS[key]
                for key in scores
            )
            
            # 判断健康状态
            status = self._get_status(overall_score)
            
            # 生成建议
            recommendations = self._generate_recommendations(scores)
            
            logger.info(f"系统健康度评分完成: {overall_score:.1f}分 ({status})")
            
            return {
                "overall_score": round(overall_score, 1),
                "status": status,
                "details": scores,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"计算健康度评分失败: {e}")
            return {
                "overall_score": 0,
                "status": "critical",
                "error": str(e)
            }
    
    async def _connect_redis(self):
        """连接Redis"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.redis_client = None
    
    async def _check_redis_health(self) -> float:
        """检查Redis健康度 (0-100)"""
        try:
            if not self.redis_client:
                return 0.0
            
            # Ping测试
            self.redis_client.ping()
            
            # 检查内存使用
            info = self.redis_client.info('memory')
            used_memory_mb = info.get('used_memory', 0) / (1024 * 1024)
            max_memory_mb = 512  # 假设最大512MB
            
            memory_score = max(0, 100 - (used_memory_mb / max_memory_mb * 100))
            
            # 检查连接数
            clients = self.redis_client.client_list()
            connection_score = 100 if len(clients) < 100 else 50
            
            # 综合评分
            score = (memory_score * 0.7 + connection_score * 0.3)
            
            return score
        
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            return 0.0
    
    async def _check_database_health(self) -> float:
        """检查数据库健康度 (0-100)"""
        try:
            # 测试连接
            db.execute("SELECT 1").fetchone()
            
            # 检查数据库大小（SQLite）
            result = db.execute("""
                SELECT page_count * page_size as size 
                FROM pragma_page_count(), pragma_page_size()
            """).fetchone()
            
            db_size_mb = result['size'] / (1024 * 1024) if result else 0
            
            # 数据库大小评分（100MB以下满分）
            size_score = max(0, 100 - (db_size_mb / 100 * 50))
            
            # 查询性能测试
            start_time = datetime.now()
            db.execute("SELECT COUNT(*) FROM message_logs WHERE created_at > datetime('now', '-1 day')").fetchone()
            query_time = (datetime.now() - start_time).total_seconds()
            
            # 查询时间评分（1秒以下满分）
            query_score = max(0, 100 - (query_time * 100))
            
            # 综合评分
            score = (size_score * 0.4 + query_score * 0.6)
            
            return score
        
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return 0.0
    
    async def _check_message_success_rate(self) -> float:
        """检查消息成功率 (0-100)"""
        try:
            # 查询最近24小时的消息统计
            result = db.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success
                FROM message_logs
                WHERE created_at > datetime('now', '-1 day')
            """).fetchone()
            
            total = result['total'] or 0
            success = result['success'] or 0
            
            if total == 0:
                # 没有消息，返回中等评分
                return 70.0
            
            # 成功率
            success_rate = (success / total) * 100
            
            return success_rate
        
        except Exception as e:
            logger.error(f"消息成功率检查失败: {e}")
            return 0.0
    
    async def _check_queue_health(self) -> float:
        """检查队列健康度 (0-100)"""
        try:
            if not self.redis_client:
                return 0.0
            
            # 获取队列大小
            pending = self.redis_client.llen("queue:pending")
            processing = self.redis_client.llen("queue:processing")
            failed = self.redis_client.llen("queue:failed")
            
            # 待处理队列评分（100条以下满分）
            pending_score = max(0, 100 - (pending / 100 * 100))
            
            # 失败队列评分（10条以下满分）
            failed_score = max(0, 100 - (failed / 10 * 100))
            
            # 处理中队列评分（10条以下满分）
            processing_score = max(0, 100 - (processing / 10 * 100))
            
            # 综合评分
            score = (
                pending_score * 0.4 +
                failed_score * 0.4 +
                processing_score * 0.2
            )
            
            return score
        
        except Exception as e:
            logger.error(f"队列健康检查失败: {e}")
            return 0.0
    
    async def _check_account_health(self) -> float:
        """检查账号健康度 (0-100)"""
        try:
            # 获取所有账号
            accounts = db.execute("SELECT * FROM accounts").fetchall()
            
            if not accounts:
                return 0.0
            
            # 计算在线账号比例
            online_count = sum(1 for acc in accounts if acc['status'] == 'online')
            online_rate = (online_count / len(accounts)) * 100
            
            # 检查最后活跃时间
            active_count = 0
            for acc in accounts:
                if acc['last_active']:
                    last_active = datetime.fromisoformat(acc['last_active'])
                    if datetime.now() - last_active < timedelta(hours=1):
                        active_count += 1
            
            active_rate = (active_count / len(accounts)) * 100 if accounts else 0
            
            # 综合评分
            score = (online_rate * 0.6 + active_rate * 0.4)
            
            return score
        
        except Exception as e:
            logger.error(f"账号健康检查失败: {e}")
            return 0.0
    
    async def _check_system_resource(self) -> float:
        """检查系统资源使用 (0-100)"""
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_score = max(0, 100 - cpu_percent)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_score = max(0, 100 - memory.percent)
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_score = max(0, 100 - disk.percent)
            
            # 综合评分
            score = (
                cpu_score * 0.3 +
                memory_score * 0.4 +
                disk_score * 0.3
            )
            
            return score
        
        except ImportError:
            # psutil未安装，返回默认分数
            return 80.0
        except Exception as e:
            logger.error(f"系统资源检查失败: {e}")
            return 70.0
    
    def _get_status(self, score: float) -> str:
        """根据评分判断状态"""
        if score >= 80:
            return "healthy"
        elif score >= 60:
            return "warning"
        else:
            return "critical"
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # Redis健康度建议
        if scores['redis_health'] < 70:
            recommendations.append("Redis性能不佳，建议检查内存使用或重启Redis服务")
        
        # 数据库健康度建议
        if scores['database_health'] < 70:
            recommendations.append("数据库性能下降，建议清理旧数据或优化查询")
        
        # 消息成功率建议
        if scores['message_success_rate'] < 90:
            recommendations.append("消息成功率较低，建议检查Bot配置和网络连接")
        
        # 队列健康度建议
        if scores['queue_health'] < 70:
            recommendations.append("队列积压严重，建议增加Worker或清理失败消息")
        
        # 账号健康度建议
        if scores['account_health'] < 70:
            recommendations.append("部分账号离线，建议检查Cookie是否过期")
        
        # 系统资源建议
        if scores['system_resource'] < 70:
            recommendations.append("系统资源紧张，建议关闭其他程序或升级硬件")
        
        if not recommendations:
            recommendations.append("系统运行良好，无需额外优化")
        
        return recommendations


# 全局实例
health_scorer = HealthScorer()
