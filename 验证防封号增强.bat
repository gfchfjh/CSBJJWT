@echo off
chcp 65001 >nul
cls
echo ========================================
echo 🔍 防封号增强验证工具
echo ========================================
echo.
echo 正在检查增强是否已生效...
echo.

echo ========================================
echo [1/5] 检查代码文件是否存在
echo ========================================
if exist backend\app\kook\scraper.py (
    echo ✅ scraper.py 存在
) else (
    echo ❌ scraper.py 不存在
    goto error
)
echo.

echo ========================================
echo [2/5] 检查关键配置 - headless模式
echo ========================================
findstr /C:"headless=False" backend\app\kook\scraper.py >nul 2>&1
if %errorlevel%==0 (
    echo ✅ 已配置为有界面模式 ^(headless=False^)
    set "check1=OK"
) else (
    echo ❌ 未配置有界面模式 ^(仍为headless=True^)
    set "check1=FAIL"
)
echo.

echo ========================================
echo [3/5] 检查关键配置 - JavaScript注入
echo ========================================
findstr /C:"navigator.webdriver" backend\app\kook\scraper.py >nul 2>&1
if %errorlevel%==0 (
    echo ✅ 已启用JavaScript反检测
    set "check2=OK"
) else (
    echo ❌ 未找到JavaScript反检测代码
    set "check2=FAIL"
)
echo.

echo ========================================
echo [4/5] 检查关键配置 - 人类行为模拟
echo ========================================
findstr /C:"simulate_human_behavior" backend\app\kook\scraper.py >nul 2>&1
if %errorlevel%==0 (
    echo ✅ 已启用人类行为模拟
    set "check3=OK"
) else (
    echo ❌ 未找到人类行为模拟代码
    set "check3=FAIL"
)
echo.

echo ========================================
echo [5/5] 检查关键配置 - User-Agent轮换
echo ========================================
findstr /C:"user_agents = [" backend\app\kook\scraper.py >nul 2>&1
if %errorlevel%==0 (
    echo ✅ 已启用User-Agent轮换
    set "check4=OK"
) else (
    echo ❌ 未找到User-Agent轮换代码
    set "check4=FAIL"
)
echo.

echo ========================================
echo 📊 验证结果汇总
echo ========================================
echo.
if "%check1%"=="OK" (echo ✅ 1. 有界面模式) else (echo ❌ 1. 有界面模式)
if "%check2%"=="OK" (echo ✅ 2. JavaScript反检测) else (echo ❌ 2. JavaScript反检测)
if "%check3%"=="OK" (echo ✅ 3. 人类行为模拟) else (echo ❌ 3. 人类行为模拟)
if "%check4%"=="OK" (echo ✅ 4. User-Agent轮换) else (echo ❌ 4. User-Agent轮换)
echo.

if "%check1%%check2%%check3%%check4%"=="OKOKOKOK" (
    echo ========================================
    echo ✅✅✅ 所有增强已生效！✅✅✅
    echo ========================================
    echo.
    echo 💡 下一步：
    echo    1. 访问前端: http://localhost:5173
    echo    2. 添加/启动KOOK账号抓取
    echo    3. 观察是否有浏览器窗口弹出
    echo    4. 观察鼠标自动移动和页面滚动
    echo.
    echo 如果看到浏览器窗口和自动行为 → 完美！✅
    echo 如果没有 → 请查看后端日志排查问题
) else (
    echo ========================================
    echo ⚠️  部分增强未生效！
    echo ========================================
    echo.
    echo 💡 可能的原因：
    echo    1. Git pull未成功，代码未更新
    echo    2. 文件编码问题
    echo    3. 服务未重启
    echo.
    echo 💡 解决方法：
    echo    1. 停止服务: 停止所有服务.bat
    echo    2. 手动下载最新代码
    echo    3. 重新启动: 一键启动全部服务.bat
    echo.
    echo 📞 需要帮助？告诉我验证结果！
)
echo.
goto end

:error
echo ========================================
echo ❌ 检查失败
echo ========================================
echo.
echo 请确保在项目根目录执行此脚本！
echo 当前目录应该是: C:\Users\tanzu\Desktop\CSBJJWT
echo.

:end
echo ========================================
echo.
echo 是否查看 scraper.py 源代码？
choice /C YN /M "查看代码 [Y/N]"
if errorlevel 2 goto finish
if errorlevel 1 goto show_code

:show_code
notepad backend\app\kook\scraper.py
goto finish

:finish
echo.
pause
