"""
审计日志系统 - P0优化
记录所有关键用户操作，用于安全审计和问题追踪
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any
from ..database import db
from .logger import logger


class AuditLogger:
    """审计日志记录器"""
    
    # 操作类型定义
    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_ADD_ACCOUNT = "add_account"
    ACTION_DELETE_ACCOUNT = "delete_account"
    ACTION_UPDATE_ACCOUNT = "update_account"
    ACTION_ADD_BOT = "add_bot"
    ACTION_DELETE_BOT = "delete_bot"
    ACTION_UPDATE_BOT = "update_bot"
    ACTION_ADD_MAPPING = "add_mapping"
    ACTION_DELETE_MAPPING = "delete_mapping"
    ACTION_UPDATE_MAPPING = "update_mapping"
    ACTION_START_SERVICE = "start_service"
    ACTION_STOP_SERVICE = "stop_service"
    ACTION_RESTART_SERVICE = "restart_service"
    ACTION_UPDATE_SETTINGS = "update_settings"
    ACTION_EXPORT_CONFIG = "export_config"
    ACTION_IMPORT_CONFIG = "import_config"
    ACTION_BACKUP_DATABASE = "backup_database"
    ACTION_RESTORE_DATABASE = "restore_database"
    ACTION_CLEAR_LOGS = "clear_logs"
    ACTION_UPDATE_FILTER = "update_filter"
    ACTION_INSTALL_PLUGIN = "install_plugin"
    ACTION_UNINSTALL_PLUGIN = "uninstall_plugin"
    
    # 严重级别
    LEVEL_INFO = "info"
    LEVEL_WARNING = "warning"
    LEVEL_ERROR = "error"
    LEVEL_CRITICAL = "critical"
    
    def __init__(self):
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """确保审计日志表存在"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_id TEXT,
                        username TEXT,
                        action TEXT NOT NULL,
                        resource_type TEXT,
                        resource_id TEXT,
                        details TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        level TEXT DEFAULT 'info',
                        success INTEGER DEFAULT 1,
                        error_message TEXT
                    )
                """)
                
                # 添加索引
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp 
                    ON audit_logs(timestamp DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_action 
                    ON audit_logs(action)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_user 
                    ON audit_logs(user_id, timestamp DESC)
                """)
                
                logger.info("审计日志表初始化成功")
                
        except Exception as e:
            logger.error(f"审计日志表初始化失败: {str(e)}")
    
    def log(
        self,
        action: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        level: str = LEVEL_INFO,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """
        记录审计日志
        
        Args:
            action: 操作类型（使用预定义的ACTION_*常量）
            user_id: 用户ID
            username: 用户名
            resource_type: 资源类型（如account, bot, mapping等）
            resource_id: 资源ID
            details: 详细信息（JSON格式）
            ip_address: IP地址
            user_agent: 用户代理
            level: 严重级别（info/warning/error/critical）
            success: 操作是否成功
            error_message: 错误信息
            
        Returns:
            是否记录成功
        """
        try:
            details_json = json.dumps(details, ensure_ascii=False) if details else None
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_logs (
                        user_id, username, action, resource_type, resource_id,
                        details, ip_address, user_agent, level, success, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, username, action, resource_type, resource_id,
                    details_json, ip_address, user_agent, level, 
                    1 if success else 0, error_message
                ))
            
            # 同时写入系统日志
            log_msg = f"[审计] {username or user_id or 'Unknown'} - {action}"
            if resource_type:
                log_msg += f" - {resource_type}:{resource_id}"
            if not success:
                log_msg += f" - FAILED: {error_message}"
            
            if level == self.LEVEL_ERROR or level == self.LEVEL_CRITICAL:
                logger.error(log_msg)
            elif level == self.LEVEL_WARNING:
                logger.warning(log_msg)
            else:
                logger.info(log_msg)
            
            return True
            
        except Exception as e:
            logger.error(f"记录审计日志失败: {str(e)}")
            return False
    
    def get_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        level: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        success_only: Optional[bool] = None
    ) -> list:
        """
        查询审计日志
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            user_id: 用户ID筛选
            action: 操作类型筛选
            level: 严重级别筛选
            start_date: 开始日期
            end_date: 结束日期
            success_only: 仅显示成功/失败的操作
            
        Returns:
            审计日志列表
        """
        try:
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if action:
                query += " AND action = ?"
                params.append(action)
            
            if level:
                query += " AND level = ?"
                params.append(level)
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            if success_only is not None:
                query += " AND success = ?"
                params.append(1 if success_only else 0)
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            result = db.execute(query, tuple(params))
            logs = [dict(row) for row in result.fetchall()]
            
            # 解析JSON details
            for log in logs:
                if log.get('details'):
                    try:
                        log['details'] = json.loads(log['details'])
                    except:
                        pass
            
            return logs
            
        except Exception as e:
            logger.error(f"查询审计日志失败: {str(e)}")
            return []
    
    def get_statistics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取审计日志统计信息
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            统计信息
        """
        try:
            query_base = "SELECT COUNT(*) as count FROM audit_logs WHERE 1=1"
            params = []
            
            if start_date:
                query_base += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query_base += " AND timestamp <= ?"
                params.append(end_date)
            
            # 总数统计
            result = db.execute(query_base, tuple(params))
            total_count = result.fetchone()['count']
            
            # 按操作类型统计
            query_action = query_base.replace("COUNT(*)", "action, COUNT(*)")
            query_action += " GROUP BY action ORDER BY COUNT(*) DESC LIMIT 10"
            result = db.execute(query_action, tuple(params))
            action_stats = [dict(row) for row in result.fetchall()]
            
            # 按级别统计
            query_level = query_base.replace("COUNT(*)", "level, COUNT(*)")
            query_level += " GROUP BY level"
            result = db.execute(query_level, tuple(params))
            level_stats = [dict(row) for row in result.fetchall()]
            
            # 成功/失败统计
            query_success = query_base + " AND success = 1"
            result = db.execute(query_success, tuple(params))
            success_count = result.fetchone()['count']
            
            query_failed = query_base + " AND success = 0"
            result = db.execute(query_failed, tuple(params))
            failed_count = result.fetchone()['count']
            
            # 按用户统计
            query_user = query_base.replace("COUNT(*)", "username, COUNT(*)")
            query_user += " AND username IS NOT NULL GROUP BY username ORDER BY COUNT(*) DESC LIMIT 10"
            result = db.execute(query_user, tuple(params))
            user_stats = [dict(row) for row in result.fetchall()]
            
            return {
                "total_count": total_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "action_stats": action_stats,
                "level_stats": level_stats,
                "user_stats": user_stats
            }
            
        except Exception as e:
            logger.error(f"获取审计日志统计失败: {str(e)}")
            return {}
    
    def clean_old_logs(self, days: int = 90) -> int:
        """
        清理旧的审计日志
        
        Args:
            days: 保留天数
            
        Returns:
            清理的记录数
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM audit_logs 
                    WHERE timestamp < datetime('now', '-' || ? || ' days')
                """, (days,))
                deleted_count = cursor.rowcount
            
            logger.info(f"清理了 {deleted_count} 条审计日志（{days}天前）")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理审计日志失败: {str(e)}")
            return 0


# 全局审计日志实例
audit_logger = AuditLogger()
