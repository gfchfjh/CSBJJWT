"""
消息翻译插件
✅ P1-2: 自动消息翻译功能
"""
import aiohttp
from typing import Optional, Dict
from .plugin_system import PluginBase, PluginInfo, PluginHook, plugin_manager
from ..utils.logger import logger
from ..config import settings


class TranslatorPlugin(PluginBase):
    """消息翻译插件"""
    
    def __init__(self):
        super().__init__()
        
        # 配置
        self.enabled_translation = getattr(settings, 'translation_enabled', False)
        self.source_lang = getattr(settings, 'translation_source_lang', 'auto')
        self.target_lang = getattr(settings, 'translation_target_lang', 'en')
        self.api_provider = getattr(settings, 'translation_api_provider', 'google')
        
        # API配置
        self.google_api_key = getattr(settings, 'google_translate_api_key', '')
        self.baidu_app_id = getattr(settings, 'baidu_translate_app_id', '')
        self.baidu_secret_key = getattr(settings, 'baidu_translate_secret_key', '')
        
        # 统计
        self.stats = {
            'total_translated': 0,
            'success': 0,
            'failed': 0
        }
    
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        return PluginInfo(
            id='translator',
            name='消息翻译',
            version='1.0.0',
            author='KOOK Forwarder Team',
            description='自动翻译消息内容到指定语言'
        )
    
    async def on_load(self):
        """插件加载"""
        # 注册钩子
        plugin_manager.register_hook(
            PluginHook.AFTER_MESSAGE_PROCESS,
            self.translate_message
        )
        
        logger.info("翻译插件已加载")
    
    async def translate_message(self, message: Dict) -> Dict:
        """
        翻译消息
        
        Args:
            message: 消息对象
            
        Returns:
            翻译后的消息对象
        """
        if not self.enabled_translation:
            return message
        
        # 提取文本内容
        content = message.get('content', '')
        
        if not content or len(content.strip()) == 0:
            return message
        
        self.stats['total_translated'] += 1
        
        try:
            # 翻译文本
            translated_text = await self._translate_text(
                content,
                self.source_lang,
                self.target_lang
            )
            
            if translated_text:
                # 添加翻译结果
                message['translated_content'] = translated_text
                message['translation_meta'] = {
                    'source_lang': self.source_lang,
                    'target_lang': self.target_lang,
                    'provider': self.api_provider
                }
                
                self.stats['success'] += 1
                
                logger.debug(f"消息翻译成功: {content[:50]}... -> {translated_text[:50]}...")
            
            return message
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"消息翻译失败: {str(e)}")
            return message
    
    async def _translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """
        翻译文本
        
        Args:
            text: 原文
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            翻译后的文本
        """
        if self.api_provider == 'google':
            return await self._translate_with_google(text, source_lang, target_lang)
        elif self.api_provider == 'baidu':
            return await self._translate_with_baidu(text, source_lang, target_lang)
        else:
            logger.error(f"未知的翻译API提供商: {self.api_provider}")
            return None
    
    async def _translate_with_google(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """使用Google翻译"""
        try:
            url = 'https://translation.googleapis.com/language/translate/v2'
            
            params = {
                'q': text,
                'target': target_lang,
                'key': self.google_api_key
            }
            
            if source_lang != 'auto':
                params['source'] = source_lang
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        translations = data.get('data', {}).get('translations', [])
                        if translations:
                            return translations[0].get('translatedText')
                    else:
                        logger.error(f"Google翻译API错误: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Google翻译失败: {str(e)}")
            return None
    
    async def _translate_with_baidu(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """使用百度翻译"""
        try:
            import hashlib
            import random
            
            url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
            
            # 生成签名
            salt = str(random.randint(32768, 65536))
            sign_str = f"{self.baidu_app_id}{text}{salt}{self.baidu_secret_key}"
            sign = hashlib.md5(sign_str.encode()).hexdigest()
            
            params = {
                'q': text,
                'from': 'auto' if source_lang == 'auto' else source_lang,
                'to': target_lang,
                'appid': self.baidu_app_id,
                'salt': salt,
                'sign': sign
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        trans_result = data.get('trans_result', [])
                        if trans_result:
                            return trans_result[0].get('dst')
                    else:
                        logger.error(f"百度翻译API错误: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"百度翻译失败: {str(e)}")
            return None
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'success_rate': (
                self.stats['success'] / self.stats['total_translated'] * 100
                if self.stats['total_translated'] > 0 else 0
            )
        }


# 自动注册插件
translator_plugin = TranslatorPlugin()
