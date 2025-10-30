"""
✅ P0-3深度优化: Redis自动下载安装器
支持从多个镜像源自动下载并安装Redis
"""
import os
import sys
import platform
import asyncio
import aiohttp
import zipfile
import tarfile
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Callable, Dict, Any
from .logger import logger


class RedisAutoInstaller:
    """Redis自动下载安装器"""
    
    # Redis下载源（多个镜像，按优先级）
    REDIS_DOWNLOAD_SOURCES = {
        "windows": [
            {
                "name": "GitHub tporadowski/redis",
                "version": "5.0.14.1",
                "url": "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip",
                "size_mb": 5.2,
                "type": "zip"
            },
            {
                "name": "GitHub microsoftarchive/redis",
                "version": "3.2.100",
                "url": "https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip",
                "size_mb": 3.8,
                "type": "zip"
            }
        ],
        "linux": [
            {
                "name": "Redis.io Official",
                "version": "stable",
                "url": "https://download.redis.io/redis-stable.tar.gz",
                "size_mb": 2.5,
                "type": "tar.gz",
                "compile": True  # 需要编译
            },
            {
                "name": "GitHub redis/redis",
                "version": "7.2.0",
                "url": "https://github.com/redis/redis/archive/refs/tags/7.2.0.tar.gz",
                "size_mb": 3.1,
                "type": "tar.gz",
                "compile": True
            }
        ],
        "darwin": [  # macOS
            {
                "name": "Redis.io Official",
                "version": "stable",
                "url": "https://download.redis.io/redis-stable.tar.gz",
                "size_mb": 2.5,
                "type": "tar.gz",
                "compile": True
            }
        ]
    }
    
    def __init__(self, install_dir: Path):
        """
        初始化安装器
        
        Args:
            install_dir: Redis安装目录
        """
        self.install_dir = Path(install_dir)
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        self.system = platform.system().lower()
        self.download_progress_callback: Optional[Callable] = None
        
        # 临时下载目录
        self.download_dir = self.install_dir / "download"
        self.download_dir.mkdir(exist_ok=True)
        
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        设置下载进度回调函数
        
        Args:
            callback: 回调函数，接收进度信息字典
                     {
                         "status": "downloading" | "extracting" | "compiling" | "complete",
                         "progress": 0-100,
                         "message": "状态消息",
                         "current_mb": 当前下载MB,
                         "total_mb": 总大小MB
                     }
        """
        self.download_progress_callback = callback
        
    def _emit_progress(self, status: str, progress: int, message: str, **kwargs):
        """触发进度回调"""
        if self.download_progress_callback:
            try:
                self.download_progress_callback({
                    "status": status,
                    "progress": progress,
                    "message": message,
                    **kwargs
                })
            except Exception as e:
                logger.error(f"进度回调失败: {e}")
    
    async def download_and_install(self) -> Tuple[bool, str]:
        """
        下载并安装Redis
        
        Returns:
            (success, message)
        """
        try:
            # 获取当前系统的下载源
            sources = self.REDIS_DOWNLOAD_SOURCES.get(self.system)
            
            if not sources:
                return False, f"不支持的操作系统: {self.system}"
            
            logger.info(f"🌐 系统: {self.system}，共有 {len(sources)} 个下载源")
            
            # 尝试每个下载源
            for idx, source in enumerate(sources, 1):
                logger.info(f"📥 尝试下载源 {idx}/{len(sources)}: {source['name']}")
                self._emit_progress("downloading", 0, f"连接 {source['name']}...")
                
                try:
                    # 下载Redis
                    download_file = await self._download_from_source(source)
                    
                    if not download_file:
                        logger.warning(f"从 {source['name']} 下载失败")
                        continue
                    
                    logger.info(f"✅ 下载完成: {download_file}")
                    
                    # 解压
                    self._emit_progress("extracting", 80, "正在解压文件...")
                    extract_success = await self._extract_file(download_file, source)
                    
                    if not extract_success:
                        logger.warning(f"解压失败: {download_file}")
                        continue
                    
                    logger.info("✅ 解压完成")
                    
                    # 如果需要编译（Linux/macOS）
                    if source.get("compile", False):
                        self._emit_progress("compiling", 85, "正在编译Redis...")
                        compile_success = await self._compile_redis()
                        
                        if not compile_success:
                            logger.warning("编译失败")
                            continue
                        
                        logger.info("✅ 编译完成")
                    
                    # 清理临时文件
                    self._cleanup_temp_files(download_file)
                    
                    # 验证安装
                    if self._verify_installation():
                        self._emit_progress("complete", 100, "Redis安装成功")
                        return True, f"Redis已从 {source['name']} 安装成功"
                    else:
                        logger.warning("安装验证失败")
                        continue
                    
                except Exception as e:
                    logger.error(f"从 {source['name']} 安装失败: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue
            
            # 所有源都失败
            return False, "所有下载源均失败，请检查网络连接或手动安装Redis"
            
        except Exception as e:
            logger.error(f"Redis安装异常: {str(e)}")
            return False, f"安装异常: {str(e)}"
    
    async def _download_from_source(self, source: Dict[str, Any]) -> Optional[Path]:
        """
        从指定源下载文件
        
        Args:
            source: 下载源信息
            
        Returns:
            下载的文件路径，失败返回None
        """
        try:
            url = source["url"]
            filename = Path(url).name
            download_path = self.download_dir / filename
            
            # 如果已经下载过，先删除
            if download_path.exists():
                download_path.unlink()
            
            logger.info(f"📥 下载: {url}")
            logger.info(f"💾 保存到: {download_path}")
            
            # 下载文件
            timeout = aiohttp.ClientTimeout(total=300, connect=30)  # 5分钟超时
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"下载失败: HTTP {response.status}")
                        return None
                    
                    # 获取文件大小
                    total_size = int(response.headers.get('content-length', 0))
                    total_mb = total_size / (1024 * 1024) if total_size else source.get("size_mb", 0)
                    
                    logger.info(f"📦 文件大小: {total_mb:.2f} MB")
                    
                    # 下载并显示进度
                    downloaded = 0
                    chunk_size = 8192
                    
                    with open(download_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 更新进度
                            if total_size > 0:
                                progress = int((downloaded / total_size) * 70)  # 下载占70%进度
                                current_mb = downloaded / (1024 * 1024)
                                
                                self._emit_progress(
                                    "downloading",
                                    progress,
                                    f"下载中: {current_mb:.1f}/{total_mb:.1f} MB",
                                    current_mb=current_mb,
                                    total_mb=total_mb
                                )
                    
                    logger.info(f"✅ 下载完成: {download_path}")
                    return download_path
                    
        except asyncio.TimeoutError:
            logger.error("下载超时")
            return None
        except Exception as e:
            logger.error(f"下载异常: {str(e)}")
            return None
    
    async def _extract_file(self, file_path: Path, source: Dict[str, Any]) -> bool:
        """
        解压下载的文件
        
        Args:
            file_path: 下载的文件路径
            source: 下载源信息
            
        Returns:
            是否成功
        """
        try:
            file_type = source.get("type", "")
            
            logger.info(f"📦 开始解压: {file_path} (类型: {file_type})")
            
            if file_type == "zip":
                # 解压ZIP
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # 获取压缩包内的文件列表
                    members = zip_ref.namelist()
                    
                    # 如果有顶层目录，提取到install_dir
                    # 否则直接提取
                    has_top_dir = len(set(m.split('/')[0] for m in members if '/' in m)) == 1
                    
                    if has_top_dir:
                        # 解压到临时目录，然后移动文件
                        temp_extract = self.download_dir / "temp_extract"
                        temp_extract.mkdir(exist_ok=True)
                        
                        zip_ref.extractall(temp_extract)
                        
                        # 找到顶层目录
                        top_dir = next(temp_extract.iterdir())
                        
                        # 移动文件到install_dir
                        for item in top_dir.iterdir():
                            dest = self.install_dir / item.name
                            if dest.exists():
                                if dest.is_dir():
                                    shutil.rmtree(dest)
                                else:
                                    dest.unlink()
                            shutil.move(str(item), str(dest))
                        
                        # 清理临时目录
                        shutil.rmtree(temp_extract)
                    else:
                        # 直接解压到install_dir
                        zip_ref.extractall(self.install_dir)
                    
                    logger.info(f"✅ ZIP解压成功，共 {len(members)} 个文件")
                    
            elif file_type == "tar.gz":
                # 解压tar.gz
                with tarfile.open(file_path, 'r:gz') as tar_ref:
                    members = tar_ref.getmembers()
                    
                    # 解压到临时目录
                    temp_extract = self.download_dir / "temp_extract"
                    temp_extract.mkdir(exist_ok=True)
                    
                    tar_ref.extractall(temp_extract)
                    
                    # 找到顶层目录（通常是redis-x.x.x）
                    top_dirs = [d for d in temp_extract.iterdir() if d.is_dir()]
                    
                    if top_dirs:
                        source_dir = top_dirs[0]
                        
                        # 移动src目录到install_dir
                        src_dir = source_dir / "src"
                        if src_dir.exists():
                            # 复制src内容到install_dir
                            for item in source_dir.iterdir():
                                dest = self.install_dir / item.name
                                if dest.exists():
                                    if dest.is_dir():
                                        shutil.rmtree(dest)
                                    else:
                                        dest.unlink()
                                
                                if item.is_dir():
                                    shutil.copytree(item, dest)
                                else:
                                    shutil.copy2(item, dest)
                        
                        # 清理临时目录
                        shutil.rmtree(temp_extract)
                        
                        logger.info(f"✅ TAR.GZ解压成功，共 {len(members)} 个文件")
                    else:
                        logger.error("未找到顶层目录")
                        return False
            else:
                logger.error(f"不支持的文件类型: {file_type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"解压失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def _compile_redis(self) -> bool:
        """
        编译Redis（Linux/macOS）
        
        Returns:
            是否成功
        """
        try:
            # 检查是否有Makefile
            makefile = self.install_dir / "Makefile"
            if not makefile.exists():
                logger.warning("未找到Makefile，跳过编译")
                return True
            
            logger.info("🔨 开始编译Redis...")
            
            # 执行make
            process = await asyncio.create_subprocess_exec(
                'make',
                cwd=str(self.install_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=180)
            
            if process.returncode == 0:
                logger.info("✅ Redis编译成功")
                
                # 复制编译好的可执行文件到根目录
                src_dir = self.install_dir / "src"
                if src_dir.exists():
                    for binary in ["redis-server", "redis-cli"]:
                        src_file = src_dir / binary
                        if src_file.exists():
                            dest_file = self.install_dir / binary
                            shutil.copy2(src_file, dest_file)
                            os.chmod(dest_file, 0o755)
                            logger.info(f"✅ 复制: {binary}")
                
                return True
            else:
                error_msg = stderr.decode('utf-8', errors='ignore')
                logger.error(f"编译失败: {error_msg}")
                return False
                
        except asyncio.TimeoutError:
            logger.error("编译超时（3分钟）")
            return False
        except Exception as e:
            logger.error(f"编译异常: {str(e)}")
            return False
    
    def _verify_installation(self) -> bool:
        """
        验证Redis安装
        
        Returns:
            是否成功安装
        """
        try:
            # 检查redis-server是否存在
            if self.system == "windows":
                redis_server = self.install_dir / "redis-server.exe"
            else:
                redis_server = self.install_dir / "redis-server"
            
            if not redis_server.exists():
                logger.error(f"未找到redis-server: {redis_server}")
                return False
            
            # 检查是否可执行
            if not os.access(redis_server, os.X_OK):
                logger.warning(f"redis-server不可执行，尝试添加执行权限")
                try:
                    os.chmod(redis_server, 0o755)
                except Exception as e:
                    logger.error(f"添加执行权限失败: {e}")
                    return False
            
            logger.info(f"✅ Redis验证成功: {redis_server}")
            return True
            
        except Exception as e:
            logger.error(f"验证安装失败: {str(e)}")
            return False
    
    def _cleanup_temp_files(self, download_file: Path):
        """清理临时文件"""
        try:
            if download_file.exists():
                download_file.unlink()
                logger.info(f"🗑️ 清理临时文件: {download_file}")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {e}")
    
    async def check_and_install_if_needed(self) -> Tuple[bool, str]:
        """
        检查Redis是否已安装，如未安装则自动下载
        
        Returns:
            (success, message)
        """
        # 检查是否已安装
        if self._verify_installation():
            return True, "Redis已安装"
        
        # 自动下载安装
        logger.info("Redis未安装，开始自动下载...")
        return await self.download_and_install()


# 便捷函数
async def ensure_redis_installed(install_dir: Path, progress_callback: Optional[Callable] = None) -> Tuple[bool, str]:
    """
    确保Redis已安装
    
    Args:
        install_dir: 安装目录
        progress_callback: 进度回调函数
        
    Returns:
        (success, message)
    """
    installer = RedisAutoInstaller(install_dir)
    
    if progress_callback:
        installer.set_progress_callback(progress_callback)
    
    return await installer.check_and_install_if_needed()
