# Windows 快速开始指南

**适用版本**: v18.0.2+  
**更新日期**: 2025-11-03  
**预计时间**: 10-15 分钟  
**难度级别**: ⭐⭐☆☆☆ (中等)  

---

## 📋 开始之前

### 必需软件

| 软件 | 版本要求 | 下载链接 |
|-----|---------|---------|
| Python | 3.11+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| Git | 2.0+ | https://git-scm.com/download/win |

### 系统要求

- Windows 10/11 (64位)
- 磁盘空间 5GB+
- 内存 8GB+ (推荐)
- 稳定的网络连接

---

## 🚀 方式1: 从源码运行（推荐）

**适用场景**: 开发、测试、快速体验

### 步骤1: 克隆代码

```cmd
# 打开 CMD（Win + R → 输入 cmd → 回车）

# 进入桌面
cd %USERPROFILE%\Desktop

# 克隆仓库
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT
```

### 步骤2: 安装后端依赖

```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r backend\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 补充可能缺失的依赖
pip install discord-webhook python-telegram-bot loguru apscheduler psutil prometheus-client -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤3: 安装前端依赖

```cmd
# 打开新的 CMD 窗口
cd %USERPROFILE%\Desktop\CSBJJWT\frontend

# 安装依赖
npm install
```

### 步骤4: 启动服务

**后端窗口（第一个 CMD）：**
```cmd
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 9527 --reload
```

**前端窗口（第二个 CMD）：**
```cmd
npm run dev
```

### 步骤5: 访问应用

1. 等待两个服务都启动完成
2. 浏览器访问：`http://localhost:5173/home`
3. 开始使用！

---

## 🛠️ 方式2: 手动构建

### 步骤1: 克隆代码

```bash
# 1. 选择工作目录
cd C:\Users\你的用户名\Desktop

# 2. 克隆仓库
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT
```

### 步骤2: 构建后端

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
call venv\Scripts\activate.bat

# 4. 升级 pip
python -m pip install --upgrade pip

# 5. 安装依赖
pip install -r requirements.txt

# 6. 安装额外依赖
pip install pyinstaller loguru discord-webhook python-telegram-bot psutil beautifulsoup4 apscheduler prometheus_client ddddocr

# 7. 验证安装
pip list | findstr "fastapi uvicorn playwright"
```

### 步骤3: 打包后端

```bash
# 1. 回到项目根目录
cd ..

# 2. 运行 PyInstaller
pyinstaller build\pyinstaller.spec --clean --noconfirm

# 3. 验证打包结果
dir dist\KOOKForwarder\KOOKForwarder.exe

# 4. 测试后端（可选）
cd dist\KOOKForwarder
KOOKForwarder.exe
# 看到 "Uvicorn running" 后按 Ctrl+C 停止
cd ..\..
```

### 步骤4: 构建前端

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖（使用 legacy-peer-deps）
npm install --legacy-peer-deps

# 3. 构建 Electron 应用
npm run electron:build:win

# 4. 等待构建完成（5-10分钟）
```

### 步骤5: 获取安装包

```bash
# 查看构建结果
dir dist-electron

# 安装包位置
# dist-electron\KOOK消息转发系统 Setup 18.0.1.exe
```

---

## 🔧 测试验证

### 验证1: 后端独立运行

```bash
# 1. 进入后端目录
cd dist\KOOKForwarder

# 2. 运行后端
KOOKForwarder.exe

# 3. 预期输出（部分）:
# ✅ 日志系统已初始化
# ✅ 智能默认配置系统已初始化
# ✅ 账号限制器初始化完成
# INFO: Application startup complete.
# INFO: Uvicorn running on http://127.0.0.1:8000

# 4. 按 Ctrl+C 停止
```

### 验证2: API 接口测试

```bash
# 在浏览器中访问:
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health

# 或使用 curl:
curl http://127.0.0.1:8000/health
```

### 验证3: Electron 应用测试

```bash
# 1. 双击安装包安装
# 2. 启动应用
# 3. 查看是否正常显示 UI

# 如果遇到 "fetch failed":
# - 参考 [TROUBLESHOOTING_WINDOWS.md](./TROUBLESHOOTING_WINDOWS.md)
# - 查看 [明天继续方案.md](./明天继续方案.md)
```

---

## ⚠️ 常见问题快速解决

### 问题1: "闪退"

**原因**: 脚本运行出错

**解决**:
```bash
# 方法1: 在命令行中运行
cmd
cd 脚本所在目录
脚本名.bat

# 方法2: 使用安全模式脚本
KOOK_Installer_Safe.bat
```

### 问题2: npm install 失败

**错误**: `ERESOLVE could not resolve`

**解决**:
```bash
cd frontend
npm install --legacy-peer-deps
```

### 问题3: PyInstaller 找不到模块

**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
# 确保在虚拟环境中
cd backend
call venv\Scripts\activate.bat

# 安装缺失模块
pip install xxx

# 重新打包
cd ..
pyinstaller build\pyinstaller.spec --clean --noconfirm
```

### 问题4: 端口被占用

**错误**: `[Errno 10048] Address already in use`

**解决**:
```bash
# 查找占用进程
netstat -ano | findstr :8000

# 结束进程（替换 <PID> 为实际进程号）
taskkill /F /PID <PID>
```

### 问题5: 前端空白页

**错误**: 浏览器显示空白页

**解决**:
```bash
# 1. 确认访问正确的URL
http://localhost:5173/home

# 2. 强制刷新浏览器
按 Ctrl + Shift + R

# 3. 查看控制台错误
按 F12 查看 Console 标签
```

---

## 📊 构建时间预估

| 步骤 | 预估时间 | 依赖网络 |
|-----|---------|---------|
| 克隆代码 | 1-3 分钟 | ✅ 是 |
| 安装 Python 依赖 | 2-5 分钟 | ✅ 是 |
| 安装 Node.js 依赖 | 3-8 分钟 | ✅ 是 |
| PyInstaller 打包 | 2-4 分钟 | ❌ 否 |
| Electron 打包 | 5-10 分钟 | ❌ 否 |
| **总计** | **15-30 分钟** | - |

**注意**:
- 首次构建时间较长（需要下载依赖）
- 二次构建会快很多（使用缓存）
- 网络速度影响下载时间

---

## 🎯 下一步

### 完成构建后

1. **安装应用**
   - 运行安装包
   - 完成安装向导

2. **初次配置**
   - 启动应用
   - 按照欢迎向导配置
   - 添加 KOOK Cookie
   - 配置转发平台

3. **开始使用**
   - 参考 [docs/用户手册.md](./docs/用户手册.md)
   - 查看教程: [docs/tutorials/](./docs/tutorials/)

### 遇到问题

1. **查看故障排查指南**
   - [TROUBLESHOOTING_WINDOWS.md](./TROUBLESHOOTING_WINDOWS.md)
   - [INSTALLATION_TROUBLESHOOTING.md](./INSTALLATION_TROUBLESHOOTING.md)

2. **提交 Issue**
   - https://github.com/gfchfjh/CSBJJWT/issues

---

## 📚 相关文档

### 核心文档
- [README.md](./README.md) - 项目主文档
- [CHANGELOG.md](./CHANGELOG.md) - 完整更新日志
- [PROJECT_STATUS_v18.md](./PROJECT_STATUS_v18.md) - 项目当前状态

### 故障排查
- [TROUBLESHOOTING_WINDOWS.md](./TROUBLESHOOTING_WINDOWS.md) - Windows 故障排查指南
- [INSTALLATION_TROUBLESHOOTING.md](./INSTALLATION_TROUBLESHOOTING.md) - 安装问题解决

### 使用文档
- [docs/用户手册.md](./docs/用户手册.md) - 用户手册
- [docs/tutorials/](./docs/tutorials/) - 教程文档

---

## 🎉 完成！

恭喜你完成了 KOOK 消息转发系统的 Windows 构建！

如有问题，随时查看文档或提交 Issue。

---

**文档版本**: 1.0  
**最后更新**: 2025-11-03  
**维护者**: KOOK Development Team
