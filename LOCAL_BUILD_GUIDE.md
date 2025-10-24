# 🏗️ 本地构建完整指南

> **从零开始的本地构建详细步骤** - 适用于Windows/macOS/Linux

---

## 📋 目录

1. [环境要求](#环境要求)
2. [Windows构建指南](#windows构建指南)
3. [macOS构建指南](#macos构建指南)
4. [Linux构建指南](#linux构建指南)
5. [验证构建结果](#验证构建结果)
6. [故障排查](#故障排查)
7. [性能优化建议](#性能优化建议)

---

## 🔧 环境要求

### 最低配置

| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 10+, macOS 10.15+, Ubuntu 20.04+ |
| **CPU** | 4核心（推荐8核心） |
| **内存** | 8GB（推荐16GB） |
| **磁盘空间** | 15GB可用空间 |
| **网络** | 稳定的互联网连接 |

### 必需软件

| 软件 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11+ | 后端构建 |
| **Node.js** | 18+ | 前端构建 |
| **npm** | 9+ | 包管理 |
| **Git** | 2.0+ | 版本控制 |

---

## 🪟 Windows构建指南

### Step 1: 准备环境（10-15分钟）

#### 1.1 安装Python 3.11+

```powershell
# 方式1: 从官网下载
# 访问: https://www.python.org/downloads/
# 下载: Python 3.11.x Windows installer (64-bit)
# 安装时勾选 "Add Python to PATH"

# 方式2: 使用Chocolatey（如已安装）
choco install python311 -y

# 验证安装
python --version
# 应显示: Python 3.11.x
```

#### 1.2 安装Node.js 18+

```powershell
# 方式1: 从官网下载
# 访问: https://nodejs.org/
# 下载: LTS版本（18.x）

# 方式2: 使用Chocolatey
choco install nodejs-lts -y

# 验证安装
node --version
# 应显示: v18.x.x

npm --version
# 应显示: 9.x.x
```

#### 1.3 安装Git

```powershell
# 方式1: 从官网下载
# 访问: https://git-scm.com/download/win

# 方式2: 使用Chocolatey
choco install git -y

# 验证安装
git --version
# 应显示: git version 2.x.x
```

---

### Step 2: 克隆项目（2-3分钟）

```powershell
# 打开PowerShell或CMD

# 1. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git

# 2. 进入项目目录
cd CSBJJWT

# 3. 查看项目结构
dir
```

---

### Step 3: 安装Python依赖（5-10分钟）

```powershell
# 1. 升级pip
python -m pip install --upgrade pip

# 2. 安装后端依赖
cd backend
pip install -r requirements.txt

# 3. 安装PyInstaller
pip install pyinstaller

# 4. 安装Pillow（图像处理）
pip install Pillow

# 5. 安装Playwright浏览器
playwright install chromium

# 6. 验证安装
python -c "import playwright; print('Playwright OK')"
python -c "import fastapi; print('FastAPI OK')"

# 7. 返回项目根目录
cd ..
```

**如果网络慢，使用国内镜像：**
```powershell
pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### Step 4: 安装前端依赖（3-5分钟）

```powershell
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 如果网络慢，使用国内镜像
# npm config set registry https://registry.npmmirror.com
# npm install

# 3. 验证安装
npm list --depth=0

# 4. 返回项目根目录
cd ..
```

---

### Step 5: 生成图标文件（1分钟）

```powershell
# 1. 生成PNG图标
python build/generate_simple_icon.py

# 2. 生成平台图标
python build/create_platform_icons.py

# 3. 验证图标
dir build\icon.*
# 应显示: icon.ico, icon.png
```

---

### Step 6: 准备Redis（可选，3-5分钟）

```powershell
# 方式1: 自动准备（推荐）
python build/prepare_redis.py

# 方式2: 手动下载
# 访问: https://github.com/tporadowski/redis/releases
# 下载: Redis-x64-5.0.14.1.zip
# 解压到: redis/
```

---

### Step 7: 构建后端（5-10分钟）

```powershell
# 1. 进入后端目录
cd backend

# 2. 清理旧构建（如果存在）
if (Test-Path build) { Remove-Item -Recurse -Force build }
if (Test-Path dist) { Remove-Item -Recurse -Force dist }

# 3. 运行PyInstaller打包
pyinstaller --clean --noconfirm ..\build\build_backend.spec

# 4. 等待打包完成（5-10分钟）
# 看到 "Building EXE" 和 "completed successfully" 即成功

# 5. 验证输出
dir dist\KookForwarder-Backend\
# 应显示: KookForwarder-Backend.exe 及相关文件

# 6. 返回项目根目录
cd ..
```

**预期输出大小：**
- 可执行文件：80-120MB
- 总大小：150-200MB

---

### Step 8: 构建前端（3-5分钟）

```powershell
# 1. 进入前端目录
cd frontend

# 2. 构建Vue应用
npm run build

# 等待完成，看到 "build complete" 即成功

# 3. 验证Vue构建
dir dist\
# 应看到 index.html, assets/, 等文件

# 4. 返回项目根目录
cd ..
```

---

### Step 9: 打包Electron应用（5-8分钟）

```powershell
# 1. 进入前端目录
cd frontend

# 2. 打包Windows安装程序
npm run electron:build:win

# 3. 等待打包完成（5-8分钟）
# 会显示下载进度和打包进度
# 看到 "Packaging app" 和 "Building installer" 等信息

# 4. 查看输出
dir dist-electron\
# 应看到: KookForwarder Setup 1.14.0.exe

# 5. 检查文件大小
# 安装包应该在 400-500MB 左右
```

---

### Step 10: 验证构建（2-3分钟）

```powershell
# 返回项目根目录
cd ..

# 运行验证脚本
python build/verify_build.py

# 检查通过率
# 应该看到: ✅ 验证通过率: 90%+ 
```

---

### Step 11: 测试安装包（5-10分钟）

```powershell
# 1. 找到安装包
cd frontend\dist-electron

# 2. 双击运行安装程序
# "KookForwarder Setup 1.14.0.exe"

# 3. 按照向导安装
# - 选择安装路径
# - 点击"安装"
# - 等待安装完成

# 4. 启动应用测试
# - 从开始菜单启动
# - 或桌面快捷方式启动

# 5. 测试基本功能
# - 配置向导是否显示
# - 可以添加账号
# - 可以配置Bot
```

---

## 🍎 macOS构建指南

### Step 1: 准备环境（10-15分钟）

#### 1.1 安装Xcode Command Line Tools

```bash
# 安装命令行工具
xcode-select --install

# 等待安装完成后验证
xcode-select -p
# 应显示: /Library/Developer/CommandLineTools
```

#### 1.2 安装Homebrew（如未安装）

```bash
# 安装Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 验证安装
brew --version
```

#### 1.3 安装Python 3.11+

```bash
# 使用Homebrew安装
brew install python@3.11

# 验证安装
python3 --version
# 应显示: Python 3.11.x

# 创建软链接（可选）
brew link python@3.11
```

#### 1.4 安装Node.js 18+

```bash
# 使用Homebrew安装
brew install node@18

# 验证安装
node --version
# 应显示: v18.x.x

npm --version
# 应显示: 9.x.x
```

---

### Step 2: 克隆项目（2-3分钟）

```bash
# 打开终端

# 1. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git

# 2. 进入项目目录
cd CSBJJWT

# 3. 查看项目结构
ls -la
```

---

### Step 3: 安装Python依赖（5-10分钟）

```bash
# 1. 升级pip
python3 -m pip install --upgrade pip

# 2. 安装后端依赖
cd backend
pip3 install -r requirements.txt

# 3. 安装PyInstaller
pip3 install pyinstaller

# 4. 安装Pillow
pip3 install Pillow

# 5. 安装Playwright浏览器
playwright install chromium
playwright install-deps chromium

# 6. 验证安装
python3 -c "import playwright; print('Playwright OK')"
python3 -c "import fastapi; print('FastAPI OK')"

# 7. 返回项目根目录
cd ..
```

---

### Step 4: 安装前端依赖（3-5分钟）

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 验证安装
npm list --depth=0

# 4. 返回项目根目录
cd ..
```

---

### Step 5: 生成图标文件（1-2分钟）

```bash
# 1. 生成PNG图标
python3 build/generate_simple_icon.py

# 2. 生成平台图标（包括.icns）
python3 build/create_platform_icons.py

# 3. 手动创建.icns（如果脚本未创建）
mkdir -p icon.iconset
sips -z 16 16     build/icon-16.png --out icon.iconset/icon_16x16.png
sips -z 32 32     build/icon-32.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     build/icon-32.png --out icon.iconset/icon_32x32.png
sips -z 64 64     build/icon-64.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   build/icon-128.png --out icon.iconset/icon_128x128.png
sips -z 256 256   build/icon-256.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   build/icon-256.png --out icon.iconset/icon_256x256.png
sips -z 512 512   build/icon-512.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   build/icon-512.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 build/icon-1024.png --out icon.iconset/icon_512x512@2x.png

# 生成.icns文件
iconutil -c icns icon.iconset -o build/icon.icns

# 清理临时目录
rm -rf icon.iconset

# 4. 验证图标
ls -lh build/icon.*
# 应显示: icon.icns, icon.png
```

---

### Step 6: 准备Redis（可选，3-5分钟）

```bash
# 方式1: 使用Homebrew安装（推荐）
brew install redis

# 方式2: 自动准备脚本
python3 build/prepare_redis.py

# 验证Redis
redis-server --version
```

---

### Step 7: 构建后端（5-10分钟）

```bash
# 1. 进入后端目录
cd backend

# 2. 清理旧构建
rm -rf build dist

# 3. 运行PyInstaller打包
pyinstaller --clean --noconfirm ../build/build_backend.spec

# 4. 等待打包完成（5-10分钟）
# 看到 "Building EXE" 和 "completed successfully" 即成功

# 5. 验证输出
ls -lh dist/KookForwarder-Backend/
# 应显示: KookForwarder-Backend 及相关文件

# 6. 检查可执行权限
chmod +x dist/KookForwarder-Backend/KookForwarder-Backend

# 7. 返回项目根目录
cd ..
```

---

### Step 8: 构建前端（3-5分钟）

```bash
# 1. 进入前端目录
cd frontend

# 2. 构建Vue应用
npm run build

# 3. 验证Vue构建
ls -la dist/
# 应看到 index.html, assets/, 等文件

# 4. 返回项目根目录
cd ..
```

---

### Step 9: 打包Electron应用（5-8分钟）

```bash
# 1. 进入前端目录
cd frontend

# 2. 打包macOS应用
npm run electron:build:mac

# 3. 等待打包完成（5-8分钟）
# 会显示下载进度和打包进度

# 4. 查看输出
ls -lh dist-electron/
# 应看到: KookForwarder-1.14.0.dmg

# 5. 检查文件大小
# DMG应该在 450-500MB 左右
```

---

### Step 10: 验证和测试（5-10分钟）

```bash
# 1. 返回项目根目录
cd ..

# 2. 运行验证脚本
python3 build/verify_build.py

# 3. 测试DMG安装
open frontend/dist-electron/KookForwarder-1.14.0.dmg

# 4. 拖动应用到Applications文件夹

# 5. 首次运行
# 右键点击应用 → 打开（绕过安全检查）

# 6. 测试基本功能
```

---

## 🐧 Linux构建指南

### Step 1: 准备环境（10-15分钟）

#### 1.1 安装系统依赖

**Ubuntu/Debian:**
```bash
# 更新包列表
sudo apt update

# 安装必需软件
sudo apt install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    libfuse2

# 验证安装
python3 --version
node --version
npm --version
git --version
```

**CentOS/RHEL:**
```bash
# 安装必需软件
sudo yum install -y \
    python3 \
    python3-pip \
    nodejs \
    npm \
    git \
    gcc \
    openssl-devel \
    libffi-devel \
    fuse-libs

# 验证安装
python3 --version
node --version
```

**Arch Linux:**
```bash
# 安装必需软件
sudo pacman -S --noconfirm \
    python \
    python-pip \
    nodejs \
    npm \
    git \
    base-devel \
    fuse2

# 验证安装
python --version
node --version
```

---

### Step 2: 克隆项目（2-3分钟）

```bash
# 打开终端

# 1. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git

# 2. 进入项目目录
cd CSBJJWT

# 3. 查看项目结构
ls -la
```

---

### Step 3: 安装Python依赖（5-10分钟）

```bash
# 1. 升级pip
python3 -m pip install --upgrade pip

# 2. 安装后端依赖
cd backend
pip3 install -r requirements.txt

# 3. 安装PyInstaller
pip3 install pyinstaller

# 4. 安装Pillow
pip3 install Pillow

# 5. 安装Playwright浏览器
playwright install chromium
playwright install-deps chromium

# 6. 验证安装
python3 -c "import playwright; print('Playwright OK')"
python3 -c "import fastapi; print('FastAPI OK')"

# 7. 返回项目根目录
cd ..
```

---

### Step 4: 安装前端依赖（3-5分钟）

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 验证安装
npm list --depth=0

# 4. 返回项目根目录
cd ..
```

---

### Step 5: 生成图标文件（1分钟）

```bash
# 1. 生成PNG图标
python3 build/generate_simple_icon.py

# 2. 生成平台图标
python3 build/create_platform_icons.py

# 3. 验证图标
ls -lh build/icon.*
# 应显示: icon.png
```

---

### Step 6: 准备Redis（可选，3-5分钟）

```bash
# 方式1: 使用系统包管理器（推荐）
# Ubuntu/Debian
sudo apt install redis-server

# CentOS/RHEL
sudo yum install redis

# Arch Linux
sudo pacman -S redis

# 方式2: 自动准备脚本
python3 build/prepare_redis.py

# 验证Redis
redis-server --version
```

---

### Step 7: 构建后端（5-10分钟）

```bash
# 1. 进入后端目录
cd backend

# 2. 清理旧构建
rm -rf build dist

# 3. 运行PyInstaller打包
pyinstaller --clean --noconfirm ../build/build_backend.spec

# 4. 等待打包完成（5-10分钟）

# 5. 验证输出
ls -lh dist/KookForwarder-Backend/
# 应显示: KookForwarder-Backend 及相关文件

# 6. 设置可执行权限
chmod +x dist/KookForwarder-Backend/KookForwarder-Backend

# 7. 返回项目根目录
cd ..
```

---

### Step 8: 构建前端（3-5分钟）

```bash
# 1. 进入前端目录
cd frontend

# 2. 构建Vue应用
npm run build

# 3. 验证Vue构建
ls -la dist/
# 应看到 index.html, assets/, 等文件

# 4. 返回项目根目录
cd ..
```

---

### Step 9: 打包Electron应用（5-8分钟）

```bash
# 1. 进入前端目录
cd frontend

# 2. 打包Linux应用
npm run electron:build:linux

# 3. 等待打包完成（5-8分钟）

# 4. 查看输出
ls -lh dist-electron/
# 应看到: KookForwarder-1.14.0.AppImage

# 5. 设置可执行权限
chmod +x dist-electron/*.AppImage

# 6. 检查文件大小
# AppImage应该在 400-450MB 左右
```

---

### Step 10: 验证和测试（5-10分钟）

```bash
# 1. 返回项目根目录
cd ..

# 2. 运行验证脚本
python3 build/verify_build.py

# 3. 测试AppImage
./frontend/dist-electron/KookForwarder-1.14.0.AppImage

# 4. 测试基本功能
# - 配置向导
# - 添加账号
# - 配置Bot
```

---

## ✅ 验证构建结果

### 自动验证

```bash
# 运行验证脚本
python3 build/verify_build.py

# 期望结果：
# ✅ 验证通过率: 90%+
# ✅ 所有图标文件存在
# ✅ 配置文件完整
# ✅ 构建产物存在
# ✅ 安装包大小正常
```

### 手动验证检查清单

#### 1. 文件完整性

```bash
# 检查后端构建
ls -lh backend/dist/KookForwarder-Backend/

# 检查前端构建
ls -lh frontend/dist/

# 检查安装包
ls -lh frontend/dist-electron/
```

#### 2. 文件大小检查

| 文件 | 预期大小 | 说明 |
|------|---------|------|
| 后端可执行文件 | 80-120MB | 单个文件 |
| 后端总大小 | 150-200MB | 包含所有依赖 |
| Vue构建产物 | 10-20MB | dist目录 |
| Windows安装包 | 400-500MB | .exe文件 |
| macOS安装包 | 450-500MB | .dmg文件 |
| Linux安装包 | 400-450MB | .AppImage文件 |

#### 3. 功能测试

**测试项目：**
- [ ] 应用能够正常启动
- [ ] 配置向导显示正常
- [ ] 可以添加KOOK账号
- [ ] 可以配置Discord/Telegram/飞书Bot
- [ ] 可以创建频道映射
- [ ] 可以发送测试消息
- [ ] 日志页面正常显示
- [ ] 设置页面功能正常

---

## 🔧 故障排查

### 问题1: PyInstaller打包失败

**错误信息：** `ModuleNotFoundError: No module named 'xxx'`

**解决方案：**
```bash
# 方案1: 重新安装依赖
pip3 install --force-reinstall -r backend/requirements.txt

# 方案2: 添加到hiddenimports
# 编辑 build/build_backend.spec
# 在hiddenimports列表中添加缺失的模块

# 方案3: 使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r backend/requirements.txt
pyinstaller build/build_backend.spec
```

---

### 问题2: Electron打包失败

**错误信息：** `ENOENT: no such file or directory`

**解决方案：**
```bash
# 方案1: 清理缓存重试
cd frontend
rm -rf node_modules dist dist-electron
npm install
npm run build
npm run electron:build

# 方案2: 检查图标文件
ls build/icon.{ico,icns,png}
python3 build/create_platform_icons.py

# 方案3: 检查Vue构建
npm run build
ls dist/index.html  # 必须存在
```

---

### 问题3: Playwright安装失败

**错误信息：** `Failed to download browser`

**解决方案：**
```bash
# 方案1: 使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium

# 方案2: 手动安装
playwright install chromium --with-deps

# 方案3: 跳过下载（构建时）
# 设置环境变量
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
```

---

### 问题4: 内存不足

**错误信息：** `JavaScript heap out of memory`

**解决方案：**
```bash
# 增加Node.js内存限制
export NODE_OPTIONS="--max-old-space-size=4096"

# Windows PowerShell
$env:NODE_OPTIONS="--max-old-space-size=4096"

# 然后重新运行构建
npm run electron:build
```

---

### 问题5: 权限问题（Linux/macOS）

**错误信息：** `Permission denied`

**解决方案：**
```bash
# 添加执行权限
chmod +x build_installer.sh
chmod +x backend/dist/KookForwarder-Backend/*
chmod +x frontend/dist-electron/*.AppImage

# 如果需要sudo
sudo chown -R $USER:$USER .
```

---

## ⚡ 性能优化建议

### 1. 加速依赖安装

#### Python镜像源
```bash
# 临时使用
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久配置
pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### npm镜像源
```bash
# 临时使用
npm install --registry=https://registry.npmmirror.com

# 永久配置
npm config set registry https://registry.npmmirror.com
```

---

### 2. 并行构建

```bash
# 使用所有CPU核心
export MAKEFLAGS="-j$(nproc)"  # Linux
export MAKEFLAGS="-j$(sysctl -n hw.ncpu)"  # macOS

# PyInstaller并行
pyinstaller --log-level=WARN build/build_backend.spec
```

---

### 3. 缓存优化

```bash
# npm缓存
npm ci  # 使用package-lock.json，更快

# PyInstaller缓存
# 不清理build目录，增量构建更快
pyinstaller build/build_backend.spec  # 不加--clean
```

---

### 4. 减少打包大小

#### 排除不必要的文件
编辑 `build/build_backend.spec`:
```python
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'tkinter',
    'PyQt5',
    'PySide2',
    'jupyter',
    'notebook',
]
```

#### 使用UPX压缩
```python
# 在build_backend.spec中
exe = EXE(
    ...
    upx=True,  # 启用UPX压缩
    upx_exclude=[],
    ...
)
```

---

## 📊 构建时间参考

| 阶段 | Windows | macOS | Linux |
|------|---------|-------|-------|
| 环境准备 | 10-15分钟 | 10-15分钟 | 10-15分钟 |
| 依赖安装 | 8-15分钟 | 8-15分钟 | 8-15分钟 |
| 后端构建 | 5-10分钟 | 5-10分钟 | 5-10分钟 |
| 前端构建 | 3-5分钟 | 3-5分钟 | 3-5分钟 |
| Electron打包 | 5-8分钟 | 5-8分钟 | 5-8分钟 |
| **总计** | **31-53分钟** | **31-53分钟** | **31-53分钟** |

**实际时间受以下因素影响：**
- CPU性能
- 内存大小
- 磁盘速度
- 网络速度
- 是否首次构建

---

## 📝 构建日志

### 保存构建日志

```bash
# Windows PowerShell
.\build_installer.bat 2>&1 | Tee-Object -FilePath build.log

# Linux/macOS
./build_installer.sh 2>&1 | tee build.log
```

### 查看详细日志

```bash
# PyInstaller详细日志
pyinstaller --log-level=DEBUG build/build_backend.spec 2>&1 | tee pyinstaller.log

# Electron打包详细日志
DEBUG=electron-builder npm run electron:build 2>&1 | tee electron.log
```

---

## 🎯 快速构建命令汇总

### Windows（一键构建）
```powershell
# 完整构建
.\build_installer.bat

# 或分步骤
python build\generate_simple_icon.py
python build\create_platform_icons.py
pip install -r backend\requirements.txt
pip install pyinstaller
cd backend && pyinstaller --clean ..\build\build_backend.spec && cd ..
cd frontend && npm install && npm run build && npm run electron:build:win && cd ..
python build\verify_build.py
```

### macOS（一键构建）
```bash
# 完整构建
./build_installer.sh

# 或分步骤
python3 build/generate_simple_icon.py
python3 build/create_platform_icons.py
pip3 install -r backend/requirements.txt
pip3 install pyinstaller
cd backend && pyinstaller --clean ../build/build_backend.spec && cd ..
cd frontend && npm install && npm run build && npm run electron:build:mac && cd ..
python3 build/verify_build.py
```

### Linux（一键构建）
```bash
# 完整构建
./build_installer.sh

# 或分步骤（同macOS）
```

---

## 📞 获取帮助

**遇到问题？**

1. 查看[故障排查](#故障排查)章节
2. 查看构建日志文件
3. 运行验证脚本：`python3 build/verify_build.py`
4. 查看项目Issues：https://github.com/gfchfjh/CSBJJWT/issues

**相关文档：**
- [PRE_BUILD_CHECKLIST.md](PRE_BUILD_CHECKLIST.md) - 构建前检查
- [BUILD_EXECUTION_GUIDE.md](BUILD_EXECUTION_GUIDE.md) - 详细指南
- [BUILD_TOOLS_README.md](BUILD_TOOLS_README.md) - 工具说明

---

**最后更新：** 2025-10-24  
**适用版本：** v1.18.0  
**文档版本：** 2.0
