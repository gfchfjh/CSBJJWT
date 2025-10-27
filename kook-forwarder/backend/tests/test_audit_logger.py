"""
测试安全审计日志模块
"""
import pytest
import json
from pathlib import Path
from datetime import datetime
from app.utils.audit_logger import AuditLogger, audit_logger


class TestAuditLogger:
    """测试审计日志功能"""
    
    def test_audit_logger_init(self, tmp_path):
        """测试审计日志初始化"""
        logger = AuditLogger()
        assert logger.audit_log_dir.exists()
        assert logger.audit_log_dir.is_dir()
    
    def test_log_login_success(self):
        """测试记录成功登录"""
        audit_logger.log_login(
            account_id=1,
            email="test@example.com",
            method="cookie",
            success=True,
            ip="127.0.0.1"
        )
        
        # 验证审计日志已写入
        audits = audit_logger.get_recent_audits(event_type="LOGIN", limit=1)
        assert len(audits) > 0
        
        latest = audits[0]
        assert latest['event_type'] == 'LOGIN'
        assert latest['data']['account_id'] == 1
        assert latest['data']['email'] == "test@example.com"
        assert latest['data']['success'] is True
    
    def test_log_login_failure(self):
        """测试记录失败登录"""
        audit_logger.log_login(
            account_id=2,
            email="fail@example.com",
            method="password",
            success=False
        )
        
        audits = audit_logger.get_recent_audits(event_type="LOGIN", limit=1)
        latest = audits[0]
        assert latest['data']['success'] is False
        assert latest['data']['severity'] == 'WARNING'
    
    def test_log_config_change(self):
        """测试记录配置变更"""
        audit_logger.log_config_change(
            user_id=1,
            config_type="redis_host",
            old_value="localhost",
            new_value="127.0.0.1",
            description="更改Redis主机地址"
        )
        
        audits = audit_logger.get_recent_audits(event_type="CONFIG_CHANGE", limit=1)
        assert len(audits) > 0
        
        latest = audits[0]
        assert latest['data']['config_type'] == 'redis_host'
        assert latest['data']['old_value'] == 'localhost'
        assert latest['data']['new_value'] == '127.0.0.1'
    
    def test_log_data_access(self):
        """测试记录数据访问"""
        audit_logger.log_data_access(
            user_id=1,
            resource_type="account",
            resource_id="123",
            action="update"
        )
        
        audits = audit_logger.get_recent_audits(event_type="DATA_ACCESS", limit=1)
        latest = audits[0]
        assert latest['data']['resource_type'] == 'account'
        assert latest['data']['action'] == 'update'
    
    def test_log_security_event_critical(self):
        """测试记录严重安全事件"""
        audit_logger.log_security_event(
            event="多次登录失败",
            severity="CRITICAL",
            details={
                "ip": "192.168.1.100",
                "attempts": 5,
                "timespan": "1分钟"
            }
        )
        
        audits = audit_logger.get_recent_audits(event_type="SECURITY_EVENT", limit=1)
        latest = audits[0]
        assert latest['data']['severity'] == 'CRITICAL'
        assert latest['data']['event'] == '多次登录失败'
    
    def test_log_api_access(self):
        """测试记录API访问"""
        audit_logger.log_api_access(
            endpoint="/api/accounts",
            method="GET",
            status_code=200,
            ip="127.0.0.1",
            duration_ms=45
        )
        
        audits = audit_logger.get_recent_audits(event_type="API_ACCESS", limit=1)
        latest = audits[0]
        assert latest['data']['endpoint'] == '/api/accounts'
        assert latest['data']['status_code'] == 200
    
    def test_log_api_access_error(self):
        """测试记录API错误访问"""
        audit_logger.log_api_access(
            endpoint="/api/bots",
            method="POST",
            status_code=500,
            ip="127.0.0.1",
            duration_ms=1200
        )
        
        audits = audit_logger.get_recent_audits(event_type="API_ACCESS", limit=1)
        latest = audits[0]
        assert latest['data']['status_code'] == 500
        assert latest['data']['severity'] == 'WARNING'
    
    def test_log_message_forward_success(self):
        """测试记录消息转发成功"""
        audit_logger.log_message_forward(
            message_id="msg_123",
            source_channel="channel_456",
            target_platform="discord",
            target_channel="789",
            success=True
        )
        
        audits = audit_logger.get_recent_audits(event_type="MESSAGE_FORWARD", limit=1)
        latest = audits[0]
        assert latest['data']['success'] is True
        assert latest['data']['target_platform'] == 'discord'
    
    def test_log_message_forward_failure(self):
        """测试记录消息转发失败"""
        audit_logger.log_message_forward(
            message_id="msg_456",
            source_channel="channel_789",
            target_platform="telegram",
            target_channel="1001",
            success=False,
            error="API限流"
        )
        
        audits = audit_logger.get_recent_audits(event_type="MESSAGE_FORWARD", limit=1)
        latest = audits[0]
        assert latest['data']['success'] is False
        assert latest['data']['error'] == 'API限流'
        assert latest['data']['severity'] == 'ERROR'
    
    def test_log_file_operation(self):
        """测试记录文件操作"""
        audit_logger.log_file_operation(
            operation="write",
            file_path="/data/config.db",
            success=True
        )
        
        audits = audit_logger.get_recent_audits(event_type="FILE_OPERATION", limit=1)
        latest = audits[0]
        assert latest['data']['operation'] == 'write'
        assert latest['data']['success'] is True
    
    def test_get_recent_audits_limit(self):
        """测试获取审计日志数量限制"""
        # 记录多条日志
        for i in range(10):
            audit_logger.log_data_access(
                user_id=1,
                resource_type="test",
                resource_id=str(i),
                action="read"
            )
        
        # 获取最近5条
        audits = audit_logger.get_recent_audits(limit=5)
        assert len(audits) <= 5
    
    def test_get_recent_audits_filter(self):
        """测试过滤特定类型审计日志"""
        # 记录不同类型的日志
        audit_logger.log_login(1, "test@example.com", "cookie", True)
        audit_logger.log_logout(1, "test@example.com")
        
        # 仅获取LOGIN类型
        login_audits = audit_logger.get_recent_audits(event_type="LOGIN", limit=10)
        for audit in login_audits:
            assert audit['event_type'] == 'LOGIN'
    
    def test_audit_file_format(self):
        """测试审计日志文件格式"""
        audit_logger.log_security_event(
            event="测试事件",
            severity="INFO",
            details={"test": "data"}
        )
        
        audit_file = audit_logger._get_audit_file()
        assert audit_file.exists()
        
        # 读取最后一行，验证JSON格式
        with open(audit_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1]
                audit_entry = json.loads(last_line)
                
                assert 'timestamp' in audit_entry
                assert 'event_type' in audit_entry
                assert 'data' in audit_entry
    
    def test_audit_timestamp_format(self):
        """测试审计日志时间戳格式"""
        audit_logger.log_security_event(
            event="时间戳测试",
            severity="INFO",
            details={}
        )
        
        audits = audit_logger.get_recent_audits(event_type="SECURITY_EVENT", limit=1)
        latest = audits[0]
        
        # 验证时间戳格式
        timestamp = latest['timestamp']
        assert 'T' in timestamp  # ISO格式包含T
        
        # 验证可以解析
        dt = datetime.fromisoformat(timestamp)
        assert isinstance(dt, datetime)
    
    def test_large_value_truncation(self):
        """测试大数据值截断"""
        large_value = "x" * 200
        
        audit_logger.log_config_change(
            user_id=1,
            config_type="test",
            old_value=large_value,
            new_value=large_value,
            description="测试截断"
        )
        
        audits = audit_logger.get_recent_audits(event_type="CONFIG_CHANGE", limit=1)
        latest = audits[0]
        
        # 验证值被截断到100字符
        assert len(latest['data']['old_value']) == 100
        assert len(latest['data']['new_value']) == 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
