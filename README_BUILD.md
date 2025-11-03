# KOOK消息转发系统 v18.0.2 - 构建说明

**版本**: v18.0.2  
**更新日期**: 2025-11-03  
**状态**: 推荐从源码运行

---

## 🚀 推荐运行方式

**v18.0.2 推荐从源码运行**（最稳定、最灵活）：

### 快速启动步骤

```bash
# 1. 克隆仓库
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 2. 安装后端依赖
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r backend\requirements.txt

# 3. 安装前端依赖
cd frontend
npm install

# 4. 启动后端（新窗口）
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 9527 --reload

# 5. 启动前端（新窗口）
cd frontend
npm run dev

# 6. 访问 http://localhost:5173/home
```

详细步骤参考：[QUICK_START_WINDOWS.md](./QUICK_START_WINDOWS.md)

---

## 📦 Electron 打包（高级用户）

### ✅ Linux完整版
```
构建命令: npm run electron:build:linux
输出文件: KOOK消息转发系统.AppImage
```

**使用方法**:
```bash
chmod +x KOOK消息转发系统-16.0.0.AppImage
./KOOK消息转发系统-16.0.0.AppImage
```

---

### ✅ Windows便携版 (128 MB)
```
文件: KOOK-Forwarder-v16.0.0-Windows-Portable.zip
路径: /workspace/frontend/dist-electron/
MD5:  0cc024894dc41b78d64693a01375948e
```

**使用方法**:
```powershell
# 解压ZIP文件
Expand-Archive KOOK-Forwarder-v16.0.0-Windows-Portable.zip

# 运行主程序
cd KOOK-Forwarder-v16.0.0-Windows-Portable\win-unpacked
.\KOOK消息转发系统.exe
```

---

## 📊 构建统计

- **构建平台**: Linux (Ubuntu)
- **构建时间**: ~4分钟
- **安装包数量**: 2个
- **总大小**: 253 MB
- **完成度**: 63% (2/3平台)

---

## 🎯 下一步操作

### 选项1: 使用GitHub Actions构建所有平台 (推荐)

```bash
# 1. 推送代码
git add .
git commit -m "release: v16.0.0"
git push origin main

# 2. 创建版本tag
git tag v16.0.0
git push origin v16.0.0

# 3. 等待自动构建（10-15分钟）
# 访问: https://github.com/your-repo/actions

# 4. 从Releases下载所有平台安装包
```

### 选项2: 手动构建

**Windows** (需在Windows系统):
```bash
python build_all_platforms.py --platform windows
```

**macOS** (需在macOS系统):
```bash
python3 build_all_platforms.py --platform mac
```

---

## 📚 文档

- `跨平台构建指南.md` - 详细构建步骤
- `全平台构建报告.md` - 构建状态总览
- `构建发布总结.md` - 发布准备清单
- `安装包清单.txt` - 安装包信息

---

## ✅ 已完成任务

- ✅ Linux AppImage (完整版)
- ✅ Windows Portable (便携版)
- ✅ 4篇详细教程文档
- ✅ 跨平台构建指南
- ✅ UI深度优化
- ✅ 功能100%实现

---

**© 2025 KOOK Forwarder Team | v16.0.0**
