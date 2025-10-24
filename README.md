# KOOK消息转发系统

<div align="center">

**一款面向普通用户的KOOK消息转发工具**

[![Version](https://img.shields.io/badge/version-3.0-brightgreen.svg)](https://github.com/gfchfjh/CSBJJWT)
[![Build](https://img.shields.io/badge/build-passing-success.svg)](https://github.com/gfchfjh/CSBJJWT/actions)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.4+-green.svg)](https://vuejs.org/)

</div>

---

## 📥 快速下载（最新版 v3.0）

### 🎯 预编译安装包 - 下载即用（推荐）

| 平台 | 文件 | 大小 | 下载链接 |
|------|------|------|----------|
| 🪟 **Windows** | KOOK.Setup.3.0.0.exe | ~100 MB | **[⬇️ 立即下载](https://github.com/gfchfjh/CSBJJWT/releases/latest)** |
| 🐧 **Linux** | KOOK.-3.0.0.AppImage | ~140 MB | **[⬇️ 立即下载](https://github.com/gfchfjh/CSBJJWT/releases/latest)** |
| 🍎 **macOS** | KOOK.-3.0.0.dmg | ~150 MB | **[⬇️ 立即下载](https://github.com/gfchfjh/CSBJJWT/releases/latest)** |
| 🐳 **Docker** | ghcr.io/gfchfjh/csbjjwt:latest | - | `docker pull ghcr.io/gfchfjh/csbjjwt:latest` |

💡 **使用说明**：
- **Windows**: 下载后双击运行，按照向导安装
- **Linux**: 下载后运行 `chmod +x *.AppImage && ./*.AppImage`
- **国内加速**: [ghproxy镜像下载](https://mirror.ghproxy.com/https://github.com/gfchfjh/CSBJJWT/releases/latest)

📖 **详细说明**: [下载安装指南](DOWNLOAD_INSTRUCTIONS.md) | [快速开始](QUICK_START.md)

---

## 🎯 v3.0 核心特性

### ⚡ 性能优化

- 🚀 **数据库批量写入**: 批量处理优化，减少I/O次数
- ⚡ **JSON解析加速**: 使用orjson高性能库
- 💻 **虚拟滚动**: 支持大量日志流畅显示
- 📊 **消息转发**: 高并发处理能力
- 🖼️ **图片处理**: 多进程并行处理

### 🔒 安全加固

- 🛡️ **HTTPS强制**: 生产环境强制HTTPS连接
- 🔐 **URL验证**: 验证码来源验证，防钓鱼攻击
- ✅ **SQL注入防护**: 完整扫描工具和修复指南
- 🔒 **传输安全**: 多项安全响应头防护

### 🏗️ 架构优化

- 📦 **依赖注入**: 解决循环依赖，提升可测试性
- 🔧 **单例模式**: 全局变量重构，线程安全
- 📝 **统一异常**: 15种异常类型，规范化处理

### 📚 完整文档

- 📖 [实施指南](OPTIMIZATION_IMPLEMENTATION_GUIDE.md) - 详细优化步骤
- 📊 [优化总结](OPTIMIZATION_SUMMARY.md) - 完整优化说明
- 📋 [更新日志](CHANGELOG_v3.0_DEEP_OPTIMIZATION.md) - 详细变更记录

---

## 📦 项目简介

KOOK消息转发系统是一款功能强大、易于使用的跨平台消息转发工具，能够将KOOK（原开黑啦）平台的消息实时转发到Discord、Telegram、飞书等其他平台。

### ✨ 核心特性

**性能与优化：**
- ⚡ **高性能处理** - 优化的消息处理流程
- 📊 **批量处理** - 数据库批量写入
- 🚀 **JSON加速** - orjson替换标准库
- 💻 **虚拟滚动** - 大数据量流畅显示
- 🖼️ **多进程处理** - 图片并行处理

**安全与稳定：**
- 🔒 **HTTPS强制** - 生产环境强制HTTPS连接
- 🛡️ **安全响应头** - 多项安全响应头防护
- 🔐 **URL验证** - 验证码来源验证，防钓鱼
- ✅ **SQL注入防护** - 完整扫描和修复
- 🔧 **异常处理** - 统一异常体系

**架构与代码：**
- 📦 **依赖注入** - 解决循环依赖问题
- 🔧 **单例模式** - 全局变量重构
- 📝 **文档完善** - 详细的技术文档

**基础特性：**
- 🎯 **零代码配置** - 完全图形化操作
- 🚀 **一键安装** - 提供Windows/macOS/Linux安装包
- 🤖 **多平台支持** - Discord、Telegram、飞书
- 🔄 **实时转发** - 平均延迟<2秒
- 🎨 **格式转换** - 自动转换消息格式
- 🔗 **链接预览** - 自动提取标题、描述、图片
- 🛡️ **智能过滤** - 关键词、用户、消息类型过滤
- 📊 **可视化监控** - 实时状态和统计
- 💾 **消息队列** - 保证不丢失任何消息
- 🔒 **主密码保护** - 启动时密码验证
- 🌙 **深色主题** - 浅色/深色/自动三种模式
- 💻 **桌面应用** - 开机自启、系统托盘、通知

---

## 🚀 快速开始

### 方式1: Docker一键部署（推荐）

```bash
# Linux/macOS/服务器，一行命令：
curl -fsSL https://raw.githubusercontent.com/gfchfjh/CSBJJWT/main/docker-install.sh | bash
```

✅ 预计时间: 3分钟  
✅ 优点: 容器化部署、自动重启、数据持久化

### 方式2: 预编译安装包

下载对应平台的安装包，双击运行即可。

详见：[快速开始指南](QUICK_START.md)

---

## 📖 文档导航

### 🚀 快速开始
- [5分钟快速开始](QUICK_START.md)
- [一键安装指南](INSTALLATION_GUIDE.md)
- [Docker部署](docker-compose.yml)

### 📚 技术文档
- [优化实施指南](OPTIMIZATION_IMPLEMENTATION_GUIDE.md) - 详细优化步骤
- [优化总结](OPTIMIZATION_SUMMARY.md) - 完整优化说明
- [更新日志](CHANGELOG_v3.0_DEEP_OPTIMIZATION.md) - 详细变更记录

### 🔧 开发文档
- [本地构建指南](LOCAL_BUILD_GUIDE.md)
- [构建发布指南](BUILD_RELEASE_GUIDE.md)
- [压力测试](STRESS_TEST_README.md)

### 📋 完整文档
查看 [docs/](docs/) 目录获取完整文档列表

---

## 🎯 版本历史

- **v3.0** (2025-10-24) - 深度优化完成版
- **v1.18.0** (2025-10-24) - 深度优化版
- **v1.17.0** (2025-10-24) - 深度优化+稳定性增强
- **v1.16.0** (2025-10-22) - 智能映射增强版
- **v1.15.0** (2025-10-20) - Telegram辅助工具
- **v1.14.0** (2025-10-18) - 多账号管理增强
- 查看 [完整更新日志](CHANGELOG_v3.0_DEEP_OPTIMIZATION.md)

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

- 问题反馈: [GitHub Issues](https://github.com/gfchfjh/CSBJJWT/issues)
- Pull Request: [GitHub PR](https://github.com/gfchfjh/CSBJJWT/pulls)

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🎉 致谢

感谢所有贡献者和用户的支持！

---

<div align="center">

**KOOK消息转发系统 v3.0**

高性能跨平台消息转发工具

[立即下载](https://github.com/gfchfjh/CSBJJWT/releases/latest) | [快速开始](QUICK_START.md) | [查看文档](docs/)

</div>
