# 应用图标说明

## 当前状态

已创建SVG源文件：`icon.svg`

## 生成其他格式

由于需要特定的图像处理工具，请根据你的操作系统使用以下方法生成图标：

### 方法1：在线工具（推荐，最简单）

1. 访问 https://www.icoconverter.com/ 或 https://cloudconvert.com/
2. 上传 `icon.svg` 文件
3. 转换为以下格式：
   - **Windows**: `icon.ico` (256x256, 128x128, 64x64, 48x48, 32x32, 16x16)
   - **macOS**: `icon.icns` (1024x1024, 512x512, 256x256, 128x128, 64x64, 32x32, 16x16)
   - **Linux**: `icon.png` (512x512)

### 方法2：使用ImageMagick（命令行）

如果已安装ImageMagick：

```bash
# 生成PNG（各种尺寸）
convert icon.svg -resize 16x16 icon-16.png
convert icon.svg -resize 32x32 icon-32.png
convert icon.svg -resize 48x48 icon-48.png
convert icon.svg -resize 64x64 icon-64.png
convert icon.svg -resize 128x128 icon-128.png
convert icon.svg -resize 256x256 icon-256.png
convert icon.svg -resize 512x512 icon.png

# 生成ICO（Windows）
convert icon.svg -define icon:auto-resize=256,128,64,48,32,16 icon.ico

# 生成ICNS（macOS，需要额外工具）
# 安装 png2icns: brew install libicns
mkdir icon.iconset
cp icon-16.png icon.iconset/icon_16x16.png
cp icon-32.png icon.iconset/icon_16x16@2x.png
cp icon-32.png icon.iconset/icon_32x32.png
cp icon-64.png icon.iconset/icon_32x32@2x.png
cp icon-128.png icon.iconset/icon_128x128.png
cp icon-256.png icon.iconset/icon_128x128@2x.png
cp icon-256.png icon.iconset/icon_256x256.png
cp icon-512.png icon.iconset/icon_256x256@2x.png
cp icon.png icon.iconset/icon_512x512.png
iconutil -c icns icon.iconset
```

### 方法3：使用Node.js工具

如果你在前端目录有Node.js环境：

```bash
npm install -g svg2png-cli
npm install -g png2icons

# 生成PNG
svg2png icon.svg --width 512 --height 512 --output icon.png

# 生成ICO和ICNS
png2icons icon.png icon -icns -ico
```

### 方法4：手动使用设计工具

1. 在Figma/Sketch/Photoshop中打开SVG
2. 导出为各种尺寸的PNG
3. 使用在线工具或专用软件转换为ICO/ICNS

## 最终文件位置

完成后，确保以下文件存在：

```
build/
├── icon.svg          ✅ 已创建（源文件）
├── icon.ico          ⚠️ 待生成（Windows）
├── icon.icns         ⚠️ 待生成（macOS）
└── icon.png          ⚠️ 待生成（Linux，512x512）
```

## 图标设计说明

当前图标设计包含：
- **渐变背景**：紫色到蓝色渐变，现代感
- **双向箭头**：表示消息转发
- **消息框**：左右两侧的消息框代表KOOK和目标平台
- **KOOK文字**：底部标识

如需修改设计，请编辑 `icon.svg` 文件。

## 快速生成脚本（推荐）

我已经在项目中创建了图标生成脚本：

```bash
# 如果有ImageMagick
cd build
./generate_icons.sh

# 或者使用Python脚本（需要PIL）
python generate_icons.py
```

如果这些脚本不存在，请参考上述方法手动生成。
