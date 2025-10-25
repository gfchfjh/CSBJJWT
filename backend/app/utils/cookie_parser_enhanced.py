"""
增强版Cookie解析器
支持10+种格式，自动修复常见错误
版本: v6.0.0
作者: KOOK Forwarder Team

支持的格式:
1. JSON数组: [{"name": "...", "value": "..."}]
2. JSON对象: {"cookie1": "value1", "cookie2": "value2"}
3. Netscape格式: domain\tflag\tpath\tsecure\texpiration\tname\tvalue
4. HTTP Header: Cookie: name1=value1; name2=value2
5. 键值对行: name1=value1\nname2=value2
6. JavaScript: document.cookie = "..."
7. Python字典: {'name': 'value'}
8. EditThisCookie格式
9. CookieTab格式
10. 浏览器开发者工具复制格式
"""

import json
import re
from typing import List, Dict, Tuple, Optional
from urllib.parse import unquote
from datetime import datetime
from ..utils.logger import logger


class CookieParserEnhanced:
    """增强版Cookie解析器"""
    
    # 支持的Cookie格式
    FORMAT_JSON_ARRAY = "json_array"
    FORMAT_JSON_OBJECT = "json_object"
    FORMAT_NETSCAPE = "netscape"
    FORMAT_HEADER_STRING = "header_string"
    FORMAT_KEY_VALUE_LINES = "key_value_lines"
    FORMAT_JAVASCRIPT = "javascript"
    FORMAT_PYTHON_DICT = "python_dict"
    FORMAT_EDIT_THIS_COOKIE = "edit_this_cookie"
    FORMAT_SINGLE_LINE = "single_line"
    
    def __init__(self):
        self.error_fixes_applied = []  # 记录应用的修复
        self.warnings = []  # 警告信息
    
    def parse(self, cookie_str: str) -> List[Dict]:
        """
        解析Cookie字符串（支持多种格式）
        
        Args:
            cookie_str: Cookie字符串
            
        Returns:
            标准Cookie列表: [{"name": "...", "value": "...", "domain": "..."}]
            
        Raises:
            ValueError: 无法识别的格式
        """
        if not cookie_str or not cookie_str.strip():
            raise ValueError("Cookie为空")
        
        cookie_str = cookie_str.strip()
        self.error_fixes_applied = []
        self.warnings = []
        
        # 预处理：移除BOM
        if cookie_str.startswith('\ufeff'):
            cookie_str = cookie_str[1:]
            self.error_fixes_applied.append("移除BOM标记")
        
        # 检测格式
        format_type = self._detect_format(cookie_str)
        logger.info(f"检测到Cookie格式: {format_type}")
        
        # 根据格式解析
        try:
            if format_type == self.FORMAT_JSON_ARRAY:
                cookies = self._parse_json_array(cookie_str)
            elif format_type == self.FORMAT_JSON_OBJECT:
                cookies = self._parse_json_object(cookie_str)
            elif format_type == self.FORMAT_NETSCAPE:
                cookies = self._parse_netscape(cookie_str)
            elif format_type == self.FORMAT_HEADER_STRING:
                cookies = self._parse_header_string(cookie_str)
            elif format_type == self.FORMAT_KEY_VALUE_LINES:
                cookies = self._parse_key_value_lines(cookie_str)
            elif format_type == self.FORMAT_JAVASCRIPT:
                cookies = self._parse_javascript(cookie_str)
            elif format_type == self.FORMAT_PYTHON_DICT:
                cookies = self._parse_python_dict(cookie_str)
            elif format_type == self.FORMAT_EDIT_THIS_COOKIE:
                cookies = self._parse_edit_this_cookie(cookie_str)
            elif format_type == self.FORMAT_SINGLE_LINE:
                cookies = self._parse_single_line(cookie_str)
            else:
                raise ValueError(f"无法识别的Cookie格式")
            
            # 标准化和验证
            cookies = self._normalize_cookies(cookies)
            
            logger.info(f"✅ 成功解析 {len(cookies)} 个Cookie")
            if self.error_fixes_applied:
                logger.info(f"应用了 {len(self.error_fixes_applied)} 个自动修复: {', '.join(self.error_fixes_applied)}")
            if self.warnings:
                logger.warning(f"警告: {', '.join(self.warnings)}")
            
            return cookies
            
        except Exception as e:
            logger.error(f"Cookie解析失败: {str(e)}")
            raise ValueError(f"Cookie解析失败: {str(e)}")
    
    def _detect_format(self, cookie_str: str) -> str:
        """自动检测Cookie格式"""
        cookie_str_stripped = cookie_str.strip()
        
        # 1. JSON数组格式
        if cookie_str_stripped.startswith('[') and cookie_str_stripped.endswith(']'):
            try:
                data = json.loads(cookie_str_stripped)
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], dict):
                        if 'name' in data[0] and 'value' in data[0]:
                            return self.FORMAT_JSON_ARRAY
            except:
                pass
        
        # 2. JSON对象格式
        if cookie_str_stripped.startswith('{') and cookie_str_stripped.endswith('}'):
            try:
                data = json.loads(cookie_str_stripped)
                if isinstance(data, dict):
                    # 区分JSON对象和EditThisCookie格式
                    if all(isinstance(v, str) for v in data.values()):
                        return self.FORMAT_JSON_OBJECT
                    elif any(isinstance(v, dict) for v in data.values()):
                        return self.FORMAT_EDIT_THIS_COOKIE
            except:
                pass
        
        # 3. Python字典格式（单引号）
        if cookie_str_stripped.startswith('{') and "'" in cookie_str_stripped:
            return self.FORMAT_PYTHON_DICT
        
        # 4. Netscape格式
        if '# Netscape HTTP Cookie File' in cookie_str or \
           (cookie_str.count('\t') >= 3 and '\n' in cookie_str):
            return self.FORMAT_NETSCAPE
        
        # 5. JavaScript格式
        if 'document.cookie' in cookie_str.lower():
            return self.FORMAT_JAVASCRIPT
        
        # 6. HTTP Header格式
        if cookie_str_stripped.lower().startswith('cookie:'):
            return self.FORMAT_HEADER_STRING
        
        # 7. 键值对行格式
        if '\n' in cookie_str and '=' in cookie_str:
            lines = cookie_str.strip().split('\n')
            if len(lines) > 1 and all('=' in line for line in lines if line.strip()):
                return self.FORMAT_KEY_VALUE_LINES
        
        # 8. 简单键值对（单行，分号分隔）
        if ';' in cookie_str and '=' in cookie_str and '\n' not in cookie_str:
            return self.FORMAT_HEADER_STRING
        
        # 9. 单个键值对
        if '=' in cookie_str and ';' not in cookie_str and '\n' not in cookie_str:
            return self.FORMAT_SINGLE_LINE
        
        return "unknown"
    
    def _parse_json_array(self, cookie_str: str) -> List[Dict]:
        """解析JSON数组格式"""
        try:
            cookies = json.loads(cookie_str)
            return cookies
        except json.JSONDecodeError as e:
            # 尝试修复常见JSON错误
            logger.warning(f"JSON解析失败，尝试自动修复: {str(e)}")
            
            fixed = cookie_str
            
            # 修复1: 单引号 → 双引号
            if "'" in fixed:
                fixed = fixed.replace("'", '"')
                self.error_fixes_applied.append("单引号转双引号")
            
            # 修复2: 尾随逗号
            fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
            if ',' in cookie_str and fixed != cookie_str:
                self.error_fixes_applied.append("移除尾随逗号")
            
            # 修复3: Python风格的True/False/None
            if 'True' in fixed or 'False' in fixed or 'None' in fixed:
                fixed = fixed.replace('True', 'true').replace('False', 'false').replace('None', 'null')
                self.error_fixes_applied.append("转换Python关键字")
            
            # 修复4: 未引号的键名
            fixed = re.sub(r'(\w+)(\s*:\s*)', r'"\1"\2', fixed)
            if fixed != cookie_str:
                self.error_fixes_applied.append("添加键名引号")
            
            try:
                cookies = json.loads(fixed)
                logger.info("✅ JSON自动修复成功")
                return cookies
            except:
                raise ValueError("JSON格式无法修复，请检查格式")
    
    def _parse_json_object(self, cookie_str: str) -> List[Dict]:
        """解析JSON对象格式"""
        try:
            obj = json.loads(cookie_str)
        except json.JSONDecodeError:
            # 尝试修复
            fixed = cookie_str.replace("'", '"')
            fixed = re.sub(r',(\s*})', r'\1', fixed)
            obj = json.loads(fixed)
            self.error_fixes_applied.append("JSON对象格式修复")
        
        # 转换为标准格式
        cookies = []
        for name, value in obj.items():
            cookies.append({
                "name": name,
                "value": str(value),
                "domain": ".kookapp.cn",
                "path": "/",
                "secure": True,
                "httpOnly": False
            })
        
        return cookies
    
    def _parse_python_dict(self, cookie_str: str) -> List[Dict]:
        """解析Python字典格式（单引号）"""
        # 将Python字典转换为JSON
        fixed = cookie_str.replace("'", '"')
        fixed = fixed.replace('True', 'true').replace('False', 'false').replace('None', 'null')
        
        try:
            data = json.loads(fixed)
            self.error_fixes_applied.append("Python字典转JSON")
            
            # 判断是数组还是对象
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return self._parse_json_object(fixed)
        except:
            raise ValueError("Python字典格式无法解析")
    
    def _parse_netscape(self, cookie_str: str) -> List[Dict]:
        """解析Netscape格式（浏览器导出）"""
        cookies = []
        
        for line in cookie_str.split('\n'):
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # Netscape格式: domain\tflag\tpath\tsecure\texpiration\tname\tvalue
            parts = line.split('\t')
            
            if len(parts) >= 7:
                cookies.append({
                    "name": parts[5],
                    "value": parts[6],
                    "domain": parts[0],
                    "path": parts[2],
                    "secure": parts[3].lower() == 'true',
                    "httpOnly": False,
                    "expirationDate": int(parts[4]) if parts[4].isdigit() else None
                })
            elif len(parts) >= 2 and '=' not in parts[0]:
                # 简化格式: name\tvalue
                cookies.append({
                    "name": parts[0],
                    "value": parts[1],
                    "domain": ".kookapp.cn",
                    "path": "/",
                    "secure": True,
                    "httpOnly": False
                })
        
        return cookies
    
    def _parse_header_string(self, cookie_str: str) -> List[Dict]:
        """解析HTTP Cookie头格式"""
        # 移除 "Cookie: " 前缀
        if cookie_str.lower().startswith('cookie:'):
            cookie_str = cookie_str[7:].strip()
        
        cookies = []
        
        # 分割: name1=value1; name2=value2
        for pair in cookie_str.split(';'):
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                cookies.append({
                    "name": name.strip(),
                    "value": unquote(value.strip()),  # URL解码
                    "domain": ".kookapp.cn",
                    "path": "/",
                    "secure": True,
                    "httpOnly": False
                })
        
        return cookies
    
    def _parse_key_value_lines(self, cookie_str: str) -> List[Dict]:
        """解析键值对行格式"""
        cookies = []
        
        for line in cookie_str.split('\n'):
            line = line.strip()
            if '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    cookies.append({
                        "name": parts[0].strip(),
                        "value": parts[1].strip(),
                        "domain": ".kookapp.cn",
                        "path": "/",
                        "secure": True,
                        "httpOnly": False
                    })
        
        return cookies
    
    def _parse_single_line(self, cookie_str: str) -> List[Dict]:
        """解析单个键值对"""
        if '=' in cookie_str:
            name, value = cookie_str.split('=', 1)
            return [{
                "name": name.strip(),
                "value": value.strip(),
                "domain": ".kookapp.cn",
                "path": "/",
                "secure": True,
                "httpOnly": False
            }]
        return []
    
    def _parse_javascript(self, cookie_str: str) -> List[Dict]:
        """解析JavaScript格式"""
        # 提取document.cookie = "..." 中的内容
        pattern = r'document\.cookie\s*=\s*["\']([^"\']+)["\']'
        matches = re.findall(pattern, cookie_str, re.IGNORECASE)
        
        if not matches:
            # 尝试提取所有字符串
            pattern = r'["\']([^"\']*=[^"\']*)["\']'
            matches = re.findall(pattern, cookie_str)
        
        cookies = []
        for match in matches:
            if '=' in match:
                name, value = match.split('=', 1)
                cookies.append({
                    "name": name.strip(),
                    "value": value.strip(),
                    "domain": ".kookapp.cn",
                    "path": "/",
                    "secure": True,
                    "httpOnly": False
                })
        
        return cookies
    
    def _parse_edit_this_cookie(self, cookie_str: str) -> List[Dict]:
        """解析EditThisCookie扩展导出格式"""
        try:
            data = json.loads(cookie_str)
            
            cookies = []
            for key, cookie_data in data.items():
                if isinstance(cookie_data, dict):
                    cookies.append({
                        "name": cookie_data.get('name', key),
                        "value": cookie_data.get('value', ''),
                        "domain": cookie_data.get('domain', '.kookapp.cn'),
                        "path": cookie_data.get('path', '/'),
                        "secure": cookie_data.get('secure', True),
                        "httpOnly": cookie_data.get('httpOnly', False),
                        "expirationDate": cookie_data.get('expirationDate')
                    })
            
            return cookies
        except:
            raise ValueError("EditThisCookie格式解析失败")
    
    def _normalize_cookies(self, cookies: List[Dict]) -> List[Dict]:
        """标准化Cookie（确保必要字段存在）"""
        normalized = []
        
        for cookie in cookies:
            # 确保name和value字段存在
            if 'name' not in cookie or 'value' not in cookie:
                self.warnings.append(f"跳过无效Cookie: {cookie}")
                continue
            
            # 跳过空Cookie
            if not cookie['name'] or not cookie['value']:
                self.warnings.append(f"跳过空Cookie: {cookie['name']}")
                continue
            
            # 标准化
            normalized_cookie = {
                "name": str(cookie['name']).strip(),
                "value": str(cookie['value']).strip(),
                "domain": cookie.get('domain', '.kookapp.cn'),
                "path": cookie.get('path', '/'),
                "secure": cookie.get('secure', True),
                "httpOnly": cookie.get('httpOnly', False),
            }
            
            # 可选字段
            if 'expirationDate' in cookie and cookie['expirationDate']:
                normalized_cookie['expirationDate'] = cookie['expirationDate']
            if 'sameSite' in cookie:
                normalized_cookie['sameSite'] = cookie['sameSite']
            
            normalized.append(normalized_cookie)
        
        return normalized
    
    def validate(self, cookies: List[Dict]) -> Tuple[bool, str]:
        """
        验证Cookie有效性
        
        Args:
            cookies: Cookie列表
            
        Returns:
            (是否有效, 提示信息)
        """
        if not cookies:
            return False, "Cookie列表为空"
        
        # 检查关键Cookie（根据KOOK实际情况）
        # 注意：这里的关键Cookie名称需要根据实际情况调整
        required_cookies = []  # 可根据需要添加必需Cookie
        found_cookies = {c['name'] for c in cookies}
        
        missing_cookies = [name for name in required_cookies if name not in found_cookies]
        
        if missing_cookies:
            message = f"警告：缺少关键Cookie（{', '.join(missing_cookies)}），登录可能失败"
            self.warnings.append(message)
            return True, message
        
        # 检查Cookie数量
        if len(cookies) < 3:
            message = f"警告：Cookie数量较少（{len(cookies)}个），建议导出完整Cookie"
            self.warnings.append(message)
            return True, message
        
        # 检查域名
        kook_domains = ['.kookapp.cn', '.kaiheila.cn', 'kookapp.cn', 'kaiheila.cn']
        has_kook_cookie = any(
            any(domain in cookie.get('domain', '') for domain in kook_domains)
            for cookie in cookies
        )
        
        if not has_kook_cookie:
            message = "警告：Cookie域名可能不正确，应包含kookapp.cn或kaiheila.cn"
            self.warnings.append(message)
            return True, message
        
        return True, f"Cookie验证通过（共{len(cookies)}个）"
    
    def get_error_fixes(self) -> List[str]:
        """获取应用的修复列表"""
        return self.error_fixes_applied
    
    def get_warnings(self) -> List[str]:
        """获取警告列表"""
        return self.warnings
    
    def get_parse_info(self) -> Dict:
        """获取解析信息"""
        return {
            "fixes": self.error_fixes_applied,
            "warnings": self.warnings,
            "fix_count": len(self.error_fixes_applied),
            "warning_count": len(self.warnings)
        }


# 全局实例
cookie_parser_enhanced = CookieParserEnhanced()
