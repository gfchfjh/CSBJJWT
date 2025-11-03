@echo off
chcp 65001 >nul
title KOOK 系统完全卸载工具

echo ========================================
echo KOOK 消息转发系统 - 完全卸载工具
echo ========================================
echo.
echo 本工具将删除以下内容：
echo   1. 已安装的 Electron 应用
echo   2. 用户数据和配置文件
echo   3. 项目源码和构建文件
echo   4. 桌面和开始菜单快捷方式
echo   5. 临时文件和缓存
echo.
echo ⚠️  警告：此操作不可逆！
echo.
set /p CONFIRM="确定要继续吗？(输入 YES 继续): "

if /i not "%CONFIRM%"=="YES" (
    echo 已取消卸载。
    pause
    exit /b
)

echo.
echo ========================================
echo 开始卸载...
echo ========================================
echo.

:: 步骤 1: 卸载应用（通过 wmic）
echo [1/8] 卸载 Electron 应用...
wmic product where "name like '%%KOOK%%'" call uninstall /nointeractive 2>nul
if %errorlevel%==0 (
    echo [OK] 应用已卸载
) else (
    echo [INFO] 未找到已安装的应用或已卸载
)
echo.

:: 步骤 2: 删除用户数据
echo [2/8] 删除用户数据...
if exist "%APPDATA%\KOOK消息转发系统" (
    rmdir /s /q "%APPDATA%\KOOK消息转发系统"
    echo [OK] 已删除 %%APPDATA%%\KOOK消息转发系统
)
if exist "%APPDATA%\kook-forwarder" (
    rmdir /s /q "%APPDATA%\kook-forwarder"
    echo [OK] 已删除 %%APPDATA%%\kook-forwarder
)
if exist "%LOCALAPPDATA%\KOOK消息转发系统" (
    rmdir /s /q "%LOCALAPPDATA%\KOOK消息转发系统"
    echo [OK] 已删除 %%LOCALAPPDATA%%\KOOK消息转发系统
)
if exist "%LOCALAPPDATA%\kook-forwarder" (
    rmdir /s /q "%LOCALAPPDATA%\kook-forwarder"
    echo [OK] 已删除 %%LOCALAPPDATA%%\kook-forwarder
)
if exist "%LOCALAPPDATA%\Programs\KOOK消息转发系统" (
    rmdir /s /q "%LOCALAPPDATA%\Programs\KOOK消息转发系统"
    echo [OK] 已删除安装目录
)
echo.

:: 步骤 3: 删除构建目录
echo [3/8] 删除构建目录...
if exist "%USERPROFILE%\KOOK-Build" (
    rmdir /s /q "%USERPROFILE%\KOOK-Build"
    echo [OK] 已删除 %%USERPROFILE%%\KOOK-Build
)
if exist "%USERPROFILE%\Desktop\CSBJJWT" (
    rmdir /s /q "%USERPROFILE%\Desktop\CSBJJWT"
    echo [OK] 已删除桌面上的 CSBJJWT
)
echo.

:: 步骤 4: 删除快捷方式
echo [4/8] 删除快捷方式...
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" (
    del "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk"
    echo [OK] 已删除桌面快捷方式
)
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统" (
    rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统"
    echo [OK] 已删除开始菜单项
)
echo.

:: 步骤 5: 清理临时文件
echo [5/8] 清理临时文件...
del /f /s /q "%TEMP%\KOOK*" 2>nul
del /f /s /q "%TEMP%\kook*" 2>nul
echo [OK] 临时文件已清理
echo.

:: 步骤 6: 清理缓存
echo [6/8] 清理缓存...
if exist "%LOCALAPPDATA%\electron" (
    rmdir /s /q "%LOCALAPPDATA%\electron"
    echo [OK] 已删除 Electron 缓存
)
if exist "%LOCALAPPDATA%\electron-builder" (
    rmdir /s /q "%LOCALAPPDATA%\electron-builder"
    echo [OK] 已删除 Electron Builder 缓存
)
echo.

:: 步骤 7: 清理注册表（需要管理员权限）
echo [7/8] 清理注册表...
reg delete "HKCU\Software\KOOK消息转发系统" /f 2>nul
reg delete "HKCU\Software\kook-forwarder" /f 2>nul
echo [OK] 注册表项已清理（如果存在）
echo.

:: 步骤 8: 验证清理
echo [8/8] 验证清理结果...
set CLEAN=1

if exist "%APPDATA%\KOOK消息转发系统" set CLEAN=0
if exist "%LOCALAPPDATA%\KOOK消息转发系统" set CLEAN=0
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" set CLEAN=0

if %CLEAN%==1 (
    echo [OK] ✅ 清理完成！
    echo.
    echo 所有 KOOK 系统相关文件已删除。
) else (
    echo [WARNING] ⚠️  部分文件可能未完全删除
    echo 请手动检查以下位置：
    echo   - %%APPDATA%%
    echo   - %%LOCALAPPDATA%%
    echo   - 桌面快捷方式
)

echo.
echo ========================================
echo 卸载完成
echo ========================================
echo.
echo 如果需要重新安装，请从 GitHub 下载最新版本。
echo GitHub: https://github.com/gfchfjh/CSBJJWT
echo.
pause
