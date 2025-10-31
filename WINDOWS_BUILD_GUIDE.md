# Windows构建指南 - KOOK消息转发系统 v18.0.0

**两种构建方式**: GitHub Actions自动构建 (推荐) | 本地手动构建

---

## 🚀 方式1: GitHub Actions自动构建 (推荐)

### 优点
- ✅ 全自动，无需Windows环境
- ✅ 构建环境标准化
- ✅ 自动发布到GitHub Release
- ✅ 包含完整的校验和

### 使用步骤

#### 选项A: 通过标签触发（推荐）
```bash
# 1. 已经创建了v18.0.0标签
# GitHub Actions会自动检测并构建

# 2. 查看构建进度
# 访问: https://github.com/gfchfjh/CSBJJWT/actions
```

#### 选项B: 手动触发
```bash
# 1. 访问 GitHub Actions 页面
https://github.com/gfchfjh/CSBJJWT/actions/workflows/build-windows.yml

# 2. 点击 "Run workflow" 按钮
# 3. 输入版本号: v18.0.0
# 4. 点击 "Run workflow"
```

### 查看构建结果

```bash
# 方式1: 通过GitHub CLI
gh run list --workflow=build-windows.yml --limit 5

# 方式2: 访问网页
https://github.com/gfchfjh/CSBJJWT/actions

# 方式3: 查看Release
https://github.com/gfchfjh/CSBJJWT/releases/tag/v18.0.0
```

### 构建产物

自动构建完成后，将生成以下文件并上传到Release:

```
KOOK-Forwarder-v18.0.0-Windows.zip  [约200 MB]
├── frontend/
│   ├── KOOK消息转发系统 Setup.exe  [NSIS安装包]
│   └── win-unpacked/  [便携版]
├── backend/
│   └── kook-forwarder-backend/  [Python后端]
├── docs/
├── README.md
└── 安装说明.txt

KOOK-Forwarder-v18.0.0-Windows.zip.md5  [MD5校验]
KOOK-Forwarder-v18.0.0-Windows.zip.sha256  [SHA256校验]
```

---

## 🖥️ 方式2: 本地手动构建

### 前提条件

#### 必需软件
1. **Windows 10/11** (64位)
2. **Python 3.11+**
   - 下载: https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"
3. **Node.js 20+**
   - 下载: https://nodejs.org/
   - 包含npm
4. **Git**
   - 下载: https://git-scm.com/download/win

#### 可选软件
- Visual Studio Build Tools (用于编译原生模块)
- Windows SDK

### 构建步骤

#### 步骤1: 克隆仓库
```bash
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT
git checkout v18.0.0
```

#### 步骤2: 运行构建脚本

**方式A: 使用批处理脚本 (推荐)**
```cmd
# 双击运行或在命令提示符中执行
build-windows.bat
```

**方式B: 使用Python脚本**
```bash
python build_all_platforms.py --platform windows
```

**方式C: 手动构建**
```bash
# 1. 安装前端依赖
cd frontend
npm install --legacy-peer-deps

# 2. 构建前端
npm run build

# 3. 打包Electron
npm run electron:build:win

# 4. 安装后端依赖
cd ../backend
pip install -r requirements.txt
pip install pyinstaller

# 5. 打包后端
pyinstaller ../build/pyinstaller.spec

# 6. 完成！
cd ..
```

### 构建产物位置

```
frontend/dist-electron/
├── KOOK消息转发系统 Setup v16.0.0.exe  [安装包, ~120 MB]
└── win-unpacked/  [便携版目录]
    └── KOOK消息转发系统.exe

backend/dist/
└── kook-forwarder-backend/  [后端服务, ~80 MB]
    └── kook-forwarder-backend.exe

dist/  [最终发布包]
└── KOOK-Forwarder-v18.0.0-Windows/
    └── [完整打包]
```

---

## 📦 安装包说明

### 1. NSIS安装包 (.exe)
```
文件: KOOK消息转发系统 Setup v16.0.0.exe
大小: ~120 MB
特点:
  - 完整的安装向导
  - 自动创建桌面快捷方式
  - 自动创建开始菜单项
  - 支持卸载
  - 推荐给普通用户
```

**使用方法**:
1. 双击运行安装包
2. 按照向导提示完成安装
3. 从桌面或开始菜单启动

### 2. 便携版 (win-unpacked)
```
目录: win-unpacked/
大小: ~120 MB (解压后)
特点:
  - 免安装
  - 可放在U盘
  - 可多实例运行
  - 推荐给高级用户
```

**使用方法**:
1. 解压 win-unpacked 目录
2. 直接运行 KOOK消息转发系统.exe
3. 无需安装

### 3. 完整发布包 (.zip)
```
文件: KOOK-Forwarder-v18.0.0-Windows.zip
大小: ~200 MB
包含:
  - Electron前端 (安装包 + 便携版)
  - Python后端
  - 完整文档
  - 安装说明
```

---

## 🔧 常见问题

### Q1: 构建失败 - Python未找到
**解决**:
```bash
# 确保Python在PATH中
python --version

# 如果失败，重新安装Python并勾选"Add to PATH"
```

### Q2: 构建失败 - Node.js未找到
**解决**:
```bash
# 确保Node.js在PATH中
node --version
npm --version

# 如果失败，重新安装Node.js
```

### Q3: npm install 失败
**解决**:
```bash
# 清理缓存
npm cache clean --force

# 删除node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install --legacy-peer-deps
```

### Q4: PyInstaller打包失败
**解决**:
```bash
# 确保安装了最新版PyInstaller
pip install --upgrade pyinstaller

# 如果还失败，安装pywin32
pip install pywin32
```

### Q5: electron-builder失败
**解决**:
```bash
# 安装Windows Build Tools
npm install --global windows-build-tools

# 或安装Visual Studio Build Tools
# 下载: https://visualstudio.microsoft.com/downloads/
```

### Q6: 缺少DLL文件
**解决**:
```bash
# 安装Visual C++ Redistributable
# 下载: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

---

## ✅ 验证构建

### 检查安装包
```bash
# 1. 验证文件存在
dir frontend\dist-electron\*.exe
dir backend\dist\kook-forwarder-backend\*.exe

# 2. 验证文件大小
# 前端安装包: ~120 MB
# 后端可执行文件: ~80 MB

# 3. 测试运行
cd frontend\dist-electron\win-unpacked
"KOOK消息转发系统.exe"
```

### 检查后端
```bash
# 测试后端
cd backend\dist\kook-forwarder-backend
kook-forwarder-backend.exe

# 应该看到FastAPI启动信息
```

---

## 📊 构建时间估算

| 步骤 | 时间 |
|------|------|
| 安装前端依赖 | ~2分钟 |
| 安装后端依赖 | ~1分钟 |
| 构建前端 | ~10秒 |
| 打包Electron | ~2分钟 |
| 打包后端 | ~20秒 |
| 创建ZIP | ~30秒 |
| **总计** | **~6分钟** |

---

## 🚀 GitHub Actions构建监控

### 实时查看构建日志
```bash
# 使用GitHub CLI
gh run watch

# 或访问网页
https://github.com/gfchfjh/CSBJJWT/actions
```

### 构建状态
```bash
# 查看最新构建
gh run list --workflow=build-windows.yml --limit 1

# 查看构建详情
gh run view [RUN_ID]

# 下载构建产物
gh run download [RUN_ID]
```

---

## 📝 发布到GitHub Release

### 自动发布（GitHub Actions）
如果通过标签触发构建，会自动上传到对应的Release:
```
https://github.com/gfchfjh/CSBJJWT/releases/tag/v18.0.0
```

### 手动发布
```bash
# 使用GitHub CLI
gh release upload v18.0.0 \
  dist/KOOK-Forwarder-v18.0.0-Windows.zip \
  dist/KOOK-Forwarder-v18.0.0-Windows.zip.md5 \
  dist/KOOK-Forwarder-v18.0.0-Windows.zip.sha256

# 或通过网页上传
https://github.com/gfchfjh/CSBJJWT/releases/tag/v18.0.0
```

---

## 🎯 下一步

### 构建完成后
1. ✅ 测试安装包
2. ✅ 验证MD5/SHA256
3. ✅ 上传到GitHub Release
4. ✅ 更新README下载链接
5. ✅ 发布公告

### 用户下载
```
Windows完整版下载:
https://github.com/gfchfjh/CSBJJWT/releases/download/v18.0.0/KOOK-Forwarder-v18.0.0-Windows.zip

大小: ~200 MB
MD5校验: 见.md5文件
SHA256校验: 见.sha256文件
```

---

**© 2025 KOOK Forwarder Team**  
**版本**: v18.0.0  
**更新日期**: 2025-10-31
