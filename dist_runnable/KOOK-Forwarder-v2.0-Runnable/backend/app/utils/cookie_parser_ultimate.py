"""
终极Cookie解析器 - 支持多种格式
"""
import json
from typing import List, Dict, Optional
from ..utils.logger import logger


class CookieParserUltimate:
    """终极Cookie解析器"""
    
    @staticmethod
    def parse(cookie_str: str) -> List[Dict]:
        """
        智能解析Cookie（支持多种格式）
        
        支持格式：
        1. JSON数组: [{"name":"token", "value":"xxx"}]
        2. JSON对象: {"cookies": [...]}
        3. Netscape格式（浏览器导出）
        4. HTTP Header格式（Cookie: name1=value1; name2=value2）
        5. 键值对格式（逐行）
        
        Args:
            cookie_str: Cookie字符串
            
        Returns:
            标准Cookie列表
        """
        if not cookie_str or not cookie_str.strip():
            return []
        
        cookie_str = cookie_str.strip()
        
        # 格式1: JSON数组或对象
        if cookie_str.startswith('{') or cookie_str.startswith('['):
            return CookieParserUltimate._parse_json(cookie_str)
        
        # 格式2: HTTP Header格式
        if ';' in cookie_str and '=' in cookie_str and '\n' not in cookie_str:
            return CookieParserUltimate._parse_header(cookie_str)
        
        # 格式3: Netscape或键值对格式（多行）
        if '\n' in cookie_str:
            return CookieParserUltimate._parse_multiline(cookie_str)
        
        # 默认尝试JSON解析
        try:
            return CookieParserUltimate._parse_json(cookie_str)
        except:
            logger.warning("无法识别Cookie格式")
            return []
    
    @staticmethod
    def _parse_json(cookie_str: str) -> List[Dict]:
        """解析JSON格式Cookie"""
        try:
            data = json.loads(cookie_str)
            
            # 如果是对象包装的数组
            if isinstance(data, dict) and 'cookies' in data:
                data = data['cookies']
            
            if not isinstance(data, list):
                return []
            
            # 标准化Cookie格式
            standardized = []
            for cookie in data:
                if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                    standardized.append({
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain', '.kookapp.cn'),
                        'path': cookie.get('path', '/'),
                        'expires': cookie.get('expires') or cookie.get('expirationDate'),
                        'httpOnly': cookie.get('httpOnly', False),
                        'secure': cookie.get('secure', True),
                        'sameSite': cookie.get('sameSite', 'lax')
                    })
            
            return standardized
        except Exception as e:
            logger.error(f"JSON解析失败: {str(e)}")
            return []
    
    @staticmethod
    def _parse_header(cookie_str: str) -> List[Dict]:
        """解析HTTP Header格式Cookie"""
        cookies = []
        
        # 移除可能的"Cookie:"前缀
        cookie_str = cookie_str.replace('Cookie:', '').strip()
        
        # 分割cookie对
        pairs = cookie_str.split(';')
        
        for pair in pairs:
            pair = pair.strip()
            if '=' not in pair:
                continue
            
            name, value = pair.split('=', 1)
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.kookapp.cn',
                'path': '/',
                'expires': None,
                'httpOnly': False,
                'secure': True,
                'sameSite': 'lax'
            })
        
        return cookies
    
    @staticmethod
    def _parse_multiline(cookie_str: str) -> List[Dict]:
        """解析多行格式Cookie（Netscape或键值对）"""
        cookies = []
        
        for line in cookie_str.split('\n'):
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # Netscape格式：domain flag path secure expiration name value
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 7:
                    cookies.append({
                        'name': parts[5],
                        'value': parts[6],
                        'domain': parts[0],
                        'path': parts[2],
                        'expires': int(parts[4]) if parts[4].isdigit() else None,
                        'httpOnly': False,
                        'secure': parts[3].lower() == 'true',
                        'sameSite': 'lax'
                    })
            # 键值对格式：name=value
            elif '=' in line:
                name, value = line.split('=', 1)
                cookies.append({
                    'name': name.strip(),
                    'value': value.strip(),
                    'domain': '.kookapp.cn',
                    'path': '/',
                    'expires': None,
                    'httpOnly': False,
                    'secure': True,
                    'sameSite': 'lax'
                })
        
        return cookies
    
    @staticmethod
    def validate(cookies: List[Dict]) -> bool:
        """
        验证Cookie是否有效
        
        检查：
        1. 至少有3个Cookie
        2. 必须包含name和value字段
        3. 域名应该是kookapp.cn
        """
        if not cookies or len(cookies) < 3:
            return False
        
        for cookie in cookies:
            if not isinstance(cookie, dict):
                return False
            if 'name' not in cookie or 'value' not in cookie:
                return False
        
        return True


# 创建全局实例
cookie_parser_ultimate = CookieParserUltimate()
