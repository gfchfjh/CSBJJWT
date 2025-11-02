@echo off
setlocal enabledelayedexpansion
title KOOK Message Forwarder - One-Click Installer

color 0B
cls
echo.
echo ============================================================
echo.
echo      KOOK Message Forwarder - One-Click Installer
echo.
echo      Version 2.0 (Safe Mode)
echo.
echo ============================================================
echo.
echo Starting installation process...
echo.
pause

:: Check admin rights
echo.
echo Checking administrator rights...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [WARNING] Not running as administrator
    echo This is OK - we will continue anyway
    echo.
) else (
    echo [OK] Running as administrator
)
echo.
pause

echo ============================================================
echo  Step 1: Environment Check
echo ============================================================
echo.

set "ENV_OK=1"

echo [Check 1] Python 3.11+
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not installed
    echo Please install Python 3.11+: https://www.python.org/downloads/
    set "ENV_OK=0"
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        echo [OK] Python %%i
    )
)

echo.
echo [Check 2] Node.js 18+
node --version >nul 2>&1
if errorlevel 1 (
    echo [X] Node.js not installed
    echo Please install Node.js 18+: https://nodejs.org/
    set "ENV_OK=0"
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do (
        echo [OK] Node.js %%i
    )
)

echo.
echo [Check 3] npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [X] npm not installed
    set "ENV_OK=0"
) else (
    for /f "tokens=1" %%i in ('npm --version 2^>^&1') do (
        echo [OK] npm %%i
    )
)

echo.
echo [Check 4] Git (optional)
git --version >nul 2>&1
if errorlevel 1 (
    echo [?] Git not installed - will use manual download
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do (
        echo [OK] Git %%i
    )
)

echo.
if "%ENV_OK%"=="0" (
    color 0C
    echo ============================================================
    echo  [ERROR] Environment Check FAILED
    echo ============================================================
    echo.
    echo Please install missing software and try again.
    echo.
    pause
    exit /b 1
)

color 0A
echo [SUCCESS] All environment checks passed!
echo.
pause

:: Set working directory
set "WORK_DIR=%USERPROFILE%\KOOK-Build"
set "SOURCE_DIR=%WORK_DIR%\CSBJJWT"

echo.
echo ============================================================
echo  Step 2: Prepare Working Directory
echo ============================================================
echo.
echo Working directory: %WORK_DIR%
echo.

if exist "%WORK_DIR%" (
    echo [INFO] Working directory already exists
    echo.
    echo What would you like to do?
    echo   1 = Delete and start fresh (Recommended)
    echo   2 = Keep existing files
    echo   3 = Exit
    echo.
    set /p CHOICE="Enter your choice (1-3): "
    
    if "!CHOICE!"=="3" (
        echo Exiting...
        pause
        exit /b 0
    )
    
    if "!CHOICE!"=="1" (
        echo.
        echo Deleting old files...
        rd /s /q "%WORK_DIR%" 2>nul
        timeout /t 2 >nul
        echo [OK] Old files deleted
    )
)

echo.
if not exist "%WORK_DIR%" (
    echo Creating working directory...
    mkdir "%WORK_DIR%"
    if errorlevel 1 (
        echo [ERROR] Cannot create directory
        pause
        exit /b 1
    )
)

cd /d "%WORK_DIR%"
echo [OK] Working directory ready: %CD%
echo.
pause

echo ============================================================
echo  Step 3: Download Source Code
echo ============================================================
echo.

if exist "%SOURCE_DIR%" (
    echo [OK] Source code already exists, skipping download
    cd /d "%SOURCE_DIR%"
    goto :after_download
)

git --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Git not found
    echo.
    echo Manual download required:
    echo   1. Open browser and visit:
    echo      https://github.com/gfchfjh/CSBJJWT/archive/refs/heads/main.zip
    echo   2. Download the ZIP file
    echo   3. Extract it to: %WORK_DIR%
    echo   4. Rename the extracted folder to: CSBJJWT
    echo.
    echo Press any key after you have completed these steps...
    pause
    goto :check_source
)

echo Downloading source code from GitHub...
echo Repository: https://github.com/gfchfjh/CSBJJWT.git
echo This may take 2-5 minutes depending on your internet speed...
echo.

git clone https://github.com/gfchfjh/CSBJJWT.git

if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] Git clone failed
    echo.
    echo Please try manual download:
    echo   https://github.com/gfchfjh/CSBJJWT/archive/refs/heads/main.zip
    echo.
    pause
    exit /b 1
)

:check_source
if not exist "%SOURCE_DIR%" (
    color 0C
    echo [ERROR] Source directory not found: %SOURCE_DIR%
    echo.
    pause
    exit /b 1
)

cd /d "%SOURCE_DIR%"

:after_download
echo [OK] Source code ready
echo Current directory: %CD%
echo.
pause

echo ============================================================
echo  Step 4: Apply Fix Patch
echo ============================================================
echo.
echo Fixing PyInstaller configuration...
echo.

if not exist "build\pyinstaller.spec" (
    echo [ERROR] Cannot find build\pyinstaller.spec
    echo Current directory: %CD%
    dir build\
    pause
    exit /b 1
)

python -c "import os; file='build/pyinstaller.spec'; content=open(file,encoding='utf-8').read(); content=content.replace(\"name='kook-forwarder-backend'\",\"name='KOOKForwarder'\"); open(file,'w',encoding='utf-8').write(content)"

if errorlevel 1 (
    echo [WARNING] Automatic fix failed
    echo You may need to manually edit build\pyinstaller.spec
    echo.
    pause
) else (
    echo [OK] PyInstaller config fixed
)
echo.
pause

echo ============================================================
echo  Step 5: Install Python Dependencies
echo ============================================================
echo.
echo This will take 5-10 minutes...
echo Installing packages: FastAPI, Playwright, Redis, etc.
echo.

cd /d "%SOURCE_DIR%\backend"

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        color 0C
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo Activating virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Cannot find venv\Scripts\activate.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing requirements (this is the long part)...
pip install -r requirements.txt

if errorlevel 1 (
    color 0C
    echo [ERROR] Requirements installation failed
    pause
    exit /b 1
)

echo.
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo [OK] All Python dependencies installed
pause

echo ============================================================
echo  Step 6: Build Backend Executable
echo ============================================================
echo.
echo This will take 5-10 minutes...
echo PyInstaller is analyzing and packaging the backend...
echo.

cd /d "%SOURCE_DIR%"

if exist "dist\KOOKForwarder" (
    echo Cleaning old build...
    rd /s /q "dist\KOOKForwarder" 2>nul
)

echo Running PyInstaller...
pyinstaller build\pyinstaller.spec --clean

if errorlevel 1 (
    color 0C
    echo [ERROR] PyInstaller failed
    pause
    exit /b 1
)

if not exist "dist\KOOKForwarder\KOOKForwarder.exe" (
    color 0C
    echo [ERROR] Backend executable not found
    echo Expected: dist\KOOKForwarder\KOOKForwarder.exe
    pause
    exit /b 1
)

echo [OK] Backend built successfully
echo Location: %CD%\dist\KOOKForwarder\KOOKForwarder.exe
pause

echo ============================================================
echo  Step 7: Install Frontend Dependencies
echo ============================================================
echo.
echo This will take 5-10 minutes...
echo Installing Vue, Electron, and other packages...
echo.

cd /d "%SOURCE_DIR%\frontend"

if not exist "node_modules" (
    echo Running npm install...
    call npm install
    if errorlevel 1 (
        color 0C
        echo [ERROR] npm install failed
        pause
        exit /b 1
    )
) else (
    echo [OK] node_modules already exists
)

echo [OK] Frontend dependencies installed
pause

echo ============================================================
echo  Step 8: Build Electron Application
echo ============================================================
echo.
echo This will take 5-15 minutes...
echo Building Windows installer with electron-builder...
echo.

echo Running npm run electron:build:win...
call npm run electron:build:win

if errorlevel 1 (
    color 0C
    echo [ERROR] Electron build failed
    pause
    exit /b 1
)

echo [OK] Electron application built
pause

echo ============================================================
echo  Step 9: Locate Installer
echo ============================================================
echo.

cd /d "%SOURCE_DIR%"

echo Searching for installer...
set "INSTALLER_FOUND=0"
set "INSTALLER_PATH="

if exist "dist\*.exe" (
    for %%F in (dist\*.exe) do (
        set "INSTALLER_PATH=%%~fF"
        set "INSTALLER_FOUND=1"
        goto :found
    )
)

if exist "frontend\dist\*.exe" (
    for %%F in (frontend\dist\*.exe) do (
        set "INSTALLER_PATH=%%~fF"
        set "INSTALLER_FOUND=1"
        goto :found
    )
)

if exist "dist_electron\*.exe" (
    for %%F in (dist_electron\*.exe) do (
        set "INSTALLER_PATH=%%~fF"
        set "INSTALLER_FOUND=1"
        goto :found
    )
)

:found
if "%INSTALLER_FOUND%"=="1" (
    echo [OK] Installer found!
    echo.
    echo Location: %INSTALLER_PATH%
    echo.
    
    echo Copying to desktop...
    copy "%INSTALLER_PATH%" "%USERPROFILE%\Desktop\" >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Could not copy to desktop
    ) else (
        echo [OK] Installer copied to desktop
    )
) else (
    color 0E
    echo [WARNING] Installer not found automatically
    echo Please check these directories:
    echo   - %SOURCE_DIR%\dist
    echo   - %SOURCE_DIR%\frontend\dist
    echo   - %SOURCE_DIR%\dist_electron
)

echo.
pause

cls
color 0A
echo.
echo ============================================================
echo.
echo         SUCCESS! BUILD COMPLETE!
echo.
echo ============================================================
echo.

if "%INSTALLER_FOUND%"=="1" (
    echo Installer location:
    echo %INSTALLER_PATH%
    echo.
    echo Also copied to your desktop!
) else (
    echo Check the directories listed above for the installer
)

echo.
echo Next steps:
echo   1. Find the installer (.exe file)
echo   2. Double-click to install
echo   3. Launch KOOK Message Forwarder
echo   4. Configure your settings
echo.
echo ============================================================
echo.

if "%INSTALLER_FOUND%"=="1" (
    echo Would you like to open the installer folder? (Y/N)
    choice /c YN /n /m "Choose: "
    if errorlevel 1 if not errorlevel 2 (
        explorer /select,"%INSTALLER_PATH%"
    )
)

echo.
echo Thank you for using KOOK Message Forwarder!
echo.
pause
exit /b 0
