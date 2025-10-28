"""
✅ P1-6优化: 智能映射学习反馈机制
记录用户对映射推荐的反馈，通过机器学习不断优化推荐准确度
"""
import time
import math
from typing import Dict, List, Optional, Tuple
from ..database import db
from ..utils.logger import logger


class MappingLearner:
    """
    映射学习引擎
    
    功能：
    1. 记录用户反馈（接受/拒绝推荐）
    2. 计算学习权重（时间衰减）
    3. 优化推荐算法
    """
    
    def __init__(self):
        self._init_database()
    
    def _init_database(self):
        """初始化学习数据库表"""
        try:
            # 创建学习反馈表
            db.execute("""
                CREATE TABLE IF NOT EXISTS mapping_learning_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kook_channel_id TEXT NOT NULL,
                    kook_channel_name TEXT NOT NULL,
                    target_platform TEXT NOT NULL,
                    target_channel_id TEXT NOT NULL,
                    target_channel_name TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,  -- accepted/rejected
                    confidence_score FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_timestamp INTEGER
                )
            """)
            
            # 创建索引
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_learning_kook_channel
                ON mapping_learning_feedback(kook_channel_id)
            """)
            
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_learning_target
                ON mapping_learning_feedback(target_platform, target_channel_id)
            """)
            
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_learning_feedback_type
                ON mapping_learning_feedback(feedback_type, created_timestamp DESC)
            """)
            
            db.commit()
            logger.info("[MappingLearner] 数据库表初始化完成")
            
        except Exception as e:
            logger.error(f"[MappingLearner] 数据库初始化失败: {str(e)}")
    
    def record_user_feedback(
        self,
        kook_channel_id: str,
        kook_channel_name: str,
        target_platform: str,
        target_channel_id: str,
        target_channel_name: str,
        accepted: bool,
        confidence_score: float = 0.0
    ) -> bool:
        """
        记录用户反馈
        
        Args:
            kook_channel_id: KOOK频道ID
            kook_channel_name: KOOK频道名称
            target_platform: 目标平台（discord/telegram/feishu）
            target_channel_id: 目标频道ID
            target_channel_name: 目标频道名称
            accepted: 用户是否接受此推荐
            confidence_score: 推荐时的置信度分数
            
        Returns:
            是否成功记录
        """
        try:
            feedback_type = 'accepted' if accepted else 'rejected'
            
            db.execute("""
                INSERT INTO mapping_learning_feedback
                (kook_channel_id, kook_channel_name, target_platform, 
                 target_channel_id, target_channel_name, feedback_type,
                 confidence_score, created_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kook_channel_id,
                kook_channel_name,
                target_platform,
                target_channel_id,
                target_channel_name,
                feedback_type,
                confidence_score,
                int(time.time())
            ))
            
            db.commit()
            
            logger.info(
                f"[MappingLearner] 记录反馈: {kook_channel_name} → "
                f"{target_platform}:{target_channel_name} ({feedback_type})"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"[MappingLearner] 记录反馈失败: {str(e)}")
            return False
    
    def get_learning_weight(
        self,
        kook_channel_id: str,
        target_platform: str,
        target_channel_id: str
    ) -> float:
        """
        计算学习权重（带时间衰减）
        
        Args:
            kook_channel_id: KOOK频道ID
            target_platform: 目标平台
            target_channel_id: 目标频道ID
            
        Returns:
            学习权重（0.0-1.0），越高表示用户越倾向于此映射
            
        算法：
        1. 查询所有相关的反馈记录
        2. 计算时间衰减权重（30天半衰期）
        3. accepted记录加权重，rejected记录减权重
        4. 归一化到0-1范围
        """
        try:
            # 查询相关反馈
            results = db.execute("""
                SELECT feedback_type, confidence_score, created_timestamp
                FROM mapping_learning_feedback
                WHERE kook_channel_id = ?
                  AND target_platform = ?
                  AND target_channel_id = ?
                ORDER BY created_timestamp DESC
                LIMIT 100
            """, (kook_channel_id, target_platform, target_channel_id)).fetchall()
            
            if not results:
                return 0.0
            
            current_time = time.time()
            total_weight = 0.0
            
            for record in results:
                feedback_type = record['feedback_type']
                created_timestamp = record['created_timestamp']
                
                # 计算时间衰减（30天半衰期）
                days_passed = (current_time - created_timestamp) / 86400  # 秒转天
                decay_factor = self._calculate_time_decay(days_passed, half_life_days=30)
                
                # accepted=+1, rejected=-1
                base_weight = 1.0 if feedback_type == 'accepted' else -1.0
                
                # 应用时间衰减
                weight = base_weight * decay_factor
                total_weight += weight
            
            # 归一化到0-1（使用sigmoid函数）
            normalized_weight = 1.0 / (1.0 + math.exp(-total_weight / len(results)))
            
            return normalized_weight
            
        except Exception as e:
            logger.error(f"[MappingLearner] 计算学习权重失败: {str(e)}")
            return 0.0
    
    def _calculate_time_decay(self, days_passed: float, half_life_days: float = 30.0) -> float:
        """
        计算时间衰减因子（指数衰减）
        
        Args:
            days_passed: 经过的天数
            half_life_days: 半衰期（天），默认30天
            
        Returns:
            衰减因子（0.0-1.0）
            
        公式: decay = e^(-λt), 其中 λ = ln(2) / half_life
        """
        lambda_value = math.log(2) / half_life_days
        decay = math.exp(-lambda_value * days_passed)
        return decay
    
    def get_weighted_recommendations(
        self,
        kook_channel_name: str,
        target_channels: List[Dict]
    ) -> List[Tuple[Dict, float]]:
        """
        获取加权后的推荐结果
        
        Args:
            kook_channel_name: KOOK频道名称
            target_channels: 目标频道列表
            
        Returns:
            [(channel, final_score), ...] 按分数降序排序
            
        final_score = base_score * 0.7 + learning_weight * 0.3
        """
        try:
            weighted_results = []
            
            for channel in target_channels:
                # 基础分数（从智能映射算法获得）
                base_score = channel.get('similarity_score', 0.0)
                
                # 学习权重
                learning_weight = self.get_learning_weight(
                    kook_channel_name,
                    channel.get('platform'),
                    channel.get('id')
                )
                
                # 综合分数（基础分数70%，学习权重30%）
                final_score = base_score * 0.7 + learning_weight * 0.3
                
                weighted_results.append((channel, final_score))
            
            # 按分数降序排序
            weighted_results.sort(key=lambda x: x[1], reverse=True)
            
            return weighted_results
            
        except Exception as e:
            logger.error(f"[MappingLearner] 获取加权推荐失败: {str(e)}")
            return []
    
    def get_learning_statistics(self) -> Dict:
        """
        获取学习统计信息
        
        Returns:
            {
                "total_feedbacks": int,
                "accepted_count": int,
                "rejected_count": int,
                "acceptance_rate": float,
                "recent_feedbacks": List[Dict],
                "top_learned_mappings": List[Dict]
            }
        """
        try:
            # 总反馈数
            total_result = db.execute("""
                SELECT COUNT(*) as count FROM mapping_learning_feedback
            """).fetchone()
            total_feedbacks = total_result['count'] if total_result else 0
            
            # 接受/拒绝数量
            accepted_result = db.execute("""
                SELECT COUNT(*) as count 
                FROM mapping_learning_feedback
                WHERE feedback_type = 'accepted'
            """).fetchone()
            accepted_count = accepted_result['count'] if accepted_result else 0
            
            rejected_result = db.execute("""
                SELECT COUNT(*) as count 
                FROM mapping_learning_feedback
                WHERE feedback_type = 'rejected'
            """).fetchone()
            rejected_count = rejected_result['count'] if rejected_result else 0
            
            # 接受率
            acceptance_rate = (accepted_count / total_feedbacks) if total_feedbacks > 0 else 0.0
            
            # 最近的反馈
            recent_results = db.execute("""
                SELECT kook_channel_name, target_platform, target_channel_name,
                       feedback_type, confidence_score, created_at
                FROM mapping_learning_feedback
                ORDER BY created_at DESC
                LIMIT 10
            """).fetchall()
            recent_feedbacks = [dict(row) for row in recent_results]
            
            # 学习效果最好的映射（按接受率）
            top_mappings = db.execute("""
                SELECT 
                    kook_channel_name,
                    target_platform,
                    target_channel_name,
                    SUM(CASE WHEN feedback_type = 'accepted' THEN 1 ELSE 0 END) as accepted,
                    COUNT(*) as total,
                    ROUND(100.0 * SUM(CASE WHEN feedback_type = 'accepted' THEN 1 ELSE 0 END) / COUNT(*), 1) as acceptance_rate
                FROM mapping_learning_feedback
                GROUP BY kook_channel_name, target_platform, target_channel_name
                HAVING total >= 3
                ORDER BY acceptance_rate DESC, total DESC
                LIMIT 10
            """).fetchall()
            top_learned_mappings = [dict(row) for row in top_mappings]
            
            return {
                "total_feedbacks": total_feedbacks,
                "accepted_count": accepted_count,
                "rejected_count": rejected_count,
                "acceptance_rate": round(acceptance_rate, 3),
                "recent_feedbacks": recent_feedbacks,
                "top_learned_mappings": top_learned_mappings
            }
            
        except Exception as e:
            logger.error(f"[MappingLearner] 获取统计信息失败: {str(e)}")
            return {
                "total_feedbacks": 0,
                "accepted_count": 0,
                "rejected_count": 0,
                "acceptance_rate": 0.0,
                "recent_feedbacks": [],
                "top_learned_mappings": []
            }
    
    def clear_old_feedbacks(self, days: int = 90):
        """
        清理旧的反馈记录
        
        Args:
            days: 保留最近多少天的记录，默认90天
        """
        try:
            cutoff_timestamp = int(time.time()) - (days * 86400)
            
            result = db.execute("""
                DELETE FROM mapping_learning_feedback
                WHERE created_timestamp < ?
            """, (cutoff_timestamp,))
            
            deleted_count = result.rowcount
            db.commit()
            
            logger.info(f"[MappingLearner] 已清理 {deleted_count} 条{days}天前的反馈记录")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"[MappingLearner] 清理旧反馈失败: {str(e)}")
            return 0


# 全局实例
mapping_learner = MappingLearner()
