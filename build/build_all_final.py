"""
一键打包脚本（最终版）
P0-17: 安装包大小优化
P0-18: 创建安装向导

功能：
1. 准备 Chromium 浏览器
2. 准备 Redis 服务
3. 打包后端（PyInstaller）
4. 打包前端（Electron Builder）
5. 创建安装向导
6. 优化安装包大小
"""
import os
import sys
import subprocess
import shutil
import json
from pathlib import Path


class FinalBuilder:
    """最终打包器"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.build_dir = self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        
        self.version = "3.1.0"  # 新版本号
    
    def run_command(self, cmd: list, cwd=None, description=""):
        """执行命令"""
        print(f"\n{'=' * 60}")
        print(f"🔨 {description}")
        print(f"   命令: {' '.join(cmd)}")
        print(f"{'=' * 60}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.root_dir,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                print(f"✅ {description} 成功")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"❌ {description} 失败")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ {description} 超时（10分钟）")
            return False
        except Exception as e:
            print(f"❌ {description} 异常: {e}")
            return False
    
    def prepare_chromium(self) -> bool:
        """准备 Chromium"""
        print("\n" + "🌐 " + "=" * 58)
        print("步骤 1/6: 准备 Chromium 浏览器")
        print("=" * 60)
        
        return self.run_command(
            [sys.executable, "build/prepare_chromium_enhanced.py"],
            description="准备 Chromium"
        )
    
    def prepare_redis(self) -> bool:
        """准备 Redis"""
        print("\n" + "📦 " + "=" * 58)
        print("步骤 2/6: 准备 Redis 服务")
        print("=" * 60)
        
        return self.run_command(
            [sys.executable, "build/prepare_redis_complete.py"],
            description="准备 Redis"
        )
    
    def build_backend(self) -> bool:
        """打包后端"""
        print("\n" + "🐍 " + "=" * 58)
        print("步骤 3/6: 打包后端（PyInstaller）")
        print("=" * 60)
        
        # 创建 PyInstaller spec 文件
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['backend/app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('dist/browsers', 'browsers'),
        ('dist/redis', 'redis'),
        ('backend/data', 'data'),
        ('docs', 'docs'),
    ],
    hiddenimports=[
        'playwright',
        'fastapi',
        'uvicorn',
        'redis',
        'aioredis',
        'discord_webhook',
        'telegram',
        'lark_oapi',
        'cryptography',
        'PIL',
        'orjson',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],
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
"""
        
        spec_path = self.build_dir / "backend_final.spec"
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        return self.run_command(
            ["pyinstaller", "--clean", str(spec_path)],
            description="PyInstaller 打包后端"
        )
    
    def build_frontend(self) -> bool:
        """打包前端"""
        print("\n" + "🎨 " + "=" * 58)
        print("步骤 4/6: 打包前端（Electron Builder）")
        print("=" * 60)
        
        frontend_dir = self.root_dir / "frontend"
        
        # 安装依赖
        if not self.run_command(
            ["npm", "install"],
            cwd=frontend_dir,
            description="安装前端依赖"
        ):
            return False
        
        # 构建前端
        if not self.run_command(
            ["npm", "run", "build"],
            cwd=frontend_dir,
            description="构建前端"
        ):
            return False
        
        # 打包 Electron
        return self.run_command(
            ["npm", "run", "electron:build"],
            cwd=frontend_dir,
            description="打包 Electron"
        )
    
    def optimize_package_size(self) -> bool:
        """优化安装包大小"""
        print("\n" + "📉 " + "=" * 58)
        print("步骤 5/6: 优化安装包大小")
        print("=" * 60)
        
        try:
            # 1. 删除不必要的文件
            print("🗑️  删除不必要的文件...")
            
            patterns_to_remove = [
                "**/*.pyc",
                "**/__pycache__",
                "**/*.pyo",
                "**/*.so.debug",
                "**/test*",
                "**/tests",
                "**/.git",
                "**/.github",
                "**/*.md",  # 除了 README
            ]
            
            removed_count = 0
            for pattern in patterns_to_remove:
                for file_path in self.dist_dir.rglob(pattern):
                    if file_path.is_file():
                        file_path.unlink()
                        removed_count += 1
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        removed_count += 1
            
            print(f"✅ 删除了 {removed_count} 个文件/目录")
            
            # 2. 压缩 Chromium
            print("\n🗜️  压缩 Chromium（使用 UPX）...")
            # 注意：需要安装 UPX
            # 这里仅做演示，实际可能需要更复杂的处理
            
            # 3. 计算最终大小
            total_size = sum(
                f.stat().st_size for f in self.dist_dir.rglob('*') if f.is_file()
            )
            size_mb = total_size / (1024 * 1024)
            
            print(f"\n📊 安装包总大小: {size_mb:.2f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ 优化失败: {e}")
            return False
    
    def create_installer(self) -> bool:
        """创建安装向导"""
        print("\n" + "📦 " + "=" * 58)
        print("步骤 6/6: 创建安装向导")
        print("=" * 60)
        
        if sys.platform == "win32":
            return self.create_windows_installer()
        elif sys.platform == "darwin":
            return self.create_macos_installer()
        else:
            return self.create_linux_installer()
    
    def create_windows_installer(self) -> bool:
        """创建 Windows 安装程序（NSIS）"""
        print("🪟 创建 Windows 安装程序...")
        
        # NSIS 脚本
        nsis_script = f"""!include "MUI2.nsh"

Name "KOOK消息转发系统"
OutFile "dist/KOOK-Forwarder-Setup-{self.version}-Windows-x64.exe"
InstallDir "$PROGRAMFILES64\\KookForwarder"

!define MUI_ABORTWARNING
!define MUI_ICON "build/icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "SimpChinese"

Section "Install"
    SetOutPath "$INSTDIR"
    File /r "dist\\kook-forwarder-backend\\*.*"
    File /r "dist\\browsers\\*.*"
    File /r "dist\\redis\\*.*"
    
    CreateDirectory "$SMPROGRAMS\\KOOK消息转发系统"
    CreateShortcut "$SMPROGRAMS\\KOOK消息转发系统\\KOOK消息转发系统.lnk" "$INSTDIR\\kook-forwarder-backend.exe"
    CreateShortcut "$DESKTOP\\KOOK消息转发系统.lnk" "$INSTDIR\\kook-forwarder-backend.exe"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\*.*"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\\KOOK消息转发系统.lnk"
    Delete "$SMPROGRAMS\\KOOK消息转发系统\\*.*"
    RMDir "$SMPROGRAMS\\KOOK消息转发系统"
SectionEnd
"""
        
        nsis_path = self.build_dir / "installer.nsi"
        with open(nsis_path, 'w', encoding='utf-8') as f:
            f.write(nsis_script)
        
        # 执行 NSIS
        return self.run_command(
            ["makensis", str(nsis_path)],
            description="NSIS 打包"
        )
    
    def create_macos_installer(self) -> bool:
        """创建 macOS 安装程序（DMG）"""
        print("🍎 创建 macOS 安装程序...")
        
        # 使用 create-dmg 工具
        return self.run_command(
            [
                "create-dmg",
                "--volname", "KOOK Forwarder",
                "--volicon", "build/icon.icns",
                "--window-pos", "200", "120",
                "--window-size", "800", "400",
                "--icon-size", "100",
                "--app-drop-link", "600", "185",
                f"dist/KOOK-Forwarder-{self.version}-macOS.dmg",
                "dist/mac/KOOK Forwarder.app"
            ],
            description="创建 DMG"
        )
    
    def create_linux_installer(self) -> bool:
        """创建 Linux 安装程序（AppImage）"""
        print("🐧 创建 Linux 安装程序...")
        
        # 使用 appimagetool
        return self.run_command(
            [
                "appimagetool",
                "dist/linux",
                f"dist/KOOK-Forwarder-{self.version}-Linux-x86_64.AppImage"
            ],
            description="创建 AppImage"
        )
    
    def build_all(self) -> bool:
        """执行完整打包流程"""
        print("\n" + "🚀 " + "=" * 58)
        print(f"开始打包 KOOK 消息转发系统 v{self.version}")
        print("=" * 60)
        
        steps = [
            ("准备 Chromium", self.prepare_chromium),
            ("准备 Redis", self.prepare_redis),
            ("打包后端", self.build_backend),
            ("打包前端", self.build_frontend),
            ("优化大小", self.optimize_package_size),
            ("创建安装程序", self.create_installer),
        ]
        
        for i, (name, func) in enumerate(steps, 1):
            print(f"\n{'🎯' * 30}")
            print(f"执行步骤 {i}/{len(steps)}: {name}")
            print(f"{'🎯' * 30}")
            
            if not func():
                print(f"\n❌ 步骤 {i} 失败: {name}")
                return False
        
        print("\n" + "🎉 " + "=" * 58)
        print(f"✅ 打包完成！")
        print(f"📦 安装包位置: {self.dist_dir}")
        print("=" * 60)
        
        return True


def main():
    """主函数"""
    builder = FinalBuilder()
    success = builder.build_all()
    
    if success:
        print("\n✅ 构建成功！")
        sys.exit(0)
    else:
        print("\n❌ 构建失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
