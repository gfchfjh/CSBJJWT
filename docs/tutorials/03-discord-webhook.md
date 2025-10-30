# 📗 如何创建Discord Webhook

本教程将详细介绍如何在Discord中创建Webhook，并配置到KOOK转发系统中。

---

## 🎯 什么是Discord Webhook？

Webhook是Discord提供的一个特殊URL，允许外部程序向Discord频道发送消息。通过Webhook，KOOK转发系统可以将消息发送到您的Discord服务器。

**优点**：
- ✅ 无需创建Discord Bot
- ✅ 配置简单，只需一个URL
- ✅ 支持富文本和嵌入内容
- ✅ 可以自定义发送者名称和头像

---

## 📋 前置要求

开始之前，请确保：
- ✅ 您有Discord账号
- ✅ 您在目标Discord服务器中有**管理Webhook**权限
- ✅ 您已安装并运行KOOK转发系统

---

## 🚀 第1步：打开Discord服务器设置

1. 打开Discord应用（桌面版或网页版）
2. 选择您想要接收KOOK消息的服务器
3. 找到您想要发送消息的频道（例如：#公告）
4. 右键点击频道名称
5. 选择"编辑频道"

![编辑频道](../screenshots/discord-edit-channel.png)

---

## 🔧 第2步：创建Webhook

### 2.1 进入Webhook设置

1. 在频道设置中，找到左侧菜单的"整合"（Integrations）
2. 点击"整合"
3. 找到"Webhook"部分
4. 点击"创建Webhook"按钮

![创建Webhook](../screenshots/discord-create-webhook.png)

### 2.2 配置Webhook

1. **设置Webhook名称**
   - 例如："KOOK公告Bot"
   - 这个名称会显示为发送消息的用户名

2. **上传头像（可选）**
   - 点击头像区域上传图片
   - 推荐使用KOOK或您服务器的图标

3. **选择频道**
   - 确认Webhook会发送到正确的频道
   - 例如：#announcements

![配置Webhook](../screenshots/discord-config-webhook.png)

### 2.3 复制Webhook URL

1. 在Webhook设置页面，找到"Webhook URL"
2. 点击"复制Webhook URL"按钮
3. URL格式类似：
   ```
   https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz
   ```

![复制Webhook URL](../screenshots/discord-copy-webhook-url.png)

4. **保存Webhook URL**
   - 将URL保存到安全的地方
   - ⚠️ 不要将Webhook URL分享给他人！

5. 点击"保存更改"

---

## 💻 第3步：在KOOK转发系统中配置Webhook

### 3.1 打开Bot配置页面

1. 启动KOOK转发系统
2. 点击左侧菜单的"机器人配置"
3. 点击顶部的"Discord"标签

![Bot配置页面](../screenshots/bot-config-discord.png)

### 3.2 添加Webhook

1. **Webhook名称**（备注用）
   - 输入一个方便您识别的名称
   - 例如："游戏公告Bot"

2. **Webhook URL**
   - 粘贴刚才复制的Webhook URL
   - 格式：`https://discord.com/api/webhooks/...`

3. **测试连接**
   - 点击"🧪 测试连接"按钮
   - 系统会发送一条测试消息到Discord
   - 如果成功，您会在Discord频道看到测试消息

![配置Webhook](../screenshots/system-config-discord.png)

### 3.3 保存配置

1. 确认测试成功后，点击"保存"按钮
2. Webhook会出现在"已配置的Webhook"列表中

![Webhook列表](../screenshots/discord-webhook-list.png)

---

## 🔀 第4步：配置频道映射

现在需要将KOOK频道映射到这个Discord Webhook。

### 4.1 进入频道映射页面

1. 点击左侧菜单的"频道映射"
2. 您会看到可视化的映射编辑器

![频道映射](../screenshots/mapping-visual.png)

### 4.2 创建映射

1. **选择KOOK频道（源）**
   - 在左侧列表中，点击要转发的KOOK频道
   - 例如："游戏公告服务器 / #公告频道"

2. **选择Discord Webhook（目标）**
   - 在右侧列表中，点击刚才配置的Webhook
   - 例如："游戏公告Bot (Discord)"

3. **确认映射**
   - 中间会出现一条连线，表示映射关系已创建
   - 您可以看到映射详情

![创建映射](../screenshots/create-mapping-discord.png)

### 4.3 保存映射

1. 点击右上角的"保存映射"按钮
2. 系统会保存所有配置

---

## ✅ 第5步：测试转发

### 5.1 启动监听服务

1. 回到"概览"页面
2. 点击"启动服务"按钮
3. 系统开始监听KOOK消息

![启动服务](../screenshots/start-service.png)

### 5.2 发送测试消息

1. 在KOOK中，向您配置的频道发送一条测试消息
   ```
   测试消息：这是一条测试消息
   ```

2. 稍等几秒（通常1-2秒）

3. 在Discord频道中检查是否收到消息

![测试消息](../screenshots/discord-test-message.png)

### 5.3 查看转发日志

1. 点击左侧菜单的"实时日志"
2. 您可以看到转发的详细记录：
   - ✅ 成功：消息已转发
   - ⏱️ 延迟时间
   - 📝 消息内容预览

![转发日志](../screenshots/forwarding-logs.png)

---

## 🎨 高级配置

### 伪装发送者

Discord Webhook支持自定义发送者名称和头像，让消息看起来更自然。

**在KOOK转发系统中启用**：

1. 进入"系统设置" → "Discord设置"
2. 勾选"伪装原始发送者"
3. 保存设置

现在，转发的消息会显示KOOK用户的名称和头像，而不是Webhook的名称。

![伪装发送者](../screenshots/discord-impersonate.png)

**消息效果**：

**未启用伪装**：
```
[KOOK公告Bot]
系统维护通知：服务器将于明天凌晨2点维护
```

**启用伪装**：
```
[管理员小明]
系统维护通知：服务器将于明天凌晨2点维护
```

### Embed卡片消息

对于包含链接或媒体的消息，可以使用Embed卡片显示：

1. 进入"系统设置" → "Discord设置"
2. 勾选"使用Embed卡片"
3. 保存设置

![Embed卡片](../screenshots/discord-embed.png)

### 超长消息分段

Discord限制每条消息最多2000字符。系统会自动分段：

- 消息长度 ≤ 2000字符：正常发送
- 消息长度 > 2000字符：自动拆分为多条

---

## 🛠️ 故障排查

### 问题1：Webhook URL无效

**症状**：提示"Webhook URL格式错误"

**解决方法**：
1. 检查URL是否完整
2. URL应以 `https://discord.com/api/webhooks/` 开头
3. 确保没有多余的空格

### 问题2：测试连接失败

**症状**：点击"测试连接"后提示失败

**可能原因**：
1. **网络问题**
   - 检查网络连接
   - 尝试访问 https://discord.com

2. **Webhook已删除**
   - 在Discord中检查Webhook是否还存在
   - 如已删除，重新创建

3. **权限问题**
   - 确认Bot有发送消息的权限
   - 检查频道权限设置

### 问题3：消息发送失败

**症状**：实时日志显示"发送失败"

**解决方法**：

1. **检查限流**
   - Discord限制每5秒最多5条消息
   - 如果超限，系统会自动排队

2. **检查Webhook状态**
   - 在Discord中重新测试Webhook
   - 确保Webhook URL未过期

3. **查看详细错误**
   - 点击失败的日志条目
   - 查看详细错误信息

![错误详情](../screenshots/discord-error-details.png)

---

## ❓ 常见问题

### Q1: 可以用一个Webhook发送到多个频道吗？

**A**: 不可以。每个Webhook只能发送到一个Discord频道。如果需要发送到多个频道：
1. 在每个频道创建独立的Webhook
2. 在KOOK转发系统中配置多个Webhook
3. 为每个Webhook创建对应的映射

### Q2: Webhook URL会过期吗？

**A**: 不会自动过期，但如果：
- 在Discord中删除Webhook
- 删除对应的频道
- 离开Discord服务器

Webhook会失效。建议定期测试Webhook是否正常工作。

### Q3: 可以修改Webhook的名称和头像吗？

**A**: 可以！有两种方法：

**方法1：在Discord中修改**
1. 打开频道设置 → 整合 → Webhook
2. 编辑Webhook的名称和头像
3. 保存更改

**方法2：通过系统配置**
1. 启用"伪装原始发送者"
2. 系统会自动使用KOOK用户的名称和头像

### Q4: 如何删除不需要的Webhook？

**A**: 两个步骤：

**在KOOK转发系统中**：
1. 进入"机器人配置" → "Discord"
2. 找到要删除的Webhook
3. 点击"删除"按钮

**在Discord中**：
1. 打开频道设置 → 整合
2. 找到对应的Webhook
3. 点击"删除Webhook"

---

## 📺 视频教程

- [📺 Discord Webhook完整配置教程（3分钟）](../videos/discord-webhook-tutorial.mp4)
- [📺 Discord高级功能演示（5分钟）](../videos/discord-advanced.mp4)

---

## 🎓 总结

恭喜！您已经成功配置了Discord Webhook。

**关键步骤回顾**：
1. ✅ 在Discord中创建Webhook
2. ✅ 复制Webhook URL
3. ✅ 在系统中配置Webhook
4. ✅ 创建频道映射
5. ✅ 测试转发

**下一步学习**：
- [📕 如何配置Telegram Bot](03-telegram-bot.md)
- [📔 如何配置飞书自建应用](04-feishu-app.md)
- [📓 频道映射配置详解](05-channel-mapping.md)

---

有问题？查看 [常见问题FAQ](../faq.md) 或 [联系支持](../support.md)
