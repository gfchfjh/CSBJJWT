"""
Cookie解析器终极版 - 支持自动格式识别
✅ P0-4优化: 支持JSON、Netscape、Header多种格式
"""
import json
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..utils.logger import logger


class CookieParserUltimate:
    """Cookie解析器终极版"""
    
    # Cookie格式检测规则
    FORMATS = {
        'json_array': {
            'detect': lambda s: s.strip().startswith('[') and '"name"' in s and '"value"' in s,
            'priority': 1
        },
        'json_object': {
            'detect': lambda s: s.strip().startswith('{') and ('"cookies"' in s or '"name"' in s),
            'priority': 2
        },
        'netscape': {
            'detect': lambda s: '# Netscape HTTP Cookie File' in s or ('\t' in s and len(s.split('\n')) > 1),
            'priority': 3
        },
        'header': {
            'detect': lambda s: ('Cookie:' in s or ('=' in s and ';' in s)) and not s.strip().startswith('{') and not s.strip().startswith('['),
            'priority': 4
        },
        'key_value_lines': {
            'detect': lambda s: '\n' in s and '=' in s and not '\t' in s,
            'priority': 5
        }
    }
    
    # KOOK必需的Cookie字段
    REQUIRED_COOKIES = ['token', '_ga', '_gid']
    
    # KOOK合法域名
    VALID_DOMAINS = ['.kookapp.cn', 'www.kookapp.cn', 'kookapp.cn']
    
    def auto_detect_format(self, content: str) -> Optional[str]:
        """
        自动检测Cookie格式
        
        Args:
            content: Cookie内容
            
        Returns:
            格式名称，无法识别返回None
        """
        content = content.strip()
        
        if not content:
            return None
        
        # 按优先级检测
        detected_formats = []
        for format_name, config in self.FORMATS.items():
            if config['detect'](content):
                detected_formats.append((format_name, config['priority']))
        
        if not detected_formats:
            return None
        
        # 返回优先级最高的格式
        detected_formats.sort(key=lambda x: x[1])
        return detected_formats[0][0]
    
    def parse(self, content: str) -> List[Dict]:
        """
        统一解析接口 - 自动识别格式并解析
        
        Args:
            content: Cookie内容
            
        Returns:
            Cookie列表（标准格式）
            
        Raises:
            ValueError: 无法识别格式或解析失败
        """
        format_name = self.auto_detect_format(content)
        
        if not format_name:
            raise ValueError("无法识别Cookie格式，请检查输入内容")
        
        logger.info(f"检测到Cookie格式: {format_name}")
        
        # 根据格式调用对应的解析方法
        parser_method = getattr(self, f'parse_{format_name}', None)
        if not parser_method:
            raise ValueError(f"不支持的格式: {format_name}")
        
        cookies = parser_method(content)
        
        # 验证解析结果
        if not cookies:
            raise ValueError("解析失败：未能提取到任何Cookie")
        
        logger.info(f"成功解析 {len(cookies)} 个Cookie")
        return cookies
    
    def parse_json_array(self, content: str) -> List[Dict]:
        """
        解析JSON数组格式
        
        格式示例:
        [
            {"name": "token", "value": "xxx", "domain": ".kookapp.cn"},
            {"name": "_ga", "value": "xxx", "domain": ".kookapp.cn"}
        ]
        """
        try:
            data = json.loads(content)
            
            if not isinstance(data, list):
                raise ValueError("JSON数组格式错误")
            
            cookies = []
            for item in data:
                if isinstance(item, dict) and 'name' in item and 'value' in item:
                    cookie = {
                        'name': item['name'],
                        'value': item['value'],
                        'domain': item.get('domain', '.kookapp.cn'),
                        'path': item.get('path', '/'),
                        'secure': item.get('secure', True),
                        'httpOnly': item.get('httpOnly', False)
                    }
                    
                    # 处理过期时间
                    if 'expirationDate' in item:
                        cookie['expirationDate'] = item['expirationDate']
                    elif 'expires' in item:
                        cookie['expirationDate'] = self._parse_expiry(item['expires'])
                    
                    cookies.append(cookie)
            
            return cookies
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {str(e)}")
    
    def parse_json_object(self, content: str) -> List[Dict]:
        """
        解析JSON对象格式
        
        格式示例:
        {
            "cookies": [...],
            ...
        }
        或
        {
            "name": "token",
            "value": "xxx",
            ...
        }
        """
        try:
            data = json.loads(content)
            
            # 情况1: 包含cookies数组
            if 'cookies' in data and isinstance(data['cookies'], list):
                return self.parse_json_array(json.dumps(data['cookies']))
            
            # 情况2: 单个Cookie对象
            elif 'name' in data and 'value' in data:
                return self.parse_json_array(json.dumps([data]))
            
            else:
                raise ValueError("JSON对象格式不符合预期")
                
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {str(e)}")
    
    def parse_netscape(self, content: str) -> List[Dict]:
        """
        解析Netscape格式
        
        格式示例:
        # Netscape HTTP Cookie File
        .kookapp.cn	TRUE	/	TRUE	1234567890	token	xxx
        .kookapp.cn	TRUE	/	FALSE	1234567890	_ga	xxx
        """
        cookies = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # 分割字段（制表符分隔）
            parts = line.split('\t')
            
            # Netscape格式应该有7个字段
            if len(parts) >= 7:
                cookie = {
                    'name': parts[5],
                    'value': parts[6],
                    'domain': parts[0],
                    'path': parts[2],
                    'secure': parts[3] == 'TRUE',
                    'httpOnly': False
                }
                
                # 解析过期时间
                try:
                    expiry_timestamp = int(parts[4])
                    cookie['expirationDate'] = expiry_timestamp
                except ValueError:
                    pass
                
                cookies.append(cookie)
            
            # 兼容某些变体（少于7个字段）
            elif len(parts) >= 2:
                cookie = {
                    'name': parts[0],
                    'value': parts[1],
                    'domain': '.kookapp.cn',
                    'path': '/',
                    'secure': True,
                    'httpOnly': False
                }
                cookies.append(cookie)
        
        return cookies
    
    def parse_header(self, content: str) -> List[Dict]:
        """
        解析HTTP Header格式
        
        格式示例:
        Cookie: token=xxx; _ga=xxx; _gid=xxx
        或
        token=xxx; _ga=xxx; _gid=xxx
        """
        # 去除 "Cookie:" 前缀
        if content.startswith('Cookie:'):
            content = content[7:].strip()
        
        cookies = []
        
        # 分割Cookie对
        pairs = content.split(';')
        
        for pair in pairs:
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                cookie = {
                    'name': name.strip(),
                    'value': value.strip(),
                    'domain': '.kookapp.cn',
                    'path': '/',
                    'secure': True,
                    'httpOnly': False
                }
                cookies.append(cookie)
        
        return cookies
    
    def parse_key_value_lines(self, content: str) -> List[Dict]:
        """
        解析键值对行格式
        
        格式示例:
        token=xxx
        _ga=xxx
        _gid=xxx
        """
        cookies = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and '=' in line:
                name, value = line.split('=', 1)
                cookie = {
                    'name': name.strip(),
                    'value': value.strip(),
                    'domain': '.kookapp.cn',
                    'path': '/',
                    'secure': True,
                    'httpOnly': False
                }
                cookies.append(cookie)
        
        return cookies
    
    def validate(self, cookies: List[Dict]) -> tuple[bool, str]:
        """
        验证Cookie的有效性
        
        Args:
            cookies: Cookie列表
            
        Returns:
            (是否有效, 错误信息)
        """
        if not cookies:
            return False, "Cookie列表为空"
        
        # 检查域名
        valid_domain_found = False
        for cookie in cookies:
            domain = cookie.get('domain', '')
            if any(valid_domain in domain for valid_domain in self.VALID_DOMAINS):
                valid_domain_found = True
                break
        
        if not valid_domain_found:
            return False, f"Cookie域名不正确，必须包含: {', '.join(self.VALID_DOMAINS)}"
        
        # 检查必需字段
        cookie_names = [c['name'] for c in cookies]
        missing_required = []
        for required in self.REQUIRED_COOKIES:
            if required not in cookie_names:
                missing_required.append(required)
        
        if missing_required:
            return False, f"缺少必需的Cookie字段: {', '.join(missing_required)}"
        
        # 检查过期时间
        now = datetime.now().timestamp()
        expired_cookies = []
        for cookie in cookies:
            if 'expirationDate' in cookie:
                expiry = cookie['expirationDate']
                if isinstance(expiry, (int, float)) and expiry < now:
                    expired_cookies.append(cookie['name'])
        
        if expired_cookies:
            return False, f"以下Cookie已过期: {', '.join(expired_cookies)}"
        
        return True, "验证通过"
    
    def get_expiry_info(self, cookies: List[Dict]) -> Dict:
        """
        获取Cookie过期信息
        
        Returns:
            {
                'min_expiry_days': 最短过期天数,
                'expires_soon': 是否即将过期（<7天）,
                'details': 详细信息
            }
        """
        now = datetime.now().timestamp()
        min_expiry = None
        
        for cookie in cookies:
            if 'expirationDate' in cookie:
                expiry = cookie['expirationDate']
                if isinstance(expiry, (int, float)):
                    days_left = (expiry - now) / 86400
                    if min_expiry is None or days_left < min_expiry:
                        min_expiry = days_left
        
        if min_expiry is None:
            return {
                'min_expiry_days': None,
                'expires_soon': False,
                'details': '未设置过期时间（会话Cookie）'
            }
        
        return {
            'min_expiry_days': int(min_expiry),
            'expires_soon': min_expiry < 7,
            'details': f"最短剩余 {int(min_expiry)} 天"
        }
    
    def _parse_expiry(self, expiry_str: str) -> Optional[int]:
        """解析各种格式的过期时间"""
        try:
            # 尝试直接转为时间戳
            return int(float(expiry_str))
        except ValueError:
            pass
        
        # 尝试解析日期字符串
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(expiry_str, fmt)
                return int(dt.timestamp())
            except ValueError:
                continue
        
        return None


# 全局实例
cookie_parser_ultimate = CookieParserUltimate()
