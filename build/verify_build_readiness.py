#!/usr/bin/env python3
"""
构建就绪性验证工具
验证所有构建前置条件是否满足
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def check_command(command: str) -> Tuple[bool, str]:
    """检查命令是否存在"""
    try:
        result = subprocess.run(
            [command, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            return True, version
        return False, ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, ""

def check_python_packages(packages: List[str]) -> Dict[str, bool]:
    """检查Python包是否安装"""
    results = {}
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            results[package] = True
        except ImportError:
            results[package] = False
    return results

def check_npm_packages(package_json_path: Path) -> Tuple[bool, List[str]]:
    """检查npm包是否安装"""
    if not package_json_path.exists():
        return False, []
    
    node_modules = package_json_path.parent / 'node_modules'
    if not node_modules.exists():
        return False, []
    
    with open(package_json_path) as f:
        pkg = json.load(f)
    
    dependencies = list(pkg.get('dependencies', {}).keys())
    dev_dependencies = list(pkg.get('devDependencies', {}).keys())
    all_packages = dependencies + dev_dependencies
    
    missing = []
    for package in all_packages:
        package_dir = node_modules / package
        if not package_dir.exists():
            missing.append(package)
    
    return len(missing) == 0, missing

def check_file_structure() -> Dict[str, bool]:
    """检查项目文件结构"""
    required_files = {
        'backend/requirements.txt': Path('backend/requirements.txt'),
        'backend/build_backend.spec': Path('backend/build_backend.spec'),
        'frontend/package.json': Path('frontend/package.json'),
        'build/electron-builder.yml': Path('build/electron-builder.yml'),
        'build_installer.sh': Path('build_installer.sh'),
        'build_installer.bat': Path('build_installer.bat'),
    }
    
    results = {}
    for name, path in required_files.items():
        results[name] = path.exists()
    
    return results

def check_icons() -> Dict[str, bool]:
    """检查图标文件"""
    icon_files = {
        'Windows图标 (icon.ico)': Path('build/icon.ico'),
        'macOS图标 (icon.icns)': Path('build/icon.icns'),
        'Linux图标 (icon.png)': Path('build/icon.png'),
        '应用图标 (icon-1024.png)': Path('build/icon-1024.png'),
    }
    
    results = {}
    for name, path in icon_files.items():
        results[name] = path.exists()
    
    return results

def check_playwright_browsers() -> bool:
    """检查Playwright浏览器是否安装"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # 尝试获取浏览器路径
            browser_path = p.chromium.executable_path
            return Path(browser_path).exists()
    except Exception:
        return False

def main():
    """主函数"""
    print_header("🔍 KOOK消息转发系统 - 构建就绪性检查")
    
    errors = []
    warnings = []
    
    # 1. 检查基础命令
    print_header("1️⃣  检查基础命令工具")
    
    commands = {
        'python3': 'Python 3',
        'node': 'Node.js',
        'npm': 'npm',
        'git': 'Git',
    }
    
    for cmd, name in commands.items():
        # Windows特殊处理
        if sys.platform == 'win32' and cmd == 'python3':
            cmd = 'python'
        
        exists, version = check_command(cmd)
        if exists:
            print_success(f"{name}: {version}")
        else:
            print_error(f"{name}: 未安装")
            errors.append(f"{name}未安装")
    
    # 2. 检查Python包
    print_header("2️⃣  检查Python依赖包")
    
    required_packages = [
        'fastapi',
        'playwright',
        'redis',
        'aiohttp',
        'pyinstaller',
        'pydantic',
        'cryptography',
        'Pillow',
    ]
    
    package_results = check_python_packages(required_packages)
    installed_count = sum(package_results.values())
    
    if installed_count == len(required_packages):
        print_success(f"所有Python包已安装 ({installed_count}/{len(required_packages)})")
    else:
        print_warning(f"部分Python包未安装 ({installed_count}/{len(required_packages)})")
        for pkg, installed in package_results.items():
            if not installed:
                print_error(f"  - {pkg}")
                warnings.append(f"Python包 {pkg} 未安装")
    
    # 3. 检查npm包
    print_header("3️⃣  检查前端依赖包")
    
    package_json = Path('frontend/package.json')
    npm_ok, missing_packages = check_npm_packages(package_json)
    
    if npm_ok:
        print_success("所有npm包已安装")
    else:
        print_warning(f"缺失{len(missing_packages)}个npm包")
        for pkg in missing_packages[:5]:  # 只显示前5个
            print_error(f"  - {pkg}")
        if len(missing_packages) > 5:
            print_info(f"  ... 还有{len(missing_packages)-5}个包未安装")
        warnings.append(f"{len(missing_packages)}个npm包未安装")
    
    # 4. 检查文件结构
    print_header("4️⃣  检查项目文件结构")
    
    file_results = check_file_structure()
    all_exist = all(file_results.values())
    
    if all_exist:
        print_success("所有必需文件都存在")
    else:
        print_warning("部分必需文件缺失")
        for name, exists in file_results.items():
            if not exists:
                print_error(f"  - {name}")
                warnings.append(f"文件 {name} 不存在")
    
    # 5. 检查图标文件
    print_header("5️⃣  检查图标文件")
    
    icon_results = check_icons()
    icons_ok = all(icon_results.values())
    
    if icons_ok:
        print_success("所有图标文件都存在")
    else:
        print_warning("部分图标文件缺失")
        for name, exists in icon_results.items():
            if not exists:
                print_error(f"  - {name}")
                warnings.append(f"图标 {name} 不存在")
    
    # 6. 检查Playwright浏览器
    print_header("6️⃣  检查Playwright浏览器")
    
    if check_playwright_browsers():
        print_success("Playwright Chromium已安装")
    else:
        print_warning("Playwright Chromium未安装")
        warnings.append("需要运行: playwright install chromium")
    
    # 7. 检查构建脚本权限（Unix系统）
    if sys.platform != 'win32':
        print_header("7️⃣  检查脚本执行权限")
        
        scripts = [
            Path('build_installer.sh'),
            Path('install.sh'),
            Path('start.sh'),
        ]
        
        for script in scripts:
            if script.exists():
                if os.access(script, os.X_OK):
                    print_success(f"{script.name} 可执行")
                else:
                    print_warning(f"{script.name} 无执行权限")
                    warnings.append(f"需要运行: chmod +x {script}")
    
    # 生成总结
    print_header("📊 检查总结")
    
    total_checks = 7
    passed_checks = total_checks - len(errors)
    
    print(f"总检查项: {total_checks}")
    print(f"通过: {Colors.GREEN}{passed_checks}{Colors.RESET}")
    print(f"错误: {Colors.RED}{len(errors)}{Colors.RESET}")
    print(f"警告: {Colors.YELLOW}{len(warnings)}{Colors.RESET}")
    
    if errors:
        print_header("❌ 严重错误（必须修复）")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
    
    if warnings:
        print_header("⚠️  警告（建议修复）")
        for i, warning in enumerate(warnings, 1):
            print(f"{i}. {warning}")
    
    # 提供修复建议
    if errors or warnings:
        print_header("🔧 修复建议")
        
        if any('Python' in e for e in errors):
            print_info("安装Python依赖:")
            print("  pip install -r backend/requirements.txt")
        
        if any('npm' in str(warnings) for warnings in warnings):
            print_info("安装npm依赖:")
            print("  cd frontend && npm install")
        
        if any('Playwright' in str(w) for w in warnings):
            print_info("安装Playwright浏览器:")
            print("  playwright install chromium --with-deps")
        
        if any('图标' in str(w) for w in warnings):
            print_info("生成图标:")
            print("  python build/create_platform_icons.py")
        
        if any('chmod' in str(w) for w in warnings):
            print_info("设置脚本权限:")
            print("  chmod +x *.sh")
    
    # 最终判断
    print()
    if not errors:
        print_success("✅ 构建环境已就绪，可以开始构建！")
        print_info("运行构建命令:")
        print("  ./build_installer.sh  # Linux/macOS")
        print("  build_installer.bat   # Windows")
        return 0
    else:
        print_error("❌ 构建环境未就绪，请先修复上述错误")
        return 1

if __name__ == '__main__':
    sys.exit(main())
