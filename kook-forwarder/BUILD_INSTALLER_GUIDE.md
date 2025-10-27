# 一键安装包构建指南

**版本**: v6.7.0  
**更新日期**: 2025-10-27  
**✅ P0-1优化**: 真正的一键安装包系统

---

## 🎯 概述

本系统提供完整的一键安装包构建流程，支持：
- ✅ Windows `.exe` 安装程序（NSIS）
- ✅ macOS `.dmg` 磁盘镜像
- ✅ Linux `.AppImage` 便携应用

所有安装包自动集成：
- ✅ Python运行时（无需用户安装Python）
- ✅ 嵌入式Redis（自动启动）
- ✅ Chromium浏览器（首次启动自动下载）
- ✅ 所有Python依赖库
- ✅ 完整的前端资源

---

## 🚀 快速开始

### 一键构建（推荐）

```bash
# Linux/macOS
python3 build/build_installer_ultimate.py --clean

# Windows
python build\build_installer_ultimate.py --clean
```

### 构建特定平台

```bash
# 仅构建Windows安装包
python build/build_installer_ultimate.py --platform windows --clean

# 仅构建macOS安装包
python build/build_installer_ultimate.py --platform macos --clean

# 仅构建Linux安装包
python build/build_installer_ultimate.py --platform linux --clean

# 构建所有平台（需要在对应系统上运行）
python build/build_installer_ultimate.py --platform all --clean
```

---

## 📋 前置条件

### Windows构建环境

1. **Python 3.11+**
   ```bash
   python --version
   ```

2. **Node.js 18+**
   ```bash
   node --version
   npm --version
   ```

3. **PyInstaller**
   ```bash
   pip install pyinstaller
   ```

4. **NSIS（安装程序打包工具）**
   - 下载: https://nsis.sourceforge.io/
   - 安装后确保 `makensis` 在PATH中

5. **Redis预编译版本**
   - 下载: https://github.com/tporadowski/redis/releases
   - 解压到 `build/redis/`

### macOS构建环境

1. **Xcode Command Line Tools**
   ```bash
   xcode-select --install
   ```

2. **Python 3.11+**
   ```bash
   python3 --version
   ```

3. **Node.js 18+**
   ```bash
   brew install node
   ```

4. **PyInstaller**
   ```bash
   pip3 install pyinstaller
   ```

5. **代码签名证书（可选，用于公证）**
   - Apple Developer账号
   - 开发者证书

### Linux构建环境

1. **Python 3.11+**
   ```bash
   sudo apt install python3.11 python3.11-venv python3.11-dev
   ```

2. **Node.js 18+**
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

3. **构建工具**
   ```bash
   sudo apt install -y build-essential libssl-dev libffi-dev
   ```

4. **AppImage工具**
   ```bash
   # electron-builder会自动处理
   ```

---

## 🔧 详细构建步骤

### 步骤1: 清理旧文件

```bash
python build/build_installer_ultimate.py --clean
```

这将删除：
- `dist/` 目录（旧的安装包）
- `build/backend/` 和 `build/frontend/` 目录
- `backend/dist/` 和 `frontend/dist/` 目录

### 步骤2: 准备依赖

自动执行以下操作：

1. **下载Redis**
   - Windows: 从GitHub下载预编译版本
   - macOS/Linux: 下载源码并编译

2. **下载Chromium**
   ```bash
   playwright install chromium
   ```

3. **安装Python依赖**
   ```bash
   pip install -r backend/requirements.txt
   ```

### 步骤3: 构建后端

使用PyInstaller将Python后端打包为单文件可执行程序：

```bash
cd backend
pyinstaller build_backend_enhanced.spec
```

生成文件：
- `backend/dist/kook-forwarder-backend` (Linux/macOS)
- `backend/dist/kook-forwarder-backend.exe` (Windows)

### 步骤4: 构建前端

1. **安装npm依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **构建Vue资源**
   ```bash
   npm run build
   ```
   
   生成 `frontend/dist/` 目录

3. **打包Electron应用**
   ```bash
   # Windows
   npm run electron:build:win
   
   # macOS
   npm run electron:build:mac
   
   # Linux
   npm run electron:build:linux
   ```

### 步骤5: 集成资源

将以下资源复制到安装包：
- Redis可执行文件
- Chromium浏览器（或下载脚本）
- 配置模板
- 文档和教程

### 步骤6: 生成安装包

#### Windows（NSIS）
```bash
makensis build/installer.nsi
```

生成: `dist/KOOK-Forwarder-Setup-6.7.0.exe`

#### macOS（DMG）
```bash
# electron-builder自动生成
```

生成: `dist/KOOK-Forwarder-6.7.0.dmg`

#### Linux（AppImage）
```bash
# electron-builder自动生成
```

生成: `dist/KOOK-Forwarder-6.7.0.AppImage`

### 步骤7: 生成校验和

```bash
# 自动生成checksums.json
```

包含所有安装包的SHA256哈希值。

---

## 📦 安装包结构

### Windows安装包内容

```
KOOK-Forwarder/
├── KOOK-Forwarder.exe           # Electron主程序
├── resources/
│   ├── app.asar                 # 打包的前端资源
│   ├── redis/
│   │   ├── redis-server.exe
│   │   └── redis.conf
│   ├── backend/
│   │   └── kook-forwarder-backend.exe
│   └── config_templates/
├── locales/                     # 语言文件
└── README.txt                   # 快速开始
```

### macOS DMG内容

```
KOOK消息转发系统.app/
└── Contents/
    ├── MacOS/
    │   └── KOOK消息转发系统
    ├── Resources/
    │   ├── app.asar
    │   ├── redis/
    │   └── backend/
    └── Info.plist
```

### Linux AppImage内容

```
KOOK-Forwarder.AppImage
├── AppRun
├── kook-forwarder
├── resources/
└── usr/
```

---

## 🎬 使用安装包

### Windows

1. 双击 `KOOK-Forwarder-Setup-6.7.0.exe`
2. 按照向导完成安装
3. 安装完成后自动启动
4. 首次启动会自动：
   - 启动Redis服务
   - 下载Chromium（带进度条）
   - 显示3步配置向导

### macOS

1. 打开 `KOOK-Forwarder-6.7.0.dmg`
2. 拖动应用到"应用程序"文件夹
3. 首次打开：右键 → 打开（绕过安全检查）
4. 自动启动配置向导

### Linux

1. 赋予执行权限：
   ```bash
   chmod +x KOOK-Forwarder-6.7.0.AppImage
   ```

2. 双击运行或命令行：
   ```bash
   ./KOOK-Forwarder-6.7.0.AppImage
   ```

3. 自动启动配置向导

---

## ⚙️ 自定义配置

### 修改应用图标

替换以下文件：
- Windows: `build/icon.ico`
- macOS: `build/icon.icns`
- Linux: `build/icon.png`

### 修改应用名称

编辑 `frontend/package.json`:
```json
{
  "name": "kook-forwarder-frontend",
  "productName": "KOOK消息转发系统",  // <- 修改这里
  "version": "6.7.0"
}
```

### 添加启动参数

编辑 `frontend/electron/main.js` 的 `createWindow` 函数。

---

## 🐛 常见问题

### Q: PyInstaller打包失败？

**A**: 检查以下几点：
1. 确保所有依赖已安装: `pip install -r requirements.txt`
2. 清理缓存: `pyinstaller --clean`
3. 检查Python版本: 建议使用3.11

### Q: electron-builder构建失败？

**A**: 
1. 确保npm依赖已安装: `npm install`
2. 清理node_modules: `rm -rf node_modules && npm install`
3. 检查electron-builder配置: `frontend/electron-builder.yml`

### Q: Windows安装包无法运行？

**A**:
1. 检查是否安装了Visual C++ Redistributable
2. 以管理员身份运行
3. 关闭杀毒软件（可能误报）

### Q: macOS提示"应用已损坏"？

**A**:
```bash
# 移除扩展属性
xattr -cr "/Applications/KOOK消息转发系统.app"

# 或者使用代码签名
```

### Q: 安装包太大？

**A**: 优化方法：
1. 排除不必要的依赖
2. 使用UPX压缩可执行文件
3. 不打包Chromium（首次启动时下载）

---

## 📊 安装包大小参考

| 平台 | 包含Chromium | 不包含Chromium |
|------|-------------|---------------|
| Windows | ~180MB | ~80MB |
| macOS | ~200MB | ~90MB |
| Linux | ~170MB | ~75MB |

**建议**: 不包含Chromium，首次启动时自动下载（带进度条）

---

## 🔒 代码签名

### Windows代码签名

```bash
# 使用signtool
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/KOOK-Forwarder-Setup.exe
```

### macOS代码签名和公证

```bash
# 签名
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" "KOOK消息转发系统.app"

# 公证（需要Apple Developer账号）
xcrun notarytool submit KOOK-Forwarder.dmg --keychain-profile "AC_PASSWORD"
```

### Linux（不需要签名）

Linux AppImage不需要代码签名。

---

## 📝 发布检查清单

构建完成后，发布前请检查：

- [ ] 安装包可以正常安装
- [ ] 应用可以正常启动
- [ ] 3步配置向导可以正常使用
- [ ] Cookie导入功能正常
- [ ] 验证码处理正常
- [ ] Redis自动启动正常
- [ ] Chromium自动下载正常
- [ ] 所有依赖都已打包
- [ ] 生成了校验和文件
- [ ] 更新了版本号
- [ ] 更新了更新日志

---

## 🚀 持续集成

### GitHub Actions自动构建

创建 `.github/workflows/build-installer.yml`:

```yaml
name: Build Installers

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
          node-version: '18'
      - name: Build
        run: python build/build_installer_ultimate.py --clean
      - uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: dist/*.exe

  build-macos:
    runs-on: macos-latest
    # ... 类似配置

  build-linux:
    runs-on: ubuntu-latest
    # ... 类似配置
```

---

## 📖 参考文档

- [PyInstaller文档](https://pyinstaller.org/)
- [electron-builder文档](https://www.electron.build/)
- [NSIS文档](https://nsis.sourceforge.io/Docs/)

---

**构建脚本位置**: `/workspace/build/build_installer_ultimate.py`  
**快速构建**: `python build/build_installer_ultimate.py --clean`
