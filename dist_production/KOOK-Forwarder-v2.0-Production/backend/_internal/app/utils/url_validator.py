"""
URL验证器
✅ P1-5优化: 验证码来源验证，防止钓鱼攻击
"""
from urllib.parse import urlparse
from typing import List
from ..utils.exceptions import SecurityException


class URLValidator:
    """
    URL验证器 - 确保URL来自可信域名
    
    使用方式:
    ```python
    # 验证验证码URL
    URLValidator.validate_captcha_url(captcha_url)
    
    # 验证图片URL
    URLValidator.validate_image_url(image_url)
    
    # 检查域名
    if URLValidator.is_kook_domain(url):
        # 安全处理
    ```
    """
    
    # KOOK官方允许的域名
    KOOK_DOMAINS = [
        'kookapp.cn',
        'www.kookapp.cn',
        'img.kookapp.cn',
        'captcha.kookapp.cn',
        'api.kookapp.cn',
        'cdn.kookapp.cn',
    ]
    
    # 允许的图片域名
    IMAGE_DOMAINS = KOOK_DOMAINS + [
        'img.kaiheila.cn',  # 旧域名
        'cdn.kaiheila.cn',
    ]
    
    @classmethod
    def is_kook_domain(cls, url: str) -> bool:
        """
        验证URL是否来自KOOK官方域名
        
        Args:
            url: 要验证的URL
            
        Returns:
            是否为KOOK官方域名
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # 精确匹配
            if domain in cls.KOOK_DOMAINS:
                return True
            
            # 子域名匹配
            for allowed in cls.KOOK_DOMAINS:
                if domain.endswith('.' + allowed):
                    return True
            
            return False
            
        except Exception:
            return False
    
    @classmethod
    def is_image_domain(cls, url: str) -> bool:
        """
        验证URL是否为允许的图片域名
        
        Args:
            url: 要验证的URL
            
        Returns:
            是否为允许的图片域名
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # 精确匹配
            if domain in cls.IMAGE_DOMAINS:
                return True
            
            # 子域名匹配
            for allowed in cls.IMAGE_DOMAINS:
                if domain.endswith('.' + allowed):
                    return True
            
            return False
            
        except Exception:
            return False
    
    @classmethod
    def validate_captcha_url(cls, url: str):
        """
        验证验证码URL（严格验证）
        
        Args:
            url: 验证码图片URL
            
        Raises:
            SecurityException: 如果URL来源不可信
        """
        if not url:
            raise SecurityException(
                "验证码URL为空",
                error_code="EMPTY_CAPTCHA_URL",
                user_friendly_message="验证码URL无效"
            )
        
        if not cls.is_kook_domain(url):
            raise SecurityException(
                f"验证码URL来源不可信: {url}",
                error_code="UNTRUSTED_CAPTCHA_SOURCE",
                user_friendly_message="验证码来源不是KOOK官方域名，可能存在安全风险"
            )
    
    @classmethod
    def validate_image_url(cls, url: str):
        """
        验证图片URL
        
        Args:
            url: 图片URL
            
        Raises:
            SecurityException: 如果URL来源不可信
        """
        if not url:
            raise SecurityException(
                "图片URL为空",
                error_code="EMPTY_IMAGE_URL",
                user_friendly_message="图片URL无效"
            )
        
        if not cls.is_image_domain(url):
            from .logger import logger
            logger.warning(f"⚠️ 图片URL来源可能不可信: {url}")
            # 图片URL不强制阻止，仅警告
    
    @classmethod
    def validate_webhook_url(cls, url: str, platform: str):
        """
        验证Webhook URL
        
        Args:
            url: Webhook URL
            platform: 平台名称（discord/telegram/feishu）
            
        Raises:
            SecurityException: 如果URL格式不正确
        """
        if not url:
            raise SecurityException(
                f"{platform} Webhook URL为空",
                error_code="EMPTY_WEBHOOK_URL",
                user_friendly_message="Webhook URL不能为空"
            )
        
        try:
            parsed = urlparse(url)
            
            # 检查协议
            if parsed.scheme not in ['http', 'https']:
                raise SecurityException(
                    f"Webhook URL协议无效: {parsed.scheme}",
                    error_code="INVALID_WEBHOOK_PROTOCOL",
                    user_friendly_message="Webhook URL必须使用http或https协议"
                )
            
            # 建议使用HTTPS
            if parsed.scheme == 'http':
                from .logger import logger
                logger.warning(f"⚠️ Webhook URL使用HTTP（不安全），建议使用HTTPS: {url}")
            
            # 检查域名
            if not parsed.netloc:
                raise SecurityException(
                    "Webhook URL缺少域名",
                    error_code="MISSING_WEBHOOK_DOMAIN",
                    user_friendly_message="Webhook URL格式错误，缺少域名"
                )
            
            # 平台特定验证
            if platform == 'discord':
                if 'discord.com' not in parsed.netloc and 'discordapp.com' not in parsed.netloc:
                    from .logger import logger
                    logger.warning(f"⚠️ Discord Webhook URL域名可能不正确: {parsed.netloc}")
            
            elif platform == 'feishu':
                if 'feishu.cn' not in parsed.netloc and 'larksuite.com' not in parsed.netloc:
                    from .logger import logger
                    logger.warning(f"⚠️ 飞书Webhook URL域名可能不正确: {parsed.netloc}")
            
        except SecurityException:
            raise
        except Exception as e:
            raise SecurityException(
                f"Webhook URL解析失败: {str(e)}",
                error_code="WEBHOOK_URL_PARSE_ERROR",
                user_friendly_message="Webhook URL格式错误"
            )
    
    @classmethod
    def add_trusted_domain(cls, domain: str, domain_type: str = 'kook'):
        """
        添加受信任域名（动态扩展）
        
        Args:
            domain: 域名
            domain_type: 域名类型（'kook' 或 'image'）
        """
        domain = domain.lower()
        
        if domain_type == 'kook':
            if domain not in cls.KOOK_DOMAINS:
                cls.KOOK_DOMAINS.append(domain)
        elif domain_type == 'image':
            if domain not in cls.IMAGE_DOMAINS:
                cls.IMAGE_DOMAINS.append(domain)
