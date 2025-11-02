@echo off
echo ============================================================
echo KOOK Installer - Test Version
echo ============================================================
echo.
echo If you see this, the script is running!
echo.
pause

echo.
echo Testing Python...
python --version
echo.

echo Testing Node.js...
node --version
echo.

echo Testing npm...
npm --version
echo.

echo Testing Git...
git --version
echo.

echo ============================================================
echo Test Complete!
echo ============================================================
pause
