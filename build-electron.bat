@echo off
REM KOOK消息转发系统 - Electron应用构建脚本 (Windows)
REM 用法: build-electron.bat [win|mac|linux]

echo ========================================================
echo KOOK消息转发系统 - Electron应用构建
echo ========================================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

REM 运行构建脚本
python scripts\build_electron_app.py %*

if errorlevel 1 (
    echo.
    echo [错误] 构建失败，请查看上方错误信息
    pause
    exit /b 1
)

echo.
echo [成功] Electron应用构建完成！
echo.
echo 构建产物位于: frontend\dist-electron\
echo.
pause
