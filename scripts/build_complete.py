#!/usr/bin/env python3
"""
KOOK消息转发系统 - 完整打包脚本
✅ P1-1优化：一键打包所有组件

功能：
1. 打包Python后端（PyInstaller）
2. 下载并打包Chromium浏览器
3. 打包Redis服务
4. 打包Electron前端
5. 生成安装包（Windows/macOS/Linux）

使用方法：
    python scripts/build_complete.py [--platform all|windows|macos|linux]
"""

import os
import sys
import subprocess
import platform
import shutil
import requests
import zipfile
import tarfile
from pathlib import Path
from typing import Optional
import argparse
import json

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(msg):
    print(f"{Colors.BLUE}{Colors.BOLD}[步骤] {msg}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.HEADER}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{Colors.END}\n")

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
REDIS_DIR = PROJECT_ROOT / "redis"

# 确保目录存在
DIST_DIR.mkdir(exist_ok=True)
BUILD_DIR.mkdir(exist_ok=True)


def get_version():
    """从VERSION文件读取版本号"""
    version_file = PROJECT_ROOT / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "1.0.0"


def run_command(cmd, cwd=None, shell=False):
    """运行命令并实时输出"""
    print(f"  执行命令: {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    
    try:
        if isinstance(cmd, str) and not shell:
            cmd = cmd.split()
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            shell=shell,
            universal_newlines=True
        )
        
        for line in process.stdout:
            print(f"  {line.rstrip()}")
        
        process.wait()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)
        
        return True
    except Exception as e:
        print_error(f"命令执行失败: {e}")
        return False


def download_chromium():
    """下载Chromium浏览器"""
    print_step("下载Chromium浏览器...")
    
    # 使用Playwright自动下载
    try:
        print("  安装Playwright浏览器...")
        run_command([
            sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"
        ])
        print_success("Chromium下载成功")
        return True
    except Exception as e:
        print_error(f"Chromium下载失败: {e}")
        return False


def package_redis():
    """下载并打包Redis"""
    print_step("准备Redis...")
    
    system = platform.system()
    
    if system == "Windows":
        # Windows使用预编译的Redis
        redis_url = "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
        redis_zip = DIST_DIR / "redis-windows.zip"
        
        if not redis_zip.exists():
            print("  下载Redis for Windows...")
            try:
                response = requests.get(redis_url, stream=True)
                with open(redis_zip, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print_success("Redis下载完成")
            except Exception as e:
                print_error(f"Redis下载失败: {e}")
                return False
        
        # 解压Redis
        redis_extract_dir = REDIS_DIR
        redis_extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(redis_zip, 'r') as zip_ref:
            zip_ref.extractall(redis_extract_dir)
        
        print_success("Redis准备完成")
        return True
        
    elif system == "Linux":
        # Linux使用apt或从源码编译
        print("  检查Redis是否已安装...")
        try:
            subprocess.run(["redis-server", "--version"], check=True, capture_output=True)
            print_success("Redis已安装")
            return True
        except:
            print_warning("Redis未安装，尝试从包管理器安装...")
            try:
                subprocess.run(["sudo", "apt-get", "install", "-y", "redis-server"], check=True)
                print_success("Redis安装成功")
                return True
            except:
                print_error("Redis安装失败，请手动安装")
                return False
                
    elif system == "Darwin":  # macOS
        # macOS使用Homebrew
        print("  检查Redis是否已安装...")
        try:
            subprocess.run(["redis-server", "--version"], check=True, capture_output=True)
            print_success("Redis已安装")
            return True
        except:
            print_warning("Redis未安装，尝试通过Homebrew安装...")
            try:
                subprocess.run(["brew", "install", "redis"], check=True)
                print_success("Redis安装成功")
                return True
            except:
                print_error("Redis安装失败，请确保已安装Homebrew")
                return False
    
    return True


def build_backend():
    """打包Python后端"""
    print_step("打包Python后端...")
    
    # 检查依赖
    print("  检查Python依赖...")
    requirements_file = BACKEND_DIR / "requirements.txt"
    if requirements_file.exists():
        run_command([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
    
    # 安装PyInstaller
    print("  安装PyInstaller...")
    run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 运行PyInstaller
    print("  使用PyInstaller打包...")
    spec_file = BUILD_DIR / "pyinstaller.spec"
    
    if not spec_file.exists():
        print_warning("pyinstaller.spec不存在，使用默认配置")
        # 创建基础spec文件
        create_default_spec()
    
    success = run_command([
        sys.executable, "-m", "PyInstaller",
        str(spec_file),
        "--clean",
        "--noconfirm"
    ], cwd=PROJECT_ROOT)
    
    if success:
        print_success("后端打包成功")
        return True
    else:
        print_error("后端打包失败")
        return False


def create_default_spec():
    """创建默认的PyInstaller spec文件"""
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['backend/app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/data', 'data'),
        ('redis', 'redis'),
    ],
    hiddenimports=[
        'playwright',
        'fastapi',
        'uvicorn',
        'pydantic',
        'aiohttp',
    ],
    hookspath=[],
    hooksconfig={},
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='kook-forwarder-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    spec_file = BUILD_DIR / "pyinstaller.spec"
    spec_file.write_text(spec_content)
    print_success("已创建默认spec文件")


def build_frontend():
    """打包Electron前端"""
    print_step("打包Electron前端...")
    
    # 检查Node.js
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
    except:
        print_error("Node.js未安装，请先安装Node.js")
        return False
    
    # 安装依赖
    print("  安装npm依赖...")
    if not run_command(["npm", "install"], cwd=FRONTEND_DIR):
        return False
    
    # 构建Vue应用
    print("  构建Vue应用...")
    if not run_command(["npm", "run", "build"], cwd=FRONTEND_DIR):
        return False
    
    # 打包Electron
    print("  打包Electron应用...")
    system = platform.system()
    
    if system == "Windows":
        cmd = ["npm", "run", "electron:build:win"]
    elif system == "Darwin":
        cmd = ["npm", "run", "electron:build:mac"]
    else:
        cmd = ["npm", "run", "electron:build:linux"]
    
    if run_command(cmd, cwd=FRONTEND_DIR):
        print_success("前端打包成功")
        return True
    else:
        print_error("前端打包失败")
        return False


def create_installer():
    """创建安装程序"""
    print_step("创建安装程序...")
    
    version = get_version()
    system = platform.system()
    
    # 移动文件到dist目录
    frontend_dist = FRONTEND_DIR / "dist-electron"
    
    if frontend_dist.exists():
        # 复制到主dist目录
        for file in frontend_dist.iterdir():
            if file.is_file():
                dest = DIST_DIR / file.name
                shutil.copy2(file, dest)
                print(f"  复制: {file.name}")
        
        print_success(f"安装包已生成在: {DIST_DIR}")
        
        # 列出生成的文件
        print("\n生成的安装包:")
        for file in DIST_DIR.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  📦 {file.name} ({size_mb:.2f} MB)")
        
        return True
    else:
        print_error("未找到打包结果")
        return False


def clean_build():
    """清理构建文件"""
    print_step("清理旧的构建文件...")
    
    dirs_to_clean = [
        PROJECT_ROOT / "dist",
        PROJECT_ROOT / "build",
        FRONTEND_DIR / "dist",
        FRONTEND_DIR / "dist-electron",
        BACKEND_DIR / "dist",
        BACKEND_DIR / "build",
    ]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  删除: {dir_path}")
    
    print_success("清理完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='KOOK消息转发系统 - 完整打包脚本')
    parser.add_argument(
        '--platform',
        choices=['all', 'windows', 'macos', 'linux'],
        default='current',
        help='目标平台（默认：当前平台）'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='打包前清理旧文件'
    )
    parser.add_argument(
        '--skip-backend',
        action='store_true',
        help='跳过后端打包'
    )
    parser.add_argument(
        '--skip-frontend',
        action='store_true',
        help='跳过前端打包'
    )
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    version = get_version()
    print_header(f"KOOK消息转发系统 v{version} - 完整打包脚本")
    
    print(f"目标平台: {args.platform}")
    print(f"当前系统: {platform.system()} {platform.machine()}")
    print(f"Python版本: {sys.version}")
    print()
    
    # 清理旧文件
    if args.clean:
        clean_build()
    
    # 执行打包流程
    success = True
    
    # 1. 下载Chromium
    print_header("第1步：准备Chromium浏览器")
    if not download_chromium():
        print_warning("Chromium下载失败，继续...")
    
    # 2. 准备Redis
    print_header("第2步：准备Redis服务")
    if not package_redis():
        print_warning("Redis准备失败，继续...")
    
    # 3. 打包后端
    if not args.skip_backend:
        print_header("第3步：打包Python后端")
        if not build_backend():
            success = False
            print_error("后端打包失败")
    else:
        print_warning("跳过后端打包")
    
    # 4. 打包前端
    if not args.skip_frontend:
        print_header("第4步：打包Electron前端")
        if not build_frontend():
            success = False
            print_error("前端打包失败")
    else:
        print_warning("跳过前端打包")
    
    # 5. 创建安装包
    if success:
        print_header("第5步：生成安装程序")
        create_installer()
    
    # 完成
    print_header("打包完成")
    
    if success:
        print_success("所有组件打包成功！")
        print(f"\n安装包位置: {DIST_DIR}")
        print("\n下一步：")
        print("  1. 测试安装包")
        print("  2. 签名安装包（如需发布）")
        print("  3. 上传到发布平台")
    else:
        print_error("部分组件打包失败，请查看上面的错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
