# KOOK 系统完全卸载指南

**版本**: 1.0  
**适用系统**: Windows 10/11  
**更新日期**: 2025-11-03  

---

## 📋 目录

- [快速清理（推荐）](#快速清理推荐)
- [手动完全清理](#手动完全清理)
- [清理验证](#清理验证)
- [常见问题](#常见问题)

---

## 🚀 快速清理（推荐）

### 使用自动清理脚本

1. **下载清理脚本**: `KOOK_完全卸载.bat`（见下方）
2. **右键以管理员身份运行**
3. **按提示操作**

**预计时间**: 2-5 分钟

---

## 🛠️ 手动完全清理

### 步骤 1: 卸载 Electron 应用

#### 方法 1: 通过 Windows 设置（推荐）

```bash
# 1. 打开 Windows 设置
Win + I

# 2. 进入"应用" → "应用和功能"

# 3. 搜索 "KOOK" 或 "KOOK消息转发系统"

# 4. 点击应用 → 点击"卸载"

# 5. 确认卸载
```

#### 方法 2: 通过控制面板

```bash
# 1. 打开控制面板
Win + R → 输入 control → 回车

# 2. 程序 → 程序和功能

# 3. 找到 "KOOK消息转发系统"

# 4. 右键 → 卸载
```

#### 方法 3: 手动删除（如果以上方法失败）

```bash
# 查找安装位置（通常是以下之一）
C:\Program Files\KOOK消息转发系统\
C:\Program Files (x86)\KOOK消息转发系统\
%LOCALAPPDATA%\Programs\KOOK消息转发系统\

# 删除整个文件夹
```

---

### 步骤 2: 删除用户数据和配置

#### 应用数据目录

```bash
# 1. 打开资源管理器
Win + E

# 2. 在地址栏输入以下路径并删除：

# 用户数据
%APPDATA%\KOOK消息转发系统\
%APPDATA%\kook-forwarder\

# 本地数据
%LOCALAPPDATA%\KOOK消息转发系统\
%LOCALAPPDATA%\kook-forwarder\
%LOCALAPPDATA%\Programs\KOOK消息转发系统\

# 临时文件
%TEMP%\KOOK*
%TEMP%\kook*
```

#### 具体包含的文件

- **配置文件**: `config.json`, `settings.json`
- **日志文件**: `logs/` 文件夹
- **数据库文件**: `*.db`, `*.sqlite`
- **缓存文件**: `cache/` 文件夹
- **Cookie 文件**: `cookies.json`

---

### 步骤 3: 删除开发/构建文件

#### 项目源码目录

```bash
# 如果你有克隆或下载的源码，删除整个目录

# 常见位置：
C:\Users\你的用户名\Desktop\CSBJJWT\
C:\Users\你的用户名\KOOK-Build\CSBJJWT\
C:\Users\你的用户名\Documents\CSBJJWT\

# 构建目录（如果使用了一键安装脚本）
C:\Users\你的用户名\KOOK-Build\

# 删除整个文件夹
```

#### 虚拟环境

```bash
# 如果创建了 Python 虚拟环境
C:\Users\你的用户名\KOOK-Build\CSBJJWT\backend\venv\

# 删除 venv 文件夹
```

---

### 步骤 4: 删除桌面和开始菜单快捷方式

```bash
# 桌面快捷方式
%USERPROFILE%\Desktop\KOOK消息转发系统.lnk

# 开始菜单
%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统\

# 手动删除这些快捷方式
```

---

### 步骤 5: 清理注册表（高级，可选）

> ⚠️ **警告**: 修改注册表有风险，建议先备份！

#### 自动清理（推荐）

使用清理脚本会自动处理。

#### 手动清理

1. **打开注册表编辑器**:
   ```bash
   Win + R → 输入 regedit → 回车
   ```

2. **导出备份**（强烈推荐）:
   ```
   文件 → 导出 → 保存为 registry_backup.reg
   ```

3. **搜索并删除以下键**:
   ```
   HKEY_CURRENT_USER\Software\KOOK消息转发系统
   HKEY_CURRENT_USER\Software\kook-forwarder
   HKEY_LOCAL_MACHINE\SOFTWARE\KOOK消息转发系统
   HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\KOOK消息转发系统
   ```

4. **搜索卸载信息**:
   ```
   HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\
   # 查找包含 "KOOK" 的项并删除
   ```

---

### 步骤 6: 删除 Chrome 扩展

如果安装了 KOOK Cookie 导出扩展：

```bash
# 1. 打开 Chrome
# 2. 进入扩展管理页面
chrome://extensions/

# 3. 找到 "KOOK Cookie Export" 或类似名称

# 4. 点击"移除"

# 5. 确认删除
```

---

### 步骤 7: 清理 Redis（如果安装了）

```bash
# 如果单独安装了 Redis for Windows

# 1. 停止 Redis 服务
net stop Redis

# 2. 卸载 Redis（通过控制面板）
# 或者手动删除 Redis 安装目录

# 常见位置：
C:\Redis\
C:\Program Files\Redis\
```

---

### 步骤 8: 清理 Python 依赖（可选）

如果想清理安装的 Python 包：

```bash
# 如果使用了虚拟环境，直接删除 venv 文件夹即可

# 如果是全局安装的包，可以卸载：
pip uninstall fastapi uvicorn playwright aiohttp redis pydantic sqlalchemy apscheduler pillow cryptography aiosmtplib psutil loguru

# 清理 pip 缓存
pip cache purge
```

---

### 步骤 9: 清理 Node.js 依赖（可选）

如果想清理 Node.js 相关文件：

```bash
# 进入前端目录（如果还存在）
cd C:\Users\你的用户名\KOOK-Build\CSBJJWT\frontend

# 删除 node_modules
rmdir /s /q node_modules

# 清理 npm 缓存
npm cache clean --force

# 清理 Electron 缓存
%LOCALAPPDATA%\electron\
%LOCALAPPDATA%\electron-builder\
```

---

### 步骤 10: 清理临时文件和缓存

```bash
# 1. 运行磁盘清理
cleanmgr

# 2. 勾选"临时文件"、"下载文件夹"等

# 3. 点击"确定"清理

# 或手动清理：
%TEMP%\*
C:\Windows\Temp\*
```

---

## ✅ 清理验证

### 验证清单

运行以下命令检查是否清理干净：

```bash
# 1. 检查程序是否卸载
wmic product where "name like '%KOOK%'" get name, version

# 2. 检查应用数据
dir %APPDATA%\KOOK* /s
dir %LOCALAPPDATA%\KOOK* /s

# 3. 检查桌面快捷方式
dir %USERPROFILE%\Desktop\*KOOK*.lnk

# 4. 检查开始菜单
dir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\*KOOK*" /s

# 如果没有输出或提示"找不到文件"，说明已清理干净
```

---

## 🔧 清理脚本

### 自动清理脚本

保存为 `KOOK_完全卸载.bat`:

```batch
@echo off
chcp 65001 >nul
title KOOK 系统完全卸载工具

echo ========================================
echo KOOK 消息转发系统 - 完全卸载工具
echo ========================================
echo.
echo 本工具将删除以下内容：
echo   1. 已安装的 Electron 应用
echo   2. 用户数据和配置文件
echo   3. 项目源码和构建文件
echo   4. 桌面和开始菜单快捷方式
echo   5. 临时文件和缓存
echo.
echo ⚠️  警告：此操作不可逆！
echo.
set /p CONFIRM="确定要继续吗？(输入 YES 继续): "

if /i not "%CONFIRM%"=="YES" (
    echo 已取消卸载。
    pause
    exit /b
)

echo.
echo ========================================
echo 开始卸载...
echo ========================================
echo.

:: 步骤 1: 卸载应用（通过 wmic）
echo [1/8] 卸载 Electron 应用...
wmic product where "name like '%%KOOK%%'" call uninstall /nointeractive 2>nul
if %errorlevel%==0 (
    echo [OK] 应用已卸载
) else (
    echo [INFO] 未找到已安装的应用或已卸载
)
echo.

:: 步骤 2: 删除用户数据
echo [2/8] 删除用户数据...
if exist "%APPDATA%\KOOK消息转发系统" (
    rmdir /s /q "%APPDATA%\KOOK消息转发系统"
    echo [OK] 已删除 %APPDATA%\KOOK消息转发系统
)
if exist "%APPDATA%\kook-forwarder" (
    rmdir /s /q "%APPDATA%\kook-forwarder"
    echo [OK] 已删除 %APPDATA%\kook-forwarder
)
if exist "%LOCALAPPDATA%\KOOK消息转发系统" (
    rmdir /s /q "%LOCALAPPDATA%\KOOK消息转发系统"
    echo [OK] 已删除 %LOCALAPPDATA%\KOOK消息转发系统
)
if exist "%LOCALAPPDATA%\kook-forwarder" (
    rmdir /s /q "%LOCALAPPDATA%\kook-forwarder"
    echo [OK] 已删除 %LOCALAPPDATA%\kook-forwarder
)
if exist "%LOCALAPPDATA%\Programs\KOOK消息转发系统" (
    rmdir /s /q "%LOCALAPPDATA%\Programs\KOOK消息转发系统"
    echo [OK] 已删除安装目录
)
echo.

:: 步骤 3: 删除构建目录
echo [3/8] 删除构建目录...
if exist "%USERPROFILE%\KOOK-Build" (
    rmdir /s /q "%USERPROFILE%\KOOK-Build"
    echo [OK] 已删除 %USERPROFILE%\KOOK-Build
)
if exist "%USERPROFILE%\Desktop\CSBJJWT" (
    rmdir /s /q "%USERPROFILE%\Desktop\CSBJJWT"
    echo [OK] 已删除桌面上的 CSBJJWT
)
echo.

:: 步骤 4: 删除快捷方式
echo [4/8] 删除快捷方式...
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" (
    del "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk"
    echo [OK] 已删除桌面快捷方式
)
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统" (
    rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\KOOK消息转发系统"
    echo [OK] 已删除开始菜单项
)
echo.

:: 步骤 5: 清理临时文件
echo [5/8] 清理临时文件...
del /f /s /q "%TEMP%\KOOK*" 2>nul
del /f /s /q "%TEMP%\kook*" 2>nul
echo [OK] 临时文件已清理
echo.

:: 步骤 6: 清理缓存
echo [6/8] 清理缓存...
if exist "%LOCALAPPDATA%\electron" (
    rmdir /s /q "%LOCALAPPDATA%\electron"
    echo [OK] 已删除 Electron 缓存
)
if exist "%LOCALAPPDATA%\electron-builder" (
    rmdir /s /q "%LOCALAPPDATA%\electron-builder"
    echo [OK] 已删除 Electron Builder 缓存
)
echo.

:: 步骤 7: 清理注册表（需要管理员权限）
echo [7/8] 清理注册表...
reg delete "HKCU\Software\KOOK消息转发系统" /f 2>nul
reg delete "HKCU\Software\kook-forwarder" /f 2>nul
echo [OK] 注册表项已清理（如果存在）
echo.

:: 步骤 8: 验证清理
echo [8/8] 验证清理结果...
set CLEAN=1

if exist "%APPDATA%\KOOK消息转发系统" set CLEAN=0
if exist "%LOCALAPPDATA%\KOOK消息转发系统" set CLEAN=0
if exist "%USERPROFILE%\Desktop\KOOK消息转发系统.lnk" set CLEAN=0

if %CLEAN%==1 (
    echo [OK] ✅ 清理完成！
    echo.
    echo 所有 KOOK 系统相关文件已删除。
) else (
    echo [WARNING] ⚠️  部分文件可能未完全删除
    echo 请手动检查以下位置：
    echo   - %APPDATA%
    echo   - %LOCALAPPDATA%
    echo   - 桌面快捷方式
)

echo.
echo ========================================
echo 卸载完成
echo ========================================
echo.
echo 如果需要重新安装，请从 GitHub 下载最新版本。
echo GitHub: https://github.com/gfchfjh/CSBJJWT
echo.
pause
```

---

## ❓ 常见问题

### Q1: 卸载后可以重新安装吗？

**答**: 可以。完全卸载后，可以随时从 GitHub 重新下载安装。

---

### Q2: 会删除 Python 和 Node.js 吗？

**答**: 不会。清理脚本只删除 KOOK 系统相关文件，不会删除 Python、Node.js 等开发工具。

---

### Q3: 会影响其他程序吗？

**答**: 不会。清理范围严格限定在 KOOK 系统相关文件，不会影响其他程序。

---

### Q4: 卸载后如何恢复数据？

**答**: 
- 如果在清理前做了备份，可以恢复
- 如果没有备份，数据无法恢复
- 建议清理前备份以下文件：
  - `%APPDATA%\KOOK消息转发系统\config.json`
  - `%APPDATA%\KOOK消息转发系统\cookies.json`
  - `%APPDATA%\KOOK消息转发系统\*.db`

---

### Q5: 清理脚本运行失败怎么办？

**答**: 
1. 确保以管理员身份运行
2. 如果仍然失败，按照"手动完全清理"步骤操作
3. 部分文件可能被占用，重启后再试

---

### Q6: 如何只保留配置，删除程序？

**答**: 
1. 只执行"步骤 1"卸载应用
2. 备份 `%APPDATA%\KOOK消息转发系统\config.json`
3. 重新安装后恢复配置文件

---

### Q7: 删除后还能在任务管理器看到进程？

**答**: 
1. 打开任务管理器 (Ctrl + Shift + Esc)
2. 找到 KOOK 相关进程
3. 右键 → 结束任务
4. 如果无法结束，重启电脑

---

### Q8: 如何确认已完全删除？

**答**: 运行验证命令（见"清理验证"章节），如果所有命令都返回"找不到文件"，说明已清理干净。

---

## 📊 清理内容总结

### 会删除的内容

| 类别 | 位置 | 大小估算 |
|-----|------|---------|
| 已安装应用 | `Program Files/` | ~100 MB |
| 用户数据 | `%APPDATA%/` | ~10 MB |
| 缓存文件 | `%LOCALAPPDATA%/` | ~50 MB |
| 源码文件 | `KOOK-Build/` | ~500 MB |
| 虚拟环境 | `backend/venv/` | ~1 GB |
| 快捷方式 | 桌面/开始菜单 | ~1 KB |
| **总计** | - | **~1.7 GB** |

### 不会删除的内容

- ✅ Python 环境
- ✅ Node.js 环境
- ✅ Git 工具
- ✅ Chrome 浏览器
- ✅ 其他程序的数据

---

## 🔄 重新安装

完全卸载后，如需重新安装：

1. **访问 GitHub**:
   ```
   https://github.com/gfchfjh/CSBJJWT
   ```

2. **下载最新版本**:
   - Release 页面下载安装包
   - 或克隆源码构建

3. **按照安装指南操作**:
   - [QUICK_START_WINDOWS.md](./QUICK_START_WINDOWS.md)

---

## 📞 需要帮助？

如遇到问题：

1. 查看 [TROUBLESHOOTING_WINDOWS.md](./TROUBLESHOOTING_WINDOWS.md)
2. 提交 GitHub Issue
3. 查看项目文档

---

**文档版本**: 1.0  
**最后更新**: 2025-11-03  
**维护者**: KOOK Development Team

---

**祝您使用愉快！如有疑问，欢迎反馈。** 😊
