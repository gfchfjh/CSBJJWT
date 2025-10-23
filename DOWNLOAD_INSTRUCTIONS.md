# 📥 Windows安装包下载指南

## 🎯 快速下载

### Windows用户（推荐）

**直接下载链接：**
```
https://github.com/gfchfjh/CSBJJWT/releases/download/v1.14.0/KOOK.Setup.1.13.3.exe
```

**或者访问Release页面：**
1. 打开 https://github.com/gfchfjh/CSBJJWT/releases/latest
2. 在 **Assets** 区域找到 `KOOK.Setup.1.13.3.exe`
3. 点击文件名下载

---

## 📦 所有平台下载

| 平台 | 文件名 | 大小 | 下载链接 |
|------|--------|------|----------|
| 🪟 **Windows** | KOOK.Setup.1.13.3.exe | 93.2 MB | [点击下载](https://github.com/gfchfjh/CSBJJWT/releases/download/v1.14.0/KOOK.Setup.1.13.3.exe) |
| 🐧 **Linux** | KOOK.-1.13.3.AppImage | 130 MB | [点击下载](https://github.com/gfchfjh/CSBJJWT/releases/download/v1.14.0/KOOK.-1.13.3.AppImage) |
| 🍎 **macOS** | 暂不可用 | - | 请使用Docker版本 |
| 🐳 **Docker** | - | - | `docker pull ghcr.io/gfchfjh/csbjjwt:latest` |

---

## 🚀 安装步骤

### Windows安装
```
1. 下载 KOOK.Setup.1.13.3.exe
2. 双击运行安装程序
3. 按照安装向导操作
4. 完成后启动应用
5. 按照配置向导完成初始设置
```

### Linux安装
```bash
# 下载AppImage
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v1.14.0/KOOK.-1.13.3.AppImage

# 赋予执行权限
chmod +x KOOK.-1.13.3.AppImage

# 运行
./KOOK.-1.13.3.AppImage
```

### Docker部署
```bash
# 方式1: 使用docker命令
docker run -d -p 9527:9527 -p 9528:9528 \
  -v $(pwd)/data:/app/data \
  --name kook-forwarder \
  ghcr.io/gfchfjh/csbjjwt:latest

# 方式2: 使用docker-compose
docker-compose -f docker-compose.standalone.yml up -d

# 方式3: 开发模式
docker-compose -f docker-compose.dev.yml up -d
```

---

## 🌍 国内加速下载

如果GitHub下载速度慢，可以使用以下镜像：

### 方式1: 使用ghproxy镜像
```bash
# Windows
https://mirror.ghproxy.com/https://github.com/gfchfjh/CSBJJWT/releases/download/v1.14.0/KOOK.Setup.1.13.3.exe

# Linux
https://mirror.ghproxy.com/https://github.com/gfchfjh/CSBJJWT/releases/download/v1.14.0/KOOK.-1.13.3.AppImage
```

### 方式2: 使用GitHub CLI（推荐开发者）
```bash
# 安装gh cli (https://cli.github.com/)
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: 参考官网

# 下载Windows安装包
gh release download v1.14.0 -R gfchfjh/CSBJJWT -p "*.exe"

# 下载Linux安装包
gh release download v1.14.0 -R gfchfjh/CSBJJWT -p "*.AppImage"
```

### 方式3: 使用代理
```bash
# 使用代理加速（需要先配置代理）
export https_proxy=http://127.0.0.1:7890
wget https://github.com/gfchfjh/CSBJJWT/releases/download/v1.14.0/KOOK.Setup.1.13.3.exe
```

---

## ❓ 常见问题

### Q: 找不到下载链接？
**A:** 点击Release页面的 "Assets" 展开区域，然后就能看到所有可下载文件。

### Q: 下载后提示病毒？
**A:** 这是Windows Defender的误报，因为应用没有代码签名证书。解决方法：
1. 右键文件 → 属性
2. 勾选"解除锁定"
3. 点击"应用"

### Q: 双击无法运行？
**A:** Windows可能阻止了未签名的应用，解决方法：
1. 右键文件 → 以管理员身份运行
2. 或在Windows安全中心添加信任

### Q: Linux下没有图形界面？
**A:** AppImage需要图形环境，如果是服务器请使用Docker版本：
```bash
docker run -d -p 9527:9527 ghcr.io/gfchfjh/csbjjwt:latest
```

### Q: macOS版本什么时候发布？
**A:** 需要购买Apple开发者证书进行代码签名，暂时请使用Docker版本。

---

## 🔐 文件校验

为了确保下载的文件完整性，可以验证SHA256哈希值：

### Windows (v1.14.0)
```
SHA256: d837663e034c46f26a4c6cd77975826d349ee9ebb176bb048b5f5ab3d010ccd7
文件名: KOOK.Setup.1.13.3.exe
```

### Linux (v1.14.0)
```
SHA256: bad131f72be604c307358c65471f75508651ce5125c79517275325a484224020
文件名: KOOK.-1.13.3.AppImage
```

**验证方法：**
```bash
# Windows (PowerShell)
Get-FileHash KOOK.Setup.1.13.3.exe -Algorithm SHA256

# Linux/macOS
sha256sum KOOK.-1.13.3.AppImage
```

---

## 📞 获取帮助

如果下载或安装遇到问题，请：
1. 查看 [完整用户手册](docs/用户手册.md)
2. 查看 [常见问题FAQ](docs/FAQ.md)
3. 提交 [Issue](https://github.com/gfchfjh/CSBJJWT/issues/new)
4. 加入交流群（见README）

---

## 🔄 版本更新

**当前版本：** v1.14.0  
**发布日期：** 2025-10-23  
**更新日志：** [CHANGELOG_v1.14.0.md](CHANGELOG_v1.14.0.md)

**检查更新：**
应用内置了自动更新检查功能，新版本发布后会自动提示。

---

## 💡 提示

- ✅ 推荐使用**最新版本**以获得最佳体验和安全性
- ✅ 首次安装后请完成**配置向导**
- ✅ 建议定期**备份配置文件**（位于用户文档目录）
- ✅ 遇到问题先查看**日志文件**（应用内可查看）

---

**祝您使用愉快！如果觉得有用，请给项目一个⭐Star！**
