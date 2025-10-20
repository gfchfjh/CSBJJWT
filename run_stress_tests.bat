@echo off
chcp 65001 >nul
echo =========================================
echo  KOOK消息转发系统 - 压力测试执行脚本
echo =========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装
    pause
    exit /b 1
)

echo ✅ Python已安装

REM 检查后端服务
echo.
echo 检查后端服务...
curl -s http://127.0.0.1:9527/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 后端服务运行中
) else (
    echo ⚠️  后端服务未运行
    echo 请先在另一个终端启动后端服务: cd backend ^&^& python -m app.main
    pause
    exit /b 1
)

echo.
echo =========================================
echo  选择测试类型
echo =========================================
echo 1. 基础压力测试 (7个测试, 约3-5分钟)
echo 2. 全面压力测试 (7个测试, 约15-20分钟)
echo 3. 两者都运行 (14个测试, 约20-25分钟)
echo.
set /p choice=请选择 [1-3]: 

if "%choice%"=="1" (
    echo.
    echo 运行基础压力测试...
    python stress_test.py
) else if "%choice%"=="2" (
    echo.
    echo 运行全面压力测试...
    python comprehensive_stress_test.py
) else if "%choice%"=="3" (
    echo.
    echo 先运行基础压力测试...
    python stress_test.py
    echo.
    echo =========================================
    echo.
    echo 现在运行全面压力测试...
    python comprehensive_stress_test.py
) else (
    echo 无效选择，退出
    pause
    exit /b 1
)

echo.
echo =========================================
echo  测试完成！
echo =========================================
echo.
echo 测试报告位置：
echo   • 基础测试: ./压力测试报告.md
echo   • 全面测试: ./comprehensive_stress_test_report.md
echo.
echo JSON结果：
echo   • 基础测试: ./stress_test_report.json
echo   • 全面测试: ./comprehensive_stress_test_results.json
echo.
pause
