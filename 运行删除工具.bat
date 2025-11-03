@echo off
:: Encoding Fix Launcher for KOOK Deletion Tool
:: This script ensures proper encoding and admin rights

:: Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Set working directory
cd /d "%~dp0"

echo ================================================================
echo KOOK System Deletion Tool Launcher
echo ================================================================
echo.
echo Checking for available scripts...
echo.

:: Check which script exists
if exist "Delete-KOOK-System.bat" (
    echo [1] Found: Delete-KOOK-System.bat (English version)
    echo     - No encoding issues
    echo     - Recommended
    echo.
    set SCRIPT_EN=1
) else (
    set SCRIPT_EN=0
)

if exist "自动扫描删除KOOK.bat" (
    echo [2] Found: Auto Scan Delete (Chinese version)
    echo     - May have encoding issues
    echo.
    set SCRIPT_CN=1
) else (
    set SCRIPT_CN=0
)

echo.

if %SCRIPT_EN%==1 (
    echo Running English version...
    echo.
    call "Delete-KOOK-System.bat"
) else if %SCRIPT_CN%==1 (
    echo Running Chinese version with encoding fix...
    echo.
    chcp 65001 >nul
    call "自动扫描删除KOOK.bat"
) else (
    echo.
    echo [ERROR] No deletion script found!
    echo.
    echo Please ensure one of these files exists:
    echo   * Delete-KOOK-System.bat (English)
    echo   * Auto Scan Delete KOOK.bat (Chinese)
    echo.
    pause
)
