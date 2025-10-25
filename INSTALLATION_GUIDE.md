# 📥 KOOK消息转发系统 - 安装指南

> **多种安装方式，满足不同用户需求**

**当前版本：** v2.0.0  
**最后更新：** 2025-10-24

---

## 🆕 v2.0.0 深度优化完成版

**从"技术工具"到"普通用户产品"的完美蜕变！**

### 核心特性

#### ⚡ 安装体验革命性提升
- 🎯 **安装时间**：30分钟 → 5分钟（**↓ 83%**）
- 🔍 **智能检查**：8项环境检查 + 一键修复
- 🧙 **配置向导**：10+步 → 4步（**↓ 60%**）
- 📚 **完整帮助**：内置教程 + FAQ + 视频

#### 🎁 全新功能
- ✅ **一键打包系统**：自动准备Chromium + Redis
- ✅ **智能环境检查**：自动检测8项环境，一键修复问题
- ✅ **Cookie智能导入**：3种方式（文本/文件/插件）
- ✅ **智能频道映射**：75%+准确率，拖拽界面
- ✅ **增强过滤规则**：黑白名单 + 正则表达式
- ✅ **WebSocket实时通信**：CPU使用率↓60%
- ✅ **虚拟滚动列表**：10000+日志流畅显示
- ✅ **安全加固**：Token认证 + 速率限制
- ✅ **国际化主题**：中英双语 + 深色主题

详见：[v2.0.0完整优化报告](COMPLETE_OPTIMIZATION_REPORT.md)

---

## 🎯 选择安装方式

| 方式 | 适合人群 | 时间 | 状态 |
|------|---------|------|------|
| **方式1: 预编译安装包** | 普通用户 | **5分钟** | ✅ v2.0.0可用 推荐 |
| **方式2: Docker一键部署** | 服务器用户 | **3分钟** | ✅ 可用 |
| **方式3: 源码安装** | 开发者 | 10-15分钟 | ✅ 可用 |

**🔥 强烈推荐使用方式1**：Windows/Linux/macOS均已提供预编译安装包

**📖 快速导航**: 
- **[START_HERE.md](START_HERE.md)** - 新手入口 🌟
- **[完整优化报告](COMPLETE_OPTIMIZATION_REPORT.md)** - 53项优化详解
- **[使用指南](HOW_TO_USE_OPTIMIZATIONS.md)** - 新功能使用方法

---

## 🚀 方式1: 预编译安装包（推荐）

**适合**: 普通用户，零代码基础
**下载**: [GitHub Releases](https://github.com/gfchfjh/CSBJJWT/releases/tag/v2.0.0)

### 步骤1: 下载安装包

访问: https://github.com/gfchfjh/CSBJJWT/releases/latest

选择您的系统：

#### Windows (Win 10/11 x64)
```
✅ 已发布: KOOK-Forwarder-2.0.0-win.exe (100 MB)
包含: Python + Node.js + Electron + Redis + Chromium + 所有依赖
下载: https://github.com/gfchfjh/CSBJJWT/releases/download/v2.0.0/KOOK-Forwarder-2.0.0-win.exe
```

#### macOS (10.15+, Intel/M1/M2)
```
✅ 已发布: KOOK-Forwarder-2.0.0.dmg (150 MB)
包含: Python + Node.js + Electron + Redis + Chromium + 所有依赖
下载: https://github.com/gfchfjh/CSBJJWT/releases/download/v2.0.0/KOOK-Forwarder-2.0.0.dmg
```

#### Linux (Ubuntu 20.04+)
```
✅ 已发布: KOOK-Forwarder-2.0.0.AppImage (140 MB)
包含: Python + Node.js + Electron + Redis + Chromium + 所有依赖
下载: https://github.com/gfchfjh/CSBJJWT/releases/download/v2.0.0/KOOK-Forwarder-2.0.0.AppImage
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
chmod +x KOOK-Forwarder-2.0.0.AppImage

# 2. 运行
./KOOK-Forwarder-2.0.0.AppImage

# 3. （可选）添加到应用菜单
# Ubuntu/Debian:
./KOOK-Forwarder-2.0.0.AppImage --appimage-extract
sudo mv squashfs-root /opt/kook-forwarder
sudo ln -s /opt/kook-forwarder/AppRun /usr/local/bin/kook-forwarder

# 完成！运行 kook-forwarder 启动
```

### 步骤3: 首次配置（v2.0.0新向导）

启动应用后会自动打开配置向导，按照提示完成5步配置：

#### 步骤1: 环境检查（新增）

系统会自动检查8项环境：

| 检查项 | 说明 | 自动修复 |
|--------|------|----------|
| ✅ Python版本 | 检查Python 3.11+ | ❌ 需手动安装 |
| ✅ 依赖库 | 检查所有Python依赖 | ✅ 一键安装 |
| ✅ Playwright浏览器 | 检查Chromium浏览器 | ✅ 一键安装 |
| ✅ Redis连接 | 检查Redis服务 | ✅ 自动启动 |
| ✅ 端口占用 | 检查9527端口 | ✅ 自动释放 |
| ✅ 磁盘空间 | 检查可用空间>5GB | ❌ 需手动清理 |
| ✅ 网络连通性 | 检查网络连接 | ❌ 需手动修复 |
| ✅ 写权限 | 检查文件写权限 | ✅ 自动修复 |

**操作**：
- 查看检查结果
- 点击"一键修复"解决问题
- 点击"下一步"继续

#### 步骤2: Cookie导入（增强）

v2.0.0提供3种导入方式：

**方式1: 浏览器插件（推荐）**
```
1. 安装Chrome扩展（项目内提供）
2. 登录KOOK网页版
3. 点击扩展图标
4. 一键导入Cookie
```

**方式2: 文件拖拽**
```
1. 将Cookie保存为JSON或TXT文件
2. 拖拽文件到导入区域
3. 系统自动解析和验证
```

**方式3: 文本粘贴**
```
1. 登录KOOK网页版（https://www.kookapp.cn）
2. 按F12打开开发者工具
3. Application → Cookies → kookapp.cn
4. 复制Cookie值并粘贴
```

#### 步骤3: 频道配置（智能映射）

**选择频道**：
1. 选择KOOK服务器和频道
2. 配置目标平台（Discord/Telegram/飞书）

**智能匹配（新功能）**：
- 点击"智能匹配"按钮
- 系统自动匹配频道（准确率75%+）
- 查看匹配结果和置信度
- 确认或手动调整映射

**拖拽界面（新功能）**：
- 左侧：KOOK频道列表
- 右侧：目标平台频道
- 拖拽：创建映射关系

#### 步骤4: 转发测试（新增）

**测试功能**：
1. 发送测试消息
2. 查看详细结果
3. 验证转发正常

#### 步骤5: 完成启动

- 查看实时监控
- 系统自动开始转发消息

**恭喜！安装和配置完成！** 🎉

整个过程只需5分钟！

---

## 🐳 方式2: Docker一键部署（推荐服务器用户）

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
# ✅ 拉取v2.0.0镜像
# ✅ 创建配置文件
# ✅ 启动服务
# ✅ 执行健康检查
# ✅ 显示访问地址

# ✅ 完成！3分钟搞定
```

### 方法B: 使用预构建镜像

```bash
# 拉取并运行v2.0.0
docker run -d \
  --name kook-forwarder \
  --restart unless-stopped \
  -p 9527:9527 \
  -p 9528:9528 \
  -v $(pwd)/data:/app/data \
  ghcr.io/gfchfjh/csbjjwt:2.0.0

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

# 更新到v2.0.0
docker-compose -f docker-compose.standalone.yml pull
docker-compose -f docker-compose.standalone.yml up -d

# 完全删除
docker-compose -f docker-compose.standalone.yml down -v
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
1. 下载v2.0.0安装包
2. 卸载旧版本（配置会自动保留）
3. 安装新版本
4. 启动应用
```

### Docker用户

```bash
# 更新到v2.0.0
docker pull ghcr.io/gfchfjh/csbjjwt:2.0.0
docker stop kook-forwarder
docker rm kook-forwarder
docker run -d --name kook-forwarder \
  -p 9527:9527 \
  -v kook-data:/app/data \
  ghcr.io/gfchfjh/csbjjwt:2.0.0
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
rm KOOK-Forwarder-*.AppImage

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

- 📖 [完整故障排查指南](docs/应用启动失败排查指南.md)
- 🔍 [环境检查工具](HOW_TO_USE_OPTIMIZATIONS.md#智能环境检查)
- 🛠️ [一键修复功能](HOW_TO_USE_OPTIMIZATIONS.md#一键修复)
- 🐛 [提交Bug](https://github.com/gfchfjh/CSBJJWT/issues/new?template=bug_report.md)

### 使用帮助

v2.0.0内置完整帮助系统：
1. 点击应用右上角"帮助"按钮
2. 或按 `F1` 快捷键
3. 查看教程、FAQ和视频

### 获取帮助

1. 查看日志文件
2. 使用内置诊断工具
3. 搜索已有Issues
4. 提交新Issue（附带日志和错误信息）

---

## 📚 下一步

安装完成后：

1. 📖 [快速开始指南](QUICK_START.md) - 5分钟上手
2. 📊 [v2.0.0完整优化报告](COMPLETE_OPTIMIZATION_REPORT.md) - 了解所有新功能
3. 🎯 [新功能使用指南](HOW_TO_USE_OPTIMIZATIONS.md) - 详细使用方法
4. 📚 [文档索引](INDEX.md) - 查看所有文档

---

<div align="center">

**如果觉得有帮助，请给个 Star 支持一下！**

[返回主页](README.md) | [快速开始](QUICK_START.md) | [查看新功能](HOW_TO_USE_OPTIMIZATIONS.md)

**KOOK消息转发系统 v2.0.0 - 从"技术工具"到"普通用户产品"的完美蜕变**

</div>
