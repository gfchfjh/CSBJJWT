import re

# Read file
with open('Layout.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Moon and Sunny icons
content = content.replace('  Fold\n} from', '  Fold,\n  Moon,\n  Sunny\n} from')

# 2. Import useTheme
content = content.replace("import axios from 'axios'", "import axios from 'axios'\nimport { useTheme } from '../composables/useTheme'")

# 3. Add theme variables
content = re.sub(
    r"(const route = useRoute\(\))",
    r"\1\n\n// Theme toggle\nconst { activeTheme, toggleTheme } = useTheme()\nconst isDark = computed(() => activeTheme.value === 'dark')",
    content
)

# 4. Add toggle method
content = re.sub(
    r"(const logout = \(\) => \{[^}]+\})",
    r"\1\n\n// Method: Toggle theme\nconst handleToggleTheme = () => {\n  toggleTheme()\n}",
    content
)

# 5. Add theme button
button = '''
          <!-- Theme Toggle -->
          <el-tooltip :content="isDark ? '切换到浅色' : '切换到深色'" placement="bottom">
            <el-button :icon="isDark ? Sunny : Moon" circle @click="handleToggleTheme" />
          </el-tooltip>'''

content = content.replace(
    '          </el-badge>\n          \n          <!-- User Menu -->',
    '          </el-badge>\n' + button + '\n          \n          <!-- User Menu -->'
)

# Write file
with open('Layout.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 主题切换按钮添加成功！')