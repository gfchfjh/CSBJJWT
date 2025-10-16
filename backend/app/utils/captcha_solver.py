"""
验证码自动识别模块（2Captcha集成）
"""
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from .logger import logger


class CaptchaSolver:
    """验证码求解器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化验证码求解器
        
        Args:
            api_key: 2Captcha API Key
        """
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
        self.enabled = bool(api_key)
    
    async def solve_image_captcha(self, image_url: Optional[str] = None,
                                  image_base64: Optional[str] = None,
                                  timeout: int = 120) -> Optional[str]:
        """
        解决图片验证码
        
        Args:
            image_url: 图片URL
            image_base64: 图片base64数据
            timeout: 超时时间（秒）
            
        Returns:
            验证码文本，失败返回None
        """
        if not self.enabled:
            logger.warning("2Captcha未配置，无法自动识别验证码")
            return None
        
        if not image_url and not image_base64:
            logger.error("必须提供image_url或image_base64")
            return None
        
        try:
            # 1. 提交验证码任务
            task_id = await self._submit_captcha(image_url, image_base64)
            if not task_id:
                return None
            
            logger.info(f"验证码任务已提交: {task_id}")
            
            # 2. 轮询获取结果
            result = await self._get_captcha_result(task_id, timeout)
            
            if result:
                logger.info(f"✅ 验证码识别成功: {result}")
                return result
            else:
                logger.error("❌ 验证码识别失败")
                return None
                
        except Exception as e:
            logger.error(f"验证码识别异常: {str(e)}")
            return None
    
    async def _submit_captcha(self, image_url: Optional[str] = None,
                             image_base64: Optional[str] = None) -> Optional[str]:
        """
        提交验证码任务到2Captcha
        
        Args:
            image_url: 图片URL
            image_base64: 图片base64数据
            
        Returns:
            任务ID
        """
        try:
            params = {
                'key': self.api_key,
                'method': 'base64' if image_base64 else 'post',
                'json': 1
            }
            
            if image_base64:
                params['body'] = image_base64
            elif image_url:
                params['url'] = image_url
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/in.php",
                    data=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    data = await response.json()
                    
                    if data.get('status') == 1:
                        return data.get('request')
                    else:
                        error_text = data.get('request', 'Unknown error')
                        logger.error(f"提交验证码失败: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"提交验证码异常: {str(e)}")
            return None
    
    async def _get_captcha_result(self, task_id: str, timeout: int = 120) -> Optional[str]:
        """
        获取验证码识别结果
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            验证码文本
        """
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                params = {
                    'key': self.api_key,
                    'action': 'get',
                    'id': task_id,
                    'json': 1
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}/res.php",
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        data = await response.json()
                        
                        if data.get('status') == 1:
                            # 识别成功
                            return data.get('request')
                        elif data.get('request') == 'CAPCHA_NOT_READY':
                            # 还未完成，等待5秒后重试
                            await asyncio.sleep(5)
                        else:
                            # 识别失败
                            error_text = data.get('request', 'Unknown error')
                            logger.error(f"获取验证码结果失败: {error_text}")
                            return None
                            
            except asyncio.TimeoutError:
                logger.warning("获取验证码结果超时，重试中...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"获取验证码结果异常: {str(e)}")
                await asyncio.sleep(5)
        
        logger.error(f"验证码识别超时（{timeout}秒）")
        return None
    
    async def report_bad(self, task_id: str) -> bool:
        """
        报告错误的验证码结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        if not self.enabled:
            return False
        
        try:
            params = {
                'key': self.api_key,
                'action': 'reportbad',
                'id': task_id,
                'json': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/res.php",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    data = await response.json()
                    
                    if data.get('status') == 1:
                        logger.info("已报告错误的验证码")
                        return True
                    else:
                        logger.error("报告错误的验证码失败")
                        return False
                        
        except Exception as e:
            logger.error(f"报告错误的验证码异常: {str(e)}")
            return False
    
    async def get_balance(self) -> Optional[float]:
        """
        获取2Captcha账户余额
        
        Returns:
            余额（美元）
        """
        if not self.enabled:
            return None
        
        try:
            params = {
                'key': self.api_key,
                'action': 'getbalance',
                'json': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/res.php",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    data = await response.json()
                    
                    if data.get('status') == 1:
                        balance = float(data.get('request', 0))
                        logger.info(f"2Captcha余额: ${balance:.2f}")
                        return balance
                    else:
                        logger.error("获取余额失败")
                        return None
                        
        except Exception as e:
            logger.error(f"获取余额异常: {str(e)}")
            return None


# 创建全局实例（API Key从配置中读取）
captcha_solver = None


def init_captcha_solver(api_key: Optional[str] = None):
    """
    初始化验证码求解器
    
    Args:
        api_key: 2Captcha API Key
    """
    global captcha_solver
    captcha_solver = CaptchaSolver(api_key)
    return captcha_solver


def get_captcha_solver() -> CaptchaSolver:
    """获取验证码求解器实例"""
    global captcha_solver
    if captcha_solver is None:
        captcha_solver = CaptchaSolver()
    return captcha_solver
