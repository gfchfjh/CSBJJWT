@echo off 
cd /d "%%~dp0backend" 
call venv\Scripts\activate.bat 
start /MIN cmd /k "python -m app.main" 
timeout /t 15 /nobreak >nul 
start http://127.0.0.1:9527 
pause
