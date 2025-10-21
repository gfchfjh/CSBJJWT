#!/usr/bin/env python3
"""
占位图标生成器
用于生成临时的应用图标，直到正式图标设计完成

生成的图标:
- 紫色背景（KOOK品牌色）
- 白色"K"字母或消息图标
- 多种尺寸（16-512）

使用方法:
    python build/placeholder_icon_generator.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

# 配置
BRAND_COLOR = (108, 92, 231, 255)  # KOOK紫色 #6C5CE7
WHITE = (255, 255, 255, 255)
SIZES = [16, 32, 48, 64, 128, 256, 512]
OUTPUT_DIR = "build/icons"


def create_letter_icon(size=512, letter="K"):
    """创建字母图标"""
    # 创建圆角矩形背景
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆角矩形背景
    corner_radius = size // 8
    draw.rounded_rectangle(
        [(0, 0), (size, size)],
        radius=corner_radius,
        fill=BRAND_COLOR
    )
    
    # 绘制字母
    font_size = int(size * 0.55)
    try:
        # 尝试使用系统字体
        font_candidates = [
            "Arial Bold.ttf",
            "Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ]
        font = None
        for font_path in font_candidates:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
        
        if font is None:
            raise Exception("No suitable font found")
            
    except:
        # 回退到默认字体
        font = ImageFont.load_default()
        font_size = int(size * 0.3)  # 默认字体需要调整大小
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]  # 调整基线
    
    draw.text((x, y), letter, fill=WHITE, font=font)
    
    return img


def create_arrow_icon(size=512):
    """创建双向箭头图标"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    draw.ellipse([(0, 0), (size, size)], fill=BRAND_COLOR)
    
    # 绘制双向箭头
    arrow_width = size // 10
    arrow_length = int(size * 0.6)
    center_y = size // 2
    
    # 左箭头 →
    right_arrow_start = int(size * 0.2)
    right_arrow_end = right_arrow_start + arrow_length
    
    # 箭头线
    draw.rectangle(
        [(right_arrow_start, center_y - arrow_width // 2),
         (right_arrow_end, center_y + arrow_width // 2)],
        fill=WHITE
    )
    
    # 箭头头部
    arrow_head_size = arrow_width * 2
    draw.polygon([
        (right_arrow_end, center_y),
        (right_arrow_end - arrow_head_size, center_y - arrow_head_size),
        (right_arrow_end - arrow_head_size, center_y + arrow_head_size)
    ], fill=WHITE)
    
    # 左箭头 ←
    left_arrow_end = int(size * 0.8)
    left_arrow_start = left_arrow_end - arrow_length
    
    # 箭头线
    draw.rectangle(
        [(left_arrow_start, center_y - arrow_width // 2 + arrow_width * 2),
         (left_arrow_end, center_y + arrow_width // 2 + arrow_width * 2)],
        fill=WHITE
    )
    
    # 箭头头部
    draw.polygon([
        (left_arrow_start, center_y + arrow_width * 2),
        (left_arrow_start + arrow_head_size, center_y - arrow_head_size + arrow_width * 2),
        (left_arrow_start + arrow_head_size, center_y + arrow_head_size + arrow_width * 2)
    ], fill=WHITE)
    
    return img


def generate_all_sizes(icon_func, prefix="icon"):
    """生成所有尺寸的图标"""
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"🎨 生成图标样式: {prefix}")
    print("")
    
    for size in SIZES:
        print(f"  ⏳ 生成 {size}x{size}...", end=" ")
        
        if callable(icon_func):
            img = icon_func(size)
        else:
            img = create_letter_icon(size, icon_func)
        
        filename = f"{OUTPUT_DIR}/{size}x{size}.png"
        img.save(filename)
        
        print(f"✅ {filename}")
    
    # 额外生成一个512大图用于转换
    print(f"\n  ⏳ 生成源文件 (512x512)...", end=" ")
    if callable(icon_func):
        img = icon_func(512)
    else:
        img = create_letter_icon(512, icon_func)
    
    source_file = f"{OUTPUT_DIR}/../icon_512.png"
    img.save(source_file)
    print(f"✅ {source_file}")


def generate_dmg_background():
    """生成macOS DMG背景图"""
    width = 540
    height = 380
    
    img = Image.new('RGB', (width, height), (248, 248, 248))
    draw = ImageDraw.Draw(img)
    
    # 绘制应用图标（左侧）
    icon_size = 128
    icon_x = 144 - icon_size // 2
    icon_y = 188 - icon_size // 2
    
    # 简化版图标
    icon_img = create_letter_icon(icon_size)
    img.paste(icon_img, (icon_x, icon_y), icon_img)
    
    # 绘制箭头
    arrow_start = icon_x + icon_size + 20
    arrow_end = 396 - 64 - 20
    arrow_y = 188
    
    draw.line([(arrow_start, arrow_y), (arrow_end, arrow_y)], 
              fill=(108, 92, 231), width=3)
    draw.polygon([
        (arrow_end, arrow_y),
        (arrow_end - 10, arrow_y - 10),
        (arrow_end - 10, arrow_y + 10)
    ], fill=(108, 92, 231))
    
    # 绘制Applications文件夹图标（右侧）
    folder_size = 128
    folder_x = 396 - folder_size // 2
    folder_y = 188 - folder_size // 2
    
    # 简化版文件夹
    draw.rounded_rectangle(
        [(folder_x, folder_y), (folder_x + folder_size, folder_y + folder_size)],
        radius=15,
        fill=(108, 92, 231, 128)
    )
    
    # 添加文字
    try:
        font = ImageFont.truetype("Arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    text = "Drag to Applications"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    text_y = 320
    
    draw.text((text_x, text_y), text, fill=(80, 80, 80), font=font)
    
    # 保存
    output_file = "build/dmg-background.png"
    img.save(output_file)
    print(f"\n📦 DMG背景图已生成: {output_file}")


def main():
    """主函数"""
    print("="*60)
    print("KOOK消息转发系统 - 占位图标生成器")
    print("="*60)
    print("")
    
    choice = input("选择图标样式:\n  1. 字母 'K' 图标（简洁）\n  2. 双向箭头图标（形象）\n请输入选项 [1/2，默认1]: ").strip()
    
    if choice == "2":
        generate_all_sizes(create_arrow_icon, "arrow")
    else:
        generate_all_sizes("K", "letter")
    
    # 生成DMG背景
    generate_dmg = input("\n是否生成macOS DMG背景图? [y/N]: ").strip().lower()
    if generate_dmg == 'y':
        generate_dmg_background()
    
    print("")
    print("="*60)
    print("✅ 所有图标已生成完成！")
    print("")
    print("📝 下一步:")
    print("  1. 使用在线工具将 icon_512.png 转换为:")
    print("     - Windows ICO: https://www.icoconverter.com")
    print("     - macOS ICNS: https://cloudconvert.com")
    print("  2. 将生成的图标文件放到正确位置:")
    print("     - build/icon.ico (Windows)")
    print("     - build/icon.icns (macOS)")
    print("     - build/icons/*.png (Linux)")
    print("  3. 或者雇佣设计师设计更专业的图标")
    print("")
    print("📚 详细说明请查看: build/ICON_REQUIREMENTS.md")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
    except Exception as e:
        print(f"\n\n❌ 错误: {str(e)}")
        print("请确保已安装 Pillow: pip install Pillow")
