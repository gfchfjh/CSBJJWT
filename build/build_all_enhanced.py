#!/usr/bin/env python3
"""
完整打包脚本（增强版）
一键打包前端+后端，生成三平台安装包

v1.12.0+ 增强功能：
- 自动环境检查
- Chromium自动打包
- 详细进度显示
- 错误诊断和修复建议
"""
import sys
import os
import subprocess
import shutil
import platform
from pathlib import Path
import time

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
BUILD_DIR = ROOT_DIR / "build"
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
DIST_DIR = BUILD_DIR / "dist"

# 颜色输出（支持Windows/Linux/macOS）
try:
    from colorama import init, Fore, Style
    init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

def colored(text, color=''):
    """彩色输出"""
    if not HAS_COLOR:
        return text
    
    colors = {
        'green': Fore.GREEN,
        'red': Fore.RED,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'cyan': Fore.CYAN,
    }
    
    color_code = colors.get(color, '')
    return f"{color_code}{text}{Style.RESET_ALL}" if color_code else text

def print_header(text):
    """打印标题"""
    print()
    print("=" * 80)
    print(colored(f"  {text}", 'cyan'))
    print("=" * 80)
    print()

def print_step(num, total, text):
    """打印步骤"""
    print(colored(f"\n[{num}/{total}] {text}", 'blue'))
    print("-" * 80)

def print_success(text):
    """打印成功信息"""
    print(colored(f"✅ {text}", 'green'))

def print_error(text):
    """打印错误信息"""
    print(colored(f"❌ {text}", 'red'))

def print_warning(text):
    """打印警告信息"""
    print(colored(f"⚠️  {text}", 'yellow'))

def check_command(command, name):
    """检查命令是否存在"""
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print_success(f"{name} 已安装: {version}")
            return True
        else:
            print_error(f"{name} 未正确安装")
            return False
    except FileNotFoundError:
        print_error(f"{name} 未找到")
        return False
    except subprocess.TimeoutExpired:
        print_warning(f"{name} 命令超时")
        return False

def check_environment():
    """检查构建环境"""
    print_step(1, 8, "环境检查")
    
    all_ok = True
    
    # Python版本检查
    py_version = sys.version.split()[0]
    if sys.version_info >= (3, 11):
        print_success(f"Python 版本: {py_version}")
    else:
        print_error(f"Python 版本过低: {py_version}，需要3.11+")
        all_ok = False
    
    # Node.js检查
    if not check_command("node", "Node.js"):
        print_error("请安装Node.js 18+: https://nodejs.org/")
        all_ok = False
    
    # npm检查
    if not check_command("npm", "npm"):
        all_ok = False
    
    # Playwright检查
    if not check_command("playwright", "Playwright"):
        print_warning("Playwright未安装，将在构建时自动安装")
    
    # PyInstaller检查
    try:
        import PyInstaller
        print_success(f"PyInstaller 已安装: {PyInstaller.__version__}")
    except ImportError:
        print_error("PyInstaller 未安装")
        print("  请运行: pip install pyinstaller")
        all_ok = False
    
    if not all_ok:
        print_error("\n环境检查失败！请先安装缺失的依赖。")
        return False
    
    print_success("\n环境检查通过！")
    return True

def install_dependencies():
    """安装依赖"""
    print_step(2, 8, "安装依赖")
    
    # 后端依赖
    print("📦 安装后端依赖...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(BACKEND_DIR / "requirements.txt")],
            check=True,
            cwd=BACKEND_DIR
        )
        print_success("后端依赖安装完成")
    except subprocess.CalledProcessError as e:
        print_error(f"后端依赖安装失败: {e}")
        return False
    
    # 前端依赖
    print("\n📦 安装前端依赖...")
    try:
        subprocess.run(
            ["npm", "install"],
            check=True,
            cwd=FRONTEND_DIR
        )
        print_success("前端依赖安装完成")
    except subprocess.CalledProcessError as e:
        print_error(f"前端依赖安装失败: {e}")
        return False
    
    return True

def prepare_chromium():
    """准备Chromium浏览器"""
    print_step(3, 8, "准备Chromium浏览器")
    
    print("这可能需要几分钟时间（约170MB下载）...")
    
    try:
        subprocess.run(
            ["playwright", "install", "chromium"],
            check=True,
            timeout=600  # 10分钟超时
        )
        print_success("Chromium下载完成")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Chromium下载失败: {e}")
        return False
    except subprocess.TimeoutExpired:
        print_error("Chromium下载超时")
        return False

def build_backend():
    """构建后端"""
    print_step(4, 8, "构建后端可执行文件")
    
    try:
        # 导入并运行打包脚本
        sys.path.insert(0, str(BUILD_DIR))
        from build_backend import build_backend as do_build
        
        if do_build():
            print_success("后端构建成功")
            return True
        else:
            print_error("后端构建失败")
            return False
    except Exception as e:
        print_error(f"后端构建异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def build_frontend():
    """构建前端"""
    print_step(5, 8, "构建前端应用")
    
    # 先构建Web资源
    print("📦 构建Web资源...")
    try:
        subprocess.run(
            ["npm", "run", "build"],
            check=True,
            cwd=FRONTEND_DIR
        )
        print_success("Web资源构建完成")
    except subprocess.CalledProcessError as e:
        print_error(f"Web资源构建失败: {e}")
        return False
    
    # 再构建Electron应用
    print("\n📦 构建Electron应用...")
    
    # 根据平台选择构建命令
    system = platform.system()
    if system == "Windows":
        build_cmd = "electron:build:win"
    elif system == "Darwin":
        build_cmd = "electron:build:mac"
    else:  # Linux
        build_cmd = "electron:build:linux"
    
    try:
        subprocess.run(
            ["npm", "run", build_cmd],
            check=True,
            cwd=FRONTEND_DIR
        )
        print_success("Electron应用构建完成")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Electron应用构建失败: {e}")
        return False

def package_release():
    """打包发布版本"""
    print_step(6, 8, "打包发布版本")
    
    # 创建发布目录
    release_dir = BUILD_DIR / "release"
    release_dir.mkdir(exist_ok=True)
    
    print(f"📦 发布目录: {release_dir}")
    
    # 复制后端可执行文件
    backend_exe = DIST_DIR / "kook-forwarder-backend"
    if platform.system() == "Windows":
        backend_exe = backend_exe.with_suffix('.exe')
    
    if backend_exe.exists():
        shutil.copy2(backend_exe, release_dir)
        print_success(f"已复制后端: {backend_exe.name}")
    else:
        print_warning(f"后端可执行文件未找到: {backend_exe}")
    
    # 复制前端安装包
    frontend_dist = FRONTEND_DIR / "dist-electron"
    if frontend_dist.exists():
        for file in frontend_dist.glob("*"):
            if file.is_file() and file.suffix in ['.exe', '.dmg', '.AppImage', '.deb']:
                shutil.copy2(file, release_dir)
                print_success(f"已复制前端: {file.name}")
    else:
        print_warning(f"前端安装包未找到: {frontend_dist}")
    
    print_success("\n发布版本打包完成")
    return True

def generate_checksums():
    """生成校验和文件"""
    print_step(7, 8, "生成校验和文件")
    
    import hashlib
    
    release_dir = BUILD_DIR / "release"
    checksum_file = release_dir / "SHA256SUMS.txt"
    
    with open(checksum_file, 'w', encoding='utf-8') as f:
        for file in sorted(release_dir.glob("*")):
            if file.is_file() and file.name != "SHA256SUMS.txt":
                # 计算SHA256
                sha256 = hashlib.sha256()
                with open(file, 'rb') as fb:
                    for chunk in iter(lambda: fb.read(4096), b""):
                        sha256.update(chunk)
                
                checksum = sha256.hexdigest()
                size_mb = file.stat().st_size / 1024 / 1024
                
                f.write(f"{checksum}  {file.name}\n")
                print(f"  {file.name:50s} {size_mb:8.1f} MB")
    
    print_success(f"\n校验和文件已生成: {checksum_file}")
    return True

def print_summary():
    """打印构建摘要"""
    print_step(8, 8, "构建摘要")
    
    release_dir = BUILD_DIR / "release"
    
    print("📦 生成的文件:")
    print()
    
    total_size = 0
    for file in sorted(release_dir.glob("*")):
        if file.is_file():
            size_mb = file.stat().st_size / 1024 / 1024
            total_size += size_mb
            
            icon = "📦" if file.suffix in ['.exe', '.dmg', '.AppImage'] else "📄"
            print(f"  {icon} {file.name}")
            print(f"     大小: {size_mb:.1f} MB")
            print(f"     路径: {file}")
            print()
    
    print(f"总大小: {total_size:.1f} MB")
    print()
    print_success(f"所有文件位于: {release_dir}")

def main():
    """主函数"""
    print_header("🚀 KOOK消息转发系统 - 完整打包脚本")
    
    print(f"项目根目录: {ROOT_DIR}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version.split()[0]}")
    
    start_time = time.time()
    
    # 步骤1: 环境检查
    if not check_environment():
        print_error("\n构建失败：环境检查不通过")
        return False
    
    # 步骤2: 安装依赖
    if not install_dependencies():
        print_error("\n构建失败：依赖安装失败")
        return False
    
    # 步骤3: 准备Chromium
    if not prepare_chromium():
        print_warning("\n警告：Chromium准备失败，继续构建...")
    
    # 步骤4: 构建后端
    if not build_backend():
        print_error("\n构建失败：后端构建失败")
        return False
    
    # 步骤5: 构建前端
    if not build_frontend():
        print_error("\n构建失败：前端构建失败")
        return False
    
    # 步骤6: 打包发布版本
    if not package_release():
        print_error("\n构建失败：打包发布版本失败")
        return False
    
    # 步骤7: 生成校验和
    if not generate_checksums():
        print_warning("\n警告：校验和生成失败")
    
    # 步骤8: 打印摘要
    print_summary()
    
    # 计算耗时
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    print_header(f"✅ 构建成功！耗时: {minutes}分{seconds}秒")
    
    print("下一步:")
    print("  1. 测试安装包是否能正常运行")
    print("  2. 上传到GitHub Releases")
    print("  3. 发布Release Notes")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断构建")
        sys.exit(130)
    except Exception as e:
        print_error(f"\n构建异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
