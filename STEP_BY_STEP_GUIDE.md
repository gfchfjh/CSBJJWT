# 方案1详细操作指南 - 一步一步完成

**用户**: tanzu (Windows 11)  
**方案**: 重新构建修复版本  
**预计时间**: 20-30分钟  
**难度**: ⭐⭐ 简单

---

## 📋 开始前的准备清单

### 第一步：检查您的电脑环境

打开 **命令提示符**（Win+R，输入 `cmd`，回车）

#### 检查1: Python版本
```cmd
python --version
```

**期望输出**:
```
Python 3.11.x 或更高
```

**如果显示错误或版本过低**:
1. 访问: https://www.python.org/downloads/
2. 下载Python 3.11或更高版本
3. 安装时**必须勾选** "Add Python to PATH"
4. 安装完成后重新打开命令提示符测试

---

#### 检查2: Node.js版本
```cmd
node --version
```

**期望输出**:
```
v18.x.x 或更高
```

**如果显示错误或版本过低**:
1. 访问: https://nodejs.org/
2. 下载LTS版本（推荐20.x）
3. 安装
4. 重新打开命令提示符测试

---

#### 检查3: Git（可选但推荐）
```cmd
git --version
```

**如果没有Git**:
1. 访问: https://git-scm.com/download/win
2. 下载并安装
3. 或者手动下载项目ZIP文件

---

### 第二步：创建工作目录

选择一个有足够空间的位置（需要约2GB）

**推荐位置**:
```
C:\KOOK\
```

打开命令提示符，执行：
```cmd
mkdir C:\KOOK
cd C:\KOOK
```

---

## 📥 第一部分：获取项目和修复文件

### 步骤1: 下载原项目

#### 方法A：使用Git（推荐）
```cmd
cd C:\KOOK
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT
```

#### 方法B：手动下载
1. 访问: https://github.com/gfchfjh/CSBJJWT
2. 点击绿色按钮 "Code" → "Download ZIP"
3. 解压到 `C:\KOOK\CSBJJWT`
4. 打开命令提示符:
   ```cmd
   cd C:\KOOK\CSBJJWT
   ```

**验证**:
```cmd
dir
```

**应该看到**:
```
backend
frontend
build
docs
README.md
...
```

---

### 步骤2: 获取修复文件

#### 📝 核心修复文件：build/pyinstaller.spec

**方法A：复制我提供的内容**

1. 打开记事本
2. 复制以下完整内容：

```python
# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller打包配置 - 修复版
✅ 修复：输出文件名改为 KOOKForwarder，匹配 Electron 期望
"""

block_cipher = None

# 后端主文件
backend_main = Analysis(
    ['../backend/app/main.py'],
    pathex=['../backend'],
    binaries=[],
    datas=[
        # 包含数据文件
        ('../backend/data', 'data'),
        ('../backend/app/api', 'app/api'),
        ('../backend/app/processors', 'app/processors'),
        ('../backend/app/forwarders', 'app/forwarders'),
        ('../backend/app/utils', 'app/utils'),
        ('../backend/app/kook', 'app/kook'),
        ('../backend/app/queue', 'app/queue'),
        ('../backend/app/plugins', 'app/plugins'),
        ('../backend/app/webhooks', 'app/webhooks'),
        ('../backend/app/scheduler', 'app/scheduler'),
        ('../backend/app/search', 'app/search'),
        ('../backend/app/analytics', 'app/analytics'),
        ('../backend/app/middleware', 'app/middleware'),
        ('../backend/app/core', 'app/core'),
        # Redis可执行文件
        ('../redis', 'redis'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.websockets',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'playwright',
        'playwright._impl',
        'playwright.sync_api',
        'playwright.async_api',
        'aiohttp',
        'aiohttp.web',
        'aiofiles',
        'redis',
        'redis.asyncio',
        'pydantic',
        'pydantic_settings',
        'aiosqlite',
        'apscheduler',
        'PIL',
        'PIL.Image',
        'cryptography',
        'cryptography.fernet',
        'aiosmtplib',
        'psutil',
        'orjson',
        'bcrypt',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(backend_main.pure, backend_main.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    backend_main.scripts,
    [],
    exclude_binaries=True,
    name='KOOKForwarder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../build/icon.ico',
)

coll = COLLECT(
    exe,
    backend_main.binaries,
    backend_main.zipfiles,
    backend_main.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KOOKForwarder',
)
```

3. 保存为: `C:\KOOK\CSBJJWT\build\pyinstaller.spec`
   - **注意**: 覆盖原文件
   - 文件类型选择"所有文件"
   - 确保扩展名是 `.spec` 不是 `.spec.txt`

**方法B：手动修改原文件**

1. 用记事本打开: `C:\KOOK\CSBJJWT\build\pyinstaller.spec`
2. 按 `Ctrl+F` 搜索 `name='kook-forwarder-backend'`
3. 找到第一处（约第66行），改为 `name='KOOKForwarder'`
4. 找到第二处（约第91行），改为 `name='KOOKForwarder'`
5. 保存文件

---

#### 📝 自动构建脚本：build-fixed-windows.bat

1. 打开记事本
2. 复制以下内容：

```batch
@echo off
chcp 65001 >nul
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   KOOK消息转发系统 - 自动构建脚本（修复版）               ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 正在开始构建，请稍候...
pause

:: 步骤1: 检查环境
echo [1/7] 检查环境...
python --version || (echo Python未安装 && pause && exit /b 1)
node --version || (echo Node.js未安装 && pause && exit /b 1)

:: 步骤2: 安装后端依赖
echo [2/7] 安装后端依赖...
cd backend
if not exist venv python -m venv venv
call venv\Scripts\activate
pip install -q -r requirements.txt
pip install -q pyinstaller
cd ..

:: 步骤3: 打包后端
echo [3/7] 打包后端（5-10分钟）...
cd build
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
pyinstaller pyinstaller.spec || (echo 打包失败 && pause && exit /b 1)
cd ..

:: 步骤4: 复制后端
echo [4/7] 复制后端文件...
if not exist backend\dist mkdir backend\dist
xcopy /Y /E /I build\dist\KOOKForwarder backend\dist\KOOKForwarder >nul

:: 步骤5: 安装前端依赖
echo [5/7] 安装前端依赖...
cd frontend
if not exist node_modules call npm install
cd ..

:: 步骤6: 构建前端
echo [6/7] 构建前端...
cd frontend
if exist dist rmdir /s /q dist
if exist dist-electron rmdir /s /q dist-electron
call npm run build || (echo 构建失败 && pause && exit /b 1)

:: 步骤7: 打包Electron
echo [7/7] 打包Electron（5-10分钟）...
call npm run electron:build:win || (echo 打包失败 && pause && exit /b 1)
cd ..

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   🎉 构建成功！                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 安装包位置: frontend\dist-electron\
pause
```

3. 保存为: `C:\KOOK\CSBJJWT\build-fixed-windows.bat`
   - 文件类型选择"所有文件"
   - 确保扩展名是 `.bat` 不是 `.bat.txt`

---

### 步骤3: 添加Windows Defender排除项（重要！）

**防止文件被删除**

1. 按 `Win+I` 打开设置
2. 点击"隐私和安全性"
3. 点击"Windows 安全中心"
4. 点击"病毒和威胁防护"
5. 点击"管理设置"
6. 滚动到"排除项"
7. 点击"添加或删除排除项"
8. 点击"添加排除项" → "文件夹"
9. 选择: `C:\KOOK\CSBJJWT`
10. 确认

---

## 🚀 第二部分：运行自动构建

### 步骤4: 启动构建

1. 找到文件: `C:\KOOK\CSBJJWT\build-fixed-windows.bat`
2. **右键点击**
3. 选择"**以管理员身份运行**"
4. 如果弹出UAC提示，点击"是"

### 步骤5: 等待完成

**构建过程会显示**:
```
[1/7] 检查环境...
[2/7] 安装后端依赖...（2-5分钟）
[3/7] 打包后端...（5-10分钟）
[4/7] 复制后端文件...
[5/7] 安装前端依赖...（2-5分钟）
[6/7] 构建前端...（1-2分钟）
[7/7] 打包Electron...（5-10分钟）

🎉 构建成功！
```

**总计时间**: 15-30分钟（取决于网络速度和电脑性能）

**注意事项**:
- ❌ 不要关闭窗口
- ❌ 不要按键盘
- ✅ 耐心等待
- ✅ 可以去喝杯咖啡 ☕

---

## ✅ 第三部分：验证和安装

### 步骤6: 检查输出文件

构建成功后，检查：

```cmd
dir C:\KOOK\CSBJJWT\frontend\dist-electron
```

**应该看到**:
```
KOOK消息转发系统 Setup 18.0.0.exe  (约80-90 MB)
win-unpacked/                       (文件夹)
```

### 步骤7: 验证后端文件名

**这是最关键的检查！**

```cmd
dir C:\KOOK\CSBJJWT\build\dist\KOOKForwarder
```

**应该看到**:
```
KOOKForwarder.exe  ✅ 正确！
```

**如果看到**:
```
kook-forwarder-backend.exe  ❌ 错误！说明修复未生效
```

如果是错误的，检查 `build/pyinstaller.spec` 是否正确修改。

---

### 步骤8: 安装应用

#### 方法A: 使用安装程序（推荐）

1. 双击运行:
   ```
   C:\KOOK\CSBJJWT\frontend\dist-electron\KOOK消息转发系统 Setup 18.0.0.exe
   ```

2. 如果Windows提示"Windows已保护你的电脑":
   - 点击"更多信息"
   - 点击"仍然运行"

3. 按照安装向导操作:
   - 选择安装位置（默认即可）
   - 勾选"创建桌面快捷方式"
   - 点击"安装"

4. 等待安装完成

#### 方法B: 使用便携版

1. 进入目录:
   ```
   C:\KOOK\CSBJJWT\frontend\dist-electron\win-unpacked\
   ```

2. 双击运行:
   ```
   KOOK消息转发系统.exe
   ```

---

### 步骤9: 首次启动

1. **双击桌面图标**或从开始菜单启动

2. **应该看到**:
   - ✅ 应用正常启动
   - ✅ 免责声明页面
   - ✅ 或配置向导

3. **不应该看到**:
   - ❌ "后端服务未找到"错误

4. **首次配置**:
   - 同意免责声明
   - 设置管理员密码（8-20位，包含大小写字母、数字、特殊字符）
   - 进入配置向导或主界面

---

## 🎉 第四部分：成功验证

### 验证清单

打开应用后，检查以下项目：

#### ✅ 启动检查
- [ ] 应用成功启动，没有报错
- [ ] 可以看到主界面
- [ ] 系统托盘有图标

#### ✅ 服务检查
- [ ] 后端服务自动启动（查看任务管理器应该有 KOOKForwarder.exe 进程）
- [ ] Redis服务自动启动

#### ✅ 功能检查
- [ ] 可以打开设置页面
- [ ] 可以访问账号管理
- [ ] 可以访问Bot配置
- [ ] 可以访问频道映射

---

## ⚠️ 常见问题处理

### 问题1: 构建脚本执行失败

**症状**: 脚本运行到某一步就停止了

**检查**:
```cmd
# 查看错误信息
# 通常会显示是哪个步骤失败
```

**解决方案A: Python依赖安装失败**
```cmd
cd C:\KOOK\CSBJJWT\backend
venv\Scripts\activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**解决方案B: Node.js依赖安装失败**
```cmd
cd C:\KOOK\CSBJJWT\frontend
npm install --registry=https://registry.npmmirror.com
```

**解决方案C: PyInstaller打包失败**
```cmd
cd C:\KOOK\CSBJJWT\backend
venv\Scripts\activate
pip install pyinstaller --force-reinstall
cd ..\build
rmdir /s /q dist
rmdir /s /q build
pyinstaller pyinstaller.spec
```

---

### 问题2: 后端文件名仍然错误

**症状**: 生成的是 `kook-forwarder-backend.exe` 而不是 `KOOKForwarder.exe`

**原因**: pyinstaller.spec 文件未正确修改

**解决**:
1. 重新打开 `C:\KOOK\CSBJJWT\build\pyinstaller.spec`
2. 按 `Ctrl+F` 搜索 `kook-forwarder-backend`
3. 确保两处都改为 `KOOKForwarder`
4. 保存
5. 重新运行构建脚本

---

### 问题3: 安装后仍然报错"后端服务未找到"

**验证文件是否存在**:
```cmd
dir "C:\Users\tanzu\AppData\Local\Programs\kook-forwarder-frontend\resources\backend\KOOKForwarder\KOOKForwarder.exe"
```

**如果文件不存在**:

**方案A: 重新安装**
1. 卸载当前版本
2. 删除安装目录
3. 重新运行安装程序

**方案B: 手动复制**
1. 找到打包的后端:
   ```
   C:\KOOK\CSBJJWT\backend\dist\KOOKForwarder\
   ```
2. 复制整个文件夹到:
   ```
   C:\Users\tanzu\AppData\Local\Programs\kook-forwarder-frontend\resources\backend\
   ```

---

### 问题4: 杀毒软件删除了exe文件

**症状**: 文件突然消失

**解决**:
1. 打开Windows安全中心
2. 病毒和威胁防护 → 保护历史记录
3. 查找被隔离的文件
4. 点击"还原"
5. 重新添加排除项（参见步骤3）
6. 重新运行构建

---

### 问题5: 磁盘空间不足

**症状**: 构建失败，提示空间不足

**解决**:
1. 清理C盘空间（至少需要2GB）
2. 或更改工作目录到其他盘:
   ```cmd
   mkdir D:\KOOK
   cd D:\KOOK
   # 重新开始
   ```

---

## 📊 构建进度参考

正常的构建时间参考：

| 步骤 | 时间 | 说明 |
|-----|------|------|
| 1. 检查环境 | 10秒 | 快速检查 |
| 2. 安装后端依赖 | 2-5分钟 | 下载约200MB |
| 3. 打包后端 | 5-10分钟 | CPU密集型 |
| 4. 复制后端 | 10秒 | 快速复制 |
| 5. 安装前端依赖 | 2-5分钟 | 下载约400MB |
| 6. 构建前端 | 1-2分钟 | 编译Vue |
| 7. 打包Electron | 5-10分钟 | 打包应用 |

**总计**: 15-30分钟

---

## 🎁 额外提示

### 备份安装包

构建成功后，建议备份：

```cmd
# 创建备份目录
mkdir C:\KOOK\Backup

# 复制安装包
copy "C:\KOOK\CSBJJWT\frontend\dist-electron\KOOK消息转发系统 Setup 18.0.0.exe" C:\KOOK\Backup\

# 或压缩整个dist-electron文件夹
```

### 创建便携版

如果想要免安装版本：

1. 进入: `C:\KOOK\CSBJJWT\frontend\dist-electron\win-unpacked\`
2. 复制整个文件夹到U盘或其他位置
3. 直接运行 `KOOK消息转发系统.exe`

---

## ✅ 完成！

如果您已经完成所有步骤，并且应用正常启动，**恭喜您成功了！** 🎉

现在您可以：
1. 添加KOOK账号
2. 配置Discord/Telegram/飞书Bot
3. 设置频道映射
4. 启动消息转发服务
5. 开始使用完整功能

---

## 📞 需要帮助？

如果遇到任何问题，请提供：
1. 在哪一步失败
2. 完整的错误信息（截图）
3. 相关的日志文件

我会继续帮助您解决！
