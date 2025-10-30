"""
✅ P0-4深度优化: Playwright/Chromium自动下载器
支持实时进度显示
"""
import asyncio
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Callable, Dict, Any
from .logger import logger


class PlaywrightDownloader:
    """Playwright/Chromium下载器"""
    
    def __init__(self):
        self.progress_callback: Optional[Callable] = None
        
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """设置进度回调"""
        self.progress_callback = callback
        
    def _emit_progress(self, status: str, progress: int, message: str):
        """触发进度回调"""
        if self.progress_callback:
            try:
                self.progress_callback({
                    "status": status,
                    "progress": progress,
                    "message": message
                })
            except Exception as e:
                logger.error(f"进度回调失败: {e}")
    
    async def check_chromium_installed(self) -> bool:
        """检查Chromium是否已安装"""
        try:
            from playwright.async_api import async_playwright
            
            playwright = await async_playwright().start()
            try:
                browser = await asyncio.wait_for(
                    playwright.chromium.launch(headless=True),
                    timeout=3.0
                )
                await browser.close()
                return True
            except:
                return False
            finally:
                await playwright.stop()
        except:
            return False
    
    async def install_chromium(self) -> Tuple[bool, str]:
        """
        安装Playwright Chromium
        
        Returns:
            (success, message)
        """
        try:
            logger.info("📥 开始下载Chromium浏览器...")
            self._emit_progress("downloading", 0, "初始化下载...")
            
            # 执行playwright install chromium
            process = await asyncio.create_subprocess_exec(
                'playwright',
                'install',
                'chromium',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            # 读取输出并更新进度
            progress = 0
            async for line in process.stdout:
                line_text = line.decode('utf-8', errors='ignore').strip()
                logger.info(f"Playwright: {line_text}")
                
                # 解析进度
                if 'Downloading' in line_text:
                    progress = min(progress + 10, 90)
                    self._emit_progress("downloading", progress, line_text)
                elif 'Installing' in line_text:
                    progress = 95
                    self._emit_progress("installing", progress, line_text)
            
            await process.wait()
            
            if process.returncode == 0:
                self._emit_progress("complete", 100, "Chromium安装成功")
                logger.info("✅ Chromium安装成功")
                return True, "Chromium安装成功"
            else:
                logger.error("❌ Chromium安装失败")
                return False, "Chromium安装失败"
                
        except Exception as e:
            logger.error(f"Chromium安装异常: {str(e)}")
            return False, f"安装异常: {str(e)}"
    
    async def ensure_chromium_available(self) -> Tuple[bool, str]:
        """
        确保Chromium可用
        
        Returns:
            (success, message)
        """
        # 检查是否已安装
        if await self.check_chromium_installed():
            return True, "Chromium已安装"
        
        # 自动安装
        logger.info("Chromium未安装，开始自动下载...")
        return await self.install_chromium()


# 便捷函数
async def ensure_chromium_available(progress_callback: Optional[Callable] = None) -> Tuple[bool, str]:
    """确保Chromium可用"""
    downloader = PlaywrightDownloader()
    
    if progress_callback:
        downloader.set_progress_callback(progress_callback)
    
    return await downloader.ensure_chromium_available()
