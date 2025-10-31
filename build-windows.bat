@echo off
REM KOOK消息转发系统 - Windows构建脚本
REM 版本: v18.0.0

echo ================================================
echo KOOK消息转发系统 - Windows构建脚本
echo 版本: v18.0.0
echo ================================================
echo.

REM 颜色设置
setlocal enabledelayedexpansion

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 建议以管理员权限运行此脚本
    echo.
)

REM 检查Python
echo [步骤1/6] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python未安装！请安装Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    exit /b 1
)
python --version
echo.

REM 检查Node.js
echo [步骤2/6] 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Node.js未安装！请安装Node.js 20+
    echo 下载地址: https://nodejs.org/
    exit /b 1
)
node --version
npm --version
echo.

REM 安装前端依赖
echo [步骤3/6] 安装前端依赖...
cd frontend
if %errorlevel% neq 0 (
    echo [错误] frontend目录不存在！
    exit /b 1
)

echo 执行: npm install --legacy-peer-deps
call npm install --legacy-peer-deps
if %errorlevel% neq 0 (
    echo [错误] 前端依赖安装失败！
    exit /b 1
)
cd ..
echo [成功] 前端依赖安装完成
echo.

REM 安装后端依赖
echo [步骤4/6] 安装后端依赖...
cd backend
if %errorlevel% neq 0 (
    echo [错误] backend目录不存在！
    exit /b 1
)

echo 执行: pip install -r requirements.txt
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [错误] 后端依赖安装失败！
    exit /b 1
)

echo 执行: pip install pyinstaller
pip install pyinstaller
if %errorlevel% neq 0 (
    echo [错误] PyInstaller安装失败！
    exit /b 1
)
cd ..
echo [成功] 后端依赖安装完成
echo.

REM 构建前端
echo [步骤5/6] 构建前端应用...
cd frontend

echo 执行: npm run build
call npm run build
if %errorlevel% neq 0 (
    echo [错误] 前端构建失败！
    exit /b 1
)
echo [成功] 前端构建完成
echo.

echo 执行: npm run electron:build:win
call npm run electron:build:win
if %errorlevel% neq 0 (
    echo [错误] Electron打包失败！
    exit /b 1
)
echo [成功] Electron打包完成
cd ..
echo.

REM 构建后端
echo [步骤6/6] 构建后端服务...
cd backend

echo 执行: pyinstaller ../build/pyinstaller.spec
pyinstaller ..\build\pyinstaller.spec
if %errorlevel% neq 0 (
    echo [错误] 后端打包失败！
    exit /b 1
)
echo [成功] 后端打包完成
cd ..
echo.

REM 创建发布目录
echo ================================================
echo 创建发布包...
echo ================================================
echo.

set RELEASE_DIR=dist\KOOK-Forwarder-v18.0.0-Windows
if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%\frontend"
mkdir "%RELEASE_DIR%\backend"
mkdir "%RELEASE_DIR%\docs"

REM 复制文件
echo 复制Electron安装包...
xcopy /Y /I frontend\dist-electron\*.exe "%RELEASE_DIR%\frontend\" 2>nul
xcopy /Y /I frontend\dist-electron\win-unpacked "%RELEASE_DIR%\frontend\win-unpacked\" /E 2>nul

echo 复制Python后端...
xcopy /Y /I backend\dist\kook-forwarder-backend "%RELEASE_DIR%\backend\kook-forwarder-backend\" /E

echo 复制文档...
copy /Y README.md "%RELEASE_DIR%\" >nul 2>&1
copy /Y BUILD_SUCCESS_REPORT.md "%RELEASE_DIR%\" >nul 2>&1
copy /Y SYSTEM_COMPLETION_REPORT.md "%RELEASE_DIR%\docs\" >nul 2>&1

REM 创建安装说明
echo 创建安装说明...
(
echo KOOK消息转发系统 v18.0.0 - Windows安装指南
echo.
echo 快速开始:
echo 1. 解压此文件夹到任意位置
echo 2. 进入 frontend 目录
echo 3. 双击运行 KOOK消息转发系统 Setup.exe 安装
echo    或直接运行 win-unpacked\KOOK消息转发系统.exe
echo.
echo 系统要求:
echo - Windows 10/11 ^(64位^)
echo - 4 GB RAM
echo - 1 GB 磁盘空间
echo.
echo 遇到问题?
echo - 查看 README.md
echo - 访问 https://github.com/gfchfjh/CSBJJWT/issues
) > "%RELEASE_DIR%\安装说明.txt"

REM 创建ZIP压缩包
echo 创建ZIP压缩包...
cd dist
if exist "KOOK-Forwarder-v18.0.0-Windows.zip" del /f "KOOK-Forwarder-v18.0.0-Windows.zip"

REM 使用PowerShell创建ZIP
powershell -Command "Compress-Archive -Path 'KOOK-Forwarder-v18.0.0-Windows' -DestinationPath 'KOOK-Forwarder-v18.0.0-Windows.zip' -CompressionLevel Optimal"
if %errorlevel% neq 0 (
    echo [警告] ZIP创建失败，请手动压缩 dist\KOOK-Forwarder-v18.0.0-Windows 目录
) else (
    echo [成功] ZIP压缩包创建完成
)

REM 生成MD5校验
echo 生成MD5校验...
certutil -hashfile "KOOK-Forwarder-v18.0.0-Windows.zip" MD5 > "KOOK-Forwarder-v18.0.0-Windows.zip.md5"

cd ..

echo.
echo ================================================
echo 构建完成！
echo ================================================
echo.
echo 生成的文件:
dir /b dist\KOOK-Forwarder-v18.0.0-Windows.zip 2>nul
dir /b dist\KOOK-Forwarder-v18.0.0-Windows.zip.md5 2>nul
echo.
echo 安装包位置: dist\KOOK-Forwarder-v18.0.0-Windows\frontend\
echo.
echo 按任意键退出...
pause >nul
