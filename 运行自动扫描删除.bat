@echo off
:: 自动以管理员权限运行自动扫描删除脚本

:: 检查是否是管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在请求管理员权限...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: 已经是管理员权限，运行主脚本
cd /d "%~dp0"

if exist "自动扫描删除KOOK.bat" (
    echo 正在启动自动扫描删除工具...
    call "自动扫描删除KOOK.bat"
) else (
    echo.
    echo [错误] 未找到 自动扫描删除KOOK.bat
    echo.
    echo 请确保以下文件在同一目录：
    echo   • 运行自动扫描删除.bat （本文件）
    echo   • 自动扫描删除KOOK.bat
    echo.
    pause
)
