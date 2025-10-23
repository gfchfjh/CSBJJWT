# KOOK消息转发系统 - 预编译安装包构建指南

**目标**: 生成 Windows/macOS/Linux 三平台预编译安装包

**构建方式**: GitHub Actions 自动化构建（推荐）

**预计时间**: 15-20 分钟

---

## 🚀 方式一：一键发布脚本

### 步骤1: 执行发布脚本

```bash
# Linux/macOS
./release_package.sh

# Windows (使用Git Bash)
bash release_package.sh
```

### 步骤2: 按提示操作

脚本会自动：
1. ✅ 检查Git仓库状态
2. ✅ 获取当前版本号
3. ✅ 提示输入新版本号（可选）
4. ✅ 创建Git Tag
5. ✅ 推送到GitHub
6. ✅ 触发GitHub Actions构建

### 步骤3: 监控构建进度

访问: https://github.com/gfchfjh/CSBJJWT/actions

等待约15-20分钟，直到所有构建任务完成。

### 步骤4: 下载安装包

访问: https://github.com/gfchfjh/CSBJJWT/releases

从最新的Release中下载安装包。

---

## 🔧 方式二：手动发布（标准流程）

### 前提条件

- ✅ 已完成所有代码提交
- ✅ 已测试所有功能正常
- ✅ 已更新文档和CHANGELOG

### 步骤1: 更新版本号

编辑 `frontend/package.json`:
```json
{
  "version": "1.14.0"
}
```

### 步骤2: 提交更改

```bash
git add frontend/package.json
git commit -m "chore: bump version to v1.14.0"
git push origin main
```

### 步骤3: 创建Git Tag

```bash
# 创建带注释的标签
git tag -a v1.14.0 -m "Release v1.14.0

🎉 KOOK消息转发系统 v1.14.0

## 📦 安装包
- Windows: KookForwarder-Setup-1.14.0.exe
- macOS: KookForwarder-1.14.0.dmg
- Linux: KookForwarder-1.14.0.AppImage

## 🐳 Docker镜像
\`\`\`bash
docker pull ghcr.io/gfchfjh/csbjjwt:1.14.0
\`\`\`

## 📚 文档
- 快速开始: https://github.com/gfchfjh/CSBJJWT/blob/main/QUICK_START.md
- 完整文档: https://github.com/gfchfjh/CSBJJWT/blob/main/README.md
"

# 推送标签到远程
git push origin v1.14.0
```

### 步骤4: GitHub Actions 自动构建

推送标签后，GitHub Actions 会自动触发构建流程：

**构建任务**:
1. **build-backend** (3个并行任务)
   - Ubuntu: 构建Linux后端
   - Windows: 构建Windows后端
   - macOS: 构建macOS后端
   - 耗时: 约5-8分钟

2. **build-electron-windows** (依赖后端构建完成)
   - 下载Windows后端
   - 安装前端依赖
   - 构建Windows安装包 (.exe)
   - 耗时: 约3-5分钟

3. **build-electron-macos** (依赖后端构建完成)
   - 下载macOS后端
   - 安装前端依赖
   - 构建macOS安装包 (.dmg)
   - 耗时: 约4-6分钟

4. **build-electron-linux** (依赖后端构建完成)
   - 下载Linux后端
   - 安装前端依赖
   - 构建Linux安装包 (.AppImage)
   - 耗时: 约3-5分钟

5. **build-docker** (独立并行)
   - 构建多架构Docker镜像
   - 推送到GitHub Container Registry
   - 耗时: 约5-8分钟

6. **create-release** (依赖所有构建完成)
   - 下载所有构建产物
   - 创建GitHub Release
   - 上传所有安装包
   - 耗时: 约1-2分钟

**总耗时**: 约15-20分钟

### 步骤5: 监控构建进度

访问GitHub Actions页面:
```
https://github.com/gfchfjh/CSBJJWT/actions
```

查看最新的 "Build and Release" 工作流运行状态。

**成功标志**:
- ✅ 所有6个任务显示绿色对勾
- ✅ GitHub Releases 页面出现新版本
- ✅ 所有3个安装包文件已上传

### 步骤6: 验证发布

访问Release页面:
```
https://github.com/gfchfjh/CSBJJWT/releases/tag/v1.14.0
```

**检查内容**:
- ✅ Windows安装包 (KookForwarder-Setup-1.14.0.exe, ~450MB)
- ✅ macOS安装包 (KookForwarder-1.14.0.dmg, ~480MB)
- ✅ Linux安装包 (KookForwarder-1.14.0.AppImage, ~420MB)
- ✅ 发布说明完整
- ✅ Docker镜像已推送

---

## 🧪 方式三：本地构建（不推荐，仅供测试）

⚠️ **警告**: 本地构建比较复杂，需要安装大量依赖，推荐使用GitHub Actions。

### 前提条件

```bash
# 1. 安装Python 3.11+
python3 --version

# 2. 安装Node.js 18+
node --version

# 3. 安装后端依赖
cd backend
pip install -r requirements.txt
pip install pyinstaller

# 4. 安装Playwright浏览器（~170MB）
playwright install chromium
playwright install-deps chromium

# 5. 安装前端依赖
cd ../frontend
npm install
```

### 构建步骤

#### 步骤1: 构建后端

```bash
cd /workspace
python build/build_backend.py
```

这会：
- 下载Chromium浏览器（~170MB）
- 准备Redis二进制文件（~5MB）
- 使用PyInstaller打包后端
- 输出到 `build/dist/kook-forwarder-backend`

**预计时间**: 10-15分钟（首次需要下载Chromium）

#### 步骤2: 构建前端

```bash
cd frontend

# 构建前端资源
npm run build

# 根据平台选择构建命令
# Windows
npm run electron:build:win

# macOS
npm run electron:build:mac

# Linux
npm run electron:build:linux
```

**预计时间**: 5-10分钟

#### 步骤3: 查看输出

安装包位置:
```
frontend/dist-electron/
├── KookForwarder-Setup-1.14.0.exe      # Windows
├── KookForwarder-1.14.0.dmg            # macOS
└── KookForwarder-1.14.0.AppImage       # Linux
```

---

## 📦 安装包说明

### Windows (.exe)

**文件名**: `KookForwarder-Setup-1.14.0.exe`  
**大小**: ~450MB  
**包含**:
- Python 3.11 运行时
- Chromium 浏览器
- Redis 服务
- 所有Python依赖
- Electron应用
- 完整前端资源

**安装方式**:
1. 双击运行安装程序
2. 选择安装路径
3. 点击"安装"
4. 完成后自动启动

### macOS (.dmg)

**文件名**: `KookForwarder-1.14.0.dmg`  
**大小**: ~480MB  
**包含**: 同Windows

**安装方式**:
1. 打开 .dmg 文件
2. 拖拽到"应用程序"文件夹
3. 首次打开：右键 → 打开
4. 同意安全警告

### Linux (.AppImage)

**文件名**: `KookForwarder-1.14.0.AppImage`  
**大小**: ~420MB  
**包含**: 同Windows

**使用方式**:
```bash
# 赋予执行权限
chmod +x KookForwarder-1.14.0.AppImage

# 运行
./KookForwarder-1.14.0.AppImage

# （可选）安装到系统
# Ubuntu/Debian
sudo apt install libfuse2
```

---

## 🐳 Docker镜像

### 镜像信息

**仓库**: `ghcr.io/gfchfjh/csbjjwt`  
**标签**:
- `latest` - 最新稳定版
- `1.14.0` - 特定版本
- `1.13` - 次版本
- `1` - 主版本

### 拉取镜像

```bash
# 拉取最新版本
docker pull ghcr.io/gfchfjh/csbjjwt:latest

# 拉取特定版本
docker pull ghcr.io/gfchfjh/csbjjwt:1.14.0
```

### 运行镜像

```bash
# 简单运行
docker run -d \
  --name kook-forwarder \
  -p 9527:9527 \
  -p 9528:9528 \
  -v $(pwd)/data:/app/data \
  ghcr.io/gfchfjh/csbjjwt:latest

# 使用docker-compose
docker-compose -f docker-compose.standalone.yml up -d
```

---

## 🔍 构建问题排查

### 问题1: GitHub Actions构建失败

**可能原因**:
- Git Tag未正确推送
- Secrets未配置
- 依赖下载失败

**解决方法**:
1. 检查Actions页面的错误日志
2. 确认Tag已推送: `git ls-remote --tags origin`
3. 重新推送Tag: `git push -f origin v1.14.0`

### 问题2: 本地构建Chromium下载失败

**解决方法**:
```bash
# 手动安装Chromium
playwright install chromium --with-deps

# 或设置代理
export HTTPS_PROXY=http://proxy.example.com:8080
playwright install chromium
```

### 问题3: PyInstaller打包失败

**解决方法**:
```bash
# 清理缓存
rm -rf build/build build/dist

# 重新打包
python build/build_backend.py
```

### 问题4: Electron构建失败

**解决方法**:
```bash
# 清理node_modules
cd frontend
rm -rf node_modules dist dist-electron

# 重新安装依赖
npm install

# 重新构建
npm run electron:build
```

---

## ✅ 发布检查清单

发布前请确认：

**代码质量**:
- [ ] 所有测试通过 (`pytest backend/tests/`)
- [ ] 前端测试通过 (`npm run test`)
- [ ] 代码已格式化和检查
- [ ] 无严重的Linter错误

**功能验证**:
- [ ] KOOK登录正常
- [ ] Discord转发正常
- [ ] Telegram转发正常
- [ ] 飞书转发正常
- [ ] 配置向导正常
- [ ] 图片转发正常

**文档更新**:
- [ ] README.md 已更新版本号
- [ ] CHANGELOG.md 已添加版本历史
- [ ] 快速开始指南已更新
- [ ] API文档已同步

**版本信息**:
- [ ] `frontend/package.json` 版本号正确
- [ ] Git Tag 已创建
- [ ] Git Tag 消息完整

**构建验证**:
- [ ] GitHub Actions 所有任务成功
- [ ] 所有3个安装包已上传
- [ ] Docker镜像已推送
- [ ] Release说明完整

**发布后验证**:
- [ ] 下载Windows安装包并测试
- [ ] 下载macOS安装包并测试
- [ ] 下载Linux安装包并测试
- [ ] Docker镜像运行正常
- [ ] Release页面链接正常

---

## 📞 获取帮助

如有问题：
1. 查看GitHub Actions日志
2. 查看本文档的问题排查部分
3. 提交Issue: https://github.com/gfchfjh/CSBJJWT/issues

---

## 📚 相关文档

- [快速开始指南](QUICK_START.md)
- [安装指南](INSTALLATION_GUIDE.md)
- [开发指南](docs/开发指南.md)
- [构建指南](build/README_BUILD.md)
- [发布指南](RELEASE_GUIDE.md)

---

**文档版本**: v1.0  
**更新日期**: 2025-10-23  
**维护者**: KOOK Forwarder Team
