#!/usr/bin/env python3
"""
简单图标生成脚本 - 不需要任何依赖
"""
import struct

def create_simple_png(filename, size=256):
    """创建一个简单的 PNG 图标"""
    # 这里创建一个简单的蓝色方块
    # 实际的 PNG 格式太复杂，让我们创建一个 SVG 然后说明
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{size}" height="{size}" fill="#4A90E2"/>
  <text x="50%" y="50%" font-family="Arial" font-size="120" 
        fill="white" text-anchor="middle" dominant-baseline="middle">K</text>
</svg>'''
    
    svg_filename = filename.replace('.png', '.svg')
    with open(svg_filename, 'w') as f:
        f.write(svg_content)
    print(f"✅ 创建了 SVG 图标: {svg_filename}")
    print("⚠️ 注意: 需要 Pillow 或 ImageMagick 将 SVG 转换为 PNG")

if __name__ == '__main__':
    create_simple_png('icon.png')
