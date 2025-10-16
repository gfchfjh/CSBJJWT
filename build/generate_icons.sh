#!/bin/bash
# 应用图标生成脚本（使用ImageMagick）

set -e

echo "🎨 KOOK消息转发系统 - 图标生成脚本"
echo "=================================="
echo ""

# 检查ImageMagick是否安装
if ! command -v convert &> /dev/null; then
    echo "❌ 未找到ImageMagick，请先安装："
    echo ""
    echo "macOS:   brew install imagemagick"
    echo "Ubuntu:  sudo apt-get install imagemagick"
    echo "CentOS:  sudo yum install imagemagick"
    echo "Windows: 从 https://imagemagick.org/script/download.php 下载"
    echo ""
    exit 1
fi

echo "✅ 检测到ImageMagick"
echo ""

# 确保在build目录
cd "$(dirname "$0")"

# 检查SVG源文件
if [ ! -f "icon.svg" ]; then
    echo "❌ 未找到 icon.svg 源文件"
    exit 1
fi

echo "📦 开始生成图标文件..."
echo ""

# 生成各种尺寸的PNG
echo "1️⃣ 生成PNG文件（各种尺寸）"
for size in 16 32 48 64 128 256 512; do
    echo "   - 生成 ${size}x${size} PNG"
    convert icon.svg -resize ${size}x${size} icon-${size}.png
done

# 生成主图标（512x512）
echo "   - 生成主图标 icon.png (512x512)"
cp icon-512.png icon.png

echo "   ✅ PNG文件生成完成"
echo ""

# 生成ICO（Windows）
echo "2️⃣ 生成Windows ICO文件"
echo "   - 包含尺寸: 16, 32, 48, 64, 128, 256"
convert icon.svg -define icon:auto-resize=256,128,64,48,32,16 icon.ico
echo "   ✅ icon.ico 生成完成"
echo ""

# 生成ICNS（macOS）
echo "3️⃣ 生成macOS ICNS文件"

# 检查iconutil（macOS专用）
if command -v iconutil &> /dev/null; then
    echo "   - 检测到macOS iconutil工具"
    
    # 创建iconset目录
    mkdir -p icon.iconset
    
    # 复制各种尺寸
    cp icon-16.png icon.iconset/icon_16x16.png
    cp icon-32.png icon.iconset/icon_16x16@2x.png
    cp icon-32.png icon.iconset/icon_32x32.png
    cp icon-64.png icon.iconset/icon_32x32@2x.png
    cp icon-128.png icon.iconset/icon_128x128.png
    cp icon-256.png icon.iconset/icon_128x128@2x.png
    cp icon-256.png icon.iconset/icon_256x256.png
    cp icon-512.png icon.iconset/icon_256x256@2x.png
    cp icon-512.png icon.iconset/icon_512x512.png
    
    # 生成ICNS
    iconutil -c icns icon.iconset
    
    # 清理
    rm -rf icon.iconset
    
    echo "   ✅ icon.icns 生成完成"
else
    echo "   ⚠️  未找到iconutil（仅macOS可用）"
    echo "   💡 如需生成.icns文件，请："
    echo "      1. 在macOS上运行此脚本"
    echo "      2. 或使用在线工具: https://cloudconvert.com/png-to-icns"
fi

echo ""

# 清理中间文件
echo "4️⃣ 清理中间文件"
for size in 16 32 48 64 128 256; do
    rm -f icon-${size}.png
done
echo "   ✅ 清理完成"
echo ""

# 显示结果
echo "=================================="
echo "🎉 图标生成完成！"
echo ""
echo "生成的文件："
ls -lh icon.* 2>/dev/null | grep -v "icon.svg" || true
echo ""
echo "文件位置："
echo "  - icon.png  → Linux图标 (512x512)"
echo "  - icon.ico  → Windows图标"
if [ -f "icon.icns" ]; then
    echo "  - icon.icns → macOS图标"
else
    echo "  - icon.icns → 未生成（需要在macOS上运行）"
fi
echo ""
echo "✅ 可以开始打包应用了！"
