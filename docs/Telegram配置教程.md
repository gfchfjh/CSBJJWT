# Telegram配置教程

**更新日期**: 2025-10-21  

**预计耗时**: 4-5分钟

## 🎉 v1.12.0 新特性


---

## 📖 目录
1. [创建Bot](#创建bot)
2. [获取Chat ID](#获取chat-id)
3. [配置权限](#配置权限)
4. [测试配置](#测试配置)
5. [常见问题](#常见问题)

---

## 创建Bot

### 步骤1: 与BotFather对话

![](https://via.placeholder.com/800x400?text=BotFather+Conversation)

1. 在Telegram搜索 `@BotFather` 或访问 [t.me/BotFather](https://t.me/BotFather)
2. 点击 **START** 开始对话
3. 发送 `/newbot` 命令

### 步骤2: 设置Bot信息

![](https://via.placeholder.com/800x400?text=Bot+Setup)

**设置名称**:
```
BotFather: Alright, a new bot. How are we going to call it?
你: KOOK转发机器人
```

**设置用户名**:
```
BotFather: Good. Now let's choose a username for your bot.
你: kook_forward_bot
```

**⚠️ 注意**:
- 用户名必须以 `bot` 结尾
- 只能包含字母、数字和下划线
- 必须是唯一的（未被使用）

### 步骤3: 获取Token

创建成功后，BotFather会发送：

```
Done! Congratulations on your new bot. You will find it at 
t.me/kook_forward_bot. You can now add a description, about 
section and profile picture for your bot, see /help for a list of commands.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz_1234567

Keep your token secure and store it safely, it can be used by 
anyone to control your bot.
```

**Bot Token 格式**: `数字:字符串`

示例: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz_1234567`

**⚠️ 重要**: 
- 这是Bot的密钥，妥善保管
- 不要分享给其他人
- 如果泄露，使用 `/revoke` 命令重新生成

---

## 获取Chat ID

### 方法1: 使用自动获取工具（推荐）

![](https://via.placeholder.com/800x400?text=Auto+Get+Chat+ID)

在KOOK转发系统中：

1. 将Bot添加到目标群组
2. 在群组中发送任意消息（例如：`/start`）
3. 在配置页面点击 **自动获取Chat ID**
4. 系统会自动检测并填入

### 方法2: 使用getUpdates API

![](https://via.placeholder.com/800x400?text=getUpdates+API)

**步骤**:

1. 将Bot添加到群组
2. 在群组中发送一条消息
3. 访问以下URL（替换YOUR_BOT_TOKEN）:

```
https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
```

4. 查找返回的JSON中的 `chat.id`:

```json
{
  "ok": true,
  "result": [{
    "update_id": 123456,
    "message": {
      "message_id": 1,
      "chat": {
        "id": -1001234567890,    // ← 这就是Chat ID
        "title": "我的群组",
        "type": "supergroup"
      },
      ...
    }
  }]
}
```

**Chat ID 格式**:
- 私聊: 正数，例如 `123456789`
- 群组: 负数，例如 `-1001234567890`

### 方法3: 使用第三方Bot

使用 `@userinfobot` 或 `@getidsbot`:

1. 将Bot邀请到群组
2. 它会自动发送群组的Chat ID

---

## 配置权限

### 必需权限

Bot在群组中需要以下权限：

✅ **发送消息** - 必须
✅ **发送照片** - 如需转发图片
✅ **发送文件** - 如需转发附件
☐ 删除消息 - 可选
☐ 管理员 - 不需要

### 如何设置权限

![](https://via.placeholder.com/800x400?text=Bot+Permissions)

1. 在群组中，点击群组名称
2. 选择 **编辑**
3. 点击 **管理员**
4. 找到你的Bot
5. 勾选需要的权限
6. 点击 **保存**

### 隐私设置

默认情况下，Bot只能接收：
- 直接@它的消息
- 以`/`开头的命令

如需接收所有消息（不推荐），请关闭隐私模式：

1. 与 @BotFather 对话
2. 发送 `/mybots`
3. 选择你的Bot
4. Bot Settings → Group Privacy → Turn off

---

## 测试配置

### 在KOOK转发系统中测试

![](https://via.placeholder.com/800x400?text=Test+Connection)

1. 填入 Bot Token 和 Chat ID
2. 点击 **测试连接** 按钮
3. 在Telegram群组中查看测试消息

### 测试消息示例

如果配置正确，你会在Telegram群组看到：

```
✅ KOOK消息转发系统测试消息

如果您看到这条消息，说明Bot配置成功！
```

### 手动测试（使用Curl）

```bash
curl -X POST "https://api.telegram.org/bot你的TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "你的Chat_ID",
    "text": "测试消息"
  }'
```

成功响应示例：
```json
{
  "ok": true,
  "result": {
    "message_id": 123,
    "chat": {
      "id": -1001234567890,
      "title": "我的群组",
      "type": "supergroup"
    },
    "text": "测试消息"
  }
}
```

---

## 常见问题

### Q: Bot Token无效？

**A**: 检查以下几点：
1. Token格式正确（数字:字母）
2. 没有多余的空格
3. 没有拼写错误
4. Bot未被删除

### Q: Chat ID无法获取？

**A**: 
1. 确保Bot已加入群组
2. 在群组中发送至少一条消息
3. 使用 getUpdates API 查看
4. 检查Bot是否被封禁

### Q: Bot发不了消息？

**A**: 可能的原因：

**1. Bot未加入群组**
- 将Bot重新添加到群组

**2. Bot被踢出**
- 检查群组成员列表

**3. 权限不足**
- 给Bot"发送消息"权限

**4. 群组被限制**
- 检查群组是否被Telegram限制

### Q: 发送图片失败？

**A**:

**原因1: 图片URL无效**
- 确保图片URL可访问
- 检查图片格式（支持JPG、PNG、GIF）

**原因2: 图片过大**
- Telegram限制: 照片最大10MB
- 文件最大50MB

**解决方法**:
```
设置 → 图片处理 → 开启压缩
```

### Q: 如何@群组成员？

**A**:
Telegram Bot可以@用户，但有限制：

**方式1: 使用用户名**
```
@username 你好
```

**方式2: 使用用户ID（HTML格式）**
```html
<a href="tg://user?id=123456789">@用户</a>
```

**⚠️ 限制**:
- Bot无法@所有人（@everyone）
- 只能@已有用户名的用户

### Q: 如何使用Markdown格式？

**A**:
Telegram支持多种格式：

**HTML格式**（推荐）:
```html
<b>粗体</b>
<i>斜体</i>
<code>代码</code>
<a href="URL">链接</a>
```

**Markdown格式**:
```
*粗体*
_斜体_
`代码`
[链接](URL)
```

KOOK转发系统默认使用HTML格式。

---

## 高级配置

### 设置Bot头像

![](https://via.placeholder.com/800x400?text=Set+Bot+Profile+Picture)

1. 与 @BotFather 对话
2. 发送 `/mybots`
3. 选择你的Bot
4. Edit Bot → Edit Profile Picture
5. 发送图片

### 设置Bot描述

```
/setdescription
选择你的Bot
输入描述（例如：KOOK消息转发机器人）
```

### 设置Bot关于

```
/setabouttext
选择你的Bot
输入"关于"文本
```

### 自定义命令

```
/setcommands
选择你的Bot
输入命令列表（格式：命令 - 描述）

示例:
start - 开始使用
help - 帮助信息
status - 查看状态
```

### 内联模式（可选）

如需使用内联查询：

```
/setinline
选择你的Bot
输入提示文本
```

---

## API限流

Telegram有严格的限流：

### 消息发送限制

| 限制类型 | 限制值 |
|---------|--------|
| 私聊消息 | 30条/秒 |
| 群组消息 | 20条/分钟 |
| 所有消息 | 30条/秒 |

### 如何避免封禁

1. **使用队列**: KOOK转发系统已自动实现
2. **延迟发送**: 消息间隔至少50ms
3. **批量发送**: 使用sendMediaGroup发送多张图片
4. **监控错误**: 收到429错误立即停止

---

## 安全建议

### ✅ 最佳实践

1. **保护Token**: 不要在代码中硬编码
2. **定期更换**: 建议每3个月更换Token
3. **限制范围**: 一个Bot只用于一个用途
4. **监控日志**: 检查Bot的API调用记录

### ⚠️ 如果Token泄露

```
1. 立即使用 /revoke 命令（与@BotFather对话）
2. 获取新Token
3. 更新所有使用该Token的地方
4. 检查Bot的消息记录，确认没有被滥用
```

---

## 参考资料

- [Telegram Bot API官方文档](https://core.telegram.org/bots/api)
- [BotFather命令列表](https://core.telegram.org/bots#botfather)
- [Telegram Bot FAQ](https://core.telegram.org/bots/faq)

---

**配置完成！** 🎉

返回 [完整用户手册](./完整用户手册.md)
