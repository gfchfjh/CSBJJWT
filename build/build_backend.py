"""
PyInstaller打包脚本
将Python后端打包为可执行文件
"""
import PyInstaller.__main__
import sys
import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

def build_backend():
    """打包后端"""
    
    print("=" * 50)
    print("开始打包KOOK消息转发系统后端...")
    print("=" * 50)
    
    # PyInstaller参数
    args = [
        str(BACKEND_DIR / "app" / "main.py"),
        
        # 输出配置
        "--name=kook-forwarder-backend",
        "--onefile",
        "--clean",
        
        # 数据文件
        f"--add-data={ROOT_DIR / 'redis'}:redis",
        
        # 隐藏导入
        "--hidden-import=playwright",
        "--hidden-import=playwright.sync_api",
        "--hidden-import=playwright.async_api",
        "--hidden-import=discord_webhook",
        "--hidden-import=telegram",
        "--hidden-import=telegram.ext",
        "--hidden-import=lark_oapi",
        "--hidden-import=aiohttp",
        "--hidden-import=aiosqlite",
        "--hidden-import=loguru",
        "--hidden-import=PIL",
        "--hidden-import=cryptography",
        
        # 排除不需要的模块
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--exclude-module=numpy",
        "--exclude-module=tkinter",
        
        # 输出目录
        f"--distpath={ROOT_DIR / 'build' / 'dist'}",
        f"--workpath={ROOT_DIR / 'build' / 'work'}",
        f"--specpath={ROOT_DIR / 'build'}",
    ]
    
    # Windows特定配置
    if sys.platform == "win32":
        args.append("--console")
        args.append("--icon=NONE")
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 50)
        print("✅ 打包成功！")
        print(f"可执行文件位置: {ROOT_DIR / 'build' / 'dist'}")
        print("=" * 50)
        print("\n下一步:")
        print("1. 确保Redis已安装到 redis/ 目录")
        print("2. 运行 playwright install chromium")
        print("3. 使用electron-builder打包前端")
    except Exception as e:
        print(f"\n❌ 打包失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = build_backend()
    sys.exit(0 if success else 1)
