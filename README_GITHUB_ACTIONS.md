# 🚀 GitHub Actions 自动构建 - 快速开始

**版本**: v17.0.0  
**状态**: ✅ 完全配置完成，随时可触发  

---

## ⚡ 快速开始（5分钟）

### 方法1: 使用一键部署脚本（推荐）

```bash
# 在项目根目录执行
./deploy-v17.0.0.sh
```

脚本会自动：
1. ✅ 添加所有更改
2. ✅ 创建commit
3. ✅ 创建v17.0.0 tag
4. ✅ 推送到GitHub
5. ✅ 触发自动构建

---

### 方法2: 手动执行命令

```bash
cd /workspace

# 1. 添加所有更改
git add .

# 2. 提交
git commit -m "feat: v17.0.0 深度优化版发布"

# 3. 创建tag
git tag -a v17.0.0 -m "Release v17.0.0 - 深度优化版"

# 4. 推送（替换<分支名>为你的分支）
git push origin cursor/kook-message-forwarding-system-setup-4d5d
git push origin v17.0.0
```

---

### 方法3: 在GitHub网页手动触发

1. 访问 https://github.com/gfchfjh/CSBJJWT
2. 点击 "Actions" 标签
3. 选择 "Build Windows Installer"
4. 点击 "Run workflow"
5. 选择分支，点击 "Run workflow" 按钮

---

## 📊 构建状态监控

### 查看构建进度
```
https://github.com/gfchfjh/CSBJJWT/actions
```

### 构建状态含义
- 🟡 **黄色圆点**: 正在构建中
- 🟢 **绿色对勾**: 构建成功
- 🔴 **红色叉号**: 构建失败

### 预计时间
- Windows: 15-20分钟
- macOS: 20-25分钟  
- Linux: 10-15分钟
- 全平台: 25-30分钟（并行）

---

## 📥 下载安装包

### 构建完成后（Artifacts）

1. 访问 Actions 页面
2. 点击完成的工作流
3. 下拉到 "Artifacts" 部分
4. 点击下载 "windows-installer-x64"

**保留期**: 30天

---

### 正式发布（Release）

1. 访问 https://github.com/gfchfjh/CSBJJWT/releases
2. 找到 "v17.0.0" Release
3. 在 "Assets" 下载安装包

**文件名**: `KOOK消息转发系统-v17.0.0-win-x64.exe`  
**大小**: ~100-120MB  
**永久保存**

---

## 🎯 工作流说明

### build-windows.yml
**专门构建Windows安装包**

触发条件:
- 推送tag（v*）
- 手动触发

输出:
- Windows x64 NSIS安装程序
- 自动创建GitHub Release

---

### build-all-platforms.yml
**同时构建所有平台**

触发条件:
- 推送tag（v*）
- 手动触发

输出:
- Windows安装包
- macOS DMG
- Linux AppImage
- 统一Release

---

## ✅ 已完成的配置

### 工作流文件
```
✅ .github/workflows/build-windows.yml
✅ .github/workflows/build-all-platforms.yml
```

### 前端构建
```
✅ frontend/dist/ (已构建完成)
✅ 2097个模块已编译
✅ 输出大小: 2.8MB
```

### 依赖和配置
```
✅ 所有npm依赖已安装
✅ electron-builder配置完成
✅ 图标和资源文件就绪
✅ LICENSE文件存在
```

### 文档
```
✅ GITHUB_ACTIONS_SETUP.md (详细设置指南)
✅ RELEASE_CHECKLIST.md (发布清单)
✅ README_GITHUB_ACTIONS.md (本文件)
```

---

## 🔧 工作流配置详情

### Node.js环境
```yaml
node-version: '18'  # LTS版本
```

### 构建步骤
```
1. Checkout代码
2. 安装Node.js 18
3. 安装依赖（--legacy-peer-deps）
4. 安装sass-embedded
5. 构建前端（npm run build）
6. electron-builder打包
7. 上传Artifacts
8. 创建Release（如果是tag）
```

### 构建命令
```bash
npx electron-builder --win --x64 --publish never
```

---

## 📝 Release Notes（自动生成）

GitHub Actions会自动生成Release，包含：

### 标题
```
KOOK消息转发系统 v17.0.0
```

### 内容
- ✨ 主要更新列表
- 📦 下载说明
- 📖 文档链接
- ⚠️ 重要提示
- 🐛 问题反馈链接

---

## ❓ 常见问题

### Q: 推送后没有触发构建？

**检查**:
1. 是否创建了tag？（必须v开头）
2. tag是否成功推送到远程？
3. 工作流文件是否在正确位置？

**验证**:
```bash
# 查看本地tag
git tag -l

# 查看远程tag
git ls-remote --tags origin
```

---

### Q: 构建失败怎么办？

**步骤**:
1. 进入Actions页面
2. 点击失败的工作流
3. 展开失败的步骤
4. 查看错误日志

**常见错误**:
- 依赖安装失败 → 检查package.json
- 构建超时 → 检查构建配置
- 资源缺失 → 检查build/目录

---

### Q: 没有生成Release？

**原因**: 只有tag才会创建Release

**确认**:
```bash
# 必须推送tag
git push origin v17.0.0
```

如果推送了分支但忘记tag，可以：
```bash
git tag -a v17.0.0 -m "Release"
git push origin v17.0.0
```

---

### Q: 如何更新已发布的Release？

**方法1**: 删除tag重新发布
```bash
# 本地删除
git tag -d v17.0.0

# 远程删除
git push origin :refs/tags/v17.0.0

# 重新创建并推送
git tag -a v17.0.0 -m "Release v17.0.0"
git push origin v17.0.0
```

**方法2**: 发布新版本
```bash
git tag -a v17.0.1 -m "Hotfix"
git push origin v17.0.1
```

---

## 📊 构建监控

### 实时状态

访问Actions查看实时日志：
```
https://github.com/gfchfjh/CSBJJWT/actions
```

### 构建时间线

```
0:00  - 开始构建
0:30  - 检出代码完成
1:00  - Node.js环境设置完成
3:00  - 依赖安装完成
4:00  - 前端构建完成
15:00 - electron-builder打包完成
16:00 - 上传Artifacts完成
17:00 - 创建Release完成
```

---

## 🎉 成功标志

### 构建成功后你会看到

1. **Actions页面**
   - ✅ 绿色对勾
   - "Build Windows Installer" 显示成功

2. **Artifacts区域**
   - 📦 "windows-installer-x64" 可下载
   - 文件大小约100-120MB

3. **Releases页面**
   - 🎊 v17.0.0 Release已创建
   - 📥 安装包已上传到Assets
   - 📝 Release Notes自动生成

---

## 🚀 立即执行

### 现在就可以开始！

#### 选项A: 一键部署（最简单）
```bash
./deploy-v17.0.0.sh
```

#### 选项B: 手动推送（更灵活）
```bash
git add .
git commit -m "feat: v17.0.0 release"
git tag -a v17.0.0 -m "Release v17.0.0"
git push origin <你的分支名>
git push origin v17.0.0
```

#### 选项C: 网页触发（无需命令行）
访问 GitHub → Actions → Run workflow

---

### ⏱️ 然后...

1. **0分钟**: 推送完成
2. **1分钟**: GitHub Actions开始构建
3. **15分钟**: Windows构建完成
4. **20分钟**: 下载安装包
5. **30分钟**: 测试并发布！

---

## 📞 需要帮助？

### 详细文档
- [GitHub Actions设置指南](GITHUB_ACTIONS_SETUP.md)
- [发布检查清单](RELEASE_CHECKLIST.md)
- [Windows构建指南](WINDOWS_BUILD_GUIDE.md)
- [构建状态报告](BUILD_STATUS_REPORT.md)

### 在线资源
- GitHub Actions文档: https://docs.github.com/actions
- electron-builder文档: https://www.electron.build/

---

## ✨ 最后的话

**一切就绪！推送代码，等待15分钟，v17.0.0就构建完成了！** 🎊

```
git push origin <分支名> && git push origin v17.0.0
```

**祝发布顺利！** 🚀
