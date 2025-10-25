"""
Chromium 浏览器准备脚本（增强版）
P0-15: Chromium 打包流程优化

功能：
1. 检测 Playwright Chromium 是否已安装
2. 自动下载并安装 Chromium
3. 验证浏览器可用性
4. 准备打包所需的浏览器文件
"""
import os
import sys
import asyncio
import shutil
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright


class ChromiumPreparer:
    """Chromium 准备器"""
    
    def __init__(self):
        self.playwright_dir = Path.home() / ".cache/ms-playwright"
        self.build_browsers_dir = Path(__file__).parent.parent / "dist/browsers"
        self.build_browsers_dir.mkdir(parents=True, exist_ok=True)
        
    def find_chromium_path(self) -> Path:
        """查找 Chromium 安装路径"""
        if sys.platform == "win32":
            # Windows: chrome.exe
            pattern = "chromium-*/chrome-win/chrome.exe"
        elif sys.platform == "darwin":
            # macOS: Chromium.app
            pattern = "chromium-*/chrome-mac/Chromium.app"
        else:
            # Linux: chrome
            pattern = "chromium-*/chrome-linux/chrome"
        
        matches = list(self.playwright_dir.glob(pattern))
        if matches:
            return matches[0]
        return None
    
    async def check_chromium_installed(self) -> bool:
        """检查 Chromium 是否已安装并可用"""
        try:
            chromium_path = self.find_chromium_path()
            if not chromium_path or not chromium_path.exists():
                print("❌ Chromium 未找到")
                return False
            
            print(f"✅ Chromium 路径: {chromium_path}")
            
            # 验证浏览器可用性
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                print("✅ Chromium 可正常启动")
                await browser.close()
                return True
                
        except Exception as e:
            print(f"❌ Chromium 检查失败: {e}")
            return False
    
    def install_chromium(self) -> bool:
        """安装 Playwright Chromium"""
        try:
            print("📥 开始安装 Chromium...")
            
            # 执行 playwright install chromium
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                print("✅ Chromium 安装成功")
                print(result.stdout)
                return True
            else:
                print(f"❌ Chromium 安装失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Chromium 安装超时（10分钟）")
            return False
        except Exception as e:
            print(f"❌ Chromium 安装异常: {e}")
            return False
    
    def copy_chromium_to_build(self) -> bool:
        """复制 Chromium 到构建目录"""
        try:
            chromium_path = self.find_chromium_path()
            if not chromium_path:
                print("❌ 未找到 Chromium 路径")
                return False
            
            # 获取 Chromium 目录（包含版本号）
            chromium_version_dir = chromium_path.parent.parent
            
            # 目标路径
            target_dir = self.build_browsers_dir / chromium_version_dir.name
            
            print(f"📦 复制 Chromium: {chromium_version_dir} -> {target_dir}")
            
            # 复制整个目录
            if target_dir.exists():
                shutil.rmtree(target_dir)
            
            shutil.copytree(chromium_version_dir, target_dir)
            
            print(f"✅ Chromium 已复制到: {target_dir}")
            
            # 计算大小
            total_size = sum(
                f.stat().st_size for f in target_dir.rglob('*') if f.is_file()
            )
            size_mb = total_size / (1024 * 1024)
            print(f"📊 Chromium 大小: {size_mb:.2f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ 复制 Chromium 失败: {e}")
            return False
    
    def create_browser_config(self):
        """创建浏览器配置文件"""
        config_content = f"""# Chromium 浏览器配置

# 浏览器路径（相对于应用根目录）
PLAYWRIGHT_BROWSERS_PATH=./browsers

# 跳过浏览器下载（使用打包的版本）
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# 浏览器类型
BROWSER_TYPE=chromium
"""
        
        config_path = self.build_browsers_dir.parent / "browser_config.txt"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ 浏览器配置已创建: {config_path}")
    
    async def prepare(self) -> bool:
        """准备 Chromium（完整流程）"""
        print("=" * 60)
        print("🚀 开始准备 Chromium 浏览器")
        print("=" * 60)
        
        # 1. 检查是否已安装
        installed = await self.check_chromium_installed()
        
        # 2. 如果未安装，执行安装
        if not installed:
            print("\n📥 Chromium 未安装，开始自动安装...")
            if not self.install_chromium():
                print("❌ Chromium 安装失败，准备中止")
                return False
            
            # 再次验证
            installed = await self.check_chromium_installed()
            if not installed:
                print("❌ Chromium 安装后验证失败")
                return False
        
        # 3. 复制到构建目录
        print("\n📦 复制 Chromium 到构建目录...")
        if not self.copy_chromium_to_build():
            print("❌ Chromium 复制失败")
            return False
        
        # 4. 创建配置文件
        print("\n⚙️ 创建浏览器配置...")
        self.create_browser_config()
        
        print("\n" + "=" * 60)
        print("✅ Chromium 准备完成！")
        print("=" * 60)
        
        return True


async def main():
    """主函数"""
    preparer = ChromiumPreparer()
    success = await preparer.prepare()
    
    if success:
        print("\n✅ 可以继续进行打包流程")
        sys.exit(0)
    else:
        print("\n❌ 准备失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
