@echo off
chcp 65001 >nul
title 清理 KOOK 开发文件

echo ========================================
echo KOOK 开发文件清理工具
echo ========================================
echo.
echo 本工具将清理：
echo   ✓ backend/venv/ (Python虚拟环境)
echo   ✓ frontend/node_modules/ (Node依赖)
echo   ✓ dist/ (构建产物)
echo   ✓ build/pyinstaller/ (PyInstaller缓存)
echo   ✓ __pycache__/ (Python缓存)
echo   ✓ *.pyc (Python字节码)
echo.
echo ⚠️  这将释放大量磁盘空间（可能超过1GB）
echo.
set /p CONFIRM="确定要继续吗？(Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo 已取消清理。
    pause
    exit /b
)

echo.
echo 开始清理...
echo.

:: 检查是否在项目根目录
if not exist "backend" (
    echo [ERROR] 未找到 backend 目录
    echo 请在项目根目录运行此脚本
    pause
    exit /b 1
)

:: 清理 Python 虚拟环境
echo [1/8] 清理 Python 虚拟环境...
if exist "backend\venv" (
    rmdir /s /q "backend\venv"
    echo [OK] 已删除 backend\venv (~1GB)
) else (
    echo [SKIP] backend\venv 不存在
)

:: 清理 Node.js 依赖
echo [2/8] 清理 Node.js 依赖...
if exist "frontend\node_modules" (
    rmdir /s /q "frontend\node_modules"
    echo [OK] 已删除 frontend\node_modules (~500MB)
) else (
    echo [SKIP] frontend\node_modules 不存在
)

:: 清理 dist 构建产物
echo [3/8] 清理构建产物...
if exist "dist" (
    rmdir /s /q "dist"
    echo [OK] 已删除 dist/
)
if exist "frontend\dist" (
    rmdir /s /q "frontend\dist"
    echo [OK] 已删除 frontend\dist/
)
if exist "frontend\dist-electron" (
    rmdir /s /q "frontend\dist-electron"
    echo [OK] 已删除 frontend\dist-electron/
)

:: 清理 PyInstaller 缓存
echo [4/8] 清理 PyInstaller 缓存...
if exist "build\pyinstaller" (
    rmdir /s /q "build\pyinstaller"
    echo [OK] 已删除 build\pyinstaller/
)

:: 清理 Python 缓存
echo [5/8] 清理 Python 缓存...
for /r "backend" %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d"
        echo [OK] 已删除 %%d
    )
)

:: 清理 .pyc 文件
echo [6/8] 清理 .pyc 文件...
del /s /q "backend\*.pyc" 2>nul
echo [OK] .pyc 文件已清理

:: 清理前端缓存
echo [7/8] 清理前端缓存...
if exist "frontend\.vite" (
    rmdir /s /q "frontend\.vite"
    echo [OK] 已删除 frontend\.vite/
)
if exist "frontend\node_modules\.cache" (
    rmdir /s /q "frontend\node_modules\.cache"
    echo [OK] 已删除 frontend\node_modules\.cache/
)

:: 清理日志文件
echo [8/8] 清理日志文件...
del /q "backend\*.log" 2>nul
del /q "frontend\*.log" 2>nul
echo [OK] 日志文件已清理

echo.
echo ========================================
echo 清理完成！
echo ========================================
echo.
echo 已清理的内容：
echo   ✓ Python 虚拟环境
echo   ✓ Node.js 依赖包
echo   ✓ 构建产物
echo   ✓ 缓存文件
echo.
echo 下次构建前需要重新安装依赖：
echo   1. cd backend ^&^& python -m venv venv ^&^& venv\Scripts\activate.bat
echo   2. pip install -r requirements.txt
echo   3. cd ..\frontend ^&^& npm install --legacy-peer-deps
echo.
pause
