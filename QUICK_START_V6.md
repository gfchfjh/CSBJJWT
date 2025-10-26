# 🎬 KOOK消息转发系统 - 快速开始指南 V6.2

> **5分钟快速上手 · 零代码基础 · 企业级桌面应用**

---

## 📋 目录

- [前置准备](#前置准备)
- [方式一：一键安装包（推荐）](#方式一一键安装包推荐)
- [方式二：Docker部署](#方式二docker部署)
- [方式三：源码运行](#方式三源码运行)
- [配置向导](#配置向导)
- [常见问题](#常见问题)

---

## 前置准备

### 您需要准备

✅ **必需**：
- 一个KOOK账号
- 至少一个转发目标（Discord/Telegram/飞书其中之一）
- 5分钟时间

❌ **不需要**：
- 编程知识
- 服务器
- 数据库
- Redis（已内置）
- Chromium（已内置）

### 系统要求

| 操作系统 | 最低要求 | 推荐配置 |
|---------|---------|---------|
| **Windows** | Win 10+ (x64) | Win 11 |
| **macOS** | 10.15+ | 12.0+ (Intel/Apple Silicon) |
| **Linux** | Ubuntu 20.04+ | Ubuntu 22.04+ |

**硬件要求**：
- CPU: 双核2GHz+
- 内存: 4GB+
- 硬盘: 1GB空闲空间
- 网络: 稳定网络连接

---

## 方式一：一键安装包（推荐）

> **最简单！** 无需任何技术背景，5分钟完成。

### 步骤1：下载安装包

访问 [GitHub Releases](https://github.com/gfchfjh/CSBJJWT/releases/latest)

根据您的操作系统选择对应的安装包：

| 操作系统 | 文件名 | 大小 |
|---------|--------|------|
| Windows | `KOOK-Forwarder-Setup-6.2.0.exe` | ~250MB |
| macOS (Intel) | `KOOK-Forwarder-6.2.0-x64.dmg` | ~300MB |
| macOS (M1/M2) | `KOOK-Forwarder-6.2.0-arm64.dmg` | ~280MB |
| Linux | `KOOK-Forwarder-6.2.0.AppImage` | ~280MB |

### 步骤2：安装应用

#### Windows

1. 双击 `.exe` 文件
2. 如果出现SmartScreen警告，点击「更多信息」→「仍要运行」
3. 按照安装向导完成安装
4. 完成后会自动启动应用

#### macOS

1. 双击 `.dmg` 文件
2. 将应用拖拽到「应用程序」文件夹
3. 首次运行：右键点击应用 → 「打开」
4. 确认安全警告

**常见问题**：
- **「已损坏」警告**：执行命令
  ```bash
  sudo xattr -r -d com.apple.quarantine /Applications/KOOK消息转发系统.app
  ```

#### Linux

1. 赋予执行权限：
   ```bash
   chmod +x KOOK-Forwarder-6.2.0.AppImage
   ```

2. 双击运行，或命令行：
   ```bash
   ./KOOK-Forwarder-6.2.0.AppImage
   ```

3. 首次运行可能需要安装FUSE：
   ```bash
   sudo apt install fuse libfuse2
   ```

### 步骤3：完成配置向导

首次启动会进入**5步配置向导**（详见[配置向导](#配置向导)部分）

### 步骤4：开始使用

配置完成后：
1. 点击「启动服务」按钮
2. 等待状态变为「🟢 运行中」
3. 完成！消息将自动转发

---

## 方式二：Docker部署

> **适合有一定技术背景的用户，或需要服务器部署的场景。**

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 快速启动

```bash
# 1. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 2. 启动所有服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 访问Web界面
# 浏览器打开: http://localhost:8080
```

### Docker Compose配置

默认使用 `docker-compose.yml`，包含：
- ✅ 前端服务（Electron Web版）
- ✅ 后端API服务
- ✅ Redis服务
- ✅ 数据持久化

**端口映射**：
- `8080` - Web界面
- `9527` - 后端API
- `6379` - Redis（仅内部）

### 数据持久化

数据存储在Docker卷中：
```bash
# 查看卷
docker volume ls | grep kook

# 备份数据
docker run --rm -v kook_data:/data -v $(pwd):/backup ubuntu tar czf /backup/kook-backup.tar.gz /data
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

📖 **详细文档**：[Docker部署指南](DEPLOYMENT_GUIDE_V6.md)

---

## 方式三：源码运行

> **适合开发者和需要二次开发的用户。**

### 前置要求

- Python 3.11+
- Node.js 18+
- Redis 7.0+（或使用Docker启动）
- Git

### 1. 克隆项目

```bash
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT
```

### 2. 启动Redis（如果未安装）

**方式A：Docker快速启动**
```bash
docker run -d -p 6379:6379 --name kook-redis redis:7.2-alpine
```

**方式B：本地安装**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt install redis-server
sudo systemctl start redis

# Windows
# 下载：https://github.com/tporadowski/redis/releases
```

### 3. 启动后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python -m app.main

# 服务将运行在: http://localhost:9527
```

### 4. 启动前端（新终端）

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 前端将运行在: http://localhost:5173
```

### 5. 访问应用

打开浏览器，访问：http://localhost:5173

📖 **详细文档**：[开发指南](docs/开发指南.md)

---

## 配置向导

首次启动应用会自动进入配置向导，共5步：

### 第1步：免责声明 ⚠️

- 仔细阅读免责声明
- 勾选「我已阅读并同意」
- 点击「同意并开始配置」

**重要提示**：
- 使用本软件可能违反KOOK服务条款
- 请仅在已授权场景使用
- 自行承担使用风险

### 第2步：登录KOOK账号 🔐

**方式A：Chrome扩展（推荐）**
1. 点击「下载Chrome扩展」
2. 安装扩展（仅首次）
3. 打开 [KOOK网页版](https://www.kookapp.cn) 并登录
4. 点击扩展图标 → 「导出Cookie」
5. 回到应用，粘贴Cookie（Ctrl+V）
6. 点击「验证并登录」

**方式B：手动粘贴Cookie**
1. 打开 [KOOK网页版](https://www.kookapp.cn) 并登录
2. 按F12打开开发者工具
3. 切换到「Application」标签
4. 左侧选择「Cookies」→「https://www.kookapp.cn」
5. 复制所有Cookie（或使用JSON格式）
6. 粘贴到应用

**方式C：账号密码登录**
1. 输入KOOK邮箱
2. 输入密码
3. 点击「登录」
4. 如需验证码，会弹出输入框

📖 **详细教程**：[Cookie获取教程](docs/tutorials/02-Cookie获取详细教程.md)

### 第3步：选择监听的服务器和频道 🎯

1. 应用会自动加载您的所有KOOK服务器
2. 勾选您想监听的服务器
3. 展开服务器，勾选具体频道
4. 点击「下一步」

**建议**：先选择1-2个测试频道，成功后再添加更多

### 第4步：配置转发目标（Bot）🤖

#### Discord Webhook

1. 在Discord服务器中，右键点击目标频道
2. 选择「编辑频道」→「整合」→「Webhook」
3. 点击「新建Webhook」
4. 复制Webhook URL
5. 粘贴到应用，点击「测试连接」

📖 **详细教程**：[Discord配置教程](docs/tutorials/03-Discord配置教程.md)

#### Telegram Bot

1. 与 `@BotFather` 对话
2. 发送 `/newbot` 创建Bot
3. 复制Bot Token
4. 将Bot添加到目标群组
5. 在应用中填入Token，点击「自动获取Chat ID」

📖 **详细教程**：[Telegram配置教程](docs/tutorials/04-Telegram配置教程.md)

#### 飞书Bot

1. 访问 [飞书开放平台](https://open.feishu.cn)
2. 创建企业自建应用
3. 开启「机器人」能力
4. 复制App ID和App Secret
5. 将机器人添加到群组
6. 在应用中填入配置

📖 **详细教程**：[飞书配置教程](docs/tutorials/05-飞书配置教程.md)

### 第5步：设置频道映射 🔀

**方式A：一键智能映射（推荐）** 🎯

1. 点击「智能映射」按钮
2. 应用会自动匹配同名或相似的频道
3. 检查匹配结果（准确率高+）
4. 确认无误后点击「应用」

**匹配示例**：
- KOOK「#公告」 → Discord「#announcements」✅ 90%相似度
- KOOK「#活动」 → Telegram「活动群」✅ 85%相似度
- KOOK「#技术讨论」 → 飞书「Tech Support」✅ 78%相似度

**方式B：手动配置**

1. 点击「添加映射」
2. 选择KOOK频道
3. 选择目标平台和Bot
4. 输入目标频道ID
5. 保存

### 配置完成！🎉

点击「完成配置」，进入主界面。

---

## 使用应用

### 主界面功能

#### 1. 服务控制 🚀

- **启动服务** - 开始监听和转发消息
- **停止服务** - 暂停所有转发
- **重启服务** - 重启服务（解决异常）
- **查看日志** - 查看详细日志

**状态显示**：
- 🟢 运行中 - 服务正常
- 🔴 已停止 - 服务未启动
- 🟡 启动中 - 正在启动
- ⚠️ 异常 - 需要检查

#### 2. 实时统计 📊

- **今日消息数** - 今天转发的消息总数
- **成功率** - 成功转发的百分比
- **平均延迟** - 平均转发时间
- **队列大小** - 待处理的消息数

#### 3. 最近日志 📋

- 实时显示最近10条消息日志
- 点击「查看全部」进入日志页面
- 支持重试失败的消息

### 左侧菜单

- **首页** - 概览和快速操作
- **账号管理** - 添加/删除/重新登录
- **机器人配置** - 管理Discord/Telegram/飞书Bot
- **频道映射** - 管理映射规则
- **过滤规则** - 设置过滤条件
- **消息日志** - 查看所有转发记录
- **系统设置** - 8个标签页的完整设置
- **帮助文档** - 查看教程和FAQ

### 系统托盘

- **最小化到托盘** - 关闭窗口时最小化（不退出）
- **快捷操作** - 右键托盘图标查看菜单
- **实时状态** - 托盘图标显示运行状态

---

## 常见问题

### Q1: 应用无法启动？

**Windows用户**：
1. 右键点击 → 「以管理员身份运行」
2. 检查杀毒软件，添加到白名单
3. 安装 [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

**macOS用户**：
1. 右键点击 → 「打开」（不要双击）
2. 如果提示「已损坏」，执行：
   ```bash
   sudo xattr -r -d com.apple.quarantine /Applications/KOOK消息转发系统.app
   ```

**Linux用户**：
1. 赋予执行权限：`chmod +x *.AppImage`
2. 安装FUSE：`sudo apt install fuse libfuse2`

### Q2: Cookie导入失败？

**解决方法**：
1. 使用Chrome扩展（最可靠）
2. 检查JSON格式是否正确
3. 确保复制完整（不要截断）
4. 尝试重新登录KOOK网页版

📖 **详细教程**：[Cookie获取教程](docs/tutorials/02-Cookie获取详细教程.md)

### Q3: 消息没有转发？

**检查清单**：
1. ✅ 服务是否运行？（主界面查看状态）
2. ✅ 账号是否在线？（账号页面查看）
3. ✅ 是否创建了映射？（映射页面检查）
4. ✅ 映射是否启用？（状态列查看）
5. ✅ Bot配置是否正确？（测试连接）

### Q4: 图片转发失败？

**解决方法**：
1. 切换到「智能模式」（设置 → 图片处理）
2. 降低图片大小限制
3. 查看日志中的详细错误
4. 检查目标平台限制

### Q5: 性能问题（卡顿/占用高）？

**优化方法**：
1. 关闭不必要的账号
2. 减少映射数量
3. 重启服务
4. 清理图片缓存
5. 降低日志级别

### 更多问题？

📖 查看 [完整FAQ](docs/tutorials/FAQ-常见问题.md)（35个常见问题详解）

---

## 下一步

### 📚 推荐阅读

- [完整用户手册](docs/用户手册.md) - 所有功能详解
- [API接口文档](docs/API接口文档.md) - 开发者参考
- [部署指南](DEPLOYMENT_GUIDE_V6.md) - 生产环境部署

### 🎓 视频教程（即将推出）

- 完整配置演示（10分钟）
- Chrome扩展使用（3分钟）
- 常见问题排查（5分钟）

### 💬 获取帮助

- [GitHub Issues](https://github.com/gfchfjh/CSBJJWT/issues) - Bug报告
- [GitHub Discussions](https://github.com/gfchfjh/CSBJJWT/discussions) - 问题讨论
- [FAQ文档](docs/tutorials/FAQ-常见问题.md) - 常见问题

---

## 🎉 开始使用吧！

配置完成后，您的KOOK消息将自动转发到目标平台。

**享受自动化带来的便利！** 🚀

---

<div align="center">

** 如果觉得有用，请给项目点个Star**

**Made with ❤️ by KOOK消息转发系统团队**

</div>

---

**文档版本**: v6.2.0  
**最后更新**: 2025-10-26  
**预计阅读时间**: 10分钟
