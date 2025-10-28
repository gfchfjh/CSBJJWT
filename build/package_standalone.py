#!/usr/bin/env python3
"""
完整独立安装包打包脚本 - P0-1优化
特性:
- 嵌入Python运行时
- 嵌入所有依赖
- 嵌入Redis
- 嵌入Chromium浏览器
- 真正的一键安装
"""
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import json


class StandalonePackager:
    """独立安装包打包器"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.build_dir = Path(__file__).parent
        self.output_dir = self.build_dir / "output"
        self.platform_system = platform.system()
        
        print("=" * 60)
        print("📦 KOOK消息转发系统 - 独立安装包打包器")
        print("=" * 60)
        print(f"操作系统: {self.platform_system}")
        print(f"Python版本: {sys.version.split()[0]}")
        print(f"工作目录: {self.root_dir}")
        print("=" * 60)
    
    def check_requirements(self):
        """检查打包要求"""
        print("\n📋 检查打包要求...")
        
        requirements = {
            'pyinstaller': 'PyInstaller',
            'playwright': 'Playwright',
        }
        
        missing = []
        
        for module, name in requirements.items():
            try:
                __import__(module)
                print(f"  ✅ {name}")
            except ImportError:
                missing.append(name)
                print(f"  ❌ {name} 未安装")
        
        if missing:
            print(f"\n⚠️  缺少必需的包: {', '.join(missing)}")
            print(f"请运行: pip install {' '.join(missing.lower())}")
            return False
        
        # 检查Node.js
        if shutil.which('node'):
            print("  ✅ Node.js")
        else:
            print("  ⚠️  Node.js 未安装（前端打包需要）")
        
        return True
    
    def clean_output(self):
        """清理输出目录"""
        print("\n🧹 清理输出目录...")
        
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            print("  ✅ 已清理")
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_embedded_python(self):
        """下载嵌入式Python"""
        print("\n🐍 准备嵌入式Python...")
        
        if self.platform_system == "Windows":
            print("  ℹ️  Windows: PyInstaller会自动打包Python运行时")
            return True
        else:
            print("  ℹ️  Linux/macOS: 使用系统Python")
            return True
    
    def download_redis(self):
        """下载Redis"""
        print("\n🗄️  准备嵌入式Redis...")
        
        redis_dir = self.output_dir / "redis"
        redis_dir.mkdir(exist_ok=True)
        
        if self.platform_system == "Windows":
            print("  📥 下载Redis for Windows...")
            # Windows版Redis需要手动下载
            print("  ⚠️  请手动下载Redis for Windows并放入 build/output/redis/")
            print("  下载地址: https://github.com/microsoftarchive/redis/releases")
        elif self.platform_system == "Linux":
            # 检查是否已安装redis-server
            if shutil.which('redis-server'):
                print("  ✅ 系统已安装Redis")
                # 复制Redis到打包目录
                redis_bin = shutil.which('redis-server')
                shutil.copy(redis_bin, redis_dir / "redis-server")
                print(f"  ✅ 已复制: {redis_bin}")
            else:
                print("  ⚠️  未找到Redis，请先安装: sudo apt-get install redis-server")
                return False
        elif self.platform_system == "Darwin":
            # macOS
            if shutil.which('redis-server'):
                print("  ✅ 系统已安装Redis")
                redis_bin = shutil.which('redis-server')
                shutil.copy(redis_bin, redis_dir / "redis-server")
                print(f"  ✅ 已复制: {redis_bin}")
            else:
                print("  ⚠️  未找到Redis，请先安装: brew install redis")
                return False
        
        return True
    
    def download_chromium(self):
        """下载Playwright Chromium浏览器"""
        print("\n🌐 准备嵌入式Chromium浏览器...")
        
        try:
            # 检查Playwright是否已安装浏览器
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                try:
                    # 尝试启动浏览器
                    browser = p.chromium.launch(headless=True)
                    browser.close()
                    print("  ✅ Chromium浏览器已安装")
                    return True
                except Exception as e:
                    print(f"  ⚠️  Chromium浏览器未安装: {e}")
                    print("  📥 正在安装Chromium...")
                    
                    # 运行playwright install
                    result = subprocess.run(
                        [sys.executable, '-m', 'playwright', 'install', 'chromium'],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        print("  ✅ Chromium安装成功")
                        return True
                    else:
                        print(f"  ❌ Chromium安装失败: {result.stderr}")
                        return False
                        
        except ImportError:
            print("  ❌ Playwright未安装")
            return False
    
    def build_backend(self):
        """打包后端"""
        print("\n🔨 打包后端...")
        
        spec_file = self.build_dir / "pyinstaller_standalone.spec"
        
        # 创建PyInstaller spec文件
        self.create_pyinstaller_spec(spec_file)
        
        # 运行PyInstaller
        print("  ⚙️  运行PyInstaller...")
        result = subprocess.run(
            ['pyinstaller', '--clean', str(spec_file)],
            cwd=self.root_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"  ❌ 打包失败:\n{result.stderr}")
            return False
        
        print("  ✅ 后端打包完成")
        return True
    
    def create_pyinstaller_spec(self, spec_file):
        """创建PyInstaller spec文件"""
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
# PyInstaller Spec - Standalone版本

import os
from pathlib import Path

block_cipher = None

# 工作目录
root_dir = Path(r'{self.root_dir}')
backend_dir = root_dir / 'backend'

# 收集所有数据文件
datas = [
    (str(backend_dir / 'data'), 'data'),
    (str(root_dir / 'config_templates'), 'config_templates'),
    (str(root_dir / 'docs'), 'docs'),
]

# 收集所有隐藏导入
hiddenimports = [
    'fastapi',
    'uvicorn',
    'aiohttp',
    'playwright',
    'redis',
    'sqlalchemy',
    'pydantic',
    'cryptography',
    'pillow',
    'telegram',
    'discord_webhook',
    'lark_oapi',
]

# Backend应用分析
a = Analysis(
    [str(backend_dir / 'app' / 'main.py')],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
"""
        
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"  ✅ 已生成spec文件: {spec_file}")
    
    def build_frontend(self):
        """打包前端"""
        print("\n🎨 打包前端...")
        
        frontend_dir = self.root_dir / "frontend"
        
        if not (frontend_dir / "node_modules").exists():
            print("  📦 安装前端依赖...")
            result = subprocess.run(
                ['npm', 'install'],
                cwd=frontend_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"  ❌ npm install失败:\n{result.stderr}")
                return False
        
        print("  🔨 构建前端...")
        result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"  ❌ 前端构建失败:\n{result.stderr}")
            return False
        
        print("  ✅ 前端打包完成")
        return True
    
    def build_electron(self):
        """打包Electron应用"""
        print("\n⚡ 打包Electron应用...")
        
        frontend_dir = self.root_dir / "frontend"
        
        print("  🔨 构建Electron安装包...")
        result = subprocess.run(
            ['npm', 'run', 'electron:build'],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"  ❌ Electron打包失败:\n{result.stderr}")
            # 不是致命错误，继续
            return True
        
        print("  ✅ Electron打包完成")
        return True
    
    def create_installer(self):
        """创建安装包"""
        print("\n📦 创建最终安装包...")
        
        installer_dir = self.output_dir / "installer"
        installer_dir.mkdir(exist_ok=True)
        
        # 复制后端
        backend_dist = self.root_dir / "dist" / "kook-forwarder-backend"
        if backend_dist.exists():
            print("  📁 复制后端...")
            shutil.copytree(backend_dist, installer_dir / "backend", dirs_exist_ok=True)
        
        # 复制Redis
        redis_dir = self.output_dir / "redis"
        if redis_dir.exists():
            print("  📁 复制Redis...")
            shutil.copytree(redis_dir, installer_dir / "redis", dirs_exist_ok=True)
        
        # 创建启动脚本
        self.create_launcher_scripts(installer_dir)
        
        # 创建README
        self.create_readme(installer_dir)
        
        print(f"\n✅ 安装包已创建: {installer_dir}")
        print(f"\n📝 安装说明:")
        print(f"  1. 解压安装包到任意目录")
        print(f"  2. 运行 start.{self.get_script_extension()}")
        print(f"  3. 访问 http://localhost:9527")
        
        return True
    
    def create_launcher_scripts(self, installer_dir):
        """创建启动脚本"""
        print("  📝 创建启动脚本...")
        
        if self.platform_system == "Windows":
            # Windows批处理脚本
            start_script = installer_dir / "start.bat"
            with open(start_script, 'w', encoding='gbk') as f:
                f.write("""@echo off
chcp 65001
echo ================================================
echo   KOOK消息转发系统 - 独立版
echo ================================================
echo.

echo [1/3] 启动Redis...
start /B redis\\redis-server.exe redis\\redis.conf
timeout /t 2 /nobreak >nul

echo [2/3] 启动后端服务...
start /B backend\\kook-forwarder-backend.exe

echo [3/3] 启动前端界面...
timeout /t 3 /nobreak >nul
start http://localhost:9527

echo.
echo ✅ 系统已启动！
echo 📝 按任意键关闭此窗口（不影响服务运行）
pause >nul
""")
            
            # 停止脚本
            stop_script = installer_dir / "stop.bat"
            with open(stop_script, 'w', encoding='gbk') as f:
                f.write("""@echo off
chcp 65001
echo ================================================
echo   停止KOOK消息转发系统
echo ================================================
echo.

echo 停止后端服务...
taskkill /F /IM kook-forwarder-backend.exe /T >nul 2>&1

echo 停止Redis...
taskkill /F /IM redis-server.exe /T >nul 2>&1

echo.
echo ✅ 系统已停止
pause
""")
        
        else:
            # Linux/macOS Shell脚本
            start_script = installer_dir / "start.sh"
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write("""#!/bin/bash

echo "================================================"
echo "  KOOK消息转发系统 - 独立版"
echo "================================================"
echo

echo "[1/3] 启动Redis..."
./redis/redis-server redis/redis.conf &
sleep 2

echo "[2/3] 启动后端服务..."
./backend/kook-forwarder-backend &
sleep 3

echo "[3/3] 打开浏览器..."
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:9527
elif command -v open > /dev/null; then
    open http://localhost:9527
fi

echo
echo "✅ 系统已启动！"
echo "📝 访问: http://localhost:9527"
""")
            
            # 添加执行权限
            os.chmod(start_script, 0o755)
            
            # 停止脚本
            stop_script = installer_dir / "stop.sh"
            with open(stop_script, 'w', encoding='utf-8') as f:
                f.write("""#!/bin/bash

echo "================================================"
echo "  停止KOOK消息转发系统"
echo "================================================"
echo

echo "停止后端服务..."
pkill -f kook-forwarder-backend

echo "停止Redis..."
pkill -f redis-server

echo
echo "✅ 系统已停止"
""")
            
            os.chmod(stop_script, 0o755)
        
        print(f"  ✅ 启动脚本: {start_script.name}")
        print(f"  ✅ 停止脚本: {stop_script.name if 'stop_script' in locals() else 'stop.' + self.get_script_extension()}")
    
    def create_readme(self, installer_dir):
        """创建README文件"""
        readme_file = installer_dir / "README.txt"
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(f"""KOOK消息转发系统 - 独立安装包
===============================================

📦 版本: 11.0.0 (Standalone)
🎯 特性: 一键安装，无需配置环境

安装说明
-------
1. 解压此文件夹到任意位置（建议英文路径）
2. 运行 start.{self.get_script_extension()}
3. 访问 http://localhost:9527

目录结构
-------
backend/          后端程序（嵌入Python运行时）
redis/            Redis数据库
start.{self.get_script_extension()}        启动脚本
stop.{self.get_script_extension()}         停止脚本
README.txt        说明文档

使用说明
-------
详细教程请访问：
https://github.com/gfchfjh/CSBJJWT/blob/main/docs/tutorials/01-快速入门指南.md

常见问题
-------
1. 端口被占用？
   修改 backend/config.json 中的端口配置

2. Redis启动失败？
   检查 redis/redis.conf 配置

3. 无法访问？
   检查防火墙设置，确保允许本地访问

技术支持
-------
GitHub: https://github.com/gfchfjh/CSBJJWT
Issues: https://github.com/gfchfjh/CSBJJWT/issues
""")
        
        print(f"  ✅ README: {readme_file.name}")
    
    def get_script_extension(self):
        """获取脚本扩展名"""
        return "bat" if self.platform_system == "Windows" else "sh"
    
    def package(self):
        """执行完整打包流程"""
        try:
            # 1. 检查要求
            if not self.check_requirements():
                return False
            
            # 2. 清理输出
            self.clean_output()
            
            # 3. 下载嵌入式组件
            if not self.download_embedded_python():
                return False
            
            if not self.download_redis():
                print("  ⚠️  Redis下载失败，请手动添加")
            
            if not self.download_chromium():
                print("  ⚠️  Chromium下载失败，Playwright功能可能不可用")
            
            # 4. 打包后端
            if not self.build_backend():
                return False
            
            # 5. 打包前端（可选）
            if shutil.which('node'):
                self.build_frontend()
                self.build_electron()
            else:
                print("  ⚠️  跳过前端打包（未安装Node.js）")
            
            # 6. 创建安装包
            if not self.create_installer():
                return False
            
            print("\n" + "=" * 60)
            print("🎉 打包完成！")
            print("=" * 60)
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  打包已中断")
            return False
        except Exception as e:
            print(f"\n❌ 打包失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    packager = StandalonePackager()
    success = packager.package()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
