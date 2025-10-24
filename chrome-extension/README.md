# KOOK消息转发系统 - Cookie导出浏览器扩展

## ✅ P0-2 优化完成

这是一个Chrome/Edge浏览器扩展，用于一键导出KOOK Cookie到消息转发系统。

## 🎯 功能特性

- ✅ 一键导出KOOK的所有Cookie
- ✅ 自动检测是否在KOOK网站
- ✅ 支持复制到剪贴板
- ✅ 支持直接发送到应用（如果应用正在运行）
- ✅ 美观的UI界面
- ✅ 详细的使用说明

## 📦 安装方法

### Chrome浏览器

1. 打开Chrome浏览器
2. 访问 `chrome://extensions/`
3. 开启右上角的"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择本文件夹（`chrome-extension`）
6. 扩展安装完成！

### Edge浏览器

1. 打开Edge浏览器
2. 访问 `edge://extensions/`
3. 开启左下角的"开发人员模式"
4. 点击"加载解压缩的扩展"
5. 选择本文件夹（`chrome-extension`）
6. 扩展安装完成！

## 🚀 使用方法

1. 在浏览器中打开 [KOOK网页版](https://www.kookapp.cn/)
2. 登录您的KOOK账号
3. 点击浏览器工具栏上的扩展图标
4. 点击"导出Cookie"按钮
5. 选择"复制到剪贴板"或"发送到应用"
6. 在KOOK消息转发系统中粘贴Cookie

## 📝 工作原理

1. 扩展使用Chrome的Cookie API获取所有`.kookapp.cn`域名下的Cookie
2. 将Cookie格式化为JSON数组格式
3. 用户可以选择：
   - **复制到剪贴板**: 复制后在应用中手动粘贴
   - **发送到应用**: 直接发送到运行在`localhost:9527`的应用

## 🔒 安全说明

- ✅ 扩展**仅在KOOK网站上运行**
- ✅ Cookie数据**不会上传到任何服务器**
- ✅ 所有操作都在本地完成
- ✅ 源代码完全开放，可审查

## 🛠️ 开发者说明

### 文件结构

```
chrome-extension/
├── manifest.json       # 扩展配置文件
├── popup.html         # 弹窗HTML
├── popup.js           # 弹窗脚本
├── background.js      # 后台脚本
├── content.js         # 内容脚本
├── icons/            # 图标文件夹
│   ├── icon-16.png
│   ├── icon-48.png
│   └── icon-128.png
└── README.md         # 本文件
```

### 构建发布版（可选）

如果需要发布到Chrome Web Store：

1. 准备图标文件（16x16, 48x48, 128x128）
2. 更新`manifest.json`中的版本号
3. 将整个文件夹打包为`.zip`文件
4. 上传到Chrome Web Store

## 📸 截图

扩展弹窗界面包含：
- 🎨 渐变色背景
- 📊 Cookie数量统计
- 🔘 大按钮易于点击
- 💡 详细使用说明

## 🐛 常见问题

### Q: 点击"发送到应用"失败？
A: 请确保KOOK消息转发系统正在运行，并且监听在`localhost:9527`端口。如果应用未运行，请使用"复制到剪贴板"方式。

### Q: 未找到Cookie？
A: 请确保已在KOOK网页版登录，并且在KOOK页面上点击扩展图标。

### Q: 如何卸载扩展？
A: 访问`chrome://extensions/`，找到本扩展，点击"移除"即可。

## 📄 许可证

MIT License - 与主项目保持一致

## 🔗 相关链接

- 主项目: [KOOK消息转发系统](https://github.com/gfchfjh/CSBJJWT)
- KOOK官网: https://www.kookapp.cn/
