"""
错误处理模块测试
"""
import pytest
from app.utils.error_handler import ErrorSolution, ErrorCategory, handle_error, format_success_message


class TestErrorSolution:
    """测试ErrorSolution类"""
    
    def test_get_friendly_error_network_timeout(self):
        """测试网络超时错误"""
        error = ErrorSolution.get_friendly_error(
            "network_timeout",
            target="Discord API"
        )
        
        assert error["category"] == ErrorCategory.NETWORK.value
        assert "超时" in error["user_message"]
        assert "Discord API" in error["detail"]
        assert len(error["solutions"]) > 0
    
    def test_get_friendly_error_auth_invalid_cookie(self):
        """测试Cookie无效错误"""
        error = ErrorSolution.get_friendly_error("auth_invalid_cookie")
        
        assert error["category"] == ErrorCategory.AUTHENTICATION.value
        assert "Cookie" in error["user_message"]
        assert error["docs_link"] is not None
    
    def test_get_friendly_error_unknown(self):
        """测试未知错误"""
        error = ErrorSolution.get_friendly_error(
            "unknown_error_key",
            detail="Some error"
        )
        
        assert error["category"] == ErrorCategory.UNKNOWN.value
        assert "未知错误" in error["user_message"]
    
    def test_format_exception_timeout(self):
        """测试格式化超时异常"""
        exception = TimeoutError("Connection timed out")
        error = ErrorSolution.format_exception(exception, context="Discord API")
        
        assert error["category"] == ErrorCategory.NETWORK.value
        assert "超时" in error["user_message"]
        assert "Discord API" in error["detail"]
    
    def test_format_exception_generic(self):
        """测试格式化通用异常"""
        exception = ValueError("Invalid value")
        error = ErrorSolution.format_exception(exception)
        
        assert error["category"] == ErrorCategory.UNKNOWN.value
        assert "ValueError" in error["technical_error"]


class TestHandleError:
    """测试handle_error函数"""
    
    def test_handle_network_error(self):
        """测试处理网络错误"""
        status_code, response = handle_error(
            "network_timeout",
            target="Test API"
        )
        
        assert status_code == 500
        assert response["success"] is False
        assert "error" in response
    
    def test_handle_auth_error(self):
        """测试处理认证错误"""
        status_code, response = handle_error("auth_invalid_cookie")
        
        assert status_code == 401
        assert response["success"] is False
    
    def test_handle_config_error(self):
        """测试处理配置错误"""
        status_code, response = handle_error(
            "config_missing_required",
            field="webhook_url"
        )
        
        assert status_code == 400
        assert response["success"] is False


class TestFormatSuccessMessage:
    """测试format_success_message函数"""
    
    def test_format_simple_success(self):
        """测试格式化简单成功消息"""
        message = format_success_message("登录")
        
        assert message["success"] is True
        assert "登录" in message["message"]
        assert "✅" in message["message"]
    
    def test_format_success_with_detail(self):
        """测试格式化带详情的成功消息"""
        message = format_success_message("保存配置", detail="已保存3个Bot配置")
        
        assert message["success"] is True
        assert "保存配置" in message["message"]
        assert message["detail"] == "已保存3个Bot配置"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
