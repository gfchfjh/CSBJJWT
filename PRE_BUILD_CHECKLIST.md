# 🔍 构建前检查清单

> **在执行构建前，请逐项检查以下内容，确保构建成功**

## 📋 检查清单

### ✅ 1. 环境准备

#### 1.1 Python环境
- [ ] Python 3.11+ 已安装
  ```bash
  python3 --version  # 应显示 3.11.x 或更高
  ```
- [ ] pip已安装并更新
  ```bash
  pip3 --version
  pip3 install --upgrade pip
  ```
- [ ] PyInstaller已安装
  ```bash
  pip3 install pyinstaller
  ```

#### 1.2 Node.js环境
- [ ] Node.js 18+ 已安装
  ```bash
  node --version  # 应显示 v18.x 或更高
  ```
- [ ] npm已安装
  ```bash
  npm --version
  ```

#### 1.3 系统工具
- [ ] Git已安装
  ```bash
  git --version
  ```
- [ ] (macOS) Xcode Command Line Tools已安装
  ```bash
  xcode-select -p
  ```

---

### ✅ 2. 项目依赖

#### 2.1 Python依赖
- [ ] 后端依赖已安装
  ```bash
  cd backend
  pip3 install -r requirements.txt
  ```
- [ ] Playwright浏览器已安装
  ```bash
  playwright install chromium
  playwright install-deps chromium  # Linux需要
  ```
- [ ] Pillow图像处理库已安装
  ```bash
  pip3 install Pillow
  ```

#### 2.2 前端依赖
- [ ] 前端依赖已安装
  ```bash
  cd frontend
  npm install
  ```

---

### ✅ 3. 资源文件准备

#### 3.1 图标文件 ⭐ **重要**
- [ ] PNG图标已生成
  ```bash
  python3 build/generate_simple_icon.py
  ```
  
- [ ] 平台图标已创建
  ```bash
  python3 build/create_platform_icons.py
  ```
  
- [ ] 验证图标文件存在：
  - [ ] `build/icon.ico` (Windows)
  - [ ] `build/icon.png` (Linux)
  - [ ] `build/icon.icns` (macOS，GitHub Actions自动创建)
  - [ ] `frontend/public/icon.png` (开发)

#### 3.2 Redis准备 ⚠️ **可选**
- [ ] Redis二进制文件准备（可选，推荐使用系统Redis）
  ```bash
  python3 build/prepare_redis.py
  ```
  
**注意：** 如果不打包Redis，需要确保目标系统已安装Redis

---

### ✅ 4. 配置文件检查

#### 4.1 PyInstaller配置
- [ ] `backend/build_backend.spec` 文件存在
- [ ] spec文件中的路径正确
- [ ] 隐藏导入列表完整

#### 4.2 Electron Builder配置
- [ ] `frontend/package.json` 中的build节点配置正确
- [ ] 版本号已更新
  ```json
  {
    "version": "1.13.2",  // 检查此处
    "build": { ... }
  }
  ```

#### 4.3 GitHub Actions配置
- [ ] `.github/workflows/build-and-release.yml` 文件存在
- [ ] Secrets配置完整（如果需要代码签名）
  - `GITHUB_TOKEN` (自动提供)
  - `MACOS_CERTIFICATE` (macOS签名，可选)
  - `MACOS_CERTIFICATE_PASSWORD` (macOS签名，可选)

---

### ✅ 5. 代码质量检查

#### 5.1 语法检查
- [ ] 后端代码无语法错误
  ```bash
  cd backend
  python3 -m py_compile app/main.py
  ```

#### 5.2 测试运行
- [ ] 后端测试通过
  ```bash
  cd backend
  pytest tests/ -v
  ```
  
- [ ] 前端测试通过
  ```bash
  cd frontend
  npm run test
  ```

---

### ✅ 6. Git状态检查

#### 6.1 版本控制
- [ ] 所有更改已提交
  ```bash
  git status  # 应显示 "nothing to commit"
  ```
  
- [ ] 版本号已更新
  - [ ] `frontend/package.json`
  - [ ] `README.md`

- [ ] Git Tag准备（可选）
  ```bash
  git tag v1.13.2
  git push origin v1.13.2
  ```

---

### ✅ 7. 磁盘空间检查

- [ ] 至少有10GB可用磁盘空间
  ```bash
  df -h .  # Linux/macOS
  ```
  
**构建所需空间估算：**
- 后端打包: ~200MB
- 前端打包: ~300MB
- Chromium浏览器: ~170MB
- 临时文件: ~1GB
- 最终安装包: ~450MB (Windows), ~480MB (macOS), ~420MB (Linux)

---

### ✅ 8. 网络连接检查

- [ ] 网络连接正常（下载依赖）
- [ ] GitHub访问正常（推送代码和触发Actions）
- [ ] npm registry访问正常
  ```bash
  npm ping
  ```

---

## 🚀 执行构建

### 方式1: 本地构建

#### Linux/macOS
```bash
# 一键构建
./build_installer.sh

# 或分步执行
cd build
./build_all.sh
```

#### Windows
```batch
# 一键构建
build_installer.bat

# 或分步执行
cd build
build_all.bat
```

### 方式2: GitHub Actions自动构建 ⭐ **推荐**

```bash
# 触发构建
./release_package.sh

# 或手动创建Tag
git tag v1.13.2
git push origin v1.13.2
```

**GitHub Actions将自动：**
1. ✅ 在3个平台构建（Windows/macOS/Linux）
2. ✅ 运行所有测试
3. ✅ 创建Release
4. ✅ 上传安装包

**预计时间：** 15-20分钟

---

## ❓ 常见问题

### Q1: 图标创建失败？
```bash
# 安装Pillow
pip3 install Pillow

# 重新生成
python3 build/generate_simple_icon.py
python3 build/create_platform_icons.py
```

### Q2: PyInstaller打包失败？
```bash
# 清理缓存
rm -rf backend/build backend/dist backend/*.spec.bak

# 更新PyInstaller
pip3 install --upgrade pyinstaller

# 重新打包
cd backend
pyinstaller --clean ../build/build_backend.spec
```

### Q3: Electron打包失败？
```bash
# 清理缓存
cd frontend
rm -rf node_modules dist dist-electron

# 重新安装依赖
npm install

# 重新构建
npm run build
npm run electron:build
```

### Q4: GitHub Actions失败？
1. 检查GitHub Actions日志
2. 验证Secrets配置
3. 检查.yml文件语法
4. 重新触发构建

---

## 📝 检查清单快速摘要

```bash
# 快速检查脚本
echo "=== 环境检查 ==="
python3 --version && echo "✅ Python" || echo "❌ Python"
node --version && echo "✅ Node.js" || echo "❌ Node.js"
git --version && echo "✅ Git" || echo "❌ Git"

echo ""
echo "=== 图标检查 ==="
ls build/icon.ico 2>/dev/null && echo "✅ Windows图标" || echo "❌ Windows图标"
ls build/icon.png 2>/dev/null && echo "✅ Linux图标" || echo "❌ Linux图标"
ls frontend/public/icon.png 2>/dev/null && echo "✅ 前端图标" || echo "❌ 前端图标"

echo ""
echo "=== 依赖检查 ==="
pip3 show pyinstaller >/dev/null 2>&1 && echo "✅ PyInstaller" || echo "❌ PyInstaller"
test -d frontend/node_modules && echo "✅ 前端依赖" || echo "❌ 前端依赖"
playwright list 2>/dev/null | grep -q chromium && echo "✅ Playwright" || echo "❌ Playwright"

echo ""
echo "=== Git状态 ==="
git status --short | wc -l | xargs -I {} echo "未提交文件: {} 个"

echo ""
echo "=== 磁盘空间 ==="
df -h . | tail -1
```

---

## 🎯 准备就绪？

当所有检查项都标记为 ✅ 后，您就可以开始构建了！

**推荐构建方式：**

```bash
# 最简单：触发GitHub Actions
./release_package.sh

# 等待15-20分钟后，在GitHub Releases页面下载安装包
```

**祝您构建顺利！** 🚀
