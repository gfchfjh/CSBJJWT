"""
验证码自动识别模块（2Captcha + 本地OCR）
支持多种识别方案：
1. 本地OCR识别（ddddocr，免费快速）
2. 2Captcha在线识别（付费，准确率高）
3. 手动输入（回退方案）
"""
import asyncio
import aiohttp
import base64
from typing import Optional, Dict, Any, Callable
from pathlib import Path
from .logger import logger

# 尝试导入OCR库
try:
    import ddddocr
    DDDDOCR_AVAILABLE = True
    logger.info("✅ ddddocr库已加载，本地OCR识别可用")
except ImportError:
    DDDDOCR_AVAILABLE = False
    logger.warning("⚠️ ddddocr库未安装，本地OCR识别不可用。安装命令: pip install ddddocr")


class CaptchaSolver:
    """
    验证码求解器
    支持多种识别策略：
    1. 本地OCR（优先，免费）
    2. 2Captcha在线（备用，付费）
    3. 手动输入回调（最终回退）
    """
    
    def __init__(self, api_key: Optional[str] = None, manual_callback: Optional[Callable] = None):
        """
        初始化验证码求解器
        
        Args:
            api_key: 2Captcha API Key
            manual_callback: 手动输入回调函数 async def callback(image_base64: str) -> str
        """
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
        self.enabled = bool(api_key)
        self.manual_callback = manual_callback
        
        # 初始化本地OCR
        self.ocr = None
        if DDDDOCR_AVAILABLE:
            try:
                self.ocr = ddddocr.DdddOcr(show_ad=False)
                logger.info("✅ 本地OCR引擎初始化成功")
            except Exception as e:
                logger.error(f"❌ 本地OCR引擎初始化失败: {str(e)}")
                self.ocr = None
    
    async def solve_image_captcha(self, image_url: Optional[str] = None,
                                  image_base64: Optional[str] = None,
                                  timeout: int = 120,
                                  use_local_first: bool = True) -> Optional[str]:
        """
        解决图片验证码（智能策略）
        
        识别策略：
        1. 优先使用本地OCR（免费、快速）
        2. 失败时使用2Captcha（付费、准确）
        3. 最终回退到手动输入
        
        Args:
            image_url: 图片URL
            image_base64: 图片base64数据
            timeout: 超时时间（秒）
            use_local_first: 是否优先使用本地OCR
            
        Returns:
            验证码文本，失败返回None
        """
        if not image_url and not image_base64:
            logger.error("必须提供image_url或image_base64")
            return None
        
        # 如果只有URL，先下载图片
        if image_url and not image_base64:
            image_base64 = await self._download_image_as_base64(image_url)
            if not image_base64:
                logger.error("下载验证码图片失败")
                return None
        
        # 策略1: 优先尝试本地OCR识别
        if use_local_first and self.ocr:
            result = await self._solve_with_local_ocr(image_base64)
            if result and len(result) >= 4:  # 验证码通常至少4位
                logger.info(f"✅ 本地OCR识别成功: {result}")
                return result
            else:
                logger.warning("⚠️ 本地OCR识别失败或结果不可靠，尝试备用方案")
        
        # 策略2: 使用2Captcha在线识别
        if self.enabled:
            try:
                result = await self._solve_with_2captcha(image_url, image_base64, timeout)
                if result:
                    logger.info(f"✅ 2Captcha识别成功: {result}")
                    return result
                else:
                    logger.warning("⚠️ 2Captcha识别失败，尝试手动输入")
            except Exception as e:
                logger.error(f"2Captcha识别异常: {str(e)}")
        
        # 策略3: 手动输入（最终回退）
        if self.manual_callback:
            try:
                logger.info("🖐️ 请求手动输入验证码")
                result = await self.manual_callback(image_base64)
                if result:
                    logger.info("✅ 手动输入验证码完成")
                    return result
            except Exception as e:
                logger.error(f"手动输入异常: {str(e)}")
        
        logger.error("❌ 所有验证码识别策略均失败")
        return None
    
    async def _solve_with_local_ocr(self, image_base64: str) -> Optional[str]:
        """
        使用本地OCR识别验证码
        
        Args:
            image_base64: 图片base64数据
            
        Returns:
            验证码文本
        """
        if not self.ocr:
            return None
        
        try:
            # 解码base64图片
            image_data = base64.b64decode(image_base64)
            
            # OCR识别（在线程池中执行以避免阻塞）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.ocr.classification, image_data)
            
            # 清理结果（移除空格、特殊字符）
            result = result.strip().replace(' ', '').replace('\n', '')
            
            logger.debug(f"本地OCR识别结果: {result}")
            return result if result else None
            
        except Exception as e:
            logger.error(f"本地OCR识别异常: {str(e)}")
            return None
    
    async def _solve_with_2captcha(self, image_url: Optional[str] = None,
                                   image_base64: Optional[str] = None,
                                   timeout: int = 120) -> Optional[str]:
        """
        使用2Captcha在线识别验证码
        
        Args:
            image_url: 图片URL
            image_base64: 图片base64数据
            timeout: 超时时间（秒）
            
        Returns:
            验证码文本
        """
        try:
            # 1. 提交验证码任务
            task_id = await self._submit_captcha(image_url, image_base64)
            if not task_id:
                return None
            
            logger.info(f"2Captcha任务已提交: {task_id}")
            
            # 2. 轮询获取结果
            result = await self._get_captcha_result(task_id, timeout)
            return result
                
        except Exception as e:
            logger.error(f"2Captcha识别异常: {str(e)}")
            return None
    
    async def _download_image_as_base64(self, image_url: str) -> Optional[str]:
        """
        下载图片并转换为base64
        
        Args:
            image_url: 图片URL
            
        Returns:
            base64编码的图片数据
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        return base64.b64encode(image_data).decode('utf-8')
                    else:
                        logger.error(f"下载图片失败，状态码: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"下载图片异常: {str(e)}")
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


def init_captcha_solver(api_key: Optional[str] = None, manual_callback: Optional[Callable] = None):
    """
    初始化验证码求解器
    
    Args:
        api_key: 2Captcha API Key
        manual_callback: 手动输入回调函数
    """
    global captcha_solver
    captcha_solver = CaptchaSolver(api_key, manual_callback)
    return captcha_solver


def get_captcha_solver() -> CaptchaSolver:
    """获取验证码求解器实例"""
    global captcha_solver
    if captcha_solver is None:
        captcha_solver = CaptchaSolver()
    return captcha_solver
