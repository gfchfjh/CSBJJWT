# 📥 KOOK消息转发系统 - 安装指南

> **三种安装方式，满足不同用户需求**

---

## 🎯 选择安装方式

| 方式 | 适合人群 | 难度 | 时间 | 体验 |
|------|---------|------|------|------|
| **方式1: 预编译安装包** | 普通用户 | ⭐ | 2分钟 | ⭐⭐⭐⭐⭐ |
| **方式2: 一键安装脚本** | 技术用户 | ⭐⭐ | 5分钟 | ⭐⭐⭐⭐ |
| **方式3: 源码安装** | 开发者 | ⭐⭐⭐ | 10分钟 | ⭐⭐⭐ |

---

## 🚀 方式1: 预编译安装包（推荐）⭐⭐⭐⭐⭐

**适合**: 普通用户，零代码基础

### 步骤1: 下载安装包

访问: https://github.com/gfchfjh/CSBJJWT/releases/latest

选择您的系统：

#### Windows (Win 10/11 x64)
```
下载: KookForwarder-Setup-1.13.1.exe (~450MB)
包含: Python + Node.js + Chromium + Redis + 所有依赖
```

#### macOS (10.15+, Intel/M1/M2)
```
下载: KookForwarder-1.13.1.dmg (~480MB)
包含: Python + Node.js + Chromium + Redis + 所有依赖
```

#### Linux (Ubuntu 20.04+)
```
下载: KookForwarder-1.13.1.AppImage (~420MB)
包含: Python + Node.js + Chromium + Redis + 所有依赖
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
chmod +x KookForwarder-1.13.1.AppImage

# 2. 运行
./KookForwarder-1.13.1.AppImage

# 3. （可选）添加到应用菜单
# Ubuntu/Debian:
./KookForwarder-1.13.1.AppImage --appimage-extract
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

## 🛠️ 方式2: 一键安装脚本 ⭐⭐⭐⭐

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

## 🔧 方式3: 源码安装（开发者）⭐⭐⭐

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

**如果觉得有帮助，请给个 ⭐ Star 支持一下！**

[返回主页](README.md) | [快速开始](QUICK_START.md) | [提交Issue](https://github.com/gfchfjh/CSBJJWT/issues)

</div>
