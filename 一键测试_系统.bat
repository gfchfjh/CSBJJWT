@echo off
chcp 65001 >nul
title KOOK转发系统 - 系统测试
color 0E

echo ========================================
echo   KOOK消息转发系统 - 系统测试脚本
echo   版本: v18.0.4+
echo ========================================
echo.

cd /d "%~dp0"

echo [测试开始] %date% %time%
echo.

REM 测试1: Python环境
echo [测试1/8] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python已安装:
    python --version
) else (
    echo ❌ Python未安装
)
echo.

REM 测试2: Node.js环境
echo [测试2/8] 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js已安装:
    node --version
) else (
    echo ❌ Node.js未安装
)
echo.

REM 测试3: Git环境
echo [测试3/8] 检查Git环境...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git已安装:
    git --version
) else (
    echo ❌ Git未安装
)
echo.

REM 测试4: 虚拟环境
echo [测试4/8] 检查虚拟环境...
if exist "venv\Scripts\activate.bat" (
    echo ✅ 虚拟环境存在
) else (
    echo ❌ 虚拟环境不存在
)
echo.

REM 测试5: 后端代码
echo [测试5/8] 检查后端代码...
if exist "backend\app\main.py" (
    echo ✅ 后端代码存在
    dir backend\app\main.py | findstr /C:"main.py"
) else (
    echo ❌ 后端代码不存在
)
echo.

REM 测试6: 前端代码
echo [测试6/8] 检查前端代码...
if exist "frontend\package.json" (
    echo ✅ 前端代码存在
    dir frontend\package.json | findstr /C:"package.json"
) else (
    echo ❌ 前端代码不存在
)
echo.

REM 测试7: 数据目录
echo [测试7/8] 检查数据目录...
if exist "%USERPROFILE%\Documents\KookForwarder\data" (
    echo ✅ 数据目录存在
    echo 路径: %USERPROFILE%\Documents\KookForwarder\data
) else (
    echo ⚠️  数据目录不存在（首次运行会自动创建）
)
echo.

REM 测试8: 数据库文件
echo [测试8/8] 检查数据库文件...
if exist "%USERPROFILE%\Documents\KookForwarder\data\config.db" (
    echo ✅ 数据库文件存在
    dir "%USERPROFILE%\Documents\KookForwarder\data\config.db" | findstr /C:"config.db"
) else (
    echo ⚠️  数据库文件不存在（首次运行会自动创建）
)
echo.

echo ========================================
echo   测试完成！
echo ========================================
echo.

REM 生成测试报告
echo [测试总结]
echo 时间: %date% %time%
echo.

REM 检查是否可以启动
if exist "venv\Scripts\activate.bat" (
    if exist "backend\app\main.py" (
        if exist "frontend\package.json" (
            echo ✅✅✅ 系统环境完整，可以正常启动！
            echo.
            echo [下一步]
            echo 1. 运行 "快速启动_后端.bat" 启动后端
            echo 2. 运行 "快速启动_前端.bat" 启动前端
            echo 3. 浏览器访问 http://localhost:5173
        )
    )
) else (
    echo ❌ 环境不完整，请先运行 install.bat 安装
)

echo.
echo [详细文档] 请查看 CMD_操作指南_完整版.md
echo.
pause
