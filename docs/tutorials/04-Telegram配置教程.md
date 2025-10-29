# 📘 Telegram Bot 配置教程

> 4分钟创建Bot，实现KOOK到Telegram的消息转发

---

## 🎯 什么是Telegram Bot？

Bot是Telegram提供的自动化账号，可以发送消息、响应命令等。

**特点**：
- ✅ 官方支持，稳定可靠
- ✅ 配置简单，无需服务器
- ✅ 支持富文本（HTML/Markdown）
- ✅ 可发送图片、文件等

---

## 🚀 创建Telegram Bot

### 前置条件

- ✅ 您有Telegram账号
- ✅ 已创建目标群组（或使用现有群组）

---

### 步骤1：与BotFather对话

1. 打开Telegram
2. 搜索 `@BotFather`（官方Bot，有蓝色认证标记）
3. 点击「Start」或发送 `/start`

![BotFather](../images/telegram-botfather.png)

---

### 步骤2：创建新Bot

1. 发送命令 `/newbot`
2. BotFather会询问Bot名称，例如：`KOOK消息转发Bot`
3. 设置Bot用户名（必须以bot结尾），例如：`kook_forwarder_bot`

![创建Bot](../images/telegram-create.png)

**示例对话**：
```
You: /newbot
BotFather: Alright, a new bot. How are we going to call it?

You: KOOK消息转发Bot
BotFather: Good. Now let's choose a username for your bot.

You: kook_forwarder_bot
BotFather: Done! Congratulations on your new bot.
```

---

### 步骤3：获取Bot Token

BotFather会返回您的Bot Token：

```
Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

⚠️ **重要**：
- Token就是Bot的密码
- 请妥善保管，不要泄露
- 如果泄露，使用 `/revoke` 命令重新生成

---

### 步骤4：将Bot添加到群组

1. 在Telegram中找到您的Bot（搜索刚才设置的用户名）
2. 点击「Start」激活Bot
3. 将Bot添加到目标群组：
   - 打开目标群组
   - 点击群组名称
   - 选择「添加成员」
   - 搜索并添加您的Bot

![添加Bot](../images/telegram-add-bot.png)

💡 **提示**：确保Bot有发送消息的权限

---

### 步骤5：获取Chat ID

Chat ID是群组的唯一标识。

#### 方法A：使用转发系统自动获取（推荐）✅

1. 在转发系统中打开「🤖 机器人」页面
2. 添加Telegram Bot配置
3. 填入Bot Token
4. 点击「🔍 自动获取Chat ID」按钮
5. 转发系统会列出所有可用的Chat ID
6. 选择目标群组

![自动获取](../images/telegram-auto-chatid.png)

#### 方法B：手动获取

1. 在群组中给Bot发送一条消息（例如：`/start`）
2. 访问以下URL（替换YOUR_BOT_TOKEN）：
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. 在返回的JSON中找到 `"chat":{"id":-1001234567890}`
4. Chat ID就是 `-1001234567890`（负数，保留负号）

![手动获取](../images/telegram-manual-chatid.png)

---

### 步骤6：测试连接

1. 在转发系统中填入：
   - Bot Token
   - Chat ID
2. 点击「🧪 测试连接」
3. 检查群组是否收到测试消息

![测试成功](../images/telegram-test.png)

✅ **看到测试消息？恭喜，配置成功！**

---

## 🎨 高级配置

### 消息格式

Telegram支持两种消息格式：

#### 1. HTML格式（推荐）✅

转发系统默认使用HTML格式：

```html
<b>粗体文字</b>
<i>斜体文字</i>
<code>代码</code>
<a href="url">链接</a>
```

**效果**：
- **粗体**
- *斜体*
- `代码`
- [链接](url)

#### 2. Markdown格式

也支持Markdown：

```markdown
**粗体**
*斜体*
`代码`
[链接](url)
```

**配置方法**：
- 在Bot配置中选择「消息格式」为「Markdown」

---

### 静音消息

可以让Bot发送消息时不发出通知声音。

**配置方法**：
1. 编辑Bot配置
2. 启用「静音消息」选项
3. 保存

**使用场景**：
- 深夜消息不打扰用户
- 大量消息不刷屏通知

---

### 消息限制

Telegram消息限制：

| 类型 | 限制 |
|-----|------|
| 文本消息 | 最多4096字符 |
| 图片 | 最大10MB |
| 文件 | 最大50MB |
| 发送速率 | 30条/秒 |

**转发系统自动处理**：
- 超长消息自动分段
- 大图片自动压缩
- 超速时自动排队

---

## 🔧 限流说明

Telegram Bot API限制：

- 每秒最多30条消息
- 每个Chat每分钟最多20条消息（群组）

**转发系统自动处理**：
- 检测到限流时自动延迟
- 不会丢失任何消息
- 日志中显示「⏳ 队列中」

---

## ❓ 常见问题

### Q1: Bot无法发送消息？

**可能原因**：
1. Bot未添加到群组
2. Bot没有发送消息权限
3. Bot Token错误

**解决方法**：
1. 确认Bot在群组成员列表中
2. 检查群组设置 到 权限
3. 重新复制Token，确保完整

---

### Q2: Chat ID获取失败？

**可能原因**：
- Bot没有收到任何消息
- Token错误

**解决方法**：
1. 在群组中给Bot发送一条消息（如 `/start`）
2. 等待几秒后重试「自动获取」
3. 如果还是失败，使用方法B手动获取

---

### Q3: 收到「Forbidden: bot was blocked by the user」错误？

**原因**：Bot被用户或群组管理员封禁

**解决方法**：
1. 检查Bot是否被移出群组
2. 确认Bot没有被封禁
3. 重新添加Bot到群组

---

### Q4: 如何删除Bot？

1. 与 `@BotFather` 对话
2. 发送 `/deletebot`
3. 选择要删除的Bot
4. 确认删除

⚠️ **警告**：删除Bot后，Token将失效，无法恢复！

---

### Q5: Bot被滥用怎么办？

如果Token泄露，Bot可能被他人滥用。

**解决方法**：
1. 与 `@BotFather` 对话
2. 发送 `/revoke`
3. 选择Bot
4. 重新生成Token
5. 在转发系统中更新Token

---

## 🔒 安全提示

### 保护Bot Token

⚠️ **Token等同于Bot的密码！**

**安全措施**：
- ✅ 不要在公开场合展示Token
- ✅ 不要通过聊天软件发送Token
- ✅ 定期更换Token
- ❌ 不要提交到GitHub等公开仓库
- ❌ 不要在截图中包含Token

### 限制Bot权限

**最小权限原则**：
- Bot只需要「发送消息」权限
- 不需要「删除消息」「管理员」等权限

**配置方法**：
1. 群组设置 到 权限
2. 为Bot设置自定义权限
3. 仅保留必要权限

---

## 🎯 最佳实践

### 1. 多Bot策略

对于大型转发（>100条/分钟）：
- 创建多个Bot
- 分散到不同频道
- 避免单Bot限流

### 2. 频道命名

建议Telegram群组名称与KOOK频道对应：
- KOOK「公告」 到 Telegram「KOOK公告群」
- KOOK「活动」 到 Telegram「KOOK活动群」

智能映射会更准确！

### 3. 测试Bot

创建一个测试群组：
- 仅添加Bot和自己
- 用于测试消息格式
- 确认无误后再用于生产

---

## 📚 延伸阅读

- [Telegram Bot API官方文档](https://core.telegram.org/bots/api)
- [飞书配置教程](05-飞书配置教程.md)
- [频道映射配置详解](06-频道映射详解.md)

---

## ✅ 配置完成检查清单

- [ ] Bot已创建（通过BotFather）
- [ ] Bot Token已复制
- [ ] Bot已添加到目标群组
- [ ] Chat ID已获取
- [ ] 在转发系统中添加了Telegram Bot配置
- [ ] 测试连接成功（收到测试消息）
- [ ] 创建了频道映射
- [ ] 在Telegram中看到转发的消息

全部完成？🎉 恭喜！您已掌握Telegram配置！

---

**文档版本**: v10.0.0  
**最后更新**: 2025-10-26  
**预计阅读时间**: 8分钟
