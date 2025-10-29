# 📘 快速入门教程（5分钟上手）

欢迎使用KOOK消息转发系统！本教程将帮助您在5分钟内完成基础配置并开始使用。

---

## 🎯 学习目标

完成本教程后，您将能够：
- ✅ 安装并启动KOOK转发系统
- ✅ 登录您的KOOK账号
- ✅ 选择要监听的频道
- ✅ 查看实时转发的消息

**预计用时**：5分钟

---

## 📦 第1步：安装软件

### Windows用户

1. 下载安装包：`KOOK消息转发系统-vX.X.X-Windows-x64.exe`
2. 双击运行安装程序
3. 选择安装路径（推荐默认路径：`C:\Program Files\KOOK Forwarder`）
4. 点击"安装"按钮

![Windows安装步骤](../screenshots/windows-install.png)

### macOS用户

1. 下载安装包：`KOOK消息转发系统-vX.X.X-macOS.dmg`
2. 打开DMG文件
3. 将应用拖拽到"应用程序"文件夹
4. 首次打开时，右键点击应用 → 选择"打开"（绕过安全检查）

![macOS安装步骤](../screenshots/macos-install.png)

### Linux用户

1. 下载AppImage：`KOOK消息转发系统-vX.X.X-Linux-x64.AppImage`
2. 打开终端，进入下载目录
3. 赋予执行权限：
   ```bash
   chmod +x KOOK消息转发系统*.AppImage
   ```
4. 运行应用：
   ```bash
   ./KOOK消息转发系统*.AppImage
   ```

![Linux安装步骤](../screenshots/linux-install.png)

---

## 🚀 第2步：首次启动配置向导

安装完成后，软件会自动启动并显示配置向导。

### 2.1 欢迎页面

您会看到欢迎页面，介绍软件的主要功能。

![欢迎页面](../screenshots/wizard-welcome.png)

点击 **"开始配置"** 按钮继续。

### 2.2 登录KOOK账号

有两种登录方式，**推荐使用Cookie导入**（最简单）：

#### 方式一：Cookie导入（推荐） ⭐

1. **安装Chrome扩展**
   - 点击"下载Chrome扩展"按钮
   - 在Chrome浏览器中打开扩展管理页面
   - 开启"开发者模式"
   - 点击"加载已解压的扩展程序"，选择下载的扩展文件夹

   ![Chrome扩展安装](../screenshots/chrome-extension-install.png)

2. **登录KOOK网页版**
   - 打开 https://www.kookapp.cn
   - 使用您的账号密码登录

   ![KOOK网页登录](../screenshots/kook-web-login.png)

3. **一键导出Cookie**
   - 登录成功后，点击浏览器右上角的扩展图标
   - Cookie会自动发送到转发系统
   - 看到"✅ Cookie已自动导入"提示即成功

   ![Cookie导出成功](../screenshots/cookie-export-success.png)

#### 方式二：账号密码登录

1. 在向导中选择"账号密码登录"标签
2. 输入您的KOOK邮箱和密码
3. 点击"登录"按钮
4. 如果出现验证码，会自动弹窗让您输入

![账号密码登录](../screenshots/password-login.png)

> 💡 **提示**：Cookie导入方式更稳定，推荐使用！

### 2.3 选择要监听的服务器和频道

登录成功后，系统会自动获取您加入的所有KOOK服务器和频道。

1. **查看服务器列表**
   
   您会看到类似这样的树形结构：
   ```
   ☑️ 游戏公告服务器
      └─ #公告频道
      └─ #活动频道
      └─ #更新日志
   
   ☑️ 技术交流服务器
      └─ #技术讨论
      └─ #求助频道
   ```

   ![服务器列表](../screenshots/server-selection.png)

2. **勾选要监听的频道**
   
   - 点击服务器名称前的复选框：选择该服务器下的所有频道
   - 点击频道名称前的复选框：仅选择该频道
   - 使用"全选"/"全不选"按钮快速操作

   ![频道选择](../screenshots/channel-selection.png)

3. **完成选择**
   
   选择完成后，点击 **"完成配置"** 按钮。

---

## ✅ 第3步：配置完成

恭喜！您已经完成了基础配置。

![配置完成](../screenshots/wizard-complete.png)

### 接下来您可以：

#### 选项1：仅监听消息（不转发）

- 点击"开始监听"按钮
- 系统会开始监听您选择的KOOK频道
- 进入"实时日志"页面查看收到的消息

![仅监听模式](../screenshots/listen-only.png)

#### 选项2：配置转发Bot（推荐）

如果您想将KOOK消息转发到Discord、Telegram或飞书，请继续配置Bot：

1. 点击"配置转发Bot"
2. 参考相应的教程配置Bot：
   - [如何配置Discord Webhook](02-discord-webhook.md)
   - [如何配置Telegram Bot](03-telegram-bot.md)
   - [如何配置飞书应用](04-feishu-app.md)

![Bot配置入口](../screenshots/bot-config-entry.png)

---

## 🎊 完成！

您已经成功配置了KOOK消息转发系统！

### 下一步学习

- 📗 [如何配置Discord Webhook](02-discord-webhook.md)
- 📕 [如何配置Telegram Bot](03-telegram-bot.md)
- 📔 [如何配置飞书自建应用](04-feishu-app.md)
- 📓 [频道映射配置详解](05-channel-mapping.md)
- 📒 [过滤规则使用技巧](06-filter-rules.md)

### 遇到问题？

- 💬 [常见问题FAQ](../faq.md)
- 🐛 [问题排查指南](../troubleshooting.md)
- 📺 [观看视频教程](../video-tutorials.md)

---

## 📝 小贴士

### 如何查看实时日志？

1. 点击左侧菜单的"实时日志"
2. 您会看到所有接收到的KOOK消息
3. 筛选条件可以帮助您查找特定消息

![实时日志](../screenshots/real-time-logs.png)

### 如何暂停/恢复监听？

1. 点击主界面右上角的"运行中"按钮
2. 选择"暂停服务"
3. 需要恢复时，点击"启动服务"

![服务控制](../screenshots/service-control.png)

### 如何修改配置？

所有配置都可以随时修改：

- **账号管理**：左侧菜单 → 账号管理 → 编辑/删除账号
- **频道选择**：左侧菜单 → 账号管理 → 选择频道
- **Bot配置**：左侧菜单 → 机器人配置 → 编辑Bot
- **映射关系**：左侧菜单 → 频道映射 → 修改映射

![设置修改](../screenshots/settings-modify.png)

---

**🎉 恭喜您完成快速入门教程！现在您可以开始使用KOOK消息转发系统了！**
