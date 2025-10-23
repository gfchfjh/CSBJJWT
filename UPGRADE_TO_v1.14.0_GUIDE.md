# 🚀 升级到 v1.14.0 操作指南

**3步完成升级，立即享受一键安装体验！**

---

## 📋 快速概览

**升级时间**: 5-10分钟  
**难度等级**: ⭐ 简单  
**需要权限**: Git推送权限  

---

## 🎯 立即开始

### 步骤1: 拉取最新代码 (1分钟)

```bash
cd /workspace  # 或您的项目目录

# 拉取所有更新
git pull origin main

# 查看新增文件
git status
git log --oneline -5
```

**预期结果**: 看到13个新增文件，包括：
- ✅ `release_complete.sh`
- ✅ `build/verify_build_readiness.py`
- ✅ `build/prepare_chromium.py`
- ✅ `build/prepare_redis_enhanced.py`
- ✅ `backend/app/utils/environment_checker.py`
- ✅ 等等...

---

### 步骤2: 验证构建环境 (2分钟)

```bash
# 运行构建验证工具
python3 build/verify_build_readiness.py
```

**预期输出**:
```
🔍 KOOK消息转发系统 - 构建就绪性检查
========================================

1️⃣  检查基础命令工具
✅ Python 3: Python 3.11.x
✅ Node.js: v18.x.x
✅ npm: 9.x.x
✅ Git: 2.x.x

2️⃣  检查Python依赖包
✅ 所有Python包已安装 (8/8)

3️⃣  检查前端依赖包
✅ 所有npm包已安装

4️⃣  检查项目文件结构
✅ 所有必需文件都存在

5️⃣  检查图标文件
⚠️  部分图标文件缺失
  - macOS图标 (icon.icns)

6️⃣  检查Playwright浏览器
✅ Playwright Chromium已安装

7️⃣  检查脚本执行权限
✅ 所有脚本可执行

📊 检查总结
总检查项: 7
通过: 6
错误: 0
警告: 1

💡 修复建议
ℹ️  生成图标:
  python build/create_platform_icons.py

✅ 构建环境已就绪，可以开始构建！
```

**如果有错误**: 按照提示修复，例如：
```bash
# 安装Python依赖
pip install -r backend/requirements.txt

# 安装npm依赖
cd frontend && npm install

# 安装Playwright浏览器
playwright install chromium
```

---

### 步骤3: 触发构建和发布 (2分钟操作 + 15分钟等待)

```bash
# 运行完整发布脚本
./release_complete.sh
```

**交互式流程**:

1. **版本号确认**
   ```
   当前版本: v1.13.3
   是否要更新版本号？(y/N):
   ```
   - 输入 `y` 并输入新版本号 `1.14.0`
   - 或输入 `N` 保持当前版本

2. **Git状态检查**
   ```
   🔍 检查Git状态...
   ✅ Git状态检查通过
   ```

3. **构建环境验证**
   ```
   🔍 验证构建环境...
   ✅ 构建环境验证通过
   ```

4. **选择发布方式**（重要！）
   ```
   选择构建方式:
     1) 仅创建Tag（触发GitHub Actions自动构建）推荐⭐
     2) 本地完整构建（耗时较长）
     3) 跳过构建
   请选择 (1/2/3):
   ```
   
   **推荐选择 `1`** - 自动构建，省时省力
   
5. **确认并执行**
   ```
   🏷️  创建Git Tag v1.14.0...
   ✅ Git Tag创建成功
   
   🚀 推送到GitHub...
   ✅ 已推送到GitHub
   ✅ GitHub Actions将自动开始构建
   
   ℹ️  查看进度: https://github.com/gfchfjh/CSBJJWT/actions
   ```

6. **等待GitHub Actions构建**（15-20分钟）
   - 访问: https://github.com/gfchfjh/CSBJJWT/actions
   - 等待3个构建任务完成：
     - ✅ Build Windows
     - ✅ Build macOS
     - ✅ Build Linux

7. **查看发布结果**
   - 访问: https://github.com/gfchfjh/CSBJJWT/releases/tag/v1.14.0
   - 下载并测试安装包

---

## ✅ 完成验证

### 验证清单

- [ ] 所有构建任务都成功完成
- [ ] GitHub Release已创建
- [ ] 3个平台的安装包都已上传
- [ ] 下载并测试Windows安装包
- [ ] 下载并测试macOS安装包
- [ ] 下载并测试Linux AppImage

### 测试安装包

**Windows**:
```
1. 下载 KOOK消息转发系统_v1.14.0_Windows_x64.exe
2. 双击运行
3. 完成安装向导
4. 启动应用并测试基本功能
```

**macOS**:
```
1. 下载 KOOK消息转发系统_v1.14.0_macOS.dmg
2. 打开DMG文件
3. 拖拽到Applications文件夹
4. 首次打开：右键 → 打开
5. 测试基本功能
```

**Linux**:
```
1. 下载 KOOK消息转发系统_v1.14.0_Linux_x64.AppImage
2. chmod +x *.AppImage
3. ./KOOK消息转发系统_v1.14.0_Linux_x64.AppImage
4. 测试基本功能
```

---

## 🔧 可选：本地构建（开发者）

如果选择了选项2（本地构建），需要执行：

```bash
# 1. 准备Chromium（可选）
python3 build/prepare_chromium.py
# 选择策略1（首次运行下载）

# 2. 准备Redis（可选）
python3 build/prepare_redis_enhanced.py
# 选择当前平台或所有平台

# 3. 构建后端
cd backend
pyinstaller --clean --noconfirm build_backend.spec
cd ..

# 4. 构建前端
cd frontend
npm run build
npm run electron:build
cd ..

# 5. 查看构建产物
ls -lh frontend/dist-electron/
```

---

## 📊 新功能一览

### 1. 环境自动检查

启动应用时自动检查环境，发现问题自动修复！

**体验位置**: 后端启动时控制台输出

**功能亮点**:
- ✅ 自动下载Playwright Chromium
- ✅ 自动创建数据目录
- ✅ 智能诊断网络、磁盘等问题
- ✅ 提供详细的修复建议

### 2. 一键发布脚本

从代码提交到发布，一个命令搞定！

**使用方式**: `./release_complete.sh`

**功能亮点**:
- ✅ 自动版本号管理
- ✅ Git Tag自动创建
- ✅ 触发CI/CD自动构建
- ✅ 生成发布说明

### 3. 配置模板系统

6个预置模板，一键导入频道映射！

**体验位置**: 应用内 → 频道映射 → 导入模板

**模板列表**:
- 🎮 游戏社区
- 💻 技术社区
- 🎬 内容创作者
- 🔄 跨平台镜像
- 👑 仅官方消息
- 🚨 仅重要警报

**配置文件**: `config_templates/frequency_mapping_templates.json`

### 4. 视频教程规划

8个视频教程脚本已完成，等待录制！

**查看详情**: `docs/video_tutorials_resources.md`

**教程清单**:
1. 快速开始（5分钟）
2. Cookie获取（3分钟）
3. Discord配置（2分钟）
4. Telegram配置（4分钟）
5. 飞书配置（5分钟）
6. 频道映射（3分钟）
7. 过滤规则（3分钟）
8. 故障排查（4分钟）

---

## 📚 文档更新

### 新增文档

- ✅ `v1.14.0_COMPLETE_UPGRADE_REPORT.md` - 完整升级报告
- ✅ `UPGRADE_TO_v1.14.0_GUIDE.md` - 本操作指南
- ✅ `docs/video_tutorials_resources.md` - 视频教程资源

### 配置示例

- ✅ `backend/.env.production.example` - 生产环境配置
- ✅ `config_templates/frequency_mapping_templates.json` - 映射模板

---

## 🆘 遇到问题？

### 常见问题

**Q1: 构建验证失败？**
```bash
# 安装缺失的依赖
pip install -r backend/requirements.txt
cd frontend && npm install
playwright install chromium
```

**Q2: GitHub Actions构建失败？**
- 检查: https://github.com/gfchfjh/CSBJJWT/actions
- 查看日志找到错误原因
- 修复后重新推送Tag

**Q3: 安装包太大？**
- Chromium策略选择"首次运行下载"
- 不打包Redis（使用系统Redis或运行时下载）

### 获取帮助

- 📖 [完整升级报告](v1.14.0_COMPLETE_UPGRADE_REPORT.md)
- 🐛 [提交Issue](https://github.com/gfchfjh/CSBJJWT/issues)
- 💬 [讨论区](https://github.com/gfchfjh/CSBJJWT/discussions)

---

## 🎉 升级完成

恭喜！您已成功升级到 v1.14.0

### 现在您可以：

✅ **一键构建**: `./release_complete.sh`  
✅ **自动发布**: GitHub Actions  
✅ **预编译包**: 三平台安装包  
✅ **环境检查**: 自动诊断修复  
✅ **配置模板**: 一键导入  

### 下一步：

1. 📦 测试预编译安装包
2. 📺 录制视频教程（可选）
3. 📢 宣传新版本
4. 📊 收集用户反馈

---

<div align="center">

**🎊 升级到v1.14.0，享受一键安装的便利！**

**现在可以自信地说：**
# **"KOOK消息转发系统已经可以一键安装正常使用！"** ✅

Made with ❤️ by KOOK Forwarder Team

[GitHub](https://github.com/gfchfjh/CSBJJWT) • [文档](docs/) • [发布](https://github.com/gfchfjh/CSBJJWT/releases)

</div>
