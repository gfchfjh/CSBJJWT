@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║   KOOK消息转发系统 - 自动构建脚本（修复版）               ║
echo ║   版本: v18.0.1-FIXED                                     ║
echo ║   日期: 2025-11-02                                        ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 本脚本将自动完成以下操作：
echo   1. 检查环境依赖
echo   2. 安装后端依赖
echo   3. 打包后端服务
echo   4. 安装前端依赖
echo   5. 构建前端应用
echo   6. 打包Electron应用
echo   7. 创建发布包
echo.
echo 预计耗时: 10-20分钟
echo.
pause

:: 设置错误处理
set "ERROR_OCCURRED=0"

:: ==========================================
:: 步骤1: 检查环境
:: ==========================================
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║ [1/7] 检查环境依赖                                         ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: 检查Python
echo 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] 未安装 Python
    echo.
    echo 请安装 Python 3.11 或更高版本:
    echo   下载地址: https://www.python.org/downloads/
    echo   安装时请勾选 "Add Python to PATH"
    echo.
    set "ERROR_OCCURRED=1"
    goto :error
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo [✓] Python %%i
)

:: 检查Node.js
echo 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [✗] 未安装 Node.js
    echo.
    echo 请安装 Node.js 18 或更高版本:
    echo   下载地址: https://nodejs.org/
    echo.
    set "ERROR_OCCURRED=1"
    goto :error
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do echo [✓] Node.js %%i
)

:: 检查npm
echo 检查 npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [✗] 未安装 npm
    set "ERROR_OCCURRED=1"
    goto :error
) else (
    for /f "tokens=1" %%i in ('npm --version 2^>^&1') do echo [✓] npm %%i
)

:: 检查Git
echo 检查 Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [?] 未安装 Git（可选）
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do echo [✓] Git %%i
)

echo.
echo 环境检查完成！
timeout /t 2 >nul

:: ==========================================
:: 步骤2: 安装后端依赖
:: ==========================================
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║ [2/7] 安装后端依赖                                         ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

cd backend
if errorlevel 1 (
    echo [✗] 未找到 backend 目录
    echo.
    echo 请确保在项目根目录运行此脚本！
    set "ERROR_OCCURRED=1"
    goto :error
)

:: 创建虚拟环境
if not exist venv (
    echo 创建Python虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [✗] 虚拟环境创建失败
        set "ERROR_OCCURRED=1"
        goto :error
    )
    echo [✓] 虚拟环境创建成功
) else (
    echo [✓] 虚拟环境已存在
)

:: 激活虚拟环境
call venv\Scripts\activate
if errorlevel 1 (
    echo [✗] 虚拟环境激活失败
    set "ERROR_OCCURRED=1"
    goto :error
)

:: 升级pip
echo 升级 pip...
python -m pip install --upgrade pip -q

:: 安装依赖
echo 安装依赖包（这可能需要几分钟）...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [✗] 依赖安装失败
    echo.
    echo 尝试使用国内镜像...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q
    if errorlevel 1 (
        echo [✗] 依赖安装仍然失败，请检查网络连接
        set "ERROR_OCCURRED=1"
        goto :error
    )
)
echo [✓] 依赖安装成功

:: 安装PyInstaller
echo 安装 PyInstaller...
pip install pyinstaller -q
if errorlevel 1 (
    echo [✗] PyInstaller 安装失败
    set "ERROR_OCCURRED=1"
    goto :error
)
echo [✓] PyInstaller 安装成功

cd ..

timeout /t 1 >nul

:: ==========================================
:: 步骤3: 打包后端
:: ==========================================
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║ [3/7] 打包后端服务                                         ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

cd build
if errorlevel 1 (
    echo [✗] 未找到 build 目录
    set "ERROR_OCCURRED=1"
    goto :error
)

:: 清理旧的构建
if exist dist (
    echo 清理旧的构建...
    rmdir /s /q dist 2>nul
)
if exist build (
    rmdir /s /q build 2>nul
)

:: 运行PyInstaller
echo 正在打包后端（这可能需要5-10分钟）...
echo 请耐心等待，不要关闭窗口...
echo.

pyinstaller pyinstaller.spec
if errorlevel 1 (
    echo [✗] 后端打包失败
    echo.
    echo 请检查错误信息并尝试以下操作：
    echo   1. 确保所有依赖已正确安装
    echo   2. 尝试删除 build 和 dist 目录后重新运行
    echo   3. 检查 pyinstaller.spec 文件是否正确
    echo.
    set "ERROR_OCCURRED=1"
    goto :error
)

:: 验证输出
if not exist "dist\KOOKForwarder\KOOKForwarder.exe" (
    echo [✗] 后端可执行文件未生成
    echo 期望位置: dist\KOOKForwarder\KOOKForwarder.exe
    set "ERROR_OCCURRED=1"
    goto :error
)

echo [✓] 后端打包成功
for %%f in (dist\KOOKForwarder\KOOKForwarder.exe) do echo     文件大小: %%~zf 字节
cd ..

timeout /t 1 >nul

:: ==========================================
:: 步骤4: 复制后端文件
:: ==========================================
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║ [4/7] 复制后端文件到前端资源目录                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: 创建目标目录
if not exist backend\dist (
    mkdir backend\dist
)

:: 复制文件
echo 复制后端文件...
xcopy /Y /E /I build\dist\KOOKForwarder backend\dist\KOOKForwarder >nul 2>&1
if errorlevel 1 (
    echo [✗] 文件复制失败
    set "ERROR_OCCURRED=1"
    goto :error
)

:: 验证
if exist "backend\dist\KOOKForwarder\KOOKForwarder.exe" (
    echo [✓] 后端文件复制成功
    echo     位置: backend\dist\KOOKForwarder\KOOKForwarder.exe
) else (
    echo [✗] 后端文件复制验证失败
    set "ERROR_OCCURRED=1"
    goto :error
)

timeout /t 1 >nul

:: ==========================================
:: 步骤5: 安装前端依赖
:: ==========================================
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║ [5/7] 安装前端依赖                                         ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

cd frontend
if errorlevel 1 (
    echo [✗] 未找到 frontend 目录
    set "ERROR_OCCURRED=1"
    goto :error
)

:: 检查node_modules
if exist node_modules (
    echo [✓] node_modules 已存在，跳过安装
) else (
    echo 安装依赖包（这可能需要几分钟）...
    call npm install
    if errorlevel 1 (
        echo [✗] 前端依赖安装失败
        echo.
        echo 尝试使用国内镜像...
        call npm install --registry=https://registry.npmmirror.com
        if errorlevel 1 (
            echo [✗] 依赖安装仍然失败
            set "ERROR_OCCURRED=1"
            goto :error
        )
    )
    echo [✓] 前端依赖安装成功
)

timeout /t 1 >nul

:: ==========================================
:: 步骤6: 构建前端
:: ==========================================
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║ [6/7] 构建前端应用                                         ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: 清理旧构建
if exist dist (
    echo 清理旧的前端构建...
    rmdir /s /q dist 2>nul
)

if exist dist-electron (
    echo 清理旧的Electron构建...
    rmdir /s /q dist-electron 2>nul
)

:: 构建Vue应用
echo 构建Vue应用...
call npm run build
if errorlevel 1 (
    echo [✗] 前端构建失败
    set "ERROR_OCCURRED=1"
    goto :error
)

:: 验证
if not exist dist\index.html (
    echo [✗] 前端构建验证失败（未找到 index.html）
    set "ERROR_OCCURRED=1"
    goto :error
)

echo [✓] 前端构建成功

timeout /t 1 >nul

:: ==========================================
:: 步骤7: 打包Electron应用
:: ==========================================
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║ [7/7] 打包Electron应用                                     ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo 打包Electron应用（这可能需要5-10分钟）...
echo 请耐心等待...
echo.

call npm run electron:build:win
if errorlevel 1 (
    echo [✗] Electron打包失败
    echo.
    echo 可能的原因：
    echo   1. 后端文件未正确复制
    echo   2. electron-builder配置问题
    echo   3. 磁盘空间不足
    echo.
    set "ERROR_OCCURRED=1"
    goto :error
)

:: 验证输出
if not exist "dist-electron\win-unpacked\KOOK消息转发系统.exe" (
    echo [✗] Electron打包验证失败
    echo 未找到: dist-electron\win-unpacked\KOOK消息转发系统.exe
    set "ERROR_OCCURRED=1"
    goto :error
)

echo [✓] Electron打包成功

:: 显示输出信息
echo.
echo 输出文件:
for /f %%f in ('dir /b dist-electron\*.exe 2^>nul') do (
    echo   [安装程序] dist-electron\%%f
    for %%s in (dist-electron\%%f) do echo              大小: %%~zs 字节
)
echo   [便携版] dist-electron\win-unpacked\KOOK消息转发系统.exe

cd ..

timeout /t 2 >nul

:: ==========================================
:: 构建成功
:: ==========================================
:success
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║   🎉 构建成功！                                           ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo ════════════════════════════════════════════════════════════
echo 输出位置:
echo ════════════════════════════════════════════════════════════
echo.
echo 📦 安装程序:
echo    frontend\dist-electron\KOOK消息转发系统 Setup 18.0.0.exe
echo.
echo 💼 便携版:
echo    frontend\dist-electron\win-unpacked\KOOK消息转发系统.exe
echo.
echo ════════════════════════════════════════════════════════════
echo 下一步操作:
echo ════════════════════════════════════════════════════════════
echo.
echo 1. 测试安装程序
echo    - 运行安装程序
echo    - 检查应用是否正常启动
echo    - 验证后端服务是否自动启动
echo.
echo 2. 测试便携版
echo    - 直接运行便携版exe
echo    - 验证所有功能
echo.
echo 3. 创建发布包
echo    - 压缩为ZIP文件
echo    - 添加README和安装说明
echo    - 上传到GitHub Release
echo.
echo ════════════════════════════════════════════════════════════
echo 修复说明:
echo ════════════════════════════════════════════════════════════
echo.
echo ✅ 修复了后端文件名不匹配问题
echo ✅ 统一使用 KOOKForwarder 作为后端文件名
echo ✅ 增强了依赖导入列表
echo ✅ 优化了打包配置
echo.
echo 此版本应该可以在 Windows 11 上正常运行！
echo.
echo ════════════════════════════════════════════════════════════
pause
exit /b 0

:: ==========================================
:: 错误处理
:: ==========================================
:error
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║   ❌ 构建失败                                             ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 请根据上面的错误信息进行排查。
echo.
echo 常见问题解决方案:
echo ════════════════════════════════════════════════════════════
echo.
echo 1. 依赖安装失败
echo    - 检查网络连接
echo    - 尝试使用国内镜像
echo    - 手动安装失败的包
echo.
echo 2. 打包失败
echo    - 删除 build\dist 和 build\build 目录
echo    - 重新运行脚本
echo    - 检查磁盘空间是否充足
echo.
echo 3. 权限问题
echo    - 以管理员身份运行脚本
echo    - 关闭杀毒软件
echo    - 添加项目目录到排除列表
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 如需帮助，请提供完整的错误信息。
echo.
pause
exit /b 1
