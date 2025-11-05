@echo off
chcp 65001 >nul
cls
echo ========================================
echo 🛡️ KOOK防封号增强已完成！
echo ========================================
echo.
echo ✅ 已应用最强反检测技术：
echo.
echo    1. ✅ JavaScript注入（隐藏自动化特征）
echo    2. ✅ 有界面浏览器模式
echo    3. ✅ 多User-Agent轮换
echo    4. ✅ 浏览器指纹伪装
echo    5. ✅ 人类行为模拟（鼠标+滚动）
echo    6. ✅ 分步访问+随机延迟
echo    7. ✅ 定期活动模拟
echo.
echo ========================================
echo ⚠️  重要提醒
echo ========================================
echo.
echo    1. 技术只能降低风险，不能消除
echo    2. 务必使用测试账号，不要用主号
echo    3. 严格控制使用时间（每天最多4小时）
echo    4. 避开高峰时段（晚上8-10点）
echo    5. 定期更新Cookie（每周1次）
echo.
echo ========================================
echo 📋 下一步操作
echo ========================================
echo.
echo [1] 查看详细使用指南（强烈推荐）
echo [2] 重启服务应用增强
echo [3] 直接开始使用
echo [X] 退出
echo.
choice /C 123X /N /M "请选择 [1/2/3/X]: "

if errorlevel 4 goto end
if errorlevel 3 goto start_use
if errorlevel 2 goto restart
if errorlevel 1 goto show_guide

:show_guide
cls
echo ========================================
echo 📖 正在打开使用指南...
echo ========================================
echo.
if exist 防封号使用指南-重要必读.md (
    start notepad 防封号使用指南-重要必读.md
    echo ✅ 文档已打开
    echo.
    echo 📋 请仔细阅读以下章节：
    echo    - 极其重要的警告
    echo    - 已实施的反检测措施
    echo    - 最关键的使用建议
    echo    - 最佳实践方案
    echo    - 立即行动清单
) else (
    echo ❌ 文档不存在
)
echo.
pause
goto end

:restart
cls
echo ========================================
echo 🔄 重启服务应用增强...
echo ========================================
echo.
echo [1/2] 停止当前服务...
call 停止所有服务.bat
echo.
echo [2/2] 启动增强版服务...
call 一键启动全部服务.bat
echo.
echo ========================================
echo ✅ 服务已重启，增强功能已生效！
echo ========================================
echo.
echo 💡 提示：
echo    - 您应该能看到浏览器窗口打开（有界面模式）
echo    - 观察浏览器的鼠标移动和页面滚动
echo    - 这些都是模拟人类行为的表现
echo.
pause
goto end

:start_use
cls
echo ========================================
echo 🚀 开始使用
echo ========================================
echo.
echo ⚠️  使用前最后检查：
echo.
echo    ☐ 我使用的是测试账号（不是主号）
echo    ☐ 我了解可能被封号的风险
echo    ☐ 我已阅读使用建议
echo    ☐ 当前不是高峰时段
echo    ☐ Cookie在7天内更新过
echo.
echo 如果以上全部确认，请按任意键继续...
pause >nul
echo.
echo ========================================
echo 📊 系统访问地址：
echo ========================================
echo.
echo    前端界面: http://localhost:5173
echo    后端API:  http://localhost:9527/docs
echo.
echo 正在打开前端界面...
start http://localhost:5173
echo.
echo ✅ 已打开，请开始使用！
echo.
pause
goto end

:end
echo.
echo ========================================
echo 📞 重要提醒
echo ========================================
echo.
echo    如需查看使用指南: 查看防封号指南.bat
echo    如需重启服务: 停止所有服务.bat + 一键启动全部服务.bat
echo    如需测试系统: 一键测试系统.bat
echo.
echo ⚠️  请务必遵守使用建议，严格控制频率！
echo.
pause
