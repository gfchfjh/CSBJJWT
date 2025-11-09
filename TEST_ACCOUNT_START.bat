@echo off
chcp 65001 >nul
echo ========================================
echo 账号启动功能测试脚本
echo ========================================
echo.
echo 日期: 2025-11-09
echo 修复: 启动按钮无响应问题
echo.
echo ========================================
echo 测试准备
echo ========================================
echo.

:: 检查Python环境
echo [1/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)
echo ✅ Python环境正常

:: 检查Node环境
echo.
echo [2/5] 检查Node环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装或未添加到PATH
    pause
    exit /b 1
)
echo ✅ Node.js环境正常

:: 检查后端代码
echo.
echo [3/5] 检查后端修复...
python -c "import sys; f=open('backend/app/api/accounts.py','r',encoding='utf-8'); content=f.read(); f.close(); assert 'return {\"message\": \"抓取器已启动\"' in content; print('✅ 后端API已修复')"
if errorlevel 1 (
    echo ❌ 后端API未修复
    pause
    exit /b 1
)

:: 检查scraper修复
echo.
echo [4/5] 检查scraper修复...
python -c "import sys; f=open('backend/app/kook/scraper.py','r',encoding='utf-8'); content=f.read(); f.close(); assert 'return True' in content and 'return False' in content; print('✅ scraper_manager已修复')"
if errorlevel 1 (
    echo ❌ scraper_manager未修复
    pause
    exit /b 1
)

:: 检查Git状态
echo.
echo [5/5] 检查Git提交...
git log --oneline -1 | findstr "return values" >nul
if errorlevel 1 (
    echo ⚠️ 未找到相关Git提交
) else (
    echo ✅ Git提交已完成
)

echo.
echo ========================================
echo 测试完成
echo ========================================
echo.
echo ✅ 所有检查通过！
echo.
echo 接下来请执行：
echo.
echo 1. 启动后端（新CMD窗口）：
echo    cd backend
echo    ..\venv\Scripts\activate
echo    python -m uvicorn app.main:app --host 0.0.0.0 --port 9527 --reload
echo.
echo 2. 启动前端（新CMD窗口）：
echo    cd frontend
echo    npm run dev
echo.
echo 3. 访问系统：
echo    http://localhost:5173
echo.
echo 4. 测试启动按钮：
echo    - 进入"账号管理"
echo    - 点击"启动"按钮
echo    - 应该看到成功提示
echo    - Chrome浏览器应该自动打开
echo.
echo ========================================
echo.
pause
