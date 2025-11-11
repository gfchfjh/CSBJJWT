@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 🎯 KOOK消息转发系统 - 一键全面测试
echo ========================================
echo.
echo 本脚本将依次执行:
echo   1. 环境检查
echo   2. 数据库检查
echo   3. Redis检查
echo   4. Cookie功能验证
echo   5. 端到端测试准备
echo   6. 系统健康监控（5分钟）
echo   7. 生成完整测试报告
echo.
echo 预计耗时: 约20分钟
echo.
pause

cd /d %~dp0
call venv\Scripts\activate.bat

echo.
echo ========================================
echo [1/7] 环境检查
echo ========================================
python --version
if errorlevel 1 python3 --version
node --version
git --version
echo ✅ 环境检查完成

echo.
echo ========================================
echo [2/7] 数据库检查
echo ========================================
python scripts\check_database.py
if errorlevel 1 python3 scripts\check_database.py
echo ✅ 数据库检查完成

echo.
echo ========================================
echo [3/7] Redis检查
echo ========================================
python scripts\test_redis.py
if errorlevel 1 python3 scripts\test_redis.py
echo ℹ️  Redis检查完成（如果失败，系统会使用内置Redis）

echo.
echo ========================================
echo [4/7] Cookie功能验证
echo ========================================
python scripts\verify_cookie_storage.py
if errorlevel 1 python3 scripts\verify_cookie_storage.py
echo ✅ Cookie验证完成

echo.
echo ========================================
echo [5/7] 端到端测试准备检查
echo ========================================
python scripts\e2e_test_preparation.py
if errorlevel 1 python3 scripts\e2e_test_preparation.py
echo ✅ 准备检查完成

echo.
echo ========================================
echo [6/7] 系统健康监控（5分钟）
echo ========================================
echo ℹ️  将进行5分钟持续监控...
echo ℹ️  可以按 Ctrl+C 跳过此步骤
python scripts\monitor_system_health.py
if errorlevel 1 python3 scripts\monitor_system_health.py
echo ✅ 健康监控完成

echo.
echo ========================================
echo [7/7] 生成完整测试报告
echo ========================================
python scripts\generate_test_report.py
if errorlevel 1 python3 scripts\generate_test_report.py
echo ✅ 报告生成完成

echo.
echo ========================================
echo 🎉 所有测试完成！
echo ========================================
echo.
echo 报告位置: %USERPROFILE%\Documents\KookForwarder\data\reports\
echo.
pause
