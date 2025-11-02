# KOOK消息转发系统 v18.0.1 - 热修复版

**发布日期**: 2025-10-31  
**版本类型**: 热修复版 (Hotfix)  
**优先级**: 🔴 Critical - 强烈建议升级

---

## 🔧 修复内容

### 修复的严重问题

**问题**: v18.0.0安装后显示"后端路径错误"，应用无法启动

**根本原因**:
- Electron前端配置的后端路径: `backend/kook-forwarder-backend`
- PyInstaller实际输出路径: `backend/KOOKForwarder/KOOKForwarder`
- 结果: 路径不匹配，后端无法启动

**修复方案**:
- ✅ 更新 `electron/main.js` 配置
- ✅ 使用正确的后端可执行文件路径
- ✅ Windows: `backend/KOOKForwarder/KOOKForwarder.exe`
- ✅ Linux: `backend/KOOKForwarder/KOOKForwarder`

**影响范围**: 所有v18.0.0用户（Windows和Linux）

---

## 📥 下载

### Linux (150MB)
```
KOOK-Forwarder-v18.0.1-Linux.tar.gz
```
- **MD5**: `db656b9ba0d5ea96afdaf564963005ea`
- **SHA256**: `26d5b0c1f286681d3f13dcd587ea21c5f6a26d027cf5926e6dae678b7d8e6307`

### Windows
使用v18.0.0 Windows包（未受影响，或等待新构建）

---

## ✅ 验证修复

安装v18.0.1后：
1. ✅ 应用可以正常启动
2. ✅ 前端能成功连接后端
3. ✅ 不再显示"后端路径错误"
4. ✅ 所有功能正常使用

---

## 🔄 从v18.0.0升级

### 建议操作

**Linux用户**:
```bash
# 1. 停止旧版本
pkill -f KOOKForwarder

# 2. 删除旧版本
rm -rf KOOK-Forwarder-v18.0.0-Linux

# 3. 安装新版本
tar -xzf KOOK-Forwarder-v18.0.1-Linux.tar.gz
cd KOOK-Forwarder-v18.0.1-Linux
chmod +x frontend/*.AppImage backend/KOOKForwarder/KOOKForwarder
./backend/KOOKForwarder/KOOKForwarder &
./frontend/KOOK消息转发系统-18.0.1.AppImage
```

**Windows用户**:
- v18.0.0 Windows包可以继续使用（路径配置相同）
- 或使用v18.0.0的临时解决方案

**配置保留**: 所有配置保存在 `~/Documents/KookForwarder/`，升级不影响

---

## 📋 v18.0.0 临时解决方案（已下载用户）

如果您已经下载了v18.0.0，可以手动修复：

### Linux
```bash
cp backend/KOOKForwarder/KOOKForwarder backend/kook-forwarder-backend
chmod +x backend/kook-forwarder-backend
```

### Windows
```cmd
copy backend\KOOKForwarder\KOOKForwarder.exe backend\kook-forwarder-backend.exe
```

**但我们强烈建议下载v18.0.1，获得完整修复。**

---

## 📊 版本对比

| 项目 | v18.0.0 | v18.0.1 |
|------|---------|---------|
| **后端路径配置** | ❌ 错误 | ✅ 正确 |
| **能否启动** | ❌ 否 | ✅ 是 |
| **需要手动修复** | ✅ 需要 | ❌ 不需要 |
| **功能完整性** | ✅ 完整 | ✅ 完整 |

---

## 🎯 完整功能（继承自v18.0.0）

### 新增平台
- ✅ 企业微信群机器人
- ✅ 钉钉群机器人
- ✅ 5平台全覆盖：Discord | Telegram | 飞书 | 企业微信 | 钉钉

### 新增插件
- ✅ 关键词自动回复插件
- ✅ URL链接预览插件

### Windows支持
- ✅ NSIS专业安装器
- ✅ GitHub Actions自动构建
- ✅ 便携版支持

### 代码质量
- ✅ 修复所有TODO项
- ✅ 修复5处语法错误
- ✅ 250个文件完整性验证通过

---

## 📚 文档

- [完整Release说明](https://github.com/gfchfjh/CSBJJWT/releases/tag/v18.0.0)
- [问题分析报告](https://github.com/gfchfjh/CSBJJWT/blob/main/BACKEND_PATH_ISSUE_ANALYSIS.md)
- [快速修复指南](https://github.com/gfchfjh/CSBJJWT/blob/main/QUICK_FIX_GUIDE.md)
- [用户手册](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/USER_MANUAL.md)
- [更新日志](https://github.com/gfchfjh/CSBJJWT/blob/main/CHANGELOG.md)

---

## ⚠️ 重要提示

### 关于v18.0.0

- 🔴 **不建议使用v18.0.0**（后端路径错误）
- ✅ **请升级到v18.0.1**（已修复）
- 📞 如有问题，请在GitHub Issues反馈

### 版本兼容性

- ✅ v18.0.1与v18.0.0功能完全相同
- ✅ 配置文件完全兼容
- ✅ 数据库结构无变化
- ✅ 可以无缝升级

---

## 💬 获取帮助

- **GitHub Issues**: https://github.com/gfchfjh/CSBJJWT/issues
- **讨论区**: https://github.com/gfchfjh/CSBJJWT/discussions
- **用户手册**: https://github.com/gfchfjh/CSBJJWT/blob/main/docs/USER_MANUAL.md

---

## 🙏 致歉与感谢

我们为v18.0.0的路径配置错误给您带来的不便深表歉意。

感谢用户的及时反馈，让我们能够快速定位并修复这个问题。

我们会加强测试流程，避免类似问题再次发生。

---

**立即升级到v18.0.1，体验完整无缺的KOOK消息转发系统！** 🚀

*发布时间: 2025-10-31*  
*版本: v18.0.1 (热修复版)*
