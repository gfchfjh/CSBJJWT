# Electron 一键安装包构建指南

> 生成真正的桌面应用安装包（.exe / .dmg / .AppImage）

---

## 📋 当前状态

### ✅ 已有版本
- **Production Edition (Web版)**: `dist_production/KOOK-Forwarder-v2.0-Production.zip` (27MB)
  - 类型：Web应用（后端可执行文件 + 静态HTML）
  - 使用：需要启动脚本 + 浏览器访问
  - 优点：已打包，立即可用
  - 缺点：不是真正的桌面应用

### ❌ 待构建版本
- **Electron Windows**: `.exe` 安装程序（约150MB）
- **Electron macOS**: `.dmg` 安装程序（约150MB）
- **Electron Linux**: `.AppImage` 可执行文件（约150MB）

---

## 🚀 快速构建（推荐）

### 方案1：自动化构建脚本

```bash
# 1. 确保在项目根目录
cd /workspace

# 2. 安装Python构建依赖
pip3 install pyinstaller

# 3. 安装前端依赖（第一次需要5-10分钟）
cd frontend
npm install

# 4. 运行自动化构建脚本
cd ..
python3 scripts/build_electron_app.py

# 构建完成后，安装包位于：
# frontend/dist-electron/KOOK消息转发系统_v15.0.0_<平台>.exe|dmg|AppImage
```

**预计时间**：
- 首次构建：15-20分钟
- 后续构建：5-10分钟

### 方案2：指定平台构建

```bash
# 仅构建Windows版本
cd /workspace/frontend
npm install
npm run electron:build:win

# 仅构建macOS版本
npm run electron:build:mac

# 仅构建Linux版本
npm run electron:build:linux
```

---

## 📦 详细构建步骤

### 步骤1：准备环境

```bash
# 检查环境
python3 --version  # 需要 3.8+
node --version     # 需要 18+
npm --version      # 需要 9+

# 安装PyInstaller
pip3 install pyinstaller

# 安装前端依赖（时间较长）
cd /workspace/frontend
npm install
```

### 步骤2：构建后端（可选）

如果需要更新后端：

```bash
cd /workspace/backend
pyinstaller ../build/pyinstaller.spec --clean --noconfirm

# 构建产物：backend/dist/kook-forwarder-backend/
```

### 步骤3：构建前端

```bash
cd /workspace/frontend
npm run build

# 构建产物：frontend/dist/
```

### 步骤4：打包Electron应用

```bash
cd /workspace/frontend

# 选择一个命令运行：

# 打包当前平台
npm run electron:build

# 或指定平台
npm run electron:build:win    # Windows
npm run electron:build:mac    # macOS
npm run electron:build:linux  # Linux

# 构建产物：frontend/dist-electron/
```

---

## 📁 构建产物说明

### Windows (.exe)

```
frontend/dist-electron/
  └── KOOK消息转发系统 Setup 15.0.0.exe  (~150MB)
```

**特性**：
- ✅ NSIS安装程序
- ✅ 自定义安装路径
- ✅ 桌面快捷方式
- ✅ 开始菜单快捷方式
- ✅ 卸载程序

**使用**：
1. 双击 `.exe` 文件
2. 按照安装向导操作
3. 安装完成后从桌面或开始菜单启动

### macOS (.dmg)

```
frontend/dist-electron/
  └── KOOK消息转发系统-15.0.0.dmg  (~150MB)
```

**特性**：
- ✅ DMG镜像文件
- ✅ 拖拽安装界面
- ✅ 应用程序签名（需证书）
- ✅ 深色模式支持

**使用**：
1. 打开 `.dmg` 文件
2. 拖动应用到 "应用程序" 文件夹
3. 从启动台启动应用

### Linux (.AppImage)

```
frontend/dist-electron/
  └── KOOK消息转发系统-15.0.0.AppImage  (~150MB)
```

**特性**：
- ✅ 单文件可执行
- ✅ 无需安装
- ✅ 便携式运行

**使用**：
```bash
# 赋予执行权限
chmod +x KOOK消息转发系统-15.0.0.AppImage

# 直接运行
./KOOK消息转发系统-15.0.0.AppImage
```

---

## 🔧 常见问题

### Q1: npm install 失败

```bash
# 清理缓存重试
cd /workspace/frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Q2: electron-builder 构建失败

```bash
# 检查磁盘空间（需要至少5GB）
df -h

# 清理旧构建
rm -rf frontend/dist frontend/dist-electron

# 重新构建
npm run build
npm run electron:build
```

### Q3: 缺少图标文件

确保以下图标文件存在：
- `build/icon.ico` (Windows)
- `build/icon.icns` (macOS)
- `build/icon.png` (Linux)

### Q4: Windows上构建macOS版本

需要在macOS系统上构建，或使用云构建服务。

---

## 🎯 临时解决方案：使用现有Web版

如果构建时间过长，可以先使用已打包的Web版：

```bash
# 解压Production版本
cd /workspace/dist_production
unzip KOOK-Forwarder-v2.0-Production.zip
cd KOOK-Forwarder-v2.0-Production

# Windows启动
start.bat

# Linux/Mac启动
chmod +x start.sh
./start.sh
# 然后手动打开浏览器访问 web/index.html
```

**优点**：
- ✅ 立即可用，无需等待
- ✅ 功能完整
- ✅ 体积小巧（27MB）

**缺点**：
- ❌ 需要手动启动脚本
- ❌ 需要浏览器访问
- ❌ 无系统托盘
- ❌ 无开机自启

---

## 📊 版本对比

| 特性 | Web版 (当前) | Electron版 (待构建) |
|------|-------------|-------------------|
| 安装方式 | 解压即用 | 双击安装 |
| 启动方式 | 启动脚本 + 浏览器 | 桌面图标 |
| 系统托盘 | ❌ | ✅ |
| 开机自启 | ❌ | ✅ |
| 原生体验 | ⚠️ (浏览器) | ✅ (桌面应用) |
| 包大小 | 27 MB | ~150 MB |
| 构建时间 | 已完成 | 15-20分钟 |
| 依赖环境 | 无 | 无 |
| 功能完整性 | 100% | 100% |

---

## 💡 建议

### 如果需要立即使用：
使用 **Production Edition (Web版)**，功能完整，立即可用。

### 如果需要最佳体验：
花15-20分钟构建 **Electron桌面版**，获得：
- ✅ 真正的桌面应用
- ✅ 系统托盘集成
- ✅ 开机自启动
- ✅ 更好的用户体验

---

## 🚀 一键构建命令（推荐）

```bash
# 复制这些命令，一次性执行：

cd /workspace
pip3 install pyinstaller
cd frontend
npm install
npm run build
npm run electron:build:linux  # 或 :win / :mac

echo "✅ 构建完成！安装包位于 frontend/dist-electron/"
```

**注意**：
- 首次运行 `npm install` 需要 5-10 分钟
- `electron:build` 需要 3-5 分钟
- 总计约 10-15 分钟

---

## 📞 技术支持

- **构建问题**：检查 `frontend/dist-electron/` 目录是否有错误日志
- **运行问题**：查看应用日志（通常在 `~/.kook-forwarder/logs/`）
- **其他问题**：参考 `docs/` 目录中的文档

---

*文档生成时间: 2025-10-30*
*当前版本: v15.0.0*
