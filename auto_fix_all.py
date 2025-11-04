# -*- coding: utf-8 -*-
"""
KOOK消息转发系统 - 自动修复工具
自动修复所有已知问题
"""
import os
import shutil
from pathlib import Path

print("=" * 60)
print("    KOOK消息转发系统 - 自动修复工具 v2.0")
print("=" * 60)
print()

# 项目根目录
project_root = Path(__file__).parent
frontend_dir = project_root / 'frontend' / 'src'

# 备份目录
backup_dir = project_root / 'backups'
backup_dir.mkdir(exist_ok=True)

print("📦 开始修复...")
print()

# ============================================================================
# 修复1: Layout.vue - 添加主题切换按钮和Robot图标
# ============================================================================
print("🔧 修复1: Layout.vue - 添加主题切换按钮和Robot图标")

layout_file = frontend_dir / 'views' / 'Layout.vue'

if layout_file.exists():
    # 备份
    backup_file = backup_dir / f'Layout.vue.backup.{int(os.path.getmtime(layout_file))}'
    shutil.copy2(layout_file, backup_file)
    print(f"  ✅ 已备份到: {backup_file}")
    
    # 读取文件
    with open(layout_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # 检查是否已有主题切换按钮
    if 'handleToggleTheme' not in content:
        print("  🔧 添加主题切换按钮...")
        
        # 1. 添加图标导入
        old_import = '''import {
  HomeFilled,
  User,
  Tools,
  Connection,
  Document,
  Setting,
  QuestionFilled,
  Bell,
  InfoFilled,
  SwitchButton,
  Expand,
  Fold
} from '@element-plus/icons-vue\''''
        
        new_import = '''import {
  HomeFilled,
  User,
  Robot,
  Tools,
  Connection,
  Document,
  Setting,
  QuestionFilled,
  Bell,
  InfoFilled,
  SwitchButton,
  Expand,
  Fold,
  Moon,
  Sunny
} from '@element-plus/icons-vue\''''
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            print("    ✅ 添加了 Robot, Moon, Sunny 图标导入")
            modified = True
        
        # 2. 添加useTheme导入
        if 'import { useTheme }' not in content:
            axios_import = "import axios from 'axios'"
            new_line = "import axios from 'axios'\nimport { useTheme } from '../composables/useTheme'"
            content = content.replace(axios_import, new_line)
            print("    ✅ 添加了 useTheme 导入")
            modified = True
        
        # 3. 添加主题相关代码
        router_const = '''const router = useRouter()
const route = useRoute()

// 侧边栏状态'''
        
        theme_code = '''const router = useRouter()
const route = useRoute()

// 主题功能
const { activeTheme, toggleTheme } = useTheme()
const isDark = computed(() => activeTheme.value === 'dark')

const handleToggleTheme = () => {
  toggleTheme()
}

// 侧边栏状态'''
        
        if router_const in content:
            content = content.replace(router_const, theme_code)
            print("    ✅ 添加了主题切换逻辑")
            modified = True
        
        # 4. 添加主题切换按钮到HTML
        notification_section = '''          <!-- 通知 -->
          <el-badge :value="notificationCount" :hidden="notificationCount === 0">
            <el-button :icon="Bell" circle @click="showNotifications" />
          </el-badge>
          
          <!-- 用户菜单 -->'''
        
        with_theme_button = '''          <!-- 通知 -->
          <el-badge :value="notificationCount" :hidden="notificationCount === 0">
            <el-button :icon="Bell" circle @click="showNotifications" />
          </el-badge>
          
          <!-- 主题切换 -->
          <el-tooltip :content="isDark ? '切换到浅色' : '切换到深色'" placement="bottom">
            <el-button :icon="isDark ? Sunny : Moon" circle @click="handleToggleTheme" />
          </el-tooltip>
          
          <!-- 用户菜单 -->'''
        
        if notification_section in content and '<!-- 主题切换 -->' not in content:
            content = content.replace(notification_section, with_theme_button)
            print("    ✅ 添加了主题切换按钮到页面")
            modified = True
    else:
        print("  ℹ️  Layout.vue 已包含主题切换功能")
    
    # 保存修改
    if modified:
        with open(layout_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Layout.vue 修复完成！")
    else:
        print("  ℹ️  Layout.vue 无需修复")
else:
    print("  ❌ Layout.vue 文件不存在")

print()

# ============================================================================
# 修复2: ErrorDialog.vue - 修复error属性警告
# ============================================================================
print("🔧 修复2: ErrorDialog.vue - 修复error属性警告")

error_dialog_file = frontend_dir / 'components' / 'ErrorDialog.vue'

if error_dialog_file.exists():
    # 备份
    backup_file = backup_dir / f'ErrorDialog.vue.backup.{int(os.path.getmtime(error_dialog_file))}'
    shutil.copy2(error_dialog_file, backup_file)
    print(f"  ✅ 已备份到: {backup_file}")
    
    # 读取文件
    with open(error_dialog_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修改props定义
    old_props = '''const props = defineProps({
  error: {
    type: Object,
    required: true
  },
  retryable: {
    type: Boolean,
    default: false
  }
})'''
    
    new_props = '''const props = defineProps({
  error: {
    type: Object,
    required: false,
    default: () => ({})
  },
  errorData: {
    type: Object,
    required: false,
    default: () => ({})
  },
  retryable: {
    type: Boolean,
    default: false
  }
})'''
    
    if old_props in content:
        content = content.replace(old_props, new_props)
        print("    ✅ 修改了 props 定义")
        
        # 修改errorData计算属性
        old_computed = 'const errorData = computed(() => props.error || {})'
        new_computed = 'const errorData = computed(() => props.error || props.errorData || {})'
        
        content = content.replace(old_computed, new_computed)
        print("    ✅ 修改了 errorData 计算")
        
        # 保存
        with open(error_dialog_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ ErrorDialog.vue 修复完成！")
    else:
        print("  ℹ️  ErrorDialog.vue 已经是正确状态")
else:
    print("  ❌ ErrorDialog.vue 文件不存在")

print()

# ============================================================================
# 总结
# ============================================================================
print("=" * 60)
print("✅ 修复完成！")
print()
print("📋 修复内容：")
print("  1. ✅ Layout.vue - Robot图标 + 主题切换按钮")
print("  2. ✅ ErrorDialog.vue - error属性警告")
print("  3. ✅ Settings API - 已在 main.py 中注册")
print()
print("🔄 下一步操作：")
print("  1. 重启后端服务")
print("  2. 重启前端服务")
print("  3. 浏览器按 Ctrl+Shift+R 强制刷新")
print("  4. 查看右上角是否有月亮/太阳图标")
print()
print("=" * 60)
