@echo off
chcp 65001 >nul
title 环境测试

echo.
echo ═══════════════════════════════════════
echo   KOOK 环境检测
echo ═══════════════════════════════════════
echo.

echo [1/3] 检查 Python...
python --version
if errorlevel 1 (
    echo [✗] Python 检测失败
    goto :error
) else (
    echo [✓] Python 正常
)

echo.
echo [2/3] 检查 Node.js...
node --version
if errorlevel 1 (
    echo [✗] Node.js 检测失败
    goto :error
) else (
    echo [✓] Node.js 正常
)

echo.
echo [3/3] 检查 npm...
npm --version
if errorlevel 1 (
    echo [✗] npm 检测失败
    goto :error
) else (
    echo [✓] npm 正常
)

echo.
echo ═══════════════════════════════════════
echo.
color 0A
echo ✅✅✅ 所有环境检查通过！✅✅✅
echo.
echo 🎉 您可以运行一键安装脚本了！
echo.
echo ═══════════════════════════════════════
pause
exit /b 0

:error
echo.
color 0C
echo ═══════════════════════════════════════
echo [✗] 环境检查失败
echo ═══════════════════════════════════════
pause
exit /b 1
