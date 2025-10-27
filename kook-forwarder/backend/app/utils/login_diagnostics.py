"""
登录诊断工具
P0-10: 登录失败诊断
"""
import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import Page
from ..utils.logger import logger


class LoginDiagnostics:
    """登录诊断器"""
    
    def __init__(self):
        self.diagnosis_results = {}
    
    async def diagnose(self, page: Page, error_message: str = "") -> Dict[str, Any]:
        """
        全面诊断登录失败原因
        
        Args:
            page: Playwright 页面对象
            error_message: 错误消息
            
        Returns:
            诊断结果
        """
        logger.info("🔍 开始登录诊断...")
        
        results = {
            'error_message': error_message,
            'issues': [],
            'suggestions': [],
            'details': {}
        }
        
        # 1. 检查网络连接
        network_ok, network_msg = await self._check_network(page)
        results['details']['network'] = {'ok': network_ok, 'message': network_msg}
        if not network_ok:
            results['issues'].append('network')
            results['suggestions'].append('请检查网络连接，确保能访问 www.kookapp.cn')
        
        # 2. 检查页面状态
        page_ok, page_msg = await self._check_page_state(page)
        results['details']['page'] = {'ok': page_ok, 'message': page_msg}
        if not page_ok:
            results['issues'].append('page')
            results['suggestions'].append('页面加载失败，请刷新后重试')
        
        # 3. 检查凭据有效性
        cred_ok, cred_msg = await self._check_credentials(page)
        results['details']['credentials'] = {'ok': cred_ok, 'message': cred_msg}
        if not cred_ok:
            results['issues'].append('credentials')
            results['suggestions'].append('邮箱或密码错误，请检查后重试')
        
        # 4. 检查验证码
        captcha_required, captcha_msg = await self._check_captcha(page)
        results['details']['captcha'] = {'required': captcha_required, 'message': captcha_msg}
        if captcha_required:
            results['issues'].append('captcha')
            results['suggestions'].append('需要验证码，请配置 2Captcha API Key 或手动输入')
        
        # 5. 检查手机验证
        sms_required, sms_msg = await self._check_sms_verification(page)
        results['details']['sms'] = {'required': sms_required, 'message': sms_msg}
        if sms_required:
            results['issues'].append('sms')
            results['suggestions'].append('需要短信验证码，请查看手机')
        
        # 6. 检查 IP 限制
        ip_blocked, ip_msg = await self._check_ip_restriction(page)
        results['details']['ip'] = {'blocked': ip_blocked, 'message': ip_msg}
        if ip_blocked:
            results['issues'].append('ip_blocked')
            results['suggestions'].append('IP 可能被限制，请更换网络或使用代理')
        
        # 7. 检查账号状态
        account_ok, account_msg = await self._check_account_status(page)
        results['details']['account'] = {'ok': account_ok, 'message': account_msg}
        if not account_ok:
            results['issues'].append('account_banned')
            results['suggestions'].append('账号可能被封禁，请联系 KOOK 客服')
        
        # 生成诊断摘要
        results['summary'] = self._generate_summary(results)
        
        logger.info(f"✅ 诊断完成，发现 {len(results['issues'])} 个问题")
        
        return results
    
    async def _check_network(self, page: Page) -> tuple[bool, str]:
        """检查网络连接"""
        try:
            # 尝试访问 KOOK
            response = await page.goto('https://www.kookapp.cn', wait_until='domcontentloaded', timeout=10000)
            
            if response and response.ok:
                return True, "网络连接正常"
            else:
                return False, f"无法访问 KOOK（HTTP {response.status if response else '无响应'}）"
                
        except asyncio.TimeoutError:
            return False, "网络连接超时（10 秒）"
        except Exception as e:
            return False, f"网络连接异常: {str(e)}"
    
    async def _check_page_state(self, page: Page) -> tuple[bool, str]:
        """检查页面状态"""
        try:
            # 检查页面是否加载完成
            if page.url == 'about:blank':
                return False, "页面未加载"
            
            # 检查页面标题
            title = await page.title()
            if 'KOOK' not in title and '开黑啦' not in title:
                return False, f"页面标题异常: {title}"
            
            return True, "页面状态正常"
            
        except Exception as e:
            return False, f"页面状态检查失败: {str(e)}"
    
    async def _check_credentials(self, page: Page) -> tuple[bool, str]:
        """检查凭据有效性（通过页面提示判断）"""
        try:
            # 查找错误提示
            error_selectors = [
                '.error-message',
                '[class*="error"]',
                '.toast-error',
                'div:has-text("邮箱或密码错误")',
                'div:has-text("账号不存在")',
            ]
            
            for selector in error_selectors:
                try:
                    error_element = await page.query_selector(selector)
                    if error_element:
                        error_text = await error_element.inner_text()
                        if '密码' in error_text or '邮箱' in error_text:
                            return False, f"凭据错误: {error_text}"
                except:
                    continue
            
            return True, "暂未发现凭据错误提示"
            
        except Exception as e:
            return True, f"检查异常（假定正常）: {str(e)}"
    
    async def _check_captcha(self, page: Page) -> tuple[bool, str]:
        """检查是否需要验证码"""
        try:
            captcha_selectors = [
                'input[name="captcha"]',
                'input[placeholder*="验证码"]',
                'img.captcha-image',
                '.captcha-container'
            ]
            
            for selector in captcha_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element:
                        return True, "需要验证码"
                except:
                    continue
            
            return False, "不需要验证码"
            
        except Exception as e:
            return False, f"检查异常: {str(e)}"
    
    async def _check_sms_verification(self, page: Page) -> tuple[bool, str]:
        """检查是否需要短信验证"""
        try:
            sms_selectors = [
                'input[name="sms_code"]',
                'input[placeholder*="短信验证码"]',
                'input[placeholder*="手机验证码"]',
                'div:has-text("短信验证码")',
            ]
            
            for selector in sms_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element:
                        return True, "需要短信验证码"
                except:
                    continue
            
            return False, "不需要短信验证码"
            
        except Exception as e:
            return False, f"检查异常: {str(e)}"
    
    async def _check_ip_restriction(self, page: Page) -> tuple[bool, str]:
        """检查 IP 是否被限制"""
        try:
            # 查找 IP 限制提示
            restriction_keywords = [
                'IP 被限制',
                '访问频繁',
                '异常登录',
                '请稍后再试',
                'too many requests',
            ]
            
            page_content = await page.content()
            page_content_lower = page_content.lower()
            
            for keyword in restriction_keywords:
                if keyword.lower() in page_content_lower:
                    return True, f"检测到限制提示: {keyword}"
            
            return False, "未检测到 IP 限制"
            
        except Exception as e:
            return False, f"检查异常: {str(e)}"
    
    async def _check_account_status(self, page: Page) -> tuple[bool, str]:
        """检查账号状态"""
        try:
            # 查找账号封禁提示
            banned_keywords = [
                '账号已被封禁',
                '账号异常',
                '账号被冻结',
                '违反用户协议',
                'account banned',
                'account suspended',
            ]
            
            page_content = await page.content()
            page_content_lower = page_content.lower()
            
            for keyword in banned_keywords:
                if keyword.lower() in page_content_lower:
                    return False, f"账号异常: {keyword}"
            
            return True, "账号状态正常"
            
        except Exception as e:
            return True, f"检查异常（假定正常）: {str(e)}"
    
    def _generate_summary(self, results: Dict) -> str:
        """生成诊断摘要"""
        if not results['issues']:
            return "✅ 未发现明显问题，登录失败可能是临时网络波动，请重试"
        
        # 按优先级排序问题
        priority_order = ['account_banned', 'ip_blocked', 'credentials', 'captcha', 'sms', 'network', 'page']
        
        sorted_issues = sorted(
            results['issues'],
            key=lambda x: priority_order.index(x) if x in priority_order else 999
        )
        
        # 主要问题
        main_issue = sorted_issues[0]
        
        issue_messages = {
            'account_banned': '❌ 账号被封禁或冻结',
            'ip_blocked': '⚠️ IP 被限制',
            'credentials': '❌ 邮箱或密码错误',
            'captcha': '🔐 需要验证码',
            'sms': '📱 需要短信验证码',
            'network': '🌐 网络连接问题',
            'page': '📄 页面加载问题',
        }
        
        return issue_messages.get(main_issue, f"❓ 未知问题: {main_issue}")


# 全局实例
login_diagnostics = LoginDiagnostics()
