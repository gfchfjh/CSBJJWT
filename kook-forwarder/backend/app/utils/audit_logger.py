"""
安全审计日志模块
用于记录关键操作和安全事件
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from .logger import logger
from ..config import settings


class AuditLogger:
    """安全审计日志记录器"""
    
    def __init__(self):
        self.audit_log_dir = settings.log_dir / "audit"
        self.audit_log_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_audit_file(self) -> Path:
        """获取当前审计日志文件路径"""
        date_str = datetime.now().strftime("%Y-%m")
        return self.audit_log_dir / f"audit_{date_str}.log"
    
    def _write_audit(self, event_type: str, event_data: Dict[str, Any]):
        """写入审计日志"""
        try:
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": event_data
            }
            
            # 写入审计日志文件（JSON格式，每行一条）
            with open(self._get_audit_file(), 'a', encoding='utf-8') as f:
                f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"写入审计日志失败: {str(e)}")
    
    def log_login(self, account_id: int, email: str, 
                   method: str, success: bool, 
                   ip: Optional[str] = None):
        """
        记录登录事件
        
        Args:
            account_id: 账号ID
            email: 邮箱
            method: 登录方式（cookie/password）
            success: 是否成功
            ip: IP地址
        """
        self._write_audit("LOGIN", {
            "account_id": account_id,
            "email": email,
            "method": method,
            "success": success,
            "ip": ip,
            "severity": "INFO" if success else "WARNING"
        })
        
        log_msg = f"登录{'成功' if success else '失败'}: {email} (ID:{account_id}) 方式:{method}"
        if ip:
            log_msg += f" IP:{ip}"
            
        if success:
            logger.info(log_msg)
        else:
            logger.warning(log_msg)
    
    def log_logout(self, account_id: int, email: str):
        """
        记录登出事件
        
        Args:
            account_id: 账号ID
            email: 邮箱
        """
        self._write_audit("LOGOUT", {
            "account_id": account_id,
            "email": email,
            "severity": "INFO"
        })
        logger.info(f"登出: {email} (ID:{account_id})")
    
    def log_config_change(self, user_id: Optional[int], 
                         config_type: str, 
                         old_value: Any, 
                         new_value: Any,
                         description: str = ""):
        """
        记录配置变更
        
        Args:
            user_id: 用户ID
            config_type: 配置类型
            old_value: 旧值
            new_value: 新值
            description: 描述
        """
        self._write_audit("CONFIG_CHANGE", {
            "user_id": user_id,
            "config_type": config_type,
            "old_value": str(old_value)[:100],  # 限制长度
            "new_value": str(new_value)[:100],
            "description": description,
            "severity": "INFO"
        })
        logger.info(f"配置变更: {config_type} - {description}")
    
    def log_data_access(self, user_id: Optional[int], 
                       resource_type: str, 
                       resource_id: str,
                       action: str):
        """
        记录数据访问
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型（account/bot/mapping等）
            resource_id: 资源ID
            action: 操作（read/create/update/delete）
        """
        self._write_audit("DATA_ACCESS", {
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "severity": "DEBUG" if action == "read" else "INFO"
        })
        
        if action != "read":  # 读操作不记录到常规日志，避免过多
            logger.info(f"数据操作: {action} {resource_type}:{resource_id}")
    
    def log_security_event(self, event: str, 
                          severity: str, 
                          details: Dict[str, Any]):
        """
        记录安全事件
        
        Args:
            event: 事件名称
            severity: 严重程度（INFO/WARNING/ERROR/CRITICAL）
            details: 详细信息
        """
        self._write_audit("SECURITY_EVENT", {
            "event": event,
            "severity": severity,
            "details": details
        })
        
        log_func = {
            "INFO": logger.info,
            "WARNING": logger.warning,
            "ERROR": logger.error,
            "CRITICAL": logger.critical
        }.get(severity, logger.info)
        
        log_func(f"安全事件 [{severity}]: {event} - {json.dumps(details, ensure_ascii=False)}")
    
    def log_api_access(self, endpoint: str, 
                      method: str, 
                      status_code: int,
                      ip: Optional[str] = None,
                      user_agent: Optional[str] = None,
                      duration_ms: Optional[int] = None):
        """
        记录API访问
        
        Args:
            endpoint: API端点
            method: HTTP方法
            status_code: 状态码
            ip: IP地址
            user_agent: User-Agent
            duration_ms: 响应时间（毫秒）
        """
        self._write_audit("API_ACCESS", {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "ip": ip,
            "user_agent": user_agent,
            "duration_ms": duration_ms,
            "severity": "WARNING" if status_code >= 400 else "DEBUG"
        })
        
        # 仅记录异常状态码到常规日志
        if status_code >= 400:
            logger.warning(f"API异常: {method} {endpoint} -> {status_code} ({duration_ms}ms)")
    
    def log_message_forward(self, message_id: str,
                           source_channel: str,
                           target_platform: str,
                           target_channel: str,
                           success: bool,
                           error: Optional[str] = None):
        """
        记录消息转发（关键操作）
        
        Args:
            message_id: 消息ID
            source_channel: 源频道
            target_platform: 目标平台
            target_channel: 目标频道
            success: 是否成功
            error: 错误信息
        """
        self._write_audit("MESSAGE_FORWARD", {
            "message_id": message_id,
            "source_channel": source_channel,
            "target_platform": target_platform,
            "target_channel": target_channel,
            "success": success,
            "error": error,
            "severity": "INFO" if success else "ERROR"
        })
        
        if not success:
            logger.error(f"消息转发失败: {message_id} -> {target_platform}:{target_channel} - {error}")
    
    def log_file_operation(self, operation: str, 
                          file_path: str, 
                          success: bool,
                          error: Optional[str] = None):
        """
        记录文件操作
        
        Args:
            operation: 操作类型（read/write/delete）
            file_path: 文件路径
            success: 是否成功
            error: 错误信息
        """
        self._write_audit("FILE_OPERATION", {
            "operation": operation,
            "file_path": file_path,
            "success": success,
            "error": error,
            "severity": "WARNING" if not success else "DEBUG"
        })
        
        if not success:
            logger.warning(f"文件操作失败: {operation} {file_path} - {error}")
    
    def get_recent_audits(self, event_type: Optional[str] = None, 
                         limit: int = 100) -> list:
        """
        获取最近的审计日志
        
        Args:
            event_type: 事件类型过滤
            limit: 返回数量限制
            
        Returns:
            审计日志列表
        """
        try:
            audit_file = self._get_audit_file()
            if not audit_file.exists():
                return []
            
            audits = []
            with open(audit_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        audit = json.loads(line.strip())
                        if event_type is None or audit.get('event_type') == event_type:
                            audits.append(audit)
                    except json.JSONDecodeError:
                        continue
            
            # 返回最新的N条（倒序）
            return audits[-limit:][::-1]
            
        except Exception as e:
            logger.error(f"读取审计日志失败: {str(e)}")
            return []


# 创建全局审计日志实例
audit_logger = AuditLogger()
