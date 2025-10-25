"""
Cookie解析器增强版测试
版本: v6.0.0
"""

import pytest
from app.utils.cookie_parser_enhanced import cookie_parser_enhanced


class TestCookieParserEnhanced:
    """Cookie解析器测试类"""
    
    def test_parse_json_array(self):
        """测试JSON数组格式"""
        cookie_str = '[{"name": "test", "value": "123", "domain": ".kookapp.cn"}]'
        cookies = cookie_parser_enhanced.parse(cookie_str)
        
        assert len(cookies) == 1
        assert cookies[0]['name'] == 'test'
        assert cookies[0]['value'] == '123'
        assert cookies[0]['domain'] == '.kookapp.cn'
    
    def test_parse_json_object(self):
        """测试JSON对象格式"""
        cookie_str = '{"cookie1": "value1", "cookie2": "value2"}'
        cookies = cookie_parser_enhanced.parse(cookie_str)
        
        assert len(cookies) == 2
        assert any(c['name'] == 'cookie1' and c['value'] == 'value1' for c in cookies)
    
    def test_parse_with_single_quotes(self):
        """测试单引号格式（自动修复）"""
        cookie_str = "[{'name': 'test', 'value': '123'}]"
        cookies = cookie_parser_enhanced.parse(cookie_str)
        
        assert len(cookies) == 1
        assert "单引号转双引号" in cookie_parser_enhanced.get_error_fixes()
    
    def test_parse_with_trailing_comma(self):
        """测试尾随逗号（自动修复）"""
        cookie_str = '[{"name": "test", "value": "123",}]'
        cookies = cookie_parser_enhanced.parse(cookie_str)
        
        assert len(cookies) == 1
        assert "移除尾随逗号" in cookie_parser_enhanced.get_error_fixes()
    
    def test_parse_python_keywords(self):
        """测试Python关键字（自动修复）"""
        cookie_str = '[{"name": "test", "value": "123", "secure": True, "httpOnly": False}]'
        cookies = cookie_parser_enhanced.parse(cookie_str)
        
        assert len(cookies) == 1
        assert "转换Python关键字" in cookie_parser_enhanced.get_error_fixes()
    
    def test_parse_netscape_format(self):
        """测试Netscape格式"""
        cookie_str = """# Netscape HTTP Cookie File
.kookapp.cn\tTRUE\t/\tTRUE\t1735660800\ttest\t123
.kookapp.cn\tTRUE\t/\tFALSE\t1735660800\ttest2\t456"""
        
        cookies = cookie_parser_enhanced.parse(cookie_str)
        
        assert len(cookies) == 2
        assert cookies[0]['name'] == 'test'
        assert cookies[0]['secure'] == True
    
    def test_parse_header_string(self):
        """测试HTTP Cookie头格式"""
        cookie_str = "Cookie: test=123; test2=456; test3=789"
        cookies = cookie_parser_enhanced.parse(cookie_str)
        
        assert len(cookies) == 3
        assert cookies[0]['name'] == 'test'
    
    def test_parse_key_value_lines(self):
        """测试键值对行格式"""
        cookie_str = """test=123
test2=456
test3=789"""
        
        cookies = cookie_parser_enhanced.parse(cookie_str)
        
        assert len(cookies) == 3
    
    def test_parse_javascript_format(self):
        """测试JavaScript格式"""
        cookie_str = '''document.cookie = "test=123";
document.cookie = "test2=456";'''
        
        cookies = cookie_parser_enhanced.parse(cookie_str)
        
        assert len(cookies) == 2
    
    def test_parse_empty_cookie(self):
        """测试空Cookie"""
        with pytest.raises(ValueError, match="Cookie为空"):
            cookie_parser_enhanced.parse("")
    
    def test_parse_invalid_format(self):
        """测试无效格式"""
        with pytest.raises(ValueError):
            cookie_parser_enhanced.parse("this is not a valid cookie format")
    
    def test_validate_cookies(self):
        """测试Cookie验证"""
        cookies = [
            {"name": "test1", "value": "123", "domain": ".kookapp.cn"},
            {"name": "test2", "value": "456", "domain": ".kookapp.cn"},
            {"name": "test3", "value": "789", "domain": ".kookapp.cn"}
        ]
        
        valid, message = cookie_parser_enhanced.validate(cookies)
        
        assert valid == True
        assert "验证通过" in message
    
    def test_validate_empty_cookies(self):
        """测试空Cookie列表验证"""
        valid, message = cookie_parser_enhanced.validate([])
        
        assert valid == False
        assert "为空" in message
    
    def test_validate_few_cookies(self):
        """测试Cookie数量不足警告"""
        cookies = [{"name": "test", "value": "123", "domain": ".kookapp.cn"}]
        
        valid, message = cookie_parser_enhanced.validate(cookies)
        
        assert valid == True  # 仍然有效
        assert "警告" in message or "较少" in message
    
    def test_validate_wrong_domain(self):
        """测试错误域名警告"""
        cookies = [
            {"name": "test1", "value": "123", "domain": ".example.com"},
            {"name": "test2", "value": "456", "domain": ".example.com"}
        ]
        
        valid, message = cookie_parser_enhanced.validate(cookies)
        
        assert valid == True  # 仍然有效
        assert "警告" in message or "域名" in message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
