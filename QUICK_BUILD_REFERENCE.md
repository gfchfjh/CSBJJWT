# ⚡ 快速构建参考卡片

> **命令速查表** - 复制粘贴即可使用

---

## 🚀 三种构建方式

### 方式1: GitHub Actions ⭐ **最推荐**

```bash
# 一键触发（自动构建3个平台）
./release_package.sh

# 15-20分钟后访问
# https://github.com/gfchfjh/CSBJJWT/releases
```

**优点：** 无需本地环境，自动测试，3平台并行

---

### 方式2: 一键脚本

```bash
# Linux/macOS
./BUILD_QUICKSTART.sh
./build_installer.sh

# Windows
BUILD_QUICKSTART.sh
build_installer.bat
```

**优点：** 简单快速，适合有环境的用户

---

### 方式3: 手动构建（详细控制）

查看 [LOCAL_BUILD_GUIDE.md](LOCAL_BUILD_GUIDE.md)

---

## 📋 Windows快速构建

```powershell
# 1. 安装环境（首次）
choco install python311 nodejs-lts git -y

# 2. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 3. 准备资源
python build\generate_simple_icon.py
python build\create_platform_icons.py

# 4. 安装依赖
pip install -r backend\requirements.txt
pip install pyinstaller Pillow
playwright install chromium
cd frontend && npm install && cd ..

# 5. 构建
cd backend && pyinstaller --clean ..\build\build_backend.spec && cd ..
cd frontend && npm run build && npm run electron:build:win && cd ..

# 6. 验证
python build\verify_build.py

# 7. 查看输出
dir frontend\dist-electron\*.exe
```

**输出：** `KookForwarder Setup 1.13.3.exe` (~450MB)

---

## 📋 macOS快速构建

```bash
# 1. 安装环境（首次）
brew install python@3.11 node@18 git

# 2. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 3. 准备资源
python3 build/generate_simple_icon.py
python3 build/create_platform_icons.py

# 创建.icns（macOS专用）
mkdir icon.iconset
sips -z 16 16 build/icon-16.png --out icon.iconset/icon_16x16.png
sips -z 32 32 build/icon-32.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32 build/icon-32.png --out icon.iconset/icon_32x32.png
sips -z 64 64 build/icon-64.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128 build/icon-128.png --out icon.iconset/icon_128x128.png
sips -z 256 256 build/icon-256.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256 build/icon-256.png --out icon.iconset/icon_256x256.png
sips -z 512 512 build/icon-512.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512 build/icon-512.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 build/icon-1024.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset -o build/icon.icns
rm -rf icon.iconset

# 4. 安装依赖
pip3 install -r backend/requirements.txt
pip3 install pyinstaller Pillow
playwright install chromium
cd frontend && npm install && cd ..

# 5. 构建
cd backend && pyinstaller --clean ../build/build_backend.spec && cd ..
cd frontend && npm run build && npm run electron:build:mac && cd ..

# 6. 验证
python3 build/verify_build.py

# 7. 查看输出
ls -lh frontend/dist-electron/*.dmg
```

**输出：** `KookForwarder-1.13.3.dmg` (~480MB)

---

## 📋 Linux快速构建

```bash
# 1. 安装环境（首次，Ubuntu/Debian）
sudo apt update
sudo apt install -y python3.11 python3-pip nodejs npm git \
    build-essential libssl-dev libffi-dev libfuse2

# 2. 克隆项目
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 3. 准备资源
python3 build/generate_simple_icon.py
python3 build/create_platform_icons.py

# 4. 安装依赖
pip3 install -r backend/requirements.txt
pip3 install pyinstaller Pillow
playwright install chromium
playwright install-deps chromium
cd frontend && npm install && cd ..

# 5. 构建
cd backend && pyinstaller --clean ../build/build_backend.spec && cd ..
cd frontend && npm run build && npm run electron:build:linux && cd ..

# 6. 验证
python3 build/verify_build.py

# 7. 查看输出
ls -lh frontend/dist-electron/*.AppImage
```

**输出：** `KookForwarder-1.13.3.AppImage` (~420MB)

---

## 🔍 验证命令

```bash
# 运行完整验证
python3 build/verify_build.py

# 快速检查
ls -lh build/icon.*              # 图标文件
ls -lh backend/dist/             # 后端构建
ls -lh frontend/dist/            # Vue构建
ls -lh frontend/dist-electron/   # 安装包
```

---

## ⏱️ 时间估算

| 步骤 | Windows | macOS | Linux |
|------|---------|-------|-------|
| 环境准备 | 10-15分 | 10-15分 | 10-15分 |
| 依赖安装 | 8-15分 | 8-15分 | 8-15分 |
| 图标生成 | 1分 | 2分 | 1分 |
| 后端构建 | 5-10分 | 5-10分 | 5-10分 |
| 前端构建 | 3-5分 | 3-5分 | 3-5分 |
| Electron打包 | 5-8分 | 5-8分 | 5-8分 |
| 验证测试 | 5-10分 | 5-10分 | 5-10分 |
| **总计** | **37-68分** | **38-70分** | **37-68分** |

---

## 💾 磁盘空间需求

| 项目 | 大小 |
|------|------|
| 项目源码 | ~100MB |
| Python依赖 | ~500MB |
| Node依赖 | ~800MB |
| Playwright浏览器 | ~170MB |
| 后端构建 | ~200MB |
| 前端构建 | ~50MB |
| 临时文件 | ~1GB |
| 最终安装包 | 400-500MB |
| **总计** | **~3.2GB** |

**建议：** 至少10GB可用磁盘空间

---

## 🔧 常用命令

### 清理缓存
```bash
# 清理Python构建
rm -rf backend/build backend/dist

# 清理前端构建
rm -rf frontend/dist frontend/dist-electron

# 清理依赖（谨慎）
rm -rf frontend/node_modules

# 完全清理
git clean -fdx -e node_modules
```

### 重新构建
```bash
# 后端
cd backend && pyinstaller --clean ../build/build_backend.spec && cd ..

# 前端
cd frontend && npm run build && npm run electron:build && cd ..
```

### 测试构建产物
```bash
# 测试后端可执行文件
./backend/dist/KookForwarder-Backend/KookForwarder-Backend --version

# 测试安装包
./frontend/dist-electron/*.AppImage  # Linux
open frontend/dist-electron/*.dmg    # macOS
# 双击.exe                           # Windows
```

---

## 📞 获取帮助

**详细文档：**
- [LOCAL_BUILD_GUIDE.md](LOCAL_BUILD_GUIDE.md) - 1000+行详细指南
- [BUILD_EXECUTION_GUIDE.md](BUILD_EXECUTION_GUIDE.md) - 执行指南
- [PRE_BUILD_CHECKLIST.md](PRE_BUILD_CHECKLIST.md) - 检查清单

**快速命令：**
```bash
# 查看工具说明
cat BUILD_TOOLS_README.md

# 运行快速准备
./BUILD_QUICKSTART.sh

# 验证构建
python3 build/verify_build.py
```

---

**打印此卡片：** 
```bash
cat QUICK_BUILD_REFERENCE.md
```

**最后更新：** 2025-10-23  
**版本：** v1.13.3
