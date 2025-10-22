@echo off
REM KOOK消息转发系统 - 完整压力测试运行脚本 (Windows)

echo ==========================================
echo   KOOK消息转发系统 - 完整压力测试
echo ==========================================
echo.
echo 测试时间: %date% %time%
echo.

REM 检查Python环境
echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装
    pause
    exit /b 1
)
echo ✅ Python已安装

REM 检查依赖包
echo 检查依赖包...
python -c "import aiohttp, redis, PIL" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  部分依赖包未安装，尝试安装...
    pip install aiohttp redis pillow
)

REM 检查后端服务
echo 检查后端服务状态...
curl -s http://127.0.0.1:9527/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  后端服务未运行
    echo 请先启动后端服务: cd backend ^&^& python -m app.main
    echo 继续执行测试（某些测试可能会失败）...
) else (
    echo ✅ 后端服务运行正常
)

REM 检查Redis服务
echo 检查Redis服务状态...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Redis服务未运行
    echo 请先启动Redis服务
    echo 继续执行测试（某些测试可能会失败）...
) else (
    echo ✅ Redis服务运行正常
)

echo.
echo ==========================================
echo   开始执行压力测试
echo ==========================================
echo.

REM 创建测试结果目录
if not exist test_results mkdir test_results

REM 1. 运行原有的压力测试
echo [1/3] 运行原有压力测试...
python stress_test.py 2>&1 | tee test_results\stress_test.log
if %errorlevel% equ 0 (
    echo ✅ 原有压力测试完成
) else (
    echo ❌ 原有压力测试失败
)
echo.

REM 2. 运行全面压力测试
echo [2/3] 运行全面压力测试...
python comprehensive_stress_test.py 2>&1 | tee test_results\comprehensive_stress_test.log
if %errorlevel% equ 0 (
    echo ✅ 全面压力测试完成
) else (
    echo ❌ 全面压力测试失败
)
echo.

REM 3. 运行模块专项测试
echo [3/3] 运行模块专项测试...
python module_specific_stress_test.py 2>&1 | tee test_results\module_specific_stress_test.log
if %errorlevel% equ 0 (
    echo ✅ 模块专项测试完成
) else (
    echo ❌ 模块专项测试失败
)
echo.

REM 移动报告文件到结果目录
echo 整理测试报告...
move /Y stress_test_report.json test_results\ >nul 2>&1
move /Y 压力测试报告.md test_results\ >nul 2>&1
move /Y comprehensive_stress_test_report.json test_results\ >nul 2>&1
move /Y 全面压力测试报告.md test_results\ >nul 2>&1
move /Y module_stress_test_report.json test_results\ >nul 2>&1

echo.
echo ==========================================
echo   测试完成
echo ==========================================
echo.
echo 测试报告保存在: .\test_results\
echo.
echo 生成的报告文件:
dir /B test_results\*.json test_results\*.md test_results\*.log 2>nul
echo.
echo ✅ 所有压力测试执行完毕！
echo.
pause
