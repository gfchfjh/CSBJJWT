#!/usr/bin/env python3
"""
KOOK消息转发系统 - 终极打包脚本
一键生成 Windows/macOS/Linux 安装包

使用方法:
    python build/package_ultimate.py --platform all
    python build/package_ultimate.py --platform windows
    python build/package_ultimate.py --platform macos
    python build/package_ultimate.py --platform linux
"""

import subprocess
import shutil
import platform
import sys
import os
from pathlib import Path
import argparse
import json

class UltimatePackager:
    """终极打包器"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.build_dir = self.root_dir / "build"
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.dist_dir = self.root_dir / "dist"
        
        # 读取版本号
        self.version = self._read_version()
        
        print(f"🚀 KOOK消息转发系统 - 终极打包器 v{self.version}")
        print("=" * 60)
    
    def _read_version(self) -> str:
        """读取版本号"""
        version_file = self.root_dir / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        return "1.0.0"
    
    def build_all(self, target_platform: str = "all"):
        """
        执行完整构建流程
        
        Args:
            target_platform: 目标平台 (all/windows/macos/linux)
        """
        print("\n📦 开始完整构建流程...")
        
        # 步骤1: 准备环境
        print("\n[1/7] 📋 检查构建环境...")
        self._check_build_environment()
        
        # 步骤2: 安装依赖
        print("\n[2/7] 📥 安装构建依赖...")
        self._install_dependencies()
        
        # 步骤3: 下载Playwright浏览器
        print("\n[3/7] 🌐 下载Chromium浏览器...")
        self._download_chromium()
        
        # 步骤4: 打包Python后端
        print("\n[4/7] 🐍 打包Python后端...")
        self._package_backend()
        
        # 步骤5: 构建前端
        print("\n[5/7] 🎨 构建前端...")
        self._build_frontend()
        
        # 步骤6: 准备Redis
        print("\n[6/7] 💾 准备嵌入式Redis...")
        self._prepare_redis()
        
        # 步骤7: 打包Electron应用
        print("\n[7/7] 📦 打包Electron应用...")
        self._package_electron(target_platform)
        
        print("\n" + "=" * 60)
        print("✅ 构建完成！")
        print(f"📁 输出目录: {self.dist_dir}")
        self._show_package_info()
    
    def _check_build_environment(self):
        """检查构建环境"""
        checks = []
        
        # 检查Python
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 11:
            checks.append(("Python", "✅", f"{python_version.major}.{python_version.minor}.{python_version.micro}"))
        else:
            checks.append(("Python", "❌", f"需要3.11+，当前{python_version.major}.{python_version.minor}"))
        
        # 检查Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            node_version = result.stdout.strip()
            checks.append(("Node.js", "✅", node_version))
        except FileNotFoundError:
            checks.append(("Node.js", "❌", "未安装"))
        
        # 检查npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            npm_version = result.stdout.strip()
            checks.append(("npm", "✅", npm_version))
        except FileNotFoundError:
            checks.append(("npm", "❌", "未安装"))
        
        # 检查PyInstaller
        try:
            result = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True)
            pyinstaller_version = result.stdout.strip()
            checks.append(("PyInstaller", "✅", pyinstaller_version))
        except FileNotFoundError:
            checks.append(("PyInstaller", "❌", "未安装"))
        
        # 打印检查结果
        for tool, status, version in checks:
            print(f"  {status} {tool:15} {version}")
        
        # 如果有失败项，退出
        if any(status == "❌" for _, status, _ in checks):
            print("\n❌ 构建环境检查失败，请安装缺失的工具")
            sys.exit(1)
    
    def _install_dependencies(self):
        """安装构建依赖"""
        print("  安装Python依赖...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r",
            str(self.backend_dir / "requirements.txt")
        ], check=True)
        
        # 安装打包工具
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "pyinstaller>=6.0.0",
            "playwright>=1.40.0"
        ], check=True)
        
        print("  安装前端依赖...")
        subprocess.run(["npm", "install"], cwd=str(self.frontend_dir), check=True)
    
    def _download_chromium(self):
        """下载Chromium浏览器"""
        print("  正在下载Chromium（可能需要几分钟）...")
        subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"
        ], check=True)
        
        print("  ✅ Chromium下载完成")
    
    def _package_backend(self):
        """打包Python后端"""
        print("  使用PyInstaller打包后端...")
        
        # 获取Playwright浏览器路径
        import playwright
        playwright_path = Path(playwright.__file__).parent / "driver" / "package" / ".local-browsers"
        
        # 构建PyInstaller命令
        pyinstaller_args = [
            "pyinstaller",
            "--clean",
            "--noconfirm",
            "--onefile",
            "--name", f"kook-forwarder-backend-{self.version}",
            # 添加数据文件
            "--add-data", f"{self.backend_dir / 'data'}:{os.pathsep}data",
            # 添加Chromium浏览器
            "--add-data", f"{playwright_path}:{os.pathsep}.local-browsers",
            # 隐藏导入
            "--hidden-import", "playwright",
            "--hidden-import", "aiohttp",
            "--hidden-import", "fastapi",
            "--hidden-import", "uvicorn",
            "--hidden-import", "pydantic",
            "--hidden-import", "redis",
            "--hidden-import", "PIL",
            "--hidden-import", "cryptography",
            # 优化选项
            "--optimize", "2",
            # 控制台窗口（Windows）
            "--console",
            # 入口文件
            str(self.backend_dir / "app" / "main.py")
        ]
        
        subprocess.run(pyinstaller_args, cwd=str(self.root_dir), check=True)
        print("  ✅ 后端打包完成")
    
    def _build_frontend(self):
        """构建前端"""
        print("  构建Vue前端...")
        subprocess.run(["npm", "run", "build"], cwd=str(self.frontend_dir), check=True)
        print("  ✅ 前端构建完成")
    
    def _prepare_redis(self):
        """准备嵌入式Redis"""
        redis_dir = self.root_dir / "redis"
        
        current_os = platform.system()
        
        if current_os == "Windows":
            print("  准备Windows版Redis...")
            # 检查是否已有Redis
            redis_exe = redis_dir / "redis-server.exe"
            if not redis_exe.exists():
                print("  ⚠️  Redis未找到，请手动下载放到redis/目录")
                print("  下载地址: https://github.com/microsoftarchive/redis/releases")
        
        elif current_os == "Darwin":
            print("  准备macOS版Redis...")
            # macOS可以使用Homebrew安装的Redis
            redis_bin = redis_dir / "redis-server"
            if not redis_bin.exists():
                print("  尝试复制系统Redis...")
                try:
                    shutil.copy("/usr/local/bin/redis-server", redis_bin)
                except FileNotFoundError:
                    print("  ⚠️  未找到系统Redis，请使用: brew install redis")
        
        else:  # Linux
            print("  准备Linux版Redis...")
            redis_bin = redis_dir / "redis-server"
            if not redis_bin.exists():
                print("  尝试复制系统Redis...")
                try:
                    shutil.copy("/usr/bin/redis-server", redis_bin)
                except FileNotFoundError:
                    print("  ⚠️  未找到系统Redis，请使用: apt install redis-server")
        
        print("  ✅ Redis准备完成")
    
    def _package_electron(self, target_platform: str):
        """打包Electron应用"""
        print(f"  打包目标平台: {target_platform}")
        
        # 确保后端可执行文件在electron资源中
        self._copy_backend_to_electron()
        
        # 根据平台选择打包命令
        if target_platform == "all":
            platforms = ["windows", "macos", "linux"]
        else:
            platforms = [target_platform]
        
        for plat in platforms:
            print(f"\n  📦 打包 {plat.upper()} 版本...")
            
            if plat == "windows":
                cmd = "electron:build:win"
            elif plat == "macos":
                cmd = "electron:build:mac"
            else:
                cmd = "electron:build:linux"
            
            try:
                subprocess.run(
                    ["npm", "run", cmd],
                    cwd=str(self.frontend_dir),
                    check=True
                )
                print(f"  ✅ {plat.upper()} 版本打包完成")
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️  {plat.upper()} 版本打包失败: {e}")
    
    def _copy_backend_to_electron(self):
        """复制后端可执行文件到Electron资源目录"""
        dist_backend = self.root_dir / "dist" / f"kook-forwarder-backend-{self.version}"
        
        current_os = platform.system()
        if current_os == "Windows":
            dist_backend = Path(str(dist_backend) + ".exe")
        
        if dist_backend.exists():
            # 复制到frontend/electron/resources/
            resources_dir = self.frontend_dir / "electron" / "resources"
            resources_dir.mkdir(parents=True, exist_ok=True)
            
            shutil.copy(dist_backend, resources_dir / dist_backend.name)
            print(f"  ✅ 已复制后端到: {resources_dir}")
        else:
            print(f"  ⚠️  未找到后端可执行文件: {dist_backend}")
    
    def _show_package_info(self):
        """显示打包信息"""
        print("\n📦 打包信息:")
        print(f"  版本: v{self.version}")
        print(f"  输出目录: {self.dist_dir}")
        
        # 查找生成的安装包
        electron_dist = self.frontend_dir / "dist-electron"
        if electron_dist.exists():
            packages = list(electron_dist.glob("*.exe")) + \
                      list(electron_dist.glob("*.dmg")) + \
                      list(electron_dist.glob("*.AppImage"))
            
            if packages:
                print("\n📦 生成的安装包:")
                for pkg in packages:
                    size_mb = pkg.stat().st_size / (1024 * 1024)
                    print(f"  ✅ {pkg.name} ({size_mb:.1f} MB)")
            else:
                print("  ⚠️  未找到安装包文件")
        
        print("\n🎉 打包完成！现在可以分发安装包了。")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="KOOK消息转发系统 - 终极打包器")
    parser.add_argument(
        "--platform",
        choices=["all", "windows", "macos", "linux"],
        default="all",
        help="目标平台 (默认: all)"
    )
    
    args = parser.parse_args()
    
    packager = UltimatePackager()
    
    try:
        packager.build_all(args.platform)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断构建")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
