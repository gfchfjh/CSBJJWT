"""
Cookie智能验证器（✅ P0-2优化：10种错误类型+自动修复）
"""
import json
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from ..utils.logger import logger


class CookieErrorType(Enum):
    """Cookie错误类型"""
    MISSING_REQUIRED_FIELD = "missing_required_field"      # 缺少必需字段
    INVALID_JSON_FORMAT = "invalid_json_format"            # JSON格式错误
    EXPIRED_COOKIE = "expired_cookie"                      # Cookie已过期
    DOMAIN_MISMATCH = "domain_mismatch"                    # 域名不匹配
    ENCODING_ERROR = "encoding_error"                      # 编码错误
    EMPTY_COOKIE = "empty_cookie"                          # Cookie内容为空
    INCOMPLETE_FIELDS = "incomplete_fields"                # 字段不完整
    INVALID_TIMESTAMP = "invalid_timestamp"                # 时间戳格式错误
    DUPLICATE_COOKIES = "duplicate_cookies"                # 存在重复Cookie
    INVALID_PATH = "invalid_path"                          # 路径格式错误


class CookieValidatorEnhanced:
    """
    Cookie智能验证器
    
    功能：
    1. 10种错误类型识别
    2. 自动修复逻辑
    3. 友好错误提示
    4. 修复建议
    """
    
    # 必需的Cookie字段
    REQUIRED_FIELDS = ['domain', 'name', 'value']
    
    # 可选字段及其默认值
    OPTIONAL_FIELDS = {
        'path': '/',
        'secure': True,
        'httpOnly': False,
        'sameSite': 'Lax'
    }
    
    # KOOK有效域名
    VALID_DOMAINS = [
        'kookapp.cn',
        'www.kookapp.cn',
        '.kookapp.cn',
        'kaiheila.cn',
        'www.kaiheila.cn',
        '.kaiheila.cn'
    ]
    
    # 关键Cookie名称（KOOK特有）
    KOOK_COOKIE_NAMES = [
        'token',
        'kook_token',
        'session',
        'user_id',
        'auth_token'
    ]
    
    @staticmethod
    def validate_and_fix(cookie_data: str) -> Dict[str, Any]:
        """
        验证Cookie并自动修复
        
        Args:
            cookie_data: Cookie字符串（可能是JSON、文本等格式）
            
        Returns:
            {
                "valid": bool,              # 是否有效
                "cookies": List[Dict],      # 修复后的Cookie列表
                "errors": List[Dict],       # 错误列表
                "auto_fixed": bool,         # 是否自动修复
                "warnings": List[str],      # 警告信息
                "suggestions": List[str]    # 修复建议
            }
        """
        result = {
            "valid": False,
            "cookies": [],
            "errors": [],
            "auto_fixed": False,
            "warnings": [],
            "suggestions": []
        }
        
        # 1. 检查空Cookie
        if not cookie_data or cookie_data.strip() == '':
            result["errors"].append({
                "type": CookieErrorType.EMPTY_COOKIE.value,
                "message": "🔴 Cookie内容为空",
                "description": "您还没有粘贴任何Cookie内容",
                "solution": "请从浏览器中复制完整的Cookie内容并粘贴"
            })
            result["suggestions"].append("💡 提示：Cookie通常是一个JSON数组或多行文本")
            return result
        
        # 2. 检查编码错误
        try:
            # 尝试转换为UTF-8
            if isinstance(cookie_data, bytes):
                cookie_data = cookie_data.decode('utf-8')
        except UnicodeDecodeError:
            result["errors"].append({
                "type": CookieErrorType.ENCODING_ERROR.value,
                "message": "🔴 Cookie编码错误",
                "description": "Cookie内容包含无法识别的字符",
                "solution": "请确保Cookie是UTF-8编码格式"
            })
            result["suggestions"].append("💡 提示：请重新从浏览器复制Cookie")
            return result
        
        # 3. 尝试解析Cookie
        cookies, parse_errors = CookieValidatorEnhanced._parse_cookie(cookie_data)
        
        if parse_errors:
            result["errors"].extend(parse_errors)
            
            # 如果完全解析失败，返回
            if not cookies:
                return result
        
        # 4. 验证和修复每个Cookie
        fixed_cookies = []
        for i, cookie in enumerate(cookies):
            cookie_result = CookieValidatorEnhanced._validate_single_cookie(cookie, i)
            
            if cookie_result["valid"]:
                fixed_cookies.append(cookie_result["cookie"])
                
                if cookie_result["fixed"]:
                    result["auto_fixed"] = True
                    result["warnings"].extend(cookie_result["warnings"])
            else:
                result["errors"].extend(cookie_result["errors"])
        
        # 5. 检查是否有关键Cookie
        if fixed_cookies:
            has_kook_cookie = CookieValidatorEnhanced._check_kook_cookies(fixed_cookies)
            
            if not has_kook_cookie:
                result["warnings"].append(
                    "⚠️ 未检测到KOOK关键Cookie（token、session等），可能无法正常登录"
                )
                result["suggestions"].append(
                    "💡 提示：请确保导出了KOOK网站（kookapp.cn）的Cookie"
                )
        
        # 6. 检查重复Cookie
        fixed_cookies = CookieValidatorEnhanced._remove_duplicate_cookies(fixed_cookies)
        
        # 7. 最终结果
        result["cookies"] = fixed_cookies
        result["valid"] = len(fixed_cookies) > 0 and len(result["errors"]) == 0
        
        # 8. 生成友好建议
        if result["valid"]:
            result["suggestions"].append(
                f"✅ Cookie验证成功！共{len(fixed_cookies)}条有效Cookie"
            )
        else:
            result["suggestions"].append(
                "❌ Cookie验证失败，请查看错误详情并修正"
            )
        
        return result
    
    @staticmethod
    def _parse_cookie(cookie_data: str) -> Tuple[List[Dict], List[Dict]]:
        """
        解析Cookie（支持多种格式）
        
        Returns:
            (cookie列表, 错误列表)
        """
        cookies = []
        errors = []
        
        # 格式1：JSON数组（标准格式）
        try:
            parsed = json.loads(cookie_data)
            
            if isinstance(parsed, list):
                cookies = parsed
                logger.info(f"✅ JSON数组格式解析成功，共{len(cookies)}条")
                return cookies, errors
            elif isinstance(parsed, dict):
                cookies = [parsed]
                logger.info("✅ JSON对象格式解析成功")
                return cookies, errors
                
        except json.JSONDecodeError as e:
            # JSON解析失败，尝试自动修复
            logger.debug(f"JSON解析失败: {str(e)}")
            
            # 尝试修复常见JSON错误
            fixed_json = CookieValidatorEnhanced._fix_json_format(cookie_data)
            if fixed_json:
                try:
                    parsed = json.loads(fixed_json)
                    if isinstance(parsed, list):
                        cookies = parsed
                        errors.append({
                            "type": CookieErrorType.INVALID_JSON_FORMAT.value,
                            "message": "⚠️ JSON格式错误已自动修复",
                            "description": "原始Cookie格式有误，但已成功自动修复",
                            "solution": "无需操作，系统已自动修复"
                        })
                        logger.info(f"✅ JSON格式自动修复成功，共{len(cookies)}条")
                        return cookies, errors
                except:
                    pass
        
        # 格式2：Netscape格式（例如EditThisCookie导出）
        if cookie_data.strip().startswith('#'):
            cookies = CookieValidatorEnhanced._parse_netscape_format(cookie_data)
            if cookies:
                logger.info(f"✅ Netscape格式解析成功，共{len(cookies)}条")
                return cookies, errors
        
        # 格式3：键值对格式（name=value; name2=value2）
        if '=' in cookie_data and ';' in cookie_data:
            cookies = CookieValidatorEnhanced._parse_key_value_format(cookie_data)
            if cookies:
                logger.info(f"✅ 键值对格式解析成功，共{len(cookies)}条")
                return cookies, errors
        
        # 所有格式都解析失败
        errors.append({
            "type": CookieErrorType.INVALID_JSON_FORMAT.value,
            "message": "🔴 Cookie格式无法识别",
            "description": "Cookie不是有效的JSON格式、Netscape格式或键值对格式",
            "solution": "请确保Cookie格式正确",
            "examples": [
                "JSON数组格式：[{\"name\":\"token\",\"value\":\"...\"}]",
                "键值对格式：token=abc123; session=xyz789",
                "Netscape格式：# Netscape HTTP Cookie File..."
            ]
        })
        
        return cookies, errors
    
    @staticmethod
    def _fix_json_format(json_str: str) -> str:
        """
        尝试修复常见的JSON格式错误
        
        Returns:
            修复后的JSON字符串，或None（无法修复）
        """
        try:
            # 修复1：单引号替换为双引号
            fixed = json_str.replace("'", '"')
            
            # 修复2：属性名没有引号
            fixed = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', fixed)
            
            # 修复3：移除尾部逗号
            fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
            
            # 修复4：处理未转义的换行符
            fixed = fixed.replace('\n', '\\n').replace('\r', '\\r')
            
            # 验证修复后的JSON
            json.loads(fixed)
            logger.info("✅ JSON格式自动修复成功")
            return fixed
            
        except Exception as e:
            logger.debug(f"JSON修复失败: {str(e)}")
            return None
    
    @staticmethod
    def _parse_netscape_format(cookie_data: str) -> List[Dict]:
        """解析Netscape格式Cookie"""
        cookies = []
        
        for line in cookie_data.split('\n'):
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # Netscape格式：domain flag path secure expiration name value
            parts = line.split('\t')
            if len(parts) >= 7:
                cookies.append({
                    'domain': parts[0],
                    'path': parts[2],
                    'secure': parts[3] == 'TRUE',
                    'expiry': int(parts[4]) if parts[4].isdigit() else None,
                    'name': parts[5],
                    'value': parts[6]
                })
        
        return cookies
    
    @staticmethod
    def _parse_key_value_format(cookie_data: str) -> List[Dict]:
        """解析键值对格式Cookie（name=value; name2=value2）"""
        cookies = []
        
        # 分割成多个cookie
        for pair in cookie_data.split(';'):
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                cookies.append({
                    'name': name.strip(),
                    'value': value.strip(),
                    'domain': '.kookapp.cn',  # 默认域名
                    'path': '/'
                })
        
        return cookies
    
    @staticmethod
    def _validate_single_cookie(cookie: Dict, index: int) -> Dict[str, Any]:
        """
        验证单个Cookie
        
        Returns:
            {
                "valid": bool,
                "cookie": Dict,
                "fixed": bool,
                "errors": List,
                "warnings": List
            }
        """
        result = {
            "valid": False,
            "cookie": {},
            "fixed": False,
            "errors": [],
            "warnings": []
        }
        
        fixed_cookie = dict(cookie)
        
        # 1. 检查必需字段
        missing_fields = []
        for field in CookieValidatorEnhanced.REQUIRED_FIELDS:
            if field not in fixed_cookie or not fixed_cookie[field]:
                missing_fields.append(field)
        
        if missing_fields:
            result["errors"].append({
                "type": CookieErrorType.MISSING_REQUIRED_FIELD.value,
                "message": f"🔴 Cookie #{index+1} 缺少必需字段",
                "description": f"缺少字段：{', '.join(missing_fields)}",
                "solution": "请确保Cookie包含name、value和domain字段"
            })
            return result
        
        # 2. 检查并修正域名
        domain = fixed_cookie['domain']
        if domain not in CookieValidatorEnhanced.VALID_DOMAINS:
            # 尝试修正域名
            if 'kook' in domain.lower() or 'kaiheila' in domain.lower():
                # 修正为标准域名
                fixed_cookie['domain'] = '.kookapp.cn'
                result["fixed"] = True
                result["warnings"].append(
                    f"⚠️ Cookie #{index+1} 域名已自动修正: {domain} → .kookapp.cn"
                )
            else:
                result["errors"].append({
                    "type": CookieErrorType.DOMAIN_MISMATCH.value,
                    "message": f"🔴 Cookie #{index+1} 域名不匹配",
                    "description": f"域名 '{domain}' 不是KOOK的有效域名",
                    "solution": "请确保Cookie来自kookapp.cn或kaiheila.cn",
                    "valid_domains": CookieValidatorEnhanced.VALID_DOMAINS
                })
                return result
        
        # 3. 补充可选字段
        for field, default_value in CookieValidatorEnhanced.OPTIONAL_FIELDS.items():
            if field not in fixed_cookie:
                fixed_cookie[field] = default_value
                result["fixed"] = True
        
        # 4. 检查并修正路径
        if 'path' not in fixed_cookie or not fixed_cookie['path']:
            fixed_cookie['path'] = '/'
            result["fixed"] = True
        elif not fixed_cookie['path'].startswith('/'):
            # 路径格式错误，自动修正
            fixed_cookie['path'] = '/' + fixed_cookie['path'].lstrip('/')
            result["fixed"] = True
            result["warnings"].append(
                f"⚠️ Cookie #{index+1} 路径格式已自动修正"
            )
        
        # 5. 检查过期时间
        if 'expiry' in fixed_cookie or 'expirationDate' in fixed_cookie:
            expiry_field = 'expiry' if 'expiry' in fixed_cookie else 'expirationDate'
            expiry_value = fixed_cookie[expiry_field]
            
            # 统一为expiry字段
            if expiry_field == 'expirationDate':
                fixed_cookie['expiry'] = expiry_value
                del fixed_cookie['expirationDate']
                result["fixed"] = True
            
            # 验证时间戳
            try:
                if isinstance(expiry_value, str):
                    expiry_timestamp = int(expiry_value)
                else:
                    expiry_timestamp = int(expiry_value)
                
                # 检查是否过期
                current_timestamp = int(datetime.now().timestamp())
                if expiry_timestamp < current_timestamp:
                    result["errors"].append({
                        "type": CookieErrorType.EXPIRED_COOKIE.value,
                        "message": f"🔴 Cookie #{index+1} 已过期",
                        "description": f"过期时间：{datetime.fromtimestamp(expiry_timestamp).strftime('%Y-%m-%d %H:%M:%S')}",
                        "solution": "请重新登录KOOK并导出新的Cookie"
                    })
                    return result
                
                # 警告即将过期的Cookie（7天内）
                days_until_expiry = (expiry_timestamp - current_timestamp) / 86400
                if days_until_expiry < 7:
                    result["warnings"].append(
                        f"⚠️ Cookie #{index+1} 将在{int(days_until_expiry)}天后过期，建议尽快更新"
                    )
                
            except (ValueError, TypeError):
                result["errors"].append({
                    "type": CookieErrorType.INVALID_TIMESTAMP.value,
                    "message": f"🔴 Cookie #{index+1} 时间戳格式错误",
                    "description": f"无效的时间戳: {expiry_value}",
                    "solution": "请确保expiry字段是有效的Unix时间戳"
                })
                return result
        
        # 6. 验证成功
        result["valid"] = True
        result["cookie"] = fixed_cookie
        
        return result
    
    @staticmethod
    def _check_kook_cookies(cookies: List[Dict]) -> bool:
        """检查是否包含KOOK关键Cookie"""
        cookie_names = [c['name'].lower() for c in cookies]
        
        for kook_name in CookieValidatorEnhanced.KOOK_COOKIE_NAMES:
            if kook_name in cookie_names:
                return True
        
        return False
    
    @staticmethod
    def _remove_duplicate_cookies(cookies: List[Dict]) -> List[Dict]:
        """移除重复的Cookie（保留最新的）"""
        seen = {}
        
        for cookie in cookies:
            key = f"{cookie['domain']}:{cookie['name']}"
            seen[key] = cookie
        
        return list(seen.values())
    
    @staticmethod
    def get_friendly_error_message(error_type: str) -> str:
        """获取友好的错误提示"""
        messages = {
            CookieErrorType.EMPTY_COOKIE.value: "Cookie内容为空，请粘贴完整的Cookie内容",
            CookieErrorType.INVALID_JSON_FORMAT.value: "Cookie格式错误，请确保是有效的JSON格式",
            CookieErrorType.EXPIRED_COOKIE.value: "Cookie已过期，请重新登录KOOK",
            CookieErrorType.DOMAIN_MISMATCH.value: "Cookie域名不匹配，请确保来自kookapp.cn",
            CookieErrorType.ENCODING_ERROR.value: "Cookie编码错误，请重新复制",
            CookieErrorType.MISSING_REQUIRED_FIELD.value: "Cookie缺少必需字段（name、value、domain）",
            CookieErrorType.INCOMPLETE_FIELDS.value: "Cookie字段不完整",
            CookieErrorType.INVALID_TIMESTAMP.value: "Cookie过期时间格式错误",
            CookieErrorType.DUPLICATE_COOKIES.value: "存在重复的Cookie",
            CookieErrorType.INVALID_PATH.value: "Cookie路径格式错误"
        }
        
        return messages.get(error_type, "未知错误")


# 全局实例
cookie_validator = CookieValidatorEnhanced()
