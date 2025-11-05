@echo off
chcp 65001 >nul
cls
echo ========================================
echo 🛡️ KOOK防封号使用指南
echo ========================================
echo.
if exist 防封号使用指南-重要必读.md (
    start notepad 防封号使用指南-重要必读.md
    echo ✅ 文档已打开，请仔细阅读！
    echo.
    echo ⚠️  重要提醒：
    echo    - 已应用最强反检测技术
    echo    - 但仍需严格遵守使用建议
    echo    - 务必使用测试账号
    echo    - 控制使用时间和频率
) else (
    echo ❌ 文档文件不存在！
    echo    请确保文件位于项目根目录
)
echo.
echo ========================================
pause
