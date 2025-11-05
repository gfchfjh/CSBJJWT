@echo off
chcp 65001 >nul
echo ========================================
echo 正在创建反检测增强文件...
echo ========================================
echo.

echo [1/3] 创建文档文件...
(
echo # KOOK消息转发系统 - 反检测增强说明
echo.
echo **版本**: v18.0.3 Enhanced
echo **更新日期**: 2025-11-05
echo **风险等级**: ⚠️ 中高风险
echo.
echo ---
echo.
echo ## ⚠️ 重要警告
echo.
echo 1. ❌ **没有100%%不被检测的方法**
echo 2. ⚠️ **所有增强措施只能降低风险，不能消除风险**
echo 3. ⚠️ **使用此工具可能违反KOOK服务条款**
echo 4. ⚠️ **您需要自行承担账号被封的风险**
echo 5. ✅ **建议仅用于测试账号，不要用主号**
echo.
echo ---
echo.
echo ## 📊 项目已实现的措施
echo.
echo ### 基础反检测 ✅
echo - 禁用自动化控制特征
echo - 使用真实User-Agent
echo - Cookie登录（避免账号密码）
echo.
echo **效果**：可以绕过基础的自动化检测
echo.
echo ---
echo.
echo ## 🚀 可增强的9大措施
echo.
echo ### 1. JavaScript注入反检测 ⭐⭐⭐⭐⭐
echo - 删除webdriver标记
echo - 伪装chrome对象
echo - 效果：通过大部分JS检测
echo - 风险：低-中
echo.
echo ### 2. 随机延迟模拟人类 ⭐⭐⭐⭐
echo - 所有操作添加随机延迟
echo - 避免机械化规律
echo - 风险：低
echo.
echo ### 3. 鼠标轨迹模拟 ⭐⭐⭐
echo - 随机移动鼠标和滚动
echo - 模拟真实交互
echo - 风险：低-中
echo.
echo ### 4. 有界面模式 ⭐⭐⭐⭐ ^(最简单^)
echo - headless=False
echo - 真实浏览器环境
echo - 风险：低
echo.
echo ### 5. 请求头随机化 ⭐⭐⭐
echo - 使用User-Agent池
echo - 避免单一特征
echo - 风险：低
echo.
echo ### 6. Cookie定期刷新 ⭐⭐⭐⭐
echo - 每周重新登录
echo - 保持会话活跃
echo - 风险：低
echo.
echo ### 7. 降低请求频率 ⭐⭐⭐⭐⭐ ^(最有效^)
echo - 限制操作频率
echo - 避免触发频率限制
echo - 风险：低
echo.
echo ### 8. IP代理轮换 ⭐⭐⭐
echo - 使用代理IP
echo - 需要购买服务
echo - 风险：中
echo.
echo ### 9. 浏览器指纹伪装 ⭐⭐⭐⭐
echo - 完整上下文配置
echo - 伪装设备信息
echo - 风险：中
echo.
echo ---
echo.
echo ## 🎯 推荐方案
echo.
echo ### 方案A: 低风险配置 ^(推荐^) ⭐⭐⭐⭐⭐
echo - Cookie登录
echo - 真实User-Agent
echo - 随机延迟
echo - 降低频率
echo.
echo ### 方案B: 中等加强配置 ⭐⭐⭐⭐
echo - 方案A所有措施
echo - JavaScript注入
echo - 鼠标轨迹模拟
echo - 有界面模式
echo.
echo ### 方案C: 最强配置 ^(慎用^) ⭐⭐⭐
echo - 方案B所有措施
echo - IP代理轮换
echo - 指纹伪装
echo.
echo **注意：即使最强配置，仍有被检测风险！**
echo.
echo ---
echo.
echo ## 📋 立即可做的 ^(无需修改代码^)
echo.
echo ### 1. 降低使用频率
echo - 不要24小时运行
echo - 控制转发数量
echo - 避免高峰时段 ^(晚上8-10点^)
echo.
echo ### 2. 使用测试账号
echo - 注册新的小号
echo - 不用重要账号
echo - 观察一段时间
echo.
echo ### 3. Cookie定期更新
echo - 每周重新登录
echo - 重新导出Cookie
echo - 保持会话新鲜
echo.
echo ---
echo.
echo ## ⚠️ 最终建议
echo.
echo ### 技术角度
echo - ✅ 可以实现更多反检测措施
echo - ⚠️ 但不能保证100%%安全
echo.
echo ### 合规角度
echo - ❌ 使用自动化工具可能违反服务条款
echo - ⚠️ 即使技术上不被检测，仍可能违规
echo.
echo ### 风险角度
echo - 🔴 **主号**：高风险，不建议
echo - 🟡 **小号**：中风险，可测试
echo - 🟢 **官方API**：零风险，最推荐
echo.
echo ---
echo.
echo ## 🎯 具体实施建议
echo.
echo ### 方案A: 快速增强 ^(5分钟^)
echo 修改 backend\app\kook\scraper.py:
echo - 找到: headless=True
echo - 改为: headless=False
echo - 重启后端
echo.
echo ### 方案B: 完整增强 ^(15分钟^)
echo 使用增强版抓取器:
echo - 将 scraper.py 改为 scraper_stealth.py
echo - 包含所有反检测措施
echo.
echo ### 方案C: 谨慎使用 ^(推荐^)
echo 不修改代码，只改使用习惯:
echo - 每天最多运行4小时
echo - 避开高峰时段
echo - 用测试账号
echo - 定期更新Cookie
echo.
echo ---
echo.
echo 📞 **需要配置帮助？** 运行 启用反检测增强.bat
) > 反检测增强说明.md

echo ✅ 文档创建完成

echo.
echo [2/3] 创建查看文档工具...
(
echo @echo off
echo chcp 65001 ^>nul
echo cls
echo echo ========================================
echo echo 📖 KOOK反检测增强说明
echo echo ========================================
echo echo.
echo if exist 反检测增强说明.md ^(
echo     start notepad 反检测增强说明.md
echo     echo ✅ 文档已打开
echo ^) else ^(
echo     echo ❌ 文档文件不存在
echo ^)
echo echo.
echo pause
) > 查看反检测说明.bat

echo ✅ 查看工具创建完成

echo.
echo [3/3] 创建配置向导...
(
echo @echo off
echo chcp 65001 ^>nul
echo cls
echo echo ========================================
echo echo 🛡️ KOOK反检测增强配置向导
echo echo ========================================
echo echo.
echo echo ⚠️  重要提醒：
echo echo    1. 此功能无法保证100%%%%不被检测
echo echo    2. 请使用测试账号，不要用主号
echo echo    3. 建议低频使用，避免高峰时段
echo echo.
echo echo ========================================
echo echo 📋 可选方案：
echo echo ========================================
echo echo.
echo echo [A] 快速增强 - 改为有界面模式 ^(最简单^)
echo echo     修改1行代码：headless=False
echo echo     效果：⭐⭐⭐⭐ 风险：低
echo echo.
echo echo [B] 完整增强 - 使用增强版抓取器
echo echo     使用 scraper_stealth.py
echo echo     效果：⭐⭐⭐⭐⭐ 风险：低-中
echo echo.
echo echo [C] 谨慎使用 - 只改使用习惯 ^(推荐^)
echo echo     不修改代码，只降低使用频率
echo echo     效果：⭐⭐⭐⭐ 风险：最低
echo echo.
echo echo [X] 查看详细说明
echo echo.
echo choice /C ABCX /N /M "请选择 [A/B/C/X]: "
echo if errorlevel 4 goto show_doc
echo if errorlevel 3 goto plan_c
echo if errorlevel 2 goto plan_b
echo if errorlevel 1 goto plan_a
echo.
echo :plan_a
echo cls
echo echo ========================================
echo echo ✅ 方案A：快速增强
echo echo ========================================
echo echo.
echo echo 📝 修改步骤：
echo echo    1. 打开文件：backend\app\kook\scraper.py
echo echo    2. 搜索：headless=True
echo echo    3. 改为：headless=False
echo echo    4. 保存文件
echo echo    5. 重启后端服务
echo echo.
echo echo 💡 效果：使用真实浏览器窗口，更难被检测
echo echo.
echo goto end
echo.
echo :plan_b
echo cls
echo echo ========================================
echo echo ✅ 方案B：完整增强
echo echo ========================================
echo echo.
echo echo 📝 修改步骤：
echo echo    1. 确保文件存在：backend\app\kook\scraper_stealth.py
echo echo    2. 在使用的地方修改导入
echo echo    3. 重启服务
echo echo.
echo echo 💡 包含9种反检测措施，效果最强
echo echo.
echo goto end
echo.
echo :plan_c
echo cls
echo echo ========================================
echo echo ✅ 方案C：谨慎使用 ^(最推荐^)
echo echo ========================================
echo echo.
echo echo 📋 使用建议：
echo echo.
echo echo ✅ 1. 使用时间控制
echo echo       - 每天最多运行 4 小时
echo echo       - 分散到不同时段
echo echo.
echo echo ✅ 2. 避开高峰时段
echo echo       - 避免晚上 8-10 点
echo echo       - 选择深夜或凌晨
echo echo.
echo echo ✅ 3. Cookie定期更新
echo echo       - 每周重新登录KOOK
echo echo       - 重新导出Cookie
echo echo.
echo echo ✅ 4. 使用测试账号
echo echo       - 不要用主号
echo echo       - 注册新的小号测试
echo echo.
echo echo ✅ 5. 控制转发量
echo echo       - 每小时不超过50条消息
echo echo.
echo echo 💡 这是风险最低的方案！
echo echo.
echo goto end
echo.
echo :show_doc
echo cls
echo if exist 反检测增强说明.md ^(
echo     start notepad 反检测增强说明.md
echo     echo ✅ 已打开详细文档
echo ^) else ^(
echo     echo ❌ 文档不存在
echo ^)
echo goto end
echo.
echo :end
echo echo ========================================
echo pause
) > 启用反检测增强.bat

echo ✅ 配置向导创建完成

echo.
echo ========================================
echo ✅ 所有文件创建成功！
echo ========================================
echo.
echo 已创建以下文件：
echo   1. 反检测增强说明.md
echo   2. 查看反检测说明.bat
echo   3. 启用反检测增强.bat
echo.
echo 您现在可以运行：
echo   查看反检测说明.bat   - 查看详细文档
echo   启用反检测增强.bat   - 配置增强功能
echo.
pause
