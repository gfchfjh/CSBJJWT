#!/usr/bin/env python3
"""
全平台自动化构建脚本
支持Windows、macOS、Linux的一键构建
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform
import json


class PlatformBuilder:
    """跨平台构建器"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.resolve()
        self.frontend_dir = self.root_dir / "frontend"
        self.backend_dir = self.root_dir / "backend"
        self.build_dir = self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        
        self.current_platform = platform.system().lower()
        print(f"🖥️  当前平台: {self.current_platform}")
    
    def run_command(self, cmd, cwd=None, shell=False):
        """运行命令"""
        print(f"\n▶️  执行: {cmd}")
        try:
            result = subprocess.run(
                cmd if shell else cmd.split(),
                cwd=cwd or self.root_dir,
                shell=shell,
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 命令执行失败: {e}")
            print(e.stderr)
            return False
    
    def check_dependencies(self):
        """检查依赖"""
        print("\n🔍 检查构建依赖...")
        
        dependencies = {
            'node': 'Node.js未安装，请安装 https://nodejs.org/',
            'npm': 'npm未安装',
        }
        
        # 检查Python（支持python或python3）
        python_installed = False
        for py_cmd in ['python', 'python3']:
            try:
                subprocess.run([py_cmd, '--version'], capture_output=True, check=True)
                print(f"  ✅ {py_cmd} 已安装")
                python_installed = True
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if not python_installed:
            print(f"  ❌ Python未安装，请安装Python 3.11+")
            return False
        
        for cmd, error_msg in dependencies.items():
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
                print(f"  ✅ {cmd} 已安装")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"  ❌ {error_msg}")
                return False
        
        return True
    
    def install_frontend_deps(self):
        """安装前端依赖"""
        print("\n📦 安装前端依赖...")
        return self.run_command("npm install --legacy-peer-deps", cwd=self.frontend_dir, shell=True)
    
    def install_backend_deps(self):
        """安装后端依赖"""
        print("\n📦 安装后端依赖...")
        return self.run_command("pip install -r requirements.txt", cwd=self.backend_dir, shell=True)
    
    def build_frontend(self):
        """构建前端"""
        print("\n🔨 构建前端...")
        return self.run_command("npm run build", cwd=self.frontend_dir)
    
    def build_electron_windows(self):
        """构建Windows Electron应用"""
        print("\n🪟 构建Windows安装包...")
        return self.run_command("npm run electron:build:win", cwd=self.frontend_dir)
    
    def build_electron_mac(self):
        """构建macOS Electron应用"""
        print("\n🍎 构建macOS安装包...")
        return self.run_command("npm run electron:build:mac", cwd=self.frontend_dir)
    
    def build_electron_linux(self):
        """构建Linux Electron应用"""
        print("\n🐧 构建Linux安装包...")
        return self.run_command("npm run electron:build:linux", cwd=self.frontend_dir)
    
    def build_backend(self):
        """构建Python后端"""
        print("\n🐍 构建Python后端...")
        
        # 使用PyInstaller
        spec_file = self.build_dir / "pyinstaller.spec"
        if not spec_file.exists():
            print("❌ pyinstaller.spec 文件不存在")
            return False
        
        return self.run_command(
            f"pyinstaller {spec_file}",
            cwd=self.backend_dir,
            shell=True
        )
    
    def package_production(self):
        """打包生产版本"""
        print("\n📦 打包生产版本...")
        
        # 创建dist目录
        self.dist_dir.mkdir(exist_ok=True)
        
        # 复制文件
        # TODO: 实现具体的打包逻辑
        
        return True
    
    def build_all(self, platforms=None):
        """构建所有平台"""
        print("=" * 60)
        print("🚀 KOOK消息转发系统 - 全平台构建")
        print("=" * 60)
        
        # 检查依赖
        if not self.check_dependencies():
            print("\n❌ 依赖检查失败，请安装缺失的依赖")
            return False
        
        # 安装依赖
        if not self.install_frontend_deps():
            print("\n❌ 前端依赖安装失败")
            return False
        
        if not self.install_backend_deps():
            print("\n❌ 后端依赖安装失败")
            return False
        
        # 构建前端
        if not self.build_frontend():
            print("\n❌ 前端构建失败")
            return False
        
        # 根据指定的平台构建
        if platforms is None:
            platforms = ['windows', 'mac', 'linux']
        
        success = True
        
        if 'windows' in platforms:
            if not self.build_electron_windows():
                print("\n⚠️  Windows构建失败")
                success = False
        
        if 'mac' in platforms:
            if not self.build_electron_mac():
                print("\n⚠️  macOS构建失败")
                success = False
        
        if 'linux' in platforms:
            if not self.build_electron_linux():
                print("\n⚠️  Linux构建失败")
                success = False
        
        # 构建后端
        if not self.build_backend():
            print("\n⚠️  后端构建失败")
            success = False
        
        # 打包
        if not self.package_production():
            print("\n⚠️  打包失败")
            success = False
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 所有平台构建成功！")
            print(f"📦 输出目录: {self.dist_dir}")
        else:
            print("⚠️  部分平台构建失败，请检查错误日志")
        print("=" * 60)
        
        return success
    
    def build_current_platform(self):
        """仅构建当前平台"""
        platform_map = {
            'windows': ['windows'],
            'darwin': ['mac'],
            'linux': ['linux']
        }
        
        platforms = platform_map.get(self.current_platform, ['linux'])
        return self.build_all(platforms=platforms)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KOOK消息转发系统 - 构建工具')
    parser.add_argument(
        '--platform',
        choices=['windows', 'mac', 'linux', 'all', 'current'],
        default='current',
        help='指定构建平台'
    )
    parser.add_argument(
        '--skip-deps',
        action='store_true',
        help='跳过依赖安装'
    )
    
    args = parser.parse_args()
    
    builder = PlatformBuilder()
    
    if args.platform == 'all':
        success = builder.build_all()
    elif args.platform == 'current':
        success = builder.build_current_platform()
    else:
        success = builder.build_all(platforms=[args.platform])
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
