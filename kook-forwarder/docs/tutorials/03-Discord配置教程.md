# 📘 Discord 配置教程

> 2分钟创建Webhook，实现KOOK到Discord的消息转发

---

## 🎯 什么是Discord Webhook？

Webhook是Discord提供的消息接口，允许外部程序向Discord频道发送消息。

**特点**：
- ✅ 无需创建Bot
- ✅ 配置超级简单
- ✅ 支持富文本和嵌入卡片
- ✅ 可以伪装成任何用户

---

## 🚀 创建Discord Webhook

### 前置条件

- ✅ 您是Discord服务器的管理员或有「管理Webhook」权限
- ✅ 已确定要接收消息的目标频道

---

### 步骤1：打开频道设置

1. 右键点击目标频道（例如 #announcements）
2. 选择「编辑频道」

![右键菜单](../images/discord-step1.png)

---

### 步骤2：创建Webhook

1. 点击左侧的「整合」标签
2. 找到「Webhook」部分
3. 点击「新建Webhook」

![创建Webhook](../images/discord-step2.png)

---

### 步骤3：配置Webhook

1. **名称**：给Webhook起个名字（例如：KOOK消息转发）
2. **头像**（可选）：上传一个图标
3. 点击「复制Webhook URL」按钮

![配置Webhook](../images/discord-step3.png)

**Webhook URL格式**：
```
https://discord.com/api/webhooks/1234567890/AbCdEfGhIjKlMnOpQrStUvWxYz
```

4. 点击「保存更改」

---

### 步骤4：粘贴到转发系统

1. 回到KOOK转发系统
2. 进入「🤖 机器人」页面
3. 点击「➕ 添加配置」
4. 选择平台：Discord
5. 粘贴刚才复制的Webhook URL
6. 点击「🧪 测试连接」

![测试连接](../images/discord-test.png)

**测试成功**：
- 转发系统会发送一条测试消息到Discord频道
- 如果您在Discord中看到测试消息，说明配置成功！

---

## 🎨 高级配置

### 配置Embed卡片

Embed是Discord的富文本卡片，可以显示标题、描述、图片等。

**示例效果**：

![Embed示例](../images/discord-embed.png)

**配置方法**：

在转发系统中，编辑Discord Bot配置，启用「使用Embed卡片」选项。

**自定义Embed样式**：
```json
{
  "title": "来自KOOK的消息",
  "description": "消息内容",
  "color": 0x00FF00,
  "footer": {
    "text": "KOOK消息转发系统"
  }
}
```

---

### 设置用户伪装

可以让消息显示为KOOK原始发送者的名字和头像。

**配置步骤**：
1. 编辑Bot配置
2. 启用「伪装原始发送者」
3. 保存

**效果展示**：

**未启用**：
```
KOOK消息转发 Today at 14:23
张三: 大家好
```

**已启用**：
```
张三 Today at 14:23
大家好
```

---

### 超长消息处理

Discord单条消息最多2000字符。

**转发系统自动处理**：
- 超过2000字符的消息会自动分段
- 分段发送，保持内容完整
- 您无需任何配置

---

### 多个Webhook

同一个Discord服务器可以创建多个Webhook。

**使用场景**：
- KOOK「#公告」 → Discord「#announcements」（Webhook A）
- KOOK「#活动」 → Discord「#events」（Webhook B）
- KOOK「#技术」 → Discord「#tech」（Webhook C）

**配置方法**：
- 在不同Discord频道中分别创建Webhook
- 在转发系统中添加多个Discord Bot配置

---

## 🔧 限流说明

Discord对Webhook有速率限制：

- 每5秒最多5条消息
- 每分钟最多30条消息

**转发系统自动处理**：
- 检测到限流时自动排队
- 延迟发送，不会丢失消息
- 您会在日志中看到「⏳ 队列中」状态

---

## ❓ 常见问题

### Q1: Webhook测试失败？

**检查清单**：
- ✅ URL是否完整复制？
- ✅ URL是否包含 `https://discord.com/api/webhooks/`？
- ✅ Webhook是否被删除？
- ✅ 网络连接是否正常？

**解决方法**：
1. 重新复制Webhook URL
2. 确认Webhook仍然存在（在Discord设置中查看）
3. 尝试访问Webhook URL（应该返回JSON）

---

### Q2: 消息没有发送到Discord？

**可能原因**：
- 映射配置错误
- 服务未启动
- Webhook被删除

**排查步骤**：
1. 检查映射配置（KOOK频道 → Discord频道）
2. 确认服务状态为「运行中」
3. 在Discord中确认Webhook存在
4. 查看日志中的错误信息

---

### Q3: 图片没有显示？

**可能原因**：
- 图片URL失效
- 防盗链限制
- 网络问题

**解决方法**：
1. 在设置中切换到「智能模式」
2. 转发系统会自动处理防盗链
3. 查看日志中的详细错误

---

### Q4: 如何删除Webhook？

1. 打开Discord频道设置
2. 进入「整合」→「Webhook」
3. 找到对应的Webhook
4. 点击「删除Webhook」

⚠️ 删除后，该Webhook URL将失效，转发会失败！

---

### Q5: Webhook安全吗？

**安全建议**：
- ✅ Webhook URL等同于密码，不要泄露
- ✅ 不要在公开场合展示URL
- ✅ 如果URL泄露，立即删除并重新创建
- ❌ 不要分享给不信任的人

**权限说明**：
- Webhook只能发送消息，不能读取消息
- Webhook不能删除消息或修改频道设置
- 相对安全，但仍需妥善保管

---

## 🎯 最佳实践

### 1. 频道命名规范

建议Discord频道名称与KOOK频道对应：
- KOOK「公告」 → Discord「announcements」
- KOOK「活动」 → Discord「events」

这样智能映射会更准确！

### 2. 权限设置

确保Webhook所在频道：
- ✅ 允许「发送消息」
- ✅ 允许「嵌入链接」
- ✅ 允许「附加文件」

### 3. 性能优化

如果转发消息量很大（>60条/分钟）：
- 创建多个Webhook（负载均衡）
- 转发系统会自动轮询使用

---

## 📚 延伸阅读

- [Discord Webhook官方文档](https://discord.com/developers/docs/resources/webhook)
- [Telegram配置教程](04-Telegram配置教程.md)
- [飞书配置教程](05-飞书配置教程.md)

---

## ✅ 配置完成检查清单

- [ ] Webhook已创建
- [ ] Webhook URL已复制
- [ ] 在转发系统中添加了Discord Bot配置
- [ ] 测试连接成功（收到测试消息）
- [ ] 创建了频道映射
- [ ] 在Discord中看到转发的消息

全部完成？🎉 恭喜！您已掌握Discord配置！

---

**文档版本**: v6.1.0  
**最后更新**: 2025-10-26  
**预计阅读时间**: 5分钟
