# 🎯 一键安装使用 - 最简化指南

> **最快5分钟即可完成安装并开始使用！**

---

## ⚡ 超快速安装（选择一种）

### Windows用户

```powershell
# 方式1: 下载预编译包（推荐）⭐⭐⭐⭐⭐
访问: https://github.com/gfchfjh/CSBJJWT/releases/latest
下载: KookForwarder-Setup-*.exe
双击安装 → 完成！

# 方式2: 自动安装脚本（如没有预编译包）⭐⭐⭐⭐⭐
# 右键管理员PowerShell，运行：
Set-ExecutionPolicy Bypass -Scope Process -Force; `
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/install_enhanced.bat'))
```

### macOS用户

```bash
# 方式1: 下载预编译包（推荐）⭐⭐⭐⭐⭐
访问: https://github.com/gfchfjh/CSBJJWT/releases/latest
下载: KookForwarder-*.dmg
拖拽安装 → 完成！

# 方式2: 一键安装脚本⭐⭐⭐⭐
curl -fsSL https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/install.sh | bash
cd CSBJJWT && ./start.sh
```

### Linux用户

```bash
# 方式1: 下载预编译包（推荐）⭐⭐⭐⭐⭐
wget https://github.com/gfchfjh/CSBJJWT/releases/latest/download/KookForwarder-*.AppImage
chmod +x KookForwarder-*.AppImage
./KookForwarder-*.AppImage

# 方式2: Docker部署⭐⭐⭐⭐
docker run -d -p 9527:9527 -v $(pwd)/data:/app/data ghcr.io/gfchfjh/csbjjwt:latest

# 方式3: 一键安装脚本⭐⭐⭐⭐
curl -fsSL https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/install.sh | bash
cd CSBJJWT && ./start.sh
```

---

## ✅ 验证安装

```bash
# 检查服务
curl http://localhost:9527/health

# 应该返回
{"status": "ok"}

# ✅ 成功！
```

---

## 📝 快速配置

启动后按5步向导配置（3分钟）：

```
1. 欢迎页 → 开始配置
2. 登录KOOK → 使用Cookie或密码
3. 选择服务器 → 勾选要监听的频道
4. 配置Bot → Discord/Telegram/飞书
5. 完成 → 启动服务
```

**获取Cookie**:
```
1. 浏览器访问 kookapp.cn
2. F12 → Application → Cookies
3. 复制粘贴到应用
```

**配置Discord**:
```
Discord服务器 → 设置 → 集成 → Webhooks → 创建
复制URL → 粘贴到应用 → 测试
```

---

## 🎉 开始使用

```
1. 点击"启动服务"
2. 在KOOK发消息
3. 在Discord/Telegram/飞书看到转发
4. 成功！🎉
```

---

## 🆘 遇到问题？

- 📖 [详细安装指南](docs/一键安装指南.md)
- ❓ [常见问题](docs/FAQ.md)
- 🐛 [提交Bug](https://github.com/gfchfjh/CSBJJWT/issues)

---

**总耗时**: 预编译包2分钟 | 自动安装5-10分钟 | Docker 3分钟

**成功率**: 95%+ (按照步骤操作)

**享受自动化！** 🚀
