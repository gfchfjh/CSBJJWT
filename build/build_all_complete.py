"""
完整打包脚本
一键打包前后端和所有依赖
"""
import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = BUILD_DIR / "dist"

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_step(step_num, message):
    """打印步骤信息"""
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}步骤 {step_num}: {message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_success(message):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    """打印错误信息"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_warning(message):
    """打印警告信息"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def run_command(command, cwd=None, shell=True):
    """运行命令"""
    print(f"{Colors.OKCYAN}运行: {command}{Colors.ENDC}")
    try:
        result = subprocess.run(
            command,
            shell=shell,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"命令执行失败: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def check_dependencies():
    """检查依赖"""
    print_step(1, "检查依赖")
    
    dependencies = {
        'python': 'python --version',
        'node': 'node --version',
        'npm': 'npm --version',
        'pip': 'pip --version',
    }
    
    all_ok = True
    for dep, cmd in dependencies.items():
        if run_command(cmd):
            print_success(f"{dep} 已安装")
        else:
            print_error(f"{dep} 未安装")
            all_ok = False
    
    return all_ok

def install_python_dependencies():
    """安装Python依赖"""
    print_step(2, "安装Python依赖")
    
    requirements_file = BACKEND_DIR / "requirements.txt"
    if not requirements_file.exists():
        print_error(f"未找到 {requirements_file}")
        return False
    
    if not run_command(f"pip install -r {requirements_file}"):
        print_error("安装Python依赖失败")
        return False
    
    print_success("Python依赖安装完成")
    
    # 安装Playwright浏览器
    print("\n安装Playwright浏览器...")
    if run_command("playwright install chromium"):
        print_success("Playwright浏览器安装完成")
    else:
        print_warning("Playwright浏览器安装失败，请手动执行: playwright install chromium")
    
    return True

def install_node_dependencies():
    """安装Node依赖"""
    print_step(3, "安装Node.js依赖")
    
    if not run_command("npm install", cwd=FRONTEND_DIR):
        print_error("安装Node依赖失败")
        return False
    
    print_success("Node依赖安装完成")
    return True

def build_frontend():
    """打包前端"""
    print_step(4, "打包前端（Vue应用）")
    
    # 构建Vue应用
    if not run_command("npm run build", cwd=FRONTEND_DIR):
        print_error("构建前端失败")
        return False
    
    print_success("前端构建完成")
    return True

def build_backend_pyinstaller():
    """使用PyInstaller打包后端"""
    print_step(5, "打包后端（Python应用）")
    
    try:
        import PyInstaller.__main__
        
        args = [
            str(BACKEND_DIR / "app" / "main.py"),
            "--name=kook-forwarder-backend",
            "--onefile",
            "--clean",
            
            # 添加数据文件
            f"--add-data={ROOT_DIR / 'docs'}:docs",
            
            # 隐藏导入
            "--hidden-import=playwright",
            "--hidden-import=playwright.async_api",
            "--hidden-import=discord_webhook",
            "--hidden-import=telegram",
            "--hidden-import=lark_oapi",
            "--hidden-import=aiohttp",
            "--hidden-import=aiosqlite",
            "--hidden-import=loguru",
            "--hidden-import=PIL",
            "--hidden-import=cryptography",
            "--hidden-import=fastapi",
            "--hidden-import=uvicorn",
            "--hidden-import=pydantic",
            
            # 收集数据
            "--collect-data=playwright",
            
            # 输出目录
            f"--distpath={DIST_DIR}",
            f"--workpath={BUILD_DIR / 'work'}",
            f"--specpath={BUILD_DIR}",
        ]
        
        # 平台特定配置
        if sys.platform == "win32":
            args.extend(["--console"])
        
        PyInstaller.__main__.run(args)
        print_success("后端打包完成")
        return True
        
    except Exception as e:
        print_error(f"打包后端失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def copy_resources():
    """复制资源文件"""
    print_step(6, "复制资源文件")
    
    # 创建分发目录
    dist_app_dir = DIST_DIR / "KookForwarder"
    dist_app_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制文档
    docs_src = ROOT_DIR / "docs"
    docs_dest = dist_app_dir / "docs"
    if docs_src.exists():
        shutil.copytree(docs_src, docs_dest, dirs_exist_ok=True)
        print_success(f"复制文档到 {docs_dest}")
    
    # 复制README
    readme_src = ROOT_DIR / "README.md"
    readme_dest = dist_app_dir / "README.md"
    if readme_src.exists():
        shutil.copy2(readme_src, readme_dest)
        print_success("复制README")
    
    # 复制启动脚本
    start_script_content = """#!/bin/bash
# KOOK消息转发系统启动脚本

echo "正在启动KOOK消息转发系统..."

# 启动后端
./kook-forwarder-backend &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 打开浏览器
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:9527
elif command -v open > /dev/null; then
    open http://localhost:9527
fi

echo "KOOK消息转发系统已启动"
echo "访问地址: http://localhost:9527"
echo "按 Ctrl+C 停止服务"

# 等待进程结束
wait $BACKEND_PID
"""
    
    start_script_path = dist_app_dir / "start.sh"
    start_script_path.write_text(start_script_content)
    start_script_path.chmod(0o755)
    print_success("创建启动脚本")
    
    # Windows启动脚本
    if sys.platform == "win32":
        start_bat_content = """@echo off
echo 正在启动KOOK消息转发系统...

start "" kook-forwarder-backend.exe

timeout /t 3 /nobreak > nul

start http://localhost:9527

echo KOOK消息转发系统已启动
echo 访问地址: http://localhost:9527
pause
"""
        start_bat_path = dist_app_dir / "start.bat"
        start_bat_path.write_text(start_bat_content, encoding='utf-8')
        print_success("创建Windows启动脚本")
    
    return True

def download_redis():
    """下载Redis（如果不存在）"""
    print_step(7, "配置Redis")
    
    redis_dir = ROOT_DIR / "redis"
    
    if redis_dir.exists() and any(redis_dir.glob("redis-server*")):
        print_success("Redis已存在")
        return True
    
    print_warning("Redis未找到，请手动下载：")
    
    if sys.platform == "win32":
        print("Windows: https://github.com/microsoftarchive/redis/releases")
    elif sys.platform == "darwin":
        print("macOS: brew install redis")
    else:
        print("Linux: sudo apt install redis-server")
    
    print("将Redis文件放置到项目根目录的 redis/ 文件夹中")
    
    return True

def build_electron_app():
    """打包Electron应用"""
    print_step(8, "打包Electron应用（最终安装包）")
    
    print_warning("Electron打包需要较长时间，请耐心等待...")
    
    if not run_command("npm run electron:build", cwd=FRONTEND_DIR):
        print_error("Electron打包失败")
        return False
    
    print_success("Electron应用打包完成")
    return True

def create_package_info():
    """创建打包信息文件"""
    print_step(9, "创建打包信息")
    
    info_content = f"""KOOK消息转发系统 v1.0.0
构建日期: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
平台: {platform.system()} {platform.machine()}
Python: {sys.version}

文件列表:
- kook-forwarder-backend: 后端服务可执行文件
- docs/: 用户文档
- README.md: 项目说明
- start.sh: 启动脚本（Linux/macOS）
- start.bat: 启动脚本（Windows）

使用方法:
1. 运行 start.sh (Linux/macOS) 或 start.bat (Windows)
2. 浏览器访问 http://localhost:9527
3. 按照配置向导完成设置

技术支持:
- GitHub: https://github.com/gfchfjh/CSBJJWT
"""
    
    info_file = DIST_DIR / "KookForwarder" / "BUILD_INFO.txt"
    info_file.write_text(info_content, encoding='utf-8')
    print_success("创建打包信息文件")
    
    return True

def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("=" * 70)
    print("      KOOK消息转发系统 - 完整打包脚本")
    print("=" * 70)
    print(f"{Colors.ENDC}\n")
    
    # 检查依赖
    if not check_dependencies():
        print_error("依赖检查失败，请安装所需依赖")
        return False
    
    # 安装依赖
    if not install_python_dependencies():
        print_error("Python依赖安装失败")
        return False
    
    if not install_node_dependencies():
        print_error("Node依赖安装失败")
        return False
    
    # 打包前端
    if not build_frontend():
        print_error("前端打包失败")
        return False
    
    # 打包后端
    if not build_backend_pyinstaller():
        print_error("后端打包失败")
        return False
    
    # 复制资源
    if not copy_resources():
        print_error("复制资源失败")
        return False
    
    # 配置Redis
    download_redis()
    
    # 创建打包信息
    create_package_info()
    
    # 最终提示
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
    print("=" * 70)
    print("      ✅ 打包完成！")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    print(f"\n{Colors.OKCYAN}打包文件位置:{Colors.ENDC}")
    print(f"  📁 {DIST_DIR / 'KookForwarder'}")
    
    print(f"\n{Colors.OKBLUE}下一步操作:{Colors.ENDC}")
    print("  1. 确保Redis已配置（如未自动配置）")
    print("  2. 运行 start.sh 或 start.bat 测试")
    print("  3. （可选）使用 electron-builder 打包完整安装程序:")
    print(f"     cd {FRONTEND_DIR}")
    print("     npm run electron:build")
    
    print(f"\n{Colors.WARNING}注意事项:{Colors.ENDC}")
    print("  ⚠️  首次运行需要下载Chromium（约150MB）")
    print("  ⚠️  如需分发，请包含整个 KookForwarder 文件夹")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\n用户中断打包")
        sys.exit(1)
    except Exception as e:
        print_error(f"打包过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
