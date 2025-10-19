# macOS代码签名配置指南

**目标**: 配置代码签名，让macOS用户无需"右键→打开"即可运行应用

---

## 📋 前置要求

1. **Apple开发者账号**
   - 个人开发者：$99/年
   - 企业开发者：$299/年
   - 申请地址：https://developer.apple.com/programs/

2. **macOS开发环境**
   - macOS 10.15+（Catalina或更高版本）
   - Xcode（通过App Store安装）

3. **开发者证书**
   - Developer ID Application证书
   - Developer ID Installer证书（用于pkg安装包）

---

## 🔑 步骤1：申请Apple开发者账号

### 1.1 注册流程

1. 访问 https://developer.apple.com
2. 点击"Account"登录或注册
3. 选择开发者计划类型（个人/企业）
4. 支付年费（$99或$299）
5. 等待审核（通常1-3天）

### 1.2 审核通过后

- 您将收到确认邮件
- 可以访问开发者中心
- 可以创建证书和配置文件

---

## 📜 步骤2：创建开发者证书

### 2.1 使用Xcode创建（推荐）

1. **打开Xcode**
   
2. **进入Preferences**
   - `Xcode → Preferences` (或按 `Cmd + ,`)

3. **添加Apple ID**
   - 点击"Accounts"标签
   - 点击左下角"+"号
   - 选择"Apple ID"
   - 输入您的Apple开发者账号

4. **管理证书**
   - 选择您的Team
   - 点击"Manage Certificates"
   - 点击"+"号
   - 选择"Developer ID Application"
   - 点击"Done"

### 2.2 使用开发者中心创建（手动）

1. **生成证书签名请求（CSR）**
   ```bash
   # 打开"钥匙串访问"
   # 菜单：钥匙串访问 → 证书助理 → 从证书颁发机构请求证书
   # 填写信息：
   #   - 用户电子邮件地址：你的Apple ID
   #   - 常用名称：你的姓名
   #   - CA电子邮件地址：留空
   #   - 请求是：存储到磁盘
   # 保存CSR文件到桌面
   ```

2. **在开发者中心创建证书**
   - 访问：https://developer.apple.com/account/resources/certificates/list
   - 点击"+"创建新证书
   - 选择"Developer ID Application"
   - 上传CSR文件
   - 下载生成的证书（.cer文件）

3. **安装证书**
   - 双击下载的.cer文件
   - 证书会自动安装到"钥匙串访问"中

---

## 🔧 步骤3：配置electron-builder

### 3.1 更新electron-builder.yml

编辑 `build/electron-builder.yml`:

```yaml
mac:
  target:
    - dmg
  icon: build/icon.icns
  category: public.app-category.utilities
  artifactName: ${productName}_v${version}_macOS.${ext}
  hardenedRuntime: true
  gatekeeperAssess: false
  
  # ===== 添加签名配置 =====
  identity: "Developer ID Application: Your Name (TEAM_ID)"
  # 示例：identity: "Developer ID Application: Zhang San (AB12CD34EF)"
  
  # entitlements文件
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  
  # 代码签名
  sign: true
  type: distribution

dmg:
  title: ${productName} ${version}
  icon: build/icon.icns
  background: build/dmg-background.png
  window:
    width: 540
    height: 380
  contents:
    - x: 144
      y: 188
      type: file
    - x: 396
      y: 188
      type: link
      path: /Applications
  # DMG也需要签名
  sign: true
```

### 3.2 查找您的Identity字符串

```bash
# 列出所有开发者证书
security find-identity -v -p codesigning

# 输出示例：
# 1) AB12CD34EF... "Developer ID Application: Zhang San (AB12CD34EF)"
```

复制完整的字符串（包括引号内的内容）

### 3.3 创建entitlements.mac.plist

创建文件 `build/entitlements.mac.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <!-- 允许JIT编译（Chromium需要） -->
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    
    <!-- 允许执行未签名的代码（Python后端） -->
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    
    <!-- 允许动态库加载 -->
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
    
    <!-- 禁用库验证 -->
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    
    <!-- 网络访问（Client） -->
    <key>com.apple.security.network.client</key>
    <true/>
    
    <!-- 网络访问（Server - 用于本地API） -->
    <key>com.apple.security.network.server</key>
    <true/>
    
    <!-- 文件系统访问（只读） -->
    <key>com.apple.security.files.user-selected.read-only</key>
    <true/>
    
    <!-- 文件系统访问（读写） -->
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
  </dict>
</plist>
```

---

## 🤖 步骤4：配置GitHub Actions自动签名

### 4.1 准备密钥

1. **导出证书为P12文件**
   ```bash
   # 打开"钥匙串访问"
   # 找到"Developer ID Application"证书
   # 右键 → 导出"Developer ID Application: ..."
   # 文件格式：个人信息交换 (.p12)
   # 设置密码（记住这个密码！）
   # 保存为certificate.p12
   ```

2. **转换为Base64**
   ```bash
   base64 -i certificate.p12 -o certificate_base64.txt
   cat certificate_base64.txt
   ```
   
   复制输出的Base64字符串

3. **获取App专用密码**（用于公证）
   - 访问：https://appleid.apple.com
   - 登录后选择"安全"
   - "App专用密码" → 生成
   - 复制生成的密码（格式：xxxx-xxxx-xxxx-xxxx）

### 4.2 添加GitHub Secrets

在GitHub仓库的`Settings → Secrets and variables → Actions`添加：

| Secret名称 | 值 | 说明 |
|-----------|---|------|
| `APPLE_CERTIFICATE` | Base64字符串 | P12证书的Base64编码 |
| `APPLE_CERTIFICATE_PASSWORD` | 证书密码 | 导出P12时设置的密码 |
| `APPLE_ID` | Apple ID邮箱 | 用于公证的Apple ID |
| `APPLE_PASSWORD` | App专用密码 | 刚才生成的专用密码 |
| `APPLE_TEAM_ID` | Team ID | 在证书中的括号内，如(AB12CD34EF) |

### 4.3 更新GitHub Actions配置

编辑 `.github/workflows/build-and-release.yml`，在macOS构建部分添加：

```yaml
build-macos:
  name: Build macOS
  runs-on: macos-latest
  needs: test
  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ env.NODE_VERSION }}

    # ===== 添加证书导入步骤 =====
    - name: Import Code Signing Certificate
      run: |
        # 创建临时钥匙串
        security create-keychain -p actions temp.keychain
        security default-keychain -s temp.keychain
        security unlock-keychain -p actions temp.keychain
        security set-keychain-settings -lut 21600 temp.keychain
        
        # 解码并导入证书
        echo "${{ secrets.APPLE_CERTIFICATE }}" | base64 --decode > certificate.p12
        security import certificate.p12 -k temp.keychain \
          -P "${{ secrets.APPLE_CERTIFICATE_PASSWORD }}" \
          -T /usr/bin/codesign \
          -T /usr/bin/productsign
        
        # 设置访问权限
        security set-key-partition-list -S apple-tool:,apple: -s -k actions temp.keychain
        
        # 验证证书
        security find-identity -v -p codesigning temp.keychain

    - name: Install Python dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Install Playwright
      run: |
        cd backend
        playwright install chromium

    - name: Build backend
      run: |
        cd backend
        pyinstaller --name=kook-forwarder-backend \
          --onefile \
          --add-data "app:app" \
          --hidden-import=playwright \
          --hidden-import=playwright._impl._driver \
          app/main.py

    - name: Install frontend dependencies
      run: |
        cd frontend
        npm install

    - name: Build frontend
      run: |
        cd frontend
        npm run build

    # ===== 修改Electron构建步骤，启用签名 =====
    - name: Build Electron (macOS)
      run: |
        cd frontend
        npm run electron:build -- --mac
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        # 签名环境变量
        CSC_LINK: ${{ secrets.APPLE_CERTIFICATE }}
        CSC_KEY_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
        APPLE_ID: ${{ secrets.APPLE_ID }}
        APPLE_ID_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
        APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}

    # ===== 添加公证步骤 =====
    - name: Notarize app
      run: |
        # 查找DMG文件
        DMG_PATH=$(find frontend/dist-electron -name "*.dmg" | head -n 1)
        
        if [ -z "$DMG_PATH" ]; then
          echo "❌ DMG文件未找到"
          exit 1
        fi
        
        echo "📦 开始公证: $DMG_PATH"
        
        # 上传公证
        xcrun notarytool submit "$DMG_PATH" \
          --apple-id "${{ secrets.APPLE_ID }}" \
          --password "${{ secrets.APPLE_PASSWORD }}" \
          --team-id "${{ secrets.APPLE_TEAM_ID }}" \
          --wait
        
        # 附加公证票据
        xcrun stapler staple "$DMG_PATH"
        
        echo "✅ 公证完成"
      env:
        APPLE_ID: ${{ secrets.APPLE_ID }}
        APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
        APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}

    # ===== 清理钥匙串 =====
    - name: Cleanup keychain
      if: always()
      run: |
        security delete-keychain temp.keychain || true
        rm -f certificate.p12

    - name: Upload macOS artifact
      uses: actions/upload-artifact@v4
      with:
        name: macos-build
        path: frontend/dist-electron/*.dmg
        retention-days: 7
```

---

## 🧪 步骤5：本地测试签名

在提交到GitHub之前，先在本地测试：

```bash
# 1. 设置环境变量
export CSC_NAME="Developer ID Application: Your Name (TEAM_ID)"

# 2. 构建应用
cd frontend
npm run electron:build -- --mac

# 3. 验证签名
codesign -dv --verbose=4 "dist-electron/KOOK消息转发系统.app"

# 输出应该包含：
# Authority=Developer ID Application: Your Name (TEAM_ID)
# Signature=adhoc

# 4. 验证Gatekeeper
spctl -a -t exec -vv "dist-electron/KOOK消息转发系统.app"

# 输出应该是：
# accepted
# source=Developer ID
```

---

## 🚀 步骤6：发布签名版本

### 6.1 创建Git标签触发构建

```bash
git tag -a v1.7.0 -m "Release v1.7.0 with code signing"
git push origin v1.7.0
```

### 6.2 监控构建过程

- 访问GitHub Actions页面
- 查看macOS构建日志
- 确认签名和公证步骤成功

### 6.3 测试已签名的应用

下载构建好的DMG文件，测试：

```bash
# 1. 挂载DMG
hdiutil attach KookForwarder_v1.7.0_macOS.dmg

# 2. 验证签名
codesign -dv --verbose=4 "/Volumes/KOOK消息转发系统/KOOK消息转发系统.app"

# 3. 验证公证
spctl -a -t exec -vv "/Volumes/KOOK消息转发系统/KOOK消息转发系统.app"

# 4. 卸载DMG
hdiutil detach "/Volumes/KOOK消息转发系统"
```

如果所有检查通过，用户现在可以直接双击打开应用了！

---

## ❌ 故障排查

### 问题1：证书未找到

**错误信息**：
```
No identity found for signing
```

**解决方法**：
1. 检查证书是否正确安装：`security find-identity -v -p codesigning`
2. 检查electron-builder.yml中的identity是否正确
3. 确认证书未过期

### 问题2：公证失败

**错误信息**：
```
Error: Unable to notarize app
```

**解决方法**：
1. 确认Apple ID和App专用密码正确
2. 确认Team ID正确
3. 检查Apple开发者账号是否有效（未过期）
4. 等待10-30分钟重试（Apple服务器可能延迟）

### 问题3：Entitlements权限不足

**错误信息**：
```
The executable requests XXX entitlement
```

**解决方法**：
在`build/entitlements.mac.plist`中添加对应的权限

### 问题4：签名后应用无法运行

**解决方法**：
1. 检查entitlements是否包含所有必需的权限
2. 尝试禁用library-validation
3. 检查Python后端是否正确打包

---

## 📝 最佳实践

1. **定期更新证书**
   - 证书有效期为1年（随开发者账号续费）
   - 设置日历提醒，提前30天续费

2. **保护密钥安全**
   - P12文件和密码妥善保管
   - 不要提交到Git仓库
   - 仅在GitHub Secrets中存储

3. **测试流程**
   - 每次更新签名配置后都要测试
   - 在不同macOS版本上测试
   - 确保所有功能正常

4. **用户文档**
   - 在README中说明应用已签名
   - 如果未签名，说明安装步骤

---

## 💰 成本预算

| 项目 | 费用 | 周期 |
|------|------|------|
| Apple开发者账号（个人） | $99 | 1年 |
| Apple开发者账号（企业） | $299 | 1年 |
| 代码签名服务（可选） | $50-200 | 一次性 |

**总成本**：$99-$299/年（取决于账号类型）

---

## 🤔 是否需要代码签名？

### 优点：
- ✅ 用户无需"右键→打开"
- ✅ 更专业的用户体验
- ✅ 提升软件可信度
- ✅ 符合Apple安全规范

### 缺点：
- ❌ 需要年费（$99/年）
- ❌ 配置稍复杂
- ❌ 需要等待审核

### 建议：

**如果您打算长期维护该项目**，强烈建议配置代码签名。

**如果只是个人使用或测试**，可以暂时不配置，在README中说明安装方法即可。

---

## 📚 参考资料

- [Apple开发者文档 - 代码签名](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [electron-builder macOS配置](https://www.electron.build/configuration/mac)
- [公证指南](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

---

**配置签名后，您的应用将更加专业和易用！** 🎉

---

*最后更新：2025-10-19*
