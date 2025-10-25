# KOOK Cookie Exporter - Chrome扩展

一键导出KOOK Cookie，用于KOOK消息转发系统。

## 功能

- 🍪 一键导出KOOK所有Cookie
- 📋 复制到剪贴板
- 💾 下载为JSON文件
- ✅ 自动格式化为标准JSON格式
- 🔒 仅在KOOK网站域名下工作，安全可靠

## 安装方法

### 开发模式安装

1. 打开Chrome浏览器
2. 访问 `chrome://extensions/`
3. 开启右上角的"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择本扩展所在的文件夹

### 打包安装

1. 在 `chrome://extensions/` 页面
2. 点击"打包扩展程序"
3. 选择本扩展文件夹
4. 生成 `.crx` 文件
5. 将 `.crx` 文件拖拽到Chrome安装

## 使用方法

1. 访问KOOK网站（www.kookapp.cn）并登录
2. 点击浏览器工具栏的扩展图标
3. 点击"导出Cookie"按钮
4. 选择"复制到剪贴板"或"下载为文件"
5. 在KOOK消息转发系统中导入Cookie

## 文件说明

- `manifest.json` - 扩展配置文件
- `popup.html` - 弹出窗口界面
- `popup.js` - 弹出窗口逻辑
- `background.js` - 后台服务脚本
- `icon*.png` - 扩展图标（各种尺寸）

## 权限说明

- `cookies` - 读取Cookie权限（仅用于导出KOOK Cookie）
- `activeTab` - 获取当前标签页信息
- `https://*.kookapp.cn/*` - 仅在KOOK域名下工作
- `https://*.kaiheila.cn/*` - 支持旧域名

## 隐私声明

本扩展：
- ✅ 仅读取KOOK域名的Cookie
- ✅ 所有数据仅在本地处理
- ✅ 不上传任何数据到服务器
- ✅ 不跟踪用户行为
- ✅ 开源透明

## 版本历史

### v1.0.0 (2025-10-25)
- 首次发布
- 支持一键导出KOOK Cookie
- 支持复制和下载功能

## 许可证

MIT License
