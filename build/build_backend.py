"""
PyInstaller打包脚本
将Python后端打包为可执行文件（包含Chromium浏览器）
v1.12.0+ 新增：自动打包Playwright Chromium，实现真正的"零依赖"
"""
import PyInstaller.__main__
import sys
import os
import subprocess
import shutil
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

def prepare_chromium():
    """
    准备Chromium浏览器用于打包
    下载Playwright Chromium并将其添加到打包资源
    
    Returns:
        chromium_path: Chromium浏览器路径，None表示失败
    """
    print("\n" + "=" * 50)
    print("📥 准备Chromium浏览器...")
    print("=" * 50)
    
    try:
        # 1. 安装Playwright Chromium
        print("正在下载Chromium浏览器（约170MB，请耐心等待）...")
        result = subprocess.run(
            ["playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode != 0:
            print(f"⚠️  Playwright安装警告: {result.stderr}")
        
        # 2. 查找Chromium路径
        # 不同操作系统的Playwright缓存路径
        if sys.platform == "win32":
            playwright_cache = Path.home() / "AppData" / "Local" / "ms-playwright"
        elif sys.platform == "darwin":
            playwright_cache = Path.home() / "Library" / "Caches" / "ms-playwright"
        else:  # Linux
            playwright_cache = Path.home() / ".cache" / "ms-playwright"
        
        # 查找chromium目录
        chromium_dirs = list(playwright_cache.glob("chromium-*"))
        
        if not chromium_dirs:
            print("⚠️  未找到Chromium，尝试环境变量路径...")
            # 尝试从环境变量获取
            env_path = os.getenv("PLAYWRIGHT_BROWSERS_PATH")
            if env_path:
                playwright_cache = Path(env_path)
                chromium_dirs = list(playwright_cache.glob("chromium-*"))
        
        if chromium_dirs:
            chromium_path = chromium_dirs[0]  # 取最新版本
            print(f"✅ 找到Chromium: {chromium_path}")
            print(f"   大小: {sum(f.stat().st_size for f in chromium_path.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")
            return chromium_path
        else:
            print("❌ 未找到Chromium浏览器")
            print("   提示: 请手动运行 'playwright install chromium'")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Chromium下载超时（超过10分钟）")
        print("   建议: 手动下载或检查网络连接")
        return None
    except FileNotFoundError:
        print("❌ 未找到playwright命令")
        print("   请先安装: pip install playwright")
        return None
    except Exception as e:
        print(f"❌ 准备Chromium失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def build_backend():
    """打包后端"""
    
    print("=" * 50)
    print("🚀 开始打包KOOK消息转发系统后端...")
    print("=" * 50)
    
    # 准备Chromium浏览器
    chromium_path = prepare_chromium()
    
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
        
        # 排除不需要的模块（减小体积）
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
    
    # ✅ 新增：如果找到Chromium，打包进可执行文件
    if chromium_path and chromium_path.exists():
        print(f"\n✅ 将Chromium打包进可执行文件...")
        separator = ";" if sys.platform == "win32" else ":"
        args.append(f"--add-data={chromium_path}{separator}playwright/chromium")
        print(f"   已添加: {chromium_path}")
    else:
        print("\n⚠️  未打包Chromium，用户首次运行时需要下载")
        print("   建议: 手动运行 'playwright install chromium' 后重新打包")
    
    # Windows特定配置
    if sys.platform == "win32":
        args.append("--console")
        args.append("--icon=NONE")
    
    try:
        print("\n" + "=" * 50)
        print("📦 开始PyInstaller打包...")
        print("=" * 50)
        
        PyInstaller.__main__.run(args)
        
        print("\n" + "=" * 50)
        print("✅ 打包成功！")
        print("=" * 50)
        print(f"\n📁 可执行文件位置: {ROOT_DIR / 'build' / 'dist'}")
        
        # 显示文件大小
        exe_path = ROOT_DIR / 'build' / 'dist' / 'kook-forwarder-backend'
        if sys.platform == "win32":
            exe_path = exe_path.with_suffix('.exe')
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / 1024 / 1024
            print(f"📊 文件大小: {size_mb:.1f} MB")
        
        print("\n" + "=" * 50)
        print("📝 下一步:")
        print("=" * 50)
        if chromium_path:
            print("✅ 1. Chromium已打包，无需额外操作")
        else:
            print("⚠️  1. 用户首次运行时需要执行: playwright install chromium")
        print("✅ 2. 确保Redis已安装到 redis/ 目录")
        print("✅ 3. 使用electron-builder打包前端")
        print("✅ 4. 测试可执行文件是否能正常运行")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 打包失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = build_backend()
    sys.exit(0 if success else 1)
