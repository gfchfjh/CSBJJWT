# 构建和打包指南

> ✅ P0-1深度优化：一键打包所有平台

## 📦 快速开始

### 一键打包（推荐）

```bash
# 安装构建依赖
pip install -r ../backend/requirements.txt
pip install pyinstaller playwright
playwright install chromium --with-deps

cd ../frontend
npm install

# 返回构建目录
cd ../build

# 🚀 一键打包所有平台
python package_ultimate.py --platform all

# 或打包特定平台
python package_ultimate.py --platform windows
python package_ultimate.py --platform macos
python package_ultimate.py --platform linux
```

### 输出文件

打包完成后，安装包位于：

```
frontend/dist-electron/
├── KOOK-Forwarder-9.0.0-Setup.exe        # Windows安装包
├── KOOK-Forwarder-9.0.0-macOS-x64.dmg    # macOS Intel安装包
├── KOOK-Forwarder-9.0.0-macOS-arm64.dmg  # macOS Apple Silicon安装包
└── KOOK-Forwarder-9.0.0-x64.AppImage     # Linux安装包
```

## 🛠️ 详细步骤

### 1. 准备环境

**必需工具**：
- Python 3.11+
- Node.js 18+
- npm 9+
- PyInstaller 6.0+
- Playwright 1.40+

**检查环境**：
```bash
python --version   # 应显示 3.11+
node --version     # 应显示 v18+
npm --version      # 应显示 9+
```

### 2. 安装依赖

```bash
# Python依赖
cd backend
pip install -r requirements.txt
pip install pyinstaller

# Playwright浏览器
playwright install chromium --with-deps

# 前端依赖
cd ../frontend
npm install
```

### 3. 打包后端

```bash
cd ../build

# 使用PyInstaller规范文件
pyinstaller pyinstaller.spec

# 或使用自动化脚本（推荐）
python package_ultimate.py --platform windows
```

**输出**：
- `dist/kook-forwarder-backend(.exe)` - 后端可执行文件

### 4. 构建前端

```bash
cd ../frontend

# 构建Vue应用
npm run build

# 输出到 dist/ 目录
```

### 5. 打包Electron应用

```bash
# Windows
npm run electron:build:win

# macOS
npm run electron:build:mac

# Linux
npm run electron:build:linux

# 全平台（仅限macOS或Linux环境）
npm run electron:build
```

## 📋 配置文件说明

### pyinstaller.spec

PyInstaller配置文件，控制Python后端打包：

- **hiddenimports**: 隐藏导入的模块
- **datas**: 需要包含的数据文件
- **binaries**: 需要包含的二进制文件
- **excludes**: 排除的模块（减小体积）

### electron-builder.yml

Electron Builder配置文件，控制桌面应用打包：

- **files**: 包含的文件
- **extraResources**: 额外资源（后端、Redis等）
- **win/mac/linux**: 各平台特定配置
- **nsis**: Windows安装程序配置

### installer.nsh

NSIS自定义安装脚本（Windows）：

- 安装前检查旧版本
- 创建桌面快捷方式
- 写入注册表
- 卸载时询问是否删除数据

## 🎯 平台特定说明

### Windows

**目标**：`.exe` NSIS安装程序

**特点**：
- 支持选择安装路径
- 创建桌面快捷方式
- 添加到开始菜单
- 注册表集成
- 卸载程序

**依赖**：
- NSIS（electron-builder自动处理）
- Windows SDK

### macOS

**目标**：`.dmg` 磁盘镜像

**特点**：
- 拖拽安装
- 支持Intel和Apple Silicon
- 代码签名（需要Apple Developer账号）
- 公证（需要Apple ID）

**代码签名**：
```bash
# 需要在electron-builder.yml中配置
mac:
  identity: "Developer ID Application: Your Name (TEAM_ID)"
  
# 需要环境变量
export CSC_LINK=/path/to/certificate.p12
export CSC_KEY_PASSWORD=your_password
```

### Linux

**目标**：`.AppImage` / `.deb` / `.rpm`

**特点**：
- AppImage无需安装
- deb适用于Debian/Ubuntu
- rpm适用于Fedora/RHEL

**系统依赖**：
```bash
# Ubuntu/Debian
sudo apt-get install libappindicator1 libnotify-bin

# Fedora/RHEL
sudo yum install libappindicator libnotify
```

## 🔧 高级配置

### 减小安装包体积

1. **排除不必要的模块**：
   ```python
   # pyinstaller.spec
   excludes=[
       'matplotlib',  # 如果不需要图表
       'numpy',       # 如果不需要数值计算
       'pandas',      # 如果不需要数据分析
   ]
   ```

2. **使用UPX压缩**：
   ```python
   # pyinstaller.spec
   upx=True,
   upx_exclude=[],
   ```

3. **优化Chromium**：
   ```bash
   # 仅安装必需的浏览器
   playwright install chromium
   # 不要安装 firefox 和 webkit
   ```

### 自动更新

electron-builder.yml中已配置GitHub自动更新：

```yaml
publish:
  provider: github
  owner: gfchfjh
  repo: CSBJJWT
```

需要在代码中添加：

```javascript
// frontend/electron/main.js
const { autoUpdater } = require('electron-updater')

autoUpdater.checkForUpdatesAndNotify()
```

## 🐛 故障排查

### Python打包失败

**问题**: `ModuleNotFoundError`

**解决**:
```bash
# 确保所有依赖都已安装
pip install -r requirements.txt

# 添加到 hiddenimports
--hidden-import=missing_module
```

### Electron打包失败

**问题**: `Cannot find module 'xxx'`

**解决**:
```bash
# 清理缓存
rm -rf node_modules
rm package-lock.json
npm install

# 重新构建
npm run build
npm run electron:build
```

### macOS签名失败

**问题**: `Code signing failed`

**解决**:
```bash
# 暂时禁用签名（仅用于测试）
# electron-builder.yml
mac:
  identity: null

# 或配置正确的证书
export CSC_LINK=/path/to/certificate.p12
export CSC_KEY_PASSWORD=your_password
```

## 📝 版本发布检查清单

- [ ] 更新 `VERSION` 文件
- [ ] 更新 `frontend/package.json` 版本号
- [ ] 更新 `README.md` 版本说明
- [ ] 运行完整测试套件
- [ ] 执行打包脚本
- [ ] 测试各平台安装包
- [ ] 创建GitHub Release
- [ ] 上传安装包到Release
- [ ] 更新下载链接

## 📚 相关文档

- [PyInstaller文档](https://pyinstaller.org/)
- [electron-builder文档](https://www.electron.build/)
- [Playwright文档](https://playwright.dev/)
- [NSIS文档](https://nsis.sourceforge.io/)

---

**维护团队**: KOOK Forwarder Team  
**最后更新**: 2025-10-28
