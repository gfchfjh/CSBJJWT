# macOS代码签名和公证配置指南

**文档版本**: v1.0  
**更新时间**: 2025-10-24  
**作者**: 深度优化版  

---

## 📋 概述

本指南详细说明如何为KOOK消息转发系统配置macOS代码签名和公证，以便发布到macOS平台。

---

## 🎯 前置要求

### 1. Apple开发者账号
- **个人账号**: $99/年
- **企业账号**: $299/年（推荐，可发布企业应用）

### 2. 所需证书
- **Developer ID Application**: 用于签名应用
- **Developer ID Installer**: 用于签名安装包（可选）

### 3. 开发环境
- macOS 10.15+
- Xcode 12+
- Xcode Command Line Tools

---

## 🔐 步骤1: 申请Apple开发者证书

### 1.1 访问Apple开发者网站
```bash
# 登录Apple开发者网站
open https://developer.apple.com/account/
```

### 1.2 创建证书
1. 进入 **Certificates, Identifiers & Profiles**
2. 点击 **Certificates** → **+** 创建新证书
3. 选择 **Developer ID Application**
4. 按照提示生成CSR（Certificate Signing Request）

### 1.3 生成CSR
```bash
# 打开钥匙串访问（Keychain Access）
# 菜单栏 → 钥匙串访问 → 证书助理 → 从证书颁发机构请求证书...

# 填写信息：
# - 用户电子邮件地址: your.email@example.com
# - 常用名称: Your Name
# - CA电子邮件地址: 留空
# - 请求是: 存储到磁盘

# 保存CSR文件到桌面
```

### 1.4 下载并安装证书
1. 上传CSR到Apple开发者网站
2. 下载生成的证书（.cer文件）
3. 双击安装到钥匙串

---

## 🔑 步骤2: 配置环境变量

### 2.1 查找证书标识
```bash
# 查看已安装的证书
security find-identity -v -p codesigning

# 输出示例：
# 1) ABC123DEF456 "Developer ID Application: Your Name (TEAM_ID)"
#    ^^^^^^^^^^^^^^^^^^ 这是证书的SHA-1标识
```

### 2.2 设置环境变量
```bash
# 在 ~/.bash_profile 或 ~/.zshrc 中添加

# Apple开发者账号
export APPLE_ID="your.email@example.com"
export APPLE_TEAM_ID="YOUR_TEAM_ID"

# App特定密码（用于公证）
# 在 https://appleid.apple.com 生成
export APPLE_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"

# 证书标识
export CSC_NAME="Developer ID Application: Your Name (TEAM_ID)"

# 刷新环境变量
source ~/.zshrc
```

---

## 📦 步骤3: 配置electron-builder

### 3.1 更新electron-builder.yml
```yaml
# build/electron-builder.yml

mac:
  target:
    - dmg
    - zip
  icon: build/icon.icns
  category: public.app-category.utilities
  artifactName: ${productName}_v${version}_macOS_${arch}.${ext}
  hardenedRuntime: true
  gatekeeperAssess: false
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  
  # ✅ 代码签名配置
  identity: "Developer ID Application: Your Name (TEAM_ID)"
  
  # ✅ 公证配置
  notarize:
    teamId: "YOUR_TEAM_ID"
  
  darkModeSupport: true
  minimumSystemVersion: "10.15.0"
```

### 3.2 验证配置
```bash
# 测试构建（不签名）
cd frontend
npm run build:mac:test

# 完整构建（签名+公证）
npm run build:mac
```

---

## 🔨 步骤4: 本地构建测试

### 4.1 准备图标
```bash
# 生成.icns图标文件
cd build

# 使用iconutil（需要1024x1024 PNG）
mkdir icon.iconset
# 复制不同尺寸的图标到icon.iconset/
iconutil -c icns icon.iconset

# 或使用在线工具: https://cloudconvert.com/png-to-icns
```

### 4.2 执行构建
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建macOS应用
npm run build:mac

# 构建成功后，产物在 frontend/dist/
# - KOOK消息转发系统_v1.17.0_macOS_x64.dmg
# - KOOK消息转发系统_v1.17.0_macOS_x64.zip
```

### 4.3 验证签名
```bash
# 验证应用签名
codesign --verify --deep --strict --verbose=2 \
  "frontend/dist/mac/KOOK消息转发系统.app"

# 查看签名信息
codesign -dv --verbose=4 \
  "frontend/dist/mac/KOOK消息转发系统.app"

# 验证公证状态
spctl -a -vvv -t install \
  "frontend/dist/KOOK消息转发系统_v1.17.0_macOS_x64.dmg"
```

---

## 🌐 步骤5: 配置自动化公证

### 5.1 创建App特定密码
```bash
# 1. 访问 https://appleid.apple.com
# 2. 登录Apple ID
# 3. 安全 → App特定密码 → 生成密码
# 4. 保存生成的密码（格式：xxxx-xxxx-xxxx-xxxx）
```

### 5.2 配置公证脚本
```bash
# build/notarize.js

const { notarize } = require('electron-notarize');

exports.default = async function notarizing(context) {
  const { electronPlatformName, appOutDir } = context;
  
  if (electronPlatformName !== 'darwin') {
    return;
  }

  const appName = context.packager.appInfo.productFilename;
  const appPath = `${appOutDir}/${appName}.app`;

  console.log(`开始公证: ${appPath}`);

  return await notarize({
    appBundleId: 'com.kook.forwarder',
    appPath: appPath,
    appleId: process.env.APPLE_ID,
    appleIdPassword: process.env.APPLE_APP_PASSWORD,
    teamId: process.env.APPLE_TEAM_ID,
  });
};
```

### 5.3 更新package.json
```json
{
  "name": "kook-forwarder",
  "version": "1.17.0",
  "build": {
    "appId": "com.kook.forwarder",
    "afterSign": "build/notarize.js",
    "mac": {
      "hardenedRuntime": true,
      "gatekeeperAssess": false,
      "entitlements": "build/entitlements.mac.plist",
      "entitlementsInherit": "build/entitlements.mac.plist"
    }
  }
}
```

---

## 🚀 步骤6: GitHub Actions自动化

### 6.1 配置GitHub Secrets
在GitHub仓库设置中添加以下Secrets:
- `APPLE_ID`: Apple开发者账号邮箱
- `APPLE_APP_PASSWORD`: App特定密码
- `APPLE_TEAM_ID`: Team ID
- `CSC_LINK`: 证书的base64编码（见下方说明）
- `CSC_KEY_PASSWORD`: 证书密码

### 6.2 导出证书
```bash
# 导出证书为.p12文件
# 1. 打开钥匙串访问
# 2. 找到 "Developer ID Application" 证书
# 3. 右键 → 导出
# 4. 保存为certificate.p12，设置密码

# 转换为base64
base64 -i certificate.p12 -o certificate.txt

# 复制certificate.txt内容到GitHub Secret: CSC_LINK
```

### 6.3 创建GitHub Actions工作流
```yaml
# .github/workflows/build-macos.yml

name: Build macOS

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-macos:
    runs-on: macos-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      
      - name: Build macOS App
        env:
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_APP_PASSWORD: ${{ secrets.APPLE_APP_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
          CSC_LINK: ${{ secrets.CSC_LINK }}
          CSC_KEY_PASSWORD: ${{ secrets.CSC_KEY_PASSWORD }}
        run: |
          cd frontend
          npm run build:mac
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: macos-dmg
          path: |
            frontend/dist/*.dmg
            frontend/dist/*.zip
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: |
            frontend/dist/*.dmg
            frontend/dist/*.zip
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 🔍 步骤7: 故障排查

### 7.1 常见错误

#### 错误1: "Developer ID Application not found"
```bash
# 原因: 证书未正确安装
# 解决:
security find-identity -v -p codesigning
# 确保列表中有 "Developer ID Application"
```

#### 错误2: "altool verification failed"
```bash
# 原因: App特定密码错误或网络问题
# 解决:
# 1. 重新生成App特定密码
# 2. 检查网络连接
# 3. 使用VPN（如果在中国大陆）
```

#### 错误3: "Bundle format unrecognized"
```bash
# 原因: 应用结构不正确
# 解决:
# 1. 检查entitlements配置
# 2. 确保所有二进制文件都已签名
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application" \
  "YourApp.app"
```

### 7.2 调试命令
```bash
# 检查应用签名
codesign -dv --verbose=4 "YourApp.app"

# 检查所有签名
codesign --verify --deep --strict --verbose=2 "YourApp.app"

# 检查公证状态
xcrun altool --notarization-info REQUEST_ID \
  --username "$APPLE_ID" \
  --password "$APPLE_APP_PASSWORD"

# 查看公证历史
xcrun altool --notarization-history 0 \
  --username "$APPLE_ID" \
  --password "$APPLE_APP_PASSWORD"
```

---

## 📊 估算时间线

| 步骤 | 预计时间 |
|------|---------|
| 申请Apple开发者账号 | 1-3个工作日 |
| 生成证书 | 1小时 |
| 配置本地环境 | 2小时 |
| 首次构建测试 | 3小时 |
| 配置GitHub Actions | 4小时 |
| 测试和调试 | 8小时 |
| **总计** | **约2-3天** |

---

## ✅ 验收清单

- [ ] Apple开发者账号已激活
- [ ] Developer ID Application证书已安装
- [ ] 本地环境变量已配置
- [ ] .icns图标已生成
- [ ] entitlements.mac.plist已配置
- [ ] 本地构建成功（未签名）
- [ ] 本地构建成功（已签名）
- [ ] 公证成功
- [ ] GitHub Actions配置完成
- [ ] 自动化发布测试通过
- [ ] macOS 10.15+测试安装成功
- [ ] macOS 13+测试运行正常

---

## 📚 参考资源

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [electron-builder macOS](https://www.electron.build/configuration/mac)
- [electron-notarize](https://github.com/electron/electron-notarize)
- [Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)

---

## 💡 最佳实践

1. **证书管理**: 使用钥匙串妥善保管证书
2. **密码安全**: 不要在代码中硬编码密码
3. **自动化**: 使用GitHub Actions自动化构建
4. **测试**: 在多个macOS版本上测试
5. **备份**: 定期备份证书和配置

---

## 🆘 获取帮助

如遇到问题，请：
1. 查看本文档的故障排查章节
2. 访问项目Issues页面
3. 联系开发团队

---

*本文档持续更新，最后更新: 2025-10-24*
