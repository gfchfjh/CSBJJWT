#!/usr/bin/env python3
"""
KOOK消息转发系统 - 统一打包脚本
自动打包前端（Electron）+ 后端（PyInstaller）+ 嵌入式组件（Redis + Chromium）
生成完全独立的一键安装包
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
import zipfile
import tarfile

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

# 项目路径
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"
REDIS_DIR = ROOT_DIR / "redis"

# 读取版本号
VERSION_FILE = ROOT_DIR / "VERSION"
VERSION = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "14.0.0"

# 操作系统检测
OS_NAME = platform.system().lower()
IS_WINDOWS = OS_NAME == "windows"
IS_MACOS = OS_NAME == "darwin"
IS_LINUX = OS_NAME == "linux"


class PackageBuilder:
    """统一打包构建器"""
    
    def __init__(self):
        self.os_name = OS_NAME
        self.version = VERSION
        self.dist_dir = DIST_DIR
        
    def clean_dist(self):
        """清理构建目录"""
        print_header("清理构建目录")
        
        if self.dist_dir.exists():
            print_info(f"删除旧的构建目录: {self.dist_dir}")
            shutil.rmtree(self.dist_dir)
        
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        print_success("构建目录清理完成")
    
    def build_backend(self):
        """打包Python后端（PyInstaller）"""
        print_header("打包Python后端")
        
        print_info("检查PyInstaller...")
        try:
            subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_warning("PyInstaller未安装，正在安装...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        print_info("开始打包后端...")
        spec_file = BUILD_DIR / "pyinstaller.spec"
        
        if not spec_file.exists():
            print_error(f"PyInstaller配置文件不存在: {spec_file}")
            return False
        
        # 执行PyInstaller打包
        cmd = ["pyinstaller", "--clean", "--noconfirm", str(spec_file)]
        result = subprocess.run(cmd, cwd=ROOT_DIR)
        
        if result.returncode != 0:
            print_error("后端打包失败")
            return False
        
        print_success("后端打包完成")
        return True
    
    def download_redis(self):
        """下载/准备Redis可执行文件"""
        print_header("准备Redis服务")
        
        redis_bin_dir = DIST_DIR / "redis"
        redis_bin_dir.mkdir(parents=True, exist_ok=True)
        
        if IS_WINDOWS:
            # Windows: 使用预编译的Redis
            print_info("准备Windows版Redis...")
            redis_exe = REDIS_DIR / "redis-server.exe"
            
            if not redis_exe.exists():
                print_warning("Redis可执行文件不存在，需要手动下载")
                print_info("请从 https://github.com/tporadowski/redis/releases 下载Windows版Redis")
                print_info("并将redis-server.exe放到 redis/ 目录")
                return False
            
            # 复制Redis文件
            shutil.copy(redis_exe, redis_bin_dir / "redis-server.exe")
            if (REDIS_DIR / "redis.conf").exists():
                shutil.copy(REDIS_DIR / "redis.conf", redis_bin_dir / "redis.conf")
            
        elif IS_LINUX or IS_MACOS:
            # Linux/macOS: 检查系统Redis
            print_info("检查系统Redis...")
            result = subprocess.run(["which", "redis-server"], capture_output=True)
            
            if result.returncode == 0:
                redis_path = result.stdout.decode().strip()
                print_info(f"找到系统Redis: {redis_path}")
                shutil.copy(redis_path, redis_bin_dir / "redis-server")
            else:
                print_warning("未找到系统Redis，将在安装时提示用户安装")
        
        print_success("Redis准备完成")
        return True
    
    def download_chromium(self):
        """准备Playwright Chromium"""
        print_header("准备Chromium浏览器")
        
        print_info("安装Playwright浏览器...")
        
        # 激活虚拟环境（如果存在）
        venv_python = BACKEND_DIR / "venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = sys.executable
        
        # 安装Chromium
        cmd = [str(venv_python), "-m", "playwright", "install", "chromium"]
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            print_error("Chromium安装失败")
            return False
        
        print_success("Chromium准备完成")
        return True
    
    def build_frontend(self):
        """打包前端（Vue + Electron）"""
        print_header("打包前端")
        
        print_info("检查Node.js环境...")
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error("Node.js或npm未安装，请先安装Node.js")
            return False
        
        print_info("安装前端依赖...")
        npm_cmd = ["npm", "install"]
        result = subprocess.run(npm_cmd, cwd=FRONTEND_DIR)
        if result.returncode != 0:
            print_error("依赖安装失败")
            return False
        
        print_info("构建前端资源...")
        build_cmd = ["npm", "run", "build"]
        result = subprocess.run(build_cmd, cwd=FRONTEND_DIR)
        if result.returncode != 0:
            print_error("前端构建失败")
            return False
        
        print_info("打包Electron应用...")
        
        # 根据操作系统选择打包命令
        if IS_WINDOWS:
            pack_cmd = ["npm", "run", "electron:build:win"]
        elif IS_MACOS:
            pack_cmd = ["npm", "run", "electron:build:mac"]
        else:
            pack_cmd = ["npm", "run", "electron:build:linux"]
        
        result = subprocess.run(pack_cmd, cwd=FRONTEND_DIR)
        if result.returncode != 0:
            print_error("Electron打包失败")
            return False
        
        print_success("前端打包完成")
        return True
    
    def create_installer(self):
        """创建最终安装包"""
        print_header("创建安装包")
        
        installer_dir = DIST_DIR / "installer"
        installer_dir.mkdir(parents=True, exist_ok=True)
        
        print_info("收集所有文件...")
        
        # 1. 复制后端可执行文件
        backend_dist = DIST_DIR / "kook-forwarder-backend"
        if backend_dist.exists():
            if IS_WINDOWS:
                backend_exe = backend_dist.parent / "kook-forwarder-backend.exe"
            else:
                backend_exe = backend_dist
            
            if backend_exe.exists():
                shutil.copy(backend_exe, installer_dir / backend_exe.name)
        
        # 2. 复制前端应用
        frontend_dist = FRONTEND_DIR / "dist-electron"
        if frontend_dist.exists():
            # 复制整个前端构建目录
            shutil.copytree(frontend_dist, installer_dir / "frontend", dirs_exist_ok=True)
        
        # 3. 复制Redis
        redis_dist = DIST_DIR / "redis"
        if redis_dist.exists():
            shutil.copytree(redis_dist, installer_dir / "redis", dirs_exist_ok=True)
        
        # 4. 复制文档
        docs_to_copy = [
            ROOT_DIR / "README.md",
            ROOT_DIR / "LICENSE",
            ROOT_DIR / "VERSION",
        ]
        
        for doc in docs_to_copy:
            if doc.exists():
                shutil.copy(doc, installer_dir / doc.name)
        
        # 5. 创建启动脚本
        self._create_startup_scripts(installer_dir)
        
        # 6. 打包为压缩文件
        self._create_archive(installer_dir)
        
        print_success("安装包创建完成")
        return True
    
    def _create_startup_scripts(self, installer_dir):
        """创建启动脚本"""
        print_info("创建启动脚本...")
        
        if IS_WINDOWS:
            # Windows批处理脚本
            start_script = installer_dir / "启动.bat"
            start_script.write_text("""@echo off
chcp 65001 >nul
title KOOK消息转发系统

echo ╔═══════════════════════════════════════════════╗
echo ║                                               ║
echo ║   KOOK消息转发系统 v{version}                 ║
echo ║                                               ║
echo ╚═══════════════════════════════════════════════╝
echo.

echo [1/3] 启动Redis服务...
start /B redis\\redis-server.exe redis\\redis.conf
timeout /t 2 /nobreak >nul

echo [2/3] 启动后端服务...
start /B kook-forwarder-backend.exe
timeout /t 3 /nobreak >nul

echo [3/3] 启动前端应用...
cd frontend
start "" "KOOK消息转发系统.exe"
cd ..

echo.
echo ✅ 启动完成！
echo.
echo 提示：请勿关闭此窗口
pause
""".format(version=VERSION), encoding="utf-8")
            
        else:
            # Linux/macOS Shell脚本
            start_script = installer_dir / "start.sh"
            start_script.write_text("""#!/bin/bash

echo "╔═══════════════════════════════════════════════╗"
echo "║                                               ║"
echo "║   KOOK消息转发系统 v{version}                 ║"
echo "║                                               ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

echo "[1/3] 启动Redis服务..."
./redis/redis-server ./redis/redis.conf &
sleep 2

echo "[2/3] 启动后端服务..."
./kook-forwarder-backend &
sleep 3

echo "[3/3] 启动前端应用..."
cd frontend
./"KOOK消息转发系统" &
cd ..

echo ""
echo "✅ 启动完成！"
echo ""
""".format(version=VERSION))
            start_script.chmod(0o755)
    
    def _create_archive(self, installer_dir):
        """打包为压缩文件"""
        print_info("创建压缩包...")
        
        if IS_WINDOWS:
            archive_name = f"KOOK-Forwarder-v{VERSION}-Windows-x64.zip"
            archive_path = DIST_DIR / archive_name
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file in installer_dir.rglob("*"):
                    if file.is_file():
                        arcname = file.relative_to(installer_dir.parent)
                        zf.write(file, arcname)
            
        else:
            if IS_MACOS:
                archive_name = f"KOOK-Forwarder-v{VERSION}-macOS-x64.tar.gz"
            else:
                archive_name = f"KOOK-Forwarder-v{VERSION}-Linux-x64.tar.gz"
            
            archive_path = DIST_DIR / archive_name
            
            with tarfile.open(archive_path, 'w:gz') as tf:
                tf.add(installer_dir, arcname=installer_dir.name)
        
        print_success(f"压缩包已创建: {archive_path}")
        
        # 显示文件大小
        size_mb = archive_path.stat().st_size / (1024 * 1024)
        print_info(f"文件大小: {size_mb:.2f} MB")
    
    def build_all(self):
        """执行完整构建流程"""
        print_header(f"开始构建 KOOK消息转发系统 v{self.version}")
        print_info(f"操作系统: {self.os_name}")
        print_info(f"构建目录: {self.dist_dir}")
        
        steps = [
            ("清理构建目录", self.clean_dist),
            ("下载Redis", self.download_redis),
            ("下载Chromium", self.download_chromium),
            ("打包后端", self.build_backend),
            ("打包前端", self.build_frontend),
            ("创建安装包", self.create_installer),
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print_error(f"步骤失败: {step_name}")
                    return False
            except Exception as e:
                print_error(f"步骤异常: {step_name}")
                print_error(f"错误信息: {str(e)}")
                return False
        
        print_header("✅ 构建完成！")
        print_success(f"安装包位置: {self.dist_dir}")
        print_info("\n下一步：")
        print_info("1. 测试安装包")
        print_info("2. 上传到GitHub Releases")
        print_info("3. 更新README.md中的下载链接")
        
        return True


def main():
    """主函数"""
    try:
        builder = PackageBuilder()
        success = builder.build_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"构建失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
