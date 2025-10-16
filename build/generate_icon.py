"""
生成应用图标脚本
从SVG生成各平台所需的图标格式
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cairosvg

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
BUILD_DIR = ROOT_DIR / "build"
FRONTEND_PUBLIC_DIR = ROOT_DIR / "frontend" / "public"

# 图标尺寸
ICON_SIZES = {
    'windows': [16, 24, 32, 48, 64, 128, 256],
    'mac': [16, 32, 64, 128, 256, 512, 1024],
    'linux': [16, 24, 32, 48, 64, 128, 256, 512],
    'png': [256]  # 通用PNG
}


def create_simple_icon():
    """创建简单的应用图标（如果没有SVG源文件）"""
    size = 512
    
    # 创建带渐变背景的图标
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变圆形背景
    for i in range(size):
        ratio = i / size
        r = int(102 + (118 - 102) * ratio)  # 从 #667eea 到 #764ba2
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        
        center = size // 2
        radius = size // 2 - i
        if radius > 0:
            draw.ellipse(
                [center - radius, center - radius, center + radius, center + radius],
                fill=(r, g, b, 255)
            )
    
    # 绘制白色的"K"字母
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size // 2)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/Arial.ttf", size // 2)
        except:
            font = ImageFont.load_default()
    
    # 绘制文字
    text = "K"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - size // 20
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # 添加底部小文字
    try:
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size // 10)
    except:
        try:
            small_font = ImageFont.truetype("C:/Windows/Fonts/Arial.ttf", size // 10)
        except:
            small_font = ImageFont.load_default()
    
    small_text = "转发"
    bbox = draw.textbbox((0, 0), small_text, font=small_font)
    text_width = bbox[2] - bbox[0]
    
    x = (size - text_width) // 2
    y = size * 3 // 4
    
    draw.text((x, y), small_text, fill=(255, 255, 255, 200), font=small_font)
    
    return img


def convert_svg_to_png(svg_path, output_path, size):
    """将SVG转换为PNG"""
    try:
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(output_path),
            output_width=size,
            output_height=size
        )
        print(f"✅ 生成 {size}x{size} PNG: {output_path}")
        return True
    except Exception as e:
        print(f"❌ SVG转PNG失败: {e}")
        return False


def generate_ico(png_images, output_path):
    """生成Windows ICO文件"""
    try:
        # ICO文件包含多个尺寸
        images = []
        for size in [16, 24, 32, 48, 64, 128, 256]:
            if size in png_images:
                img = Image.open(png_images[size])
                images.append(img)
        
        if images:
            images[0].save(
                output_path,
                format='ICO',
                sizes=[(img.width, img.height) for img in images]
            )
            print(f"✅ 生成 Windows ICO: {output_path}")
            return True
    except Exception as e:
        print(f"❌ 生成ICO失败: {e}")
        return False


def generate_icns(png_images, output_path):
    """生成macOS ICNS文件"""
    try:
        # macOS需要特定尺寸的iconset
        iconset_dir = output_path.parent / "icon.iconset"
        iconset_dir.mkdir(exist_ok=True)
        
        icns_sizes = {
            16: "16x16",
            32: ["16x16@2x", "32x32"],
            64: "32x32@2x",
            128: ["64x64", "128x128"],
            256: ["128x128@2x", "256x256"],
            512: ["256x256@2x", "512x512"],
            1024: "512x512@2x"
        }
        
        for size, names in icns_sizes.items():
            if size in png_images:
                img = Image.open(png_images[size])
                if isinstance(names, list):
                    for name in names:
                        img.save(iconset_dir / f"icon_{name}.png")
                else:
                    img.save(iconset_dir / f"icon_{names}.png")
        
        # 使用iconutil生成icns（仅macOS）
        import platform
        if platform.system() == 'Darwin':
            os.system(f"iconutil -c icns {iconset_dir} -o {output_path}")
            print(f"✅ 生成 macOS ICNS: {output_path}")
        else:
            print(f"⚠️  非macOS系统，跳过ICNS生成（需要在macOS上运行iconutil）")
        
        return True
    except Exception as e:
        print(f"❌ 生成ICNS失败: {e}")
        return False


def main():
    print("=" * 60)
    print("KOOK消息转发系统 - 图标生成工具")
    print("=" * 60)
    
    # 检查SVG源文件
    svg_path = BUILD_DIR / "icon.svg"
    
    if not svg_path.exists():
        print(f"⚠️  未找到 {svg_path}")
        print("📝 生成默认图标...")
        
        # 生成默认图标
        base_icon = create_simple_icon()
        
        # 保存基础PNG
        base_png = BUILD_DIR / "icon_512.png"
        base_icon.save(base_png)
        print(f"✅ 生成基础图标: {base_png}")
    else:
        print(f"✅ 找到SVG源文件: {svg_path}")
        # 从SVG生成512x512的基础图标
        base_png = BUILD_DIR / "icon_512.png"
        if convert_svg_to_png(svg_path, base_png, 512):
            base_icon = Image.open(base_png)
        else:
            print("📝 生成默认图标...")
            base_icon = create_simple_icon()
            base_icon.save(base_png)
    
    # 生成各种尺寸的PNG
    print("\n📐 生成不同尺寸的PNG...")
    png_images = {}
    
    for size in sorted(set(ICON_SIZES['windows'] + ICON_SIZES['mac'] + ICON_SIZES['linux'])):
        img = base_icon.resize((size, size), Image.Resampling.LANCZOS)
        png_path = BUILD_DIR / f"icon_{size}.png"
        img.save(png_path)
        png_images[size] = png_path
        print(f"  ✅ {size}x{size}")
    
    # 生成Windows ICO
    print("\n🪟 生成Windows图标...")
    ico_path = BUILD_DIR / "icon.ico"
    generate_ico(png_images, ico_path)
    
    # 复制到frontend/public
    frontend_ico = FRONTEND_PUBLIC_DIR / "icon.ico"
    if ico_path.exists():
        import shutil
        shutil.copy2(ico_path, frontend_ico)
        print(f"  ✅ 复制到: {frontend_ico}")
    
    # 生成macOS ICNS
    print("\n🍎 生成macOS图标...")
    icns_path = BUILD_DIR / "icon.icns"
    generate_icns(png_images, icns_path)
    
    # 生成Linux PNG
    print("\n🐧 生成Linux图标...")
    linux_png = BUILD_DIR / "icon.png"
    png_images[256].copy(linux_png) if 256 in png_images else None
    frontend_png = FRONTEND_PUBLIC_DIR / "icon.png"
    if linux_png.exists():
        import shutil
        shutil.copy2(linux_png, frontend_png)
        print(f"  ✅ {linux_png}")
        print(f"  ✅ 复制到: {frontend_png}")
    
    # 生成favicon
    print("\n🌐 生成Favicon...")
    if 32 in png_images:
        favicon_path = FRONTEND_PUBLIC_DIR / "favicon.ico"
        img_32 = Image.open(png_images[32])
        img_32.save(favicon_path, format='ICO')
        print(f"  ✅ {favicon_path}")
    
    print("\n" + "=" * 60)
    print("✅ 图标生成完成！")
    print("=" * 60)
    print("\n生成的文件：")
    print(f"  - Windows ICO: {ico_path}")
    print(f"  - macOS ICNS: {icns_path}")
    print(f"  - Linux PNG: {linux_png}")
    print(f"  - Frontend: {frontend_ico}, {frontend_png}")


if __name__ == "__main__":
    main()
