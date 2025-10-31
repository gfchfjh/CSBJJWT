# Windows安装包构建指南

**状态**: 前端代码已构建完成 ✅  
**限制**: Linux环境无法直接构建Windows安装包（需要Wine）  
**解决方案**: 在Windows环境下完成最后的打包步骤  

---

## 当前构建状态

### ✅ 已完成
- [x] 前端代码构建 (`npm run build`)
- [x] 所有依赖安装
- [x] 配置文件准备
- [x] 图标文件准备

### ⏸️ 待在Windows环境完成
- [ ] electron-builder打包
- [ ] NSIS安装程序生成
- [ ] 代码签名（可选）

---

## 方案一：在Windows上完成构建（推荐）

### 前置要求
- Windows 10/11（x64）
- Node.js 18+ 
- Git

### 步骤

#### 1. 克隆代码
```bash
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT
```

#### 2. 安装前端依赖
```bash
cd frontend
npm install --legacy-peer-deps
npm install -D sass-embedded --legacy-peer-deps
```

#### 3. 构建前端
```bash
npm run build
```

#### 4. 构建Windows安装包
```bash
# 方式A: 使用完整配置（包含后端和Redis）
npm run electron:build:win

# 方式B: 使用简化配置（仅前端）
npx electron-builder --config electron-builder-simple.yml --win --x64
```

#### 5. 查看输出
```bash
# 安装包位置
dir dist-electron\*KOOK*.exe
```

---

## 方案二：在Linux上使用Wine

### 安装Wine
```bash
# Ubuntu/Debian
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install wine wine32 wine64

# 验证
wine --version
```

### 构建
```bash
cd /workspace/frontend
npx electron-builder --config electron-builder-simple.yml --win --x64
```

---

## 方案三：使用GitHub Actions自动构建

### 创建工作流
```yaml
# .github/workflows/build-windows.yml
name: Build Windows

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

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
          npm install --legacy-peer-deps
          npm install -D sass-embedded --legacy-peer-deps
      
      - name: Build frontend
        run: |
          cd frontend
          npm run build
      
      - name: Build installer
        run: |
          cd frontend
          npx electron-builder --win --x64
        env:
          GH_TOKEN: \${{ secrets.GITHUB_TOKEN }}
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: frontend/dist-electron/*.exe
```

### 触发构建
```bash
# 创建tag触发
git tag -a v17.0.0 -m "Release v17.0.0"
git push origin v17.0.0

# 或在GitHub网页上手动触发
```

---

## 输出文件说明

### 成功构建后会生成
```
frontend/dist-electron/
├── KOOK消息转发系统-v17.0.0-Frontend-win-x64.exe  # NSIS安装程序
├── win-unpacked/                                    # 未打包的应用
│   ├── KOOK消息转发系统.exe                        # 主程序
│   ├── resources/                                   # 资源文件
│   └── ...
└── builder-effective-config.yaml                    # 有效配置
```

### 文件大小预期
- **安装程序**: 约100-120MB
- **解压后**: 约150-180MB

---

## 当前构建产物

### 可用文件（已在Linux上生成）
```
/workspace/frontend/dist/              # 前端构建产物（已完成）
├── index.html
├── assets/
│   ├── index-*.js     (2.4MB gzip后800KB)
│   ├── index-*.css    (382KB gzip后54KB)
│   └── ...
└── ...

/workspace/build/                       # 资源文件（已准备）
├── icon-512.png                       # 应用图标
├── icon.png
├── LICENSE
└── ...
```

### 可以直接复制到Windows环境使用
```bash
# 打包dist目录和配置文件
cd /workspace
tar -czf frontend-build-ready.tar.gz \
  frontend/dist \
  frontend/electron \
  frontend/package.json \
  frontend/electron-builder*.yml \
  build/

# 在Windows上解压后直接打包
tar -xzf frontend-build-ready.tar.gz
cd frontend
npm install electron-builder --save-dev
npx electron-builder --win
```

---

## 常见问题

### Q1: 提示缺少图标？
A: 确保 `/build/icon-512.png` 存在且尺寸正确

### Q2: 打包失败提示权限错误？
A: 以管理员身份运行PowerShell/CMD

### Q3: 安装包太大？
A: 参考 `BUILD_IMPROVEMENTS.md` 中的优化建议

### Q4: 需要代码签名吗？
A: 不必须，但签名后用户体验更好（无"未知发布者"警告）

---

## 代码签名（可选）

### 获取证书
1. 从CA购买代码签名证书（如DigiCert、Sectigo）
2. 导出为PFX格式
3. 保存到安全位置

### 配置签名
```yaml
# electron-builder.yml
win:
  certificateFile: path/to/certificate.pfx
  certificatePassword: ${CERT_PASSWORD}
  signDlls: true
```

### 签名命令
```bash
# 设置密码环境变量
set CERT_PASSWORD=your_password

# 构建并签名
npx electron-builder --win --x64
```

---

## 测试清单

### 安装测试
- [ ] 双击exe可以安装
- [ ] 安装到自定义目录
- [ ] 创建桌面快捷方式
- [ ] 创建开始菜单项

### 功能测试
- [ ] 应用可以正常启动
- [ ] 所有页面可以访问
- [ ] 前端功能正常
- [ ] 没有控制台错误

### 卸载测试
- [ ] 可以正常卸载
- [ ] 询问是否保留数据
- [ ] 清理桌面快捷方式

---

## 下一步

1. **立即**: 将代码同步到Windows环境
2. **10分钟**: 在Windows上完成构建
3. **测试**: 安装并验证功能
4. **发布**: 上传到GitHub Releases

---

**当前状态总结**:
- ✅ 前端代码已完整构建
- ✅ 所有资源文件已准备
- ⏸️ 需要在Windows环境或使用GitHub Actions完成最后打包
- 📦 预计Windows安装包大小：100-120MB

**建议**: 使用GitHub Actions自动构建，最方便且无需本地环境。
