"""
媒体处理器（图片和附件）
从worker.py拆分出来，专注于媒体文件处理
"""
import asyncio
from typing import List, Dict, Any, Optional
from ..utils.structured_logger import logger, log_info, log_error
from ..utils.metrics import metrics, async_measure_time
from ..config import settings
from .image import image_processor, attachment_processor
from .file_security import file_security_checker


class MediaHandler:
    """媒体文件处理器"""
    
    async def process_images(
        self,
        image_urls: List[str],
        cookies: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        并行处理多张图片
        
        Args:
            image_urls: 图片URL列表
            cookies: Cookie字典
            
        Returns:
            处理后的图片信息列表
        """
        if not image_urls:
            return []
        
        log_info("开始并行处理图片", count=len(image_urls))
        
        # 创建并行任务
        tasks = [
            self._process_single_image(url, cookies)
            for url in image_urls
        ]
        
        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        processed_images = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                log_error("图片处理失败", url=image_urls[i], error=str(result))
                metrics.record_image_operation('process', 'failed')
            elif result:
                processed_images.append(result)
                metrics.record_image_operation('process', 'success')
        
        log_info("图片处理完成",
                success=len(processed_images),
                total=len(image_urls))
        
        return processed_images
    
    async def _process_single_image(
        self,
        url: str,
        cookies: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """
        处理单张图片
        
        Args:
            url: 图片URL
            cookies: Cookie字典
            
        Returns:
            处理后的图片信息
        """
        try:
            # 使用指标记录处理时间
            async with async_measure_time('image', 'download'):
                # 下载图片
                image_data = await image_processor.download_image(
                    url=url,
                    cookies=cookies,
                    referer='https://www.kookapp.cn'
                )
            
            if not image_data:
                log_error("图片下载失败", url=url)
                return None
            
            # 压缩图片（使用多进程池）
            loop = asyncio.get_event_loop()
            async with async_measure_time('image', 'compress'):
                compressed_data = await loop.run_in_executor(
                    image_processor.process_pool,
                    image_processor._compress_image_worker,
                    image_data,
                    settings.image_max_size_mb,
                    settings.image_compression_quality
                )
            
            # 保存并处理策略
            result = await image_processor.save_and_process_strategy(
                compressed_data=compressed_data,
                original_url=url,
                strategy=settings.image_strategy
            )
            
            return result
            
        except Exception as e:
            log_error("处理图片异常", url=url, error=str(e))
            raise
    
    async def process_attachments(
        self,
        file_attachments: List[Dict[str, Any]],
        cookies: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        并行处理附件文件
        
        Args:
            file_attachments: 附件列表
            cookies: Cookie字典
            
        Returns:
            处理后的附件信息列表
        """
        if not file_attachments:
            return []
        
        log_info("开始并行处理附件", count=len(file_attachments))
        
        # 创建并行任务
        tasks = [
            self._process_single_attachment(attachment, cookies)
            for attachment in file_attachments
        ]
        
        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        processed_attachments = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                log_error("附件处理失败",
                         filename=file_attachments[i].get('name'),
                         error=str(result))
            elif result:
                processed_attachments.append(result)
        
        log_info("附件处理完成",
                success=len(processed_attachments),
                total=len(file_attachments))
        
        return processed_attachments
    
    async def _process_single_attachment(
        self,
        attachment: Dict[str, Any],
        cookies: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """
        处理单个附件
        
        Args:
            attachment: 附件信息
            cookies: Cookie字典
            
        Returns:
            处理后的附件信息
        """
        try:
            url = attachment.get('url')
            filename = attachment.get('name', 'unknown')
            file_size_bytes = attachment.get('size', 0)
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            log_info("处理附件", filename=filename, size_mb=f"{file_size_mb:.2f}")
            
            # 文件安全检查
            is_safe, risk_level, reason = file_security_checker.is_safe_file(
                filename,
                file_size_bytes
            )
            
            if not is_safe:
                log_error("附件被安全拦截", filename=filename, reason=reason)
                return None
            
            if risk_level == "warning":
                log_info("附件安全警告", filename=filename, reason=reason)
            
            # 检查文件大小
            if file_size_mb > 50:
                log_error("附件过大", filename=filename, size_mb=file_size_mb)
                return None
            
            # 下载附件
            local_path = await attachment_processor.download_attachment(
                url=url,
                filename=filename,
                cookies=cookies,
                referer='https://www.kookapp.cn'
            )
            
            if local_path:
                log_info("附件下载成功", filename=filename)
                return {
                    'original_url': url,
                    'filename': filename,
                    'local_path': local_path,
                    'size': file_size_bytes,
                    'type': attachment.get('type', 'application/octet-stream')
                }
            else:
                log_error("附件下载失败", filename=filename)
                return None
                
        except Exception as e:
            log_error("处理附件异常",
                     filename=attachment.get('name'),
                     error=str(e))
            raise
