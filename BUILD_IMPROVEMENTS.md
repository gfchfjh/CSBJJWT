# 构建改进指南 - v17.0.0深度优化

**目标**: 完善Windows和macOS构建配置，优化安装包大小

---

## 一、macOS构建完善

### 1.1 图标生成

#### 自动化脚本
```bash
# 运行图标生成脚本
./scripts/generate_macos_icons.sh
```

#### 手动生成（如果脚本失败）

```bash
# 1. 创建iconset目录
mkdir -p build/icon.iconset

# 2. 使用sips或convert生成各尺寸图标
sips -z 16 16     build/icon-1024.png --out build/icon.iconset/icon_16x16.png
sips -z 32 32     build/icon-1024.png --out build/icon.iconset/icon_16x16@2x.png
sips -z 32 32     build/icon-1024.png --out build/icon.iconset/icon_32x32.png
sips -z 64 64     build/icon-1024.png --out build/icon.iconset/icon_32x32@2x.png
sips -z 128 128   build/icon-1024.png --out build/icon.iconset/icon_128x128.png
sips -z 256 256   build/icon-1024.png --out build/icon.iconset/icon_128x128@2x.png
sips -z 256 256   build/icon-1024.png --out build/icon.iconset/icon_256x256.png
sips -z 512 512   build/icon-1024.png --out build/icon.iconset/icon_256x256@2x.png
sips -z 512 512   build/icon-1024.png --out build/icon.iconset/icon_512x512.png
sips -z 1024 1024 build/icon-1024.png --out build/icon.iconset/icon_512x512@2x.png

# 3. 转换为icns
iconutil -c icns build/icon.iconset -o build/icon.icns
```

### 1.2 代码签名

#### 申请开发者证书
1. 登录 [Apple Developer](https://developer.apple.com/)
2. 创建"Developer ID Application"证书
3. 下载并安装到钥匙串

#### 配置签名
```yaml
# frontend/electron-builder.yml
mac:
  identity: "Developer ID Application: YOUR NAME (TEAM_ID)"
  hardenedRuntime: true
  gatekeeperAssess: false
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
```

#### 公证（Notarization）
```bash
# 1. 上传到Apple公证
xcrun altool --notarize-app \
  --primary-bundle-id "com.kook.forwarder" \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD" \
  --file dist/KOOK-Forwarder-1.0.0.dmg

# 2. 检查公证状态
xcrun altool --notarization-info REQUEST_UUID \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD"

# 3. 装订公证票据
xcrun stapler staple dist/KOOK-Forwarder-1.0.0.dmg
```

---

## 二、Windows构建完善

### 2.1 NSIS安装器配置

#### 增强版配置
```yaml
# frontend/electron-builder.yml
nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
  allowElevation: true
  installerIcon: build/icon.ico
  uninstallerIcon: build/icon.ico
  installerHeaderIcon: build/icon.ico
  createDesktopShortcut: true
  createStartMenuShortcut: true
  shortcutName: KOOK消息转发系统
  license: LICENSE
  language: 2052  # 中文
  
  # ✅ v17.0.0新增：自定义安装脚本
  include: build/installer.nsh
  
  # ✅ 卸载时保留用户数据选项
  deleteAppDataOnUninstall: false
```

#### 自定义安装脚本
```nsh
# build/installer.nsh

# 安装前检查
!macro customInit
  # 检查是否已安装
  ReadRegStr $0 HKLM "Software\KOOKForwarder" "InstallLocation"
  ${If} $0 != ""
    MessageBox MB_YESNO "检测到已安装版本，是否卸载后继续安装？" IDYES uninstall IDNO abort
    uninstall:
      ExecWait '"$0\Uninstall.exe" /S'
      Goto done
    abort:
      Abort "安装已取消"
    done:
  ${EndIf}
!macroend

# 安装后操作
!macro customInstall
  # 创建数据目录
  CreateDirectory "$APPDATA\KOOKForwarder"
  
  # 写入注册表
  WriteRegStr HKLM "Software\KOOKForwarder" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\KOOKForwarder" "Version" "${VERSION}"
  
  # 添加到PATH（可选）
  # ${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$INSTDIR"
!macroend

# 卸载前确认
!macro customUnInstall
  MessageBox MB_YESNO "是否保留用户数据和配置？" IDYES keep IDNO remove
  keep:
    DetailPrint "保留用户数据"
    Goto done
  remove:
    RMDir /r "$APPDATA\KOOKForwarder"
    DetailPrint "已删除用户数据"
  done:
  
  # 清理注册表
  DeleteRegKey HKLM "Software\KOOKForwarder"
!macroend
```

### 2.2 代码签名

#### 获取代码签名证书
1. 从受信任的CA购买代码签名证书（如Sectigo、DigiCert）
2. 导出为PFX格式

#### 配置签名
```yaml
# frontend/electron-builder.yml
win:
  certificateFile: build/certificate.pfx
  certificatePassword: ${CERTIFICATE_PASSWORD}
  signDlls: true
  
  # 或使用USB Token
  # certificateSubjectName: "YOUR COMPANY NAME"
  # certificateSha1: "THUMBPRINT"
  # signingHashAlgorithms: ['sha256']
```

#### 时间戳服务器
```yaml
win:
  rfc3161TimeStampServer: "http://timestamp.digicert.com"
  timeStampServer: "http://timestamp.digicert.com"
```

---

## 三、安装包大小优化

### 3.1 当前大小分析

| 组件 | 大小 | 占比 |
|------|------|------|
| Electron框架 | ~60MB | 40% |
| Python运行时 | ~40MB | 27% |
| Node.js依赖 | ~30MB | 20% |
| Redis | ~5MB | 3% |
| 应用代码 | ~10MB | 7% |
| 其他 | ~5MB | 3% |
| **总计** | **~150MB** | **100%** |

### 3.2 优化策略

#### 策略1：压缩资源文件（预计减少20-30MB）

```javascript
// frontend/electron/main.js
const { app } = require('electron');

// 启用资源压缩
if (!app.isPackaged) {
  process.env.NODE_ENV = 'production';
}

// 使用asar压缩
// 自动由electron-builder处理
```

```yaml
# frontend/electron-builder.yml
asar: true
asarUnpack:
  - "resources/**"
  - "backend/**"
  - "redis/**"

compression: maximum  # 最大压缩
```

#### 策略2：剔除开发依赖（预计减少10-15MB）

```json
// package.json
{
  "devDependencies": {
    // 这些不会被打包
    "electron-builder": "^24.0.0",
    "vite": "^5.0.0"
  },
  "dependencies": {
    // 只打包生产依赖
    "electron": "^28.0.0"
  }
}
```

#### 策略3：Python运行时精简（预计减少15-20MB）

```python
# scripts/optimize_python_bundle.py
import os
import shutil
from pathlib import Path

def remove_unused_files(bundle_dir):
    """移除不必要的Python文件"""
    
    # 移除.pyc缓存
    for root, dirs, files in os.walk(bundle_dir):
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))
    
    # 移除测试文件
    test_patterns = ['*/tests/*', '*/test/*', '*_test.py']
    for pattern in test_patterns:
        for file in Path(bundle_dir).rglob(pattern):
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)
    
    # 移除文档文件
    doc_patterns = ['*.rst', '*.md', 'LICENSE', 'CHANGELOG']
    for pattern in doc_patterns:
        for file in Path(bundle_dir).rglob(pattern):
            file.unlink()
```

#### 策略4：使用外部Redis（预计减少5MB）

```yaml
# 方案A：默认使用外部Redis
redis:
  use_embedded: false
  host: "localhost"
  port: 6379

# 方案B：仅在用户未安装Redis时才使用内置
# 安装时检测系统是否已有Redis
```

#### 策略5：按需下载Chromium（预计减少50-70MB）

```javascript
// frontend/electron/main.js
const { app } = require('electron');
const path = require('path');
const fs = require('fs');

// 首次启动时下载Playwright Chromium
async function ensureChromium() {
  const chromiumPath = path.join(app.getPath('userData'), 'chromium');
  
  if (!fs.existsSync(chromiumPath)) {
    // 显示下载进度对话框
    const { dialog } = require('electron');
    dialog.showMessageBox({
      type: 'info',
      message: '首次启动需要下载浏览器组件（约70MB），请稍候...',
      buttons: ['确定']
    });
    
    // 下载Chromium
    const playwright = require('playwright');
    await playwright.chromium.launch({ executablePath: chromiumPath });
  }
}

app.on('ready', async () => {
  await ensureChromium();
  // 继续启动应用...
});
```

#### 策略6：使用UPX压缩可执行文件（预计减少30-40%）

```bash
# 安装UPX
# macOS: brew install upx
# Windows: choco install upx
# Linux: apt-get install upx

# 压缩可执行文件
upx --best --lzma dist/KOOK-Forwarder.exe

# electron-builder自动配置
```

```yaml
# frontend/electron-builder.yml
win:
  target:
    - target: nsis
      arch: [x64]
  
  # ✅ v17.0.0新增：UPX压缩
  compression: maximum
  
linux:
  target: [AppImage]
  
  # UPX压缩
  compression: maximum
```

### 3.3 优化后预期大小

| 版本 | 原大小 | 优化后 | 减少 |
|------|--------|--------|------|
| Windows NSIS | 150MB | 90-100MB | 33-40% |
| macOS DMG | 155MB | 95-105MB | 32-39% |
| Linux AppImage | 145MB | 85-95MB | 34-41% |

### 3.4 实施步骤

1. **备份当前构建**
```bash
cp -r dist/ dist_backup/
```

2. **应用优化配置**
```bash
# 更新electron-builder.yml
# 运行优化脚本
python scripts/optimize_python_bundle.py
```

3. **重新构建**
```bash
cd frontend
npm run build
npm run electron:build:win
npm run electron:build:mac
npm run electron:build:linux
```

4. **测试功能完整性**
```bash
# 安装测试
# 运行所有功能测试
# 确保无功能缺失
```

5. **对比大小**
```bash
ls -lh dist/ dist_backup/
```

---

## 四、持续集成配置

### 4.1 GitHub Actions配置

```yaml
# .github/workflows/build.yml
name: Build All Platforms

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build
        run: |
          cd frontend
          npm run build
          npm run electron:build:win
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: frontend/dist/*.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Generate icns
        run: ./scripts/generate_macos_icons.sh
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build
        run: |
          cd frontend
          npm run build
          npm run electron:build:mac
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: macos-dmg
          path: frontend/dist/*.dmg

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build
        run: |
          cd frontend
          npm run build
          npm run electron:build:linux
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: linux-appimage
          path: frontend/dist/*.AppImage

  release:
    needs: [build-windows, build-macos, build-linux]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            windows-installer/*
            macos-dmg/*
            linux-appimage/*
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 五、构建检查清单

### 构建前检查
- [ ] 更新VERSION文件
- [ ] 更新CHANGELOG.md
- [ ] 运行所有测试
- [ ] 检查依赖版本
- [ ] 生成macOS图标

### 构建中检查
- [ ] 监控构建日志
- [ ] 检查文件大小
- [ ] 验证签名状态
- [ ] 检查依赖完整性

### 构建后检查
- [ ] 在各平台测试安装
- [ ] 验证所有功能
- [ ] 检查自动更新
- [ ] 测试卸载过程
- [ ] 验证用户数据保留

### 发布前检查
- [ ] 生成SHA256校验和
- [ ] 编写Release Notes
- [ ] 更新官网下载链接
- [ ] 准备用户通知

---

## 六、故障排查

### 问题1：macOS图标不显示

**原因**: icns文件格式不正确

**解决**:
```bash
# 验证icns文件
sips -g all build/icon.icns

# 重新生成
./scripts/generate_macos_icons.sh
```

### 问题2：Windows签名失败

**原因**: 证书密码或路径错误

**解决**:
```bash
# 设置环境变量
export CERTIFICATE_PASSWORD="your_password"

# 或在命令行中指定
electron-builder --win --publish never \
  --config.win.certificatePassword="$CERTIFICATE_PASSWORD"
```

### 问题3：安装包过大

**原因**: 包含了开发依赖或测试文件

**解决**:
```bash
# 分析包内容
asar extract app.asar extracted/

# 查看哪些文件占用空间
du -sh extracted/* | sort -h

# 在electron-builder.yml中排除
files:
  - "!**/*.map"
  - "!**/node_modules/.cache"
  - "!**/tests"
```

---

**最后更新**: 2025-10-31  
**适用版本**: v17.0.0+
