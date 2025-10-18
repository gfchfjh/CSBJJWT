# 构建指南

本目录包含打包和构建应用所需的配置和资源。

## 📦 打包前准备

### 1. 图标生成

#### 方法A：使用Python脚本（推荐）

```bash
# 安装依赖
pip install Pillow

# 生成基础图标
python build/generate_simple_icon.py

# 这将生成多个尺寸的PNG图标
```

#### 方法B：使用现有设计

如果你有设计师提供的图标，将其放置在以下位置：
- `build/icon.ico` - Windows图标
- `build/icon.icns` - macOS图标
- `build/icons/` - Linux图标目录

### 2. Windows图标转换

```bash
# 在线转换（推荐）
# 访问 https://convertio.co/zh/png-ico/
# 上传 build/icon-256.png
# 下载为 icon.ico 并放到 build/ 目录

# 或使用ImageMagick
convert build/icon-256.png -define icon:auto-resize=256,128,64,48,32,16 build/icon.ico
```

### 3. macOS图标生成

```bash
# 创建iconset目录
mkdir icon.iconset

# 生成不同尺寸（macOS需要特定尺寸）
sips -z 16 16     build/icon-16.png   --out icon.iconset/icon_16x16.png
sips -z 32 32     build/icon-32.png   --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     build/icon-32.png   --out icon.iconset/icon_32x32.png
sips -z 64 64     build/icon-64.png   --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   build/icon-128.png  --out icon.iconset/icon_128x128.png
sips -z 256 256   build/icon-256.png  --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   build/icon-256.png  --out icon.iconset/icon_256x256.png
sips -z 512 512   build/icon-512.png  --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   build/icon-512.png  --out icon.iconset/icon_512x512.png
sips -z 1024 1024 build/icon-1024.png --out icon.iconset/icon_512x512@2x.png

# 生成icns文件
iconutil -c icns icon.iconset

# 移动到build目录
mv icon.icns build/
```

## 🔨 构建应用

### 前端构建

```bash
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 打包Electron应用
npm run electron:build
```

### 后端构建

```bash
cd backend

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 打包后端（使用PyInstaller）
pyinstaller build/build_backend.py

# 或使用脚本
python build/build_backend.py
```

### 完整构建

```bash
# 使用构建脚本（推荐）
./build/build_all.sh    # Linux/macOS
build\build_all.bat     # Windows

# 或使用Python脚本
python build/build_all_complete.py
```

## 📋 构建产物

构建完成后，产物位于：

- **Windows**: `frontend/dist/KookForwarder_v{version}_Windows_x64.exe`
- **macOS**: `frontend/dist/KookForwarder_v{version}_macOS.dmg`
- **Linux**: `frontend/dist/KookForwarder_v{version}_Linux_x64.AppImage`

## 🧪 测试打包应用

### Windows

```bash
# 安装
双击 .exe 文件

# 测试
启动应用，检查：
- 图标是否正确显示
- 应用是否正常启动
- 后端服务是否自动启动
- Redis是否正常运行
```

### macOS

```bash
# 挂载DMG
open KookForwarder_v1.0.0_macOS.dmg

# 拖动到Applications
# 首次启动需要右键→打开

# 测试
启动应用，检查同上
```

### Linux

```bash
# 赋予执行权限
chmod +x KookForwarder_v1.0.0_Linux_x64.AppImage

# 运行
./KookForwarder_v1.0.0_Linux_x64.AppImage

# 测试
启动应用，检查同上
```

## 🐛 常见问题

### 1. 图标不显示

**原因**：图标文件缺失或路径错误

**解决**：
- 确保 `build/icon.ico`（Windows）存在
- 确保 `build/icon.icns`（macOS）存在
- 确保 `build/icons/`（Linux）目录存在且包含所有尺寸

### 2. 后端打包失败

**原因**：缺少依赖或路径错误

**解决**：
```bash
# 清理缓存
rm -rf build dist *.spec

# 重新打包
pip install -r requirements.txt
pip install pyinstaller
python build/build_backend.py
```

### 3. Redis未打包

**原因**：Redis二进制文件缺失

**解决**：
```bash
# 确保redis目录存在
ls redis/

# 应该包含：
# - redis-server.exe (Windows)
# - redis-server (Linux/macOS)
# - redis.conf

# 如果缺失，从Redis官网下载
```

### 4. Playwright Chromium缺失

**原因**：Chromium未打包

**解决**：
```bash
# 安装Chromium
playwright install chromium

# 确保打包时包含
# 在build_backend.py中检查--add-binary参数
```

## 📝 版本更新

更新版本号：

1. **package.json**：`frontend/package.json`
2. **Python配置**：`backend/app/config.py`
3. **README**：更新版本徽章

```bash
# 统一更新版本号
VERSION="1.5.0"

# 更新package.json
sed -i "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" frontend/package.json

# 更新Python配置
sed -i "s/app_version = \".*\"/app_version = \"$VERSION\"/" backend/app/config.py

# 提交
git add .
git commit -m "chore: bump version to $VERSION"
git tag v$VERSION
git push origin v$VERSION
```

## 🚀 CI/CD自动构建

项目已配置GitHub Actions自动构建：

1. 推送tag时自动触发
2. 在三个平台上并行构建
3. 自动创建GitHub Release
4. 上传构建产物

触发构建：
```bash
git tag v1.5.0
git push origin v1.5.0
```

查看构建状态：
https://github.com/yourusername/CSBJJWT/actions

## 📚 参考文档

- [Electron Builder](https://www.electron.build/)
- [PyInstaller](https://pyinstaller.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)
