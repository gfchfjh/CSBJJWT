#!/usr/bin/env python3
"""
创建各平台所需的图标格式
- Windows: .ico
- macOS: .icns  
- Linux: .png
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image
    print("✅ PIL/Pillow已安装")
except ImportError:
    print("❌ 请先安装Pillow: pip install Pillow")
    sys.exit(1)

def create_ico(png_path, ico_path):
    """创建Windows .ico文件"""
    try:
        # 打开PNG图像
        img = Image.open(png_path)
        
        # 创建多尺寸ico（Windows推荐尺寸）
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # 调整图像为各种尺寸
        icon_images = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # 保存为ico格式（包含多个尺寸）
        icon_images[0].save(
            ico_path,
            format='ICO',
            sizes=sizes,
            append_images=icon_images[1:]
        )
        
        print(f"✅ 已创建: {ico_path}")
        return True
    except Exception as e:
        print(f"❌ 创建.ico失败: {e}")
        return False

def create_icns(base_dir, icns_path):
    """创建macOS .icns文件（如果在macOS系统）"""
    if sys.platform != 'darwin':
        print("ℹ️  .icns文件只能在macOS系统上创建，跳过")
        print("💡 提示：在GitHub Actions macOS构建时会自动创建")
        return False
    
    try:
        import subprocess
        
        # 创建临时iconset目录
        iconset_dir = base_dir / 'icon.iconset'
        iconset_dir.mkdir(exist_ok=True)
        
        # macOS要求的图标尺寸
        icon_sizes = [
            (16, 'icon_16x16.png'),
            (32, 'icon_16x16@2x.png'),
            (32, 'icon_32x32.png'),
            (64, 'icon_32x32@2x.png'),
            (128, 'icon_128x128.png'),
            (256, 'icon_128x128@2x.png'),
            (256, 'icon_256x256.png'),
            (512, 'icon_256x256@2x.png'),
            (512, 'icon_512x512.png'),
            (1024, 'icon_512x512@2x.png'),
        ]
        
        # 生成各种尺寸的图标
        base_icon = Image.open(base_dir / 'icon-1024.png')
        for size, filename in icon_sizes:
            resized = base_icon.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(iconset_dir / filename, 'PNG')
        
        # 使用iconutil命令创建icns文件
        subprocess.run(['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(icns_path)], check=True)
        
        # 清理临时目录
        import shutil
        shutil.rmtree(iconset_dir)
        
        print(f"✅ 已创建: {icns_path}")
        return True
    except Exception as e:
        print(f"❌ 创建.icns失败: {e}")
        return False

def copy_linux_icon(png_path, output_path):
    """复制Linux图标（直接使用PNG）"""
    try:
        import shutil
        shutil.copy(png_path, output_path)
        print(f"✅ 已创建: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 复制Linux图标失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎨 创建各平台图标文件")
    print("=" * 60)
    print()
    
    # 项目目录
    build_dir = Path('build')
    
    # 检查源PNG文件是否存在
    icon_256 = build_dir / 'icon-256.png'
    icon_512 = build_dir / 'icon-512.png'
    
    if not icon_256.exists():
        print("❌ 找不到icon-256.png，请先运行generate_simple_icon.py")
        sys.exit(1)
    
    print(f"📁 工作目录: {build_dir.absolute()}")
    print()
    
    # 1. 创建Windows .ico文件
    print("1️⃣  创建Windows图标 (.ico)")
    print("-" * 60)
    ico_path = build_dir / 'icon.ico'
    create_ico(icon_256, ico_path)
    print()
    
    # 2. 创建macOS .icns文件
    print("2️⃣  创建macOS图标 (.icns)")
    print("-" * 60)
    icns_path = build_dir / 'icon.icns'
    create_icns(build_dir, icns_path)
    print()
    
    # 3. 创建Linux图标（使用高分辨率PNG）
    print("3️⃣  创建Linux图标 (.png)")
    print("-" * 60)
    png_path = build_dir / 'icon.png'
    copy_linux_icon(icon_512, png_path)
    print()
    
    # 4. 复制到frontend/public目录（供开发时使用）
    print("4️⃣  复制图标到前端目录")
    print("-" * 60)
    frontend_public = Path('frontend/public')
    if frontend_public.exists():
        copy_linux_icon(icon_256, frontend_public / 'icon.png')
    else:
        print("⚠️  frontend/public目录不存在，跳过")
    print()
    
    # 总结
    print("=" * 60)
    print("✅ 图标创建完成！")
    print("=" * 60)
    print()
    print("生成的文件：")
    
    files_to_check = [
        (build_dir / 'icon.ico', 'Windows图标'),
        (build_dir / 'icon.icns', 'macOS图标'),
        (build_dir / 'icon.png', 'Linux图标'),
        (frontend_public / 'icon.png', '前端图标（开发）'),
    ]
    
    for file_path, description in files_to_check:
        if file_path.exists():
            size = file_path.stat().st_size / 1024
            print(f"  ✅ {description}: {file_path} ({size:.1f} KB)")
        else:
            print(f"  ⚠️  {description}: {file_path} (未创建)")
    
    print()
    print("💡 提示：")
    print("   - Windows .ico 已包含多种尺寸（16-256px）")
    print("   - macOS .icns 需要在macOS系统或GitHub Actions中创建")
    print("   - Linux 使用512x512的PNG格式")
    print()

if __name__ == '__main__':
    main()
