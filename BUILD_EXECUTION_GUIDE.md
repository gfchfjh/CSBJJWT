# 🏗️ 预编译安装包构建执行指南

> **完整的构建流程和步骤说明** - 从准备到发布的完整指南

---

## 📑 目录

1. [快速开始](#快速开始)
2. [环境准备](#环境准备)
3. [构建方式](#构建方式)
4. [详细步骤](#详细步骤)
5. [故障排查](#故障排查)
6. [验证测试](#验证测试)

---

## 🚀 快速开始

### 最简单的方式：GitHub Actions自动构建 ⭐

```bash
# 1. 确保所有更改已提交
git add .
git commit -m "准备构建 v1.13.2"
git push

# 2. 运行发布脚本
./release_package.sh

# 3. 等待15-20分钟，GitHub Actions会自动：
#    ✅ 在Windows/macOS/Linux上构建
#    ✅ 运行测试
#    ✅ 创建GitHub Release
#    ✅ 上传所有平台的安装包

# 4. 访问 GitHub Releases 页面下载
#    https://github.com/gfchfjh/CSBJJWT/releases
```

---

## 🔧 环境准备

### Step 1: 安装构建前准备检查

```bash
# 运行检查清单
cat PRE_BUILD_CHECKLIST.md

# 快速检查脚本
bash -c '
echo "=== 环境检查 ==="
python3 --version && echo "✅ Python" || echo "❌ Python未安装"
node --version && echo "✅ Node.js" || echo "❌ Node.js未安装"
git --version && echo "✅ Git" || echo "❌ Git未安装"
'
```

### Step 2: 安装必要的依赖

```bash
# Python依赖
pip3 install --upgrade pip
pip3 install pyinstaller Pillow
pip3 install -r backend/requirements.txt
playwright install chromium

# 前端依赖
cd frontend
npm install
cd ..
```

### Step 3: 生成图标文件

```bash
# 生成PNG图标
python3 build/generate_simple_icon.py

# 生成平台特定图标（.ico, .icns, .png）
python3 build/create_platform_icons.py

# 验证图标
ls -lh build/icon.*
```

### Step 4: 准备Redis（可选）

```bash
# 如果要打包Redis到安装包中
python3 build/prepare_redis.py

# 或使用系统Redis（推荐）
# 安装包会在运行时使用系统的Redis
```

---

## 🏗️ 构建方式

### 方式1: GitHub Actions自动构建 ⭐ **强烈推荐**

**优点：**
- ✅ 3个平台同时构建（Windows/macOS/Linux）
- ✅ 自动运行测试
- ✅ 自动创建Release
- ✅ 自动上传安装包
- ✅ 无需本地环境配置

**步骤：**

```bash
# 1. 准备代码
git add .
git commit -m "准备发布 v1.13.2"
git push origin main

# 2. 运行发布脚本（推荐）
./release_package.sh
# 脚本会：
#   - 检查Git状态
#   - 更新版本号
#   - 创建Git Tag
#   - 推送到GitHub
#   - 自动触发GitHub Actions

# 或手动创建Tag
git tag v1.13.2
git push origin v1.13.2

# 3. 监控构建进度
# 访问: https://github.com/gfchfjh/CSBJJWT/actions
# 查看 "Build and Release" workflow

# 4. 下载安装包（15-20分钟后）
# 访问: https://github.com/gfchfjh/CSBJJWT/releases/tag/v1.13.2
```

**构建输出：**
- `KookForwarder_v1.13.2_Windows_x64.exe` (~450MB)
- `KookForwarder_v1.13.2_macOS.dmg` (~480MB)
- `KookForwarder_v1.13.2_Linux_x64.AppImage` (~420MB)

---

### 方式2: 本地构建（单平台）

#### 2.1 Linux构建

```bash
# 完整构建脚本
./build_installer.sh

# 或分步执行：

# 1. 安装依赖
pip3 install -r backend/requirements.txt
pip3 install pyinstaller
cd frontend && npm install && cd ..

# 2. 构建后端
cd backend
pyinstaller --clean --noconfirm ../build/build_backend.spec
cd ..

# 3. 构建前端
cd frontend
npm run build
npm run electron:build:linux
cd ..

# 4. 查看输出
ls -lh frontend/dist-electron/*.AppImage
```

**输出：** `frontend/dist-electron/KookForwarder-1.13.2.AppImage`

#### 2.2 macOS构建

```bash
# 完整构建脚本
./build_installer.sh

# 或分步执行：

# 1. 安装依赖（同Linux）
pip3 install -r backend/requirements.txt
pip3 install pyinstaller
cd frontend && npm install && cd ..

# 2. 生成.icns图标
mkdir -p icon.iconset
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

# 3. 构建后端
cd backend
pyinstaller --clean --noconfirm ../build/build_backend.spec
cd ..

# 4. 构建前端
cd frontend
npm run build
npm run electron:build:mac
cd ..

# 5. 查看输出
ls -lh frontend/dist-electron/*.dmg
```

**输出：** `frontend/dist-electron/KookForwarder-1.13.2.dmg`

#### 2.3 Windows构建

```batch
REM 完整构建脚本
build_installer.bat

REM 或分步执行：

REM 1. 安装依赖
pip install -r backend\requirements.txt
pip install pyinstaller
cd frontend
npm install
cd ..

REM 2. 构建后端
cd backend
pyinstaller --clean --noconfirm ..\build\build_backend.spec
cd ..

REM 3. 构建前端
cd frontend
npm run build
npm run electron:build:win
cd ..

REM 4. 查看输出
dir frontend\dist-electron\*.exe
```

**输出：** `frontend\dist-electron\KookForwarder Setup 1.13.2.exe`

---

## 📝 详细步骤

### 阶段1: 准备工作 (5分钟)

#### 1.1 检查环境
```bash
# 运行检查脚本
bash PRE_BUILD_CHECKLIST.md

# 或手动检查
python3 --version  # >= 3.11
node --version     # >= 18
git --version
```

#### 1.2 更新版本号
```bash
# 编辑 frontend/package.json
nano frontend/package.json
# 修改 "version": "1.13.2"

# 编辑 README.md (更新版本号)
nano README.md
```

#### 1.3 生成图标
```bash
python3 build/generate_simple_icon.py
python3 build/create_platform_icons.py

# 验证
ls build/icon.{ico,png}
```

---

### 阶段2: 后端构建 (5-10分钟)

#### 2.1 安装Python依赖
```bash
cd backend
pip3 install -r requirements.txt
pip3 install pyinstaller
```

#### 2.2 安装Playwright浏览器
```bash
playwright install chromium
# Linux额外需要
playwright install-deps chromium
```

#### 2.3 运行PyInstaller打包
```bash
# 清理旧文件
rm -rf build dist *.spec.bak

# 打包
pyinstaller --clean --noconfirm ../build/build_backend.spec

# 验证输出
ls -lh dist/KookForwarder-Backend/
```

**预期输出：**
- Linux/macOS: `dist/KookForwarder-Backend/KookForwarder-Backend`
- Windows: `dist/KookForwarder-Backend/KookForwarder-Backend.exe`

**大小估算：**
- 可执行文件: ~80-120MB
- 包含依赖: ~150-200MB

---

### 阶段3: 前端构建 (3-5分钟)

#### 3.1 安装前端依赖
```bash
cd ../frontend
npm install
```

#### 3.2 构建Vue应用
```bash
npm run build

# 验证输出
ls -la dist/
```

#### 3.3 打包Electron应用
```bash
# Linux
npm run electron:build:linux

# macOS
npm run electron:build:mac

# Windows
npm run electron:build:win

# 验证输出
ls -lh dist-electron/
```

**预期输出：**
- Linux: `*.AppImage` (~420MB)
- macOS: `*.dmg` (~480MB)
- Windows: `*.exe` (~450MB)

---

### 阶段4: 测试安装包 (10-15分钟)

#### 4.1 安装测试
```bash
# Linux
chmod +x frontend/dist-electron/*.AppImage
./frontend/dist-electron/*.AppImage

# macOS
open frontend/dist-electron/*.dmg

# Windows
# 双击.exe文件安装
```

#### 4.2 功能测试
```bash
# 运行验证脚本
python3 build/verify_build.py
```

**测试项目：**
1. ✅ 应用启动成功
2. ✅ 配置向导显示
3. ✅ 添加KOOK账号
4. ✅ 配置Bot
5. ✅ 创建频道映射
6. ✅ 发送测试消息

---

### 阶段5: 发布 (5分钟)

#### 5.1 创建GitHub Release（自动）
```bash
# GitHub Actions会自动创建
# 或手动创建：
gh release create v1.13.2 \
  frontend/dist-electron/*.AppImage \
  --title "v1.13.2 Release" \
  --notes "完整的一键安装包，支持Windows/macOS/Linux"
```

#### 5.2 更新文档
```bash
# 更新README.md中的下载链接
nano README.md

# 提交更改
git add README.md
git commit -m "docs: update download links for v1.13.2"
git push
```

---

## 🔧 故障排查

### 问题1: PyInstaller打包失败

**症状：** `ERROR: ModuleNotFoundError: No module named 'xxx'`

**解决方案：**
```bash
# 方案1: 添加到hiddenimports
nano build/build_backend.spec
# 在hiddenimports列表中添加缺失的模块

# 方案2: 重新安装依赖
pip3 install --force-reinstall -r backend/requirements.txt

# 方案3: 清理缓存重试
rm -rf backend/build backend/dist
pyinstaller --clean --noconfirm build/build_backend.spec
```

---

### 问题2: Electron打包失败

**症状：** `ENOENT: no such file or directory`

**解决方案：**
```bash
# 方案1: 清理缓存
cd frontend
rm -rf node_modules dist dist-electron
npm install
npm run build

# 方案2: 检查图标文件
ls build/icon.{ico,icns,png}
python3 build/create_platform_icons.py

# 方案3: 检查package.json配置
nano frontend/package.json
# 验证build节点配置正确
```

---

### 问题3: 图标显示异常

**症状：** 安装包没有图标或图标显示错误

**解决方案：**
```bash
# 重新生成图标
python3 build/generate_simple_icon.py
python3 build/create_platform_icons.py

# 验证图标文件
file build/icon.ico  # Windows
file build/icon.png  # Linux
file build/icon.icns # macOS（需要在macOS上）

# 检查文件大小（太小可能损坏）
ls -lh build/icon.*
```

---

### 问题4: GitHub Actions失败

**常见错误及解决：**

1. **权限错误**
   ```yaml
   # 检查.github/workflows/build-and-release.yml
   # 确保有正确的permissions配置
   permissions:
     contents: write
   ```

2. **依赖安装失败**
   ```bash
   # 检查requirements.txt和package.json
   # 确保所有依赖版本可用
   ```

3. **构建超时**
   ```yaml
   # 增加超时时间
   timeout-minutes: 60
   ```

---

## ✅ 验证测试

### 自动化验证脚本

创建并运行验证脚本：

```bash
# 运行验证
python3 build/verify_build.py

# 或手动验证
bash -c '
echo "=== 安装包验证 ==="
echo ""

# 检查文件存在
if [ -f frontend/dist-electron/*.AppImage ]; then
    echo "✅ Linux安装包"
    ls -lh frontend/dist-electron/*.AppImage
else
    echo "❌ Linux安装包不存在"
fi

# 检查文件大小
SIZE=$(du -sm frontend/dist-electron/*.AppImage 2>/dev/null | cut -f1)
if [ "$SIZE" -gt 100 ]; then
    echo "✅ 安装包大小正常: ${SIZE}MB"
else
    echo "⚠️  安装包大小异常: ${SIZE}MB"
fi

# 检查可执行权限
if [ -x frontend/dist-electron/*.AppImage ]; then
    echo "✅ 可执行权限正常"
else
    echo "❌ 缺少可执行权限"
fi
'
```

### 手动验证清单

- [ ] 安装包文件存在
- [ ] 文件大小正常（>100MB）
- [ ] 文件可执行
- [ ] 双击可以启动
- [ ] 配置向导显示
- [ ] 可以添加账号
- [ ] 可以配置Bot
- [ ] 可以创建映射
- [ ] 可以转发消息

---

## 📊 构建性能参考

### 时间估算

| 阶段 | 本地构建 | GitHub Actions |
|------|---------|---------------|
| 准备 | 5分钟 | 2分钟 |
| 后端 | 5-10分钟 | 3-5分钟 |
| 前端 | 3-5分钟 | 2-4分钟 |
| 打包 | 2-3分钟 | 2-3分钟 |
| **总计** | **15-23分钟** | **9-14分钟/平台** |

**GitHub Actions总时间：** 15-20分钟（3个平台并行）

### 资源使用

| 资源 | 使用量 |
|------|--------|
| CPU | 高（构建时100%） |
| 内存 | 4-8GB |
| 磁盘 | 10GB（临时+输出） |
| 网络 | 1-2GB（下载依赖） |

---

## 🎯 最佳实践

### 1. 使用GitHub Actions ⭐

**原因：**
- 环境一致性
- 多平台同时构建
- 自动化测试
- 自动发布

### 2. 定期清理

```bash
# 清理构建缓存
rm -rf backend/build backend/dist
rm -rf frontend/node_modules frontend/dist frontend/dist-electron
rm -rf build/download

# 清理Git未跟踪文件
git clean -fdx -e node_modules
```

### 3. 版本管理

```bash
# 每次构建前更新版本号
nano frontend/package.json

# 创建Git Tag
git tag v1.13.2
git push origin v1.13.2

# 遵循语义化版本号
# MAJOR.MINOR.PATCH
# 1.13.2 -> 1.13.3 (补丁)
# 1.13.2 -> 1.14.0 (次版本)
# 1.13.2 -> 2.0.0 (主版本)
```

### 4. 测试先行

```bash
# 构建前运行测试
cd backend && pytest tests/ -v
cd frontend && npm run test

# 构建后验证安装包
python3 build/verify_build.py
```

---

## 📞 获取帮助

**遇到问题？**

1. 查看[PRE_BUILD_CHECKLIST.md](PRE_BUILD_CHECKLIST.md)
2. 查看[故障排查](#故障排查)章节
3. 查看GitHub Actions日志
4. 查看项目Issues: https://github.com/gfchfjh/CSBJJWT/issues

**成功构建！** 🎉
