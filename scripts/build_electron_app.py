#!/usr/bin/env python3
"""
Electron应用完整构建脚本
✅ 自动化打包后端 + 前端 + Electron
✅ 支持Windows / macOS / Linux
✅ 生成独立安装包
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import json

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

def print_step(msg):
    print(f"{Colors.OKCYAN}{Colors.BOLD}[STEP] {msg}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.OKGREEN}[✓] {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}[✗] {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}[!] {msg}{Colors.ENDC}")

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist_electron"

# 版本号
VERSION_FILE = ROOT_DIR / "VERSION"
VERSION = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "1.0.0"

def run_command(cmd, cwd=None, check=True):
    """运行命令"""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(result.stdout)
    
    if result.returncode != 0:
        if result.stderr:
            print_error(result.stderr)
        if check:
            sys.exit(1)
    
    return result.returncode == 0

def clean_build():
    """清理构建目录"""
    print_step("清理构建目录...")
    
    dirs_to_clean = [
        DIST_DIR,
        FRONTEND_DIR / "dist",
        FRONTEND_DIR / "dist-electron",
        BACKEND_DIR / "dist",
        BACKEND_DIR / "build",
    ]
    
    for d in dirs_to_clean:
        if d.exists():
            print(f"  删除: {d}")
            shutil.rmtree(d)
    
    print_success("构建目录已清理")

def build_backend():
    """构建后端（使用PyInstaller）"""
    print_step("构建后端服务...")
    
    # 检查PyInstaller
    if not run_command(["pip", "show", "pyinstaller"], check=False):
        print_warning("PyInstaller未安装，正在安装...")
        run_command(["pip", "install", "pyinstaller"])
    
    # 构建
    spec_file = BUILD_DIR / "pyinstaller.spec"
    if not spec_file.exists():
        print_error(f"打包配置文件不存在: {spec_file}")
        sys.exit(1)
    
    run_command(
        ["pyinstaller", str(spec_file), "--clean", "--noconfirm"],
        cwd=BACKEND_DIR
    )
    
    print_success("后端服务构建完成")

def build_frontend():
    """构建前端"""
    print_step("构建前端应用...")
    
    # 检查node_modules
    if not (FRONTEND_DIR / "node_modules").exists():
        print_warning("依赖未安装，正在安装...")
        run_command(["npm", "install"], cwd=FRONTEND_DIR)
    
    # 构建
    run_command(["npm", "run", "build"], cwd=FRONTEND_DIR)
    
    print_success("前端应用构建完成")

def package_electron(target_platform=None):
    """打包Electron应用"""
    print_step(f"打包Electron应用 (目标: {target_platform or '当前平台'})...")
    
    # 确定打包命令
    if target_platform == "win":
        cmd = ["npm", "run", "electron:build:win"]
    elif target_platform == "mac":
        cmd = ["npm", "run", "electron:build:mac"]
    elif target_platform == "linux":
        cmd = ["npm", "run", "electron:build:linux"]
    else:
        cmd = ["npm", "run", "electron:build"]
    
    run_command(cmd, cwd=FRONTEND_DIR)
    
    print_success("Electron应用打包完成")

def copy_resources():
    """复制额外资源"""
    print_step("复制资源文件...")
    
    # 创建resources目录
    resources_dir = DIST_DIR / "resources"
    resources_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制Redis
    redis_src = ROOT_DIR / "redis"
    if redis_src.exists():
        redis_dest = resources_dir / "redis"
        print(f"  复制: Redis → {redis_dest}")
        shutil.copytree(redis_src, redis_dest, dirs_exist_ok=True)
    
    # 复制文档
    docs_src = ROOT_DIR / "docs"
    if docs_src.exists():
        docs_dest = resources_dir / "docs"
        print(f"  复制: 文档 → {docs_dest}")
        shutil.copytree(docs_src, docs_dest, dirs_exist_ok=True)
    
    # 复制LICENSE和README
    for file in ["LICENSE", "README.md"]:
        src = ROOT_DIR / file
        if src.exists():
            dest = DIST_DIR / file
            print(f"  复制: {file}")
            shutil.copy2(src, dest)
    
    print_success("资源文件已复制")

def create_installer():
    """创建安装程序"""
    print_step("创建安装程序...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Windows: NSIS已由electron-builder处理
        print_success("Windows安装程序已由electron-builder创建")
    
    elif system == "darwin":
        # macOS: DMG已由electron-builder处理
        print_success("macOS安装程序已由electron-builder创建")
    
    elif system == "linux":
        # Linux: AppImage已由electron-builder处理
        print_success("Linux安装程序已由electron-builder创建")
    
    else:
        print_warning(f"未知系统: {system}")

def verify_build():
    """验证构建结果"""
    print_step("验证构建结果...")
    
    # 检查输出目录
    electron_dist = FRONTEND_DIR / "dist-electron"
    if not electron_dist.exists():
        print_error("Electron构建目录不存在")
        return False
    
    # 检查安装包
    installers = list(electron_dist.glob("*"))
    if not installers:
        print_error("未找到安装包")
        return False
    
    print_success("构建验证通过")
    print(f"\n{Colors.BOLD}构建产物:{Colors.ENDC}")
    for installer in installers:
        size_mb = installer.stat().st_size / (1024 * 1024)
        print(f"  - {installer.name} ({size_mb:.1f} MB)")
    
    return True

def generate_checksums():
    """生成校验和"""
    print_step("生成文件校验和...")
    
    import hashlib
    
    electron_dist = FRONTEND_DIR / "dist-electron"
    if not electron_dist.exists():
        print_warning("构建目录不存在，跳过校验和生成")
        return
    
    checksums_file = electron_dist / "checksums.txt"
    
    with open(checksums_file, 'w') as f:
        for file in electron_dist.iterdir():
            if file.is_file() and file.name != "checksums.txt":
                # 计算SHA256
                sha256 = hashlib.sha256()
                with open(file, 'rb') as bf:
                    for chunk in iter(lambda: bf.read(4096), b""):
                        sha256.update(chunk)
                
                checksum = sha256.hexdigest()
                f.write(f"{checksum}  {file.name}\n")
                print(f"  {file.name}: {checksum[:16]}...")
    
    print_success(f"校验和已保存到: {checksums_file}")

def create_build_info():
    """创建构建信息文件"""
    print_step("创建构建信息...")
    
    import datetime
    
    build_info = {
        "version": VERSION,
        "build_date": datetime.datetime.now().isoformat(),
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "node_version": subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True
        ).stdout.strip(),
    }
    
    build_info_file = DIST_DIR / "build-info.json"
    build_info_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(build_info_file, 'w') as f:
        json.dump(build_info, f, indent=2)
    
    print_success(f"构建信息已保存到: {build_info_file}")

def main():
    """主函数"""
    print(f"""
{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════╗
║  KOOK消息转发系统 - Electron应用构建脚本              ║
║  版本: {VERSION:<45} ║
╚═══════════════════════════════════════════════════════╝
{Colors.ENDC}
""")
    
    # 解析参数
    target_platform = None
    if len(sys.argv) > 1:
        target_platform = sys.argv[1]
    
    try:
        # 1. 清理
        clean_build()
        
        # 2. 构建后端
        build_backend()
        
        # 3. 构建前端
        build_frontend()
        
        # 4. 打包Electron
        package_electron(target_platform)
        
        # 5. 复制资源
        copy_resources()
        
        # 6. 创建安装程序
        create_installer()
        
        # 7. 验证构建
        if not verify_build():
            sys.exit(1)
        
        # 8. 生成校验和
        generate_checksums()
        
        # 9. 创建构建信息
        create_build_info()
        
        print(f"""
{Colors.OKGREEN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════╗
║  ✓ 构建成功！                                         ║
║  构建产物位于: frontend/dist-electron/                ║
╚═══════════════════════════════════════════════════════╝
{Colors.ENDC}
""")
        
    except KeyboardInterrupt:
        print_error("\n构建已取消")
        sys.exit(1)
    except Exception as e:
        print_error(f"构建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
