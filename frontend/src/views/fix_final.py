import re

# 读取文件
with open('Layout.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复步骤1: 添加 Moon 和 Sunny 图标（在 Fold 后面）
content = re.sub(
    r'(\s+Fold\s*\n)(\s*\} from)',
    r'\1  Moon,\n  Sunny\n\2',
    content
)

# 修复步骤2: 添加 useTheme 导入（在 axios 导入后面）
content = re.sub(
    r"(import axios from 'axios'\s*\n)",
    r"\1import { useTheme } from '../composables/useTheme'\n",
    content
)

# 修复步骤3: 添加主题变量（在 route 定义后面）
content = re.sub(
    r"(const route = useRoute\(\)\s*\n)",
    r"\1\n// Theme toggle\nconst { activeTheme, toggleTheme } = useTheme()\nconst isDark = computed(() => activeTheme.value === 'dark')\n",
    content
)

# 修复步骤4: 添加主题切换按钮（在 </el-badge> 和 <!-- User Menu --> 之间）
button_html = '''
          <!-- Theme Toggle -->
          <el-tooltip :content="isDark ? '切换到浅色' : '切换到深色'" placement="bottom">
            <el-button :icon="isDark ? Sunny : Moon" circle @click="handleToggleTheme" />
          </el-tooltip>
'''

content = re.sub(
    r'(</el-badge>\s*\n\s*\n\s*<!-- User Menu -->)',
    r'</el-badge>\n' + button_html + '\n          <!-- User Menu -->',
    content
)

# 修复步骤5: 添加切换方法（在 logout 函数后面）
# 先找到 logout 函数的完整定义
logout_pattern = r"(const logout = \(\) => \{\s*if \(confirm\('确定要退出吗？'\)\) \{\s*localStorage\.clear\(\)\s*router\.push\('/login'\)\s*\}\s*\})"

toggle_method = '''

// Method: Toggle theme
const handleToggleTheme = () => {
  toggleTheme()
}'''

content = re.sub(logout_pattern, r'\1' + toggle_method, content)

# 写入文件
with open('Layout.vue', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print('✅ 修复完成！')
print('请刷新浏览器查看效果')