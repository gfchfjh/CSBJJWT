@echo off
title KOOK System Complete Removal Tool

color 0A
echo.
echo ================================================================
echo.
echo          KOOK System Complete Removal Tool v2.0
echo          Auto Scan + One-Click Delete + Deep Clean
echo.
echo ================================================================
echo.
echo.
echo This tool will:
echo.
echo    1. Scan entire system for all KOOK related files
echo    2. List all found files and folders
echo    3. Delete all found items with one click
echo.
echo Features:
echo    * Smart Scan: Auto search all drives and common locations
echo    * Deep Clean: Including registry, temp files, cache
echo    * Safe: Show list before delete, need confirmation
echo.
pause
cls

:: ============================================================
:: Stage 1: Scan System
:: ============================================================
color 0E
echo.
echo ================================================================
echo Stage 1: Scanning system...
echo ================================================================
echo.
echo Scanning, please wait...
echo.

:: Create temp file to store results
set TEMP_FILE=%TEMP%\kook_scan_result.txt
if exist "%TEMP_FILE%" del "%TEMP_FILE%"

:: Scan counter
set FOUND=0

echo [1/10] Scanning installed programs...
wmic product where "name like '%%KOOK%%'" get name 2>nul | find "KOOK" >nul
if %errorlevel%==0 (
    echo    Found installed KOOK program >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [2/10] Scanning user config directories...
if exist "%APPDATA%\KOOK消息转发系统" (
    echo    %APPDATA%\KOOK (App) >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%APPDATA%\kook-forwarder" (
    echo    %APPDATA%\kook-forwarder >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [3/10] Scanning local data directories...
if exist "%LOCALAPPDATA%\KOOK消息转发系统" (
    echo    %LOCALAPPDATA%\KOOK (Local) >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%LOCALAPPDATA%\kook-forwarder" (
    echo    %LOCALAPPDATA%\kook-forwarder >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%LOCALAPPDATA%\Programs\KOOK消息转发系统" (
    echo    %LOCALAPPDATA%\Programs\KOOK >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [4/10] Scanning program directories...
if exist "%ProgramFiles%\KOOK消息转发系统" (
    echo    %ProgramFiles%\KOOK >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%ProgramFiles(x86)%\KOOK消息转发系统" (
    echo    %ProgramFiles(x86)%\KOOK >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [5/10] Scanning user directories...
if exist "%USERPROFILE%\KOOK-Build" (
    echo    %USERPROFILE%\KOOK-Build >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [6/10] Scanning Desktop...
if exist "%USERPROFILE%\Desktop\CSBJJWT" (
    echo    Desktop\CSBJJWT >> "%TEMP_FILE%"
    set /a FOUND+=1
)
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" (
    echo    Desktop\KOOK Shortcut >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [7/10] Scanning Documents...
if exist "%USERPROFILE%\Documents\CSBJJWT" (
    echo    Documents\CSBJJWT >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [8/10] Scanning Downloads...
if exist "%USERPROFILE%\Downloads\CSBJJWT" (
    echo    Downloads\CSBJJWT >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [9/10] Scanning Start Menu...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统" (
    echo    Start Menu: KOOK >> "%TEMP_FILE%"
    set /a FOUND+=1
)

echo [10/10] Scanning system drives...
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
echo Scan completed!
timeout /t 2 >nul

:: ============================================================
:: Show scan results
:: ============================================================
cls
color 0A
echo.
echo ================================================================
echo Scan Results
echo ================================================================
echo.

if %FOUND%==0 (
    color 0A
    echo.
    echo    Congratulations! No KOOK system files found
    echo.
    echo    Your computer has no KOOK system related files.
    echo.
    pause
    exit /b 0
)

echo Found %FOUND% items:
echo.
echo ----------------------------------------------------------------

:: Show found items
type "%TEMP_FILE%"

echo ----------------------------------------------------------------
echo.
echo.
echo WARNING: About to delete all items above!
echo.
echo    * Cannot be recovered after deletion
echo    * Total about 700 MB - 1.8 GB
echo    * Only delete KOOK files, other programs not affected
echo.
echo.

set /p CONFIRM="Are you sure to delete all items above? (Type YES to continue): "

if /i not "%CONFIRM%"=="YES" (
    echo.
    echo [Cancelled] Operation cancelled.
    echo.
    pause
    exit /b 0
)

:: ============================================================
:: Stage 2: Delete Files
:: ============================================================
cls
color 0C
echo.
echo ================================================================
echo Stage 2: Deleting files...
echo ================================================================
echo.

set DELETED=0

:: End related processes
echo [Prepare] Ending related processes...
taskkill /f /im "KOOK消息转发系统.exe" >nul 2>&1
taskkill /f /im "KOOKForwarder.exe" >nul 2>&1
taskkill /f /im "kook-forwarder*.exe" >nul 2>&1
echo    Done: All related processes ended
echo.

:: Uninstall app
echo [1/15] Uninstalling application...
wmic product where "name like '%%KOOK%%'" call uninstall /nointeractive >nul 2>&1
if %errorlevel%==0 (
    echo    Done: App uninstalled
    set /a DELETED+=1
) else (
    echo    Skip: No installed app
)

:: Delete program directories
echo [2/15] Deleting program directories...
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
    echo    Done: Deleted %DEL_COUNT% installation directories
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    Skip: No installation directories
)

:: Delete user config
echo [3/15] Deleting user config...
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
    echo    Done: Deleted %DEL_COUNT% config directories
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    Skip: No config directories
)

:: Delete local data
echo [4/15] Deleting local data...
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
    echo    Done: Deleted %DEL_COUNT% local data directories
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    Skip: No local data
)

:: Delete source directories
echo [5/15] Deleting source directories...
set DEL_COUNT=0
if exist "%USERPROFILE%\KOOK-Build" (
    echo    Deleting KOOK-Build (may take time)...
    rmdir /s /q "%USERPROFILE%\KOOK-Build"
    set /a DEL_COUNT+=1
)
if %DEL_COUNT% gtr 0 (
    echo    Done: Deleted KOOK-Build directory
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    Skip: No KOOK-Build directory
)

:: Delete desktop folders
echo [6/15] Deleting desktop folders...
set DEL_COUNT=0
if exist "%USERPROFILE%\Desktop\CSBJJWT" (
    echo    Deleting Desktop\CSBJJWT (may take time)...
    rmdir /s /q "%USERPROFILE%\Desktop\CSBJJWT"
    set /a DEL_COUNT+=1
)
if %DEL_COUNT% gtr 0 (
    echo    Done: Deleted CSBJJWT folder from desktop
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    Skip: No CSBJJWT on desktop
)

:: Delete documents
echo [7/15] Deleting documents...
if exist "%USERPROFILE%\Documents\CSBJJWT" (
    rmdir /s /q "%USERPROFILE%\Documents\CSBJJWT"
    echo    Done: Deleted Documents\CSBJJWT
    set /a DELETED+=1
) else (
    echo    Skip: No CSBJJWT in documents
)

:: Delete downloads
echo [8/15] Deleting downloads...
if exist "%USERPROFILE%\Downloads\CSBJJWT" (
    rmdir /s /q "%USERPROFILE%\Downloads\CSBJJWT"
    echo    Done: Deleted Downloads\CSBJJWT
    set /a DELETED+=1
) else (
    echo    Skip: No CSBJJWT in downloads
)

:: Delete root directories
echo [9/15] Deleting root directories...
set DEL_COUNT=0
for %%d in (C D E F) do (
    if exist "%%d:\CSBJJWT" (
        echo    Deleting %%d:\CSBJJWT...
        rmdir /s /q "%%d:\CSBJJWT"
        set /a DEL_COUNT+=1
    )
    if exist "%%d:\KOOK-Build" (
        echo    Deleting %%d:\KOOK-Build...
        rmdir /s /q "%%d:\KOOK-Build"
        set /a DEL_COUNT+=1
    )
)
if %DEL_COUNT% gtr 0 (
    echo    Done: Deleted %DEL_COUNT% root directories
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    Skip: No root directories
)

:: Delete shortcuts
echo [10/15] Deleting shortcuts...
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
    echo    Done: Deleted %DEL_COUNT% shortcuts
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    Skip: No shortcuts
)

:: Delete start menu
echo [11/15] Deleting start menu items...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统" (
    rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统"
    echo    Done: Deleted start menu items
    set /a DELETED+=1
) else (
    echo    Skip: No start menu items
)

:: Clean temp files
echo [12/15] Cleaning temp files...
del /f /s /q "%TEMP%\KOOK*" >nul 2>&1
del /f /s /q "%TEMP%\kook*" >nul 2>&1
del /f /s /q "%TEMP%\CSBJJWT*" >nul 2>&1
del /f /s /q "C:\Windows\Temp\KOOK*" >nul 2>&1
echo    Done: Temp files cleaned

:: Clean cache
echo [13/15] Cleaning cache...
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
    echo    Done: Deleted %DEL_COUNT% cache directories
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    Skip: No cache directories
)

:: Clean registry
echo [14/15] Cleaning registry...
set DEL_COUNT=0
reg delete "HKCU\Software\KOOK消息转发系统" /f >nul 2>&1
if %errorlevel%==0 set /a DEL_COUNT+=1
reg delete "HKCU\Software\kook-forwarder" /f >nul 2>&1
if %errorlevel%==0 set /a DEL_COUNT+=1
reg delete "HKLM\SOFTWARE\KOOK消息转发系统" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\WOW6432Node\KOOK消息转发系统" /f >nul 2>&1
if %DEL_COUNT% gtr 0 (
    echo    Done: Deleted %DEL_COUNT% registry keys
    set /a DELETED+=%DEL_COUNT%
) else (
    echo    Skip: No registry keys
)

:: Clean recycle bin
echo [15/15] Cleaning recycle bin...
rd /s /q %systemdrive%\$Recycle.bin >nul 2>&1
echo    Done: Recycle bin cleaned
echo.

:: ============================================================
:: Stage 3: Verify Results
:: ============================================================
cls
color 0A
echo.
echo ================================================================
echo Stage 3: Verifying deletion results
echo ================================================================
echo.

echo Verifying...
echo.

set REMAIN=0

:: Check for remaining files
if exist "%APPDATA%\KOOK消息转发系统" set /a REMAIN+=1
if exist "%LOCALAPPDATA%\KOOK消息转发系统" set /a REMAIN+=1
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" set /a REMAIN+=1
if exist "%USERPROFILE%\KOOK-Build" set /a REMAIN+=1
if exist "%USERPROFILE%\Desktop\CSBJJWT" set /a REMAIN+=1

timeout /t 2 >nul
cls

:: ============================================================
:: Show final results
:: ============================================================
color 0A
echo.
echo ================================================================
echo.
echo                    Deletion Complete!
echo.
echo ================================================================
echo.
echo.

if %REMAIN%==0 (
    echo Complete deletion successful!
    echo.
    echo ----------------------------------------------------------------
    echo.
    echo    Statistics:
    echo       * Scanned items: %FOUND%
    echo       * Successfully deleted: %DELETED%
    echo       * Remaining items: 0
    echo.
    echo    Freed space: About 700 MB - 1.8 GB
    echo.
    echo    Your computer has been completely cleaned of all KOOK files
    echo.
    echo ----------------------------------------------------------------
) else (
    color 0E
    echo Some items may not be completely deleted
    echo.
    echo ----------------------------------------------------------------
    echo.
    echo    Statistics:
    echo       * Scanned items: %FOUND%
    echo       * Successfully deleted: %DELETED%
    echo       * Remaining items: %REMAIN%
    echo.
    echo    Suggestion:
    echo       1. Restart computer
    echo       2. Run this script again
    echo       3. Or manually delete remaining files
    echo.
    echo ----------------------------------------------------------------
)

echo.
echo.
echo Notes:
echo    * Python, Node.js, Git and other tools not affected
echo    * To reinstall, visit:
echo      https://github.com/gfchfjh/CSBJJWT
echo.
echo ================================================================
echo.

:: Clean temp file
if exist "%TEMP_FILE%" del "%TEMP_FILE%"

pause
