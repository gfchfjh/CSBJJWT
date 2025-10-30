#!/usr/bin/env python3
"""
完整构建脚本
✅ P2-3: 跨平台自动化构建
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


class BuildSystem:
    """构建系统"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.backend_dir = self.root_dir / 'backend'
        self.frontend_dir = self.root_dir / 'frontend'
        self.build_dir = self.root_dir / 'build'
        self.dist_dir = self.root_dir / 'dist'
        
        # 清理旧的构建
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.dist_dir.mkdir()
    
    def run_command(self, cmd, cwd=None, shell=False):
        """运行命令"""
        print(f"\n▶️  执行: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        
        result = subprocess.run(
            cmd,
            cwd=cwd or self.root_dir,
            shell=shell,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败:")
            print(result.stderr)
            sys.exit(1)
        
        return result.stdout
    
    def build_backend(self):
        """构建后端"""
        print("\n" + "="*60)
        print("📦 构建后端...")
        print("="*60)
        
        # 安装Playwright浏览器
        print("\n1️⃣  安装Playwright浏览器...")
        self.run_command(
            [sys.executable, '-m', 'playwright', 'install', 'chromium'],
            cwd=self.backend_dir
        )
        
        # 使用PyInstaller打包
        print("\n2️⃣  使用PyInstaller打包...")
        spec_file = self.build_dir / 'pyinstaller.spec'
        
        self.run_command(
            ['pyinstaller', str(spec_file), '--clean'],
            cwd=self.root_dir
        )
        
        print("✅ 后端构建完成")
    
    def build_frontend(self):
        """构建前端"""
        print("\n" + "="*60)
        print("🎨 构建前端...")
        print("="*60)
        
        # 安装依赖
        print("\n1️⃣  安装npm依赖...")
        self.run_command(['npm', 'install'], cwd=self.frontend_dir)
        
        # 构建Vue项目
        print("\n2️⃣  构建Vue项目...")
        self.run_command(['npm', 'run', 'build'], cwd=self.frontend_dir)
        
        # 构建Electron应用
        print("\n3️⃣  构建Electron应用...")
        self.run_command(['npm', 'run', 'electron:build'], cwd=self.frontend_dir)
        
        print("✅ 前端构建完成")
    
    def package_redis(self):
        """打包Redis"""
        print("\n" + "="*60)
        print("📦 打包Redis...")
        print("="*60)
        
        redis_dir = self.root_dir / 'redis'
        
        if not redis_dir.exists():
            print("⚠️  Redis目录不存在，跳过")
            return
        
        # 复制Redis到dist
        dist_redis = self.dist_dir / 'redis'
        shutil.copytree(redis_dir, dist_redis)
        
        print("✅ Redis打包完成")
    
    def create_installers(self):
        """创建安装包"""
        print("\n" + "="*60)
        print("📦 创建安装包...")
        print("="*60)
        
        platform = sys.platform
        
        if platform == 'win32':
            self.create_windows_installer()
        elif platform == 'darwin':
            self.create_macos_installer()
        elif platform == 'linux':
            self.create_linux_installer()
        else:
            print(f"⚠️  未知平台: {platform}")
    
    def create_windows_installer(self):
        """创建Windows安装包"""
        print("\n🪟 创建Windows安装包...")
        
        # Electron Builder已经创建了NSIS安装包
        installer_files = list(self.frontend_dir.glob('dist/*.exe'))
        
        if installer_files:
            for installer in installer_files:
                dest = self.dist_dir / installer.name
                shutil.copy2(installer, dest)
                print(f"✅ 安装包: {dest}")
        else:
            print("⚠️  未找到安装包")
    
    def create_macos_installer(self):
        """创建macOS安装包"""
        print("\n🍎 创建macOS安装包...")
        
        # Electron Builder已经创建了DMG
        dmg_files = list(self.frontend_dir.glob('dist/*.dmg'))
        
        if dmg_files:
            for dmg in dmg_files:
                dest = self.dist_dir / dmg.name
                shutil.copy2(dmg, dest)
                print(f"✅ 安装包: {dest}")
        else:
            print("⚠️  未找到安装包")
    
    def create_linux_installer(self):
        """创建Linux安装包"""
        print("\n🐧 创建Linux安装包...")
        
        # Electron Builder已经创建了AppImage/deb/rpm
        installer_files = list(self.frontend_dir.glob('dist/*.AppImage'))
        installer_files += list(self.frontend_dir.glob('dist/*.deb'))
        installer_files += list(self.frontend_dir.glob('dist/*.rpm'))
        
        if installer_files:
            for installer in installer_files:
                dest = self.dist_dir / installer.name
                shutil.copy2(installer, dest)
                print(f"✅ 安装包: {dest}")
        else:
            print("⚠️  未找到安装包")
    
    def generate_checksums(self):
        """生成校验和"""
        print("\n" + "="*60)
        print("🔐 生成校验和...")
        print("="*60)
        
        import hashlib
        
        checksums_file = self.dist_dir / 'checksums.txt'
        
        with open(checksums_file, 'w') as f:
            for file in self.dist_dir.iterdir():
                if file.is_file() and file.name != 'checksums.txt':
                    # 计算SHA256
                    sha256 = hashlib.sha256()
                    
                    with open(file, 'rb') as fh:
                        while True:
                            data = fh.read(65536)
                            if not data:
                                break
                            sha256.update(data)
                    
                    checksum = sha256.hexdigest()
                    f.write(f"{checksum}  {file.name}\n")
                    print(f"✅ {file.name}: {checksum}")
        
        print(f"\n✅ 校验和文件: {checksums_file}")
    
    def build_all(self):
        """执行完整构建"""
        print("\n" + "="*60)
        print("🚀 开始完整构建...")
        print("="*60)
        
        try:
            # 1. 构建后端
            self.build_backend()
            
            # 2. 构建前端
            self.build_frontend()
            
            # 3. 打包Redis
            self.package_redis()
            
            # 4. 创建安装包
            self.create_installers()
            
            # 5. 生成校验和
            self.generate_checksums()
            
            print("\n" + "="*60)
            print("🎉 构建完成！")
            print("="*60)
            print(f"\n📦 安装包位置: {self.dist_dir}")
            
            # 列出所有文件
            print("\n📋 生成的文件:")
            for file in sorted(self.dist_dir.iterdir()):
                size = file.stat().st_size / 1024 / 1024
                print(f"  - {file.name} ({size:.1f} MB)")
            
        except Exception as e:
            print(f"\n❌ 构建失败: {str(e)}")
            sys.exit(1)


def main():
    """主函数"""
    builder = BuildSystem()
    builder.build_all()


if __name__ == '__main__':
    main()
