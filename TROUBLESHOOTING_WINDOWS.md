# Windows 故障排查指南

**版本**: 2.1  
**适用系统**: Windows 10/11  
**更新日期**: 2025-11-06  
**适用版本**: v18.0.4+  

---

## 📋 目录

- [环境问题](#环境问题)
- [构建问题](#构建问题)
- [启动问题](#启动问题)
- [运行时问题](#运行时问题)
  - [浏览器启动问题](#浏览器启动问题)
  - [Cookie处理问题](#cookie处理问题)
- [常见错误代码](#常见错误代码)
- [日志收集](#日志收集)

---

## 🔍 环境问题

### 问题1: Python 未安装

**现象**:
```bash
'python' 不是内部或外部命令
```

**检查方法**:
```bash
python --version
```

**解决方案**:
1. 下载 Python 3.11+ 安装包: https://www.python.org/downloads/
2. 运行安装包
3. ⚠️ **勾选** "Add Python to PATH"
4. 点击 "Install Now"
5. 重新打开命令行，验证：`python --version`

**注意事项**:
- 必须 Python 3.11 或更高版本
- 必须添加到 PATH
- 推荐使用官方安装包

---

### 问题2: Node.js 未安装

**现象**:
```bash
'node' 不是内部或外部命令
'npm' 不是内部或外部命令
```

**检查方法**:
```bash
node --version
npm --version
```

**解决方案**:
1. 下载 Node.js LTS 版本: https://nodejs.org/
2. 运行安装包（默认会自动添加到 PATH）
3. 重启命令行
4. 验证：
   ```bash
   node --version  # 应显示 v18.x.x 或更高
   npm --version   # 应显示 10.x.x 或更高
   ```

**注意事项**:
- 必须 Node.js 18 或更高版本
- 自动安装 npm
- 重启命令行后生效

---

### 问题3: Git 未安装

**现象**:
```bash
'git' 不是内部或外部命令
```

**检查方法**:
```bash
git --version
```

**解决方案**:
1. 下载 Git: https://git-scm.com/download/win
2. 运行安装包（默认选项即可）
3. 重启命令行
4. 验证：`git --version`

---

### 问题4: 权限不足

**现象**:
```bash
Access is denied
Permission denied
```

**解决方案**:

**方法1: 以管理员身份运行**
1. 右键点击命令行图标
2. 选择"以管理员身份运行"
3. 重新执行命令

**方法2: 使用用户目录**
```bash
# 不要在 C:\Program Files 等系统目录下构建
# 使用用户目录
cd C:\Users\你的用户名\Desktop
```

**方法3: 关闭杀毒软件**
- 临时禁用 Windows Defender 实时保护
- 关闭第三方杀毒软件

---

## 🛠️ 构建问题

### 问题1: npm install 依赖冲突

**完整错误**:
```bash
npm error code ERESOLVE
npm error ERESOLVE could not resolve
npm error While resolving: vue-echarts@6.x.x
```

**解决方案**:
```bash
cd frontend
npm install --legacy-peer-deps
```

**说明**: 
- `--legacy-peer-deps` 忽略 peer 依赖冲突
- Vue 3 生态系统的已知问题
- 不影响功能正常使用

---

### 问题2: PyInstaller 打包失败

**错误类型1: ModuleNotFoundError**
```bash
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**:
```bash
# 确保在虚拟环境中
cd backend
call venv\Scripts\activate.bat

# 安装缺失的模块
pip install xxx

# 重新打包
cd ..
pyinstaller build\pyinstaller.spec --clean --noconfirm
```

**错误类型2: 导入错误**
```bash
ImportError: attempted relative import with no known parent package
```

**解决方案**:
- 检查是否使用了 `backend/run.py` 作为入口点
- 确认 `pyinstaller.spec` 中的启动脚本设置正确：
  ```python
  ['../backend/run.py'],  # 而不是 ['../backend/app/main.py']
  ```

**错误类型3: 语法错误**
```bash
SyntaxError: 'await' outside async function
```

**解决方案**:
- 参考 [WINDOWS_PACKAGING_FIXES.md](./WINDOWS_PACKAGING_FIXES.md) 中的代码修复
- 确保所有使用 `await` 的函数都是 `async def`

---

### 问题3: Electron 打包失败

**错误类型1: 后端未找到**
```bash
后端服务未找到。路径: ...
```

**检查清单**:
```bash
# 1. 确认后端已构建
dir dist\KOOKForwarder\KOOKForwarder.exe

# 2. 检查 package.json 配置
# 确认 extraResources 包含:
# {
#   "from": "../dist/KOOKForwarder",
#   "to": "backend/KOOKForwarder",
#   "filter": ["**/*"]
# }

# 3. 清理后重建
cd frontend
rmdir /s /q dist-electron
rmdir /s /q node_modules\.vite
npm run electron:build:win
```

**错误类型2: 打包超时**
```bash
Timeout waiting for build
```

**解决方案**:
```bash
# 1. 清理缓存
cd frontend
rmdir /s /q node_modules\.cache
rmdir /s /q dist

# 2. 重新安装依赖
npm install --legacy-peer-deps

# 3. 重新打包
npm run electron:build:win
```

---

## 🚀 启动问题

### 问题1: 一键安装脚本闪退

**现象**: 双击 `.bat` 文件后窗口一闪而过

**解决方案**:

**方法1: 在命令行中运行**
```bash
# 1. 打开命令行 (cmd)
# 2. 进入脚本目录
cd C:\Users\你的用户名\Desktop
# 3. 直接运行
KOOK_Installer_Safe.bat
```

**方法2: 使用安全模式脚本**
- 使用 `KOOK_Installer_Safe.bat` 而不是 `KOOK一键安装.bat`
- 安全模式版本在每步都有暂停，不会闪退

**方法3: 添加 pause**
```batch
@echo off
你的命令
pause
```

---

### 问题2: Electron 应用启动报 "fetch failed"

**现象**: 
```
无法启动应用:fetch failed
```

**诊断步骤**:

**步骤1: 测试后端是否正常**
```bash
# 进入后端目录
cd C:\Users\你的用户名\KOOK-Build\CSBJJWT\dist\KOOKForwarder

# 运行后端
KOOKForwarder.exe

# 正常情况应该看到：
# INFO: Started server process [xxxxx]
# INFO: Application startup complete.
# INFO: Uvicorn running on http://127.0.0.1:8000
```

**步骤2: 测试端口是否被占用**
```bash
netstat -ano | findstr :8000

# 如果有输出，说明 8000 端口被占用
# 找到进程 PID（最后一列数字）
# 结束进程：
taskkill /F /PID <PID号>
```

**步骤3: 检查防火墙**
```bash
# 1. 打开 Windows Defender 防火墙
# 2. 点击"允许应用通过防火墙"
# 3. 点击"更改设置"
# 4. 点击"允许另一个应用"
# 5. 浏览并选择 KOOKForwarder.exe
# 6. 勾选"专用网络"和"公用网络"
# 7. 点击"添加"
```

**步骤4: 查看详细日志**
```bash
# 1. 找到 Electron 应用的日志文件
# 位置通常在: %APPDATA%\KOOK消息转发系统\logs

# 2. 打开最新的日志文件
notepad %APPDATA%\KOOK消息转发系统\logs\main.log

# 3. 查找 ERROR 或 FATAL 关键词
```

---

### 问题3: 后端启动后立即退出

**现象**: 
```bash
KOOKForwarder.exe
# 窗口闪一下就关闭了
```

**诊断方法**:
```bash
# 在命令行中运行，查看错误信息
cd dist\KOOKForwarder
KOOKForwarder.exe

# 或者重定向到日志文件
KOOKForwarder.exe > output.log 2>&1
```

**常见原因**:

**原因1: 端口被占用**
```bash
# 查找占用 8000 端口的进程
netstat -ano | findstr :8000
# 结束该进程
taskkill /F /PID <PID>
```

**原因2: 缺少 DLL 文件**
- 安装 Visual C++ Redistributable
- 下载: https://aka.ms/vs/17/release/vc_redist.x64.exe

**原因3: Python 运行时错误**
- 查看是否有 ModuleNotFoundError
- 参考 [WINDOWS_PACKAGING_FIXES.md](./WINDOWS_PACKAGING_FIXES.md)

---

## ⚠️ 运行时问题

### 🌐 浏览器启动问题

#### 问题: Chrome/Edge浏览器启动失败

**现象**:
```
[Scraper-2] 正在启动...
[Scraper-2] Cookie已加载
[Scraper-2] 正在访问KOOK...
# 然后没有任何反应，浏览器没有弹出
```

**常见原因及解决方案**:

**原因1: Cookie sameSite字段不兼容** (v18.0.4已修复)
```
错误信息：Cookie has "sameSite" set to "no_restriction"
```

**解决方案**:
- ✅ 已在v18.0.4自动修复
- 系统会自动将 `no_restriction`/`unspecified` 转换为 `None`
- 如果使用旧版本，请更新到v18.0.4+

**原因2: 页面加载超时**
```
错误信息：Page.goto: Timeout 30000ms exceeded
```

**解决方案**:
- ✅ 已在v18.0.4自动修复（60秒超时）
- 如果仍然超时，检查网络连接
- 尝试访问 https://www.kookapp.cn 确认可访问

**原因3: Playwright未正确安装**
```
错误信息：executable doesn't exist at C:\Users\...\chromium-...\chrome.exe
```

**解决方案**:
```powershell
# 重新安装Playwright浏览器
cd backend
python -m playwright install chromium

# 如果失败，手动安装
python -m playwright install --force chromium
```

**原因4: Python 3.13 Windows兼容性问题**
```
错误信息：NotImplementedError: Cannot add child handler, you need to use WindowsProactorEventLoopPolicy
```

**解决方案**:
- ✅ 已在v18.0.4自动修复
- 系统会自动设置 `WindowsSelectorEventLoopPolicy`

**诊断步骤**:
```powershell
# 1. 检查后端日志
# 查看是否有错误信息

# 2. 手动测试Playwright
cd backend
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(headless=False); print('成功！'); browser.close(); p.stop()"

# 3. 检查Chrome进程
tasklist | findstr chrome

# 4. 强制停止所有Chrome进程
taskkill /F /IM chrome.exe /T
```

---

### 🍪 Cookie处理问题

#### 问题1: Cookie已过期，需要重新登录

**现象**:
- 浏览器成功启动并弹出
- 显示KOOK登录页面（二维码或手机扫码）
- 无法自动登录

**原因**:
- Cookie有效期已过
- KOOK账号在其他地方登录（顶号）
- Cookie格式不正确

**解决方案**:

**方法1: 扫码重新登录**
```
1. 在弹出的Chrome浏览器中扫码登录
2. 登录成功后，Cookie会自动保存
3. 停止并重新启动账号
4. 应该能自动登录了
```

**方法2: 手动导出Cookie**
```
1. 在浏览器中按F12打开开发者工具
2. 点击"Console"（控制台）标签
3. 粘贴以下代码并按回车：

copy(JSON.stringify(document.cookie.split("; ").map(c => {
  let [name, ...v] = c.split("=");
  return {name, value: v.join("="), domain: ".kookapp.cn", path: "/", secure: true, sameSite: "None"};
})))

4. Cookie已复制到剪贴板
5. 通过前端界面的"更新Cookie"功能粘贴保存
```

**方法3: 使用Chrome扩展**
```
1. 安装"EditThisCookie"扩展
2. 在KOOK页面点击扩展图标
3. 点击"导出"(Export)
4. 复制JSON
5. 通过前端界面保存
```

#### 问题2: Cookie更新失败

**现象**:
```
❌ Cookie保存失败
❌ API返回405错误
```

**解决方案**:
```
方法1: 检查API端点
- 确认使用的API地址正确
- v18.0.4+使用: GET /api/accounts/{id}

方法2: 通过后端日志确认
- 查看后端日志中的Cookie相关信息
- 确认Cookie格式正确（JSON数组）

方法3: 重启后端
- 停止后端（Ctrl+C）
- 重新启动：python -m uvicorn app.main:app --host 0.0.0.0 --port 9527 --reload
```

#### 问题3: Cookie格式错误

**现象**:
```
错误信息：JSONDecodeError: Expecting value
错误信息：Cookie解析失败
```

**原因**:
- Cookie不是有效的JSON格式
- Cookie被加密但无法解密
- Cookie字段缺失

**解决方案**:
```
1. 确认Cookie是JSON数组格式：[{...}, {...}]
2. 检查每个Cookie对象包含必需字段：
   - name (字符串)
   - value (字符串)
   - domain (字符串)
   - path (字符串)
   
3. 示例正确格式：
[
  {
    "name": "SERVERID",
    "value": "xxx",
    "domain": ".kookapp.cn",
    "path": "/",
    "secure": true,
    "sameSite": "None"
  }
]
```

---

### 问题1: Redis 连接失败

**现象**:
```bash
ERROR | Redis连接失败: [Errno 10061] 由于目标计算机积极拒绝，无法连接。
```

**影响**: 
- ✅ 不影响核心功能
- ✅ 系统自动使用内存模式
- ❌ 消息不会持久化

**解决方案（可选）**:

**方法1: 使用内存模式（推荐）**
- 无需任何操作
- 系统已自动降级到内存模式

**方法2: 安装 Redis（高级用户）**
```bash
# 1. 下载 Redis for Windows
# https://github.com/tporadowski/redis/releases

# 2. 解压到目录
# 例如: C:\Redis

# 3. 运行 Redis
cd C:\Redis
redis-server.exe

# 4. 重新启动 KOOKForwarder
```

---

### 问题2: 数据库功能异常

**现象**:
```bash
ERROR | 'Database' object has no attribute 'execute'
ERROR | 'Database' object has no attribute 'get_mapping_learning_history'
```

**影响**: 
- ✅ 基础功能正常（消息转发、账号管理）
- ❌ 部分高级功能受限（邮件配置、映射学习历史）

**状态**: 
- 不影响日常使用
- 开发团队正在修复

---

### 问题3: 验证码识别失败

**现象**:
```bash
WARNING | ddddocr库加载失败
ERROR | OCR 识别异常
```

**解决方案**:
```bash
# 1. 确保安装了 ddddocr
pip install ddddocr

# 2. 如果遇到依赖问题
pip install --upgrade onnxruntime
pip install --upgrade Pillow

# 3. 重新打包
pyinstaller build\pyinstaller.spec --clean --noconfirm
```

---

## 📊 常见错误代码

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| `[Errno 10061]` | 连接被拒绝（目标服务未运行） | 检查后端是否启动 |
| `[Errno 10048]` | 端口被占用 | 结束占用端口的进程 |
| `[Errno 2]` | 文件未找到 | 检查路径是否正确 |
| `[Errno 13]` | 权限不足 | 以管理员身份运行 |
| `ModuleNotFoundError` | 缺少 Python 模块 | `pip install <模块名>` |
| `ImportError` | 导入错误 | 检查代码语法 |
| `SyntaxError` | 语法错误 | 修复代码错误 |
| `RuntimeError` | 运行时错误 | 查看详细日志 |

---

## 📝 日志收集

### 后端日志

**位置**:
```
C:\Users\你的用户名\KOOK-Build\CSBJJWT\dist\KOOKForwarder\logs\
```

**主要日志文件**:
- `app.log` - 应用主日志
- `error.log` - 错误日志
- `access.log` - API 访问日志

**查看方法**:
```bash
# 查看最新日志
cd dist\KOOKForwarder\logs
type app.log | more

# 查看错误日志
type error.log

# 搜索特定错误
findstr /i "error" app.log
findstr /i "failed" app.log
```

---

### Electron 日志

**位置**:
```
%APPDATA%\KOOK消息转发系统\logs\
```

**主要日志文件**:
- `main.log` - 主进程日志
- `renderer.log` - 渲染进程日志

**查看方法**:
```bash
# 打开日志目录
explorer %APPDATA%\KOOK消息转发系统\logs

# 查看主进程日志
notepad %APPDATA%\KOOK消息转发系统\logs\main.log
```

---

### 构建日志

**位置**:
```
# PyInstaller 日志
build\pyinstaller\warn-pyinstaller.txt

# npm 日志
frontend\npm-debug.log
%USERPROFILE%\AppData\Local\npm-cache\_logs\
```

**查看方法**:
```bash
# 查看 PyInstaller 警告
type build\pyinstaller\warn-pyinstaller.txt

# 查看 npm 日志
cd frontend
type npm-debug.log
```

---

## 🔧 诊断工具

### 环境检查工具

**创建 `check_env.bat`**:
```batch
@echo off
echo ========================================
echo KOOK Environment Check
echo ========================================

echo [1] Python Version:
python --version

echo.
echo [2] Node.js Version:
node --version

echo.
echo [3] npm Version:
npm --version

echo.
echo [4] Git Version:
git --version

echo.
echo [5] PyInstaller:
pip show pyinstaller

echo.
echo [6] 8000 Port Status:
netstat -ano | findstr :8000

echo.
pause
```

**运行**:
```bash
check_env.bat
```

---

### 后端测试工具

**创建 `test_backend.bat`**:
```batch
@echo off
echo Testing backend...

cd dist\KOOKForwarder
start "" KOOKForwarder.exe

timeout /t 5

curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/status

pause
```

---

### 日志分析工具

**创建 `analyze_logs.bat`**:
```batch
@echo off
echo ========================================
echo Log Analysis
echo ========================================

cd dist\KOOKForwarder\logs

echo [1] Error Count:
findstr /i /c:"error" app.log | find /c /v ""

echo.
echo [2] Warning Count:
findstr /i /c:"warning" app.log | find /c /v ""

echo.
echo [3] Fatal Errors:
findstr /i /c:"fatal" app.log

echo.
echo [4] Recent Errors:
findstr /i /c:"error" app.log | more +10

pause
```

---

## 📞 获取帮助

### 提交问题时请包含：

1. **系统信息**:
   ```bash
   systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
   ```

2. **环境版本**:
   ```bash
   python --version
   node --version
   npm --version
   ```

3. **完整错误日志**:
   - 复制完整的错误信息
   - 包含堆栈跟踪

4. **操作步骤**:
   - 详细描述你执行的命令
   - 按顺序列出

5. **已尝试的解决方案**:
   - 列出已经尝试过的方法

---

### 联系方式

- GitHub Issues: https://github.com/gfchfjh/CSBJJWT/issues
- 相关文档: [WINDOWS_PACKAGING_FIXES.md](./WINDOWS_PACKAGING_FIXES.md)

---

**文档版本**: 1.0  
**最后更新**: 2025-11-03  
**维护者**: KOOK Development Team
