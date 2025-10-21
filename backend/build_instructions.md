# 后端打包指南

本文档说明如何使用PyInstaller将Python后端打包成单个可执行文件。

---

## 📋 前提条件

### 1. 安装PyInstaller

```bash
cd backend
pip install pyinstaller
```

### 2. 安装所有依赖

```bash
pip install -r requirements.txt
```

---

## 🔨 打包步骤

### Windows打包

```bash
# 方法1：使用spec文件（推荐）
pyinstaller backend/build_backend.spec

# 方法2：直接命令行
pyinstaller \
  --onefile \
  --name KookForwarder-Backend \
  --icon build/icon.ico \
  --add-data "redis/redis-server.exe;redis" \
  --add-data "redis/redis.conf;redis" \
  --add-data "backend/data/selectors.yaml;data" \
  --hidden-import playwright \
  --hidden-import fastapi \
  --hidden-import uvicorn \
  backend/app/main.py
```

### Linux/macOS打包

```bash
# 方法1：使用spec文件（推荐）
pyinstaller backend/build_backend.spec

# 方法2：直接命令行
pyinstaller \
  --onefile \
  --name KookForwarder-Backend \
  --icon build/icon.icns \
  --add-data "redis/redis-server:redis" \
  --add-data "redis/redis.conf:redis" \
  --add-data "backend/data/selectors.yaml:data" \
  --hidden-import playwright \
  --hidden-import fastapi \
  --hidden-import uvicorn \
  backend/app/main.py
```

---

## 📦 输出文件

打包完成后，可执行文件位于：

- **Windows**: `dist/KookForwarder-Backend.exe` (~80-120MB)
- **Linux**: `dist/KookForwarder-Backend` (~70-100MB)
- **macOS**: `dist/KookForwarder-Backend` (~80-110MB)

---

## 🧪 测试打包后的程序

### 1. 运行可执行文件

```bash
# Windows
dist/KookForwarder-Backend.exe

# Linux/macOS
./dist/KookForwarder-Backend
```

### 2. 验证功能

- ✅ 后端API启动（http://localhost:9527）
- ✅ Redis自动启动
- ✅ 数据库自动创建
- ✅ Playwright浏览器下载（首次运行）

---

## ⚠️ 常见问题

### 1. 打包后体积过大（>200MB）

**原因**: 包含了不必要的依赖

**解决**:
```bash
# 在spec文件中添加excludes
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'tkinter',
]
```

### 2. 运行时提示缺少模块

**原因**: 某些动态导入的模块未被打包

**解决**:
```bash
# 在spec文件的hiddenimports中添加缺失模块
hiddenimports=[
    'missing_module_name',
]
```

### 3. Playwright浏览器未找到

**原因**: 打包后未包含浏览器文件

**解决**:
```bash
# 首次运行时手动安装
playwright install chromium
```

或在打包时包含浏览器（会增加~300MB体积）：
```python
# 在spec文件datas中添加
datas += collect_data_files('playwright')
```

### 4. Redis无法启动

**原因**: Redis可执行文件权限问题

**解决**:
```bash
# Linux/macOS
chmod +x dist/_internal/redis/redis-server

# 或在spec文件中设置权限
```

---

## 🚀 优化建议

### 1. 使用UPX压缩（可选）

```bash
# 安装UPX
# Windows: https://github.com/upx/upx/releases
# Linux: sudo apt install upx
# macOS: brew install upx

# 在spec文件中启用
upx=True,
```

**效果**: 体积减少30-50%，但启动速度会略慢

### 2. 排除不需要的文件

```python
# spec文件中
excludes=[
    'test',
    'tests',
    '__pycache__',
    '*.pyc',
    '*.pyo',
]
```

### 3. 优化隐藏导入

只导入实际使用的模块，减少不必要的依赖。

---

## 📝 完整构建脚本

### Windows构建脚本（build_windows.bat）

```batch
@echo off
echo ========================================
echo 构建KOOK消息转发系统 - Windows版本
echo ========================================

echo.
echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.11+
    exit /b 1
)

echo.
echo [2/4] 安装依赖...
pip install -r backend/requirements.txt
pip install pyinstaller

echo.
echo [3/4] 打包后端...
pyinstaller backend/build_backend.spec

echo.
echo [4/4] 构建Electron前端...
cd frontend
call npm install
call npm run build
call npm run electron:build

echo.
echo ========================================
echo 构建完成！
echo.
echo 后端: dist/KookForwarder-Backend.exe
echo 前端: frontend/dist/
echo ========================================
pause
```

### Linux/macOS构建脚本（build_unix.sh）

```bash
#!/bin/bash

echo "========================================"
echo "构建KOOK消息转发系统 - Unix版本"
echo "========================================"

# 检查Python
echo ""
echo "[1/4] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.11+"
    exit 1
fi
python3 --version

# 安装依赖
echo ""
echo "[2/4] 安装依赖..."
pip3 install -r backend/requirements.txt
pip3 install pyinstaller

# 打包后端
echo ""
echo "[3/4] 打包后端..."
pyinstaller backend/build_backend.spec

# 设置权限
chmod +x dist/KookForwarder-Backend
if [ -f "dist/_internal/redis/redis-server" ]; then
    chmod +x dist/_internal/redis/redis-server
fi

# 构建前端
echo ""
echo "[4/4] 构建Electron前端..."
cd frontend
npm install
npm run build
npm run electron:build

echo ""
echo "========================================"
echo "构建完成！"
echo ""
echo "后端: dist/KookForwarder-Backend"
echo "前端: frontend/dist/"
echo "========================================"
```

---

## 📄 参考资源

- [PyInstaller官方文档](https://pyinstaller.org/en/stable/)
- [Electron Builder文档](https://www.electron.build/)
- [UPX下载](https://github.com/upx/upx/releases)

---

**最后更新**: 2025-10-21  
**适用版本**: v1.11.0+
