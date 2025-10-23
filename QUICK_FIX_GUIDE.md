# 快速修复指南 - Windows安装包问题

## 🎯 目标
解决GitHub Actions自动构建和发布流程中的问题，使Windows安装包能够自动上传到Release。

---

## ✅ 已完成的修复

本次修复已经自动应用了以下改进：

### 1. 修复GitHub Actions权限问题
**文件：** `.github/workflows/build-and-release.yml`  
**文件：** `.github/workflows/build-windows.yml`

**修改内容：**
```yaml
# 添加了权限声明
permissions:
  contents: write    # 允许创建和上传到Releases
  packages: write    # 允许推送Docker镜像
```

**效果：**
- ✅ 解决了 "HTTP 403: Resource not accessible by integration" 错误
- ✅ GitHub Actions现在可以自动上传文件到Release

### 2. 修复Docker构建依赖问题
**文件：** `Dockerfile`

**修改内容：**
```dockerfile
# 添加了编译工具
RUN apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    build-essential
```

**效果：**
- ✅ 解决了 psutil 等库的编译失败问题
- ✅ Docker镜像现在可以正常构建

---

## 🚀 下一步操作

### 步骤1: 提交修复
```bash
# 提交修改
git add .github/workflows/build-and-release.yml
git add .github/workflows/build-windows.yml
git add Dockerfile
git add WINDOWS_INSTALLER_ANALYSIS.md
git add QUICK_FIX_GUIDE.md

git commit -m "fix(ci): Add GitHub Actions permissions and Docker build dependencies

- Add contents:write and packages:write permissions to workflows
- Add gcc, g++, python3-dev to Dockerfile for psutil compilation
- This fixes the 403 error when uploading to releases
- This fixes the Docker build failure for arm64 platform
"

git push
```

### 步骤2: 触发新的构建

#### 选项A: 创建新的tag（推荐）
```bash
# 创建并推送新版本tag
git tag -a v1.14.1 -m "Release v1.14.1 - Fix CI/CD issues"
git push origin v1.14.1
```

#### 选项B: 手动触发workflow
1. 访问 https://github.com/gfchfjh/CSBJJWT/actions
2. 选择 "Build and Release" workflow
3. 点击 "Run workflow"
4. 输入版本号：v1.14.1
5. 点击 "Run workflow" 按钮

### 步骤3: 验证修复
1. 等待GitHub Actions完成（约10-15分钟）
2. 检查 https://github.com/gfchfjh/CSBJJWT/releases/latest
3. 确认以下文件已自动上传：
   - ✅ Windows: `*.exe`
   - ✅ Linux: `*.AppImage`
   - ✅ macOS: `*.dmg`（如果有签名证书）

---

## 📋 可选的额外改进

以下改进不影响核心功能，可以后续逐步实施：

### 改进1: 统一构建配置
**问题：** 同时存在 `build/electron-builder.yml` 和 `frontend/package.json` 两个配置文件

**建议：** 删除 `build/electron-builder.yml`，统一使用 `frontend/package.json`

```bash
# 删除冗余配置
rm build/electron-builder.yml

# 更新 .github/workflows 中的引用
# 确保使用 frontend/package.json 的配置
```

### 改进2: 修复文件命名
**问题：** 生成的文件名不包含版本号和架构信息

**修改文件：** `frontend/package.json`
```json
{
  "build": {
    "artifactName": "${productName}_v${version}_${platform}_${arch}.${ext}",
    "win": {
      "artifactName": "${productName}_v${version}_Windows_${arch}.${ext}"
    }
  }
}
```

### 改进3: 生成应用图标
**问题：** 缺少 `build/icon.ico` 和 `build/icon.icns`

**方法1: 使用已有脚本**
```bash
cd build
python3 generate_icon.py
```

**方法2: 手动转换**
```bash
# 使用ImageMagick转换PNG到ICO
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico

# macOS上转换到ICNS
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
# ... 更多尺寸
iconutil -c icns icon.iconset
```

### 改进4: 添加下载说明到README
**修改文件：** `README.md`

```markdown
## 📥 下载安装

### Windows
[下载最新版 Windows 安装包](https://github.com/gfchfjh/CSBJJWT/releases/latest/download/KOOK.Setup.1.13.3.exe)

### Linux
[下载最新版 Linux AppImage](https://github.com/gfchfjh/CSBJJWT/releases/latest/download/KOOK.-1.13.3.AppImage)

### macOS
暂时不可用（需要代码签名证书）

### Docker
\```bash
docker pull ghcr.io/gfchfjh/csbjjwt:latest
\```
```

---

## 🔍 验证清单

修复完成后，请验证以下项目：

- [ ] GitHub Actions运行成功（无红色×）
- [ ] Release页面有3个文件（Windows、Linux、Docker）
- [ ] Windows安装包可以直接下载
- [ ] 文件命名符合规范
- [ ] Docker镜像可以正常拉取
- [ ] README中有明确的下载链接

---

## 📞 如果仍有问题

### 检查GitHub Actions日志
```bash
# 使用gh cli查看最新运行日志
gh run list -R gfchfjh/CSBJJWT --limit 1
gh run view <run-id> --log
```

### 检查权限设置
1. 访问仓库 Settings → Actions → General
2. 在 "Workflow permissions" 中确认选择了 "Read and write permissions"
3. 确认勾选了 "Allow GitHub Actions to create and approve pull requests"

### 手动上传（临时方案）
如果自动上传仍然失败，可以手动上传：
```bash
# 从GitHub Actions下载artifact
gh run download <run-id>

# 手动上传到Release
gh release upload v1.14.1 windows-installer/*.exe
```

---

## 📚 相关文档

- [详细问题分析报告](./WINDOWS_INSTALLER_ANALYSIS.md)
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [Electron Builder文档](https://www.electron.build/)

---

## ✨ 修复历史

| 日期 | 版本 | 修复内容 |
|------|------|----------|
| 2025-10-23 | v1.14.1 | 修复GitHub Actions权限和Docker依赖 |
| 2025-10-23 | v1.14.0 | 初始发布 |
