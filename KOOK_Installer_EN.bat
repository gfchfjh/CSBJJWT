@echo off
setlocal enabledelayedexpansion
title KOOK Message Forwarder - One-Click Installer

color 0B
echo.
echo ============================================================
echo.
echo      KOOK Message Forwarder - One-Click Installer
echo.
echo      Version 2.0
echo.
echo ============================================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0E
    echo WARNING: Administrator rights recommended
    echo.
    echo Right-click this script and select "Run as administrator"
    echo.
    echo Continue anyway? (Y/N)
    choice /c YN /n /m "Choose: "
    if errorlevel 2 exit /b 1
)

echo ============================================================
echo  Step 1: Environment Check
echo ============================================================
echo.

set "ENV_OK=1"

echo [Check 1] Python 3.11+
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [X] Python not installed
    echo     Install Python 3.11+: https://www.python.org/downloads/
    set "ENV_OK=0"
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        echo [OK] Python %%i
    )
)

echo [Check 2] Node.js 18+
node --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [X] Node.js not installed
    echo     Install Node.js 18+: https://nodejs.org/
    set "ENV_OK=0"
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do (
        echo [OK] Node.js %%i
    )
)

echo [Check 3] npm
npm --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [X] npm not installed
    set "ENV_OK=0"
) else (
    for /f "tokens=1" %%i in ('npm --version 2^>^&1') do (
        echo [OK] npm %%i
    )
)

echo [Check 4] Git
git --version >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [?] Git not installed (will use backup method)
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do (
        echo [OK] Git %%i
    )
)

if "%ENV_OK%"=="0" (
    echo.
    color 0C
    echo ============================================================
    echo  Environment Check FAILED
    echo ============================================================
    echo.
    echo Please install missing software and try again.
    pause
    exit /b 1
)

echo.
color 0A
echo [OK] Environment check passed!
echo.
timeout /t 2 >nul

:: Set working directory
set "WORK_DIR=%USERPROFILE%\KOOK-Build"
set "SOURCE_DIR=%WORK_DIR%\CSBJJWT"

echo ============================================================
echo  Step 2: Prepare Working Directory
echo ============================================================
echo.
echo Working directory: %WORK_DIR%
echo.

if exist "%WORK_DIR%" (
    echo Existing working directory detected.
    echo.
    echo Options:
    echo   [1] Delete old files and start fresh (Recommended)
    echo   [2] Continue with existing files
    echo   [3] Exit
    echo.
    choice /c 123 /n /m "Choose (1-3): "
    
    if errorlevel 3 exit /b 0
    if errorlevel 2 goto :skip_clean
    if errorlevel 1 (
        echo.
        echo Cleaning old files...
        rd /s /q "%WORK_DIR%" 2>nul
        timeout /t 1 >nul
    )
)

:skip_clean
if not exist "%WORK_DIR%" (
    echo Creating working directory...
    mkdir "%WORK_DIR%"
)
cd /d "%WORK_DIR%"
echo [OK] Working directory ready
echo.

echo ============================================================
echo  Step 3: Download Source Code
echo ============================================================
echo.

if exist "%SOURCE_DIR%" (
    echo [OK] Source code exists, skipping download
) else (
    git --version >nul 2>&1
    if errorlevel 1 (
        echo Git not detected, using backup download method...
        echo.
        echo Please manually:
        echo   1. Visit: https://github.com/gfchfjh/CSBJJWT/archive/refs/heads/main.zip
        echo   2. Download and extract to: %WORK_DIR%
        echo   3. Make sure folder name is: CSBJJWT
        echo.
        pause
    ) else (
        echo Cloning from GitHub...
        echo Repository: https://github.com/gfchfjh/CSBJJWT.git
        echo.
        git clone https://github.com/gfchfjh/CSBJJWT.git
        if errorlevel 1 (
            color 0C
            echo.
            echo [X] Clone failed
            echo.
            echo Possible reasons:
            echo   - Network connection issue
            echo   - GitHub access restricted
            echo.
            echo Solutions:
            echo   1. Check network connection
            echo   2. Or manually download: https://github.com/gfchfjh/CSBJJWT/archive/refs/heads/main.zip
            echo   3. Extract to: %WORK_DIR%\CSBJJWT
            echo.
            pause
            exit /b 1
        )
    )
)

if not exist "%SOURCE_DIR%" (
    color 0C
    echo [X] Source directory not found
    pause
    exit /b 1
)

cd /d "%SOURCE_DIR%"
echo [OK] Source code ready
echo.

echo ============================================================
echo  Step 4: Apply Fix Patch
echo ============================================================
echo.
echo Fixing PyInstaller config...

python -c "import os; file='build/pyinstaller.spec'; content=open(file,encoding='utf-8').read(); content=content.replace(\"name='kook-forwarder-backend'\",\"name='KOOKForwarder'\"); open(file,'w',encoding='utf-8').write(content)"

if errorlevel 1 (
    color 0E
    echo [!] Auto-fix failed, trying manual fix...
    
    if exist "build\pyinstaller.spec" (
        echo Please manually edit build\pyinstaller.spec
        echo Change all name='kook-forwarder-backend' to name='KOOKForwarder'
        pause
    ) else (
        echo [X] Cannot find pyinstaller.spec file
        pause
        exit /b 1
    )
) else (
    echo [OK] PyInstaller config fixed
)
echo.

echo ============================================================
echo  Step 5: Install Python Dependencies
echo ============================================================
echo.
echo This may take 5-10 minutes...
echo.

cd /d "%SOURCE_DIR%\backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        color 0C
        echo [X] Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

if errorlevel 1 (
    color 0C
    echo [X] Dependency installation failed
    pause
    exit /b 1
)

echo [OK] Python dependencies installed
echo.

echo ============================================================
echo  Step 6: Build Backend Executable
echo ============================================================
echo.
echo This may take 5-10 minutes...
echo.

cd /d "%SOURCE_DIR%"

if exist "dist\KOOKForwarder" (
    echo Cleaning old build files...
    rd /s /q "dist\KOOKForwarder" 2>nul
)

echo Packaging backend with PyInstaller...
pyinstaller build\pyinstaller.spec --clean

if errorlevel 1 (
    color 0C
    echo [X] Backend packaging failed
    pause
    exit /b 1
)

if not exist "dist\KOOKForwarder\KOOKForwarder.exe" (
    color 0C
    echo [X] Backend executable not generated
    pause
    exit /b 1
)

echo [OK] Backend build complete
echo.

echo ============================================================
echo  Step 7: Install Frontend Dependencies
echo ============================================================
echo.
echo This may take 5-10 minutes...
echo.

cd /d "%SOURCE_DIR%\frontend"

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
    if errorlevel 1 (
        color 0C
        echo [X] Frontend dependency installation failed
        pause
        exit /b 1
    )
) else (
    echo [OK] Frontend dependencies exist
)

echo [OK] Frontend dependencies installed
echo.

echo ============================================================
echo  Step 8: Build Electron Application
echo ============================================================
echo.
echo This may take 5-15 minutes...
echo.

echo Building Windows installer...
call npm run electron:build:win

if errorlevel 1 (
    color 0C
    echo [X] Electron packaging failed
    pause
    exit /b 1
)

echo [OK] Electron application built
echo.

echo ============================================================
echo  Step 9: Find Installer
echo ============================================================
echo.

cd /d "%SOURCE_DIR%"

:: Find generated installer
set "INSTALLER_FOUND=0"
set "INSTALLER_PATH="

if exist "dist\*.exe" (
    for %%F in (dist\*.exe) do (
        set "INSTALLER_PATH=%%~fF"
        set "INSTALLER_FOUND=1"
        goto :found_installer
    )
)

if exist "frontend\dist\*.exe" (
    for %%F in (frontend\dist\*.exe) do (
        set "INSTALLER_PATH=%%~fF"
        set "INSTALLER_FOUND=1"
        goto :found_installer
    )
)

if exist "dist_electron\*.exe" (
    for %%F in (dist_electron\*.exe) do (
        set "INSTALLER_PATH=%%~fF"
        set "INSTALLER_FOUND=1"
        goto :found_installer
    )
)

:found_installer

if "%INSTALLER_FOUND%"=="1" (
    echo [OK] Found installer
    echo.
    echo Installer location:
    echo %INSTALLER_PATH%
    echo.
    
    :: Copy to desktop
    echo Copying installer to desktop...
    copy "%INSTALLER_PATH%" "%USERPROFILE%\Desktop\" >nul
    if errorlevel 1 (
        echo [!] Cannot copy to desktop, but file is available at above path
    ) else (
        echo [OK] Installer copied to desktop
    )
) else (
    color 0E
    echo [!] Installer not found
    echo     Please manually check .exe files in:
    echo     - %SOURCE_DIR%\dist
    echo     - %SOURCE_DIR%\frontend\dist
    echo     - %SOURCE_DIR%\dist_electron
)

echo.
echo ============================================================
color 0A
echo.
echo   SUCCESS! BUILD COMPLETE!
echo.
echo ============================================================
echo.
echo  Build completed successfully!
echo.
echo  Installer ready
echo  Location: %INSTALLER_PATH%
echo  Desktop copy available
echo.
echo  Next steps:
echo    1. Double-click the installer
echo    2. Follow installation wizard
echo    3. Launch KOOK Message Forwarder
echo    4. Configure settings on first run
echo.
echo ============================================================
echo.

:: Ask to open file location
echo Open installer folder? (Y/N)
choice /c YN /n /m "Choose: "
if errorlevel 2 goto :end
if errorlevel 1 (
    if "%INSTALLER_FOUND%"=="1" (
        explorer /select,"%INSTALLER_PATH%"
    ) else (
        explorer "%SOURCE_DIR%\dist"
    )
)

:end
echo.
echo Thank you for using!
echo.
pause
exit /b 0
