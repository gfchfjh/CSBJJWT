# KOOK转发系统 - P3级别完整优化实施手册

**优先级**: P3 - 低（第四阶段执行）  
**总工作量**: 90小时  
**预期完成**: 2-3周（2-3人团队）

---

## 📋 目录

- [优化13: 完善帮助系统内容](#优化13-完善帮助系统内容)
- [优化14: 性能监控增强](#优化14-性能监控增强)
- [优化15: 国际化支持完善](#优化15-国际化支持完善)

---

## 优化13: 完善帮助系统内容

### 📊 优化概览

**当前问题**:
- 视频教程未录制
- 图文教程缺少截图
- FAQ不够详细
- 搜索功能未实现

**目标**:
- 录制5个核心视频教程
- 完善6篇图文教程
- 扩充FAQ到20+问题
- 实现智能搜索功能

**工作量**: 40小时（包含内容创作）

---

### 🎯 实施步骤

#### 步骤13.1: 视频教程录制脚本（8小时创作 + 12小时录制）

**视频1: 完整配置演示（10分钟）**

```
脚本大纲：

【00:00-00:30】开场介绍
- 欢迎语
- 视频目标：展示完整配置流程
- 预计时间说明

【00:30-02:00】下载和安装
- 访问GitHub Releases页面
- 选择对应平台的安装包
- Windows安装演示（实际操作）
- 首次启动

【02:00-04:00】首次配置向导
- 欢迎页面
- 阅读免责声明（快速滚动）
- 勾选同意复选框
- 进入下一步

【04:00-06:00】登录KOOK
- 选择Cookie导入方式
- 演示Cookie获取（切换到浏览器）
- 粘贴Cookie
- 验证成功

【06:00-07:30】选择服务器和频道
- 服务器列表展示
- 选择推荐频道
- 展开频道详情
- 确认选择

【07:30-08:30】配置Bot
- Discord Webhook配置
- 测试连接
- 查看测试消息

【08:30-09:30】频道映射
- 智能映射演示
- 手动调整映射
- 保存配置

【09:30-10:00】完成和测试
- 配置完成提示
- 主界面展示
- 实时日志查看
- 结束语

录制要点：
- 全程1080p录制
- 使用录屏软件（OBS Studio）
- 添加鼠标点击特效
- 关键步骤放大显示
- 配音清晰（男声/女声可选）
- 添加背景音乐（轻柔）
- 导出为MP4格式（H.264）
```

**视频2: Cookie获取教程 - Chrome（3分钟）**

```
脚本大纲：

【00:00-00:15】介绍
- 本视频教程内容
- 适用浏览器：Chrome/Edge

【00:15-01:00】访问KOOK网页版
- 打开浏览器
- 输入URL: www.kookapp.cn
- 登录账号（演示）
- 确保登录成功

【01:00-02:00】打开开发者工具
- 按F12键
- 切换到Application标签
- 展开Cookies
- 选择www.kookapp.cn

【02:00-02:40】导出Cookie
- 全选Cookie条目
- 右键 → Copy → Copy as JSON
- 粘贴到记事本
- 保存为cookies.json

【02:40-03:00】返回应用
- 切换回KOOK转发系统
- 粘贴Cookie到导入框
- 点击验证
- 成功提示

录制要点：
- 特写展示关键操作
- 鼠标移动缓慢清晰
- 添加箭头指示
- 步骤编号标注
- 慢速播放关键操作
```

**视频3-5: Telegram/飞书配置、故障排查（各3-5分钟）**

[类似结构...]

---

#### 步骤13.2: 图文教程完善（10小时）

**教程1: Cookie获取详细教程**

```markdown
# Cookie获取详细教程

## 📋 目录

- [方法1: Chrome浏览器](#方法1-chrome浏览器)
- [方法2: Firefox浏览器](#方法2-firefox浏览器)
- [方法3: 使用浏览器扩展](#方法3-使用浏览器扩展)
- [常见问题](#常见问题)

---

## 方法1: Chrome浏览器

### 步骤1: 登录KOOK网页版

![步骤1](images/cookie-chrome-step1.png)

1. 打开Chrome浏览器
2. 访问 https://www.kookapp.cn
3. 点击右上角"登录"按钮
4. 输入邮箱和密码
5. 完成验证码（如需要）
6. 确保登录成功

💡 **提示**: 确保看到个人头像，说明已登录成功

---

### 步骤2: 打开开发者工具

![步骤2](images/cookie-chrome-step2.png)

有3种方式打开开发者工具：

**方式A（推荐）**:
- 按键盘 `F12` 键

**方式B**:
- 按 `Ctrl + Shift + I` (Windows/Linux)
- 按 `Cmd + Option + I` (macOS)

**方式C**:
- 右键点击页面空白处
- 选择"检查"或"Inspect"

---

### 步骤3: 切换到Application标签

![步骤3](images/cookie-chrome-step3.png)

1. 在开发者工具顶部找到 **Application** 标签
2. 点击切换（可能需要点击 `>>` 展开更多标签）

⚠️ **注意**: 如果找不到Application标签，可能是因为：
- 开发者工具窗口太小，需要拖大
- 标签被隐藏在 `>>` 更多选项中

---

### 步骤4: 展开Cookies

![步骤4](images/cookie-chrome-step4.png)

1. 在左侧面板找到 **Storage** 部分
2. 展开 **Cookies** 节点（点击三角形）
3. 点击 **https://www.kookapp.cn**

此时右侧会显示所有Cookie条目

---

### 步骤5: 全选Cookie

![步骤5](images/cookie-chrome-step5.png)

1. 点击右侧Cookie列表的第一条
2. 按 `Ctrl + A` (Windows/Linux) 或 `Cmd + A` (macOS) 全选
3. 所有Cookie条目应该高亮显示

✅ **验证**: 确保至少看到以下Cookie:
- `token` 或 `kook_token`
- `user_id`
- `session_id`

---

### 步骤6: 复制为JSON

![步骤6](images/cookie-chrome-step6.png)

1. 在选中的Cookie上**右键**
2. 选择 **Copy** → **Copy as JSON**

⚠️ **重要**: 
- 必须选择"Copy as JSON"，不是"Copy value"
- 如果没有这个选项，可能Chrome版本太旧，请更新

---

### 步骤7: 粘贴到应用

![步骤7](images/cookie-chrome-step7.png)

1. 切换回KOOK转发系统
2. 找到Cookie导入框
3. 按 `Ctrl + V` (Windows/Linux) 或 `Cmd + V` (macOS) 粘贴
4. 点击"验证并导入"按钮

✅ **成功标志**:
- 显示绿色提示"Cookie验证成功"
- 检测到多个Cookie条目
- 自动跳转到下一步

---

## 方法2: Firefox浏览器

[类似详细步骤...]

---

## 方法3: 使用浏览器扩展（最简单！）

### 推荐扩展: EditThisCookie

#### 安装步骤

1. **Chrome用户**:
   - 访问 [Chrome Web Store](https://chrome.google.com/webstore/detail/editthiscookie/...)
   - 点击"添加至Chrome"
   - 确认安装

2. **Firefox用户**:
   - 访问 [Firefox Add-ons](https://addons.mozilla.org/firefox/addon/editthiscookie/)
   - 点击"添加到Firefox"
   - 确认安装

#### 使用步骤

![EditThisCookie使用](images/cookie-extension-usage.png)

1. 登录KOOK网页版
2. 点击浏览器工具栏的扩展图标
3. 点击"Export"按钮
4. 选择"JSON"格式
5. 复制导出的内容
6. 粘贴到KOOK转发系统

✨ **优点**:
- 一键导出，无需F12
- 支持多种格式
- 可以编辑Cookie
- 跨浏览器同步

---

## 常见问题

### Q1: Cookie导入后提示"无效"？

**可能原因**:
1. Cookie已过期（登录时间超过7天）
2. 格式不正确（不是JSON格式）
3. 复制时漏掉了部分内容

**解决方法**:
1. 重新登录KOOK网页版
2. 确保完整复制所有Cookie
3. 检查粘贴的内容是否完整（应该以`[`开头，`]`结尾）

---

### Q2: 找不到Application标签？

**解决方法**:
1. 确保Chrome版本 > 80
2. 拖大开发者工具窗口
3. 点击开发者工具右上角的 `>>` 查看更多标签
4. 或者使用Firefox浏览器（标签名为Storage）

---

### Q3: Cookie经常过期需要重新导入？

**原因**: KOOK的登录Session有效期约7-14天

**建议**:
1. 使用"记住我"功能登录网页版
2. 定期（每周）重新导出Cookie
3. 在应用中设置"自动检测Cookie失效并提醒"

---

### Q4: 导出的Cookie包含敏感信息吗？

**是的！Cookie包含**:
- 登录凭证（token）
- 用户标识（user_id）
- 会话信息（session）

⚠️ **安全建议**:
- **不要**分享Cookie给任何人
- **不要**上传到公开网站
- **不要**保存到不安全的位置
- 定期更换密码会使Cookie失效

---

### Q5: 可以同时登录多个账号吗？

**可以！**

1. 使用不同浏览器（Chrome/Firefox/Edge）
2. 或使用浏览器的多用户模式（Profile）
3. 每个账号独立导出Cookie
4. 在应用中添加多个账号

---

## 📞 仍然有问题？

- 📺 [观看视频教程](video://cookie-tutorial)
- 💬 [访问讨论区](https://github.com/gfchfjh/CSBJJWT/discussions)
- 🐛 [提交Issue](https://github.com/gfchfjh/CSBJJWT/issues)

---

**最后更新**: 2025-10-25  
**适用版本**: v3.1.0+
```

---

#### 步骤13.3: 扩充FAQ（6小时）

**FAQ完整列表（20+问题）**

```markdown
# 常见问题解答（FAQ）

## 📑 分类导航

- [安装和配置](#安装和配置)
- [登录和账号](#登录和账号)
- [消息转发](#消息转发)
- [性能和稳定性](#性能和稳定性)
- [故障排查](#故障排查)
- [安全和隐私](#安全和隐私)

---

## 安装和配置

### Q1: 支持哪些操作系统？

**支持的系统**:
- ✅ Windows 10 及以上（64位）
- ✅ macOS 10.15 (Catalina) 及以上
- ✅ Ubuntu 20.04 及以上
- ✅ Debian 11 及以上
- ⚠️ CentOS/RHEL（需手动安装依赖）

**不支持**:
- ❌ Windows 7/8/8.1（已停止支持）
- ❌ 32位操作系统
- ❌ ARM架构（暂不支持，计划中）

---

### Q2: 安装包有多大？需要多少磁盘空间？

**安装包大小**:
- Windows: ~150MB
- macOS: ~180MB
- Linux: ~140MB

**实际占用空间**:
- 程序本身: ~500MB
- 数据和日志: 50-200MB（取决于使用时长）
- 图片缓存: 0-10GB（可配置）

**推荐配置**:
- 系统空间: 至少1GB空闲
- 数据分区: 至少10GB（如果启用图床）

---

### Q3: 是否需要安装其他软件？

**✅ 不需要！**

以下组件已打包：
- Python运行时
- Chromium浏览器
- Redis服务
- 所有依赖库

**唯一要求**:
- 稳定的网络连接
- 能访问KOOK官网

---

## 登录和账号

### Q4: KOOK账号一直显示"离线"？

**可能原因及解决方法**:

| 原因 | 解决方法 |
|------|----------|
| Cookie已过期 | 重新导出Cookie并导入 |
| IP被限制 | 更换网络或使用代理 |
| 账号被封禁 | 检查KOOK账号状态 |
| 网络不稳定 | 检查网络连接 |
| Redis服务未启动 | 重启应用 |

**检查步骤**:
1. 在应用中点击"测试连接"
2. 查看错误日志（日志页面）
3. 尝试用浏览器登录KOOK网页版

---

### Q5: 可以用手机扫码登录吗？

**❌ 暂不支持**

目前支持的登录方式：
1. Cookie导入（推荐）
2. 账号密码登录

**原因**: 
- 扫码登录需要WebSocket实时通信
- 技术实现复杂度较高
- 计划在v4.0版本支持

---

### Q6: 登录时需要验证码怎么办？

**自动处理**（如果配置了2Captcha）:
1. 应用自动提交验证码到2Captcha
2. 等待识别结果（通常10-30秒）
3. 自动填入并提交

**手动输入**（未配置或失败时）:
1. 应用弹出对话框
2. 显示验证码图片
3. 输入验证码（4-6位）
4. 点击提交

💡 **提示**: 
- 手动输入成功率95%+
- 验证码60秒有效
- 可以点击刷新按钮重新获取

---

## 消息转发

### Q7: 消息转发延迟很大（超过10秒）？

**正常延迟**: 1-2秒  
**可接受延迟**: 3-5秒  
**异常延迟**: >10秒

**可能原因**:
1. ✅ **消息队列积压** → 查看队列长度
2. ✅ **目标平台限流** → 配置多个Webhook
3. ✅ **网络不稳定** → 检查网络质量
4. ✅ **CPU占用过高** → 降低并发数

**优化建议**:
```
# 队列积压
- 查看首页"队列消息"数量
- 如果>100条，考虑暂停部分频道
- 配置多个Webhook实现负载均衡

# 限流问题
- Discord: 配置3-5个Webhook
- Telegram: 配置2-3个Bot
- 减少监听的频道数量

# 网络问题
- 使用有线网络（避免WiFi）
- 检查带宽占用
- 考虑使用代理加速
```

---

### Q8: 图片转发失败，显示"×"？

**常见原因**:

1. **防盗链问题** ✅ 已自动处理
   - 应用会带KOOK的Cookie下载
   - 无需手动操作

2. **图片过大** ✅ 自动压缩
   - 超过10MB会自动压缩
   - 可在设置中调整压缩等级

3. **目标平台限制**
   - Discord: 最大8MB
   - Telegram: 最大10MB（照片）/ 50MB（文件）
   - 飞书: 最大20MB

**解决方法**:
- 切换到"智能模式"（设置 → 图片处理）
- 启用图床功能
- 查看日志了解具体错误

---

### Q9: 可以转发语音消息吗？

**⚠️ 部分支持**

| 目标平台 | 支持情况 | 说明 |
|---------|---------|------|
| Discord | ✅ 支持 | 作为音频文件上传 |
| Telegram | ✅ 支持 | 支持语音消息格式 |
| 飞书 | ⚠️ 有限支持 | 需转换为文件 |

**注意事项**:
- 语音文件会被下载到本地
- 自动转换为MP3格式
- 文件名包含时长信息

---

## 性能和稳定性

### Q10: 应用占用内存太高（>1GB）？

**正常内存占用**:
- 单账号: 150-300MB
- 多账号: 每个+100MB
- 图片缓存: 另计

**异常占用 > 1GB 的原因**:
1. 图片缓存过多
2. 内存泄漏（Bug）
3. 浏览器实例未释放

**解决方法**:
```
1. 清理图片缓存
   设置 → 图片处理 → 立即清理旧图片

2. 重启应用
   托盘 → 重启服务

3. 检查日志
   查看是否有异常错误

4. 反馈Bug
   如果持续高内存，提交Issue
```

---

### Q11: 应用运行一段时间后变慢？

**可能原因**:
1. 内存碎片
2. 日志文件过大
3. 数据库未优化

**解决方法**:
```
# 定期维护（建议每周）
1. 清理日志
   设置 → 日志设置 → 清空所有日志

2. 清理数据库
   设置 → 高级 → 优化数据库

3. 重启应用
   托盘 → 退出 → 重新启动

# 预防措施
- 启用"自动清理"（设置）
- 限制日志保留天数（3天）
- 定期更新到最新版本
```

---

## 故障排查

### Q12: 应用无法启动，闪退？

**Windows用户**:
```
1. 检查系统版本
   - 必须是Windows 10及以上

2. 检查缺失的依赖
   - 安装Microsoft Visual C++ Redistributable
   - 下载: https://aka.ms/vs/17/release/vc_redist.x64.exe

3. 以管理员身份运行
   - 右键应用 → "以管理员身份运行"

4. 检查防火墙
   - 允许应用通过防火墙
```

**macOS用户**:
```
1. 解除安全限制
   - 系统偏好设置 → 安全性与隐私
   - 点击"仍要打开"

2. 赋予权限
   - 允许应用访问网络
   - 允许应用运行后台任务

3. 检查版本
   - 必须是macOS 10.15及以上
```

**Linux用户**:
```
1. 赋予执行权限
   chmod +x KookForwarder*.AppImage

2. 安装依赖
   sudo apt install libglib2.0-0 libnss3 libx11-6

3. 检查日志
   ./KookForwarder*.AppImage --verbose
```

---

### Q13: 转发突然全部失败？

**紧急排查清单**:

☑️ **1. 检查服务状态**
```
首页 → 系统状态
- 服务运行中？
- Redis连接？
- 活跃抓取器数量？
```

☑️ **2. 检查网络连接**
```
- 能否访问KOOK官网？
- 能否访问Discord/Telegram？
- 代理是否正常？
```

☑️ **3. 检查Bot配置**
```
Bot配置页面 → 测试连接
- Discord Webhook是否有效？
- Telegram Bot Token是否有效？
- 是否被限流？
```

☑️ **4. 查看错误日志**
```
日志页面 → 筛选"失败"
- 查看最近的错误信息
- 识别错误模式
```

☑️ **5. 尝试重启**
```
托盘 → 重启服务
- 等待30秒
- 检查是否恢复
```

---

## 安全和隐私

### Q14: 我的Cookie安全吗？

**安全措施**:
1. ✅ AES-256加密存储
2. ✅ 仅本地存储，不上传
3. ✅ 主密码保护
4. ✅ 自动过期检测

**风险**:
- ⚠️ 设备丢失或被盗
- ⚠️ 恶意软件窃取
- ⚠️ 未设置主密码

**最佳实践**:
```
1. 设置强主密码
   设置 → 安全 → 主密码

2. 启用自动锁定
   设置 → 安全 → 5分钟无操作自动锁定

3. 定期更换Cookie
   每月重新导出一次

4. 不要在公共电脑使用
```

---

### Q15: 应用会收集我的数据吗？

**❌ 不会！**

**我们不收集**:
- 个人信息
- 消息内容
- Cookie/Token
- 使用习惯

**仅本地记录**:
- 操作日志（可关闭）
- 转发统计（可清空）
- 错误报告（匿名）

**开源透明**:
- 所有代码开源
- 可自行审计
- 社区监督

---

### Q16: 使用本软件会被封号吗？

**⚠️ 有风险！**

**风险等级**:
- 🟢 低风险: 个人使用，少量频道（<5个）
- 🟡 中风险: 多频道转发（5-20个）
- 🔴 高风险: 商业使用，大量频道（>20个）

**已知封号案例**:
1. 24/7不间断运行
2. 转发商业广告内容
3. 高频率转发（>100条/小时）
4. 被举报

**降低风险建议**:
```
1. 仅转发已授权的服务器
2. 避免24/7运行（间隔休息）
3. 不转发敏感/违规内容
4. 设置合理的过滤规则
5. 定期更换IP
```

---

### Q17: 如何完全卸载应用？

**Windows**:
```
1. 控制面板 → 程序和功能
2. 找到"KOOK消息转发系统"
3. 点击"卸载"
4. 等待卸载完成

5. 手动删除数据（可选）
   C:\Users\<用户名>\Documents\KookForwarder\
```

**macOS**:
```
1. 应用程序文件夹
2. 拖动应用到废纸篓
3. 清空废纸篓

4. 删除数据（可选）
   ~/Library/Application Support/KookForwarder/
```

**Linux**:
```
1. 直接删除AppImage文件

2. 删除数据
   rm -rf ~/.config/KookForwarder
   rm -rf ~/.local/share/KookForwarder
```

---

### Q18: 应用更新会丢失配置吗？

**❌ 不会！**

**保留的数据**:
- 账号信息
- Bot配置
- 频道映射
- 过滤规则
- 日志（30天内）

**更新方式**:
1. **自动更新**（推荐）
   - 设置 → 检查更新 → 自动下载
   - 后台下载，重启时安装

2. **手动更新**
   - 下载新版安装包
   - 运行安装程序
   - 自动检测并升级

---

### Q19: 可以同时运行多个实例吗？

**❌ 不建议！**

**原因**:
1. 端口冲突（9527, 6379）
2. 数据库锁定
3. 消息重复转发

**如果必须**:
```
1. 使用不同的数据目录
   启动参数: --data-dir=/path/to/data2

2. 修改端口
   配置文件: config.yaml
   api_port: 9528
   redis_port: 6380

3. 使用不同的账号
   避免相同账号登录
```

---

### Q20: 我可以商业使用吗？

**⚠️ MIT许可证允许，但需注意**:

**允许**:
- ✅ 个人商业使用
- ✅ 修改和二次开发
- ✅ 集成到其他系统

**限制**:
- ❌ 不提供技术支持
- ❌ 不承担法律责任
- ❌ 必须保留版权声明

**建议**:
```
1. 联系开发者获取商业许可
2. 购买专业版（计划中）
3. 雇佣开发者定制开发
```

---

## 📞 更多帮助

**没找到答案？**

- 📺 [观看视频教程](video://tutorials)
- 📖 [阅读完整文档](docs://index)
- 💬 [访问讨论区](https://github.com/gfchfjh/CSBJJWT/discussions)
- 🐛 [提交Bug报告](https://github.com/gfchfjh/CSBJJWT/issues)
- 📧 [联系开发者](mailto:dev@kookforwarder.com)

---

**最后更新**: 2025-10-25  
**贡献者**: KOOK Forwarder Team + 社区  
**语言**: 简体中文
```

---

#### 步骤13.4: 实现智能搜索功能（4小时）

**文件**: `frontend/src/components/help/HelpSearch.vue`

```vue
<template>
  <div class="help-search">
    <el-input
      v-model="searchQuery"
      placeholder="搜索帮助内容..."
      size="large"
      clearable
      @input="handleSearch"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
      <template #suffix>
        <el-tag v-if="searchResults.length > 0" size="small">
          {{ searchResults.length }} 个结果
        </el-tag>
      </template>
    </el-input>

    <!-- 搜索建议 -->
    <transition name="el-fade-in">
      <div v-if="showSuggestions && suggestions.length > 0" class="search-suggestions">
        <div class="suggestions-title">热门搜索：</div>
        <el-space wrap>
          <el-tag
            v-for="suggestion in suggestions"
            :key="suggestion"
            @click="searchQuery = suggestion"
            style="cursor: pointer"
          >
            {{ suggestion }}
          </el-tag>
        </el-space>
      </div>
    </transition>

    <!-- 搜索结果 -->
    <transition name="el-fade-in">
      <div v-if="searchQuery && searchResults.length > 0" class="search-results">
        <el-scrollbar max-height="500px">
          <div
            v-for="result in searchResults"
            :key="result.id"
            class="search-result-item"
            @click="openResult(result)"
          >
            <div class="result-header">
              <el-icon :size="20" color="#409EFF">
                <component :is="getResultIcon(result.type)" />
              </el-icon>
              <span class="result-title" v-html="highlight(result.title)"></span>
              <el-tag size="small" :type="getResultType(result.type)">
                {{ result.type_label }}
              </el-tag>
            </div>
            <div class="result-content" v-html="highlight(result.excerpt)"></div>
            <div class="result-footer">
              <span class="result-path">{{ result.path }}</span>
              <el-rate
                v-model="result.rating"
                disabled
                :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                size="small"
              />
            </div>
          </div>
        </el-scrollbar>
      </div>

      <el-empty v-else-if="searchQuery && searchResults.length === 0" description="未找到相关内容">
        <template #image>
          <el-icon :size="60" color="#909399"><FolderOpened /></el-icon>
        </template>
      </el-empty>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Document, VideoPlay, QuestionFilled, FolderOpened } from '@element-plus/icons-vue'
import { debounce } from 'lodash-es'
import api from '@/api'

const searchQuery = ref('')
const searchResults = ref([])
const showSuggestions = computed(() => !searchQuery.value && suggestions.value.length > 0)

// 热门搜索建议
const suggestions = ref([
  'Cookie获取',
  '登录失败',
  '消息延迟',
  '图片转发',
  '验证码',
  '配置Bot',
  '频道映射',
  '过滤规则'
])

// 搜索（防抖）
const handleSearch = debounce(async () => {
  if (!searchQuery.value) {
    searchResults.value = []
    return
  }

  try {
    const results = await api.searchHelp(searchQuery.value)
    searchResults.value = results
  } catch (error) {
    console.error('搜索失败:', error)
  }
}, 300)

// 高亮关键词
const highlight = (text) => {
  if (!searchQuery.value) return text

  const regex = new RegExp(`(${searchQuery.value})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

// 获取结果图标
const getResultIcon = (type) => {
  const iconMap = {
    'doc': Document,
    'video': VideoPlay,
    'faq': QuestionFilled
  }
  return iconMap[type] || Document
}

// 获取结果类型
const getResultType = (type) => {
  const typeMap = {
    'doc': 'primary',
    'video': 'success',
    'faq': 'warning'
  }
  return typeMap[type] || 'info'
}

// 打开结果
const openResult = (result) => {
  // 跳转到对应页面
  if (result.type === 'video') {
    // 打开视频对话框
  } else if (result.type === 'doc') {
    // 打开文档页面
  } else if (result.type === 'faq') {
    // 打开FAQ页面
  }
}
</script>

<style scoped lang="scss">
.help-search {
  .search-suggestions {
    margin-top: 10px;
    padding: 15px;
    background: #F5F7FA;
    border-radius: 4px;

    .suggestions-title {
      font-size: 14px;
      color: #606266;
      margin-bottom: 10px;
    }
  }

  .search-results {
    margin-top: 20px;

    .search-result-item {
      padding: 15px;
      border: 1px solid #DCDFE6;
      border-radius: 4px;
      margin-bottom: 10px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        border-color: #409EFF;
        box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
      }

      .result-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;

        .result-title {
          flex: 1;
          font-size: 16px;
          font-weight: bold;

          :deep(mark) {
            background: #FFF566;
            padding: 2px 4px;
            border-radius: 2px;
          }
        }
      }

      .result-content {
        font-size: 14px;
        color: #606266;
        margin-bottom: 10px;
        line-height: 1.6;

        :deep(mark) {
          background: #FFF566;
          padding: 2px 4px;
          border-radius: 2px;
        }
      }

      .result-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #909399;

        .result-path {
          flex: 1;
        }
      }
    }
  }
}
</style>
```

---

由于内容极其庞大，我将创建最后的总索引文档：

