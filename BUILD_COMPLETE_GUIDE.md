# 🚀 KOOK消息转发系统 - 完整构建指南

**版本**: v6.4.0  
**日期**: 2025-10-26  
**作者**: KOOK Forwarder Team  

---

## 📋 概述

本指南详细说明如何从源码构建KOOK消息转发系统的完整安装包。

**构建产物**:
- Windows: `KOOK-Forwarder-Setup-6.4.0.exe` (~250MB)
- macOS: `KOOK-Forwarder-6.4.0.dmg` (~300MB)
- Linux: `KOOK-Forwarder-6.4.0.AppImage` (~280MB)

**构建时间**（v6.4.0优化）:
- 首次构建: 15-20分钟（优化前：30-45分钟）⬇️50%
- 后续构建: 5-8分钟（优化前：15-20分钟）⬇️60%

**v6.4.0新增**: 统一构建脚本 `build_unified_enhanced.py`

---

## 🛠️ 前置要求

### 必需软件

| 软件 | 最低版本 | 推荐版本 | 用途 |
|------|---------|---------|------|
| Python | 3.11.0 | 3.11.x | 后端运行环境 |
| Node.js | 18.0.0 | 20.x | 前端构建 |
| npm | 9.0.0 | 10.x | 包管理器 |
| Git | 2.30+ | 最新 | 版本控制 |

### 平台特定要求

#### Windows
- Visual Studio Build Tools 2019+（C++编译支持）
- NSIS 3.08+（安装包制作）

#### macOS
- Xcode Command Line Tools
- Apple Developer账号（可选，用于代码签名）

#### Linux  
- GCC/G++ 9.0+
- make
- AppImageTool

### Python依赖

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Node.js依赖

```bash
cd frontend
npm install
```

---

## 📦 构建步骤

### 快速构建（推荐）

```bash
# 一键构建所有
./build_complete_installer.sh

# 构建特定平台
./build_complete_installer.sh --platform windows
./build_complete_installer.sh --platform mac
./build_complete_installer.sh --platform linux

# 包含Playwright浏览器（增加300MB）
./build_complete_installer.sh --pack-playwright

# 清理并重新构建
./build_complete_installer.sh --clean
```

---

### 分步骤构建

#### 步骤1: 构建Python后端（15-20分钟）

```bash
# 基础构建
./build_backend.sh

# 包含Playwright浏览器
./build_backend.sh --pack-playwright

# 清理并构建
./build_backend.sh --clean

# 构建并测试
./build_backend.sh --test
```

**输出**: `backend/dist/KookForwarder-Backend` 或 `.exe`

**验证**:
```bash
cd backend/dist
./KookForwarder-Backend  # Linux/macOS
# 或
./KookForwarder-Backend.exe  # Windows

# 测试健康检查
curl http://localhost:9527/health
# 应返回: {"status": "healthy"}
```

---

#### 步骤2: 构建Vue前端（5-10分钟）

```bash
cd frontend

# 安装依赖（首次）
npm install

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

**输出**: `frontend/dist/`

**验证**:
```bash
ls -la frontend/dist/
# 应包含: index.html, assets/, images/ 等
```

---

#### 步骤3: 打包Electron应用（10-15分钟）

```bash
cd frontend

# Windows
npm run electron:build:win

# macOS
npm run electron:build:mac

# Linux
npm run electron:build:linux

# 所有平台（需要跨平台工具）
npm run electron:build
```

**输出**: `frontend/dist-electron/`

**文件清单**:

Windows:
- `KOOK-Forwarder-6.0.0-Setup.exe` - NSIS安装程序
- `KOOK-Forwarder-6.0.0-Setup.exe.blockmap` - 更新用

macOS:
- `KOOK-Forwarder-6.0.0-macOS-x64.dmg` - Intel Mac
- `KOOK-Forwarder-6.0.0-macOS-arm64.dmg` - Apple Silicon
- `KOOK-Forwarder-6.0.0-macOS-universal.dmg` - 通用版

Linux:
- `KOOK-Forwarder-6.0.0-x64.AppImage` - AppImage
- `KOOK-Forwarder-6.0.0-amd64.deb` - Debian/Ubuntu
- `KOOK-Forwarder-6.0.0-x86_64.rpm` - RedHat/Fedora

---

## 🧪 测试构建结果

### Windows测试

```bash
# 安装
frontend/dist-electron/KOOK-Forwarder-6.0.0-Setup.exe

# 安装后运行
"C:\Program Files\KOOK消息转发系统\KOOK消息转发系统.exe"

# 检查日志
%USERPROFILE%\Documents\KookForwarder\data\logs\
```

### macOS测试

```bash
# 打开DMG
open frontend/dist-electron/KOOK-Forwarder-6.0.0-macOS.dmg

# 拖动到Applications后运行
/Applications/KOOK消息转发系统.app/Contents/MacOS/KOOK消息转发系统

# 检查日志
~/Documents/KookForwarder/data/logs/
```

### Linux测试

```bash
# 添加执行权限
chmod +x frontend/dist-electron/KOOK-Forwarder-6.0.0-x64.AppImage

# 运行
./frontend/dist-electron/KOOK-Forwarder-6.0.0-x64.AppImage

# 检查日志
~/Documents/KookForwarder/data/logs/
```

---

## 🔧 高级配置

### 代码签名

#### Windows代码签名

需要购买Authenticode证书（$100-300/年）:

```bash
# 使用signtool签名
signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 KookForwarder.exe
```

配置electron-builder:
```json
{
  "win": {
    "certificateFile": "path/to/certificate.pfx",
    "certificatePassword": "password"
  }
}
```

#### macOS代码签名

需要Apple Developer账号（$99/年）:

```bash
# 环境变量
export APPLE_ID=your@email.com
export APPLE_ID_PASSWORD=app-specific-password
export APPLE_TEAM_ID=YOUR_TEAM_ID

# electron-builder会自动签名和公证
npm run electron:build:mac
```

---

### Playwright浏览器处理

#### 方案A: 首次启动下载（推荐）

**优点**: 安装包小（~150MB）
**缺点**: 首次启动需要下载（~300MB，2-3分钟）

```bash
# 不打包浏览器
./build_backend.sh
```

首次启动时自动执行:
```python
# backend/app/main.py启动时
async def ensure_playwright_browser():
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            await p.chromium.launch()
    except:
        # 自动安装
        import subprocess
        subprocess.run(['playwright', 'install', 'chromium', '--with-deps'])
```

#### 方案B: 完整打包（备选）

**优点**: 开箱即用
**缺点**: 安装包大（~450MB）

```bash
# 打包浏览器
./build_backend.sh --pack-playwright
```

---

### 自定义配置

#### 修改应用信息

`frontend/package.json`:
```json
{
  "name": "your-app-name",
  "version": "6.0.0",
  "description": "Your description"
}
```

#### 修改图标

替换以下文件:
- Windows: `build/icon.ico` (256x256)
- macOS: `build/icon.icns` (多尺寸)
- Linux: `build/icons/` (16x16, 32x32, 48x48, 64x64, 128x128, 256x256, 512x512)

生成图标:
```bash
# 从PNG生成所有格式
npm install -g electron-icon-maker
electron-icon-maker --input=icon.png --output=build
```

#### 修改安装器外观

Windows NSIS:
- `build/installer-header.bmp` (150x57)
- `build/installer-sidebar.bmp` (164x314)

macOS DMG:
- `build/dmg-background.png` (540x380)

---

## 🐛 常见问题

### Q1: PyInstaller打包失败

**症状**: `ModuleNotFoundError: No module named 'XXX'`

**解决**:
```bash
# 添加到hiddenimports
# backend/build_backend_enhanced.spec

hiddenimports = [
    # ... 现有导入
    'your_missing_module',
]
```

### Q2: electron-builder打包失败

**症状**: `Cannot find module 'XXX'`

**解决**:
```bash
# 清理并重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Q3: macOS代码签名失败

**症状**: `Code signing error`

**解决**:
1. 确保已安装Xcode Command Line Tools
2. 确保Apple Developer证书已导入Keychain
3. 设置环境变量（见上文）

或跳过签名:
```bash
# 临时禁用签名
export CSC_IDENTITY_AUTO_DISCOVERY=false
npm run electron:build:mac
```

### Q4: Linux依赖问题

**症状**: `error while loading shared libraries`

**解决**:
```bash
# Ubuntu/Debian
sudo apt-get install -y libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils libatspi2.0-0 libsecret-1-0

# Fedora/RedHat
sudo dnf install -y gtk3 libnotify nss libXScrnSaver libXtst xdg-utils at-spi2-core libsecret
```

### Q5: Redis启动失败

**症状**: `Could not create server TCP listening socket`

**解决**:
```bash
# 检查端口占用
lsof -i :6379  # Linux/macOS
netstat -ano | findstr :6379  # Windows

# 修改端口
# backend/redis/redis.conf
port 6380
```

---

## 📊 构建优化

### 减小安装包体积

1. **不打包Playwright**: 节省300MB
2. **启用UPX压缩**: 节省30-50%
3. **排除开发依赖**: 节省50MB+
4. **压缩资源文件**: 节省10-20MB

### 提升构建速度

1. **使用缓存**:
```bash
# PyInstaller缓存
export PYINSTALLER_COMPILE_BOOTLOADER=1

# npm缓存
npm ci  # 使用package-lock.json
```

2. **并行构建**:
```bash
# 同时构建后端和前端
./build_backend.sh &
cd frontend && npm run build &
wait
```

3. **增量构建**:
```bash
# 跳过未修改的部分
./build_complete_installer.sh --skip-backend  # 仅重新构建前端
```

---

## 🚀 发布流程

### 1. 版本号更新

```bash
# 更新所有版本号
./update_version_numbers.sh 6.0.0
```

### 2. 构建所有平台

```bash
# 在各平台分别执行
./build_complete_installer.sh --platform all
```

### 3. 测试安装包

- [ ] Windows 10/11测试
- [ ] macOS 12/13测试（Intel和Apple Silicon）
- [ ] Ubuntu 20.04/22.04测试
- [ ] Fedora 38测试

### 4. 创建GitHub Release

```bash
# 使用gh CLI
gh release create v6.0.0 \
  frontend/dist-electron/*.exe \
  frontend/dist-electron/*.dmg \
  frontend/dist-electron/*.AppImage \
  frontend/dist-electron/*.deb \
  frontend/dist-electron/*.rpm \
  --title "v6.0.0 - 真正的傻瓜式一键安装" \
  --notes-file RELEASE_NOTES_v6.0.0.md
```

### 5. 更新文档

- [ ] 更新README.md
- [ ] 更新CHANGELOG.md
- [ ] 更新安装指南
- [ ] 发布公告

---

## 📈 持续集成（CI/CD）

### GitHub Actions配置

创建 `.github/workflows/build.yml`:

```yaml
name: Build Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: ./build_complete_installer.sh --platform windows
      - uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: frontend/dist-electron/*.exe
  
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: ./build_complete_installer.sh --platform mac
      - uses: actions/upload-artifact@v3
        with:
          name: macos-installer
          path: frontend/dist-electron/*.dmg
  
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: ./build_complete_installer.sh --platform linux
      - uses: actions/upload-artifact@v3
        with:
          name: linux-installer
          path: frontend/dist-electron/*.AppImage
```

---

## 📖 参考资料

- [PyInstaller文档](https://pyinstaller.org/en/stable/)
- [electron-builder文档](https://www.electron.build/)
- [NSIS文档](https://nsis.sourceforge.io/Docs/)
- [DMG制作指南](https://github.com/sindresorhus/create-dmg)
- [AppImage文档](https://appimage.org/)

---

## 🆘 获取帮助

- GitHub Issues: https://github.com/gfchfjh/CSBJJWT/issues
- Discussions: https://github.com/gfchfjh/CSBJJWT/discussions
- 文档: https://github.com/gfchfjh/CSBJJWT/docs

---

**祝构建顺利！** 🎉
