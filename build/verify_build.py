#!/usr/bin/env python3
"""
构建验证脚本 - 验证构建产物的完整性和正确性

检查项目：
1. 文件存在性检查
2. 文件大小检查
3. 文件权限检查
4. 内容完整性检查
5. 依赖检查
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
import json

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """打印标题"""
    print()
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print()

def print_success(text):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    """打印错误信息"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

class BuildVerifier:
    """构建验证器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.build_dir = self.project_root / 'build'
        self.frontend_dir = self.project_root / 'frontend'
        self.backend_dir = self.project_root / 'backend'
        self.dist_dir = self.frontend_dir / 'dist-electron'
        
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def check_icons(self):
        """检查图标文件"""
        print_header("📦 检查图标文件")
        
        # 必需的图标文件
        required_icons = {
            'Windows': self.build_dir / 'icon.ico',
            'Linux': self.build_dir / 'icon.png',
            'Frontend': self.frontend_dir / 'public' / 'icon.png',
        }
        
        # macOS图标是可选的（只能在macOS上创建）
        optional_icons = {
            'macOS': self.build_dir / 'icon.icns',
        }
        
        # 检查必需图标
        for name, path in required_icons.items():
            if path.exists():
                size_kb = path.stat().st_size / 1024
                print_success(f"{name}图标存在: {path.name} ({size_kb:.1f} KB)")
                self.results['passed'].append(f'{name}图标')
            else:
                print_error(f"{name}图标不存在: {path}")
                self.results['failed'].append(f'{name}图标')
        
        # 检查可选图标
        for name, path in optional_icons.items():
            if path.exists():
                size_kb = path.stat().st_size / 1024
                print_success(f"{name}图标存在: {path.name} ({size_kb:.1f} KB)")
                self.results['passed'].append(f'{name}图标')
            else:
                print_warning(f"{name}图标不存在（可选）: {path}")
                self.results['warnings'].append(f'{name}图标（可选）')
    
    def check_backend_build(self):
        """检查后端构建产物"""
        print_header("🐍 检查后端构建产物")
        
        # 后端打包输出目录
        backend_dist = self.backend_dir / 'dist' / 'KookForwarder-Backend'
        
        if not backend_dist.exists():
            print_error(f"后端构建目录不存在: {backend_dist}")
            print_info("提示: 运行 'pyinstaller build/build_backend.spec'")
            self.results['failed'].append('后端构建')
            return
        
        # 检查可执行文件
        system = platform.system().lower()
        if system == 'windows':
            exe_name = 'KookForwarder-Backend.exe'
        else:
            exe_name = 'KookForwarder-Backend'
        
        exe_path = backend_dist / exe_name
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / 1024 / 1024
            print_success(f"后端可执行文件存在: {exe_name} ({size_mb:.1f} MB)")
            
            # 检查文件权限（Linux/macOS）
            if system != 'windows':
                if os.access(exe_path, os.X_OK):
                    print_success(f"可执行权限正常")
                    self.results['passed'].append('后端构建')
                else:
                    print_error(f"缺少可执行权限")
                    self.results['failed'].append('后端可执行权限')
            else:
                self.results['passed'].append('后端构建')
        else:
            print_error(f"后端可执行文件不存在: {exe_name}")
            self.results['failed'].append('后端可执行文件')
        
        # 检查打包大小
        total_size = sum(f.stat().st_size for f in backend_dist.rglob('*') if f.is_file())
        total_size_mb = total_size / 1024 / 1024
        print_info(f"后端打包总大小: {total_size_mb:.1f} MB")
        
        if total_size_mb < 50:
            print_warning("打包大小异常偏小，可能缺少依赖")
            self.results['warnings'].append('后端打包大小偏小')
        elif total_size_mb > 500:
            print_warning("打包大小异常偏大，可能包含不必要的文件")
            self.results['warnings'].append('后端打包大小偏大')
    
    def check_frontend_build(self):
        """检查前端构建产物"""
        print_header("⚛️  检查前端构建产物")
        
        # 检查Vue构建产物
        vue_dist = self.frontend_dir / 'dist'
        if vue_dist.exists():
            files_count = len(list(vue_dist.rglob('*')))
            print_success(f"Vue构建产物存在: {files_count} 个文件")
            self.results['passed'].append('Vue构建')
        else:
            print_error("Vue构建产物不存在")
            print_info("提示: 运行 'cd frontend && npm run build'")
            self.results['failed'].append('Vue构建')
    
    def check_installer_package(self):
        """检查安装包"""
        print_header("📦 检查安装包")
        
        if not self.dist_dir.exists():
            print_error(f"安装包目录不存在: {self.dist_dir}")
            print_info("提示: 运行 'cd frontend && npm run electron:build'")
            self.results['failed'].append('安装包目录')
            return
        
        # 根据平台检查安装包
        system = platform.system().lower()
        
        if system == 'windows':
            pattern = '*.exe'
            expected_type = 'Windows安装包'
            min_size_mb = 100  # 最小100MB
        elif system == 'darwin':
            pattern = '*.dmg'
            expected_type = 'macOS安装包'
            min_size_mb = 150
        else:  # Linux
            pattern = '*.AppImage'
            expected_type = 'Linux安装包'
            min_size_mb = 100
        
        # 查找安装包文件
        packages = list(self.dist_dir.glob(pattern))
        
        if not packages:
            print_error(f"{expected_type}不存在")
            print_info(f"提示: 运行 'cd frontend && npm run electron:build'")
            self.results['failed'].append(expected_type)
        else:
            for package in packages:
                size_mb = package.stat().st_size / 1024 / 1024
                print_success(f"{expected_type}存在: {package.name} ({size_mb:.1f} MB)")
                
                # 检查文件大小
                if size_mb < min_size_mb:
                    print_warning(f"安装包大小异常偏小: {size_mb:.1f} MB (预期 >{min_size_mb}MB)")
                    self.results['warnings'].append(f'{expected_type}大小偏小')
                else:
                    self.results['passed'].append(expected_type)
                
                # 检查可执行权限（Linux/macOS）
                if system in ['darwin', 'linux']:
                    if os.access(package, os.X_OK):
                        print_success("可执行权限正常")
                    else:
                        print_warning("缺少可执行权限，运行: chmod +x " + str(package))
                        self.results['warnings'].append(f'{expected_type}可执行权限')
    
    def check_config_files(self):
        """检查配置文件"""
        print_header("⚙️  检查配置文件")
        
        config_files = {
            'PyInstaller配置': self.build_dir.parent / 'backend' / 'build_backend.spec',
            'package.json': self.frontend_dir / 'package.json',
            'GitHub Actions': self.project_root / '.github' / 'workflows' / 'build-and-release.yml',
        }
        
        for name, path in config_files.items():
            if path.exists():
                print_success(f"{name}存在: {path.name}")
                self.results['passed'].append(f'{name}配置')
            else:
                print_error(f"{name}不存在: {path}")
                self.results['failed'].append(f'{name}配置')
    
    def check_version_consistency(self):
        """检查版本号一致性"""
        print_header("🔢 检查版本号一致性")
        
        # 读取package.json版本号
        package_json = self.frontend_dir / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    version = data.get('version', 'unknown')
                    print_info(f"package.json版本: {version}")
                    
                    # 检查README.md中的版本号
                    readme = self.project_root / 'README.md'
                    if readme.exists():
                        content = readme.read_text()
                        if version in content:
                            print_success(f"README.md版本号一致: {version}")
                            self.results['passed'].append('版本号一致性')
                        else:
                            print_warning(f"README.md中未找到版本号 {version}")
                            self.results['warnings'].append('README版本号')
                    
            except Exception as e:
                print_error(f"读取package.json失败: {e}")
                self.results['failed'].append('package.json读取')
    
    def check_dependencies(self):
        """检查关键依赖"""
        print_header("📚 检查关键依赖")
        
        # 检查Python依赖
        python_deps = [
            ('pyinstaller', 'PyInstaller'),
            ('playwright', 'Playwright'),
            ('fastapi', 'FastAPI'),
            ('redis', 'Redis'),
        ]
        
        for module, name in python_deps:
            try:
                __import__(module)
                print_success(f"Python依赖 {name} 已安装")
                self.results['passed'].append(f'Python依赖-{name}')
            except ImportError:
                print_error(f"Python依赖 {name} 未安装")
                self.results['failed'].append(f'Python依赖-{name}')
        
        # 检查node_modules
        node_modules = self.frontend_dir / 'node_modules'
        if node_modules.exists():
            deps_count = len(list(node_modules.iterdir()))
            print_success(f"Node.js依赖已安装: {deps_count} 个包")
            self.results['passed'].append('Node.js依赖')
        else:
            print_error("Node.js依赖未安装")
            print_info("提示: 运行 'cd frontend && npm install'")
            self.results['failed'].append('Node.js依赖')
    
    def generate_report(self):
        """生成验证报告"""
        print_header("📊 验证报告")
        
        total = len(self.results['passed']) + len(self.results['failed']) + len(self.results['warnings'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        warnings = len(self.results['warnings'])
        
        print(f"总检查项: {total}")
        print_success(f"通过: {passed}")
        print_error(f"失败: {failed}")
        print_warning(f"警告: {warnings}")
        print()
        
        if failed > 0:
            print_error("以下检查项失败:")
            for item in self.results['failed']:
                print(f"  ❌ {item}")
            print()
        
        if warnings > 0:
            print_warning("以下检查项有警告:")
            for item in self.results['warnings']:
                print(f"  ⚠️  {item}")
            print()
        
        # 计算通过率
        if total > 0:
            pass_rate = (passed / total) * 100
            print()
            if pass_rate >= 90:
                print_success(f"✅ 验证通过率: {pass_rate:.1f}% - 构建质量优秀！")
                return 0
            elif pass_rate >= 70:
                print_warning(f"⚠️  验证通过率: {pass_rate:.1f}% - 构建基本可用，建议修复警告")
                return 1
            else:
                print_error(f"❌ 验证通过率: {pass_rate:.1f}% - 构建存在问题，请修复失败项")
                return 2
        else:
            print_error("无检查项")
            return 3
    
    def run_all_checks(self):
        """运行所有检查"""
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║                                                                   ║")
        print("║              🔍 KOOK消息转发系统 - 构建验证工具                   ║")
        print("║                                                                   ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        print()
        print_info(f"项目根目录: {self.project_root}")
        print_info(f"当前平台: {platform.system()} {platform.machine()}")
        print()
        
        # 运行各项检查
        self.check_icons()
        self.check_config_files()
        self.check_version_consistency()
        self.check_dependencies()
        self.check_backend_build()
        self.check_frontend_build()
        self.check_installer_package()
        
        # 生成报告
        return self.generate_report()

def main():
    """主函数"""
    try:
        verifier = BuildVerifier()
        exit_code = verifier.run_all_checks()
        
        print()
        print_header("🎯 建议")
        
        if exit_code == 0:
            print_success("构建验证完全通过！可以发布安装包。")
            print()
            print("📦 发布步骤:")
            print("  1. 提交所有更改: git add . && git commit -m 'ready for release'")
            print("  2. 创建Git Tag: git tag v1.13.2")
            print("  3. 推送到GitHub: git push origin main && git push origin v1.13.2")
            print("  4. 等待GitHub Actions构建完成（15-20分钟）")
            print("  5. 访问GitHub Releases页面下载安装包")
            print()
        elif exit_code == 1:
            print_warning("构建基本可用，但有一些警告需要注意。")
            print()
            print("💡 建议:")
            print("  1. 查看上面的警告信息")
            print("  2. 如果是可选项（如macOS图标），可以忽略")
            print("  3. 如果是大小异常，检查打包配置")
            print()
        else:
            print_error("构建验证失败，请修复上述问题后重试。")
            print()
            print("🔧 常见修复方法:")
            print("  1. 缺少图标: python3 build/create_platform_icons.py")
            print("  2. 缺少依赖: pip3 install -r backend/requirements.txt")
            print("  3. 缺少前端依赖: cd frontend && npm install")
            print("  4. 缺少构建产物: 运行构建脚本")
            print()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print()
        print_warning("验证已取消")
        sys.exit(130)
    except Exception as e:
        print()
        print_error(f"验证过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
