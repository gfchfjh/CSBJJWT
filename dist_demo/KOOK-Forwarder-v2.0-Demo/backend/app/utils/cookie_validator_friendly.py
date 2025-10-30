"""
友好的Cookie验证器
✅ P0-3优化：提供用户可理解的错误提示和修复建议
"""
import json
import re
import time
from typing import Dict, List, Optional, Tuple
from ..utils.logger import logger


class FriendlyCookieValidator:
    """友好的Cookie验证器"""
    
    # 必需的Cookie字段
    REQUIRED_FIELDS = ['name', 'value', 'domain']
    
    # KOOK的关键Cookie名称
    KOOK_COOKIE_NAMES = ['token', 'auth', 'session', 'user']
    
    # 常见错误模式
    ERROR_PATTERNS = {
        'console_output': r'(console|document\.cookie|>|;$)',
        'html_content': r'<[^>]+>',
        'javascript_code': r'(function|var|const|let)\s+',
        'incomplete_json': r'^\[.*[^}\]]$',
    }
    
    def validate_and_explain(self, cookie_str: str) -> Dict:
        """
        验证Cookie并返回友好的错误说明
        
        Returns:
            {
                "valid": bool,
                "error": str,           # 错误描述（用户友好）
                "suggestion": str,      # 修复建议
                "tutorial_link": str,   # 教程链接
                "details": str,         # 技术细节（可选）
                "auto_fixable": bool    # 是否可以自动修复
            }
        """
        # 检查1：空字符串
        if not cookie_str or not cookie_str.strip():
            return {
                "valid": False,
                "error": "Cookie内容为空",
                "suggestion": "请确保已复制Cookie内容。如果不知道如何获取Cookie，请查看教程。",
                "tutorial_link": "/help/cookie-export",
                "auto_fixable": False
            }
        
        # 检查2：检测控制台输出
        if self._contains_console_output(cookie_str):
            return {
                "valid": False,
                "error": "检测到您粘贴了浏览器控制台的内容",
                "suggestion": "请仅粘贴Cookie值，不要包含 'document.cookie=' 等代码。推荐使用Chrome扩展一键导出。",
                "tutorial_link": "/help/cookie-export",
                "auto_fixable": True,
                "fix_method": "strip_console_output"
            }
        
        # 检查3：检测HTML内容
        if self._contains_html(cookie_str):
            return {
                "valid": False,
                "error": "检测到HTML标签，这不是有效的Cookie格式",
                "suggestion": "您可能复制了网页内容。请打开浏览器开发者工具，从Application标签页导出Cookie。",
                "tutorial_link": "/help/cookie-export-devtools",
                "auto_fixable": False
            }
        
        # 检查4：检测JavaScript代码
        if self._contains_javascript(cookie_str):
            return {
                "valid": False,
                "error": "检测到JavaScript代码",
                "suggestion": "请不要粘贴JavaScript代码。如果您从控制台复制，请只复制Cookie值部分。",
                "tutorial_link": "/help/cookie-export",
                "auto_fixable": True,
                "fix_method": "strip_javascript"
            }
        
        # 检查5：尝试解析JSON
        cookies_list = self._parse_cookie_string(cookie_str)
        if cookies_list is None:
            return {
                "valid": False,
                "error": "Cookie格式不正确",
                "suggestion": "Cookie应该是有效的JSON数组格式。推荐使用Chrome扩展一键导出，可以避免格式错误。",
                "tutorial_link": "/help/cookie-export",
                "details": "JSON解析失败，请检查括号、引号是否完整匹配",
                "auto_fixable": False
            }
        
        # 检查6：检查是否为空数组
        if not cookies_list:
            return {
                "valid": False,
                "error": "Cookie列表为空",
                "suggestion": "请确保已登录KOOK，然后再导出Cookie。",
                "tutorial_link": "/help/cookie-export",
                "auto_fixable": False
            }
        
        # 检查7：检查必需字段
        missing_fields_result = self._check_required_fields(cookies_list)
        if not missing_fields_result["valid"]:
            return missing_fields_result
        
        # 检查8：检查域名
        domain_result = self._check_domains(cookies_list)
        if not domain_result["valid"]:
            return domain_result
        
        # 检查9：检查是否包含KOOK关键Cookie
        key_cookies_result = self._check_key_cookies(cookies_list)
        if not key_cookies_result["valid"]:
            return key_cookies_result
        
        # 检查10：检查Cookie是否过期
        expiry_result = self._check_expiry(cookies_list)
        if not expiry_result["valid"]:
            return expiry_result
        
        # 所有检查通过
        return {
            "valid": True,
            "message": f"Cookie验证通过，共{len(cookies_list)}条",
            "cookie_count": len(cookies_list)
        }
    
    def _contains_console_output(self, text: str) -> bool:
        """检测是否包含控制台输出"""
        pattern = self.ERROR_PATTERNS['console_output']
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _contains_html(self, text: str) -> bool:
        """检测是否包含HTML标签"""
        pattern = self.ERROR_PATTERNS['html_content']
        return bool(re.search(pattern, text))
    
    def _contains_javascript(self, text: str) -> bool:
        """检测是否包含JavaScript代码"""
        pattern = self.ERROR_PATTERNS['javascript_code']
        return bool(re.search(pattern, text))
    
    def _parse_cookie_string(self, cookie_str: str) -> Optional[List[Dict]]:
        """
        尝试解析Cookie字符串
        
        支持格式：
        1. JSON数组：[{...}, {...}]
        2. 单个JSON对象：{...}（自动转换为数组）
        3. Netscape格式：name=value; domain=...（自动转换为JSON）
        """
        try:
            # 尝试解析为JSON
            data = json.loads(cookie_str.strip())
            
            # 如果是单个对象，转换为数组
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                return None
                
        except json.JSONDecodeError as e:
            logger.debug(f"JSON解析失败: {str(e)}")
            
            # 尝试解析Netscape格式
            try:
                cookies = self._parse_netscape_format(cookie_str)
                if cookies:
                    return cookies
            except Exception as parse_error:
                logger.debug(f"Netscape格式解析失败: {str(parse_error)}")
            
            return None
    
    def _parse_netscape_format(self, cookie_str: str) -> Optional[List[Dict]]:
        """
        解析Netscape Cookie格式
        
        格式示例：
        name1=value1; domain=.kookapp.cn; path=/
        name2=value2; domain=.kookapp.cn; path=/
        """
        cookies = []
        
        for line in cookie_str.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(';')
            if not parts:
                continue
            
            # 解析第一部分（name=value）
            first_part = parts[0].strip()
            if '=' not in first_part:
                continue
            
            name, value = first_part.split('=', 1)
            
            cookie = {
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.kookapp.cn',
                'path': '/'
            }
            
            # 解析其他属性
            for part in parts[1:]:
                if '=' in part:
                    key, val = part.split('=', 1)
                    key = key.strip().lower()
                    val = val.strip()
                    
                    if key == 'domain':
                        cookie['domain'] = val
                    elif key == 'path':
                        cookie['path'] = val
                    elif key == 'expires':
                        # 尝试解析过期时间
                        try:
                            import datetime
                            expires_dt = datetime.datetime.strptime(val, '%a, %d-%b-%Y %H:%M:%S GMT')
                            cookie['expirationDate'] = expires_dt.timestamp()
                        except:
                            pass
            
            cookies.append(cookie)
        
        return cookies if cookies else None
    
    def _check_required_fields(self, cookies: List[Dict]) -> Dict:
        """检查必需字段"""
        for i, cookie in enumerate(cookies):
            missing = [field for field in self.REQUIRED_FIELDS if field not in cookie]
            if missing:
                return {
                    "valid": False,
                    "error": f"第{i+1}个Cookie缺少必需字段",
                    "suggestion": f"缺少的字段：{', '.join(missing)}。请使用浏览器开发者工具或Chrome扩展导出完整的Cookie。",
                    "tutorial_link": "/help/cookie-export-complete",
                    "details": f"Cookie对象必须包含：{', '.join(self.REQUIRED_FIELDS)}",
                    "auto_fixable": False
                }
        
        return {"valid": True}
    
    def _check_domains(self, cookies: List[Dict]) -> Dict:
        """检查域名是否正确"""
        valid_domains = ['.kookapp.cn', 'kookapp.cn', '.kaiheila.cn', 'kaiheila.cn', 'www.kookapp.cn']
        
        kook_cookies = [c for c in cookies if any(domain in c.get('domain', '') for domain in valid_domains)]
        
        if not kook_cookies:
            return {
                "valid": False,
                "error": "Cookie中没有找到KOOK相关的域名",
                "suggestion": "请确保您从KOOK网站（www.kookapp.cn）导出的Cookie。如果从其他网站导出，将无法使用。",
                "tutorial_link": "/help/cookie-export",
                "details": f"有效的域名：{', '.join(valid_domains)}",
                "auto_fixable": False
            }
        
        return {"valid": True}
    
    def _check_key_cookies(self, cookies: List[Dict]) -> Dict:
        """检查是否包含关键Cookie"""
        cookie_names = [c.get('name', '').lower() for c in cookies]
        
        # 检查是否包含至少一个关键Cookie
        has_key_cookie = any(
            any(key in name for key in self.KOOK_COOKIE_NAMES)
            for name in cookie_names
        )
        
        if not has_key_cookie:
            return {
                "valid": False,
                "error": "Cookie中缺少KOOK认证信息",
                "suggestion": "您导出的Cookie可能不完整，缺少认证相关的Cookie。请确保已登录KOOK，然后重新导出。",
                "tutorial_link": "/help/cookie-export",
                "details": f"需要包含以下之一：{', '.join(self.KOOK_COOKIE_NAMES)}",
                "auto_fixable": False
            }
        
        return {"valid": True}
    
    def _check_expiry(self, cookies: List[Dict]) -> Dict:
        """检查Cookie是否过期"""
        now = time.time()
        expired_cookies = []
        
        for cookie in cookies:
            if 'expirationDate' in cookie:
                expiry = cookie['expirationDate']
                if expiry < now:
                    expired_cookies.append(cookie.get('name', 'Unknown'))
        
        if expired_cookies:
            return {
                "valid": False,
                "error": f"{len(expired_cookies)}个Cookie已过期",
                "suggestion": "Cookie已过期，请重新登录KOOK并导出新的Cookie。",
                "tutorial_link": "/help/cookie-refresh",
                "details": f"过期的Cookie：{', '.join(expired_cookies)}",
                "auto_fixable": False
            }
        
        return {"valid": True}
    
    def auto_fix(self, cookie_str: str, fix_method: str) -> Optional[str]:
        """
        尝试自动修复Cookie格式
        
        Args:
            cookie_str: 原始Cookie字符串
            fix_method: 修复方法
            
        Returns:
            修复后的Cookie字符串，失败返回None
        """
        try:
            if fix_method == "strip_console_output":
                # 移除控制台输出特征
                fixed = cookie_str
                fixed = re.sub(r'^.*?document\.cookie\s*=\s*', '', fixed, flags=re.IGNORECASE)
                fixed = re.sub(r'^.*?>\s*', '', fixed)
                fixed = fixed.strip(';').strip()
                return fixed
            
            elif fix_method == "strip_javascript":
                # 移除JavaScript代码
                fixed = cookie_str
                fixed = re.sub(r'^.*?(function|var|const|let)\s+.*?[{;]\s*', '', fixed, flags=re.IGNORECASE)
                fixed = fixed.strip()
                return fixed
            
            else:
                return None
                
        except Exception as e:
            logger.error(f"自动修复失败: {str(e)}")
            return None


# 创建全局实例
friendly_cookie_validator = FriendlyCookieValidator()
