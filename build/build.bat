@echo off
REM KOOK消息转发系统 - Windows 构建脚本

echo ==================================
echo KOOK消息转发系统 - 构建脚本
echo ==================================

REM 检查Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误: 未找到python
    exit /b 1
)

REM 检查Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误: 未找到node
    exit /b 1
)

REM 运行统一构建脚本
python build\build_unified.py %*

echo.
echo ✅ 构建完成！
echo 📦 安装包位置: dist\v6.3.0\

pause
