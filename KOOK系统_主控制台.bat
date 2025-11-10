@echo off
chcp 65001 >nul
title KOOK转发系统 - 主控制台
color 0F

:MENU
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║          KOOK消息转发系统 - 主控制台 v18.0.4+                 ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo  当前目录: %cd%
echo  当前时间: %date% %time:~0,8%
echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │  系统管理                                                      │
echo ├────────────────────────────────────────────────────────────────┤
echo │  [1] 环境检查 - 测试系统环境                                  │
echo │  [2] Cookie功能检查 - 验证Cookie更新功能                     │
echo │  [3] 数据库检查 - 查看数据库状态                              │
echo ├────────────────────────────────────────────────────────────────┤
echo │  服务启动                                                      │
echo ├────────────────────────────────────────────────────────────────┤
echo │  [4] 启动后端服务 - 端口9527                                  │
echo │  [5] 启动前端服务 - 端口5173                                  │
echo │  [6] 同时启动后端+前端（推荐）                                │
echo ├────────────────────────────────────────────────────────────────┤
echo │  快速操作                                                      │
echo ├────────────────────────────────────────────────────────────────┤
echo │  [7] 打开前端界面 - 浏览器                                    │
echo │  [8] 打开API文档 - Swagger                                    │
echo │  [9] 查看数据目录                                              │
echo │  [10] 查看日志文件                                             │
echo ├────────────────────────────────────────────────────────────────┤
echo │  代码管理                                                      │
echo ├────────────────────────────────────────────────────────────────┤
echo │  [11] Git状态查看                                              │
echo │  [12] 拉取最新代码                                             │
echo │  [13] 查看提交历史                                             │
echo ├────────────────────────────────────────────────────────────────┤
echo │  帮助文档                                                      │
echo ├────────────────────────────────────────────────────────────────┤
echo │  [14] 查看完整操作指南                                         │
echo │  [15] 查看故障排查文档                                         │
echo │  [16] 查看快速启动文档                                         │
echo ├────────────────────────────────────────────────────────────────┤
echo │  [0] 退出                                                      │
echo └────────────────────────────────────────────────────────────────┘
echo.
set /p choice=请输入选项编号: 

if "%choice%"=="1" goto CHECK_ENV
if "%choice%"=="2" goto CHECK_COOKIE
if "%choice%"=="3" goto CHECK_DB
if "%choice%"=="4" goto START_BACKEND
if "%choice%"=="5" goto START_FRONTEND
if "%choice%"=="6" goto START_BOTH
if "%choice%"=="7" goto OPEN_FRONTEND
if "%choice%"=="8" goto OPEN_API_DOCS
if "%choice%"=="9" goto OPEN_DATA_DIR
if "%choice%"=="10" goto VIEW_LOGS
if "%choice%"=="11" goto GIT_STATUS
if "%choice%"=="12" goto GIT_PULL
if "%choice%"=="13" goto GIT_LOG
if "%choice%"=="14" goto VIEW_GUIDE
if "%choice%"=="15" goto VIEW_TROUBLESHOOTING
if "%choice%"=="16" goto VIEW_QUICKSTART
if "%choice%"=="0" goto EXIT
echo.
echo [错误] 无效的选项！
timeout /t 2 >nul
goto MENU

:CHECK_ENV
cls
echo ============================================================
echo   [1] 环境检查
echo ============================================================
echo.
call "一键测试_系统.bat"
goto MENU

:CHECK_COOKIE
cls
echo ============================================================
echo   [2] Cookie功能检查
echo ============================================================
echo.
call "一键检查_Cookie功能.bat"
goto MENU

:CHECK_DB
cls
echo ============================================================
echo   [3] 数据库检查
echo ============================================================
echo.
echo [查找数据库文件]
dir /s /b "%USERPROFILE%\Documents\KookForwarder\*.db" 2>nul
echo.
echo [数据库路径]
echo %USERPROFILE%\Documents\KookForwarder\data\config.db
echo.
if exist "%USERPROFILE%\Documents\KookForwarder\data\config.db" (
    echo [文件详情]
    dir "%USERPROFILE%\Documents\KookForwarder\data\config.db"
    echo.
    echo ✅ 数据库文件存在
) else (
    echo ⚠️  数据库文件不存在（首次运行后端会自动创建）
)
echo.
pause
goto MENU

:START_BACKEND
cls
echo ============================================================
echo   [4] 启动后端服务
echo ============================================================
echo.
echo [提示] 后端服务将在新窗口启动
echo        地址: http://localhost:9527
echo        关闭窗口或按Ctrl+C可停止服务
echo.
start "KOOK后端服务" cmd /k "快速启动_后端.bat"
echo ✅ 后端服务已在新窗口启动
timeout /t 3 >nul
goto MENU

:START_FRONTEND
cls
echo ============================================================
echo   [5] 启动前端服务
echo ============================================================
echo.
echo [提示] 前端服务将在新窗口启动
echo        地址: http://localhost:5173
echo        关闭窗口或按Ctrl+C可停止服务
echo.
start "KOOK前端服务" cmd /k "快速启动_前端.bat"
echo ✅ 前端服务已在新窗口启动
timeout /t 3 >nul
goto MENU

:START_BOTH
cls
echo ============================================================
echo   [6] 同时启动后端+前端
echo ============================================================
echo.
echo [提示] 服务将在两个新窗口启动
echo        后端: http://localhost:9527
echo        前端: http://localhost:5173
echo.
start "KOOK后端服务" cmd /k "快速启动_后端.bat"
timeout /t 3 >nul
start "KOOK前端服务" cmd /k "快速启动_前端.bat"
echo ✅ 后端和前端服务已启动
echo.
echo [等待服务启动完成...]
timeout /t 5 >nul
echo.
set /p open_browser=是否打开浏览器访问前端？(Y/N): 
if /i "%open_browser%"=="Y" (
    start http://localhost:5173
    echo ✅ 浏览器已打开
)
timeout /t 2 >nul
goto MENU

:OPEN_FRONTEND
cls
echo ============================================================
echo   [7] 打开前端界面
echo ============================================================
echo.
start http://localhost:5173
echo ✅ 浏览器已打开: http://localhost:5173
timeout /t 2 >nul
goto MENU

:OPEN_API_DOCS
cls
echo ============================================================
echo   [8] 打开API文档
echo ============================================================
echo.
start http://localhost:9527/docs
echo ✅ 浏览器已打开: http://localhost:9527/docs
timeout /t 2 >nul
goto MENU

:OPEN_DATA_DIR
cls
echo ============================================================
echo   [9] 查看数据目录
echo ============================================================
echo.
if exist "%USERPROFILE%\Documents\KookForwarder\data" (
    start explorer "%USERPROFILE%\Documents\KookForwarder\data"
    echo ✅ 已打开: %USERPROFILE%\Documents\KookForwarder\data
) else (
    echo ⚠️  数据目录不存在
    echo 路径: %USERPROFILE%\Documents\KookForwarder\data
)
timeout /t 2 >nul
goto MENU

:VIEW_LOGS
cls
echo ============================================================
echo   [10] 查看日志文件
echo ============================================================
echo.
if exist "%USERPROFILE%\Documents\KookForwarder\data\logs" (
    start explorer "%USERPROFILE%\Documents\KookForwarder\data\logs"
    echo ✅ 已打开日志目录
) else (
    echo ⚠️  日志目录不存在
    echo 路径: %USERPROFILE%\Documents\KookForwarder\data\logs
)
timeout /t 2 >nul
goto MENU

:GIT_STATUS
cls
echo ============================================================
echo   [11] Git状态查看
echo ============================================================
echo.
echo [当前分支]
git branch
echo.
echo [工作区状态]
git status
echo.
echo [最近5次提交]
git log --oneline -5
echo.
pause
goto MENU

:GIT_PULL
cls
echo ============================================================
echo   [12] 拉取最新代码
echo ============================================================
echo.
echo [警告] 这将从远程仓库拉取最新代码
echo        如果有本地修改，请先提交或暂存
echo.
set /p confirm=确认拉取？(Y/N): 
if /i not "%confirm%"=="Y" goto MENU
echo.
echo [执行] git pull origin main
git pull origin main
echo.
if %errorlevel% equ 0 (
    echo ✅ 代码更新成功
) else (
    echo ❌ 代码更新失败，请检查错误信息
)
echo.
pause
goto MENU

:GIT_LOG
cls
echo ============================================================
echo   [13] 查看提交历史
echo ============================================================
echo.
echo [最近20次提交]
git log --oneline --graph --all -20
echo.
pause
goto MENU

:VIEW_GUIDE
cls
echo ============================================================
echo   [14] 查看完整操作指南
echo ============================================================
echo.
if exist "CMD_操作指南_完整版.md" (
    start notepad "CMD_操作指南_完整版.md"
    echo ✅ 已打开: CMD_操作指南_完整版.md
) else (
    echo ❌ 文件不存在: CMD_操作指南_完整版.md
)
timeout /t 2 >nul
goto MENU

:VIEW_TROUBLESHOOTING
cls
echo ============================================================
echo   [15] 查看故障排查文档
echo ============================================================
echo.
if exist "TROUBLESHOOTING_WINDOWS.md" (
    start notepad "TROUBLESHOOTING_WINDOWS.md"
    echo ✅ 已打开: TROUBLESHOOTING_WINDOWS.md
) else (
    echo ❌ 文件不存在: TROUBLESHOOTING_WINDOWS.md
)
timeout /t 2 >nul
goto MENU

:VIEW_QUICKSTART
cls
echo ============================================================
echo   [16] 查看快速启动文档
echo ============================================================
echo.
if exist "QUICK_START_WINDOWS.md" (
    start notepad "QUICK_START_WINDOWS.md"
    echo ✅ 已打开: QUICK_START_WINDOWS.md
) else (
    echo ❌ 文件不存在: QUICK_START_WINDOWS.md
)
timeout /t 2 >nul
goto MENU

:EXIT
cls
echo.
echo ========================================
echo   感谢使用KOOK消息转发系统！
echo ========================================
echo.
timeout /t 2 >nul
exit

