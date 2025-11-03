@echo off
chcp 65001 >nul
title KOOK Electron 调试工具
color 0E

:menu
cls
echo.
echo ================================================================
echo            KOOK Electron 调试工具
echo ================================================================
echo.
echo 请选择调试功能：
echo.
echo [1] 分步启动模式（后端→前端分开启动）
echo [2] 检查后端独立运行
echo [3] 查看 Electron 日志
echo [4] 检查端口占用情况
echo [5] 收集完整诊断信息
echo [6] 手动启动后端+Web访问
echo [7] 恢复备份文件
echo [8] 清理并重新构建
echo [0] 退出
echo.
echo ================================================================
echo.

set /p choice="请输入选项 (0-8): "

if "%choice%"=="1" goto step_start
if "%choice%"=="2" goto test_backend
if "%choice%"=="3" goto show_logs
if "%choice%"=="4" goto check_ports
if "%choice%"=="5" goto collect_info
if "%choice%"=="6" goto web_mode
if "%choice%"=="7" goto restore_backup
if "%choice%"=="8" goto clean_rebuild
if "%choice%"=="0" exit /b 0

echo 无效选项，请重新选择
timeout /t 2 >nul
goto menu

:: ================================================================
:: [1] 分步启动模式
:: ================================================================
:step_start
cls
echo.
echo ================================================================
echo 分步启动模式
echo ================================================================
echo.
echo 此模式将分三步启动系统，便于观察问题：
echo   1. 独立启动后端
echo   2. 验证后端可访问
echo   3. 启动 Electron 前端
echo.
pause

:: 检查安装目录
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\kook-forwarder-frontend"
if not exist "%INSTALL_DIR%" (
    echo [错误] 未找到 Electron 安装目录
    echo 请先安装 Electron 版本
    pause
    goto menu
)

echo.
echo [步骤 1/3] 启动后端服务...
echo.
cd "%INSTALL_DIR%\resources\backend\KOOKForwarder"
start "KOOK-Backend" cmd /k "echo 后端服务窗口 - 请勿关闭 && echo. && KOOKForwarder.exe"

echo [等待] 给后端 60 秒时间启动...
echo （您可以在后端窗口中观察启动过程）
echo.
timeout /t 60 /nobreak

echo.
echo [步骤 2/3] 验证后端是否就绪...
echo.

:: 检查端口
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo ✅ 端口 8000 正在监听
) else (
    echo ❌ 端口 8000 未监听
    echo 请检查后端窗口是否有错误
    pause
    goto menu
)

:: 测试 API
echo.
echo 测试 API 连接...
curl -s http://127.0.0.1:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API 响应正常
) else (
    echo ⚠️ API 未响应，但会继续尝试启动
)

echo.
echo [步骤 3/3] 启动 Electron 前端...
echo.
cd "%INSTALL_DIR%"
start "" "KOOK消息转发系统.exe"

echo.
echo ================================================================
echo 启动完成！
echo ================================================================
echo.
echo 观察要点：
echo   1. 后端窗口是否有错误日志
echo   2. Electron 是否显示 "fetch failed"
echo   3. 是否能看到登录页面
echo.
echo 提示：
echo   - 后端窗口保持打开
echo   - 如果失败，查看后端窗口的错误信息
echo.
pause
goto menu

:: ================================================================
:: [2] 检查后端独立运行
:: ================================================================
:test_backend
cls
echo.
echo ================================================================
echo 测试后端独立运行
echo ================================================================
echo.

if exist "dist\KOOKForwarder\KOOKForwarder.exe" (
    echo [测试] 使用项目构建的后端
    cd dist\KOOKForwarder
    echo.
    echo 启动后端（30秒测试）...
    echo 请观察输出信息
    echo.
    timeout /t 3 >nul
    
    start /WAIT /B cmd /c "KOOKForwarder.exe & timeout /t 30 /nobreak"
    
    echo.
    echo 测试完成
    cd ..\..
) else if exist "%LOCALAPPDATA%\Programs\kook-forwarder-frontend\resources\backend\KOOKForwarder\KOOKForwarder.exe" (
    echo [测试] 使用已安装的后端
    cd "%LOCALAPPDATA%\Programs\kook-forwarder-frontend\resources\backend\KOOKForwarder"
    echo.
    echo 启动后端（按 Ctrl+C 停止）...
    echo.
    timeout /t 3 >nul
    
    KOOKForwarder.exe
    
    cd "%~dp0"
) else (
    echo [错误] 未找到后端可执行文件
    echo.
    echo 请先运行以下之一：
    echo   1. 自动修复Electron.bat（重新构建）
    echo   2. pyinstaller build\pyinstaller.spec
)

echo.
pause
goto menu

:: ================================================================
:: [3] 查看 Electron 日志
:: ================================================================
:show_logs
cls
echo.
echo ================================================================
echo Electron 日志
echo ================================================================
echo.

set "LOG_DIR=%APPDATA%\KOOK消息转发系统\logs"
if exist "%LOG_DIR%\main.log" (
    echo 日志文件位置：
    echo %LOG_DIR%\main.log
    echo.
    echo ----------------------------------------------------------------
    type "%LOG_DIR%\main.log"
    echo ----------------------------------------------------------------
    echo.
    echo 完整日志已显示
) else (
    echo [信息] 未找到 Electron 日志文件
    echo 可能的原因：
    echo   1. Electron 从未启动过
    echo   2. 日志文件在其他位置
    echo.
    echo 尝试查找日志...
    dir /s /b "%APPDATA%\*.log" 2>nul | findstr /I "kook"
)

echo.
pause
goto menu

:: ================================================================
:: [4] 检查端口占用
:: ================================================================
:check_ports
cls
echo.
echo ================================================================
echo 检查端口占用情况
echo ================================================================
echo.

echo [检查] 端口 8000（后端）
netstat -ano | findstr :8000
if %errorlevel% equ 0 (
    echo ✅ 端口 8000 正在使用
) else (
    echo ❌ 端口 8000 空闲
)

echo.
echo [检查] 端口 9527（可选的API端口）
netstat -ano | findstr :9527
if %errorlevel% equ 0 (
    echo ✅ 端口 9527 正在使用
) else (
    echo ❌ 端口 9527 空闲
)

echo.
echo [检查] 所有 KOOK 相关进程
tasklist | findstr /I "kook electron python KOOKForwarder"

echo.
echo ================================================================
echo.
echo 如果端口被占用但应用无法访问：
echo   1. 结束占用端口的进程
echo   2. 或重启电脑
echo.
pause
goto menu

:: ================================================================
:: [5] 收集诊断信息
:: ================================================================
:collect_info
cls
echo.
echo ================================================================
echo 收集完整诊断信息
echo ================================================================
echo.

set "INFO_FILE=诊断信息_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%.txt"
set "INFO_FILE=%INFO_FILE: =0%"

echo 正在收集信息...
echo.

(
echo ================================================================
echo KOOK 系统诊断信息
echo 生成时间: %date% %time%
echo ================================================================
echo.
echo [1] 系统信息
echo ----------------------------------------------------------------
systeminfo | findstr /C:"OS Name" /C:"OS Version" /C:"System Type"
echo.
echo [2] 软件版本
echo ----------------------------------------------------------------
python --version 2^>^&1
node --version 2^>^&1
npm --version 2^>^&1
git --version 2^>^&1
echo.
echo [3] 端口占用
echo ----------------------------------------------------------------
netstat -ano ^| findstr ":8000 :9527"
echo.
echo [4] 相关进程
echo ----------------------------------------------------------------
tasklist ^| findstr /I "kook electron python"
echo.
echo [5] 项目文件
echo ----------------------------------------------------------------
if exist "backend\app\main.py" echo ✅ backend\app\main.py
if exist "backend\run_minimal.py" echo ✅ backend\run_minimal.py
if exist "frontend\electron\main.js" echo ✅ frontend\electron\main.js
if exist "dist\KOOKForwarder\KOOKForwarder.exe" echo ✅ dist\KOOKForwarder\KOOKForwarder.exe
echo.
echo [6] Electron 日志（最后50行）
echo ----------------------------------------------------------------
if exist "%APPDATA%\KOOK消息转发系统\logs\main.log" (
    powershell -Command "Get-Content '%APPDATA%\KOOK消息转发系统\logs\main.log' -Tail 50"
) else (
    echo 未找到日志文件
)
echo.
echo ================================================================
) > "%INFO_FILE%"

echo ✅ 诊断信息已保存到：
echo %INFO_FILE%
echo.
echo 正在打开文件...
notepad "%INFO_FILE%"

echo.
pause
goto menu

:: ================================================================
:: [6] 手动启动后端+Web访问
:: ================================================================
:web_mode
cls
echo.
echo ================================================================
echo 手动启动模式（Web访问）
echo ================================================================
echo.
echo 此模式绕过 Electron，直接使用浏览器访问
echo.

if exist "dist\KOOKForwarder\KOOKForwarder.exe" (
    echo [启动] 启动后端服务...
    cd dist\KOOKForwarder
    start /MIN cmd /k "title KOOK后端服务 && KOOKForwarder.exe"
    cd ..\..
    
    echo [等待] 等待后端启动（15秒）...
    timeout /t 15 /nobreak >nul
    
    echo [打开] 在浏览器中打开...
    start http://127.0.0.1:8000
    
    echo.
    echo ✅ 后端已启动，浏览器已打开
    echo.
    echo 访问地址：
    echo   http://127.0.0.1:8000
    echo   或
    echo   http://127.0.0.1:9527
    echo.
    echo 提示：关闭后端窗口将停止服务
) else (
    echo [错误] 未找到后端可执行文件
    echo 请先构建项目
)

echo.
pause
goto menu

:: ================================================================
:: [7] 恢复备份文件
:: ================================================================
:restore_backup
cls
echo.
echo ================================================================
echo 恢复备份文件
echo ================================================================
echo.

if not exist "backup" (
    echo [错误] 未找到备份目录
    echo 没有可恢复的备份
    pause
    goto menu
)

echo 发现以下备份文件：
echo.
dir /b backup\*.bak
echo.
echo 警告：恢复备份将覆盖当前修改！
echo.
set /p confirm="确认恢复备份？(Y/N): "

if /i not "%confirm%"=="Y" (
    echo 已取消
    pause
    goto menu
)

echo.
echo [恢复] 正在恢复备份文件...

if exist "backup\main.py.bak" (
    copy /Y "backup\main.py.bak" "backend\app\main.py" >nul
    echo ✅ backend\app\main.py
)

if exist "backup\main.js.bak" (
    copy /Y "backup\main.js.bak" "frontend\electron\main.js" >nul
    echo ✅ frontend\electron\main.js
)

if exist "backup\pyinstaller.spec.bak" (
    copy /Y "backup\pyinstaller.spec.bak" "build\pyinstaller.spec" >nul
    echo ✅ build\pyinstaller.spec
)

echo.
echo [完成] 备份已恢复
echo.
pause
goto menu

:: ================================================================
:: [8] 清理并重新构建
:: ================================================================
:clean_rebuild
cls
echo.
echo ================================================================
echo 清理并重新构建
echo ================================================================
echo.
echo 此操作将：
echo   1. 清理所有构建文件
echo   2. 重新构建后端
echo   3. 重新构建前端
echo.
echo 预计时间：10-15 分钟
echo.
set /p confirm="确认执行？(Y/N): "

if /i not "%confirm%"=="Y" (
    echo 已取消
    pause
    goto menu
)

echo.
echo [清理] 删除旧的构建文件...
if exist "dist" rd /s /q dist
if exist "build\dist" rd /s /q build\dist
if exist "build\build" rd /s /q build\build
if exist "frontend\dist-electron" rd /s /q frontend\dist-electron
echo ✅ 清理完成
echo.

echo [构建] 重新构建后端...
cd backend
call venv\Scripts\activate.bat
cd ..
pyinstaller build\pyinstaller.spec --clean --noconfirm

if %errorlevel% equ 0 (
    echo ✅ 后端构建成功
) else (
    echo ❌ 后端构建失败
    pause
    goto menu
)

echo.
echo [构建] 重新构建前端...
cd frontend
call npm run electron:build:win

if %errorlevel% equ 0 (
    echo ✅ 前端构建成功
) else (
    echo ❌ 前端构建失败
)
cd ..

echo.
echo [完成] 重新构建完成
echo.
pause
goto menu
