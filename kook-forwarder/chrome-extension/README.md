# KOOK Cookie 导出扩展

**版本**: v1.2.0（兼容KOOK转发系统v6.7.0）  
**更新**: 2025-10-27

## 简介

这是一个Chrome浏览器扩展，用于快速导出KOOK网站的Cookie，供KOOK消息转发系统使用。

**v6.7.0系统已支持**：
- ✅ 拖拽上传Cookie文件（大区域动画）
- ✅ 3种格式智能解析（JSON/Netscape/Header）
- ✅ 实时解析预览
- ✅ 导入帮助指南

## 功能特性

- ✅ 一键导出KOOK Cookie（JSON格式）
- ✅ 自动检测是否在KOOK网站
- ✅ 自动复制到剪贴板
- ✅ 支持 Chrome、Edge、Brave 等 Chromium 内核浏览器
- ✅ 5秒完成，操作简单

## 安装方法

### 方法1：开发者模式安装（推荐）

1. 打开Chrome浏览器，访问 `chrome://extensions/`
2. 开启右上角的「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择 `chrome-extension` 文件夹
5. 安装完成！

### 方法2：打包安装

1. 在扩展管理页面点击「打包扩展程序」
2. 选择 `chrome-extension` 文件夹
3. 生成 `.crx` 文件
4. 拖拽到扩展管理页面安装

## 使用方法

### 第一步：打开KOOK网站并登录

1. 访问 https://www.kookapp.cn
2. 登录您的KOOK账号

### 第二步：导出Cookie

1. 点击浏览器工具栏的扩展图标
2. 点击「导出Cookie」按钮
3. 等待提示「Cookie已复制到剪贴板」

### 第三步：粘贴到KOOK转发系统

1. 打开KOOK消息转发系统
2. 在登录页面选择「Cookie导入」
3. 粘贴刚才复制的内容
4. 点击「验证并登录」

## 常见问题

### Q: 提示「请先打开KOOK网站」？
**A**: 确保当前浏览器标签页是 KOOK 网站（www.kookapp.cn），而不是其他网站。

### Q: 提示「未找到Cookie」？
**A**: 您可能未登录KOOK，请先登录后再导出。

### Q: 导出的Cookie无效？
**A**: Cookie有时效性，请在导出后立即使用。如果失败，请重新登录KOOK并导出。

### Q: 支持其他浏览器吗？
**A**: 支持所有基于Chromium的浏览器，包括：
- Google Chrome
- Microsoft Edge
- Brave
- Opera
- 360极速浏览器
- QQ浏览器

### Q: 安全吗？
**A**: 
- 扩展仅在本地运行，不上传任何数据
- 仅读取KOOK网站的Cookie
- 源代码完全开源，可审查

## 技术说明

### Cookie格式

导出的Cookie为JSON数组格式：

\`\`\`json
[
  {
    "name": "token",
    "value": "xxxx",
    "domain": ".kookapp.cn",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "sameSite": "None",
    "expirationDate": 1735000000
  },
  ...
]
\`\`\`

### 权限说明

扩展需要以下权限：

- `cookies`: 读取Cookie数据
- `activeTab`: 获取当前标签页信息
- `clipboardWrite`: 复制到剪贴板
- `host_permissions`: 仅限KOOK域名

## 更新日志

### v1.1.0 (2025-10-26)
- ✨ 增强错误提示
- ✨ 添加导出统计
- ✨ 优化用户体验
- 🐛 修复Edge浏览器兼容性问题

### v1.0.0 (2025-10-12)
- 🎉 首次发布
- ✨ 基础Cookie导出功能
- ✨ 自动检测KOOK网站
- ✨ 剪贴板复制

## 开发

### 文件结构

\`\`\`
chrome-extension/
├── manifest.json       # 扩展清单
├── popup.html          # 弹窗页面
├── popup.js            # 弹窗脚本
├── popup.css           # 弹窗样式
├── icon-16.png         # 图标 16x16
├── icon-48.png         # 图标 48x48
├── icon-128.png        # 图标 128x128
└── README.md           # 说明文档
\`\`\`

### 本地开发

1. 修改代码
2. 打开 `chrome://extensions/`
3. 点击扩展卡片的「重新加载」按钮
4. 测试修改效果

## 许可证

MIT License

## 联系方式

- GitHub: https://github.com/gfchfjh/CSBJJWT
- Issues: https://github.com/gfchfjh/CSBJJWT/issues
