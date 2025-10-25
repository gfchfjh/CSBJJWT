#!/usr/bin/env python3
"""
Chromium浏览器自动打包系统（终极版）
=======================================
功能：
1. 自动检测Chromium是否已安装
2. 未安装时自动下载安装（playwright install chromium）
3. 复制Chromium到构建目录
4. 验证浏览器可用性
5. 生成启动配置文件
6. 跨平台支持（Windows/Linux/macOS）
7. 智能缓存避免重复下载

作者：KOOK Forwarder Team
日期：2025-10-25
"""

import os
import sys
import shutil
import subprocess
import platform
import json
from pathlib import Path
from typing import Tuple, Optional

class ChromiumPreparer:
    """Chromium浏览器准备器（终极版）"""
    
    def __init__(self, build_dir: Path = None):
        self.system = platform.system()
        self.build_dir = build_dir or Path(__file__).parent.parent / "dist"
        self.chromium_dir = self.build_dir / "chromium"
        
        # 根据系统确定Playwright缓存路径
        self.playwright_cache = self._get_playwright_cache_path()
        
        # 浏览器版本信息
        self.browser_version = None
        
    def _get_playwright_cache_path(self) -> Path:
        """获取Playwright浏览器缓存路径"""
        if self.system == "Windows":
            # Windows: %USERPROFILE%\AppData\Local\ms-playwright
            return Path.home() / "AppData" / "Local" / "ms-playwright"
        elif self.system == "Darwin":
            # macOS: ~/Library/Caches/ms-playwright
            return Path.home() / "Library" / "Caches" / "ms-playwright"
        else:
            # Linux: ~/.cache/ms-playwright
            return Path.home() / ".cache" / "ms-playwright"
    
    def check_chromium_installed(self) -> Tuple[bool, Optional[str]]:
        """
        检查Chromium是否已安装
        
        Returns:
            (是否已安装, 浏览器路径)
        """
        print("🔍 检查Chromium是否已安装...")
        
        if not self.playwright_cache.exists():
            print("❌ Playwright缓存目录不存在")
            return False, None
        
        # 查找chromium目录
        chromium_dirs = list(self.playwright_cache.glob("chromium-*"))
        
        if not chromium_dirs:
            print("❌ 未找到Chromium浏览器")
            return False, None
        
        # 使用最新版本
        chromium_dirs.sort(reverse=True)
        chromium_path = chromium_dirs[0]
        
        # 验证可执行文件存在
        if self.system == "Windows":
            executable = chromium_path / "chrome-win" / "chrome.exe"
        elif self.system == "Darwin":
            executable = chromium_path / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
        else:
            executable = chromium_path / "chrome-linux" / "chrome"
        
        if executable.exists():
            print(f"✅ 找到Chromium: {chromium_path}")
            self.browser_version = chromium_path.name
            return True, str(chromium_path)
        else:
            print(f"❌ Chromium可执行文件不存在: {executable}")
            return False, None
    
    def install_chromium(self) -> bool:
        """
        安装Chromium浏览器（使用playwright install）
        
        Returns:
            是否安装成功
        """
        print("\n📦 开始安装Chromium浏览器...")
        print("⚠️  这将下载约300MB文件，可能需要几分钟...")
        
        try:
            # 执行playwright install chromium
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                print("✅ Chromium安装成功")
                return True
            else:
                print(f"❌ Chromium安装失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Chromium安装超时（网络可能过慢）")
            return False
        except Exception as e:
            print(f"❌ Chromium安装异常: {str(e)}")
            return False
    
    def copy_chromium_to_build(self, source_path: str) -> bool:
        """
        复制Chromium到构建目录
        
        Args:
            source_path: Chromium源路径
            
        Returns:
            是否复制成功
        """
        print(f"\n📂 复制Chromium到构建目录...")
        print(f"源路径: {source_path}")
        print(f"目标路径: {self.chromium_dir}")
        
        try:
            # 确保构建目录存在
            self.build_dir.mkdir(parents=True, exist_ok=True)
            
            # 删除旧的chromium目录（如果存在）
            if self.chromium_dir.exists():
                print("🗑️  删除旧的Chromium目录...")
                shutil.rmtree(self.chromium_dir)
            
            # 复制整个chromium目录
            print("📋 复制文件中（约130MB-160MB）...")
            shutil.copytree(source_path, self.chromium_dir)
            
            # 计算目录大小
            total_size = sum(
                f.stat().st_size for f in self.chromium_dir.rglob('*') if f.is_file()
            )
            size_mb = total_size / (1024 * 1024)
            
            print(f"✅ 复制完成，大小: {size_mb:.1f} MB")
            return True
            
        except Exception as e:
            print(f"❌ 复制失败: {str(e)}")
            return False
    
    def verify_chromium(self) -> bool:
        """
        验证Chromium可用性
        
        Returns:
            是否可用
        """
        print("\n🔬 验证Chromium可用性...")
        
        # 确定可执行文件路径
        if self.system == "Windows":
            executable = self.chromium_dir / "chrome-win" / "chrome.exe"
        elif self.system == "Darwin":
            executable = self.chromium_dir / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
        else:
            executable = self.chromium_dir / "chrome-linux" / "chrome"
        
        if not executable.exists():
            print(f"❌ 可执行文件不存在: {executable}")
            return False
        
        # 在Unix系统上设置执行权限
        if self.system != "Windows":
            try:
                os.chmod(executable, 0o755)
                print("✅ 设置执行权限")
            except Exception as e:
                print(f"⚠️  设置执行权限失败: {str(e)}")
        
        # 尝试获取版本信息
        try:
            result = subprocess.run(
                [str(executable), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Chromium可用: {version}")
                return True
            else:
                print(f"❌ Chromium无法运行: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 验证失败: {str(e)}")
            return False
    
    def generate_config(self) -> bool:
        """
        生成Chromium配置文件
        
        Returns:
            是否生成成功
        """
        print("\n📝 生成Chromium配置文件...")
        
        try:
            config = {
                "browser_type": "chromium",
                "version": self.browser_version,
                "system": self.system,
                "executable_path": self._get_relative_executable_path(),
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ],
                "prepared_at": "2025-10-25",
                "prepared_by": "ChromiumPreparer Ultimate"
            }
            
            config_path = self.chromium_dir / "chromium_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置文件已生成: {config_path}")
            return True
            
        except Exception as e:
            print(f"❌ 生成配置失败: {str(e)}")
            return False
    
    def _get_relative_executable_path(self) -> str:
        """获取相对可执行文件路径"""
        if self.system == "Windows":
            return "chrome-win/chrome.exe"
        elif self.system == "Darwin":
            return "chrome-mac/Chromium.app/Contents/MacOS/Chromium"
        else:
            return "chrome-linux/chrome"
    
    def prepare(self) -> bool:
        """
        完整准备流程
        
        Returns:
            是否准备成功
        """
        print("=" * 60)
        print("🚀 Chromium浏览器自动打包系统（终极版）")
        print("=" * 60)
        print(f"操作系统: {self.system}")
        print(f"构建目录: {self.build_dir}")
        print()
        
        # 步骤1: 检查是否已安装
        installed, chromium_path = self.check_chromium_installed()
        
        # 步骤2: 未安装则安装
        if not installed:
            print("\n⚠️  Chromium未安装，开始自动安装...")
            if not self.install_chromium():
                print("\n❌ Chromium安装失败，无法继续")
                return False
            
            # 重新检查
            installed, chromium_path = self.check_chromium_installed()
            if not installed:
                print("\n❌ 安装后仍未找到Chromium")
                return False
        
        # 步骤3: 复制到构建目录
        if not self.copy_chromium_to_build(chromium_path):
            print("\n❌ 复制失败")
            return False
        
        # 步骤4: 验证可用性
        if not self.verify_chromium():
            print("\n❌ 验证失败")
            return False
        
        # 步骤5: 生成配置文件
        if not self.generate_config():
            print("\n❌ 生成配置失败")
            return False
        
        print("\n" + "=" * 60)
        print("✅ Chromium浏览器准备完成！")
        print("=" * 60)
        print(f"📁 浏览器位置: {self.chromium_dir}")
        print(f"📦 浏览器版本: {self.browser_version}")
        print(f"💾 占用空间: {self._get_directory_size(self.chromium_dir):.1f} MB")
        print()
        print("🎯 下一步：将此目录打包进最终安装包")
        print()
        
        return True
    
    def _get_directory_size(self, directory: Path) -> float:
        """获取目录大小（MB）"""
        total = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
        return total / (1024 * 1024)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Chromium浏览器自动打包系统')
    parser.add_argument(
        '--build-dir',
        type=Path,
        help='构建目录路径（默认: ../dist）'
    )
    parser.add_argument(
        '--force-reinstall',
        action='store_true',
        help='强制重新安装Chromium'
    )
    
    args = parser.parse_args()
    
    preparer = ChromiumPreparer(build_dir=args.build_dir)
    
    # 如果强制重新安装，先删除缓存
    if args.force_reinstall:
        print("🔄 强制重新安装模式")
        if preparer.chromium_dir.exists():
            print(f"🗑️  删除旧的构建: {preparer.chromium_dir}")
            shutil.rmtree(preparer.chromium_dir)
    
    # 执行准备
    success = preparer.prepare()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
