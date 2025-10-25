"""
生成专业品牌图标
✅ P0-12优化：创建专业的应用图标和品牌形象
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from pathlib import Path


class ProfessionalIconGenerator:
    """专业图标生成器"""
    
    # 品牌配色方案
    PRIMARY_COLOR = (64, 158, 255)      # 主色调 #409EFF (蓝色)
    SECONDARY_COLOR = (103, 194, 58)    # 辅助色 #67C23A (绿色)
    ACCENT_COLOR = (230, 162, 60)       # 强调色 #E6A23C (橙色)
    BACKGROUND_COLOR = (255, 255, 255)  # 背景色 (白色)
    DARK_COLOR = (48, 49, 51)           # 深色 #303133
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all_sizes(self):
        """生成所有尺寸的图标"""
        sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
        
        for size in sizes:
            print(f"生成 {size}x{size} 图标...")
            self.generate_icon(size)
        
        print("✅ 所有图标生成完成")
    
    def generate_icon(self, size: int):
        """
        生成指定尺寸的图标
        
        设计理念：
        - 使用信封/消息符号表示"转发"
        - 双箭头表示"多平台"
        - 圆润的设计风格
        - 专业的配色
        """
        # 创建画布
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 计算尺寸参数
        padding = int(size * 0.1)
        center_x = size // 2
        center_y = size // 2
        
        # 绘制圆形背景（渐变效果用多个圆模拟）
        for i in range(50, 0, -1):
            radius = int(size * 0.42 * (i / 50))
            alpha = int(255 * (i / 50))
            color = (*self.PRIMARY_COLOR, alpha)
            draw.ellipse(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                fill=color
            )
        
        # 绘制主图标：双向箭头（表示转发）
        arrow_width = int(size * 0.5)
        arrow_height = int(size * 0.15)
        arrow_y = center_y
        
        # 左箭头（KOOK → 目标平台）
        left_arrow_points = [
            (center_x - arrow_width // 2, arrow_y),
            (center_x + arrow_width // 2 - int(size * 0.08), arrow_y),
            (center_x + arrow_width // 2 - int(size * 0.08), arrow_y - arrow_height),
            (center_x + arrow_width // 2, arrow_y),
            (center_x + arrow_width // 2 - int(size * 0.08), arrow_y + arrow_height),
            (center_x + arrow_width // 2 - int(size * 0.08), arrow_y),
        ]
        draw.polygon(left_arrow_points, fill=self.BACKGROUND_COLOR)
        
        # 添加阴影效果
        img_shadow = img.filter(ImageFilter.GaussianBlur(radius=2))
        
        # 保存图标
        output_path = self.output_dir / f"icon-{size}.png"
        img.save(output_path, 'PNG')
        print(f"  → {output_path}")
    
    def generate_svg_icon(self):
        """
        生成SVG矢量图标
        """
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#409EFF;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#67C23A;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- 背景圆 -->
  <circle cx="256" cy="256" r="240" fill="url(#bgGradient)" />
  
  <!-- 转发箭头图标 -->
  <g transform="translate(256, 256)">
    <!-- 第一个箭头 -->
    <path d="M -80 -30 L 60 -30 L 60 -50 L 100 -10 L 60 30 L 60 10 L -80 10 Z" 
          fill="#FFFFFF" opacity="0.9"/>
    
    <!-- 第二个箭头 -->
    <path d="M 80 30 L -60 30 L -60 50 L -100 10 L -60 -30 L -60 -10 L 80 -10 Z" 
          fill="#FFFFFF" opacity="0.9"/>
  </g>
  
  <!-- 装饰小点 -->
  <circle cx="156" cy="156" r="8" fill="#FFFFFF" opacity="0.6"/>
  <circle cx="356" cy="156" r="8" fill="#FFFFFF" opacity="0.6"/>
  <circle cx="156" cy="356" r="8" fill="#FFFFFF" opacity="0.6"/>
  <circle cx="356" cy="356" r="8" fill="#FFFFFF" opacity="0.6"/>
</svg>'''
        
        svg_path = self.output_dir / "icon.svg"
        svg_path.write_text(svg_content, encoding='utf-8')
        print(f"✅ SVG图标已生成: {svg_path}")
    
    def generate_brand_guidelines(self):
        """
        生成品牌指南文档
        """
        guidelines = """# KOOK消息转发系统 - 品牌指南

## 🎨 品牌色彩

### 主色调
- **主要蓝色** `#409EFF` RGB(64, 158, 255)
  - 用途：主要按钮、链接、标题
  - 含义：可信、专业、科技

### 辅助色
- **成功绿色** `#67C23A` RGB(103, 194, 58)
  - 用途：成功状态、确认按钮
  - 含义：活力、成功、增长

- **警告橙色** `#E6A23C` RGB(230, 162, 60)
  - 用途：警告提示、重要信息
  - 含义：注意、提醒

- **危险红色** `#F56C6C` RGB(245, 108, 108)
  - 用途：错误提示、删除操作
  - 含义：危险、停止

### 中性色
- **深色文字** `#303133` RGB(48, 49, 51)
- **常规文字** `#606266` RGB(96, 98, 102)
- **次要文字** `#909399` RGB(144, 147, 153)
- **占位文字** `#C0C4CC` RGB(192, 196, 204)
- **边框颜色** `#DCDFE6` RGB(220, 223, 230)
- **背景色** `#F5F7FA` RGB(245, 247, 250)

---

## 🖼️ 图标设计

### 核心元素
- **双向箭头**：代表消息转发的核心功能
- **圆形背景**：现代、友好的视觉语言
- **渐变色**：从蓝色到绿色，代表从KOOK到多个目标平台

### 设计原则
1. **简洁**：易于识别，在小尺寸下也清晰
2. **现代**：符合2025年的设计趋势
3. **专业**：传达可靠和专业的品牌形象
4. **识别度**：与其他应用区分明显

---

## 📏 Logo使用规范

### 尺寸要求
- 桌面图标：512x512、256x256、128x128
- Windows图标：32x32、16x16
- macOS图标：1024x1024、512x512
- 网页图标：64x64、32x32、16x16

### 安全区域
- 周围至少保留10%的空白区域
- 不要在图标上叠加其他元素

### 禁止事项
- ❌ 不要改变图标的颜色
- ❌ 不要拉伸或扭曲图标
- ❌ 不要在图标上添加阴影或特效
- ❌ 不要旋转图标

---

## 🔤 字体规范

### 中文字体
- **标题**：思源黑体 Bold
- **正文**：思源黑体 Regular
- **代码**：Source Code Pro / Consolas

### 英文字体
- **标题**：Roboto Bold
- **正文**：Roboto Regular
- **代码**：Fira Code / Monaco

---

## 🎭 UI组件规范

### 按钮
- **主要按钮**：蓝色背景 (#409EFF)，白色文字
- **次要按钮**：白色背景，蓝色边框和文字
- **成功按钮**：绿色背景 (#67C23A)
- **警告按钮**：橙色背景 (#E6A23C)
- **危险按钮**：红色背景 (#F56C6C)

### 圆角
- **卡片**：8px
- **按钮**：4px
- **输入框**：4px
- **对话框**：12px

### 阴影
- **hover效果**：0 2px 12px 0 rgba(0, 0, 0, 0.1)
- **卡片**：0 2px 4px 0 rgba(0, 0, 0, 0.12)

---

## 📱 应用截图规范

### 要求
- 分辨率：1920x1080 或更高
- 格式：PNG（支持透明）
- 展示内容：主要功能界面
- 配色：使用品牌色彩

### 建议截图
1. 主界面（概览页）
2. 账号管理页
3. Bot配置页
4. 频道映射页
5. 实时日志页

---

## ✍️ 文案规范

### 语气
- **友好**：使用口语化表达
- **专业**：避免过于随意
- **简洁**：言简意赅

### 术语
- 统一使用"KOOK"而不是"开黑啦"
- 统一使用"频道"而不是"Channel"
- 统一使用"机器人"或"Bot"

### 错误提示
- ❌ 不要："Error: NullPointerException"
- ✅ 应该："无法连接到服务器，请检查网络设置"

---

## 🌍 品牌标语

**主标语**：让消息跨越平台  
**副标语**：简单、快速、可靠的KOOK消息转发解决方案

---

**版本**: v4.1.0  
**更新日期**: 2025-10-25
"""
        
        guidelines_path = self.output_dir / "BRAND_GUIDELINES.md"
        guidelines_path.write_text(guidelines, encoding='utf-8')
        print(f"✅ 品牌指南已生成: {guidelines_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("🎨 KOOK消息转发系统 - 专业品牌资源生成器")
    print("=" * 60)
    
    generator = ProfessionalIconGenerator(output_dir="../frontend/public")
    
    # 生成所有图标
    generator.generate_all_sizes()
    
    # 生成SVG
    generator.generate_svg_icon()
    
    # 生成品牌指南
    generator.generate_brand_guidelines()
    
    print("\n" + "=" * 60)
    print("✅ 所有品牌资源已生成完成！")
    print("=" * 60)
    print("\n📁 输出目录: frontend/public/")
    print("\n下一步：")
    print("1. 查看生成的图标是否满意")
    print("2. 如需专业设计，请联系设计师进一步优化")
    print("3. 将图标应用到Electron配置中")
