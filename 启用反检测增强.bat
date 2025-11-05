@echo off
chcp 65001 >nul
echo ========================================
echo 🛡️ 启用反检测增强功能
echo ========================================
echo.
echo ⚠️  重要提醒：
echo    1. 此功能无法保证100%%不被检测
echo    2. 请使用测试账号，不要用主号
echo    3. 建议低频使用，避免高峰时段
echo.
echo ========================================
echo.
choice /C YN /M "是否继续启用反检测增强功能"
if errorlevel 2 goto :cancel
if errorlevel 1 goto :enable

:enable
echo.
echo [1/3] 正在备份原始文件...
copy backend\app\kook\scraper.py backend\app\kook\scraper_backup.py >nul 2>&1
if exist backend\app\kook\scraper_backup.py (
    echo ✅ 备份完成
) else (
    echo ⚠️  备份失败，但继续执行...
)

echo.
echo [2/3] 正在检查增强文件...
if exist backend\app\kook\scraper_stealth.py (
    echo ✅ 增强文件存在
) else (
    echo ❌ 增强文件不存在！
    echo    请先确保 scraper_stealth.py 已添加到项目中
    goto :end
)

echo.
echo [3/3] 配置说明：
echo.
echo 📝 要启用增强功能，需要修改代码调用：
echo.
echo    原来：from app.kook.scraper import KookScraper
echo    改为：from app.kook.scraper_stealth import KookScraperStealth
echo.
echo 💡 建议使用方式：
echo    A. 快速增强：只改为有界面模式（headless=False）
echo    B. 完整增强：使用 scraper_stealth.py 替代 scraper.py
echo    C. 谨慎使用：保持原样，只降低使用频率
echo.
echo ========================================
echo.
choice /C ABC /M "选择您要使用的方案"
if errorlevel 3 goto :plan_c
if errorlevel 2 goto :plan_b
if errorlevel 1 goto :plan_a

:plan_a
echo.
echo ✅ 已选择方案A（快速增强）
echo.
echo 📝 请执行以下步骤：
echo    1. 打开 backend\app\kook\scraper.py
echo    2. 找到 headless=True
echo    3. 改为 headless=False
echo    4. 重启后端服务
echo.
goto :end

:plan_b
echo.
echo ✅ 已选择方案B（完整增强）
echo.
echo 📝 请执行以下步骤：
echo    1. 在需要使用的地方
echo    2. 将 from app.kook.scraper import KookScraper
echo    3. 改为 from app.kook.scraper_stealth import KookScraperStealth
echo    4. 将 KookScraper 改为 KookScraperStealth
echo    5. 重启后端服务
echo.
goto :end

:plan_c
echo.
echo ✅ 已选择方案C（谨慎使用）
echo.
echo 📝 使用建议：
echo    ✅ 每天最多运行4小时
echo    ✅ 避免晚上8-10点高峰期
echo    ✅ 每周重新登录导出Cookie
echo    ✅ 使用测试小号
echo    ✅ 控制转发消息数量
echo.
goto :end

:cancel
echo.
echo ❌ 已取消
goto :end

:end
echo.
echo ========================================
pause
