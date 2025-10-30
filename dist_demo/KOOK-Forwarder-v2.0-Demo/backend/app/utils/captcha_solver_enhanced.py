"""
验证码识别器增强版
版本: v6.0.0
作者: KOOK Forwarder Team

支持多种识别方式:
1. 2Captcha API（云端识别，准确率95%，成本$3/1000次）
2. 本地OCR（ddddocr，准确率65-70%，免费）
3. 自定义模型（TensorFlow，准确率目标85%+，免费）
4. 验证码缓存（相同验证码复用）
5. 用户手动输入（兜底方案）

智能策略:
- 优先本地识别（快速免费）
- 失败时使用2Captcha（准确但收费）
- 最后请求用户输入
"""

import aiohttp
import asyncio
import hashlib
import time
from typing import Optional, Dict, Tuple
from pathlib import Path
from ..config import settings
from ..utils.logger import logger


class CaptchaSolverEnhanced:
    """增强版验证码识别器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.captcha_2captcha_api_key
        self.enabled = bool(self.api_key)
        
        # 验证码缓存（相同图片复用结果）
        self.captcha_cache: Dict[str, str] = {}
        self.cache_ttl = 300  # 5分钟
        
        # 本地OCR模型
        self.local_ocr = None
        self._init_local_ocr()
        
        # 自定义模型（可选）
        self.custom_model = None
        self._init_custom_model()
        
        # 统计信息
        self.stats = {
            '2captcha_success': 0,
            '2captcha_failed': 0,
            'local_ocr_success': 0,
            'local_ocr_failed': 0,
            'custom_model_success': 0,
            'custom_model_failed': 0,
            'cache_hits': 0,
            'manual_input': 0,
            'total_cost_usd': 0.0
        }
    
    def _init_local_ocr(self):
        """初始化本地OCR"""
        try:
            import ddddocr
            self.local_ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
            logger.info("✅ 本地OCR已初始化（ddddocr）")
        except ImportError:
            logger.warning("⚠️  ddddocr未安装，本地OCR不可用")
            logger.info("安装方法: pip install ddddocr")
        except Exception as e:
            logger.error(f"初始化本地OCR失败: {str(e)}")
    
    def _init_custom_model(self):
        """初始化自定义模型（可选）"""
        model_path = Path(settings.data_dir) / "models" / "captcha_model.h5"
        
        if model_path.exists():
            try:
                # 尝试加载TensorFlow模型
                import tensorflow as tf
                self.custom_model = tf.keras.models.load_model(str(model_path))
                logger.info("✅ 自定义验证码模型已加载")
            except ImportError:
                logger.warning("⚠️  TensorFlow未安装，自定义模型不可用")
            except Exception as e:
                logger.error(f"加载自定义模型失败: {str(e)}")
        else:
            logger.info("ℹ️  自定义验证码模型未找到，将使用标准识别")
    
    def _get_image_hash(self, image_data: bytes) -> str:
        """计算图片哈希（用于缓存）"""
        return hashlib.md5(image_data).hexdigest()
    
    async def solve_captcha(self, image_data: bytes, 
                           strategy: str = 'smart') -> Tuple[Optional[str], str]:
        """
        识别验证码（智能策略）
        
        Args:
            image_data: 验证码图片数据
            strategy: 识别策略
                - 'smart': 智能选择（本地→2Captcha→手动）
                - 'local_only': 仅本地识别
                - '2captcha_only': 仅2Captcha
                - 'manual': 直接请求手动输入
            
        Returns:
            (验证码结果, 识别方法)
        """
        # 检查缓存
        image_hash = self._get_image_hash(image_data)
        if image_hash in self.captcha_cache:
            self.stats['cache_hits'] += 1
            logger.info("✅ 验证码缓存命中")
            return self.captcha_cache[image_hash], 'cache'
        
        result = None
        method = None
        
        # 策略执行
        if strategy == 'smart':
            # 1. 尝试自定义模型
            if self.custom_model:
                result = await self._solve_with_custom_model(image_data)
                if result:
                    method = 'custom_model'
                    self.stats['custom_model_success'] += 1
                    logger.info(f"✅ 自定义模型识别成功: {result}")
            
            # 2. 尝试本地OCR
            if not result and self.local_ocr:
                result = await self._solve_with_local_ocr(image_data)
                if result:
                    method = 'local_ocr'
                    self.stats['local_ocr_success'] += 1
                    logger.info(f"✅ 本地OCR识别成功: {result}")
            
            # 3. 尝试2Captcha
            if not result and self.enabled:
                result = await self._solve_with_2captcha(image_data)
                if result:
                    method = '2captcha'
                    self.stats['2captcha_success'] += 1
                    self.stats['total_cost_usd'] += 0.003  # $3/1000次
                    logger.info(f"✅ 2Captcha识别成功: {result}")
        
        elif strategy == 'local_only':
            if self.custom_model:
                result = await self._solve_with_custom_model(image_data)
                method = 'custom_model' if result else None
            if not result and self.local_ocr:
                result = await self._solve_with_local_ocr(image_data)
                method = 'local_ocr' if result else None
        
        elif strategy == '2captcha_only':
            if self.enabled:
                result = await self._solve_with_2captcha(image_data)
                method = '2captcha' if result else None
        
        # 缓存结果
        if result:
            self.captcha_cache[image_hash] = result
            # 5分钟后清理缓存
            asyncio.create_task(self._clear_cache_after(image_hash, self.cache_ttl))
        
        return result, method or 'none'
    
    async def _solve_with_local_ocr(self, image_data: bytes) -> Optional[str]:
        """使用本地OCR识别"""
        if not self.local_ocr:
            return None
        
        try:
            # 在线程池中运行（避免阻塞）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.local_ocr.classification,
                image_data
            )
            
            # 验证结果
            if result and len(result) >= 4:  # 验证码通常4-6位
                # 清理结果（移除空格和特殊字符）
                result = result.strip().replace(' ', '')
                return result
            
            self.stats['local_ocr_failed'] += 1
            return None
            
        except Exception as e:
            logger.error(f"本地OCR识别失败: {str(e)}")
            self.stats['local_ocr_failed'] += 1
            return None
    
    async def _solve_with_custom_model(self, image_data: bytes) -> Optional[str]:
        """使用自定义模型识别（TensorFlow）"""
        if not self.custom_model:
            return None
        
        try:
            from PIL import Image
            import numpy as np
            from io import BytesIO
            
            # 预处理图片
            img = Image.open(BytesIO(image_data))
            img = img.convert('RGB')
            img = img.resize((150, 50))  # 标准尺寸
            
            # 转换为numpy数组
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # 在线程池中运行预测
            loop = asyncio.get_event_loop()
            prediction = await loop.run_in_executor(
                None,
                self.custom_model.predict,
                img_array,
                {'verbose': 0}
            )
            
            # 解码预测结果（根据模型输出调整）
            result = self._decode_prediction(prediction)
            
            if result:
                return result
            
            self.stats['custom_model_failed'] += 1
            return None
            
        except Exception as e:
            logger.error(f"自定义模型识别失败: {str(e)}")
            self.stats['custom_model_failed'] += 1
            return None
    
    def _decode_prediction(self, prediction) -> Optional[str]:
        """解码模型预测结果"""
        # 这里需要根据实际模型输出格式调整
        # 示例：如果输出是字符概率矩阵
        try:
            import numpy as np
            
            # 假设输出shape为(1, seq_length, num_classes)
            # 每个位置取概率最高的字符
            chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            result = ''
            
            for pos in range(prediction.shape[1]):
                char_idx = np.argmax(prediction[0, pos, :])
                if char_idx < len(chars):
                    result += chars[char_idx]
            
            return result if result else None
            
        except:
            return None
    
    async def _solve_with_2captcha(self, image_data: bytes) -> Optional[str]:
        """使用2Captcha识别"""
        if not self.enabled:
            return None
        
        try:
            import base64
            
            # 将图片转换为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 提交任务
            async with aiohttp.ClientSession() as session:
                # 提交
                async with session.post(
                    'http://2captcha.com/in.php',
                    data={
                        'key': self.api_key,
                        'method': 'base64',
                        'body': image_base64,
                        'json': 1
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    data = await response.json()
                    
                    if data.get('status') != 1:
                        logger.error(f"2Captcha提交失败: {data}")
                        self.stats['2captcha_failed'] += 1
                        return None
                    
                    task_id = data.get('request')
                    logger.info(f"2Captcha任务ID: {task_id}")
                
                # 轮询结果（最多120秒）
                max_attempts = 40
                for attempt in range(max_attempts):
                    await asyncio.sleep(3)  # 每3秒查询一次
                    
                    async with session.get(
                        'http://2captcha.com/res.php',
                        params={
                            'key': self.api_key,
                            'action': 'get',
                            'id': task_id,
                            'json': 1
                        },
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        data = await response.json()
                        
                        if data.get('status') == 1:
                            # 识别成功
                            result = data.get('request')
                            logger.info(f"✅ 2Captcha识别成功: {result}")
                            return result
                        elif data.get('request') == 'CAPCHA_NOT_READY':
                            # 还在处理中
                            continue
                        else:
                            # 识别失败
                            logger.error(f"2Captcha识别失败: {data}")
                            self.stats['2captcha_failed'] += 1
                            return None
                
                # 超时
                logger.error("2Captcha识别超时（120秒）")
                self.stats['2captcha_failed'] += 1
                return None
                
        except Exception as e:
            logger.error(f"2Captcha识别异常: {str(e)}")
            self.stats['2captcha_failed'] += 1
            return None
    
    async def _clear_cache_after(self, key: str, delay: int):
        """延迟清理缓存"""
        await asyncio.sleep(delay)
        if key in self.captcha_cache:
            del self.captcha_cache[key]
    
    async def get_balance(self) -> Optional[float]:
        """获取2Captcha余额"""
        if not self.enabled:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'http://2captcha.com/res.php',
                    params={
                        'key': self.api_key,
                        'action': 'getbalance',
                        'json': 1
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    data = await response.json()
                    
                    if data.get('status') == 1:
                        balance = float(data.get('request', 0))
                        return balance
                    
                    return None
        except Exception as e:
            logger.error(f"获取2Captcha余额失败: {str(e)}")
            return None
    
    def get_stats(self) -> Dict:
        """获取识别统计"""
        total_attempts = (
            self.stats['2captcha_success'] + self.stats['2captcha_failed'] +
            self.stats['local_ocr_success'] + self.stats['local_ocr_failed'] +
            self.stats['custom_model_success'] + self.stats['custom_model_failed']
        )
        
        success_attempts = (
            self.stats['2captcha_success'] +
            self.stats['local_ocr_success'] +
            self.stats['custom_model_success'] +
            self.stats['cache_hits']
        )
        
        success_rate = success_attempts / total_attempts if total_attempts > 0 else 0
        
        return {
            **self.stats,
            'total_attempts': total_attempts,
            'success_attempts': success_attempts,
            'success_rate': f"{success_rate:.2%}",
            'cache_size': len(self.captcha_cache)
        }


# 全局实例
captcha_solver_enhanced = CaptchaSolverEnhanced()


def get_captcha_solver_enhanced() -> CaptchaSolverEnhanced:
    """获取验证码识别器实例"""
    return captcha_solver_enhanced
