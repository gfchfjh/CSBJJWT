# v18.0.0 后端路径错误 - 快速修复指南

**问题**: 下载v18.0.0安装包后，启动时显示"后端路径错误"，应用无法使用

**影响**: 所有v18.0.0 Windows和Linux用户

**状态**: 🔴 Critical - 已修复代码，等待v18.0.1发布

---

## ⚡ 临时解决方案（用户侧）

### 如果您已下载v18.0.0，可以手动修复：

#### Windows用户
1. 解压 `KOOK-Forwarder-v18.0.0-Windows.zip`
2. 打开命令提示符（cmd），进入解压目录
3. 执行以下命令：

```cmd
cd KOOK-Forwarder-v18.0.0-Windows
copy backend\KOOKForwarder\KOOKForwarder.exe backend\kook-forwarder-backend.exe
```

4. 现在可以正常运行安装器

#### Linux用户
1. 解压 `KOOK-Forwarder-v18.0.0-Linux.tar.gz`
2. 打开终端，进入解压目录
3. 执行以下命令：

```bash
cd KOOK-Forwarder-v18.0.0-Linux
cp backend/KOOKForwarder/KOOKForwarder backend/kook-forwarder-backend
chmod +x backend/kook-forwarder-backend
```

4. 现在可以正常运行

---

## ✅ 官方修复（推荐）

### 等待v18.0.1发布

**预计发布时间**: 即将发布

**修复内容**:
- 更新了Electron配置，使用正确的后端路径
- 无需手动操作，直接下载即可使用

**建议**:
- 如果还未下载，请等待v18.0.1
- 如果已下载v18.0.0，可以：
  - 使用上述临时解决方案
  - 或等待v18.0.1重新下载

---

## 🔍 问题原因

**技术细节**（供开发者参考）:

```
Electron配置期望: backend/kook-forwarder-backend
PyInstaller实际: backend/KOOKForwarder/KOOKForwarder

结果: 找不到后端可执行文件 → 启动失败
```

**已修复**:
- 文件: `frontend/electron/main.js`
- 修改: 更新后端路径为 `backend/KOOKForwarder/KOOKForwarder`
- 提交: 已提交到代码库

---

## 📞 需要帮助？

**如果临时方案不起作用**:

1. 检查文件是否存在：
   - Windows: `backend\KOOKForwarder\KOOKForwarder.exe`
   - Linux: `backend/KOOKForwarder/KOOKForwarder`

2. 查看错误日志
3. 在GitHub Issues反馈: https://github.com/gfchfjh/CSBJJWT/issues

---

## 🎯 v18.0.1 将包含

- ✅ 修复后端路径错误
- ✅ 所有v18.0.0的功能
- ✅ 无需手动操作

---

*更新时间: 2025-10-31*  
*请关注GitHub Release获取v18.0.1发布通知*
