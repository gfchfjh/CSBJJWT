"""
Cookie解析器
支持多种Cookie格式的自动识别和转换
v1.12.0+ 新增：支持JSON、Netscape、键值对等多种格式
"""
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..utils.logger import logger


class CookieParser:
    """Cookie格式解析器"""
    
    @staticmethod
    def parse(cookie_input: str) -> List[Dict[str, Any]]:
        """
        自动识别Cookie格式并解析
        
        支持格式:
        1. JSON数组格式: [{"name": "token", "value": "abc", ...}, ...]
        2. Netscape格式: # Netscape HTTP Cookie File\n.domain.com\tTRUE\t/\t...
        3. 键值对格式: token=abc; session=xyz; ...
        4. 浏览器开发者工具格式: name=value; name2=value2
        
        Args:
            cookie_input: Cookie字符串
            
        Returns:
            标准化的Cookie列表 [{"name": "...", "value": "...", "domain": "..."}]
            
        Raises:
            ValueError: 无法识别的Cookie格式
        """
        cookie_input = cookie_input.strip()
        
        if not cookie_input:
            raise ValueError("Cookie内容为空")
        
        # 尝试各种格式解析
        parsers = [
            CookieParser._parse_json,
            CookieParser._parse_netscape,
            CookieParser._parse_key_value,
            CookieParser._parse_browser_devtools,
        ]
        
        for parser in parsers:
            try:
                result = parser(cookie_input)
                if result:
                    logger.info(f"✅ Cookie解析成功，使用格式: {parser.__name__}, 共{len(result)}条")
                    return result
            except Exception as e:
                logger.debug(f"尝试{parser.__name__}失败: {str(e)}")
                continue
        
        # 所有格式都失败
        raise ValueError(
            "无法识别的Cookie格式。支持格式:\n"
            "1. JSON数组: [{\"name\": \"token\", \"value\": \"abc\", ...}]\n"
            "2. Netscape格式: # Netscape HTTP Cookie File\\n.domain.com\\t...\n"
            "3. 键值对格式: token=abc; session=xyz\n"
            "4. 开发者工具格式: name=value; name2=value2"
        )
    
    @staticmethod
    def _parse_json(cookie_input: str) -> Optional[List[Dict[str, Any]]]:
        """
        解析JSON格式Cookie
        
        格式示例:
        [
            {
                "name": "token",
                "value": "abc123",
                "domain": ".kookapp.cn",
                "path": "/",
                "expires": 1234567890,
                "httpOnly": true,
                "secure": true,
                "sameSite": "Lax"
            }
        ]
        """
        # 尝试解析JSON
        try:
            data = json.loads(cookie_input)
        except json.JSONDecodeError:
            return None
        
        # 检查是否为列表
        if not isinstance(data, list):
            return None
        
        # 检查是否为空
        if len(data) == 0:
            return None
        
        # 验证每个Cookie对象
        cookies = []
        for i, cookie in enumerate(data):
            if not isinstance(cookie, dict):
                raise ValueError(f"Cookie[{i}]必须是字典格式")
            
            # 必需字段
            if 'name' not in cookie:
                raise ValueError(f"Cookie[{i}]缺少name字段")
            if 'value' not in cookie:
                raise ValueError(f"Cookie[{i}]缺少value字段")
            
            # 标准化Cookie对象
            standardized = {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie.get('domain', '.kookapp.cn'),
                'path': cookie.get('path', '/'),
            }
            
            # 可选字段
            if 'expires' in cookie:
                standardized['expires'] = cookie['expires']
            if 'httpOnly' in cookie:
                standardized['httpOnly'] = cookie['httpOnly']
            if 'secure' in cookie:
                standardized['secure'] = cookie['secure']
            if 'sameSite' in cookie:
                standardized['sameSite'] = cookie['sameSite']
            
            cookies.append(standardized)
        
        return cookies
    
    @staticmethod
    def _parse_netscape(cookie_input: str) -> Optional[List[Dict[str, Any]]]:
        """
        解析Netscape格式Cookie
        
        格式示例:
        # Netscape HTTP Cookie File
        # This is a generated file! Do not edit.
        .kookapp.cn	TRUE	/	FALSE	1234567890	token	abc123
        .kookapp.cn	TRUE	/	TRUE	1234567890	session	xyz789
        
        字段说明:
        domain	includeSubdomains	path	secure	expires	name	value
        """
        # 检查是否为Netscape格式
        if '# Netscape' not in cookie_input and '\t' not in cookie_input:
            return None
        
        cookies = []
        lines = cookie_input.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # 分割字段（制表符分隔）
            parts = line.split('\t')
            
            # Netscape格式应该有7个字段
            if len(parts) < 7:
                logger.debug(f"Netscape格式行字段不足7个，跳过: {line}")
                continue
            
            try:
                domain = parts[0]
                # includeSubdomains = parts[1] == 'TRUE'
                path = parts[2]
                secure = parts[3] == 'TRUE'
                expires = int(parts[4]) if parts[4] != '0' else None
                name = parts[5]
                value = parts[6]
                
                cookie = {
                    'name': name,
                    'value': value,
                    'domain': domain,
                    'path': path,
                    'secure': secure,
                }
                
                if expires:
                    cookie['expires'] = expires
                
                cookies.append(cookie)
                
            except (ValueError, IndexError) as e:
                logger.warning(f"解析Netscape Cookie失败: {line}, 错误: {str(e)}")
                continue
        
        return cookies if cookies else None
    
    @staticmethod
    def _parse_key_value(cookie_input: str) -> Optional[List[Dict[str, Any]]]:
        """
        解析键值对格式Cookie
        
        格式示例:
        token=abc123; session=xyz789; user_id=12345
        
        或者:
        token=abc123
        session=xyz789
        user_id=12345
        """
        # 检查是否包含键值对
        if '=' not in cookie_input:
            return None
        
        cookies = []
        
        # 尝试分号分隔
        if ';' in cookie_input:
            pairs = cookie_input.split(';')
        # 尝试换行分隔
        elif '\n' in cookie_input:
            pairs = cookie_input.split('\n')
        # 单个键值对
        else:
            pairs = [cookie_input]
        
        for pair in pairs:
            pair = pair.strip()
            
            if not pair or '=' not in pair:
                continue
            
            # 分割键值（只分割第一个=）
            parts = pair.split('=', 1)
            if len(parts) != 2:
                continue
            
            name = parts[0].strip()
            value = parts[1].strip()
            
            # 移除可能的引号
            value = value.strip('"\'')
            
            if name and value:
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.kookapp.cn',
                    'path': '/',
                })
        
        return cookies if cookies else None
    
    @staticmethod
    def _parse_browser_devtools(cookie_input: str) -> Optional[List[Dict[str, Any]]]:
        """
        解析浏览器开发者工具格式
        
        格式示例（从浏览器Application/Storage/Cookies复制）:
        name1	value1	.kookapp.cn	/	2025-12-31T23:59:59.000Z	73	✓	✓	Lax
        name2	value2	.kookapp.cn	/	2025-12-31T23:59:59.000Z	73	✓	✓	Lax
        
        或者简化格式:
        name	value	domain	path
        """
        # 检查是否为制表符分隔的格式
        if '\t' not in cookie_input:
            return None
        
        # 已经被Netscape格式处理了，这里处理非Netscape的制表符格式
        if '# Netscape' in cookie_input:
            return None
        
        cookies = []
        lines = cookie_input.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            parts = line.split('\t')
            
            # 至少需要2个字段（name和value）
            if len(parts) < 2:
                continue
            
            try:
                name = parts[0].strip()
                value = parts[1].strip()
                domain = parts[2].strip() if len(parts) > 2 else '.kookapp.cn'
                path = parts[3].strip() if len(parts) > 3 else '/'
                
                # 解析过期时间（如果有）
                expires = None
                if len(parts) > 4:
                    expires_str = parts[4].strip()
                    # 尝试解析ISO格式时间
                    try:
                        if 'T' in expires_str:
                            dt = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                            expires = int(dt.timestamp())
                    except:
                        pass
                
                cookie = {
                    'name': name,
                    'value': value,
                    'domain': domain,
                    'path': path,
                }
                
                if expires:
                    cookie['expires'] = expires
                
                # 解析httpOnly和secure（如果有）
                if len(parts) > 6:
                    cookie['httpOnly'] = parts[6].strip() == '✓'
                if len(parts) > 7:
                    cookie['secure'] = parts[7].strip() == '✓'
                if len(parts) > 8:
                    cookie['sameSite'] = parts[8].strip()
                
                cookies.append(cookie)
                
            except (ValueError, IndexError) as e:
                logger.warning(f"解析开发者工具Cookie失败: {line}, 错误: {str(e)}")
                continue
        
        return cookies if cookies else None
    
    @staticmethod
    def validate(cookies: List[Dict[str, Any]]) -> bool:
        """
        验证Cookie列表是否有效
        
        Args:
            cookies: Cookie列表
            
        Returns:
            是否有效
        """
        if not isinstance(cookies, list):
            logger.error("Cookie必须是列表格式")
            return False
        
        if len(cookies) == 0:
            logger.error("Cookie列表不能为空")
            return False
        
        for i, cookie in enumerate(cookies):
            if not isinstance(cookie, dict):
                logger.error(f"Cookie[{i}]必须是字典格式")
                return False
            
            if 'name' not in cookie:
                logger.error(f"Cookie[{i}]缺少name字段")
                return False
            
            if 'value' not in cookie:
                logger.error(f"Cookie[{i}]缺少value字段")
                return False
        
        logger.info(f"✅ Cookie验证通过，共{len(cookies)}条")
        return True
    
    @staticmethod
    def to_json(cookies: List[Dict[str, Any]]) -> str:
        """
        将Cookie列表转换为JSON字符串
        
        Args:
            cookies: Cookie列表
            
        Returns:
            JSON字符串
        """
        return json.dumps(cookies, ensure_ascii=False, indent=2)


# 创建全局实例
cookie_parser = CookieParser()
