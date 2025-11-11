"""修复scraper.py的事件循环问题"""
import re

# 读取文件
with open('backend/app/kook/scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在with sync_playwright()之前添加事件循环策略设置
# 查找位置
if 'with sync_playwright() as p:' in content:
    # 找到这一行
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        if 'with sync_playwright() as p:' in line and 'Windows兼容性修复' not in '\n'.join(lines[max(0,i-5):i]):
            # 获取当前行的缩进
            indent = len(line) - len(line.lstrip())
            spaces = ' ' * indent
            
            # 在这一行之前添加修复代码
            new_lines.append(f'{spaces}# Windows兼容性修复：强制设置事件循环策略')
            new_lines.append(f'{spaces}import sys')
            new_lines.append(f'{spaces}if sys.platform == "win32":')
            new_lines.append(f'{spaces}    import asyncio')
            new_lines.append(f'{spaces}    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())' )
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # 保存文件
    with open('backend/app/kook/scraper.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 修复成功！")
    print("在 'with sync_playwright()' 之前添加了事件循环策略设置")
else:
    print("❌ 未找到 'with sync_playwright()'")
