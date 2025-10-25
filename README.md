# 🚀 KOOK消息转发系统

<div align="center">

![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.4-green.svg)
![Electron](https://img.shields.io/badge/electron-28.0-purple.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)

**一键部署 · 图形化配置 · 零代码门槛**

[🎬 快速开始](QUICK_START.md) | [📖 完整文档](V5_DOCUMENTATION_INDEX.md) | [🐛 问题反馈](https://github.com/gfchfjh/CSBJJWT/issues) | [💬 讨论区](https://github.com/gfchfjh/CSBJJWT/discussions)

</div>

---

## ✨ v3.1.0 Ultimate Edition 新特性

🎉 **最新版本已发布！** 包含19项深度优化，带来全面的功能增强和性能提升。

### 核心新增功能

#### 🎬 视频管理系统
- ✅ 完整的视频占位符系统
- ✅ 视频上传和流式传输
- ✅ 自动缩略图生成
- ✅ 视频状态管理（available/placeholder/missing）

#### 📧 企业级邮件系统
- ✅ 异步SMTP邮件发送
- ✅ 精美HTML邮件模板
- ✅ 6位验证码（10分钟有效期）
- ✅ 3种备选密码重置方案

#### 🛡️ 增强文件安全
- ✅ 60+危险文件类型检测
- ✅ 用户白名单机制
- ✅ 风险等级智能评估
- ✅ 完整API管理接口

#### ⚡ 性能优化
- ✅ 图片Token自动清理（10分钟）
- ✅ 数据库索引优化
- ✅ Redis持久化配置
- ✅ 多Webhook负载均衡

#### 🔌 可扩展架构
- ✅ 完整插件机制框架
- ✅ 环境变量配置支持
- ✅ 模块化设计
- ✅ RESTful API标准

**详细更新日志**: [V3.1.0 Release Notes](V5_RELEASE_NOTES.md)

---

## 📋 功能特性

### 核心功能

#### 消息抓取
- 🌐 **Playwright驱动** - 稳定可靠的浏览器自动化
- 🔐 **多种登录方式** - 账号密码 / Cookie导入 / 浏览器扩展
- 🔄 **自动重连** - 断线自动恢复，最多5次重试
- 📡 **实时监听** - WebSocket实时接收消息
- 🎭 **多账号支持** - 同时监听多个KOOK账号

#### 消息处理
- 🔄 **智能队列** - Redis消息队列，支持持久化
- 🎨 **格式转换** - KMarkdown自动转换为目标平台格式
- 🖼️ **图片处理** - 三种策略（智能/直传/图床），自动压缩
- 📎 **附件支持** - 自动下载转发，最大50MB
- 🔒 **文件安全** - 60+危险类型检测，白名单机制
- 🗑️ **消息去重** - 7天去重缓存，防止重复转发

#### 多平台转发
- 💬 **Discord** - Webhook方式，支持Embed卡片
- ✈️ **Telegram** - Bot API，支持HTML格式
- 🏢 **飞书** - 自建应用，支持消息卡片
- ⚖️ **负载均衡** - 多Webhook轮询，吞吐量提升10倍

#### 图形化界面
- 🖥️ **Electron桌面应用** - 跨平台支持（Windows/macOS/Linux）
- 🎨 **Vue 3 + Element Plus** - 现代化UI设计
- 🌍 **多语言** - 中文/英文切换
- 🌓 **主题支持** - 浅色/深色/自动跟随系统
- 📊 **实时监控** - 转发状态、统计信息、日志查看

### 高级功能

#### 智能映射
- 🔀 **一键智能映射** - 自动识别同名频道
- 🎯 **一对多转发** - 一个KOOK频道转发到多个目标
- 🔧 **灵活配置** - 支持频道级别的映射规则

#### 过滤规则
- 🔍 **关键词过滤** - 黑名单/白名单支持
- 👤 **用户过滤** - 指定用户消息转发
- 📦 **类型过滤** - 选择转发的消息类型
- 🎛️ **组合规则** - 多条件组合过滤

#### 系统增强
- 🔐 **主密码保护** - bcrypt加密，30天记住
- 📧 **邮件验证码** - 密码找回支持
- 📹 **视频教程** - 内置视频管理系统
- 🔌 **插件机制** - 可扩展的插件框架
- 🖥️ **系统托盘** - 最小化到托盘，快捷操作
- 🚀 **开机自启** - AutoLaunch自动启动

---

## 🎯 快速开始

### 前置要求
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **内存**: 最低4GB，推荐8GB
- **磁盘**: 500MB（不含图片缓存）
- **网络**: 稳定的网络连接

### 一键安装

#### Windows
```bash
# 下载安装包
# KookForwarder_v3.1.0_Windows_x64.exe

# 双击运行安装程序
# 安装向导会自动配置所有依赖
```

#### macOS
```bash
# 下载安装包
# KookForwarder_v3.1.0_macOS.dmg

# 打开.dmg文件
# 拖动到Applications文件夹
```

#### Linux
```bash
# 下载AppImage
# KookForwarder_v3.1.0_Linux_x64.AppImage

# 添加执行权限
chmod +x KookForwarder_v3.1.0_Linux_x64.AppImage

# 运行
./KookForwarder_v3.1.0_Linux_x64.AppImage
```

### 首次配置（5步向导）

1. **欢迎页** - 阅读免责声明
2. **登录KOOK** - 账号密码或Cookie导入
3. **选择服务器** - 勾选要监听的频道
4. **配置Bot** - 设置Discord/Telegram/飞书
5. **频道映射** - 一键智能映射或手动配置

**详细教程**: [快速开始指南](QUICK_START.md)

---

## 📊 技术架构

### 技术栈

#### 前端
- **框架**: Vue 3.4 + Composition API
- **UI库**: Element Plus 2.5
- **状态管理**: Pinia 2.1
- **图表**: ECharts 5.4
- **桌面框架**: Electron 28.0
- **国际化**: Vue I18n 9.8

#### 后端
- **框架**: FastAPI 0.109+
- **异步**: asyncio + aiohttp
- **浏览器**: Playwright (Chromium)
- **队列**: Redis 5.0+ (嵌入式)
- **数据库**: SQLite 3.x
- **图片处理**: Pillow + 多进程池
- **邮件**: aiosmtplib (异步SMTP)

#### 消息转发
- **Discord**: discord-webhook
- **Telegram**: python-telegram-bot
- **飞书**: lark-oapi (官方SDK)

### 架构特点

- ✅ **前后端分离** - RESTful API + WebSocket
- ✅ **异步高性能** - asyncio全异步架构
- ✅ **嵌入式服务** - Redis/Chromium内置，无需额外安装
- ✅ **模块化设计** - 清晰的代码结构，易于扩展
- ✅ **生产级质量** - 完善的错误处理和日志系统

**详细架构**: [架构设计文档](docs/架构设计.md)

---

## 📖 文档导航

### 用户文档
- 📘 [快速开始](QUICK_START.md) - 5分钟上手指南
- 📗 [安装指南](INSTALLATION_GUIDE.md) - 详细安装步骤
- 📙 [用户手册](docs/用户手册.md) - 完整功能说明
- 📕 [视频教程](docs/视频教程/README.md) - 图文视频教程

### 配置教程
- 🔧 [Cookie获取](docs/Cookie获取详细教程.md)
- 💬 [Discord配置](docs/Discord配置教程.md)
- ✈️ [Telegram配置](docs/Telegram配置教程.md)
- 🏢 [飞书配置](docs/飞书配置教程.md)

### 开发文档
- 🏗️ [架构设计](docs/架构设计.md)
- 👨‍💻 [开发指南](docs/开发指南.md)
- 📡 [API文档](docs/API接口文档.md)
- 🔨 [构建指南](BUILD_RELEASE_GUIDE.md)

### 优化报告
- 📊 [深度优化建议](DEEP_OPTIMIZATION_RECOMMENDATIONS_2025.md)
- ✅ [优化完成报告](OPTIMIZATION_COMPLETION_REPORT.md)
- 📦 [Git存档报告](GIT_ARCHIVE_REPORT.md)

**完整索引**: [文档索引](V5_DOCUMENTATION_INDEX.md)

---

## 🛠️ 开发指南

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/gfchfjh/CSBJJWT.git
cd CSBJJWT

# 后端开发
cd backend
pip install -r requirements.txt
python -m app.main

# 前端开发
cd frontend
npm install
npm run dev

# Electron开发
npm run electron:dev
```

### 构建打包

```bash
# 构建所有平台
./build/build_all.sh

# 构建特定平台
npm run electron:build:win    # Windows
npm run electron:build:mac    # macOS
npm run electron:build:linux  # Linux
```

### 测试

```bash
# 后端测试
cd backend
pytest tests/

# 前端测试
cd frontend
npm run test

# 端到端测试
npm run test:e2e
```

**详细开发指南**: [开发文档](docs/开发指南.md)

---

## 📈 项目统计

### 代码统计
- **总代码行数**: 50,000+
- **Python代码**: 25,000+
- **Vue代码**: 15,000+
- **文档**: 30+ 篇
- **API接口**: 100+

### 功能统计
- **支持平台**: 3个（Discord/Telegram/飞书）
- **消息类型**: 7种（文本/图片/文件/表情等）
- **配置选项**: 50+
- **语言支持**: 2种（中文/英文）

### 性能指标
- **消息延迟**: 平均1-2秒
- **吞吐量**: 60条/分钟（单Webhook）
- **内存占用**: ~200MB（单账号）
- **CPU占用**: <5%（空闲时）

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献方式
- 🐛 报告Bug - [提交Issue](https://github.com/gfchfjh/CSBJJWT/issues)
- 💡 功能建议 - [讨论区](https://github.com/gfchfjh/CSBJJWT/discussions)
- 📝 改进文档 - 提交PR
- 🔧 代码贡献 - 遵循[提交规范](GIT_COMMIT_GUIDE.md)

### 开发流程
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

**提交规范**: [Git提交指南](GIT_COMMIT_GUIDE.md)

---

## 📜 更新日志

### v3.1.0 Ultimate Edition (2025-10-25)

#### 🎉 核心新增
- ✨ 视频管理系统（占位符+上传+流式传输）
- ✨ 企业级邮件系统（SMTP+验证码+HTML模板）
- ✨ 增强文件安全（60+危险类型+白名单）
- ✨ 图片Token自动清理（10分钟循环）
- ✨ 20+ 新增API接口

#### ⚡ 性能优化
- 🚀 数据库索引优化（3个索引）
- 🚀 Redis持久化配置（AOF+RDB）
- 🚀 多Webhook负载均衡（轮询算法）
- 🚀 虚拟滚动优化（大数据集）

#### 🔧 架构改进
- 📦 完整插件机制框架
- 📦 环境变量配置支持
- 📦 模块化代码重构
- 📦 RESTful API标准化

#### 📝 文档完善
- 📄 深度优化建议报告（38KB）
- 📄 优化完成报告（23KB）
- 📄 Git存档报告（8KB）
- 📄 完整实施方案（13个）

**代码统计**: +2,346行, -311行, 净增+2,035行

**详细日志**: [完整更新日志](V5_RELEASE_NOTES.md)

---

## ⚠️ 免责声明

**请注意**：
1. 本软件通过浏览器自动化抓取KOOK消息，可能违反KOOK服务条款
2. 使用本软件可能导致账号被封禁，请仅在已获授权的场景下使用
3. 转发的消息内容可能涉及版权，请遵守相关法律法规
4. 本软件仅供学习交流使用，开发者不承担任何法律责任

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

```
MIT License

Copyright (c) 2025 KOOK Forwarder Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 致谢

### 开源项目
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [Electron](https://www.electronjs.org/) - 跨平台桌面应用

### 贡献者
感谢所有为本项目做出贡献的开发者！

---

## 📞 联系方式

- **GitHub**: https://github.com/gfchfjh/CSBJJWT
- **Issues**: https://github.com/gfchfjh/CSBJJWT/issues
- **Discussions**: https://github.com/gfchfjh/CSBJJWT/discussions

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**

Made with ❤️ by KOOK Forwarder Team

[🔝 回到顶部](#-kook消息转发系统)

</div>
