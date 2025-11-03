@echo off
chcp 65001 >nul
title 添加主题切换按钮

echo ========================================
echo     🎨 自动添加主题切换按钮
echo ========================================
echo.

cd /d "%~dp0frontend\src\views"

echo 【1/6】备份原文件...
copy Layout.vue Layout.vue.backup >nul
echo ✅ 已备份到 Layout.vue.backup

echo.
echo 【2/6】添加主题切换按钮...
powershell -Command "$content = Get-Content Layout.vue -Raw; $content = $content -replace '(<el-button :icon=\""Bell\"" circle @click=\""showNotifications\"" />\s*</el-badge>)', '$1`r`n          `r`n          <!-- 主题切换 -->`r`n          <el-tooltip :content=\"\"isDark ? ''切换到浅色'' : ''切换到深色''\"\" placement=\"\"bottom\"\">`r`n            <el-button :icon=\"\"isDark ? Sunny : Moon\"\" circle @click=\"\"handleToggleTheme\"\" />`r`n          </el-tooltip>'; Set-Content Layout.vue $content -NoNewline"

echo ✅ 主题切换按钮已添加

echo.
echo 【3/6】添加图标导入...
powershell -Command "$content = Get-Content Layout.vue -Raw; $content = $content -replace 'Fold\s*\n\} from', 'Fold,`r`n  Moon,`r`n  Sunny`r`n} from'; Set-Content Layout.vue $content -NoNewline"

echo ✅ 图标导入已添加

echo.
echo 【4/6】导入主题功能...
powershell -Command "$content = Get-Content Layout.vue -Raw; $content = $content -replace '(import axios from ''axios'')', '$1`r`nimport { useTheme } from ''../composables/useTheme'''; Set-Content Layout.vue $content -NoNewline"

echo ✅ 主题功能已导入

echo.
echo 【5/6】添加主题变量...
powershell -Command "$content = Get-Content Layout.vue -Raw; $content = $content -replace '(const router = useRouter\(\)\s*const route = useRoute\(\))', '$1`r`n`r`n// 主题切换`r`nconst { activeTheme, toggleTheme } = useTheme()`r`nconst isDark = computed(() => activeTheme.value === ''dark'')'; Set-Content Layout.vue $content -NoNewline"

echo ✅ 主题变量已添加

echo.
echo 【6/6】添加切换方法...
powershell -Command "$content = Get-Content Layout.vue -Raw; $content = $content -replace '(// 方法：退出\s*const logout[^}]+\})', '$1`r`n`r`n// 方法：切换主题`r`nconst handleToggleTheme = () => {`r`n  toggleTheme()`r`n}'; Set-Content Layout.vue $content -NoNewline"

echo ✅ 切换方法已添加

echo.
echo ========================================
echo     ✅ 主题切换按钮添加完成！
echo ========================================
echo.
echo 前端会自动刷新，请查看右上角是否有主题切换按钮
echo.
echo 如果出现问题，可以使用备份文件恢复：
echo     copy Layout.vue.backup Layout.vue
echo.
pause
