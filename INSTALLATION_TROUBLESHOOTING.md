# KOOK消息转发系统 - 安装故障排查指南

**更新时间**: 2025-11-02  
**适用版本**: v18.0.1

---

## 📋 目录

1. [系统要求检查](#系统要求检查)
2. [安装方式选择](#安装方式选择)
3. [常见问题及解决方案](#常见问题及解决方案)
4. [详细安装步骤](#详细安装步骤)
5. [验证安装](#验证安装)

---

## 系统要求检查

### Windows系统

**最低要求**:
- Windows 10 x64 或更高版本
- 4GB RAM（推荐8GB）
- 500MB可用磁盘空间

**检查方法**:
```cmd
# 查看Windows版本
winver

# 查看内存
systeminfo | findstr /C:"Total Physical Memory"
```

### macOS系统

**最低要求**:
- macOS 10.15 (Catalina) 或更高版本
- 4GB RAM（推荐8GB）
- 500MB可用磁盘空间

**检查方法**:
```bash
# 查看macOS版本
sw_vers

# 查看内存
sysctl hw.memsize
```

### Linux系统

**最低要求**:
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+ / Arch Linux
- 4GB RAM（推荐8GB）
- 500MB可用磁盘空间

**检查方法**:
```bash
# 查看发行版
cat /etc/os-release

# 查看内存
free -h

# 查看磁盘空间
df -h
```

---

## 安装方式选择

### 🎯 推荐：方式1 - Electron桌面应用（最简单）

**优点**:
- ✅ 无需安装Python、Node.js
- ✅ 双击即可运行
- ✅ 所有依赖已打包

**适合**:
- 普通用户
- 不想配置环境的用户
- Windows/macOS/Linux桌面用户

**下载地址**: https://github.com/gfchfjh/CSBJJWT/releases/tag/v18.0.0

---

### 方式2 - 从源码安装（适合开发者）

**前置要求**:
- Python 3.11+
- Node.js 18+
- Redis（可选，项目自带）

**适合**:
- 开发者
- 需要自定义的用户
- 想要最新代码的用户

---

### 方式3 - Docker安装（适合服务器）

**前置要求**:
- Docker 20.10+
- Docker Compose 2.0+

**适合**:
- 服务器部署
- 容器化环境
- 云服务器

---

## 常见问题及解决方案

### 问题1: Windows下载的.exe文件被杀毒软件拦截

**现象**:
- 下载后文件被删除
- 运行时提示"Windows已保护你的电脑"
- 杀毒软件报告威胁

**原因**:
- PyInstaller打包的程序经常被误报
- 应用没有数字签名

**解决方案**:

#### 方案A: 添加信任（推荐）
1. 打开Windows安全中心
2. 进入"病毒和威胁防护"
3. 点击"病毒和威胁防护设置"
4. 添加应用到排除列表

#### 方案B: 临时禁用
1. 临时关闭杀毒软件
2. 下载并安装应用
3. 将安装目录添加到白名单
4. 重新启用杀毒软件

#### 方案C: 从源码安装
如果不信任预编译版本，可以从源码安装（见下文）

---

### 问题2: macOS提示"无法打开，因为它来自身份不明的开发者"

**现象**:
- 双击应用无法打开
- 提示"已损坏，无法打开"

**解决方案**:

#### 步骤1: 右键打开
```
1. 找到应用文件
2. 右键点击（或按住Control点击）
3. 选择"打开"
4. 在弹出的对话框中点击"打开"
```

#### 步骤2: 如果步骤1无效，执行以下命令
```bash
# 移除隔离属性
sudo xattr -rd com.apple.quarantine /Applications/KOOK消息转发系统.app

# 如果还是无法打开
sudo spctl --master-disable  # 临时允许任何来源
# 打开应用后再执行
sudo spctl --master-enable   # 恢复安全设置
```

#### 步骤3: 终极方案
如果以上方法都无效，从源码安装

---

### 问题3: Linux下AppImage无法运行

**现象**:
- 双击无反应
- 终端提示权限错误

**解决方案**:

#### 步骤1: 添加执行权限
```bash
chmod +x KOOK消息转发系统-16.0.0.AppImage
```

#### 步骤2: 安装依赖（某些发行版需要）
```bash
# Ubuntu/Debian
sudo apt-get install libfuse2

# Fedora
sudo dnf install fuse-libs

# Arch Linux
sudo pacman -S fuse2
```

#### 步骤3: 运行
```bash
./KOOK消息转发系统-16.0.0.AppImage
```

---

### 问题4: install.sh脚本执行失败

**现象**:
```bash
./install.sh
bash: ./install.sh: Permission denied
```

**解决方案**:

#### 步骤1: 添加执行权限
```bash
chmod +x install.sh
```

#### 步骤2: 重新运行
```bash
./install.sh
```

#### 步骤3: 如果仍然失败，手动执行
```bash
bash install.sh
```

---

### 问题5: Python版本不符合要求

**现象**:
```
Error: Python 3.11+ is required, but you have Python 3.9
```

**解决方案**:

#### Windows:
1. 访问 https://www.python.org/downloads/
2. 下载Python 3.11或更高版本
3. 安装时勾选"Add Python to PATH"
4. 重新运行install.bat

#### macOS:
```bash
# 使用Homebrew安装
brew install python@3.11

# 设置为默认版本
echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Linux:
```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev

# 设置为默认
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

---

### 问题6: Node.js版本不符合要求

**现象**:
```
Error: Node.js 18+ is required, but you have Node.js 16
```

**解决方案**:

#### Windows:
1. 访问 https://nodejs.org/
2. 下载LTS版本（18.x或20.x）
3. 运行安装程序
4. 重新运行install.bat

#### macOS/Linux:
```bash
# 使用nvm安装
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc  # 或 ~/.zshrc

nvm install 20
nvm use 20
nvm alias default 20
```

---

### 问题7: Redis连接失败

**现象**:
```
Error: Redis connection failed: Connection refused
```

**解决方案**:

#### 方案A: 使用内置Redis（推荐）
```bash
# 项目自带Redis，会自动启动
# 如果自动启动失败，手动启动：

# Windows
cd redis
start_redis.bat

# Linux/macOS
cd redis
./start_redis.sh
```

#### 方案B: 安装系统Redis
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Windows
# 下载: https://github.com/tporadowski/redis/releases
# 解压后运行 redis-server.exe
```

#### 方案C: 使用Docker Redis
```bash
docker run -d -p 6379:6379 redis:alpine
```

---

### 问题8: Playwright浏览器下载失败

**现象**:
```
Error: Failed to download Chromium
playwright._impl._api_types.Error: browserType.launch: Executable doesn't exist
```

**解决方案**:

#### 步骤1: 手动安装Playwright浏览器
```bash
# 进入虚拟环境（如果使用）
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装浏览器
playwright install chromium

# 如果网络问题，使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

#### 步骤2: 如果仍然失败，安装依赖
```bash
# Linux
playwright install-deps chromium

# 或者
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

---

### 问题9: 端口已被占用

**现象**:
```
Error: Address already in use: 127.0.0.1:9527
```

**解决方案**:

#### 方案A: 停止占用端口的进程
```bash
# Windows
netstat -ano | findstr :9527
taskkill /PID <进程ID> /F

# Linux/macOS
lsof -ti:9527 | xargs kill -9
```

#### 方案B: 更改端口
编辑配置文件 `backend/app/config.py`:
```python
# 修改端口号
API_PORT = 9528  # 改为其他端口
```

---

### 问题10: npm install失败

**现象**:
```
npm ERR! code ECONNREFUSED
npm ERR! errno ECONNREFUSED
```

**解决方案**:

#### 步骤1: 切换npm源
```bash
# 使用国内镜像（推荐）
npm config set registry https://registry.npmmirror.com

# 或使用淘宝镜像
npm config set registry https://registry.npm.taobao.org

# 清除缓存
npm cache clean --force
```

#### 步骤2: 重新安装
```bash
cd frontend
npm install
```

#### 步骤3: 如果还是失败，使用yarn
```bash
npm install -g yarn
yarn install
```

---

### 问题11: pip install失败

**现象**:
```
ERROR: Could not find a version that satisfies the requirement
```

**解决方案**:

#### 步骤1: 升级pip
```bash
python -m pip install --upgrade pip
```

#### 步骤2: 使用国内镜像
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 步骤3: 如果仍然失败，逐个安装
```bash
# 查看哪个包失败
pip install -r requirements.txt -v

# 单独安装失败的包
pip install <package_name> --no-cache-dir
```

---

### 问题12: 启动后浏览器无法访问

**现象**:
- 后端启动成功
- 浏览器打开 http://localhost:9527 无法访问
- 提示"无法访问此网站"

**解决方案**:

#### 步骤1: 检查后端是否真的启动
```bash
# 查看进程
# Windows
tasklist | findstr python

# Linux/macOS
ps aux | grep python
```

#### 步骤2: 检查端口监听
```bash
# Windows
netstat -ano | findstr :9527

# Linux/macOS
lsof -i:9527
```

#### 步骤3: 检查防火墙
```bash
# Windows
# 控制面板 -> 系统和安全 -> Windows Defender 防火墙
# 添加入站规则，允许端口9527

# Linux
sudo ufw allow 9527
sudo firewall-cmd --add-port=9527/tcp --permanent
```

#### 步骤4: 尝试其他地址
- http://127.0.0.1:9527
- http://0.0.0.0:9527

---

## 详细安装步骤

### 方式1: Electron桌面应用（推荐新手）

#### Windows用户

**步骤1: 下载安装包**
```
访问: https://github.com/gfchfjh/CSBJJWT/releases/tag/v18.0.0
下载: KOOK-Forwarder-v18.0.0-Windows.zip (112 MB)
```

**步骤2: 解压并安装**
```
1. 解压ZIP文件到任意目录
2. 进入 frontend/ 目录
3. 双击 "KOOK消息转发系统 Setup 18.0.0.exe"
4. 如果Windows提示"Windows已保护你的电脑"：
   - 点击"更多信息"
   - 点击"仍然运行"
5. 按照安装向导操作
6. 选择安装位置（默认: C:\Program Files\KOOK消息转发系统）
7. 完成安装
```

**步骤3: 首次启动**
```
1. 双击桌面快捷方式或开始菜单图标
2. 同意免责声明（必须）
3. 设置管理员密码（8-20位，包含大小写字母、数字、特殊字符）
4. 进入首次配置向导
5. 完成配置后即可使用
```

---

#### macOS用户

**步骤1: 下载DMG文件**
```
访问: https://github.com/gfchfjh/CSBJJWT/releases/tag/v18.0.0
下载: KOOK.-16.0.0-arm64.dmg (114 MB)
注意: 文件名显示为16.0.0，实际是18.0.0版本
```

**步骤2: 安装应用**
```
1. 双击打开DMG文件
2. 拖拽应用图标到"应用程序"文件夹
3. 打开"访达" -> "应用程序"
4. 找到"KOOK消息转发系统"
5. 右键点击 -> 选择"打开"
6. 在弹出的对话框中点击"打开"
   （首次打开必须右键，否则会被拦截）
```

**步骤3: 如果被拦截**
```bash
# 在终端执行
sudo xattr -rd com.apple.quarantine /Applications/KOOK消息转发系统.app
```

**步骤4: 首次启动**
```
同Windows用户的步骤3
```

---

#### Linux用户

**步骤1: 下载并解压**
```bash
# 下载
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v18.0.0/KOOK-Forwarder-v18.0.0-Linux.tar.gz

# 解压
tar -xzf KOOK-Forwarder-v18.0.0-Linux.tar.gz

# 进入目录
cd KOOK-Forwarder-v18.0.0-Linux/frontend
```

**步骤2: 安装依赖（某些发行版需要）**
```bash
# Ubuntu/Debian
sudo apt-get install libfuse2

# Fedora
sudo dnf install fuse-libs

# Arch Linux
sudo pacman -S fuse2
```

**步骤3: 添加执行权限并运行**
```bash
chmod +x *.AppImage
./KOOK消息转发系统-16.0.0.AppImage
```

**步骤4: 首次启动**
```
同Windows用户的步骤3
```

---

### 方式2: 从源码安装（适合开发者）

#### 前置条件检查

```bash
# 检查Python版本（需要3.11+）
python3 --version

# 检查Node.js版本（需要18+）
node --version

# 检查npm版本
npm --version

# 检查Git
git --version
```

如果缺少任何工具，请先安装。

---

#### 步骤1: 克隆仓库

```bash
# 克隆代码
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT
```

---

#### 步骤2: 安装后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium

# 初始化数据库
python -c "from app.database import db; db.init_database()"

# 返回项目根目录
cd ..
```

---

#### 步骤3: 安装前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 或使用国内镜像
npm install --registry=https://registry.npmmirror.com

# 构建前端（生产环境）
npm run build

# 或启动开发服务器（开发环境）
npm run dev

# 返回项目根目录
cd ..
```

---

#### 步骤4: 启动服务

##### 开发模式（推荐开发者）

**终端1: 启动后端**
```bash
cd backend
source venv/bin/activate  # 激活虚拟环境
python -m app.main
# 或使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 9527
```

**终端2: 启动前端**
```bash
cd frontend
npm run dev
```

**终端3: 启动Redis（如果需要）**
```bash
cd redis
./start_redis.sh  # Linux/macOS
# 或
start_redis.bat   # Windows
```

访问: http://localhost:5173

---

##### 生产模式

**使用自动启动脚本**:

```bash
# Windows
start.bat

# Linux/macOS
./start.sh
```

或**手动启动**:

```bash
# 1. 启动Redis
cd redis
./start_redis.sh &

# 2. 启动后端
cd backend
source venv/bin/activate
python -m app.main &

# 3. 如果使用Electron
cd frontend
npm run electron

# 或使用Web版本
# 浏览器打开 http://localhost:9527
```

---

#### 步骤5: 验证安装

```bash
# 检查后端API
curl http://localhost:9527/api/health

# 应该返回
{"status":"ok","version":"18.0.1"}

# 检查Redis
redis-cli ping
# 应该返回 PONG

# 检查Playwright
python -c "from playwright.sync_api import sync_playwright; sync_playwright()"
# 应该没有错误
```

---

### 方式3: Docker安装（适合服务器）

#### 步骤1: 确保Docker已安装

```bash
# 检查Docker
docker --version

# 检查Docker Compose
docker-compose --version
```

#### 步骤2: 克隆仓库

```bash
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT
```

#### 步骤3: 使用Docker Compose启动

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看运行状态
docker-compose ps
```

#### 步骤4: 访问应用

```
浏览器打开: http://localhost:9527
```

#### 步骤5: 停止服务

```bash
# 停止服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器和数据卷
docker-compose down -v
```

---

## 验证安装

### 1. 检查服务状态

```bash
# 检查后端是否运行
curl http://localhost:9527/api/health

# 检查Redis是否运行
redis-cli ping

# 检查进程
# Windows
tasklist | findstr python
tasklist | findstr node

# Linux/macOS
ps aux | grep python
ps aux | grep node
```

### 2. 检查端口监听

```bash
# Windows
netstat -ano | findstr :9527
netstat -ano | findstr :6379

# Linux/macOS
lsof -i:9527
lsof -i:6379
```

### 3. 检查日志

```bash
# 后端日志
tail -f backend/data/logs/app.log

# Redis日志
tail -f redis/redis.log
```

### 4. 功能测试

1. **打开浏览器访问** `http://localhost:9527`
2. **同意免责声明**
3. **设置管理员密码**
4. **添加KOOK账号**
5. **配置Bot（Discord/Telegram/飞书）**
6. **设置频道映射**
7. **启动服务**
8. **发送测试消息验证转发**

---

## 常用命令速查

### 启动服务
```bash
# 快速启动（推荐）
./start.sh          # Linux/macOS
start.bat           # Windows

# 或使用Electron应用
# 双击桌面图标
```

### 停止服务
```bash
# 终止所有相关进程
# Windows
taskkill /F /IM python.exe
taskkill /F /IM node.exe
taskkill /F /IM redis-server.exe

# Linux/macOS
pkill -f "python.*app.main"
pkill -f "node.*electron"
pkill redis-server
```

### 查看日志
```bash
# 实时查看后端日志
tail -f backend/data/logs/app.log

# 实时查看Electron日志（Windows）
type %APPDATA%\KOOK消息转发系统\logs\main.log

# 实时查看Electron日志（Linux/macOS）
tail -f ~/.config/KOOK消息转发系统/logs/main.log
```

### 清理数据
```bash
# 清理所有数据（谨慎操作）
rm -rf backend/data/*
rm -rf frontend/.cache/*
rm -rf redis/dump.rdb

# 或使用脚本
./scripts/clean_data.sh  # Linux/macOS
scripts\clean_data.bat   # Windows
```

### 更新代码
```bash
# 拉取最新代码
git pull origin main

# 更新后端依赖
cd backend
pip install -r requirements.txt --upgrade

# 更新前端依赖
cd frontend
npm install
npm run build

# 重启服务
./start.sh  # 或 start.bat
```

---

## 获取帮助

如果以上方法都无法解决您的问题，请：

### 1. 查看详细日志
```bash
# 后端日志
cat backend/data/logs/app.log

# Electron日志
# Windows: %APPDATA%\KOOK消息转发系统\logs\main.log
# macOS: ~/Library/Logs/KOOK消息转发系统/main.log
# Linux: ~/.config/KOOK消息转发系统/logs/main.log
```

### 2. 检查系统环境
```bash
# 运行环境检查脚本
python backend/scripts/check_environment.py
```

### 3. 提交Issue
访问: https://github.com/gfchfjh/CSBJJWT/issues

提供以下信息：
- 操作系统和版本
- Python版本
- Node.js版本
- 完整的错误日志
- 安装步骤
- 截图（如果有）

### 4. 查看文档
- 用户手册: `docs/USER_MANUAL.md`
- FAQ: `docs/FAQ.md`
- 开发指南: `docs/开发指南.md`

---

**祝您安装顺利！如果还有问题，请提供详细的错误信息。**
