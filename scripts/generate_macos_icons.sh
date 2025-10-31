#!/bin/bash
#
# macOS图标生成脚本
# v17.0.0深度优化
# 
# 功能：将PNG图标转换为macOS .icns格式
# 依赖：imagemagick (brew install imagemagick)
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  macOS图标生成脚本 v17.0.0${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查依赖
echo -e "${YELLOW}检查依赖...${NC}"

if ! command -v convert &> /dev/null; then
    echo -e "${RED}错误: 未找到ImageMagick${NC}"
    echo -e "${YELLOW}请安装: brew install imagemagick${NC}"
    exit 1
fi

echo -e "${GREEN}✓ ImageMagick已安装${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 源图标文件
SOURCE_PNG="$PROJECT_ROOT/build/icon-1024.png"

# 检查源文件
if [ ! -f "$SOURCE_PNG" ]; then
    echo -e "${RED}错误: 未找到源图标文件: $SOURCE_PNG${NC}"
    echo -e "${YELLOW}请确保 build/icon-1024.png 文件存在${NC}"
    exit 1
fi

echo -e "${GREEN}源图标: $SOURCE_PNG${NC}"
echo ""

# 创建临时目录
TEMP_DIR="$PROJECT_ROOT/build/icon.iconset"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo -e "${YELLOW}生成不同尺寸的图标...${NC}"

# 生成各种尺寸的图标
# macOS要求的尺寸：16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024
# 每种尺寸需要标准版和@2x版本

# 16x16
convert "$SOURCE_PNG" -resize 16x16 "$TEMP_DIR/icon_16x16.png"
convert "$SOURCE_PNG" -resize 32x32 "$TEMP_DIR/icon_16x16@2x.png"
echo -e "${GREEN}✓ 16x16 图标生成完成${NC}"

# 32x32
convert "$SOURCE_PNG" -resize 32x32 "$TEMP_DIR/icon_32x32.png"
convert "$SOURCE_PNG" -resize 64x64 "$TEMP_DIR/icon_32x32@2x.png"
echo -e "${GREEN}✓ 32x32 图标生成完成${NC}"

# 64x64 (macOS 10.7+)
convert "$SOURCE_PNG" -resize 64x64 "$TEMP_DIR/icon_64x64.png"
convert "$SOURCE_PNG" -resize 128x128 "$TEMP_DIR/icon_64x64@2x.png"
echo -e "${GREEN}✓ 64x64 图标生成完成${NC}"

# 128x128
convert "$SOURCE_PNG" -resize 128x128 "$TEMP_DIR/icon_128x128.png"
convert "$SOURCE_PNG" -resize 256x256 "$TEMP_DIR/icon_128x128@2x.png"
echo -e "${GREEN}✓ 128x128 图标生成完成${NC}"

# 256x256
convert "$SOURCE_PNG" -resize 256x256 "$TEMP_DIR/icon_256x256.png"
convert "$SOURCE_PNG" -resize 512x512 "$TEMP_DIR/icon_256x256@2x.png"
echo -e "${GREEN}✓ 256x256 图标生成完成${NC}"

# 512x512
convert "$SOURCE_PNG" -resize 512x512 "$TEMP_DIR/icon_512x512.png"
convert "$SOURCE_PNG" -resize 1024x1024 "$TEMP_DIR/icon_512x512@2x.png"
echo -e "${GREEN}✓ 512x512 图标生成完成${NC}"

echo ""
echo -e "${YELLOW}转换为.icns格式...${NC}"

# 转换为icns格式
OUTPUT_ICNS="$PROJECT_ROOT/build/icon.icns"
iconutil -c icns "$TEMP_DIR" -o "$OUTPUT_ICNS"

if [ -f "$OUTPUT_ICNS" ]; then
    echo -e "${GREEN}✓ icns文件生成成功: $OUTPUT_ICNS${NC}"
    
    # 显示文件信息
    FILE_SIZE=$(du -h "$OUTPUT_ICNS" | cut -f1)
    echo -e "${GREEN}  文件大小: $FILE_SIZE${NC}"
    
    # 验证icns文件
    if command -v sips &> /dev/null; then
        echo ""
        echo -e "${YELLOW}验证icns文件...${NC}"
        sips -g all "$OUTPUT_ICNS" | head -10
    fi
else
    echo -e "${RED}错误: icns文件生成失败${NC}"
    exit 1
fi

# 清理临时文件
echo ""
echo -e "${YELLOW}清理临时文件...${NC}"
rm -rf "$TEMP_DIR"
echo -e "${GREEN}✓ 清理完成${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  macOS图标生成成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "输出文件: ${YELLOW}$OUTPUT_ICNS${NC}"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo -e "1. 将icon.icns复制到 build/目录"
echo -e "2. 在electron-builder.yml中配置:"
echo -e "   ${YELLOW}mac:${NC}"
echo -e "     ${YELLOW}icon: build/icon.icns${NC}"
echo -e "3. 运行构建: ${YELLOW}npm run electron:build:mac${NC}"
echo ""
