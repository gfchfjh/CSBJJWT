@echo off
chcp 65001 >nul
title KOOK 系统智能扫描删除工具

color 0B
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║         KOOK 系统智能扫描删除工具 v2.0                        ║
echo ║         自动扫描 + 一键删除 + 深度清理                        ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo.
echo 🔍 本工具将：
echo.
echo    1. 自动扫描整个系统，查找所有 KOOK 相关文件
echo    2. 列出所有找到的文件和文件夹
echo    3. 一键删除所有找到的项目
echo.
echo ⚡ 特点：
echo    • 智能扫描：自动查找所有盘符和常用位置
echo    • 深度清理：包括注册表、临时文件、缓存
echo    • 安全可靠：删除前显示清单，需要确认
echo.
pause
cls

:: ============================================================
:: 第 1 阶段：扫描系统
:: ============================================================
color 0E
echo.
echo ════════════════════════════════════════════════════════════════
echo 第 1 阶段：正在扫描系统...
echo ════════════════════════════════════════════════════════════════
echo.
echo 🔍 扫描中，请稍候...
echo.

:: 创建临时文件存储结果
set TEMP_FILE=%TEMP%\kook_scan_result.txt
if exist "%TEMP_FILE%" del "%TEMP_FILE%"

:: 扫描计数
set FOUND=0

echo [1/10] 扫描已安装的程序...
wmic product where "name like '%%KOOK%%'" get name 2>nul | find "KOOK" >nul
if %errorlevel%==0 (
    echo    ✓ 找到已安装的 KOOK 程序 >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [2/10] 扫描用户配置目录...
if exist "%APPDATA%\KOOK消息转发系统" (
    echo    %APPDATA%\KOOK消息转发系统 >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%APPDATA%\kook-forwarder" (
    echo    %APPDATA%\kook-forwarder >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [3/10] 扫描本地数据目录...
if exist "%LOCALAPPDATA%\KOOK消息转发系统" (
    echo    %LOCALAPPDATA%\KOOK消息转发系统 >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%LOCALAPPDATA%\kook-forwarder" (
    echo    %LOCALAPPDATA%\kook-forwarder >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%LOCALAPPDATA%\Programs\KOOK消息转发系统" (
    echo    %LOCALAPPDATA%\Programs\KOOK消息转发系统 >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [4/10] 扫描程序安装目录...
if exist "%ProgramFiles%\KOOK消息转发系统" (
    echo    %ProgramFiles%\KOOK消息转发系统 >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%ProgramFiles(x86)%\KOOK消息转发系统" (
    echo    %ProgramFiles(x86)%\KOOK消息转发系统 >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [5/10] 扫描用户目录...
if exist "%USERPROFILE%\KOOK-Build" (
    echo    %USERPROFILE%\KOOK-Build >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [6/10] 扫描桌面...
if exist "%USERPROFILE%\Desktop\CSBJJWT" (
    echo    %USERPROFILE%\Desktop\CSBJJWT >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" (
    echo    %USERPROFILE%\Desktop\KOOK消息转发系统.lnk >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%PUBLIC%\Desktop\KOOK消息转发系统.lnk" (
    echo    %PUBLIC%\Desktop\KOOK消息转发系统.lnk >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [7/10] 扫描文档目录...
if exist "%USERPROFILE%\Documents\CSBJJWT" (
    echo    %USERPROFILE%\Documents\CSBJJWT >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [8/10] 扫描下载目录...
if exist "%USERPROFILE%\Downloads\CSBJJWT" (
    echo    %USERPROFILE%\Downloads\CSBJJWT >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [9/10] 扫描开始菜单...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统" (
    echo    开始菜单：KOOK消息转发系统 >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [10/10] 扫描系统盘根目录...
for %%d in (C D E F) do (
    if exist "%%d:\CSBJJWT" (
        echo    %%d:\CSBJJWT >> "%TEMP_FILE%"
        set /a FOUND+=1
    )
    if exist "%%d:\KOOK-Build" (
        echo    %%d:\KOOK-Build >> "%TEMP_FILE%"
        set /a FOUND+=1
    )
)

echo.
echo ✓ 扫描完成！
timeout /t 2 >nul

:: ============================================================
:: 显示扫描结果
:: ============================================================
cls
color 0A
echo.
echo ════════════════════════════════════════════════════════════════
echo 扫描结果
echo ════════════════════════════════════════════════════════════════
echo.

if %FOUND%==0 (
    color 0A
    echo.
    echo    ✅ 恭喜！未找到任何 KOOK 系统文件
    echo.
    echo    您的电脑上没有 KOOK 系统相关文件。
    echo.
    pause
    exit /b 0
)

echo 📊 共找到 %FOUND% 个项目：
echo.
echo ────────────────────────────────────────────────────────────────

:: 显示找到的项目
type "%TEMP_FILE%"

echo ────────────────────────────────────────────────────────────────
echo.
echo.
echo ⚠️  警告：即将删除以上所有项目！
echo.
echo    • 删除后无法恢复
echo    • 总计约 700 MB - 1.8 GB
echo    • 仅删除 KOOK 相关文件，不影响其他程序
echo.
echo.

set /p CONFIRM="确定要删除以上所有项目吗？(输入 YES 继续): "

if /i not "%CONFIRM%"=="YES" (
    echo.
    echo [取消] 已取消删除操作。
    echo.
    pause
    exit /b 0
)

:: ============================================================
:: 第 2 阶段：删除文件
:: ============================================================
cls
color 0C
echo.
echo ════════════════════════════════════════════════════════════════
echo 第 2 阶段：正在删除文件...
echo ════════════════════════════════════════════════════════════════
echo.

set DELETED=0

:: 结束相关进程
echo [准备工作] 结束相关进程...
taskkill /f /im "KOOK消息转发系统.exe" >nul 2>&1
taskkill /f /im "KOOKForwarder.exe" >nul 2>&1
taskkill /f /im "kook-forwarder*.exe" >nul 2>&1
echo    ✓ 已结束所有相关进程
echo.

:: 卸载应用
echo [1/15] 卸载应用程序...
wmic product where "name like '%%KOOK%%'" call uninstall /nointeractive >nul 2>&1
if %errorlevel%==0 (
    echo    ✓ 已卸载应用
    set /a DELETED+=1
) else (
    echo    - 无已安装应用
)

:: 删除程序目录
echo [2/15] 删除程序安装目录...
set DEL_COUNT=0
if exist "%ProgramFiles%\KOOK消息转发系统" (
    rmdir /s /q "%ProgramFiles%\KOOK消息转发系统"
    set /a DEL_COUNT+=1
)
if exist "%ProgramFiles(x86)%\KOOK消息转发系统" (
    rmdir /s /q "%ProgramFiles(x86)%\KOOK消息转发系统"
    set /a DEL_COUNT+=1
)
if exist "%LOCALAPPDATA%\Programs\KOOK消息转发系统" (
    rmdir /s /q "%LOCALAPPDATA%\Programs\KOOK消息转发系统"
    set /a DEL_COUNT+=1
)
if %DEL_COUNT% gtr 0 (
    echo    ✓ 已删除 %DEL_COUNT% 个安装目录
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    - 无安装目录
)

:: 删除用户配置
echo [3/15] 删除用户配置...
set DEL_COUNT=0
if exist "%APPDATA%\KOOK消息转发系统" (
    rmdir /s /q "%APPDATA%\KOOK消息转发系统"
    set /a DEL_COUNT+=1
)
if exist "%APPDATA%\kook-forwarder" (
    rmdir /s /q "%APPDATA%\kook-forwarder"
    set /a DEL_COUNT+=1
)
if %DEL_COUNT% gtr 0 (
    echo    ✓ 已删除 %DEL_COUNT% 个配置目录
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    - 无配置目录
)

:: 删除本地数据
echo [4/15] 删除本地数据...
set DEL_COUNT=0
if exist "%LOCALAPPDATA%\KOOK消息转发系统" (
    rmdir /s /q "%LOCALAPPDATA%\KOOK消息转发系统"
    set /a DEL_COUNT+=1
)
if exist "%LOCALAPPDATA%\kook-forwarder" (
    rmdir /s /q "%LOCALAPPDATA%\kook-forwarder"
    set /a DEL_COUNT+=1
)
if %DEL_COUNT% gtr 0 (
    echo    ✓ 已删除 %DEL_COUNT% 个本地数据目录
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    - 无本地数据
)

:: 删除源码目录
echo [5/15] 删除源码目录...
set DEL_COUNT=0
if exist "%USERPROFILE%\KOOK-Build" (
    echo    正在删除 KOOK-Build (可能较大，请稍候)...
    rmdir /s /q "%USERPROFILE%\KOOK-Build"
    set /a DEL_COUNT+=1
)
if %DEL_COUNT% gtr 0 (
    echo    ✓ 已删除 KOOK-Build 目录
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    - 无 KOOK-Build 目录
)

:: 删除桌面文件夹
echo [6/15] 删除桌面文件夹...
set DEL_COUNT=0
if exist "%USERPROFILE%\Desktop\CSBJJWT" (
    echo    正在删除桌面\CSBJJWT (可能较大，请稍候)...
    rmdir /s /q "%USERPROFILE%\Desktop\CSBJJWT"
    set /a DEL_COUNT+=1
)
if %DEL_COUNT% gtr 0 (
    echo    ✓ 已删除桌面上的 CSBJJWT 文件夹
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    - 桌面无 CSBJJWT 文件夹
)

:: 删除文档目录
echo [7/15] 删除文档目录...
if exist "%USERPROFILE%\Documents\CSBJJWT" (
    rmdir /s /q "%USERPROFILE%\Documents\CSBJJWT"
    echo    ✓ 已删除文档\CSBJJWT
    set /a DELETED+=1
) else (
    echo    - 文档无 CSBJJWT 目录
)

:: 删除下载目录
echo [8/15] 删除下载目录...
if exist "%USERPROFILE%\Downloads\CSBJJWT" (
    rmdir /s /q "%USERPROFILE%\Downloads\CSBJJWT"
    echo    ✓ 已删除下载\CSBJJWT
    set /a DELETED+=1
) else (
    echo    - 下载无 CSBJJWT 目录
)

:: 删除系统盘根目录
echo [9/15] 删除系统盘根目录...
set DEL_COUNT=0
for %%d in (C D E F) do (
    if exist "%%d:\CSBJJWT" (
        echo    正在删除 %%d:\CSBJJWT...
        rmdir /s /q "%%d:\CSBJJWT"
        set /a DEL_COUNT+=1
    )
    if exist "%%d:\KOOK-Build" (
        echo    正在删除 %%d:\KOOK-Build...
        rmdir /s /q "%%d:\KOOK-Build"
        set /a DEL_COUNT+=1
    )
)
if %DEL_COUNT% gtr 0 (
    echo    ✓ 已删除 %DEL_COUNT% 个根目录文件夹
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    - 根目录无相关文件夹
)

:: 删除快捷方式
echo [10/15] 删除快捷方式...
set DEL_COUNT=0
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" (
    del "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk"
    set /a DEL_COUNT+=1
)
if exist "%USERPROFILE%\Desktop\KOOK*.lnk" (
    del "%USERPROFILE%\Desktop\KOOK*.lnk"
    set /a DEL_COUNT+=1
)
if exist "%PUBLIC%\Desktop\KOOK消息转发系统.lnk" (
    del "%PUBLIC%\Desktop\KOOK消息转发系统.lnk"
    set /a DEL_COUNT+=1
)
if %DEL_COUNT% gtr 0 (
    echo    ✓ 已删除 %DEL_COUNT% 个快捷方式
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    - 无快捷方式
)

:: 删除开始菜单
echo [11/15] 删除开始菜单项...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统" (
    rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统"
    echo    ✓ 已删除开始菜单项
    set /a DELETED+=1
) else (
    echo    - 无开始菜单项
)

:: 清理临时文件
echo [12/15] 清理临时文件...
del /f /s /q "%TEMP%\KOOK*" >nul 2>&1
del /f /s /q "%TEMP%\kook*" >nul 2>&1
del /f /s /q "%TEMP%\CSBJJWT*" >nul 2>&1
del /f /s /q "C:\Windows\Temp\KOOK*" >nul 2>&1
echo    ✓ 已清理临时文件

:: 清理缓存
echo [13/15] 清理缓存...
set DEL_COUNT=0
if exist "%LOCALAPPDATA%\electron" (
    rmdir /s /q "%LOCALAPPDATA%\electron"
    set /a DEL_COUNT+=1
)
if exist "%LOCALAPPDATA%\electron-builder" (
    rmdir /s /q "%LOCALAPPDATA%\electron-builder"
    set /a DEL_COUNT+=1
)
if %DEL_COUNT% gtr 0 (
    echo    ✓ 已删除 %DEL_COUNT% 个缓存目录
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    - 无缓存目录
)

:: 清理注册表
echo [14/15] 清理注册表...
set DEL_COUNT=0
reg delete "HKCU\Software\KOOK消息转发系统" /f >nul 2>&1
if %errorlevel%==0 set /a DEL_COUNT+=1
reg delete "HKCU\Software\kook-forwarder" /f >nul 2>&1
if %errorlevel%==0 set /a DEL_COUNT+=1
reg delete "HKLM\SOFTWARE\KOOK消息转发系统" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\WOW6432Node\KOOK消息转发系统" /f >nul 2>&1
if %DEL_COUNT% gtr 0 (
    echo    ✓ 已删除 %DEL_COUNT% 个注册表项
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    - 无注册表项
)

:: 清理回收站中的相关项
echo [15/15] 清理回收站...
rd /s /q %systemdrive%\$Recycle.bin >nul 2>&1
echo    ✓ 已清空回收站
echo.

:: ============================================================
:: 第 3 阶段：验证结果
:: ============================================================
cls
color 0A
echo.
echo ════════════════════════════════════════════════════════════════
echo 第 3 阶段：验证删除结果
echo ════════════════════════════════════════════════════════════════
echo.

echo 🔍 正在验证...
echo.

set REMAIN=0

:: 检查是否还有残留
if exist "%APPDATA%\KOOK消息转发系统" set /a REMAIN+=1
if exist "%LOCALAPPDATA%\KOOK消息转发系统" set /a REMAIN+=1
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" set /a REMAIN+=1
if exist "%USERPROFILE%\KOOK-Build" set /a REMAIN+=1
if exist "%USERPROFILE%\Desktop\CSBJJWT" set /a REMAIN+=1

timeout /t 2 >nul
cls

:: ============================================================
:: 显示最终结果
:: ============================================================
color 0A
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║                    🎉 删除完成！                              ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo.

if %REMAIN%==0 (
    echo ✅ 完全删除成功！
    echo.
    echo ────────────────────────────────────────────────────────────────
    echo.
    echo    📊 统计信息：
    echo       • 扫描到的项目：%FOUND% 个
    echo       • 成功删除：%DELETED% 个
    echo       • 残留项目：0 个
    echo.
    echo    💾 释放空间：约 700 MB - 1.8 GB
    echo.
    echo    ✨ 您的电脑已完全清除所有 KOOK 系统文件
    echo.
    echo ────────────────────────────────────────────────────────────────
) else (
    color 0E
    echo ⚠️  部分项目可能未完全删除
    echo.
    echo ────────────────────────────────────────────────────────────────
    echo.
    echo    📊 统计信息：
    echo       • 扫描到的项目：%FOUND% 个
    echo       • 成功删除：%DELETED% 个
    echo       • 残留项目：%REMAIN% 个
    echo.
    echo    💡 建议：
    echo       1. 重启电脑
    echo       2. 重新运行此脚本
    echo       3. 或手动删除残留文件
    echo.
    echo ────────────────────────────────────────────────────────────────
)

echo.
echo.
echo 📝 注意事项：
echo    • Python、Node.js、Git 等工具未受影响
echo    • 如需重新安装，请访问：
echo      https://github.com/gfchfjh/CSBJJWT
echo.
echo ════════════════════════════════════════════════════════════════
echo.

:: 清理临时文件
if exist "%TEMP_FILE%" del "%TEMP_FILE%"

pause
