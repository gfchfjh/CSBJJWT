# Windows 11 安装失败修复指南

## 问题描述
错误信息：
```
启动失败
后端服务未找到。
路径: C:\Users\tanzu\AppData\Local\Programs\kook-forwarder-front...\KOOKForwarder.exe
请重新安装应用程序。
```

## 原因分析
Electron应用期望的后端文件名与实际打包的文件名不匹配。

---

## 解决方案1: 手动修复（临时方案）⚠️

### 步骤1: 找到安装目录

打开文件资源管理器，导航到：
```
C:\Users\tanzu\AppData\Local\Programs\kook-forwarder-frontend
```

或完整路径（根据错误信息）：
```
C:\Users\tanzu\AppData\Local\Programs\kook-forwarder-front[完整路径]
```

### 步骤2: 检查目录结构

查看是否存在以下文件：

**期望的结构**:
```
C:\Users\tanzu\AppData\Local\Programs\kook-forwarder-frontend\
├── resources\
│   ├── backend\
│   │   ├── KOOKForwarder\
│   │   │   └── KOOKForwarder.exe  ← 应该在这里
│   │   └── kook-forwarder-backend\
│   │       └── kook-forwarder-backend.exe  ← 实际可能在这里
│   ├── redis\
│   └── app\
└── KOOK消息转发系统.exe
```

### 步骤3: 查找后端文件

在安装目录中搜索以下文件：
- `kook-forwarder-backend.exe`
- `KOOKForwarder.exe`
- 任何带"backend"或"KOOK"的.exe文件

### 步骤4: 手动创建正确的目录结构

**如果找到了 `kook-forwarder-backend.exe`：**

1. 在 `resources\backend\` 目录下创建文件夹：
   ```
   新建文件夹: KOOKForwarder
   ```

2. 复制或移动文件：
   ```
   从: resources\backend\kook-forwarder-backend\kook-forwarder-backend.exe
   到: resources\backend\KOOKForwarder\KOOKForwarder.exe
   ```

3. 同时复制整个目录内容：
   ```
   复制 kook-forwarder-backend 文件夹中的所有文件
   到 KOOKForwarder 文件夹
   ```

### 步骤5: 验证文件存在

确认以下文件存在：
```
resources\backend\KOOKForwarder\KOOKForwarder.exe
```

### 步骤6: 重新启动应用

双击桌面图标或开始菜单中的"KOOK消息转发系统"

---

## 解决方案2: 使用修复工具（推荐）✅

### 创建自动修复脚本

1. **打开记事本**，粘贴以下内容：

```batch
@echo off
echo ========================================
echo KOOK消息转发系统 - 自动修复工具
echo ========================================
echo.

:: 设置变量
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\kook-forwarder-frontend"
set "RESOURCES=%INSTALL_DIR%\resources"
set "BACKEND=%RESOURCES%\backend"

echo 正在检测安装目录...
if not exist "%INSTALL_DIR%" (
    echo [错误] 未找到安装目录: %INSTALL_DIR%
    echo.
    echo 请手动指定安装目录路径：
    set /p "INSTALL_DIR=输入路径: "
)

echo.
echo 安装目录: %INSTALL_DIR%
echo.

echo 正在搜索后端文件...
echo.

:: 查找可能的后端exe文件
set "FOUND_BACKEND="
for /r "%BACKEND%" %%f in (*.exe) do (
    echo 找到: %%f
    if /i "%%~nxf"=="kook-forwarder-backend.exe" set "FOUND_BACKEND=%%f"
    if /i "%%~nxf"=="KOOKForwarder.exe" set "FOUND_BACKEND=%%f"
)

if "%FOUND_BACKEND%"=="" (
    echo.
    echo [错误] 未找到后端可执行文件！
    echo.
    echo 可能的原因：
    echo 1. 安装包不完整
    echo 2. 被杀毒软件删除
    echo 3. 文件损坏
    echo.
    echo 建议：重新下载完整安装包
    echo 下载地址: https://github.com/gfchfjh/CSBJJWT/releases
    echo.
    pause
    exit /b 1
)

echo.
echo 找到后端文件: %FOUND_BACKEND%
echo.

:: 创建正确的目录结构
echo 正在创建目录结构...
set "TARGET_DIR=%BACKEND%\KOOKForwarder"
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo 正在复制文件...
:: 获取源目录
for %%f in ("%FOUND_BACKEND%") do set "SOURCE_DIR=%%~dpf"

:: 复制所有文件
xcopy /Y /E /I "%SOURCE_DIR%*" "%TARGET_DIR%\"

:: 重命名exe文件
if exist "%TARGET_DIR%\kook-forwarder-backend.exe" (
    copy /Y "%TARGET_DIR%\kook-forwarder-backend.exe" "%TARGET_DIR%\KOOKForwarder.exe"
)

echo.
echo ========================================
echo 修复完成！
echo ========================================
echo.
echo 目标文件: %TARGET_DIR%\KOOKForwarder.exe
echo.

if exist "%TARGET_DIR%\KOOKForwarder.exe" (
    echo [成功] 后端文件已就位
    echo.
    echo 现在可以启动应用程序了！
) else (
    echo [失败] 修复未成功，请尝试重新安装
)

echo.
pause
```

2. **保存为**: `fix_kook.bat`
   - 文件类型选择"所有文件"
   - 文件名输入: `fix_kook.bat`

3. **右键点击** `fix_kook.bat`，选择"以管理员身份运行"

4. 按照提示操作

---

## 解决方案3: 从源码安装（最可靠）🔧

### 前提条件

确保已安装：
- Python 3.11+
- Node.js 18+
- Git

### 步骤1: 克隆代码

打开PowerShell或命令提示符：

```powershell
# 克隆仓库
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT
```

### 步骤2: 安装后端

```powershell
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium

# 返回根目录
cd ..
```

### 步骤3: 安装前端

```powershell
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建前端
npm run build

# 返回根目录
cd ..
```

### 步骤4: 启动应用

**双击运行**: `start.bat`

或手动启动：

```powershell
# 终端1: 启动后端
cd backend
venv\Scripts\activate
python -m app.main

# 终端2: 启动前端
cd frontend
npm run electron
```

---

## 解决方案4: 检查杀毒软件（常见原因）🛡️

### Windows Defender可能删除了后端文件

#### 步骤1: 检查隔离区

1. 打开"Windows 安全中心"
2. 点击"病毒和威胁防护"
3. 点击"保护历史记录"
4. 查找最近被隔离的文件
5. 如果找到"KOOKForwarder.exe"或"kook-forwarder-backend.exe"，点击"还原"

#### 步骤2: 添加排除项

1. 打开"Windows 安全中心"
2. 病毒和威胁防护 → 管理设置
3. 滚动到"排除项"
4. 点击"添加或删除排除项"
5. 添加以下路径：
   ```
   C:\Users\tanzu\AppData\Local\Programs\kook-forwarder-frontend
   ```

#### 步骤3: 重新安装

添加排除项后，重新安装应用。

---

## 解决方案5: 验证下载完整性（推荐）📥

### 问题可能是下载不完整

#### 步骤1: 检查下载的文件大小

**正确的文件大小**（参考值）:
- Windows安装包应该是 **100-120 MB**
- 如果只有几MB，说明下载不完整

#### 步骤2: 重新下载

1. 访问: https://github.com/gfchfjh/CSBJJWT/releases/tag/v18.0.0
2. 找到 `KOOK-Forwarder-v18.0.0-Windows.zip` (112 MB)
3. 使用下载工具（如IDM）确保完整下载
4. 检查文件大小是否约112 MB
5. 解压后验证文件完整性

#### 步骤3: 验证解压结果

解压后应该包含：
```
KOOK-Forwarder-v18.0.0-Windows\
├── frontend\
│   ├── KOOK消息转发系统 Setup 18.0.0.exe  (安装程序)
│   └── win-unpacked\  (便携版)
└── backend\
    └── kook-forwarder-backend\
        └── kook-forwarder-backend.exe
```

---

## 快速诊断命令

在PowerShell中运行以下命令进行诊断：

```powershell
# 检查安装目录
Get-ChildItem "$env:LOCALAPPDATA\Programs\kook-forwarder-frontend" -Recurse -Filter "*.exe" | Select-Object FullName

# 检查进程
Get-Process | Where-Object {$_.ProcessName -like "*kook*" -or $_.ProcessName -like "*KOOK*"}

# 检查端口占用
netstat -ano | findstr :9527

# 检查防火墙
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*KOOK*"}
```

---

## 终极方案：使用便携版

如果安装版本一直有问题，尝试使用**便携版**：

### 步骤1: 解压便携版

从下载的ZIP文件中，找到：
```
KOOK-Forwarder-v18.0.0-Windows\frontend\win-unpacked\
```

### 步骤2: 复制到合适位置

将整个 `win-unpacked` 文件夹复制到：
```
C:\Program Files\KOOK消息转发系统\
```

### 步骤3: 直接运行

双击 `KOOK消息转发系统.exe`（无需安装）

---

## 获取帮助

如果以上方法都无效，请提供以下信息：

### 收集诊断信息

1. **运行诊断脚本**（新建文本文件，改名为 `diagnose.bat`）：

```batch
@echo off
echo KOOK消息转发系统 - 诊断信息
echo ========================================
echo.

echo 1. 系统信息
systeminfo | findstr /C:"OS Name" /C:"OS Version"
echo.

echo 2. 安装目录内容
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\kook-forwarder-frontend"
if exist "%INSTALL_DIR%" (
    echo 目录: %INSTALL_DIR%
    dir /S /B "%INSTALL_DIR%\*.exe"
) else (
    echo 未找到安装目录
)
echo.

echo 3. 运行进程
tasklist | findstr /I "kook python electron"
echo.

echo 4. 端口占用
netstat -ano | findstr :9527
echo.

echo 5. 最近的错误日志
if exist "%APPDATA%\KOOK消息转发系统\logs" (
    dir "%APPDATA%\KOOK消息转发系统\logs"
)
echo.

pause
```

2. **运行诊断脚本**并截图输出结果

3. **提交Issue**到GitHub，附上：
   - 诊断信息截图
   - 完整的错误信息
   - Windows版本
   - 使用的安装包来源

---

## 推荐的最佳安装流程

为了避免类似问题，推荐以下流程：

### 方案A: 使用便携版（最简单）✅

1. 下载ZIP包
2. 解压到 `C:\KOOK\`
3. 添加Windows Defender排除项
4. 运行 `win-unpacked\KOOK消息转发系统.exe`

### 方案B: 从源码安装（最可靠）✅

1. 安装Python 3.11+和Node.js 18+
2. 克隆代码
3. 运行 `install.bat`
4. 运行 `start.bat`

### 方案C: 等待修复版本（最简单）⏳

如果当前版本有bug，可以：
1. Star项目关注更新
2. 在Issue中反馈问题
3. 等待开发者发布修复版本

---

**祝您安装顺利！**
