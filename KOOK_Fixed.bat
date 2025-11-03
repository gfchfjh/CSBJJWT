@echo off
setlocal enabledelayedexpansion
title KOOK Message Forwarder - Installer

cls
echo ============================================================
echo      KOOK Message Forwarder - One-Click Installer
echo ============================================================
echo.
pause

echo.
echo Step 1: Environment Check
echo ============================================================
echo.

:: Check Python
echo Checking Python...
python --version 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)
echo [OK] Python check passed
echo.

:: Check Node.js
echo Checking Node.js...
node --version 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    pause
    exit /b 1
)
echo [OK] Node.js check passed
echo.

:: Check npm
echo Checking npm...
call npm --version 2>nul
if errorlevel 1 (
    echo [ERROR] npm not found!
    pause
    exit /b 1
)
echo [OK] npm check passed
echo.

:: Check Git
echo Checking Git...
git --version 2>nul
if errorlevel 1 (
    echo [WARNING] Git not found - manual download may be needed
) else (
    echo [OK] Git check passed
)
echo.

echo [SUCCESS] All required tools are available!
echo.
pause

:: Set directories
set "WORK_DIR=%USERPROFILE%\KOOK-Build"
set "SOURCE_DIR=%WORK_DIR%\CSBJJWT"

echo.
echo Step 2: Prepare Working Directory
echo ============================================================
echo.
echo Working directory: %WORK_DIR%
echo.

if exist "%WORK_DIR%" (
    echo Working directory already exists.
    echo.
    echo 1 = Delete and start fresh (Recommended)
    echo 2 = Keep existing files
    echo 3 = Exit
    echo.
    set /p "CHOICE=Enter your choice (1-3): "
    
    if "!CHOICE!"=="3" (
        echo Exiting...
        pause
        exit /b 0
    )
    
    if "!CHOICE!"=="1" (
        echo Deleting old files...
        rd /s /q "%WORK_DIR%" 2>nul
        echo [OK] Old files deleted
    )
)

echo.
if not exist "%WORK_DIR%" (
    echo Creating working directory...
    mkdir "%WORK_DIR%"
)
cd /d "%WORK_DIR%"
echo [OK] Working directory ready
echo.
pause

echo.
echo Step 3: Download Source Code
echo ============================================================
echo.

if exist "%SOURCE_DIR%" (
    echo [OK] Source code already exists
    cd /d "%SOURCE_DIR%"
    goto :after_download
)

git --version 2>nul
if errorlevel 1 (
    echo [ERROR] Git not found!
    echo.
    echo Please manually download:
    echo   https://github.com/gfchfjh/CSBJJWT/archive/refs/heads/main.zip
    echo.
    echo Extract to: %WORK_DIR%
    echo Rename folder to: CSBJJWT
    echo.
    pause
    goto :check_source
)

echo Downloading from GitHub...
echo This may take 2-5 minutes...
echo.
git clone https://github.com/gfchfjh/CSBJJWT.git

if errorlevel 1 (
    echo [ERROR] Download failed!
    pause
    exit /b 1
)

:check_source
if not exist "%SOURCE_DIR%" (
    echo [ERROR] Source code not found!
    pause
    exit /b 1
)

cd /d "%SOURCE_DIR%"

:after_download
echo [OK] Source code ready
echo.
pause

echo.
echo Step 4: Apply Fix
echo ============================================================
echo.

if not exist "build\pyinstaller.spec" (
    echo [ERROR] pyinstaller.spec not found!
    pause
    exit /b 1
)

echo Applying fix...
python -c "file='build/pyinstaller.spec'; content=open(file,encoding='utf-8').read(); content=content.replace(\"name='kook-forwarder-backend'\",\"name='KOOKForwarder'\"); open(file,'w',encoding='utf-8').write(content)"

if errorlevel 1 (
    echo [WARNING] Fix may have failed
) else (
    echo [OK] Fix applied
)
echo.
pause

echo.
echo Step 5: Install Python Dependencies
echo ============================================================
echo.
echo This will take 5-10 minutes...
echo.

cd /d "%SOURCE_DIR%\backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing requirements...
echo This is the long part - please wait...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Installation failed
    pause
    exit /b 1
)

echo.
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo [OK] Python dependencies installed
pause

echo.
echo Step 6: Build Backend
echo ============================================================
echo.
echo This will take 5-10 minutes...
echo.

cd /d "%SOURCE_DIR%"

if exist "dist\KOOKForwarder" (
    echo Cleaning old build...
    rd /s /q "dist\KOOKForwarder" 2>nul
)

echo Running PyInstaller...
pyinstaller build\pyinstaller.spec --clean

if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

if not exist "dist\KOOKForwarder\KOOKForwarder.exe" (
    echo [ERROR] Executable not found
    pause
    exit /b 1
)

echo [OK] Backend built successfully
pause

echo.
echo Step 7: Install Frontend Dependencies
echo ============================================================
echo.
echo This will take 5-10 minutes...
echo.

cd /d "%SOURCE_DIR%\frontend"

if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed
        pause
        exit /b 1
    )
)

echo [OK] Frontend dependencies installed
pause

echo.
echo Step 8: Build Electron Application
echo ============================================================
echo.
echo This will take 5-15 minutes...
echo.

echo Building Windows installer...
call npm run electron:build:win

if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo [OK] Electron app built
pause

echo.
echo Step 9: Find Installer
echo ============================================================
echo.

cd /d "%SOURCE_DIR%"

echo Searching for installer...
set "FOUND=0"

if exist "dist\*.exe" (
    for %%F in (dist\*.exe) do (
        set "INSTALLER=%%~fF"
        set "FOUND=1"
        goto :found_it
    )
)

if exist "frontend\dist\*.exe" (
    for %%F in (frontend\dist\*.exe) do (
        set "INSTALLER=%%~fF"
        set "FOUND=1"
        goto :found_it
    )
)

if exist "dist_electron\*.exe" (
    for %%F in (dist_electron\*.exe) do (
        set "INSTALLER=%%~fF"
        set "FOUND=1"
        goto :found_it
    )
)

:found_it
if "%FOUND%"=="1" (
    echo [OK] Installer found!
    echo.
    echo Location: %INSTALLER%
    echo.
    echo Copying to desktop...
    copy "%INSTALLER%" "%USERPROFILE%\Desktop\" >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Could not copy to desktop
    ) else (
        echo [OK] Copied to desktop
    )
) else (
    echo [WARNING] Installer not found
    echo Check these folders:
    echo   - %SOURCE_DIR%\dist
    echo   - %SOURCE_DIR%\frontend\dist
    echo   - %SOURCE_DIR%\dist_electron
)

echo.
pause

cls
echo.
echo ============================================================
echo              SUCCESS! BUILD COMPLETE!
echo ============================================================
echo.

if "%FOUND%"=="1" (
    echo Installer location: %INSTALLER%
    echo.
    echo Also available on your desktop!
    echo.
    echo Open installer folder? (Y/N)
    choice /c YN /n
    if errorlevel 1 if not errorlevel 2 (
        explorer /select,"%INSTALLER%"
    )
) else (
    echo Please check the folders listed above
)

echo.
echo Thank you for using KOOK Message Forwarder!
echo.
pause
exit /b 0
