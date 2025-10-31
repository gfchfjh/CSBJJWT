# 如何创建Telegram Bot

本教程将详细介绍如何在Telegram中创建Bot，用于接收KOOK消息转发。

---

## 📋 目录

1. [什么是Telegram Bot](#什么是telegram-bot)
2. [创建Bot详细步骤](#创建bot详细步骤)
3. [获取Chat ID](#获取chat-id)
4. [测试Bot](#测试bot)
5. [常见问题](#常见问题)

---

## 什么是Telegram Bot

**Telegram Bot** 是Telegram官方提供的自动化账号，可以通过API接收和发送消息。

### 特点
- ✅ **完全免费**：无任何费用
- ✅ **功能强大**：支持文本、图片、文件、按钮等
- ✅ **即时生效**：创建后立即可用
- ✅ **无需服务器**：Telegram托管Bot

### 限制
- ⚠️ **频率限制**：每秒最多30条消息
- ⚠️ **需要Token**：必须妥善保管Bot Token

---

## 创建Bot详细步骤

### 步骤1：打开BotFather

**BotFather** 是Telegram官方的Bot管理机器人，用于创建和管理所有Bot。

1. 打开Telegram应用
2. 在搜索框中输入：`@BotFather`
3. 点击官方认证的BotFather（带蓝色对勾✅）
4. 点击 **"START"** 或 **"开始"** 按钮

> **重要**：确保是官方的BotFather，用户名必须是 `@BotFather`

> **截图说明**：
> - [ ] 截图：搜索BotFather
> - [ ] 截图：BotFather对话界面（标注START按钮）

---

### 步骤2：创建新Bot

1. 在与BotFather的对话中，发送命令：
   ```
   /newbot
   ```

2. BotFather会回复：
   ```
   Alright, a new bot. How are we going to call it? Please choose a name for your bot.
   ```
   意思是：好的，创建新Bot。请为您的Bot选择一个名称。

3. **输入Bot的显示名称**（可以是中文）
   例如：
   ```
   KOOK消息转发Bot
   ```
   或
   ```
   游戏公告Bot
   ```

> **提示**：这个名称会显示在对话列表中，可以随时修改

> **截图说明**：
> - [ ] 截图：发送 /newbot 命令
> - [ ] 截图：BotFather请求输入名称

---

### 步骤3：设置Bot用户名

1. BotFather会继续询问：
   ```
   Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.
   ```
   意思是：好的。现在请为Bot选择一个用户名。必须以 `bot` 结尾。

2. **输入Bot用户名**（必须是英文，必须以bot结尾）
   例如：
   ```
   kook_forward_bot
   ```
   或
   ```
   game_notice_bot
   ```

> **用户名规则**：
> - ✅ 必须以 `bot` 结尾（不区分大小写）
> - ✅ 只能包含英文字母、数字和下划线
> - ✅ 至少5个字符
> - ❌ 不能包含中文或特殊符号
> - ❌ 不能与现有Bot重名

**如果用户名已被占用**：
BotFather会提示：
```
Sorry, this username is already taken.
```
请换一个用户名重试。

> **截图说明**：
> - [ ] 截图：输入Bot用户名
> - [ ] 截图：用户名已被占用的提示（如有）

---

### 步骤4：获取Bot Token

创建成功后，BotFather会发送一条包含Bot Token的消息：

```
Done! Congratulations on your new bot. You will find it at t.me/your_bot_name. You can now add a description, about section and profile picture for your bot, see /help for a list of commands.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz_1234567

For a description of the Bot API, see this page: https://core.telegram.org/bots/api
```

**重要信息**：
- **Bot链接**：`t.me/your_bot_name`
- **Bot Token**：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz_1234567`

> **安全提示**：
> - ⚠️ **Bot Token是敏感信息**，相当于密码
> - ⚠️ 任何拥有Token的人都能控制您的Bot
> - ⚠️ 请勿在公开场合分享Token
> - ✅ 如果不慎泄露，可以使用 `/revoke` 命令重置

> **截图说明**：
> - [ ] 截图：创建成功的消息（Token部分打码）
> - [ ] 截图：完整的成功消息

**复制Token**：
1. 长按Token文本
2. 选择"复制"
3. 保存到安全位置（如密码管理器）

---

### 步骤5：将Bot添加到群组

Bot创建后，需要将其添加到目标群组才能发送消息。

#### 方法1：通过Bot链接添加

1. 点击BotFather消息中的Bot链接：`t.me/your_bot_name`
2. 打开Bot对话页面
3. 点击页面底部的 **"添加到群组"**（Add to Group）按钮
4. 选择目标群组
5. 点击"添加"

#### 方法2：在群组中手动添加

1. 打开目标群组
2. 点击群组名称，进入群组信息页面
3. 点击"添加成员"
4. 搜索您的Bot用户名（例如：`@kook_forward_bot`）
5. 点击添加

> **权限设置**：
> - Bot默认只有"发送消息"权限
> - 如需更多权限，在群组设置中调整

> **截图说明**：
> - [ ] 截图：Bot对话页面的"添加到群组"按钮
> - [ ] 截图：选择群组界面
> - [ ] 截图：Bot成功加入群组的提示

---

## 获取Chat ID

**Chat ID** 是群组的唯一标识符，用于指定消息发送目标。

### 方法1：使用转发系统自动获取（推荐）

1. 打开KOOK消息转发系统
2. 进入"机器人配置" → "Telegram"
3. 填入Bot Token
4. 点击 **"🔍 自动获取"** Chat ID按钮
5. 系统会自动检测并填入Chat ID

**工作原理**：
- 系统会调用Telegram API获取Bot加入的所有群组列表
- 自动选择最近活跃的群组
- 如有多个群组，会显示选择列表

> **截图说明**：
> - [ ] 截图：转发系统的"自动获取"按钮
> - [ ] 截图：自动获取成功的提示

---

### 方法2：手动获取（备用方法）

#### 步骤1：向群组发送任意消息

1. 在群组中发送任意消息（例如："测试"）
2. 或者让Bot发送一条消息（后面会测试）

#### 步骤2：调用Telegram API

使用浏览器或curl工具访问：
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

将 `<YOUR_BOT_TOKEN>` 替换为您的Bot Token。

**示例**：
```
https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz_1234567/getUpdates
```

#### 步骤3：查找Chat ID

API返回的JSON中，找到 `"chat"` 对象的 `"id"` 字段：

```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456789,
      "message": {
        "message_id": 1,
        "from": {...},
        "chat": {
          "id": -1001234567890,  // ← 这就是Chat ID
          "title": "游戏公告群",
          "type": "supergroup"
        },
        "text": "测试"
      }
    }
  ]
}
```

**Chat ID格式**：
- 私聊：正整数（例如：`123456789`）
- 群组：负整数（例如：`-1001234567890`）
- 超级群组：以 `-100` 开头的负整数

#### 步骤4：复制Chat ID

复制 `"id"` 字段的值（包括负号），例如：`-1001234567890`

> **截图说明**：
> - [ ] 截图：浏览器中访问API的结果
> - [ ] 截图：JSON中的Chat ID（用红框标注）

---

### 方法3：使用第三方Bot（最简单）

1. 将 `@userinfobot` 或 `@getidsbot` 添加到群组
2. 这些Bot会自动发送群组的Chat ID
3. 复制Chat ID
4. 将这些Bot从群组中移除（可选）

> **截图说明**：
> - [ ] 截图：@userinfobot 发送的Chat ID消息

---

## 测试Bot

### 在转发系统中测试

1. 打开KOOK消息转发系统
2. 进入"机器人配置" → "Telegram"
3. 填写Bot信息：
   - **Bot名称**：`游戏公告TG Bot`（备注用）
   - **Bot Token**：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz_1234567`
   - **Chat ID**：`-1001234567890`
4. 点击 **"🧪 测试连接"** 按钮

**预期结果**：
- ✅ 系统显示：`测试成功！已发送测试消息到目标平台`
- ✅ Telegram群组中收到一条测试消息

**测试消息示例**：
```
🧪 测试消息

这是一条测试消息，来自KOOK消息转发系统。
如果您看到这条消息，说明Telegram Bot配置成功！

⏰ 时间：2025-10-31 12:34:56
🤖 Bot：@kook_forward_bot
```

> **截图说明**：
> - [ ] 截图：转发系统的测试按钮
> - [ ] 截图：测试成功提示
> - [ ] 截图：Telegram群组中收到的测试消息

---

## 常见问题

### ❓ 1. 找不到BotFather

**解决方法**：
1. 确保输入的是 `@BotFather`（注意大小写）
2. 确保选择的是官方认证账号（带蓝色对勾✅）
3. 检查网络连接，确保能访问Telegram

---

### ❓ 2. Bot用户名被占用

**解决方法**：
1. 尝试在用户名后加数字，例如：`kook_forward_bot_2`
2. 使用更具体的名称，例如：`your_game_kook_bot`
3. 添加下划线，例如：`kook_forward_bot_official`

---

### ❓ 3. Token泄露了怎么办？

**解决方法**：
1. 立即与BotFather对话
2. 发送命令：`/revoke`
3. 选择您的Bot
4. BotFather会生成新的Token
5. 旧Token立即失效
6. 在转发系统中更新新Token

> **截图说明**：
> - [ ] 截图：/revoke 命令
> - [ ] 截图：选择Bot界面
> - [ ] 截图：新Token生成成功

---

### ❓ 4. 测试时提示"401 Unauthorized"

**可能原因**：
1. Bot Token错误或已失效
2. Token复制不完整
3. Token包含多余的空格

**解决方法**：
- 重新复制Token，确保完整
- 检查Token格式（格式：`数字:字母数字组合`）
- 如果确认无误，尝试重新生成Token

---

### ❓ 5. 测试时提示"Chat not found"

**可能原因**：
1. Chat ID错误
2. Bot未被添加到群组
3. Bot已被移出群组

**解决方法**：
- 确认Bot已添加到群组
- 重新获取Chat ID
- 检查Chat ID是否包含负号（群组Chat ID通常是负数）

---

### ❓ 6. Bot无法发送消息

**可能原因**：
1. Bot在群组中被禁言
2. Bot没有发送消息权限
3. 群组设置了隐私模式

**解决方法**：
1. 检查群组设置，确保Bot有发送权限
2. 联系群组管理员解除禁言
3. 使用 `/setprivacy` 命令关闭隐私模式：
   - 与BotFather对话
   - 发送 `/setprivacy`
   - 选择您的Bot
   - 选择 `Disable`

---

### ❓ 7. 能否同时向多个群组发送？

**答案**：
- ✅ **可以**！一个Bot可以同时加入多个群组
- 需要为每个群组配置独立的Bot实例

**操作方法**：
1. 将同一个Bot添加到多个群组
2. 获取每个群组的Chat ID
3. 在转发系统中添加多个Bot配置（相同Token，不同Chat ID）

---

### ❓ 8. 消息发送频率限制

**Telegram限制**：
- 每个Bot：**每秒最多30条消息**
- 向同一群组：**每分钟最多20条消息**
- 超限会返回 `429 Too Many Requests`

**转发系统的处理**：
- ✅ 自动限流：系统会自动控制发送速度
- ✅ 排队机制：超限消息会进入队列
- ✅ 智能重试：失败消息自动重试

---

### ❓ 9. 如何自定义Bot头像和简介？

**设置头像**：
1. 与BotFather对话
2. 发送命令：`/setuserpic`
3. 选择您的Bot
4. 上传图片（PNG、JPG格式，推荐512x512像素）

**设置简介**：
1. 与BotFather对话
2. 发送命令：`/setdescription`
3. 选择您的Bot
4. 输入简介文本（最多512字符）

**设置关于信息**：
1. 发送命令：`/setabouttext`
2. 选择您的Bot
3. 输入关于文本（最多120字符）

> **截图说明**：
> - [ ] 截图：/setuserpic 命令
> - [ ] 截图：上传头像
> - [ ] 截图：设置简介

---

### ❓ 10. 如何删除Bot？

**删除方法**：
1. 与BotFather对话
2. 发送命令：`/deletebot`
3. 选择要删除的Bot
4. 确认删除

> **警告**：
> - ⚠️ 删除后无法恢复
> - ⚠️ Bot用户名会被释放，可能被他人注册
> - ⚠️ 所有数据和Token会永久失效

---

## 🎉 总结

### 创建流程总结

| 步骤 | 操作 | 时间 |
|------|------|------|
| 1 | 打开BotFather | 10秒 |
| 2 | 发送 /newbot | 5秒 |
| 3 | 输入Bot名称 | 10秒 |
| 4 | 输入Bot用户名 | 10秒 |
| 5 | 复制Token | 5秒 |
| 6 | 添加到群组 | 20秒 |
| 7 | 获取Chat ID | 30秒 |
| **总计** | **约1.5分钟** | |

### 关键要点
1. ✅ Bot Token是敏感信息
2. ✅ Bot用户名必须以bot结尾
3. ✅ Chat ID是负数（群组）
4. ✅ 必须将Bot添加到群组
5. ⚠️ 注意频率限制

### 下一步
- ✅ 在转发系统中添加Bot
- ✅ 配置频道映射
- ✅ 启动转发服务

---

## 📞 需要帮助？

如果按照教程操作仍有问题：
1. 查看系统的 **FAQ** 页面
2. 查看 **视频教程**（更直观）
3. 访问 [Telegram Bot API官方文档](https://core.telegram.org/bots/api)

---

## 🔗 相关教程

- [Discord Webhook创建教程](./如何创建Discord_Webhook.md)
- [飞书自建应用教程](./如何配置飞书自建应用.md)
- [频道映射配置教程](./频道映射配置详解.md)

---

**最后更新时间**：2025-10-31  
**适用版本**：v18.0.0+  
**Telegram Bot API版本**：7.0
