#!/usr/bin/env python3
"""
KOOK消息转发系统 - 统一构建脚本
版本: v6.3.0
功能: 一键生成跨平台安装包（Windows/macOS/Linux）
"""

import os
import sys
import platform
import subprocess
import shutil
import json
from pathlib import Path
from typing import List, Optional
import argparse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('build_unified.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnifiedBuilder:
    """统一构建器"""
    
    def __init__(self, target_platform: str = None, clean: bool = False):
        self.root_dir = Path(__file__).parent.parent
        self.build_dir = self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.resources_dir = self.build_dir / "resources"
        
        # 目标平台
        self.target_platform = target_platform or platform.system().lower()
        self.clean_build = clean
        
        # 版本信息
        self.version = "6.3.0"
        self.app_name = "KOOK消息转发系统"
        
        logger.info(f"初始化构建器: 平台={self.target_platform}, 版本={self.version}")
    
    def clean(self):
        """清理构建目录"""
        logger.info("🧹 清理构建目录...")
        
        dirs_to_clean = [
            self.dist_dir,
            self.build_dir / "backend_dist",
            self.frontend_dir / "dist",
            self.frontend_dir / "dist-electron",
        ]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                logger.info(f"  删除: {dir_path}")
                shutil.rmtree(dir_path)
        
        logger.info("✅ 清理完成")
    
    def prepare_resources(self):
        """准备资源文件（Redis、Chromium等）"""
        logger.info("📦 准备资源文件...")
        
        self.resources_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 准备Redis
        logger.info("  准备Redis...")
        self._prepare_redis()
        
        # 2. 准备Chromium（Playwright）
        logger.info("  准备Chromium...")
        self._prepare_chromium()
        
        # 3. 复制配置模板
        logger.info("  复制配置模板...")
        self._prepare_config_templates()
        
        logger.info("✅ 资源文件准备完成")
    
    def _prepare_redis(self):
        """准备Redis二进制文件"""
        redis_dir = self.resources_dir / "redis"
        redis_dir.mkdir(parents=True, exist_ok=True)
        
        # 根据平台复制Redis二进制文件
        if self.target_platform == "windows":
            # Windows: 使用预编译的redis-server.exe
            redis_source = self.root_dir / "redis" / "redis-server.exe"
            if redis_source.exists():
                shutil.copy(redis_source, redis_dir / "redis-server.exe")
                logger.info("    ✓ Redis for Windows 已复制")
            else:
                logger.warning("    ⚠️ 未找到redis-server.exe，将在运行时下载")
                # 创建下载脚本
                self._create_redis_download_script(redis_dir)
        
        elif self.target_platform == "darwin":
            # macOS: 可以使用Homebrew安装或静态编译版本
            redis_source = self.root_dir / "redis" / "redis-server-macos"
            if redis_source.exists():
                shutil.copy(redis_source, redis_dir / "redis-server")
                os.chmod(redis_dir / "redis-server", 0o755)
                logger.info("    ✓ Redis for macOS 已复制")
            else:
                logger.warning("    ⚠️ 未找到redis-server-macos")
        
        elif self.target_platform == "linux":
            # Linux: 静态编译版本
            redis_source = self.root_dir / "redis" / "redis-server-linux"
            if redis_source.exists():
                shutil.copy(redis_source, redis_dir / "redis-server")
                os.chmod(redis_dir / "redis-server", 0o755)
                logger.info("    ✓ Redis for Linux 已复制")
            else:
                logger.warning("    ⚠️ 未找到redis-server-linux")
        
        # 复制Redis配置文件
        redis_conf = self.root_dir / "redis" / "redis.conf"
        if redis_conf.exists():
            shutil.copy(redis_conf, redis_dir / "redis.conf")
    
    def _create_redis_download_script(self, redis_dir: Path):
        """创建Redis自动下载脚本（Windows）"""
        download_script = redis_dir / "download_redis.py"
        
        script_content = '''
"""自动下载Redis for Windows"""
import urllib.request
import zipfile
import os
from pathlib import Path

def download_redis():
    redis_url = "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
    zip_path = Path(__file__).parent / "redis.zip"
    
    print("正在下载Redis...")
    urllib.request.urlretrieve(redis_url, zip_path)
    
    print("正在解压...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(Path(__file__).parent)
    
    os.remove(zip_path)
    print("Redis下载完成！")

if __name__ == "__main__":
    download_redis()
'''
        
        download_script.write_text(script_content)
    
    def _prepare_chromium(self):
        """准备Chromium（Playwright）"""
        chromium_dir = self.resources_dir / "chromium"
        chromium_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建Playwright安装脚本
        install_script = chromium_dir / "install_chromium.py"
        
        script_content = '''
"""自动安装Playwright Chromium"""
import subprocess
import sys
import os

def install_chromium():
    print("=" * 60)
    print("正在安装Chromium浏览器...")
    print("这可能需要几分钟时间，请耐心等待...")
    print("=" * 60)
    
    try:
        # 安装playwright
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        
        # 安装chromium
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        
        print("✅ Chromium安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Chromium安装失败: {e}")
        return False

if __name__ == "__main__":
    success = install_chromium()
    sys.exit(0 if success else 1)
'''
        
        install_script.write_text(script_content)
        
        logger.info("    ✓ Chromium安装脚本已创建")
    
    def _prepare_config_templates(self):
        """准备配置模板"""
        templates_dir = self.resources_dir / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # .env模板
        env_template = templates_dir / ".env.template"
        env_template.write_text("""
# KOOK消息转发系统配置文件
# 复制此文件为.env并填写配置

# API配置
API_HOST=127.0.0.1
API_PORT=9527

# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# 图床配置
IMAGE_SERVER_PORT=9528
IMAGE_MAX_SIZE_GB=10
IMAGE_CLEANUP_DAYS=7

# 日志配置
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=3

# 安全配置
REQUIRE_PASSWORD=true

# 邮件配置（可选）
SMTP_ENABLED=false
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-password
# SMTP_FROM_EMAIL=your-email@gmail.com

# 验证码配置（可选）
# CAPTCHA_2CAPTCHA_API_KEY=your-2captcha-api-key
""")
        
        logger.info("    ✓ 配置模板已创建")
    
    def build_backend(self):
        """构建后端（PyInstaller）"""
        logger.info("🐍 构建Python后端...")
        
        # 切换到backend目录
        os.chdir(self.backend_dir)
        
        # 创建PyInstaller spec文件
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../build/resources', 'resources'),
        ('app', 'app'),
    ],
    hiddenimports=[
        'playwright',
        'aiosqlite',
        'aioredis',
        'aiohttp',
        'orjson',
        'cryptography',
        'PIL',
        'discord_webhook',
        'python_telegram_bot',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='kook-forwarder-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='kook-forwarder-backend',
)
'''
        
        spec_file = self.backend_dir / "kook-forwarder.spec"
        spec_file.write_text(spec_content)
        
        # 运行PyInstaller
        logger.info("  运行PyInstaller...")
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "kook-forwarder.spec", "--clean"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ PyInstaller失败: {result.stderr}")
            return False
        
        logger.info("✅ 后端构建完成")
        
        # 切换回根目录
        os.chdir(self.root_dir)
        return True
    
    def build_frontend(self):
        """构建前端（Electron）"""
        logger.info("⚛️ 构建Electron前端...")
        
        # 切换到frontend目录
        os.chdir(self.frontend_dir)
        
        # 1. 安装依赖
        logger.info("  安装npm依赖...")
        result = subprocess.run(["npm", "install"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"❌ npm install失败: {result.stderr}")
            return False
        
        # 2. 构建Vue应用
        logger.info("  构建Vue应用...")
        result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"❌ Vue构建失败: {result.stderr}")
            return False
        
        # 3. 打包Electron
        logger.info("  打包Electron应用...")
        
        if self.target_platform == "windows":
            build_cmd = ["npm", "run", "electron:build:win"]
        elif self.target_platform == "darwin":
            build_cmd = ["npm", "run", "electron:build:mac"]
        elif self.target_platform == "linux":
            build_cmd = ["npm", "run", "electron:build:linux"]
        else:
            build_cmd = ["npm", "run", "electron:build"]
        
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"❌ Electron打包失败: {result.stderr}")
            return False
        
        logger.info("✅ 前端构建完成")
        
        # 切换回根目录
        os.chdir(self.root_dir)
        return True
    
    def package_installer(self):
        """打包最终安装程序"""
        logger.info("📦 打包安装程序...")
        
        # 创建最终dist目录
        final_dist = self.dist_dir / f"v{self.version}"
        final_dist.mkdir(parents=True, exist_ok=True)
        
        # 复制Electron打包结果
        electron_dist = self.frontend_dir / "dist-electron"
        
        if self.target_platform == "windows":
            installer_name = f"KOOK-Forwarder-Setup-{self.version}.exe"
            source = electron_dist / installer_name
            if source.exists():
                shutil.copy(source, final_dist / installer_name)
                logger.info(f"  ✓ 已复制: {installer_name}")
        
        elif self.target_platform == "darwin":
            installer_name = f"KOOK-Forwarder-{self.version}.dmg"
            source = electron_dist / installer_name
            if source.exists():
                shutil.copy(source, final_dist / installer_name)
                logger.info(f"  ✓ 已复制: {installer_name}")
        
        elif self.target_platform == "linux":
            installer_name = f"KOOK-Forwarder-{self.version}.AppImage"
            source = electron_dist / installer_name
            if source.exists():
                shutil.copy(source, final_dist / installer_name)
                logger.info(f"  ✓ 已复制: {installer_name}")
        
        # 生成校验和
        self._generate_checksums(final_dist)
        
        logger.info("✅ 安装程序打包完成")
        logger.info(f"📍 输出目录: {final_dist}")
    
    def _generate_checksums(self, dist_dir: Path):
        """生成文件校验和"""
        import hashlib
        
        checksums = {}
        
        for file in dist_dir.glob("*"):
            if file.is_file() and file.suffix in ['.exe', '.dmg', '.AppImage']:
                logger.info(f"  计算校验和: {file.name}")
                
                sha256 = hashlib.sha256()
                with open(file, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)
                
                checksums[file.name] = {
                    'sha256': sha256.hexdigest(),
                    'size_mb': file.stat().st_size / (1024 * 1024)
                }
        
        # 保存校验和
        checksums_file = dist_dir / "checksums.json"
        with open(checksums_file, 'w', encoding='utf-8') as f:
            json.dump(checksums, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  ✓ 校验和已保存到: checksums.json")
    
    def build_all(self):
        """执行完整构建流程"""
        logger.info("=" * 60)
        logger.info(f"🚀 开始构建 {self.app_name} v{self.version}")
        logger.info(f"目标平台: {self.target_platform}")
        logger.info("=" * 60)
        
        try:
            # 1. 清理
            if self.clean_build:
                self.clean()
            
            # 2. 准备资源
            self.prepare_resources()
            
            # 3. 构建后端
            if not self.build_backend():
                logger.error("❌ 后端构建失败")
                return False
            
            # 4. 构建前端
            if not self.build_frontend():
                logger.error("❌ 前端构建失败")
                return False
            
            # 5. 打包安装程序
            self.package_installer()
            
            logger.info("=" * 60)
            logger.info("🎉 构建完成！")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 构建过程出错: {str(e)}", exc_info=True)
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='KOOK消息转发系统 - 统一构建脚本')
    parser.add_argument(
        '--platform',
        choices=['windows', 'darwin', 'linux'],
        help='目标平台（默认：当前平台）'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='构建前清理所有构建目录'
    )
    
    args = parser.parse_args()
    
    builder = UnifiedBuilder(
        target_platform=args.platform,
        clean=args.clean
    )
    
    success = builder.build_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
