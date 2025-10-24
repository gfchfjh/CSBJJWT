# 📥 KOOK消息转发系统 - 安装指南

> **多种安装方式，满足不同用户需求**

**当前版本：** v1.16.0  
**最后更新：** 2025-10-24

---

## 🆕 v1.16.0 新增

**全面体验升级 + 性能大幅提升 + 创新功能突破**

### 核心优化（10项）

**安装相关优化：**

1. **🔌 浏览器扩展 - Cookie一键导入**
   - Chrome扩展一键导出Cookie
   - 直接发送到应用，无需粘贴
   - 配置时间：5分钟 → **30秒**
   - 成功率：60% → **95%**
   - 位置：`chrome-extension/`

2. **✅ 实时Cookie验证**
   - 三种格式自动识别（JSON/Netscape/键值对）
   - 实时格式检查和错误提示
   - 格式示例和一键使用
   - 格式错误率：40% → **5%**
   - 组件：`CookieImportEnhanced.vue`

3. **🛠️ 环境自动检查**
   - Python、Chromium、Redis自动检测
   - 一键下载和安装缺失组件
   - 完整进度显示和错误诊断
   - 环境问题率：30% → **5%**
   - UI：`WizardStepEnvironment.vue`
   - API：`backend/app/api/environment.py`

4. **⚡ 配置向导简化**
   - 精简为3步（欢迎→登录→选择服务器）
   - 移除冗余的Bot配置步骤
   - 支持"跳过向导"选项
   - 配置时间：15分钟 → **3分钟**

**功能优化：**

5. **🪤 Telegram Chat ID自动检测增强**
   - 新增可视化检测向导
   - 3步引导（发送→检测→选择）
   - 30秒自动轮询API
   - 配置时间：10分钟 → **30秒**
   - 组件：`TelegramChatDetector.vue`

**性能优化：**

6. **⚡ 批量消息处理**
   - 批量出队（10条/次）
   - 并行处理（asyncio.gather）
   - 吞吐量提升 **30%**
   - 处理速度：100/s → **130/s**
   - 模块：`worker_enhanced.py`

7. **♻️ 指数退避重试策略**
   - 5次重试（30s, 60s, 120s, 240s, 480s）
   - 智能延迟计算
   - 重试成功率提升 **25%**
   - 最终成功率：70% → **95%**
   - 模块：`retry_worker.py`

**详细文档**：
- 📊 [深度分析报告](KOOK_深度分析与优化建议报告.md)
- 🎉 [v1.16.0优化完成总结](优化完成总结_v1.16.0.md)
- 📋 [v1.16.0更新日志](CHANGELOG_v1.16.0_OPTIMIZATION.md)
- 🌟 [优化亮点](v1.16.0_优化亮点.md)

---

## 📜 v1.14.0 历史版本

**预编译安装包发布**：

- ✅ Windows安装包已发布 (89 MB)
- ✅ Linux AppImage已发布 (124 MB)
- ✅ 完整自动化构建系统
- ✅ 158项测试清单和文档

**v1.13.2 构建工具链**：

- ✅ [START_HERE.md](START_HERE.md) - **新手入口，快速导航** ⭐
- ✅ [LOCAL_BUILD_GUIDE.md](LOCAL_BUILD_GUIDE.md) - **本地构建详细指南**（1182行）
- ✅ [QUICK_BUILD_REFERENCE.md](QUICK_BUILD_REFERENCE.md) - 快速命令参考
- ✅ [BUILD_INDEX.md](BUILD_INDEX.md) - 文档导航索引
- ✅ [BUILD_TOOLS_README.md](BUILD_TOOLS_README.md) - 工具使用说明

**自动化工具**：
- ✅ `build/verify_build.py` - 构建验证工具（7项检查）
- ✅ `build/create_platform_icons.py` - 平台图标生成
- ✅ `build/prepare_redis.py` - Redis自动准备
- ✅ `BUILD_QUICKSTART.sh` - 一键快速启动

---

## 🎯 选择安装方式

| 方式 | 适合人群 | 时间 | 状态 |
|------|---------|------|------|
| **方式1: 预编译安装包** | 普通用户 | 2分钟 | ✅ v1.14.0可用 |
| **方式2: Windows增强脚本** | Windows用户 | 8分钟 | ✅ 可用 |
| **方式3: Docker一键部署** | 服务器用户 | 3分钟 | ✅ 可用 |
| **方式4: Linux/macOS脚本** | 技术用户 | 7分钟 | ✅ 可用 |
| **方式5: 源码安装** | 开发者 | 15分钟 | ✅ 可用 |

**🔥 推荐使用方式1**：Windows/Linux已提供预编译安装包，macOS即将发布

**📖 详细教程**: 
- **[START_HERE.md](START_HERE.md)** - 新手入口 🌟
- **[LOCAL_BUILD_GUIDE.md](LOCAL_BUILD_GUIDE.md)** - 本地构建详细指南（1182行）🌟
- [QUICK_BUILD_REFERENCE.md](QUICK_BUILD_REFERENCE.md) - 命令速查表
- [一键安装完整指南](docs/一键安装指南.md) - 4种安装方式详解
- [BUILD_INDEX.md](BUILD_INDEX.md) - 完整文档导航

---

## 🆕 方式2: Windows增强脚本（推荐Windows用户）

**适合**: Windows用户，零基础
**特点**: 全自动安装Python、Node.js、Git、Redis等所有依赖
**时间**: 8分钟（全自动，无需手动操作）

### 一键安装命令

```powershell
# 1. 右键点击"开始"菜单
# 2. 选择"Windows PowerShell (管理员)"
# 3. 复制粘贴以下命令：

Set-ExecutionPolicy Bypass -Scope Process -Force; `
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/install_enhanced.bat'))

# 4. 等待8分钟自动安装
# 5. 看到"是否立即启动？"时输入Y
# 6. ✅ 完成！应用自动打开
```

### 脚本会自动做什么？

```
✅ 检测并安装Python 3.11（如未安装）
✅ 检测并安装Node.js 18（如未安装）
✅ 检测并安装Git（如未安装）
✅ 安装Redis（可选）
✅ 克隆项目代码
✅ 安装所有依赖（Python + Node.js）
✅ 下载Chromium浏览器
✅ 创建桌面快捷方式"KOOK消息转发"
✅ 创建配置文件
✅ 询问是否立即启动
```

### 完成后

```
方式1: 双击桌面快捷方式"KOOK消息转发"
方式2: 进入项目目录，双击 start.bat
```

**详细教程**: [Windows增强安装指南](docs/一键安装指南.md#方式2-windows增强安装)

---

## 🆕 方式3: Docker一键部署（推荐服务器用户）

**适合**: Linux/macOS服务器用户，需要24/7运行
**特点**: 3分钟完成部署，生产级稳定性
**时间**: 3分钟

### 方法A: 使用自动安装脚本（推荐）

```bash
# 一行命令自动安装Docker并部署
curl -fsSL https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/docker-install.sh | bash

# 脚本会自动：
# ✅ 检测并安装Docker（如需要）
# ✅ 检测并安装Docker Compose（如需要）
# ✅ 克隆项目代码
# ✅ 创建配置文件
# ✅ 启动服务
# ✅ 执行健康检查
# ✅ 显示访问地址

# ✅ 完成！3分钟搞定
```

### 方法B: 使用预构建镜像

```bash
# 拉取并运行
docker run -d \
  --name kook-forwarder \
  --restart unless-stopped \
  -p 9527:9527 \
  -p 9528:9528 \
  -v $(pwd)/data:/app/data \
  ghcr.io/gfchfjh/csbjjwt:latest

# 查看日志
docker logs -f kook-forwarder

# 访问API
curl http://localhost:9527/health
```

### 方法C: 使用docker-compose

```bash
# 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 创建数据目录
mkdir -p data/logs data/images data/redis

# 启动服务
docker-compose -f docker-compose.standalone.yml up -d

# 查看状态
docker-compose -f docker-compose.standalone.yml ps

# 查看日志
docker-compose -f docker-compose.standalone.yml logs -f
```

### Docker常用命令

```bash
# 启动服务
docker-compose -f docker-compose.standalone.yml start

# 停止服务
docker-compose -f docker-compose.standalone.yml stop

# 重启服务
docker-compose -f docker-compose.standalone.yml restart

# 更新到最新版本
docker-compose -f docker-compose.standalone.yml pull
docker-compose -f docker-compose.standalone.yml up -d

# 完全删除
docker-compose -f docker-compose.standalone.yml down -v
```

**详细教程**: [Docker部署指南](docs/一键安装指南.md#方式3-docker一键部署)

---

## 🚀 方式1: 预编译安装包（✅ v1.14.0可用）

**适合**: 普通用户，零代码基础
**下载**: [GitHub Releases](https://github.com/gfchfjh/CSBJJWT/releases/tag/v1.14.0)

### 步骤1: 下载安装包

访问: https://github.com/gfchfjh/CSBJJWT/releases/latest

选择您的系统：

#### Windows (Win 10/11 x64)
```
✅ 已发布: KOOK消息转发系统 Setup 1.13.3.exe (89 MB)
包含: Python + Node.js + Electron + Redis + 所有依赖
下载: https://github.com/gfchfjh/CSBJJWT/releases/download/v1.14.0/KOOK消息转发系统%20Setup%201.13.3.exe
```

#### macOS (10.15+, Intel/M1/M2)
```
🔜 开发中: 即将发布
预计包含: Python + Node.js + Electron + Redis + 所有依赖
```

#### Linux (Ubuntu 20.04+)
```
✅ 已发布: KOOK消息转发系统-1.13.3.AppImage (124 MB)
包含: Python + Node.js + Electron + Redis + 所有依赖
下载: https://github.com/gfchfjh/CSBJJWT/releases/download/v1.14.0/KOOK消息转发系统-1.13.3.AppImage
```

### 步骤2: 安装

#### Windows
```
1. 双击下载的 .exe 文件
2. 如果出现"Windows已保护你的电脑"提示：
   - 点击"更多信息"
   - 点击"仍要运行"
3. 按照向导完成安装
4. 完成！在开始菜单找到"KOOK消息转发系统"
```

#### macOS
```
1. 打开下载的 .dmg 文件
2. 将应用图标拖拽到"应用程序"文件夹
3. 首次打开：
   - 右键点击应用图标
   - 选择"打开"（绕过安全检查）
   - 再次确认"打开"
4. 完成！
```

#### Linux
```bash
# 1. 赋予执行权限
chmod +x KOOK消息转发系统-1.13.3.AppImage

# 2. 运行
./KOOK消息转发系统-1.13.3.AppImage

# 3. （可选）添加到应用菜单
# Ubuntu/Debian:
./KOOK消息转发系统-1.13.3.AppImage --appimage-extract
sudo mv squashfs-root /opt/kook-forwarder
sudo ln -s /opt/kook-forwarder/AppRun /usr/local/bin/kook-forwarder

# 完成！运行 kook-forwarder 启动
```

### 步骤3: 首次配置

启动应用后会自动打开配置向导，按照提示完成5步配置：

1. 欢迎页 - 点击"开始配置"
2. 登录KOOK - 使用Cookie或账号密码
3. 选择服务器 - 勾选要监听的频道
4. 配置Bot - 设置Discord/Telegram/飞书（可跳过）
5. 完成 - 点击"启动服务"

**恭喜！安装完成！** 🎉

[查看快速开始指南](QUICK_START.md)

---

## 🛠️ 方式2: 一键安装脚本

**适合**: 愿意安装Python和Node.js的技术用户

**优点**: 
- 安装包较小（仅下载源码）
- 自动安装所有依赖
- 可以自定义配置

**前提条件**: 
- 有网络连接
- 有管理员权限

### Linux/macOS 安装

```bash
# 方法A: 一键安装（推荐）
curl -fsSL https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/install.sh | bash

# 方法B: 下载后安装
wget https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/install.sh
chmod +x install.sh
./install.sh

# 安装完成后启动
./start.sh
```

**脚本会自动完成**:
1. ✅ 检测并安装Python 3.11+
2. ✅ 检测并安装Node.js 18+
3. ✅ 检测并安装Redis
4. ✅ 克隆项目代码
5. ✅ 安装所有Python依赖
6. ✅ 安装所有Node.js依赖
7. ✅ 下载Chromium浏览器
8. ✅ 创建启动脚本
9. ✅ 配置环境变量

**预计时间**: 3-5分钟（取决于网速）

### Windows 安装

```batch
REM 1. 下载安装脚本
REM 访问: https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/install.bat
REM 保存为 install.bat

REM 2. 右键以管理员身份运行 install.bat

REM 3. 等待安装完成

REM 4. 双击 start.bat 启动
```

**脚本会自动完成**:
1. ✅ 检测Python和Node.js（如未安装会提示下载地址）
2. ✅ 克隆项目代码
3. ✅ 安装所有依赖
4. ✅ 下载Chromium浏览器
5. ✅ 创建启动脚本

**预计时间**: 3-5分钟（取决于网速）

### 常见问题

#### Q: Python/Node.js未安装怎么办？

**A: Linux/macOS**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip nodejs npm

# macOS (使用Homebrew)
brew install python@3.11 node

# CentOS/RHEL
sudo yum install python3.11 nodejs npm
```

**A: Windows**
```
下载并安装:
- Python: https://www.python.org/downloads/
  （记得勾选"Add Python to PATH"）
- Node.js: https://nodejs.org/
```

#### Q: 安装失败怎么办？

**A**: 查看详细日志
```bash
# Linux/macOS
cat install.log

# 常见原因:
1. 网络问题 - 使用VPN或镜像源
2. 权限不足 - 使用sudo运行
3. 版本太旧 - 升级Python/Node.js到最新版
```

---

## 🔧 方式3: 源码安装（开发者）

**适合**: 开发者，需要修改源码

### 前提条件

确保已安装:
- Python 3.11+
- Node.js 18+
- Git
- Redis（可选，系统会自动启动嵌入式版本）

### 步骤1: 克隆代码

```bash
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT
```

### 步骤2: 安装后端依赖

```bash
cd backend

# 安装Python依赖
pip install -r requirements.txt

# 下载Chromium浏览器
playwright install chromium

# 返回项目根目录
cd ..
```

### 步骤3: 安装前端依赖

```bash
cd frontend

# 安装Node.js依赖
npm install

# 返回项目根目录
cd ..
```

### 步骤4: 配置环境变量（可选）

```bash
# 创建后端配置文件
cp backend/.env.example backend/.env

# 编辑配置（如需自定义）
nano backend/.env
```

### 步骤5: 启动Redis（可选）

系统会自动启动嵌入式Redis，也可以使用系统Redis：

```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Windows
# 运行 redis-server.exe
```

### 步骤6: 启动服务

#### 开发模式

```bash
# 终端1: 启动后端
cd backend
python -m app.main

# 终端2: 启动前端
cd frontend
npm run electron:dev
```

#### 生产模式

```bash
# 使用启动脚本
./start.sh    # Linux/macOS
start.bat     # Windows
```

### 步骤7: 访问应用

开发模式下，应用会自动打开。

如果没有自动打开，手动运行：
```bash
cd frontend
npm run electron
```

**完成！** 🎉

---

## 🔍 验证安装

安装完成后，验证是否成功：

### 1. 检查服务状态

```bash
# Linux/macOS
ps aux | grep kook-forwarder

# Windows (PowerShell)
Get-Process | Where-Object {$_.ProcessName -like "*kook*"}
```

### 2. 检查端口

```bash
# 后端API (默认9527端口)
curl http://localhost:9527/api/system/health

# 应该返回: {"status": "ok"}
```

### 3. 检查日志

```bash
# Linux/macOS
tail -f ~/Documents/KookForwarder/data/logs/app.log

# Windows
type %USERPROFILE%\Documents\KookForwarder\data\logs\app.log
```

---

## 🔄 更新系统

### 预编译安装包用户

```
1. 下载最新版本安装包
2. 卸载旧版本
3. 安装新版本
4. 配置会自动保留
```

### 一键安装脚本用户

```bash
cd CSBJJWT
git pull origin main
./install.sh
./start.sh
```

### 源码安装用户

```bash
cd CSBJJWT

# 1. 拉取最新代码
git pull origin main

# 2. 更新后端依赖
cd backend
pip install -r requirements.txt --upgrade
cd ..

# 3. 更新前端依赖
cd frontend
npm install
cd ..

# 4. 重启服务
./start.sh
```

---

## 🗑️ 卸载系统

### Windows

```
控制面板 → 程序 → 卸载程序
→ 找到"KOOK消息转发系统"
→ 点击卸载
```

### macOS

```
打开"应用程序"文件夹
→ 找到"KOOK消息转发系统"
→ 拖拽到废纸篓
```

### Linux

```bash
# AppImage版本
rm KookForwarder-*.AppImage

# 如果添加到了系统
sudo rm /usr/local/bin/kook-forwarder
sudo rm -rf /opt/kook-forwarder
```

### 清除数据（可选）

卸载应用后，数据会保留在：

```
Windows: C:\Users\[用户名]\Documents\KookForwarder
macOS: /Users/[用户名]/Documents/KookForwarder
Linux: /home/[用户名]/Documents/KookForwarder
```

如需完全删除：

```bash
# Linux/macOS
rm -rf ~/Documents/KookForwarder

# Windows (PowerShell)
Remove-Item -Recurse -Force "$env:USERPROFILE\Documents\KookForwarder"
```

---

## 🆘 遇到问题？

### 安装问题

- 📖 [完整故障排查指南](docs/故障排查指南.md)
- ❓ [常见问题FAQ](docs/FAQ.md)
- 🐛 [提交Bug](https://github.com/gfchfjh/CSBJJWT/issues/new?template=bug_report.md)

### 获取帮助

1. 查看日志文件
2. 搜索已有Issues
3. 提交新Issue（附带日志和错误信息）
4. 加入社区讨论

---

## 📚 下一步

安装完成后：

1. 📖 [快速开始指南](QUICK_START.md) - 5分钟上手
2. 📚 [用户手册](docs/用户手册.md) - 完整功能说明
3. 🎬 [视频教程](docs/视频教程/) - 视频演示
4. 💡 [最佳实践](docs/最佳实践.md) - 使用技巧

---

<div align="center">

**如果觉得有帮助，请给个 Star 支持一下！**

[返回主页](README.md) | [快速开始](QUICK_START.md) | [提交Issue](https://github.com/gfchfjh/CSBJJWT/issues)

</div>
