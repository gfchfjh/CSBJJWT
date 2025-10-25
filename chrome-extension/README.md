# KOOK Cookie导出工具 - Chrome扩展

## 简介

一键导出KOOK Cookie到剪贴板，配合KOOK消息转发系统使用。

## 功能特性

- ✅ **一键导出** - 点击即可将Cookie复制到剪贴板
- ✅ **自动验证** - 自动检测Cookie有效性和数量
- ✅ **智能识别** - 自动判断当前页面是否为KOOK
- ✅ **使用统计** - 记录导出次数和最后导出时间
- ✅ **格式化输出** - 输出格式化的JSON，方便阅读
- ✅ **安全提示** - 提醒用户Cookie的重要性

## 安装方法

### 方式1：Chrome应用商店（推荐）

*待发布*

### 方式2：开发者模式加载

1. 下载本扩展文件夹
2. 打开Chrome浏览器，访问 `chrome://extensions/`
3. 打开右上角的"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择本扩展文件夹

## 使用方法

1. **登录KOOK**
   - 打开 https://www.kookapp.cn/
   - 登录你的KOOK账号

2. **导出Cookie**
   - 点击浏览器工具栏的扩展图标 🍪
   - 点击"导出Cookie到剪贴板"按钮
   - Cookie已自动复制到剪贴板

3. **使用Cookie**
   - 打开KOOK消息转发系统
   - 在添加账号页面选择"Cookie导入"
   - 粘贴Cookie（Ctrl+V）
   - 点击"验证并添加"

## 截图

### 主界面

```
┌────────────────────────────────┐
│   🍪 KOOK Cookie导出            │
│        v1.0.0                  │
├────────────────────────────────┤
│                                │
│   ✅ 检测到 15 个Cookie         │
│      可以导出                   │
│                                │
│   检测到Cookie数量              │
│        15                      │
│                                │
│   ┌──────────┬──────────┐     │
│   │导出次数   │最后导出   │     │
│   │   3      │ 2分钟前   │     │
│   └──────────┴──────────┘     │
│                                │
│   [📋 导出Cookie到剪贴板]       │
│                                │
│   💡 使用说明：                 │
│   1. 确保已登录KOOK网页版       │
│   2. 点击"导出Cookie"按钮       │
│   3. 在软件中粘贴Cookie         │
│                                │
│   ⚠️ Cookie包含登录凭证，       │
│      请妥善保管，切勿泄露       │
└────────────────────────────────┘
```

## 技术细节

### 权限说明

- `cookies` - 读取Cookie
- `activeTab` - 获取当前标签页URL
- `clipboardWrite` - 复制到剪贴板
- `storage` - 存储使用统计
- `host_permissions` - 访问KOOK域名

### 文件结构

```
chrome-extension/
├── manifest.json          # 扩展清单
├── popup.html            # 弹出窗口HTML
├── popup.js              # 弹出窗口逻辑
├── background.js         # 后台服务
├── content-script.js     # 内容脚本
├── icons/                # 图标文件
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md             # 本文件
```

### 输出格式

```json
[
  {
    "name": "cookie_name",
    "value": "cookie_value",
    "domain": ".kookapp.cn",
    "path": "/",
    "secure": true,
    "httpOnly": false,
    "expirationDate": 1735660800
  }
]
```

## 常见问题

### Q: 导出失败怎么办？

A: 请确保：
1. 已在KOOK网页版登录
2. 在kookapp.cn域名下使用
3. 浏览器允许访问Cookie

### Q: Cookie包含哪些信息？

A: Cookie包含：
- 会话ID
- 用户认证Token
- 其他登录凭证

**重要：请勿将Cookie分享给他人！**

### Q: Cookie有效期多久？

A: Cookie有效期由KOOK服务器设置，通常为7-30天。

### Q: 支持哪些浏览器？

A: 目前仅支持Chrome和基于Chromium的浏览器（Edge、Brave等）。

## 更新日志

### v1.0.0 (2025-10-25)

- 🎉 首次发布
- ✅ 支持一键导出Cookie
- ✅ 自动验证Cookie有效性
- ✅ 使用统计功能
- ✅ 现代化UI设计

## 开发者

KOOK Forwarder Team

## 许可证

MIT License

## 反馈

- GitHub Issues: https://github.com/gfchfjh/CSBJJWT/issues
- Email: support@example.com

## 免责声明

本扩展仅供个人学习和研究使用。使用本扩展导出Cookie可能违反KOOK服务条款，请在获得授权的情况下使用。开发者不承担任何法律责任。
