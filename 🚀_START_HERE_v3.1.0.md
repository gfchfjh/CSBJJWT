# 🚀 KOOK消息转发系统 - 快速开始

**版本**: v3.1.0 Ultimate Edition  
**状态**: ✅ 生产就绪  
**更新日期**: 2025-10-25

---

## 🎯 5分钟快速上手

### 第1步：下载安装（1分钟）

#### Windows 用户
```bash
1. 下载 KookForwarder_v3.1.0_Windows_x64.exe
2. 双击运行安装程序
3. 按照向导完成安装
```

#### macOS 用户
```bash
1. 下载 KookForwarder_v3.1.0_macOS.dmg
2. 打开dmg文件
3. 拖动到Applications文件夹
```

#### Linux 用户
```bash
# 下载AppImage
wget https://github.com/gfchfjh/CSBJJWT/releases/latest/download/KookForwarder_v3.1.0_Linux_x64.AppImage

# 添加执行权限
chmod +x KookForwarder_v3.1.0_Linux_x64.AppImage

# 运行
./KookForwarder_v3.1.0_Linux_x64.AppImage
```

---

### 第2步：首次配置（4分钟）

#### 配置向导 - 5步完成

**步骤1: 欢迎页（30秒）**
```
✅ 阅读免责声明
✅ 勾选"我已阅读并同意"
✅ 点击"同意并继续"
```

**步骤2: 登录KOOK（1分钟）**

**方法A：账号密码（推荐新手）**
```
1. 输入KOOK邮箱
2. 输入密码
3. 如需验证码，按提示输入
4. 点击"登录"
```

**方法B：Cookie导入（推荐老手）**
```
1. 点击"导入Cookie"
2. 粘贴Cookie JSON
3. 点击"验证并导入"
```

**步骤3: 选择服务器（1分钟）**
```
1. 自动加载你的服务器列表
2. 勾选要监听的服务器
3. 展开服务器，勾选要监听的频道
4. 点击"下一步"
```

**步骤4: 配置Bot（1分钟）**
```
选择平台：Discord / Telegram / 飞书

Discord:
  → 输入Webhook URL
  → 点击"测试连接"
  → 看到测试消息即成功

Telegram:
  → 输入Bot Token
  → 点击"自动获取Chat ID"
  → 在群组发消息
  → 系统自动填入Chat ID

飞书:
  → 输入App ID
  → 输入App Secret
  → 点击"测试连接"
```

**步骤5: 频道映射（30秒）**
```
推荐：点击"智能映射"
  → 系统自动匹配同名频道
  → 确认映射关系
  → 点击"完成"

手动：逐个添加映射
  → 选择KOOK频道
  → 选择目标平台频道
  → 点击"添加"
```

---

### 第3步：开始使用

✅ 配置完成后，系统自动开始转发  
✅ 在KOOK发送测试消息验证  
✅ 查看"实时日志"确认转发状态  

---

## 🆕 v3.1.0 新功能快速导览

### 1. 视频教程系统 🎬

**位置**: 帮助 → 视频教程

**功能**:
- 📺 5个视频教程（制作中）
- 🖼️ 自动缩略图
- ⏯️ 流式播放
- 📝 图文替代方案

### 2. 邮件验证码 📧

**位置**: 设置 → 邮件配置

**功能**:
- ✉️ SMTP邮件发送
- 🔢 6位验证码
- 🔐 密码重置
- 🎨 精美HTML邮件

**配置SMTP**:
```
SMTP服务器: smtp.gmail.com
端口: 587
用户名: your@gmail.com
密码: your_app_password
```

### 3. 文件安全检查 🛡️

**位置**: 设置 → 文件安全

**功能**:
- ⚠️ 60+危险文件类型检测
- ✅ 用户白名单管理
- 📊 安全统计信息
- 🔍 实时检查

**查看危险类型**:
```
设置 → 文件安全 → 危险文件类型
查看完整的危险扩展名列表
```

### 4. 性能监控增强 📊

**位置**: 首页 → 性能监控

**新增指标**:
- 💾 内存使用情况
- 🖥️ CPU占用率
- 📈 消息处理速度
- 🔄 队列长度

---

## 💡 快速技巧

### Cookie快速获取

**Chrome浏览器**:
```
1. 访问 www.kookapp.cn 并登录
2. 按F12打开开发者工具
3. Application → Cookies → www.kookapp.cn
4. 全选 → 右键 → Copy → Copy as JSON
5. 粘贴到系统的Cookie导入框
```

**使用扩展**:
```
1. 安装"Cookie Editor"扩展
2. 访问KOOK网站
3. 点击扩展图标
4. 导出为JSON格式
5. 复制粘贴到系统
```

### 智能映射技巧

**最佳实践**:
```
1. KOOK频道命名规范化
   #公告 → 映射到 Discord #announcements
   
2. 使用相同或相似的频道名
   系统会自动识别并推荐
   
3. 一个KOOK频道可映射多个目标
   #公告 → Discord #announcements
         → Telegram 公告群
         → 飞书 运营群
```

### 负载均衡配置

**多Webhook设置**:
```
1. 创建5个Discord Webhook
2. 在Bot配置中添加所有Webhook
3. 系统自动轮询使用
4. 吞吐量提升5倍！
```

---

## ❓ 常见问题

### 1. 账号显示"离线"？

**原因**: Cookie过期或网络问题

**解决**:
```
1. 账号管理 → 选择账号 → 重新登录
2. 或删除账号后重新添加
3. 确保网络可以访问KOOK
```

### 2. 消息转发延迟大？

**原因**: 队列积压或限流

**解决**:
```
1. 查看首页"队列中消息"数量
2. 配置多个Webhook实现负载均衡
3. 减少监听的频道数量
```

### 3. 图片转发失败？

**原因**: 防盗链或图片过大

**解决**:
```
1. 系统已自动处理防盗链
2. 切换到"智能模式"（设置 → 图片处理）
3. 系统会自动压缩大图片
```

### 4. 如何配置SMTP？

**Gmail示例**:
```
1. 启用两步验证
2. 生成应用专用密码
3. 使用应用密码作为SMTP密码
4. SMTP地址: smtp.gmail.com:587
```

---

## 📖 进阶使用

### 消息过滤规则

**关键词过滤**:
```
黑名单: 广告, 代练, 外挂
白名单: 官方公告, 版本更新
```

**用户过滤**:
```
白名单: 仅转发官方账号消息
黑名单: 屏蔽广告机器人
```

### 系统托盘使用

**右键菜单**:
```
- 显示主界面
- 暂停转发
- 查看日志
- 退出
```

### 开机自启动

**启用方式**:
```
设置 → 系统 → 开机自动启动
勾选后，系统会在开机时自动运行
```

---

## 🔗 相关资源

### 文档
- 📖 [完整文档](V5_DOCUMENTATION_INDEX.md)
- 📘 [用户手册](docs/用户手册.md)
- 📗 [API文档](docs/API接口文档.md)

### 教程
- 🎬 [视频教程](docs/视频教程/README.md)
- 📄 [Cookie获取](docs/Cookie获取详细教程.md)
- 💬 [Discord配置](docs/Discord配置教程.md)
- ✈️ [Telegram配置](docs/Telegram配置教程.md)

### 优化报告
- 📊 [深度优化建议](DEEP_OPTIMIZATION_RECOMMENDATIONS_2025.md)
- ✅ [优化完成报告](OPTIMIZATION_COMPLETION_REPORT.md)

---

## 🆘 获取帮助

### 内置帮助

**位置**: 帮助 → 帮助中心

**包含**:
- 📚 6篇图文教程
- 📺 5个视频教程
- ❓ 8个常见问题
- 🔍 智能搜索

### 在线支持

- **GitHub Issues**: https://github.com/gfchfjh/CSBJJWT/issues
- **讨论区**: https://github.com/gfchfjh/CSBJJWT/discussions

---

<div align="center">

**🎉 恭喜！你已掌握KOOK消息转发系统的基础使用**

**下一步**: [探索高级功能](docs/用户手册.md) | [查看完整文档](V5_DOCUMENTATION_INDEX.md)

[🏠 返回主页](README.md)

</div>
