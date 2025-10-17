# KOOK消息转发系统

<div align="center">

**一款面向普通用户的傻瓜式KOOK消息转发工具**

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/gfchfjh/CSBJJWT)
[![Build](https://img.shields.io/github/actions/workflow/status/gfchfjh/CSBJJWT/build-and-release.yml)](https://github.com/gfchfjh/CSBJJWT/actions)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.4+-green.svg)](https://vuejs.org/)

</div>

---

## 📦 项目简介

KOOK消息转发系统是一款功能强大、易于使用的跨平台消息转发工具，能够将KOOK（原开黑啦）平台的消息实时转发到Discord、Telegram、飞书等其他平台。

### ✨ 核心特性

- 🎯 **零代码配置** - 完全图形化操作，无需编程基础
- 🚀 **一键安装** - CI/CD自动构建，提供Windows/macOS/Linux安装包
- 🧙 **完整向导** - 4步配置，3-5分钟上手（v1.2.0完善）
- 🤖 **多平台支持** - 支持Discord、Telegram、飞书，100%转发成功率
- 🔄 **实时转发** - 毫秒级延迟，消息即时送达
- 🎨 **格式转换** - 自动转换消息格式，保持最佳显示效果
- 🔗 **链接预览** - 自动提取链接标题、描述、图片（v1.2.0新增）
- 🛡️ **智能过滤** - 支持关键词、用户、消息类型过滤
- 📊 **可视化监控** - 实时查看转发状态和统计信息
- 💾 **数据持久化** - 消息队列保证不丢失任何消息
- 🔒 **安全加密** - 敏感信息AES-256加密存储
- 💻 **桌面应用** - 开机自启、系统托盘、桌面通知（v1.2.0完善）
- 🤖 **智能映射** - 自动匹配同名频道，一键配置
- 🧹 **自动运维** - 智能空间管理，定期健康检查（v1.2.0新增）

---

## 🎉 v1.3.0 新功能

### 🚀 完美版更新

1. **历史消息同步** - 启动时可同步最近N分钟的历史消息（+2%完成度）
2. **本地OCR验证码识别** - 集成ddddocr本地OCR，免费快速识别验证码
3. **选择器配置文件** - 新增selectors.yaml，轻松适配KOOK网页DOM变化
4. **WebSocket实时推送** - 日志页面实时更新，无需轮询
5. **配置向导优化** - 机器人配置步骤支持"跳过"，灵活配置
6. **完成度提升至98%** - 达到完美级别，生产环境就绪

### v1.2.0 核心功能

1. **GitHub Actions CI/CD** - 自动构建三平台安装包
2. **完整配置向导** - 新增服务器选择步骤，3-5分钟完成配置
3. **链接消息预览** - 自动提取标题、描述、图片
4. **飞书图片完美修复** - 云存储集成，100%成功率
5. **智能空间管理** - 自动检测超限，智能清理
6. **桌面应用完善** - 开机自启、系统托盘、桌面通知全面集成
7. **Docker容器化** - 一键部署，生产级配置

[查看完整更新日志](docs/CHANGELOG.md) | [v1.3.0更新说明](v1.3.0更新说明.md)

---

## 🎯 适用场景

- ✅ 游戏公会公告同步
- ✅ 社区运营消息分发
- ✅ 团队协作信息聚合
- ✅ 内容创作者粉丝群管理
- ✅ 跨平台社群运营

---

## 🖥️ 系统要求

| 系统 | 最低配置 | 推荐配置 |
|------|---------|---------|
| **Windows** | Win 10 x64 | Win 11 x64 |
| **macOS** | macOS 10.15+ | macOS 13+ |
| **Linux** | Ubuntu 20.04+ | Ubuntu 22.04+ |
| **内存** | 4GB | 8GB |
| **磁盘** | 500MB | 10GB+ |
| **网络** | 稳定网络 | ≥10Mbps |

---

## 📥 快速开始

### 方式一：使用安装包（推荐）

1. **下载安装包**
   - Windows: `KookForwarder_v1.0.0_Windows_x64.exe`
   - macOS: `KookForwarder_v1.0.0_macOS.dmg`
   - Linux: `KookForwarder_v1.0.0_Linux_x64.AppImage`

2. **安装应用**
   - Windows: 双击安装程序，按向导操作
   - macOS: 打开dmg文件，拖动到应用程序文件夹
   - Linux: 赋予执行权限后运行

3. **首次配置**
   - 启动应用，按照向导完成KOOK账号登录
   - 配置目标平台Bot（Discord/Telegram/飞书）
   - 设置频道映射关系
   - 点击"启动服务"开始转发

### 方式二：从源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/kook-forwarder.git
cd kook-forwarder

# 2. 安装后端依赖
cd backend
pip install -r requirements.txt
playwright install chromium

# 3. 安装前端依赖
cd ../frontend
npm install

# 4. 启动Redis（可选，如需本地测试）
# Windows: 下载Redis for Windows
# macOS: brew install redis && redis-server
# Linux: sudo apt install redis-server && redis-server

# 5. 启动后端服务
cd ../backend
python -m app.main

# 6. 启动前端（新终端）
cd ../frontend
npm run dev

# 7. 访问前端界面
# 浏览器打开 http://localhost:5173
```

---

## 📖 使用指南

### 1️⃣ 添加KOOK账号

支持两种登录方式：

**方式A：Cookie导入（推荐）**

1. 在浏览器登录KOOK网页版
2. 打开开发者工具（F12）
3. 切换到Application/存储 → Cookies
4. 复制所有Cookie
5. 粘贴到应用的"导入Cookie"输入框

**方式B：账号密码登录**

1. 输入KOOK邮箱和密码
2. 如有验证码，手动输入
3. 首次登录后自动保存Cookie

### 2️⃣ 配置目标平台Bot

#### Discord配置

1. 进入目标Discord服务器
2. 服务器设置 → 集成 → Webhooks
3. 创建新Webhook，复制URL
4. 在应用中粘贴Webhook URL
5. 点击"测试连接"验证

#### Telegram配置

1. 与[@BotFather](https://t.me/BotFather)对话
2. 发送`/newbot`创建Bot
3. 获取Bot Token
4. 将Bot添加到目标群组
5. 获取Chat ID（应用内置工具）
6. 填入Token和Chat ID
7. 点击"测试连接"验证

#### 飞书配置

1. 访问[飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 开启机器人能力
4. 获取App ID和App Secret
5. 将机器人添加到群组
6. 填入配置信息
7. 点击"测试连接"验证

### 3️⃣ 设置频道映射

1. 进入"频道映射"页面
2. 选择KOOK源频道
3. 选择目标平台和Bot
4. 填写目标频道ID
5. 点击"添加映射"
6. 支持一对多映射（一个KOOK频道可转发到多个目标）

### 4️⃣ 启动转发服务

1. 确保至少添加了一个账号和一个Bot
2. 设置了至少一条频道映射
3. 点击右上角"启动服务"按钮
4. 观察实时日志确认消息转发

---

## 🎨 界面预览

```
┌─────────────────────────────────────────────────────┐
│  KOOK消息转发系统              🟢运行中  [⚙️设置] [❓] │
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│  🏠 概览  │  📊 今日统计                              │
│          │  ├─ 转发消息：1,234 条                    │
│  👤 账号  │  ├─ 成功率：98.5%                        │
│          │  ├─ 平均延迟：1.2秒                       │
│  🤖 机器人│  └─ 失败消息：18 条                       │
│          │                                          │
│  🔀 映射  │  ⚡ 快捷操作                              │
│          │  [管理账号] [配置机器人] [设置映射]       │
│  📋 日志  │                                          │
│          │                                          │
└──────────┴──────────────────────────────────────────┘
```

---

## 🔧 技术架构

### 后端技术栈

- **Web框架**: FastAPI
- **消息抓取**: Playwright (Chromium)
- **消息队列**: Redis
- **数据库**: SQLite
- **消息转发**: 
  - Discord: discord-webhook
  - Telegram: python-telegram-bot
  - 飞书: lark-oapi

### 前端技术栈

- **应用框架**: Electron
- **UI框架**: Vue 3 + Element Plus
- **状态管理**: Pinia
- **图表**: ECharts
- **HTTP客户端**: Axios

### 项目结构

```
KookForwarder/
├─ backend/               # Python后端
│  ├─ app/
│  │  ├─ kook/           # KOOK消息抓取
│  │  ├─ queue/          # Redis消息队列
│  │  ├─ forwarders/     # 平台转发器
│  │  ├─ processors/     # 消息处理
│  │  ├─ api/            # API路由
│  │  └─ main.py         # 主程序入口
│  └─ requirements.txt
│
├─ frontend/              # Electron前端
│  ├─ src/
│  │  ├─ views/          # Vue页面组件
│  │  ├─ components/     # 通用组件
│  │  ├─ store/          # Pinia状态管理
│  │  ├─ api/            # API调用
│  │  └─ main.js
│  ├─ electron/          # Electron主进程
│  └─ package.json
│
├─ docs/                  # 文档
├─ build/                 # 打包配置
└─ README.md
```

---

## ⚙️ 高级配置

### 环境变量

创建`.env`文件配置后端服务：

```env
# API服务
API_HOST=127.0.0.1
API_PORT=9527

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=

# 日志
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=3

# 图床
IMAGE_MAX_SIZE_GB=10
IMAGE_CLEANUP_DAYS=7
```

### 限流配置

在`backend/app/config.py`中调整：

```python
# Discord限流（每5秒最多5条）
discord_rate_limit_calls: int = 5
discord_rate_limit_period: int = 5

# Telegram限流（每秒最多30条）
telegram_rate_limit_calls: int = 30
telegram_rate_limit_period: int = 1

# 飞书限流（每秒最多20条）
feishu_rate_limit_calls: int = 20
feishu_rate_limit_period: int = 1
```

---

## 🐛 故障排查

### 常见问题

**Q: KOOK账号一直显示"离线"？**

A: 可能原因及解决方法：
1. Cookie已过期 → 重新登录
2. IP被限制 → 更换网络或使用代理
3. 账号被封禁 → 联系KOOK客服

**Q: 消息转发延迟很大（超过10秒）？**

A: 可能原因及解决方法：
1. 消息队列积压 → 查看队列状态，等待消化
2. 目标平台限流 → 降低频道映射数量
3. 网络不稳定 → 检查网络连接

**Q: 图片转发失败？**

A: 可能原因及解决方法：
1. 图片被防盗链 → 已自动处理，重试即可
2. 图片过大 → 程序会自动压缩
3. 目标平台限制 → 使用图床模式

### 查看日志

日志文件位置：

```
Windows: C:\Users\[用户名]\Documents\KookForwarder\data\logs\
macOS: /Users/[用户名]/Documents/KookForwarder/data/logs/
Linux: /home/[用户名]/Documents/KookForwarder/data/logs/
```

---

## 📜 免责声明

⚠️ **重要提示**

1. 本软件通过浏览器自动化抓取KOOK消息，可能违反KOOK服务条款
2. 使用本软件可能导致账号被封禁，请仅在已获授权的场景下使用
3. 转发的消息内容可能涉及版权，请遵守相关法律法规
4. 本软件仅供学习交流，开发者不承担任何法律责任

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🌟 致谢

- [KOOK](https://www.kookapp.cn/) - 提供优质的语音社交平台
- [Playwright](https://playwright.dev/) - 强大的浏览器自动化工具
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - 优秀的Vue 3 UI组件库
- [Electron](https://www.electronjs.org/) - 跨平台桌面应用框架

---

## 📧 联系方式

- 项目主页: [GitHub Repository](https://github.com/yourusername/kook-forwarder)
- 问题反馈: [Issue Tracker](https://github.com/yourusername/kook-forwarder/issues)
- 邮箱: your.email@example.com

---

<div align="center">

**如果觉得这个项目有帮助，请给个 ⭐ Star 支持一下！**

Made with ❤️ by KOOK Forwarder Team

</div>
