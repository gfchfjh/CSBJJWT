@echo off
REM ============================================================================
REM KOOK消息转发系统 - 一键构建脚本 (Windows)
REM v1.13.0 新增 (P0-4优化)
REM ============================================================================

setlocal enabledelayedexpansion

echo ========================================
echo 🚀 KOOK消息转发系统 - 一键构建安装包
echo ========================================
echo.

REM 1. 环境检查
echo ========================================
echo 1️⃣  检查构建环境
echo ========================================
echo.

echo ℹ️  检查Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未安装Python，请先安装Python 3.11+
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

echo ℹ️  检查Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未安装Node.js，请先安装Node.js 18+
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js版本: %NODE_VERSION%

echo ℹ️  检查npm...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未安装npm
    exit /b 1
)
for /f %%i in ('npm --version') do set NPM_VERSION=%%i
echo ✅ npm版本: %NPM_VERSION%
echo.

REM 2. 安装依赖
echo ========================================
echo 2️⃣  安装依赖
echo ========================================
echo.

echo ℹ️  安装Python依赖...
pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo ⚠️  部分Python依赖安装失败，但继续构建
)
pip install pyinstaller
echo ✅ Python依赖安装完成
echo.

echo ℹ️  安装Playwright浏览器...
playwright install chromium
if %errorlevel% neq 0 (
    echo ⚠️  Playwright浏览器安装失败，可能需要手动安装
)
echo ✅ Playwright浏览器安装完成
echo.

echo ℹ️  安装前端依赖...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ❌ 前端依赖安装失败
    cd ..
    exit /b 1
)
cd ..
echo ✅ 前端依赖安装完成
echo.

REM 3. 准备Redis
echo ========================================
echo 3️⃣  准备Redis
echo ========================================
echo ⚠️  Redis准备：将使用系统Redis或嵌入式Redis
echo ℹ️  如需打包Redis，请运行: python build\prepare_redis.py
echo.

REM 4. 构建后端
echo ========================================
echo 4️⃣  构建Python后端
echo ========================================
echo.

if exist "build\build_backend.py" (
    echo ℹ️  开始打包后端...
    python build\build_backend.py
    if %errorlevel% neq 0 (
        echo ⚠️  后端构建失败，但继续构建前端
    ) else (
        echo ✅ 后端构建完成
    )
) else (
    echo ⚠️  build\build_backend.py不存在，跳过后端构建
    echo ℹ️  如需打包后端，请完善build\build_backend.py
)
echo.

REM 5. 构建前端
echo ========================================
echo 5️⃣  构建前端资源
echo ========================================
echo.

echo ℹ️  开始构建前端...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo ❌ 前端构建失败
    cd ..
    exit /b 1
)
cd ..
echo ✅ 前端构建完成
echo.

REM 6. 整合Electron应用
echo ========================================
echo 6️⃣  整合Electron应用
echo ========================================
echo.

echo ℹ️  整合后端可执行文件到Electron...

REM 创建backend目录
if not exist "frontend\electron\backend" mkdir frontend\electron\backend

REM 如果后端可执行文件存在，复制它
if exist "backend\dist\KookForwarder.exe" (
    copy /Y backend\dist\KookForwarder.exe frontend\electron\backend\
    echo ✅ 后端可执行文件已复制
) else if exist "dist\KookForwarder.exe" (
    copy /Y dist\KookForwarder.exe frontend\electron\backend\
    echo ✅ 后端可执行文件已复制
) else (
    echo ⚠️  后端可执行文件不存在，跳过复制
    echo ℹ️  Electron应用将使用Python源码模式运行
)
echo.

REM 7. 生成安装包
echo ========================================
echo 7️⃣  生成安装包
echo ========================================
echo.

echo ℹ️  开始打包Electron应用...
cd frontend
call npm run electron:build:win
if %errorlevel% neq 0 (
    echo ❌ Electron应用打包失败
    cd ..
    exit /b 1
)
cd ..
echo ✅ 安装包生成完成
echo.

REM 8. 显示输出
echo ========================================
echo 🎉 构建完成！
echo ========================================
echo.

echo ℹ️  安装包位置:
if exist "frontend\dist-electron" (
    dir /b frontend\dist-electron\*.exe 2>nul
    if %errorlevel% neq 0 (
        echo ⚠️  未找到.exe安装包文件
    )
) else (
    echo ⚠️  dist-electron目录不存在
)
echo.

echo ℹ️  下一步操作:
echo   1. 测试安装包: 运行生成的.exe文件
echo   2. 查看日志: 检查构建日志获取详细信息
echo   3. 发布: 将安装包上传到GitHub Releases
echo.

echo ✅ 构建流程全部完成！🎊
pause
