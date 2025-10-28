# KOOK Cookie导出助手 - Chrome扩展

> ✅ P0-3深度优化：一键导出KOOK Cookie到剪贴板

## 功能特性

### v2.0 增强版
- ✅ **自动检测登录状态** - 实时显示KOOK登录状态和Cookie数量
- ✅ **一键导出** - 点击按钮即可将Cookie复制到剪贴板
- ✅ **智能验证** - 自动检查关键Cookie是否存在
- ✅ **详细信息** - 可查看Cookie详情和统计信息
- ✅ **应用状态检测** - 自动检测转发系统是否运行
- ✅ **美化界面** - 现代化设计，操作更直观
- ✅ **快捷键支持** - `Ctrl+Shift+K` (Windows/Linux) / `Cmd+Shift+K` (macOS)

## 安装方法

### 方式1: 开发者模式安装（推荐）

1. 打开Chrome浏览器
2. 访问 `chrome://extensions/`
3. 开启右上角的"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择本项目的 `chrome-extension` 目录
6. 完成！扩展已安装

### 方式2: 打包安装

```bash
# 将扩展打包为.crx文件
chrome://extensions/ → 打包扩展程序 → 选择chrome-extension目录
```

## 使用步骤

### 第1步：登录KOOK
1. 访问 https://www.kookapp.cn
2. 使用邮箱或手机号登录
3. 确保登录成功

### 第2步：导出Cookie
1. 点击Chrome工具栏的扩展图标
2. 扩展会自动检测登录状态
3. 看到"✅ 已检测到KOOK登录"后，点击"📋 一键导出Cookie"
4. Cookie已自动复制到剪贴板

### 第3步：导入到转发系统
1. 打开KOOK消息转发系统（可点击扩展中的"立即打开转发系统"按钮）
2. 点击"添加账号"
3. 选择"粘贴Cookie"
4. 按 `Ctrl+V` 粘贴
5. 点击"验证并添加"

## 快捷键

- **Ctrl+Shift+K** (Windows/Linux)
- **Cmd+Shift+K** (macOS)

随时打开Cookie导出助手

## 故障排查

### ❌ 显示"未检测到KOOK登录"

**原因：**
- 未登录KOOK
- Cookie已过期
- 浏览器清除了Cookie

**解决：**
1. 访问 https://www.kookapp.cn 重新登录
2. 点击扩展中的"🔄 刷新登录状态"按钮
3. 确保允许浏览器保存Cookie

### ⚠️ 显示"包含关键Cookie: ⚠️ 否"

**原因：**
- Cookie不完整，可能无法正常使用

**解决：**
1. 退出KOOK账号
2. 清除浏览器缓存和Cookie
3. 重新登录KOOK
4. 再次导出Cookie

### 📋 复制失败

**原因：**
- 浏览器未授予剪贴板权限

**解决：**
1. 在 `chrome://extensions/` 中找到本扩展
2. 点击"详情"
3. 确认已授予"剪贴板"权限
4. 刷新页面后重试

## 技术细节

### 权限说明

| 权限 | 用途 |
|------|------|
| `cookies` | 读取KOOK Cookie |
| `clipboardWrite` | 将Cookie复制到剪贴板 |
| `activeTab` | 访问当前标签页 |
| `storage` | 保存用户偏好设置 |
| `host_permissions` | 访问KOOK和本地转发系统 |

### Cookie格式

导出的Cookie为标准JSON数组格式：

```json
[
  {
    "name": "cookie_name",
    "value": "cookie_value",
    "domain": ".kookapp.cn",
    "path": "/",
    "expires": 1735660800,
    "httpOnly": true,
    "secure": true,
    "sameSite": "lax"
  },
  ...
]
```

### 安全性

- ✅ **本地处理** - 所有Cookie处理均在本地完成
- ✅ **不上传** - 不会将Cookie上传到任何服务器
- ✅ **加密传输** - 仅通过剪贴板传输
- ✅ **即时清除** - 粘贴使用后建议立即清除剪贴板

## 更新日志

### v2.0.0 (2025-10-28) - P0-3深度优化
- ✅ 全新UI设计，更加美观和直观
- ✅ 自动检测转发系统运行状态
- ✅ 智能验证关键Cookie
- ✅ 添加Cookie详情查看功能
- ✅ 优化错误提示和引导流程
- ✅ 添加加载动画和过渡效果
- ✅ 支持快捷键 `Ctrl+Shift+K`
- ✅ 改进错误处理和重试机制

### v1.0.0 (2025-10-01)
- ✨ 初始版本发布
- ✅ 基础Cookie导出功能
- ✅ 登录状态检测

## 反馈与支持

- 🐛 [报告问题](https://github.com/gfchfjh/CSBJJWT/issues)
- 📖 [查看文档](https://github.com/gfchfjh/CSBJJWT/blob/main/docs/tutorials/02-Cookie获取详细教程.md)
- ⭐ [GitHub主页](https://github.com/gfchfjh/CSBJJWT)

## 许可证

MIT License - 详见 [LICENSE](../LICENSE)

---

**开发团队**: KOOK Forwarder Team  
**项目主页**: https://github.com/gfchfjh/CSBJJWT
