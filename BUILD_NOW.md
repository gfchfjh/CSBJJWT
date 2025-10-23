# 🚀 立即构建安装包 - 操作指南

**当前状态**: ✅ 所有文件已准备就绪  
**当前分支**: `cursor/bc-9bed8f66-0a1e-4dcb-b352-a4b74617e46e-27ea`

---

## 📊 构建选项

### 🌟 选项1: GitHub Actions自动构建（推荐）

**优点**:
- ⚡ 自动化，15-20分钟完成
- 🎯 同时构建3个平台（Windows/macOS/Linux）
- 📦 自动上传到GitHub Releases
- ✅ 专业CI/CD环境，成功率高

**步骤**:

```bash
# 1. 切换到main分支并合并更改
git checkout main
git merge cursor/bc-9bed8f66-0a1e-4dcb-b352-a4b74617e46e-27ea

# 2. 推送到GitHub
git push origin main

# 3. 创建发布Tag
git tag -a v1.14.0 -m "Release v1.14.0 - 完整构建系统"
git push origin v1.14.0

# 4. GitHub Actions自动触发构建
# 访问: https://github.com/gfchfjh/CSBJJWT/actions
```

**预期结果**:
- 15-20分钟后，3个平台安装包自动生成
- 下载地址: https://github.com/gfchfjh/CSBJJWT/releases/tag/v1.14.0

---

### 🔧 选项2: 本地构建（耗时较长）

**优点**:
- 🏠 完全本地控制
- 🧪 可以立即测试

**缺点**:
- ⏱️ 耗时30-60分钟
- 💻 只能构建当前平台
- 🔧 需要处理平台特定问题

**步骤**:

```bash
# 1. 安装所有依赖（如果还没安装）
cd /workspace/backend
pip install -r requirements.txt
pip install pyinstaller

cd /workspace/frontend
npm install

# 2. 准备Chromium（可选）
cd /workspace
python3 build/prepare_chromium.py
# 选择: 1 (首次运行下载)

# 3. 准备Redis（可选）
python3 build/prepare_redis_enhanced.py
# 选择: 1 (当前平台)

# 4. 构建后端
cd backend
pyinstaller --clean --noconfirm build_backend.spec

# 5. 构建前端
cd ../frontend
npm run build
npm run electron:build

# 6. 查看构建产物
ls -lh dist-electron/
```

**预期结果**:
- `frontend/dist-electron/` 目录中生成当前平台的安装包

---

## ⚡ 快速执行（推荐方式1）

如果您有GitHub推送权限，运行：

```bash
cd /workspace
./release_complete.sh
```

然后选择：
- 是否更新版本号？输入 `y`，版本号 `1.14.0`
- 选择构建方式：输入 `1` (创建Tag触发GitHub Actions)

脚本会自动完成所有操作！

---

## 📋 构建前检查

```bash
# 验证环境
python3 build/verify_build_readiness.py

# 查看当前状态
git status
git log --oneline -3

# 检查新文件
find . -name "*.py" -newer README.md -type f | wc -l  # 应该看到新文件
```

---

## 🎯 推荐流程

**最快速度（15分钟）**:

1. **合并到main分支**:
   ```bash
   git checkout main
   git merge cursor/bc-9bed8f66-0a1e-4dcb-b352-a4b74617e46e-27ea
   git push origin main
   ```

2. **触发构建**:
   ```bash
   ./release_complete.sh
   # 选择: y (更新版本)
   # 输入: 1.14.0
   # 选择: 1 (GitHub Actions)
   ```

3. **等待构建**:
   - 访问: https://github.com/gfchfjh/CSBJJWT/actions
   - 等待15-20分钟

4. **下载安装包**:
   - 访问: https://github.com/gfchfjh/CSBJJWT/releases/tag/v1.14.0

---

## ❓ 您想选择哪种方式？

### 选项A: GitHub Actions自动构建（推荐⭐）
```bash
# 运行此命令
./release_complete.sh
```

### 选项B: 本地构建
```bash
# 运行此命令
./build_installer.sh
```

---

**需要我帮您执行哪个选项？**
