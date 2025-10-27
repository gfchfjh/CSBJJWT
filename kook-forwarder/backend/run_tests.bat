@echo off
REM 运行测试脚本 (Windows)

echo ======================================
echo KOOK消息转发系统 - 测试套件
echo ======================================

REM 检查是否安装pytest
pytest --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pytest未安装，正在安装测试依赖...
    pip install -r requirements-dev.txt
)

REM 运行测试
echo.
echo 🧪 运行单元测试...
echo.

pytest tests\ -v

REM 生成覆盖率报告
echo.
echo 📊 生成覆盖率报告...
echo.

pytest tests\ --cov=app --cov-report=term-missing --cov-report=html

echo.
echo ======================================
echo ✅ 测试完成！
echo ======================================
echo.
echo 📈 覆盖率报告已生成到: htmlcov\index.html
echo.
echo 运行以下命令查看详细报告：
echo   start htmlcov\index.html
echo.

pause
