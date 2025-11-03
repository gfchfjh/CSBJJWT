@echo off
chcp 65001 >nul
title 彻底删除本地 KOOK 系统

color 0A
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║          彻底删除本地 KOOK 系统 - 自动清理工具            ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo.
echo 本工具将删除您电脑上的所有 KOOK 系统文件：
echo.
echo   📦 已安装的应用程序
echo   📁 用户配置和数据
echo   💾 源码和构建文件（桌面、KOOK-Build 等）
echo   🔗 桌面快捷方式
echo   🗂️  缓存和临时文件
echo   📝 注册表项
echo.
echo ⚠️  注意：此操作将删除所有数据，无法恢复！
echo.
echo.

set /p CONFIRM="确定要删除吗？(输入 YES 继续，输入其他取消): "

if /i not "%CONFIRM%"=="YES" (
    echo.
    echo [取消] 已取消删除操作。
    echo.
    pause
    exit /b
)

echo.
echo.
echo ════════════════════════════════════════════════════════════
echo 开始删除...
echo ════════════════════════════════════════════════════════════
echo.

:: 计数器
set COUNT=0

:: ============================================================
:: 第 1 步：卸载已安装的应用程序
:: ============================================================
echo [第 1 步] 卸载已安装的应用程序...
echo.

:: 通过 WMIC 卸载
wmic product where "name like '%%KOOK%%'" call uninstall /nointeractive >nul 2>&1
if %errorlevel%==0 (
    echo    ✓ 已卸载应用程序
    set /a COUNT+=1
) else (
    echo    ○ 未找到已安装的应用（可能已卸载或未安装）
)

:: 删除程序安装目录（常见位置）
if exist "%ProgramFiles%\KOOK消息转发系统" (
    rmdir /s /q "%ProgramFiles%\KOOK消息转发系统"
    echo    ✓ 已删除 Program Files 安装目录
    set /a COUNT+=1
)

if exist "%ProgramFiles(x86)%\KOOK消息转发系统" (
    rmdir /s /q "%ProgramFiles(x86)%\KOOK消息转发系统"
    echo    ✓ 已删除 Program Files (x86) 安装目录
    set /a COUNT+=1
)

if exist "%LOCALAPPDATA%\Programs\KOOK消息转发系统" (
    rmdir /s /q "%LOCALAPPDATA%\Programs\KOOK消息转发系统"
    echo    ✓ 已删除本地 Programs 安装目录
    set /a COUNT+=1
)

echo.

:: ============================================================
:: 第 2 步：删除用户数据和配置
:: ============================================================
echo [第 2 步] 删除用户数据和配置...
echo.

:: APPDATA
if exist "%APPDATA%\KOOK消息转发系统" (
    rmdir /s /q "%APPDATA%\KOOK消息转发系统"
    echo    ✓ 已删除用户配置目录（APPDATA）
    set /a COUNT+=1
)

if exist "%APPDATA%\kook-forwarder" (
    rmdir /s /q "%APPDATA%\kook-forwarder"
    echo    ✓ 已删除 kook-forwarder 配置
    set /a COUNT+=1
)

:: LOCALAPPDATA
if exist "%LOCALAPPDATA%\KOOK消息转发系统" (
    rmdir /s /q "%LOCALAPPDATA%\KOOK消息转发系统"
    echo    ✓ 已删除本地数据目录
    set /a COUNT+=1
)

if exist "%LOCALAPPDATA%\kook-forwarder" (
    rmdir /s /q "%LOCALAPPDATA%\kook-forwarder"
    echo    ✓ 已删除 kook-forwarder 本地数据
    set /a COUNT+=1
)

echo.

:: ============================================================
:: 第 3 步：删除源码和构建目录
:: ============================================================
echo [第 3 步] 删除源码和构建目录...
echo.

:: 常见的源码位置
if exist "%USERPROFILE%\KOOK-Build" (
    echo    正在删除 KOOK-Build 目录...
    rmdir /s /q "%USERPROFILE%\KOOK-Build"
    echo    ✓ 已删除 %USERPROFILE%\KOOK-Build
    set /a COUNT+=1
)

if exist "%USERPROFILE%\Desktop\CSBJJWT" (
    echo    正在删除桌面上的 CSBJJWT 目录...
    rmdir /s /q "%USERPROFILE%\Desktop\CSBJJWT"
    echo    ✓ 已删除桌面\CSBJJWT
    set /a COUNT+=1
)

if exist "%USERPROFILE%\Documents\CSBJJWT" (
    rmdir /s /q "%USERPROFILE%\Documents\CSBJJWT"
    echo    ✓ 已删除文档\CSBJJWT
    set /a COUNT+=1
)

if exist "%USERPROFILE%\Downloads\CSBJJWT" (
    rmdir /s /q "%USERPROFILE%\Downloads\CSBJJWT"
    echo    ✓ 已删除下载\CSBJJWT
    set /a COUNT+=1
)

:: 检查其他可能的位置
if exist "C:\CSBJJWT" (
    rmdir /s /q "C:\CSBJJWT"
    echo    ✓ 已删除 C:\CSBJJWT
    set /a COUNT+=1
)

if exist "D:\CSBJJWT" (
    rmdir /s /q "D:\CSBJJWT"
    echo    ✓ 已删除 D:\CSBJJWT
    set /a COUNT+=1
)

echo.

:: ============================================================
:: 第 4 步：删除快捷方式
:: ============================================================
echo [第 4 步] 删除快捷方式...
echo.

:: 桌面快捷方式
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" (
    del "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk"
    echo    ✓ 已删除桌面快捷方式
    set /a COUNT+=1
)

if exist "%USERPROFILE%\Desktop\KOOK*.lnk" (
    del "%USERPROFILE%\Desktop\KOOK*.lnk"
    echo    ✓ 已删除其他 KOOK 快捷方式
    set /a COUNT+=1
)

:: 开始菜单
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统" (
    rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统"
    echo    ✓ 已删除开始菜单项
    set /a COUNT+=1
)

:: 公共桌面（所有用户）
if exist "%PUBLIC%\Desktop\KOOK消息转发系统.lnk" (
    del "%PUBLIC%\Desktop\KOOK消息转发系统.lnk"
    echo    ✓ 已删除公共桌面快捷方式
    set /a COUNT+=1
)

echo.

:: ============================================================
:: 第 5 步：清理临时文件和缓存
:: ============================================================
echo [第 5 步] 清理临时文件和缓存...
echo.

:: TEMP 目录
del /f /s /q "%TEMP%\KOOK*" >nul 2>&1
del /f /s /q "%TEMP%\kook*" >nul 2>&1
del /f /s /q "%TEMP%\CSBJJWT*" >nul 2>&1
echo    ✓ 已清理用户临时文件

:: 系统 TEMP（需要管理员权限）
del /f /s /q "C:\Windows\Temp\KOOK*" >nul 2>&1
del /f /s /q "C:\Windows\Temp\kook*" >nul 2>&1
echo    ✓ 已清理系统临时文件

:: Electron 缓存
if exist "%LOCALAPPDATA%\electron" (
    rmdir /s /q "%LOCALAPPDATA%\electron"
    echo    ✓ 已删除 Electron 缓存
    set /a COUNT+=1
)

if exist "%LOCALAPPDATA%\electron-builder" (
    rmdir /s /q "%LOCALAPPDATA%\electron-builder"
    echo    ✓ 已删除 Electron Builder 缓存
    set /a COUNT+=1
)

:: npm 缓存中的相关文件
if exist "%APPDATA%\npm-cache\*kook*" (
    del /f /s /q "%APPDATA%\npm-cache\*kook*" >nul 2>&1
    echo    ✓ 已清理 npm 缓存
)

echo.

:: ============================================================
:: 第 6 步：清理注册表
:: ============================================================
echo [第 6 步] 清理注册表项...
echo.

:: 用户注册表
reg delete "HKCU\Software\KOOK消息转发系统" /f >nul 2>&1
if %errorlevel%==0 (
    echo    ✓ 已删除用户注册表项
    set /a COUNT+=1
)

reg delete "HKCU\Software\kook-forwarder" /f >nul 2>&1
if %errorlevel%==0 (
    echo    ✓ 已删除 kook-forwarder 注册表项
    set /a COUNT+=1
)

:: 系统注册表（需要管理员权限）
reg delete "HKLM\SOFTWARE\KOOK消息转发系统" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\WOW6432Node\KOOK消息转发系统" /f >nul 2>&1
echo    ✓ 已清理系统注册表项（如果存在）

echo.

:: ============================================================
:: 第 7 步：结束相关进程
:: ============================================================
echo [第 7 步] 结束相关进程...
echo.

taskkill /f /im "KOOK消息转发系统.exe" >nul 2>&1
taskkill /f /im "KOOKForwarder.exe" >nul 2>&1
taskkill /f /im "kook-forwarder*.exe" >nul 2>&1
echo    ✓ 已结束所有相关进程

echo.

:: ============================================================
:: 第 8 步：验证清理结果
:: ============================================================
echo [第 8 步] 验证清理结果...
echo.

set REMAIN=0

if exist "%APPDATA%\KOOK消息转发系统" set /a REMAIN+=1
if exist "%LOCALAPPDATA%\KOOK消息转发系统" set /a REMAIN+=1
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" set /a REMAIN+=1
if exist "%USERPROFILE%\KOOK-Build" set /a REMAIN+=1
if exist "%USERPROFILE%\Desktop\CSBJJWT" set /a REMAIN+=1

echo.
echo ════════════════════════════════════════════════════════════
echo 清理完成！
echo ════════════════════════════════════════════════════════════
echo.

if %REMAIN%==0 (
    color 0A
    echo    ✅ 完全删除成功！
    echo.
    echo    所有 KOOK 系统相关文件已从您的电脑上删除。
    echo    共删除了 %COUNT% 个项目。
) else (
    color 0E
    echo    ⚠️  部分文件可能未完全删除
    echo.
    echo    请手动检查以下位置：
    echo       - %APPDATA%\KOOK消息转发系统
    echo       - %LOCALAPPDATA%\KOOK消息转发系统
    echo       - %USERPROFILE%\KOOK-Build
    echo       - 桌面上的 CSBJJWT 文件夹
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 释放的磁盘空间：
echo    • 应用程序：约 100 MB
echo    • 用户数据：约 10 MB
echo    • 源码文件：约 500 MB - 1.7 GB（如果有）
echo    • 缓存文件：约 50 MB
echo    ─────────────────────────────────
echo    • 总计：约 700 MB - 1.8 GB
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 如需重新安装：
echo    1. 访问 GitHub: https://github.com/gfchfjh/CSBJJWT
echo    2. 下载最新版本
echo    3. 按照安装指南操作
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
