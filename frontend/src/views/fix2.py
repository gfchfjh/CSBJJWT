# 读取文件
with open('Layout.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到需要修改的行号
import_line = -1
route_line = -1
logout_line = -1
badge_line = -1

for i, line in enumerate(lines):
    if "import axios from 'axios'" in line:
        import_line = i
    if 'const route = useRoute()' in line:
        route_line = i
    if 'const logout = () => {' in line:
        logout_line = i
    if '</el-badge>' in line and i + 2 < len(lines) and 'User Menu' in lines[i + 2]:
        badge_line = i

# 1. 添加图标导入
for i, line in enumerate(lines):
    if '  Fold' in line and '} from' in lines[i + 1]:
        lines[i] = '  Fold,\n'
        lines.insert(i + 1, '  Moon,\n')
        lines.insert(i + 2, '  Sunny\n')
        break

# 2. 添加 useTheme 导入
if import_line >= 0:
    lines.insert(import_line + 1, "import { useTheme } from '../composables/useTheme'\n")

# 3. 添加主题变量
if route_line >= 0:
    lines.insert(route_line + 1, '\n')
    lines.insert(route_line + 2, '// Theme toggle\n')
    lines.insert(route_line + 3, "const { activeTheme, toggleTheme } = useTheme()\n")
    lines.insert(route_line + 4, "const isDark = computed(() => activeTheme.value === 'dark')\n")

# 4. 添加切换方法
if logout_line >= 0:
    # 找到 logout 函数的结束位置
    for i in range(logout_line, len(lines)):
        if lines[i].strip() == '}':
            lines.insert(i + 1, '\n')
            lines.insert(i + 2, '// Method: Toggle theme\n')
            lines.insert(i + 3, 'const handleToggleTheme = () => {\n')
            lines.insert(i + 4, '  toggleTheme()\n')
            lines.insert(i + 5, '}\n')
            break

# 5. 添加主题切换按钮
if badge_line >= 0:
    lines.insert(badge_line + 1, '\n')
    lines.insert(badge_line + 2, '          <!-- Theme Toggle -->\n')
    lines.insert(badge_line + 3, '          <el-tooltip :content="isDark ? \'切换到浅色\' : \'切换到深色\'" placement="bottom">\n')
    lines.insert(badge_line + 4, '            <el-button :icon="isDark ? Sunny : Moon" circle @click="handleToggleTheme" />\n')
    lines.insert(badge_line + 5, '          </el-tooltip>\n')

# 写入文件
with open('Layout.vue', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ 修复完成！')