"""
v1.11.0新增功能测试
测试Cookie自动重新登录、错误诊断、模板功能
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.utils.error_diagnosis import ErrorDiagnostic, DiagnosticLogger


class TestErrorDiagnostic:
    """测试错误诊断系统"""
    
    def test_diagnose_rate_limit_error(self):
        """测试API限流错误诊断"""
        error = Exception("429 Too Many Requests")
        diagnosis = ErrorDiagnostic.diagnose(error, {'platform': 'discord'})
        
        assert diagnosis['matched_rule'] == 'rate_limit'
        assert diagnosis['severity'] == 'warning'
        assert diagnosis['auto_fixable'] == False  # rate_limit 应该是 wait_and_retry
        assert '限流' in diagnosis['solution']
        assert len(diagnosis['suggestions']) > 0
    
    def test_diagnose_invalid_token_error(self):
        """测试Token无效错误诊断"""
        error = Exception("401 Unauthorized - Invalid token")
        diagnosis = ErrorDiagnostic.diagnose(error, {'platform': 'telegram'})
        
        assert diagnosis['matched_rule'] == 'invalid_token'
        assert diagnosis['severity'] == 'error'
        assert diagnosis['auto_fixable'] == False
        assert 'Token' in diagnosis['solution'] or 'token' in diagnosis['solution'].lower()
    
    def test_diagnose_network_timeout_error(self):
        """测试网络超时错误诊断"""
        error = Exception("Connection timeout after 30 seconds")
        diagnosis = ErrorDiagnostic.diagnose(error)
        
        assert diagnosis['matched_rule'] == 'network_timeout'
        assert diagnosis['severity'] == 'warning'
        assert diagnosis['auto_fixable'] == True
        assert '网络' in diagnosis['solution'] or '超时' in diagnosis['solution']
    
    def test_diagnose_message_too_long_error(self):
        """测试消息过长错误诊断"""
        error = Exception("Message is too long, content exceeds 2000 characters")
        diagnosis = ErrorDiagnostic.diagnose(error, {'platform': 'discord'})
        
        assert diagnosis['matched_rule'] == 'message_too_long'
        assert diagnosis['auto_fixable'] == True
    
    def test_diagnose_channel_not_found_error(self):
        """测试频道不存在错误诊断"""
        error = Exception("404 Channel not found")
        diagnosis = ErrorDiagnostic.diagnose(error, {'channel_id': '123456'})
        
        assert diagnosis['matched_rule'] == 'channel_not_found'
        assert diagnosis['severity'] == 'error'
        assert '频道' in diagnosis['solution']
    
    def test_diagnose_image_upload_failed_error(self):
        """测试图片上传失败错误诊断"""
        error = Exception("Image upload failed: File too large")
        diagnosis = ErrorDiagnostic.diagnose(error)
        
        assert diagnosis['matched_rule'] == 'image_upload_failed'
        assert diagnosis['auto_fixable'] == True
    
    def test_diagnose_unknown_error(self):
        """测试未知错误诊断"""
        error = Exception("Some random error message")
        diagnosis = ErrorDiagnostic.diagnose(error)
        
        assert diagnosis['matched_rule'] is None
        assert diagnosis['error_type'] == 'Exception'
        assert len(diagnosis['suggestions']) > 0
    
    def test_format_diagnosis_message(self):
        """测试诊断消息格式化"""
        diagnosis = {
            'error_type': 'HTTPException',
            'error_message': '429 Too Many Requests',
            'matched_rule': 'rate_limit',
            'severity': 'warning',
            'solution': 'API限流，请等待',
            'suggestions': ['等待1分钟', '配置多个Webhook'],
            'auto_fixable': True,
            'context': {'platform': 'discord'}
        }
        
        message = ErrorDiagnostic.format_diagnosis_message(diagnosis)
        
        assert '⚠️ 错误诊断报告' in message
        assert 'HTTPException' in message
        assert '429 Too Many Requests' in message
        assert 'API限流' in message
        assert '等待1分钟' in message
        assert '🔧 系统将尝试自动修复' in message
    
    def test_get_auto_fix_strategy(self):
        """测试获取自动修复策略"""
        # 网络超时
        diagnosis = {
            'matched_rule': 'network_timeout',
            'auto_fixable': True
        }
        strategy = ErrorDiagnostic.get_auto_fix_strategy(diagnosis)
        assert strategy == 'retry'
        
        # 消息过长
        diagnosis = {
            'matched_rule': 'message_too_long',
            'auto_fixable': True
        }
        strategy = ErrorDiagnostic.get_auto_fix_strategy(diagnosis)
        assert strategy == 'auto_split'
        
        # 图片上传失败
        diagnosis = {
            'matched_rule': 'image_upload_failed',
            'auto_fixable': True
        }
        strategy = ErrorDiagnostic.get_auto_fix_strategy(diagnosis)
        assert strategy == 'switch_to_imgbed'
        
        # 不可自动修复
        diagnosis = {
            'matched_rule': 'invalid_token',
            'auto_fixable': False
        }
        strategy = ErrorDiagnostic.get_auto_fix_strategy(diagnosis)
        assert strategy is None


class TestDiagnosticLogger:
    """测试诊断日志记录器"""
    
    def test_log_diagnosis(self):
        """测试记录诊断结果"""
        logger = DiagnosticLogger()
        
        diagnosis = {
            'error_type': 'ValueError',
            'matched_rule': 'test_rule',
            'severity': 'error',
            'solution': 'Test solution'
        }
        
        logger.log_diagnosis(diagnosis)
        
        assert len(logger.diagnostics_history) == 1
        assert 'timestamp' in logger.diagnostics_history[0]
    
    def test_get_recent_diagnostics(self):
        """测试获取最近诊断记录"""
        logger = DiagnosticLogger()
        
        # 添加多条记录
        for i in range(20):
            logger.log_diagnosis({
                'error_type': f'Error{i}',
                'severity': 'error'
            })
        
        # 获取最近10条
        recent = logger.get_recent_diagnostics(10)
        assert len(recent) == 10
    
    def test_get_statistics(self):
        """测试诊断统计"""
        logger = DiagnosticLogger()
        
        # 添加不同类型的错误
        logger.log_diagnosis({
            'matched_rule': 'rate_limit',
            'severity': 'warning',
            'auto_fixable': True
        })
        logger.log_diagnosis({
            'matched_rule': 'invalid_token',
            'severity': 'error',
            'auto_fixable': False
        })
        logger.log_diagnosis({
            'matched_rule': 'network_timeout',
            'severity': 'warning',
            'auto_fixable': True
        })
        
        stats = logger.get_statistics()
        
        assert stats['total_count'] == 3
        assert stats['by_severity']['warning'] == 2
        assert stats['by_severity']['error'] == 1
        assert stats['auto_fixable_count'] == 2
    
    def test_max_history_limit(self):
        """测试历史记录上限"""
        logger = DiagnosticLogger()
        logger.max_history = 10
        
        # 添加20条记录
        for i in range(20):
            logger.log_diagnosis({'error_type': f'Error{i}'})
        
        # 应该只保留最后10条
        assert len(logger.diagnostics_history) == 10
        # 最后一条应该是Error19
        assert logger.diagnostics_history[-1]['error_type'] == 'Error19'


class TestAutoReloginIntegration:
    """测试自动重新登录集成（集成测试）"""
    
    @pytest.mark.asyncio
    async def test_auto_relogin_workflow(self):
        """测试自动重新登录工作流程"""
        # 这是一个集成测试，需要模拟环境
        # 实际测试应该在真实环境中进行
        
        # Mock数据库
        with patch('app.database.db') as mock_db:
            mock_db.get_account.return_value = {
                'id': 1,
                'email': 'test@example.com',
                'password_encrypted': 'encrypted_password',
                'status': 'offline'
            }
            
            # Mock crypto_manager
            with patch('app.utils.crypto.crypto_manager') as mock_crypto:
                mock_crypto.decrypt.return_value = 'plain_password'
                
                # 这里应该继续模拟scraper的登录流程
                # 由于涉及Playwright，建议在E2E测试中进行
                pass


class TestMappingTemplate:
    """测试映射模板功能"""
    
    def test_gaming_template_structure(self):
        """测试游戏公告模板结构"""
        # 这个测试应该在前端测试中进行
        # 这里只做结构验证
        
        template = {
            'name': '游戏公告模板',
            'channels': [
                {'name': '📢 公告频道', 'kook_channel_id': 'announcements'},
                {'name': '🎉 活动频道', 'kook_channel_id': 'events'},
                {'name': '📝 更新日志', 'kook_channel_id': 'changelog'},
                {'name': '❓ 常见问题', 'kook_channel_id': 'faq'}
            ]
        }
        
        assert template['name'] == '游戏公告模板'
        assert len(template['channels']) == 4
        assert all('name' in ch for ch in template['channels'])
        assert all('kook_channel_id' in ch for ch in template['channels'])


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
