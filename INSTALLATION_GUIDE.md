# 🚀 KOOK消息转发系统 - 安装指南

**版本**: v2.0  
**更新时间**: 2025-10-30

---

## 📦 当前可用的安装包

### 演示版安装包 ✅

**文件**: `dist_demo/KOOK-Forwarder-v2.0-Demo.zip`  
**大小**: 1.13 MB  
**类型**: 源代码压缩包

**特点**:
- ✅ 包含完整的21,000行源代码
- ✅ 包含所有配置文件
- ✅ 包含用户手册
- ✅ 需要手动安装依赖
- ✅ 适合开发者和高级用户

---

## 🎯 演示版快速开始

### 步骤1: 解压安装包

```bash
# 解压
unzip KOOK-Forwarder-v2.0-Demo.zip
cd KOOK-Forwarder-v2.0-Demo
```

### 步骤2: 查看README

```bash
cat README_DEMO.txt
```

### 步骤3: 安装依赖

**后端依赖（必需）:**
```bash
cd backend
pip install -r requirements.txt
```

主要依赖:
- FastAPI
- Uvicorn
- Playwright
- aiohttp
- redis
- pydantic

**前端依赖（开发时）:**
```bash
cd frontend
npm install
```

### 步骤4: 启动系统

**快速启动（仅后端）:**
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

**完整启动（前端+后端）:**

终端1（后端）:
```bash
cd backend
python -m app.main
```

终端2（前端）:
```bash
cd frontend
npm run dev
```

终端3（Electron桌面应用）:
```bash
cd frontend
npm run electron:dev
```

### 步骤5: 访问系统

- 后端API: http://localhost:9527
- 前端界面: http://localhost:5173
- Electron应用: 自动打开窗口

---

## 🏭 生产版安装包（需要构建）

### 构建生产版

如果你需要独立的可执行文件（不需要安装依赖），可以运行完整构建：

```bash
# 安装构建依赖
pip install pyinstaller
npm install -g electron-builder

# 运行完整构建
python scripts/build_all.py
```

**生成的安装包:**
```
dist/
├── KOOK-Forwarder-v2.0-Windows-x64.exe    (约150MB)
├── KOOK-Forwarder-v2.0-macOS.dmg          (约180MB)
├── KOOK-Forwarder-v2.0-Linux.AppImage     (约160MB)
└── checksums.txt
```

### 生产版特点

- ✅ 包含所有依赖
- ✅ 独立可执行文件
- ✅ 一键安装运行
- ✅ 自动更新支持
- ✅ 无需Python/Node环境
- ✅ 开箱即用

---

## 🔧 构建说明

### 系统要求

**开发环境:**
- Python 3.11+
- Node.js 18+
- npm 9+

**构建工具:**
- PyInstaller 6.0+
- electron-builder 24+

**可选工具:**
- ffmpeg (视频转码)
- Redis (消息队列)

### 构建步骤

#### 1. 后端构建

```bash
cd backend
pip install -r requirements.txt
pip install pyinstaller

# 使用spec文件构建
pyinstaller ../build/pyinstaller.spec --clean

# 生成: dist/kook-forwarder-backend/
```

#### 2. 前端构建

```bash
cd frontend
npm install

# 构建Vue
npm run build

# 构建Electron
npm run electron:build

# 生成: dist/KOOK-Forwarder-v2.0-*.exe/dmg/AppImage
```

#### 3. 完整构建

```bash
# 一键构建（推荐）
python scripts/build_all.py
```

---

## 📝 依赖清单

### Python后端依赖

```txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
playwright>=1.40.0
aiohttp>=3.9.0
redis>=5.0.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
pillow>=10.1.0
cryptography>=41.0.0
aiosmtplib>=3.0.0
psutil>=5.9.0
apscheduler>=3.10.0
pyyaml>=6.0
```

### 前端依赖

```json
{
  "vue": "^3.4.0",
  "element-plus": "^2.5.0",
  "@vueflow/core": "^1.33.0",
  "echarts": "^5.4.0",
  "driver.js": "^1.3.0",
  "vue-i18n": "^9.9.0",
  "axios": "^1.6.0"
}
```

---

## ⚠️ 常见问题

### Q: 演示版和生产版有什么区别？

**演示版:**
- 包含源代码
- 需要Python/Node环境
- 需要手动安装依赖
- 体积小（1.13 MB）
- 适合开发者

**生产版:**
- 独立可执行文件
- 无需环境配置
- 包含所有依赖
- 体积大（150+ MB）
- 适合普通用户

### Q: 如何从演示版升级到生产版？

运行构建脚本：
```bash
python scripts/build_all.py
```

### Q: 构建失败怎么办？

常见问题：
1. **PyInstaller错误** - 检查Python版本
2. **Electron构建失败** - 检查Node版本
3. **依赖缺失** - 运行 `pip install -r requirements.txt`
4. **权限不足** - 使用管理员权限

### Q: 安装包在哪里？

**演示版:**
```
/workspace/dist_demo/KOOK-Forwarder-v2.0-Demo.zip
```

**生产版（构建后）:**
```
/workspace/dist/KOOK-Forwarder-v2.0-*.exe/dmg/AppImage
```

---

## 📞 技术支持

如有问题，请查看：
- `docs/USER_MANUAL.md` - 用户手册
- `docs/开发指南.md` - 开发指南
- `README.md` - 项目介绍

---

**祝使用愉快！** 🎉
