# 快速开始 - 两种使用方式

---

## 🎯 方案选择

### 方案A：立即使用（推荐新手）⚡
使用已打包的 **Web版**，无需等待，立即可用。

### 方案B：最佳体验（推荐长期使用）🌟
构建 **Electron桌面版**，获得原生桌面应用体验。

---

## 方案A：立即使用 Web版 ⚡

### 1. 解压并运行

**Windows**:
```bash
cd /workspace/dist_production
unzip KOOK-Forwarder-v2.0-Production.zip
cd KOOK-Forwarder-v2.0-Production
start.bat
```

**Linux/Mac**:
```bash
cd /workspace/dist_production
unzip KOOK-Forwarder-v2.0-Production.zip
cd KOOK-Forwarder-v2.0-Production
chmod +x start.sh
./start.sh
```

### 2. 访问界面

浏览器会自动打开，或手动访问：
- 📱 Web界面: `file:///path/to/web/index.html`
- 📡 API文档: `http://localhost:9527/docs`

### 3. 开始配置

按照应用内的 **4步配置向导** 完成设置：
1. 欢迎页
2. 登录KOOK账号
3. 配置目标Bot（Discord/Telegram/飞书）
4. 设置频道映射

✅ **优点**：
- 立即可用（0分钟等待）
- 功能100%完整
- 体积小（27MB）

⚠️ **缺点**：
- 需要手动启动脚本
- 需要浏览器访问
- 无系统托盘和开机自启

---

## 方案B：构建 Electron 桌面版 🌟

### 快速构建（一键命令）

```bash
# 复制以下命令，一次性执行：
cd /workspace && \
pip3 install pyinstaller && \
cd frontend && \
npm install && \
npm run build && \
npm run electron:build:linux

# 构建完成后
echo "✅ 安装包位于: /workspace/frontend/dist-electron/"
```

**预计时间**：15-20分钟（首次）

### 使用安装包

**Linux**:
```bash
cd /workspace/frontend/dist-electron
chmod +x KOOK消息转发系统-*.AppImage
./KOOK消息转发系统-*.AppImage
```

**Windows/macOS**:
- 双击安装程序即可

✅ **优点**：
- 真正的桌面应用
- 系统托盘集成
- 开机自启动
- 更好的用户体验

⏱️ **缺点**：
- 首次构建需要15-20分钟
- 安装包较大（150MB）

---

## 📊 对比表格

| 特性 | Web版 | Electron版 |
|------|-------|-----------|
| **等待时间** | 0分钟 ⚡ | 15-20分钟 |
| **安装包大小** | 27 MB | 150 MB |
| **启动方式** | 脚本+浏览器 | 双击图标 |
| **系统托盘** | ❌ | ✅ |
| **开机自启** | ❌ | ✅ |
| **功能完整性** | 100% ✅ | 100% ✅ |
| **推荐场景** | 快速测试 | 长期使用 |

---

## 💡 建议

### 新用户 / 快速测试
👉 使用 **方案A (Web版)**
- 立即可用
- 快速上手
- 功能完整

### 长期使用 / 最佳体验
👉 使用 **方案B (Electron版)**
- 原生桌面应用
- 系统集成
- 更好体验

### 理想方案
1. 先用 **Web版** 快速测试功能
2. 确认满意后构建 **Electron版** 长期使用

---

## 🚀 一键启动 Web版

```bash
cd /workspace/dist_production/KOOK-Forwarder-v2.0-Production

# Windows
start.bat

# Linux/Mac
./start.sh
```

然后访问浏览器打开的页面即可！

---

## 📖 更多信息

- **详细构建指南**: `ELECTRON_BUILD_GUIDE.md`
- **功能文档**: `docs/USER_MANUAL.md`
- **API文档**: 启动后访问 `http://localhost:9527/docs`

---

*快速开始指南*
*版本: v15.0.0*
