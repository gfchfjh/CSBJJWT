"""
PyInstaller打包脚本
将Python后端打包为可执行文件（包含Chromium浏览器和Redis）
v1.12.0+ 自动打包Playwright Chromium
v1.13.0+ 自动打包Redis (P0-1, P0-2, P0-3优化)
"""
import PyInstaller.__main__
import sys
import os
import subprocess
import shutil
import zipfile
import urllib.request
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
REDIS_DIR = ROOT_DIR / "redis"

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


def prepare_redis():
    """
    ✅ v1.13.0新增：准备Redis二进制文件用于打包 (P0-2优化)
    下载或复制Redis二进制文件到redis/目录
    
    Returns:
        redis_path: Redis目录路径，None表示失败
    """
    print("\n" + "=" * 50)
    print("📥 准备Redis二进制文件...")
    print("=" * 50)
    
    try:
        # 确保redis目录存在
        REDIS_DIR.mkdir(exist_ok=True)
        
        if sys.platform == "win32":
            # Windows: 下载Redis
            print("正在下载Windows版Redis...")
            
            redis_exe = REDIS_DIR / "redis-server.exe"
            redis_cli = REDIS_DIR / "redis-cli.exe"
            
            # 如果已存在，跳过下载
            if redis_exe.exists() and redis_cli.exists():
                print(f"✅ Redis已存在: {REDIS_DIR}")
                return REDIS_DIR
            
            # 下载Redis（使用tporadowski/redis的预编译版本）
            redis_url = "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
            zip_path = REDIS_DIR / "redis.zip"
            
            print(f"   下载地址: {redis_url}")
            print("   提示: 如果下载失败，请手动下载并解压到redis/目录")
            
            try:
                urllib.request.urlretrieve(redis_url, zip_path)
                print("✅ Redis下载完成")
                
                # 解压
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(REDIS_DIR)
                
                # 删除zip文件
                zip_path.unlink()
                
                print(f"✅ Redis解压完成: {REDIS_DIR}")
                return REDIS_DIR
                
            except Exception as download_error:
                print(f"❌ Redis下载失败: {str(download_error)}")
                print("   解决方案:")
                print("   1. 手动下载: https://github.com/tporadowski/redis/releases")
                print(f"   2. 解压到: {REDIS_DIR}")
                print("   3. 重新运行打包脚本")
                return None
                
        elif sys.platform == "darwin":
            # macOS: 使用Homebrew安装的Redis
            print("检查macOS系统Redis...")
            
            # 检查是否已安装Redis
            redis_path = shutil.which("redis-server")
            if redis_path:
                print(f"✅ 找到系统Redis: {redis_path}")
                
                # 复制到redis目录
                shutil.copy(redis_path, REDIS_DIR / "redis-server")
                
                redis_cli_path = shutil.which("redis-cli")
                if redis_cli_path:
                    shutil.copy(redis_cli_path, REDIS_DIR / "redis-cli")
                
                print(f"✅ Redis已复制到: {REDIS_DIR}")
                return REDIS_DIR
            else:
                print("❌ 未找到Redis")
                print("   解决方案:")
                print("   1. 安装Redis: brew install redis")
                print("   2. 重新运行打包脚本")
                return None
                
        else:
            # Linux: 使用系统Redis或从源码编译
            print("检查Linux系统Redis...")
            
            redis_path = shutil.which("redis-server")
            if redis_path:
                print(f"✅ 找到系统Redis: {redis_path}")
                
                # 复制到redis目录
                shutil.copy(redis_path, REDIS_DIR / "redis-server")
                
                redis_cli_path = shutil.which("redis-cli")
                if redis_cli_path:
                    shutil.copy(redis_cli_path, REDIS_DIR / "redis-cli")
                
                print(f"✅ Redis已复制到: {REDIS_DIR}")
                return REDIS_DIR
            else:
                print("❌ 未找到Redis")
                print("   解决方案:")
                print("   1. 安装Redis: sudo apt-get install redis-server")
                print("   2. 重新运行打包脚本")
                return None
                
    except Exception as e:
        print(f"❌ 准备Redis失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def build_backend():
    """打包后端"""
    
    print("=" * 50)
    print("🚀 开始打包KOOK消息转发系统后端...")
    print("=" * 50)
    
    # ✅ v1.13.0优化：准备Chromium浏览器 (P0-1)
    chromium_path = prepare_chromium()
    
    # ✅ v1.13.0新增：准备Redis (P0-2)
    redis_path = prepare_redis()
    
    # ✅ v1.13.0完善：PyInstaller参数 (P0-3)
    args = [
        str(BACKEND_DIR / "app" / "main.py"),
        
        # 输出配置
        "--name=kook-forwarder-backend",
        "--onefile",
        "--clean",
        
        # 数据文件（仅在目录存在时添加）
        # Redis将在后面单独处理
        
        # ✅ v1.13.0完善：隐藏导入（P0-3优化）
        "--hidden-import=playwright",
        "--hidden-import=playwright.sync_api",
        "--hidden-import=playwright.async_api",
        "--hidden-import=playwright._impl._driver",
        "--hidden-import=discord_webhook",
        "--hidden-import=telegram",
        "--hidden-import=telegram.ext",
        "--hidden-import=lark_oapi",
        "--hidden-import=aiohttp",
        "--hidden-import=aiosqlite",
        "--hidden-import=loguru",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=cryptography",
        "--hidden-import=cryptography.fernet",
        "--hidden-import=ddddocr",  # v1.13.0新增：本地OCR
        "--hidden-import=redis",
        "--hidden-import=pydantic",
        "--hidden-import=pydantic_settings",
        "--hidden-import=fastapi",
        "--hidden-import=uvicorn",
        "--hidden-import=bs4",  # BeautifulSoup4
        "--hidden-import=lxml",
        
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
    
    # ✅ v1.13.0优化：打包Chromium浏览器 (P0-1)
    separator = ";" if sys.platform == "win32" else ":"
    
    if chromium_path and chromium_path.exists():
        print(f"\n✅ 将Chromium打包进可执行文件...")
        args.append(f"--add-data={chromium_path}{separator}playwright/chromium")
        print(f"   已添加: {chromium_path}")
    else:
        print("\n⚠️  未打包Chromium，用户首次运行时需要下载")
        print("   建议: 手动运行 'playwright install chromium' 后重新打包")
    
    # ✅ v1.13.0新增：打包Redis (P0-2)
    if redis_path and redis_path.exists():
        print(f"\n✅ 将Redis打包进可执行文件...")
        args.append(f"--add-data={redis_path}{separator}redis")
        print(f"   已添加: {redis_path}")
        
        # 列出Redis文件
        redis_files = list(redis_path.glob("redis-*"))
        if redis_files:
            print(f"   Redis文件: {[f.name for f in redis_files]}")
    else:
        print("\n⚠️  未打包Redis，用户需要单独安装")
        print("   建议: 安装Redis后重新打包")
    
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
        print("📝 打包总结:")
        print("=" * 50)
        
        # 打包状态总结
        print("\n✅ 打包组件状态:")
        print(f"   • Chromium浏览器: {'✅ 已打包' if chromium_path else '⚠️ 未打包'}")
        print(f"   • Redis服务: {'✅ 已打包' if redis_path else '⚠️ 未打包'}")
        print(f"   • Python运行时: ✅ 已打包")
        print(f"   • 所有依赖库: ✅ 已打包")
        
        print("\n📝 下一步操作:")
        if not chromium_path:
            print("   1. ⚠️  用户首次运行时需要执行: playwright install chromium")
        if not redis_path:
            print("   2. ⚠️  用户需要单独安装Redis")
        print("   3. ✅ 使用electron-builder打包前端")
        print("   4. ✅ 测试可执行文件是否能正常运行")
        print("   5. ✅ 运行一键构建脚本: ./build_installer.sh 或 build_installer.bat")
        
        print("\n💡 提示:")
        print("   完整打包流程请使用:")
        print("   • Linux/macOS: ./build_installer.sh")
        print("   • Windows: build_installer.bat")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 打包失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = build_backend()
    sys.exit(0 if success else 1)
