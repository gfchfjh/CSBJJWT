"""
图片处理策略管理器
✅ P0-6优化：实现图片处理策略切换机制
"""
import asyncio
from typing import Optional, Dict, Tuple
from pathlib import Path
from ..config import settings
from ..utils.logger import logger
from .image import image_processor


class ImageStrategy:
    """图片处理策略管理器"""
    
    # 策略类型
    STRATEGY_SMART = "smart"      # 智能模式（默认）
    STRATEGY_DIRECT = "direct"    # 仅直传
    STRATEGY_IMAGE_BED = "image_bed"  # 仅图床
    
    def __init__(self):
        # 默认策略（从配置读取）
        self.current_strategy = getattr(settings, 'image_strategy', self.STRATEGY_SMART)
        
        # 智能模式配置
        self.smart_direct_timeout = getattr(settings, 'smart_mode_direct_timeout', 10)
        self.smart_fallback_to_bed = getattr(settings, 'smart_mode_fallback_to_bed', True)
        self.smart_save_failed = getattr(settings, 'smart_mode_save_failed', True)
        
        # 统计信息
        self.stats = {
            'total_processed': 0,
            'direct_success': 0,
            'direct_failed': 0,
            'image_bed_success': 0,
            'image_bed_failed': 0,
            'saved_for_retry': 0
        }
        
        logger.info(f"✅ 图片处理策略管理器已初始化（策略: {self.current_strategy}）")
    
    def set_strategy(self, strategy: str):
        """
        设置当前策略
        
        Args:
            strategy: 策略类型
        """
        if strategy not in [self.STRATEGY_SMART, self.STRATEGY_DIRECT, self.STRATEGY_IMAGE_BED]:
            logger.error(f"无效的策略类型: {strategy}")
            return
        
        old_strategy = self.current_strategy
        self.current_strategy = strategy
        logger.info(f"图片处理策略已更改: {old_strategy} → {strategy}")
    
    async def process_image(self, image_url: str, cookies: Dict, 
                           platform: str = "discord") -> Optional[str]:
        """
        根据当前策略处理图片
        
        Args:
            image_url: 图片URL
            cookies: Cookie字典
            platform: 目标平台
            
        Returns:
            处理后的图片URL（可用于发送），失败返回None
        """
        self.stats['total_processed'] += 1
        
        if self.current_strategy == self.STRATEGY_SMART:
            return await self.process_image_smart(image_url, cookies, platform)
        elif self.current_strategy == self.STRATEGY_DIRECT:
            return await self.process_image_direct(image_url, cookies, platform)
        elif self.current_strategy == self.STRATEGY_IMAGE_BED:
            return await self.process_image_bed(image_url, cookies)
        else:
            logger.error(f"未知的策略: {self.current_strategy}")
            return None
    
    async def process_image_smart(self, image_url: str, cookies: Dict, 
                                  platform: str) -> Optional[str]:
        """
        智能模式处理图片
        
        流程：
        1. 尝试直传到目标平台
        2. 失败时使用图床（如果启用）
        3. 全部失败时保存本地供重试（如果启用）
        """
        logger.info(f"[智能模式] 开始处理图片: {image_url}")
        
        # 步骤1：尝试直传到目标平台
        try:
            logger.info("[智能模式] 步骤1: 尝试直传到目标平台...")
            
            result_url = await asyncio.wait_for(
                self._direct_upload(image_url, cookies, platform),
                timeout=self.smart_direct_timeout
            )
            
            if result_url:
                logger.info(f"[智能模式] ✅ 直传成功: {result_url}")
                self.stats['direct_success'] += 1
                return result_url
        except asyncio.TimeoutError:
            logger.warning(f"[智能模式] ⚠️ 直传超时（{self.smart_direct_timeout}秒）")
            self.stats['direct_failed'] += 1
        except Exception as e:
            logger.warning(f"[智能模式] ⚠️ 直传失败: {str(e)}")
            self.stats['direct_failed'] += 1
        
        # 步骤2：失败时使用图床
        if self.smart_fallback_to_bed:
            try:
                logger.info("[智能模式] 步骤2: 尝试使用图床...")
                
                result_url = await self._upload_to_image_bed(image_url, cookies)
                
                if result_url:
                    logger.info(f"[智能模式] ✅ 图床上传成功: {result_url}")
                    self.stats['image_bed_success'] += 1
                    return result_url
            except Exception as e:
                logger.warning(f"[智能模式] ⚠️ 图床上传失败: {str(e)}")
                self.stats['image_bed_failed'] += 1
        
        # 步骤3：全部失败时保存本地供重试
        if self.smart_save_failed:
            logger.info("[智能模式] 步骤3: 保存到本地失败队列...")
            await self._save_to_failed_queue(image_url, cookies, platform)
            self.stats['saved_for_retry'] += 1
        
        logger.error("[智能模式] ❌ 所有处理方式都失败了")
        return None
    
    async def process_image_direct(self, image_url: str, cookies: Dict, 
                                   platform: str) -> Optional[str]:
        """
        仅直传模式
        """
        logger.info(f"[仅直传] 处理图片: {image_url}")
        
        try:
            result_url = await self._direct_upload(image_url, cookies, platform)
            
            if result_url:
                logger.info(f"[仅直传] ✅ 成功: {result_url}")
                self.stats['direct_success'] += 1
                return result_url
            else:
                logger.error(f"[仅直传] ❌ 失败")
                self.stats['direct_failed'] += 1
                return None
        except Exception as e:
            logger.error(f"[仅直传] ❌ 异常: {str(e)}")
            self.stats['direct_failed'] += 1
            return None
    
    async def process_image_bed(self, image_url: str, cookies: Dict) -> Optional[str]:
        """
        仅图床模式
        """
        logger.info(f"[仅图床] 处理图片: {image_url}")
        
        try:
            result_url = await self._upload_to_image_bed(image_url, cookies)
            
            if result_url:
                logger.info(f"[仅图床] ✅ 成功: {result_url}")
                self.stats['image_bed_success'] += 1
                return result_url
            else:
                logger.error(f"[仅图床] ❌ 失败")
                self.stats['image_bed_failed'] += 1
                return None
        except Exception as e:
            logger.error(f"[仅图床] ❌ 异常: {str(e)}")
            self.stats['image_bed_failed'] += 1
            return None
    
    async def _direct_upload(self, image_url: str, cookies: Dict, 
                            platform: str) -> Optional[str]:
        """
        直接上传到目标平台
        
        注意：这是一个简化实现，实际需要调用各平台的上传API
        """
        # 先下载图片
        image_data = await image_processor.download_image(
            image_url,
            cookies=cookies,
            referer="https://www.kookapp.cn"
        )
        
        if not image_data:
            return None
        
        # 根据平台上传（这里简化处理，实际需要实现各平台的上传）
        if platform == "discord":
            # Discord可以直接发送图片二进制数据
            # 这里返回原URL，实际应该上传后返回新URL
            return image_url
        elif platform == "telegram":
            # Telegram也可以直接发送图片
            return image_url
        elif platform == "feishu":
            # 飞书需要先上传到飞书云存储
            return image_url
        else:
            return image_url
    
    async def _upload_to_image_bed(self, image_url: str, cookies: Dict) -> Optional[str]:
        """
        上传到内置图床
        """
        try:
            # 下载图片
            image_data = await image_processor.download_image(
                image_url,
                cookies=cookies,
                referer="https://www.kookapp.cn"
            )
            
            if not image_data:
                return None
            
            # 保存到图床并获取URL
            saved_path, token = await image_processor.save_image(image_data, generate_token=True)
            
            if not saved_path:
                return None
            
            # 生成图床URL
            image_bed_url = f"http://127.0.0.1:{settings.image_server_port}/images/{saved_path.name}?token={token}"
            
            return image_bed_url
        except Exception as e:
            logger.error(f"图床上传异常: {str(e)}")
            return None
    
    async def _save_to_failed_queue(self, image_url: str, cookies: Dict, platform: str):
        """
        保存到失败队列供后续重试
        """
        try:
            # 使用message_backup保存
            from ..utils.message_backup import message_backup
            
            failed_item = {
                "type": "failed_image",
                "image_url": image_url,
                "platform": platform,
                "timestamp": asyncio.get_event_loop().time(),
                "retry_count": 0
            }
            
            message_backup.save_message(failed_item)
            logger.info(f"图片已保存到失败队列: {image_url}")
        except Exception as e:
            logger.error(f"保存到失败队列异常: {str(e)}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.stats['total_processed']
        if total == 0:
            success_rate = 0
        else:
            success = self.stats['direct_success'] + self.stats['image_bed_success']
            success_rate = (success / total) * 100
        
        return {
            **self.stats,
            'success_rate': round(success_rate, 2),
            'current_strategy': self.current_strategy
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_processed': 0,
            'direct_success': 0,
            'direct_failed': 0,
            'image_bed_success': 0,
            'image_bed_failed': 0,
            'saved_for_retry': 0
        }
        logger.info("统计信息已重置")


# 创建全局实例
image_strategy = ImageStrategy()
