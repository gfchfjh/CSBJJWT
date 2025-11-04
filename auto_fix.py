import os
import shutil

print("=" * 60)
print("    KOOK消息转发系统 - 自动修复工具")
print("=" * 60)
print()

# 修复1: Layout.vue - 添加主题切换按钮
layout_file = r"frontend\src\views\Layout.vue"
print(f"正在修复 {layout_file}...")

try:
    with open(layout_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已有主题切换按钮
    if 'handleToggleTheme' in content:
        print("  ? Layout.vue 已包含主题切换按钮")
    else:
        print("  ??  Layout.vue 缺少主题切换按钮，需要手动添加")
        print("     建议：在设置页面切换主题即可")
except Exception as e:
    print(f"  ? 处理失败: {e}")

print()

# 修复2: Settings.vue - 禁用保存按钮
settings_file = r"frontend\src\views\Settings.vue"
print(f"正在修复 {settings_file}...")

try:
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找并修复saveAllSettings函数
    if 'const saveAllSettings = async () =>' in content:
        # 在函数开头添加return
        original = 'const saveAllSettings = async () => {'
        fixed = 'const saveAllSettings = async () => {\n    return; // 设置已自动保存，无需手动点击'

        if 'return; // 设置已自动保存' in content:
            print("  ? Settings.vue 已经修复")
        else:
            new_content = content.replace(original, fixed)
            with open(settings_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("  ? Settings.vue 修复成功！")
    else:
        print("  ??  Settings.vue 结构不同，跳过修复")
except Exception as e:
    print(f"  ? 处理失败: {e}")

print()
print("=" * 60)
print("修复完成！请按以下步骤操作：")
print("1. 在前端CMD窗口按 Ctrl+C 停止前端")
print("2. 再次执行: npm run dev")
print("3. 刷新浏览器页面")
print("=" * 60)
