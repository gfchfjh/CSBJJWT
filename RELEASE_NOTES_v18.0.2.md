# KOOK消息转发系统 v18.0.2 - 紧急修复版

**发布日期**: 2025-11-02  
**版本类型**: 紧急修复版 (Critical Hotfix)  
**优先级**: 🔴 P0 Critical - 必须升级

---

## 🔧 修复内容

### 修复的Critical问题

**问题**: v18.0.1的backendCwd工作目录路径设置错误

**根本原因**:
- **错误设置**: `backendCwd = path.join(appPath, 'backend');`
- **正确设置**: `backendCwd = path.join(appPath, 'backend', 'KOOKForwarder');`
- **后果**: 后端无法找到`_internal/`目录和依赖库，启动失败

**修复方案**:
```javascript
// v18.0.1 (错误)
backendCwd = path.join(appPath, 'backend');

// v18.0.2 (正确)
backendCwd = path.join(appPath, 'backend', 'KOOKForwarder');
```

**影响范围**: 所有v18.0.1和v18.0.0用户（Windows和Linux）

**严重程度**: 🔴 P0 Critical

---

## 📥 下载

### Linux (150MB)
```
KOOK-Forwarder-v18.0.2-Linux.tar.gz
```
- **MD5**: `e6180a4641745cef3edd1eee2a71d754`
- **SHA256**: `a76fa559e86d3b0c2e4e2dfcad683062b5d6bf8a6c7fcb0209dbd61625897e0a`

### Windows
GitHub Actions正在自动构建，请稍候或使用现有v18.0.1包

---

## ✅ 验证修复

安装v18.0.2后：
1. ✅ 应用可以正常启动
2. ✅ 后端成功加载所有依赖库
3. ✅ 不再显示"路径错误"或"找不到模块"
4. ✅ 所有功能正常使用

---

## 🔄 从v18.0.1升级

### Linux用户

```bash
# 1. 停止旧版本
pkill -f KOOKForwarder

# 2. 删除旧版本
rm -rf KOOK-Forwarder-v18.0.1-Linux

# 3. 安装新版本
tar -xzf KOOK-Forwarder-v18.0.2-Linux.tar.gz
cd KOOK-Forwarder-v18.0.2-Linux
chmod +x frontend/*.AppImage backend/KOOKForwarder/KOOKForwarder
./backend/KOOKForwarder/KOOKForwarder &
./frontend/KOOK消息转发系统-18.0.2.AppImage
```

### Windows用户

等待GitHub Actions完成Windows构建，或使用临时方案

**配置保留**: 所有配置保存在 `~/Documents/KookForwarder/`，升级不影响

---

## 📊 版本对比

| 项目 | v18.0.1 | v18.0.2 |
|------|---------|---------|
| **backendCwd路径** | ❌ 错误 | ✅ 正确 |
| **能否启动** | ❌ 否 | ✅ 是 |
| **依赖库加载** | ❌ 失败 | ✅ 成功 |
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
- ✅ **修复后端可执行文件路径** (v18.0.1)
- ✅ **修复backendCwd工作目录路径** (v18.0.2) **新增**

---

## 📚 文档

- [问题分析报告](https://github.com/gfchfjh/CSBJJWT/blob/main/BACKEND_PATH_ISSUE_ANALYSIS.md)
- [用户手册](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/USER_MANUAL.md)
- [更新日志](https://github.com/gfchfjh/CSBJJWT/blob/main/CHANGELOG.md)

---

## ⚠️ 重要提示

### 版本建议

- 🔴 **不建议使用v18.0.0和v18.0.1**（路径配置错误）
- ✅ **请升级到v18.0.2**（已完全修复）

### 版本历史

| 版本 | 状态 | 问题 |
|------|------|------|
| v18.0.2 | ✅ 推荐 | 无 |
| v18.0.1 | ❌ 已弃用 | backendCwd路径错误 |
| v18.0.0 | ❌ 已删除 | 后端可执行文件路径错误 |

### 版本兼容性

- ✅ v18.0.2与v18.0.0/v18.0.1功能完全相同
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

我们为v18.0.1的工作目录路径错误给您带来的不便深表歉意。

感谢用户的及时反馈，让我们能够快速定位并修复这个问题。

我们会加强测试流程，确保未来版本的稳定性。

---

**立即升级到v18.0.2，体验完全修复的KOOK消息转发系统！** 🚀

*发布时间: 2025-11-02*  
*版本: v18.0.2 (紧急修复版)*
