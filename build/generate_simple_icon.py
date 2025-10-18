#!/usr/bin/env python3
"""
生成简单图标（如果没有设计软件）
使用PIL创建基本的应用图标
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("请先安装PIL: pip install Pillow")
    exit(1)

def create_icon(size, output_path):
    """
    创建简单的应用图标
    
    Args:
        size: 图标尺寸
        output_path: 输出路径
    """
    # 创建画布（渐变背景）
    img = Image.new('RGB', (size, size), color=(102, 126, 234))
    draw = ImageDraw.Draw(img)
    
    # 添加渐变效果
    for i in range(size):
        # 从上到下的渐变
        ratio = i / size
        r = int(102 + (118 - 102) * ratio)
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        draw.line([(0, i), (size, i)], fill=(r, g, b))
    
    # 绘制字母K（简单示意）
    # 使用基本几何图形
    padding = size // 4
    
    # K的左竖线
    draw.rectangle(
        [padding, padding, padding + size // 10, size - padding],
        fill='white'
    )
    
    # K的右上斜线
    draw.polygon([
        (padding + size // 8, size // 2),
        (size - padding, padding),
        (size - padding, padding + size // 8),
        (padding + size // 6, size // 2 + size // 20)
    ], fill='white')
    
    # K的右下斜线
    draw.polygon([
        (padding + size // 8, size // 2),
        (size - padding, size - padding),
        (size - padding, size - padding - size // 8),
        (padding + size // 6, size // 2 - size // 20)
    ], fill='white')
    
    # 保存图标
    img.save(output_path)
    print(f"✅ 已生成: {output_path} ({size}x{size})")

def main():
    """主函数"""
    print("开始生成应用图标...")
    
    # 确保build目录存在
    os.makedirs('build', exist_ok=True)
    os.makedirs('build/icons', exist_ok=True)
    
    # 生成不同尺寸的图标
    sizes = [
        (16, 'build/icon-16.png'),
        (32, 'build/icon-32.png'),
        (64, 'build/icon-64.png'),
        (128, 'build/icon-128.png'),
        (256, 'build/icon-256.png'),
        (512, 'build/icon-512.png'),
        (1024, 'build/icon-1024.png'),
    ]
    
    for size, path in sizes:
        create_icon(size, path)
    
    # 生成Linux图标目录
    linux_sizes = [16, 32, 48, 64, 128, 256, 512]
    for size in linux_sizes:
        os.makedirs(f'build/icons/{size}x{size}', exist_ok=True)
        create_icon(size, f'build/icons/{size}x{size}/icon.png')
    
    print("\n✅ 所有图标生成完成！")
    print("\n后续步骤：")
    print("1. Windows: 使用在线工具将icon-256.png转换为icon.ico")
    print("   推荐：https://convertio.co/zh/png-ico/")
    print("2. macOS: 使用以下命令生成icon.icns:")
    print("   mkdir icon.iconset")
    print("   sips -z 16 16   build/icon-16.png --out icon.iconset/icon_16x16.png")
    print("   sips -z 32 32   build/icon-32.png --out icon.iconset/icon_16x16@2x.png")
    print("   # ... 更多尺寸")
    print("   iconutil -c icns icon.iconset")

if __name__ == '__main__':
    main()
