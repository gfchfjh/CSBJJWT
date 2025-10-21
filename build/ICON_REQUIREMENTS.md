# 应用图标需求说明

本文档说明KOOK消息转发系统所需的应用图标规格和制作方法。

---

## 📋 所需图标文件

### 1. Windows图标

**文件**: `build/icon.ico`

**规格**:
- 格式: ICO
- 尺寸: 256x256像素（主尺寸）
- 包含多尺寸: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
- 颜色深度: 32位（包含透明通道）
- 用途: Windows安装程序、可执行文件图标

### 2. macOS图标

**文件**: `build/icon.icns`

**规格**:
- 格式: ICNS
- 尺寸: 512x512@2x（1024x1024）
- 包含多尺寸: 16x16, 32x32, 128x128, 256x256, 512x512（各@1x和@2x）
- 用途: macOS应用图标、DMG背景

### 3. Linux图标

**文件夹**: `build/icons/`

**规格**:
- 格式: PNG（带透明通道）
- 尺寸: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256, 512x512
- 文件名: 
  - `16x16.png`
  - `32x32.png`
  - `48x48.png`
  - `64x64.png`
  - `128x128.png`
  - `256x256.png`
  - `512x512.png`
- 用途: Linux AppImage图标、桌面快捷方式

### 4. DMG背景图

**文件**: `build/dmg-background.png`

**规格**:
- 格式: PNG
- 尺寸: 540x380像素
- 内容: 应用图标 + "拖动到Applications文件夹"提示
- 用途: macOS DMG安装界面背景

### 5. Web图标（可选）

**文件**: `frontend/public/favicon.ico` 和 `frontend/public/icon.png`

**规格**:
- favicon.ico: 32x32
- icon.png: 512x512
- 用途: 浏览器标签页图标

---

## 🎨 设计建议

### 图标设计理念

**核心元素**:
1. **KOOK品牌色**: 
   - 主色: #6C5CE7（紫色，KOOK标志性颜色）
   - 辅色: #00B894（绿色，表示"在线/转发"）
   
2. **图形元素**:
   - 主体: 对话气泡或消息图标
   - 特征: 双向箭头（表示转发）
   - 附加: KOOK的"K"字母或Logo元素

3. **风格**:
   - 扁平化设计
   - 圆角矩形或圆形背景
   - 简洁明了，避免复杂细节
   - 在小尺寸下仍清晰可辨

### 配色方案推荐

```
方案1: 紫色主题（推荐）
- 背景: #6C5CE7 (KOOK紫)
- 图标: #FFFFFF (白色箭头/消息)
- 边框: #5849C7 (深紫色)

方案2: 渐变主题
- 渐变: #6C5CE7 → #00B894
- 图标: #FFFFFF
- 现代感更强

方案3: 简约主题
- 背景: #FFFFFF
- 图标: #6C5CE7
- 边框: #E0E0E0
- 适合浅色系统
```

### 图标草图示例

```
┌────────────────┐
│   ╔══════╗    │  ← 圆角矩形背景（紫色）
│   ║ KOOK ║    │  ← "KOOK"文字或K字母
│   ║  ⇄   ║    │  ← 双向箭头（白色）
│   ╚══════╝    │
└────────────────┘

或

┌────────────────┐
│    ●───→●     │  ← 消息传递示意
│   KOOK  →  DC  │  ← 简化的平台标识
└────────────────┘
```

---

## 🔧 制作工具推荐

### 在线工具（免费）

1. **Canva** (https://www.canva.com)
   - 功能: 图形设计，有免费模板
   - 优点: 简单易用，适合非设计师
   - 导出: PNG（需转换为ICO/ICNS）

2. **Figma** (https://www.figma.com)
   - 功能: 专业UI设计工具
   - 优点: 矢量设计，导出多尺寸方便
   - 免费版: 功能足够使用

3. **Photopea** (https://www.photopea.com)
   - 功能: 在线Photoshop替代品
   - 优点: 支持PSD格式，功能强大
   - 完全免费

### 桌面软件

1. **GIMP** (免费)
   - https://www.gimp.org
   - 功能全面的图像编辑软件
   - 支持多种导出格式

2. **Inkscape** (免费)
   - https://inkscape.org
   - 矢量图形编辑器
   - 适合制作可缩放图标

3. **Adobe Photoshop/Illustrator** (付费)
   - 专业设计软件
   - 功能最强大

### 格式转换工具

1. **ICO转换** (在线)
   - https://www.icoconverter.com
   - PNG转ICO，支持多尺寸

2. **ICNS转换** (在线)
   - https://cloudconvert.com
   - PNG转ICNS（macOS）

3. **命令行工具**
   ```bash
   # macOS: PNG转ICNS
   brew install imagemagick
   mkdir icon.iconset
   # 生成不同尺寸
   sips -z 16 16   icon_512.png --out icon.iconset/icon_16x16.png
   sips -z 32 32   icon_512.png --out icon.iconset/icon_16x16@2x.png
   # ... 其他尺寸
   iconutil -c icns icon.iconset
   
   # Windows: PNG转ICO
   # 使用ImageMagick
   magick convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
   ```

---

## 📝 制作步骤

### 方法1: 使用Canva（推荐新手）

1. **创建设计**
   - 访问 https://www.canva.com
   - 新建自定义尺寸: 512x512像素
   - 选择"Logo"模板或从空白开始

2. **设计图标**
   - 添加圆角矩形作为背景（颜色: #6C5CE7）
   - 添加消息图标或双向箭头（颜色: #FFFFFF）
   - 添加"KOOK"文字或"K"字母（可选）
   - 确保图标在小尺寸下清晰可辨

3. **导出图像**
   - 导出为PNG格式，512x512像素
   - 背景透明（重要！）
   - 下载文件，命名为 `icon_512.png`

4. **生成多尺寸图标**
   - 使用在线工具：
     - Windows ICO: https://www.icoconverter.com
     - macOS ICNS: https://cloudconvert.com
     - Linux PNG: 使用GIMP批量缩放

### 方法2: 使用AI工具生成（最快）

1. **使用DALL-E/Midjourney/Stable Diffusion**
   
   提示词示例:
   ```
   A modern, minimalist app icon for a message forwarding application.
   Purple rounded square background (#6C5CE7).
   White bidirectional arrow icon in the center.
   Clean, flat design style.
   Simple and recognizable at small sizes.
   512x512 pixels, transparent background.
   ```

2. **生成后处理**
   - 使用Photopea或GIMP调整颜色
   - 确保背景透明
   - 调整对比度，使小尺寸清晰

3. **批量转换格式**
   - 按照上述格式转换工具生成ICO/ICNS/PNG

### 方法3: 雇佣设计师（最专业）

**推荐平台**:
- Fiverr: $5-50美元
- Upwork: $20-100美元
- 站酷/UI中国（国内）: ¥100-500元

**需求说明模板**:
```
项目: KOOK消息转发系统应用图标设计

需求:
1. 设计一个现代、简洁的应用图标
2. 主题: 消息转发、跨平台通信
3. 配色: 
   - 主色: #6C5CE7（紫色）
   - 辅色: #00B894（绿色）或#FFFFFF（白色）
4. 风格: 扁平化、圆角、简洁
5. 尺寸: 提供512x512源文件（PNG，透明背景）
6. 格式: 需要转换为ICO、ICNS、多尺寸PNG

参考:
- Discord图标（简洁）
- Telegram图标（现代）
- Slack图标（专业）

交付文件:
- 512x512 PNG源文件
- Windows ICO（多尺寸）
- macOS ICNS
- Linux PNG图标包
- 可编辑的源文件（PSD/AI/SVG）
```

---

## ✅ 检查清单

在提交图标前，请确认：

- [ ] **Windows ICO**
  - [ ] 文件存在: `build/icon.ico`
  - [ ] 包含多尺寸: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
  - [ ] 32位颜色深度（支持透明）
  - [ ] 在Windows资源管理器中预览正常

- [ ] **macOS ICNS**
  - [ ] 文件存在: `build/icon.icns`
  - [ ] 包含@1x和@2x尺寸
  - [ ] 在macOS Finder中预览正常
  - [ ] 拖拽到应用程序文件夹显示正确

- [ ] **Linux PNG**
  - [ ] 文件夹存在: `build/icons/`
  - [ ] 包含所有尺寸: 16-512
  - [ ] PNG格式，透明背景
  - [ ] 在Nautilus/Dolphin文件管理器中显示正常

- [ ] **DMG背景**
  - [ ] 文件存在: `build/dmg-background.png`
  - [ ] 尺寸: 540x380
  - [ ] 包含应用图标和拖拽提示
  - [ ] 背景美观，文字清晰

- [ ] **通用要求**
  - [ ] 小尺寸（16x16）下仍清晰可辨
  - [ ] 颜色对比度足够
  - [ ] 与KOOK品牌一致
  - [ ] 在浅色/深色背景下都好看

---

## 🎨 临时占位图标

如果暂时没有设计好的图标，可以使用简单的字母图标作为占位：

### 快速生成占位图标

```python
# 使用Python PIL生成简单图标
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_icon(size=512):
    # 创建紫色背景
    img = Image.new('RGBA', (size, size), (108, 92, 231, 255))
    draw = ImageDraw.Draw(img)
    
    # 绘制白色"K"字母
    font_size = int(size * 0.6)
    try:
        font = ImageFont.truetype("Arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "K"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # 保存
    img.save('icon_512.png')
    print("✅ 占位图标已生成: icon_512.png")

if __name__ == "__main__":
    create_placeholder_icon()
```

运行此脚本会生成一个紫色背景、白色"K"字母的简单图标，可用作临时占位。

---

## 📚 参考资源

- [Apple Human Interface Guidelines - Icons](https://developer.apple.com/design/human-interface-guidelines/macos/icons-and-images/app-icon/)
- [Microsoft Icon Guidelines](https://docs.microsoft.com/en-us/windows/apps/design/style/iconography/app-icons)
- [Material Design Icons](https://material.io/design/iconography/product-icons.html)
- [Icon Handbook](https://iconhandbook.co.uk/)

---

**最后更新**: 2025-10-21  
**适用版本**: v1.11.0+
