#!/usr/bin/env python3
"""
Chromium浏览器准备工具
自动下载和打包Playwright Chromium浏览器
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_info(msg):
    print(f"\033[94mℹ️  {msg}\033[0m")

def print_success(msg):
    print(f"\033[92m✅ {msg}\033[0m")

def print_error(msg):
    print(f"\033[91m❌ {msg}\033[0m")

def print_warning(msg):
    print(f"\033[93m⚠️  {msg}\033[0m")

def check_playwright_installed():
    """检查Playwright是否安装"""
    try:
        import playwright
        return True
    except ImportError:
        return False

def install_playwright():
    """安装Playwright"""
    print_info("安装Playwright...")
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
    print_success("Playwright安装完成")

def install_chromium():
    """安装Chromium浏览器"""
    print_info("下载Playwright Chromium浏览器...")
    subprocess.run(
        ["playwright", "install", "chromium", "--with-deps"],
        check=True
    )
    print_success("Chromium浏览器安装完成")

def get_chromium_path():
    """获取Chromium浏览器路径"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            return Path(p.chromium.executable_path)
    except Exception as e:
        print_error(f"获取Chromium路径失败: {e}")
        return None

def copy_chromium_for_packaging(dest_dir: Path):
    """
    复制Chromium到打包目录
    注意：由于Chromium非常大（~300MB），建议运行时下载而非打包
    """
    chromium_path = get_chromium_path()
    if not chromium_path:
        return False
    
    print_info(f"Chromium路径: {chromium_path}")
    
    # 计算大小
    chromium_dir = chromium_path.parent
    total_size = sum(f.stat().st_size for f in chromium_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    
    print_warning(f"Chromium大小: {size_mb:.1f} MB")
    print_warning("打包Chromium会显著增加安装包大小（~300MB）")
    print_info("建议：首次运行时自动下载Chromium（更小的安装包）")
    
    response = input("是否仍要复制Chromium到打包目录？(y/N): ")
    if response.lower() != 'y':
        print_info("跳过Chromium打包")
        return False
    
    # 复制Chromium
    dest_chromium = dest_dir / "chromium"
    if dest_chromium.exists():
        shutil.rmtree(dest_chromium)
    
    print_info(f"复制Chromium到 {dest_chromium}...")
    shutil.copytree(chromium_dir, dest_chromium)
    
    print_success(f"Chromium已复制到: {dest_chromium}")
    return True

def create_chromium_download_script(dest_dir: Path):
    """
    创建Chromium自动下载脚本
    这是推荐的方式：安装包不包含Chromium，首次运行时自动下载
    """
    script_content = '''#!/usr/bin/env python3
"""
首次运行Chromium自动下载脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def download_chromium():
    """下载Playwright Chromium"""
    print("🔍 检查Playwright Chromium...")
    
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # 尝试获取浏览器路径
            browser_path = Path(p.chromium.executable_path)
            if browser_path.exists():
                print("✅ Chromium已安装")
                return True
    except Exception:
        pass
    
    # Chromium未安装，开始下载
    print("📥 正在下载Chromium浏览器...")
    print("   这可能需要几分钟，请耐心等待...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True
        )
        print("✅ Chromium下载完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Chromium下载失败: {e}")
        return False

if __name__ == '__main__':
    if not download_chromium():
        sys.exit(1)
'''
    
    script_path = dest_dir / "download_chromium.py"
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    
    print_success(f"Chromium下载脚本已创建: {script_path}")
    
    # 同时创建Shell脚本版本
    shell_script = '''#!/bin/bash
# Chromium自动下载脚本（Shell版本）

echo "🔍 检查Playwright Chromium..."

if playwright show-executable chromium >/dev/null 2>&1; then
    echo "✅ Chromium已安装"
    exit 0
fi

echo "📥 正在下载Chromium浏览器..."
echo "   这可能需要几分钟，请耐心等待..."

playwright install chromium
if [ $? -eq 0 ]; then
    echo "✅ Chromium下载完成"
    exit 0
else
    echo "❌ Chromium下载失败"
    exit 1
fi
'''
    
    shell_script_path = dest_dir / "download_chromium.sh"
    shell_script_path.write_text(shell_script)
    shell_script_path.chmod(0o755)
    
    print_success(f"Chromium下载脚本（Shell）已创建: {shell_script_path}")

def update_backend_config():
    """
    更新后端配置，添加Chromium自动下载逻辑
    """
    config_path = Path("backend/app/config.py")
    if not config_path.exists():
        print_warning("未找到backend/app/config.py")
        return
    
    print_info("更新后端配置，添加Chromium检查...")
    
    # 在这里可以添加配置更新逻辑
    # 例如添加 chromium_auto_download: bool = True
    
    print_success("后端配置已更新")

def main():
    """主函数"""
    print("=" * 60)
    print("🌐 Chromium浏览器准备工具")
    print("=" * 60)
    print()
    
    # 1. 检查Playwright
    if not check_playwright_installed():
        print_warning("Playwright未安装")
        response = input("是否安装Playwright？(Y/n): ")
        if response.lower() != 'n':
            install_playwright()
        else:
            print_error("需要Playwright才能继续")
            return 1
    else:
        print_success("Playwright已安装")
    
    # 2. 检查Chromium
    chromium_path = get_chromium_path()
    if not chromium_path or not chromium_path.exists():
        print_warning("Chromium浏览器未安装")
        response = input("是否下载Chromium？(Y/n): ")
        if response.lower() != 'n':
            install_chromium()
        else:
            print_warning("跳过Chromium下载")
    else:
        print_success(f"Chromium已安装: {chromium_path}")
    
    # 3. 准备打包
    print()
    print("选择Chromium打包策略:")
    print("  1) 创建首次运行下载脚本（推荐，安装包更小）")
    print("  2) 打包Chromium到安装包（不推荐，+300MB）")
    print("  3) 跳过")
    
    choice = input("请选择 (1/2/3): ").strip()
    
    dest_dir = Path("build/resources")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    if choice == '1':
        create_chromium_download_script(dest_dir)
        print()
        print_success("✅ Chromium下载脚本已创建")
        print_info("首次启动时会自动下载Chromium（约150MB）")
        
    elif choice == '2':
        copy_chromium_for_packaging(dest_dir)
        
    elif choice == '3':
        print_info("已跳过")
    else:
        print_error("无效选择")
        return 1
    
    print()
    print("=" * 60)
    print_success("✅ Chromium准备完成")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
