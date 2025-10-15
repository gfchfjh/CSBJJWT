"""
后端打包脚本
使用PyInstaller打包Python后端为可执行文件
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"

def clean_build():
    """清理构建目录"""
    print("🧹 清理构建目录...")
    
    dirs_to_clean = [
        BACKEND_DIR / "build",
        BACKEND_DIR / "dist",
        DIST_DIR / "backend"
    ]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   已删除: {dir_path}")
    
    print("✅ 清理完成\n")

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    
    requirements_file = BACKEND_DIR / "requirements.txt"
    if not requirements_file.exists():
        print("❌ 未找到 requirements.txt")
        return False
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True
        )
        print("✅ 依赖安装完成\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def install_playwright():
    """安装Playwright浏览器"""
    print("🌐 安装Playwright浏览器...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True
        )
        print("✅ Playwright安装完成\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Playwright安装失败: {e}")
        return False

def build_with_pyinstaller():
    """使用PyInstaller打包"""
    print("🔨 开始打包后端...")
    
    # PyInstaller配置
    entry_point = BACKEND_DIR / "app" / "main.py"
    icon_file = BUILD_DIR / "icon.ico"
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个文件
        "--name", "kook-forwarder-backend",
        "--distpath", str(DIST_DIR / "backend"),
        "--workpath", str(BACKEND_DIR / "build"),
        "--specpath", str(BACKEND_DIR),
        "--clean",
        
        # 添加数据文件
        "--add-data", f"{BACKEND_DIR / 'app'}:app",
        
        # 隐藏导入
        "--hidden-import", "playwright",
        "--hidden-import", "fastapi",
        "--hidden-import", "uvicorn",
        "--hidden-import", "redis",
        "--hidden-import", "aiohttp",
        "--hidden-import", "PIL",
        
        # 排除不必要的模块（减小体积）
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "pytest",
        
        # 控制台选项
        "--console",  # 保留控制台（便于查看日志）
        
        # 图标
        # "--icon", str(icon_file) if icon_file.exists() else "",
        
        str(entry_point)
    ]
    
    try:
        subprocess.run(cmd, check=True, cwd=str(BACKEND_DIR))
        print("✅ 后端打包完成\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        return False

def copy_additional_files():
    """复制额外文件"""
    print("📋 复制额外文件...")
    
    # 复制Redis（如果需要内置）
    # redis_dir = ROOT_DIR / "redis"
    # if redis_dir.exists():
    #     shutil.copytree(redis_dir, DIST_DIR / "redis", dirs_exist_ok=True)
    #     print("   已复制: Redis")
    
    # 复制文档
    docs_dir = ROOT_DIR / "docs"
    if docs_dir.exists():
        shutil.copytree(docs_dir, DIST_DIR / "docs", dirs_exist_ok=True)
        print("   已复制: 文档")
    
    print("✅ 文件复制完成\n")

def main():
    """主函数"""
    print("=" * 60)
    print("KOOK消息转发系统 - 后端打包工具")
    print("=" * 60)
    print()
    
    # 1. 清理构建目录
    clean_build()
    
    # 2. 安装依赖
    if not install_dependencies():
        print("❌ 构建失败：依赖安装失败")
        return 1
    
    # 3. 安装Playwright
    if not install_playwright():
        print("⚠️  警告：Playwright安装失败，打包仍然继续")
    
    # 4. 打包
    if not build_with_pyinstaller():
        print("❌ 构建失败：打包失败")
        return 1
    
    # 5. 复制额外文件
    copy_additional_files()
    
    # 完成
    print("=" * 60)
    print("🎉 构建完成！")
    print(f"📦 输出目录: {DIST_DIR}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
