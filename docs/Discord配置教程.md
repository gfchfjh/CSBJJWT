# Discord配置教程

**更新日期**: 2025-10-21  
**难度**: ⭐☆☆☆☆ (非常简单)  
**预计耗时**: 2-3分钟

## 🎉 v1.12.0 新特性

- ✨ **性能监控**: 实时查看Discord转发统计
- ✨ **配置模板**: 一键应用Discord预设配置
- ✨ **视频教程**: 完整的视频录制脚本已就绪

---

## 📖 目录
1. [创建Webhook](#创建webhook)
2. [获取频道ID](#获取频道id)
3. [测试配置](#测试配置)
4. [常见问题](#常见问题)

---

## 创建Webhook

### 步骤1: 进入服务器设置

![](https://via.placeholder.com/800x400?text=Discord+Server+Settings)

1. 打开Discord桌面应用或网页版
2. 进入你的服务器
3. 右键点击目标频道
4. 选择 **编辑频道**

### 步骤2: 创建Webhook

![](https://via.placeholder.com/800x400?text=Create+Webhook)

1. 在频道设置中，选择左侧的 **集成** 标签
2. 找到 **Webhooks** 部分
3. 点击 **新建Webhook** 按钮

### 步骤3: 配置Webhook

![](https://via.placeholder.com/800x400?text=Configure+Webhook)

1. **设置名称**: 例如"KOOK转发机器人"
2. **设置头像**: 上传机器人头像（可选）
3. **选择频道**: 确认目标频道正确
4. 点击 **复制Webhook URL**

### 步骤4: 保存Webhook URL

Webhook URL格式示例：
```
https://discord.com/api/webhooks/1234567890/AbCdEfGhIjKlMnOpQrStUvWxYz123456
```

**⚠️ 重要**: 
- 这个URL包含密钥，请妥善保管
- 不要在公开场合分享
- 如果泄露，请立即删除并重新创建

---

## 获取频道ID

某些高级配置需要频道ID。

### 方法1: 启用开发者模式

![](https://via.placeholder.com/800x400?text=Developer+Mode)

1. **用户设置** → **高级** → 开启 **开发者模式**
2. 右键点击频道
3. 选择 **复制频道ID**

### 方法2: 从URL获取

在网页版Discord中，频道URL格式为：
```
https://discord.com/channels/服务器ID/频道ID
```

例如：
```
https://discord.com/channels/123456789012345678/987654321098765432
```

频道ID就是最后的数字：`987654321098765432`

---

## 测试配置

### 在KOOK转发系统中测试

1. 在"机器人配置"页面
2. 找到你创建的Discord Bot
3. 点击 **测试连接** 按钮
4. 在Discord频道中查看测试消息

### 测试消息示例

如果配置正确，你会在Discord频道看到：

```
✅ KOOK消息转发系统测试消息

如果您看到这条消息，说明Webhook配置成功！
```

### 手动测试（可选）

使用curl命令测试：

```bash
curl -X POST "https://discord.com/api/webhooks/你的Webhook_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "测试消息",
    "username": "KOOK转发Bot"
  }'
```

---

## 常见问题

### Q: Webhook URL无效怎么办？

**A**: 
1. 检查URL是否完整复制
2. 确认Webhook未被删除
3. 重新创建Webhook

### Q: 消息没有显示头像和用户名？

**A**: 
这是正常的！普通Webhook消息会显示：
- 默认头像（如果未设置）
- "KOOK转发"作为用户名

你可以在创建Webhook时自定义头像。

### Q: 如何修改Webhook？

**A**:
1. 进入频道设置 → 集成
2. 找到对应的Webhook
3. 点击编辑
4. 修改名称、头像等
5. 点击保存

### Q: 如何删除Webhook？

**A**:
1. 进入频道设置 → 集成
2. 找到对应的Webhook
3. 点击删除
4. 确认删除

**⚠️ 注意**: 删除后原URL将失效，需要更新配置！

### Q: Webhook有消息数量限制吗？

**A**: 
是的，Discord有限流限制：
- 每5秒最多5条消息
- 超过限制会返回 `429 Too Many Requests`
- KOOK转发系统已自动处理限流

### Q: 能不能在一个频道创建多个Webhook？

**A**: 
可以！一个频道可以有最多10个Webhook。

用途示例：
```
频道#公告:
├─ Webhook1: KOOK转发
├─ Webhook2: GitHub通知
└─ Webhook3: 其他服务
```

### Q: Webhook消息能@所有人吗？

**A**: 
可以，但需要特殊权限！

普通Webhook默认**不能** @everyone 或 @here。

如需此功能：
1. 联系服务器管理员
2. 在 服务器设置 → 角色 中
3. 给Webhook角色添加"提及所有人"权限

---

## 高级配置

### 使用Embed富文本

Webhook支持发送富文本消息（Embed）：

```json
{
  "content": "主要内容",
  "embeds": [{
    "title": "标题",
    "description": "描述",
    "color": 5814783,
    "fields": [
      {
        "name": "字段1",
        "value": "值1"
      }
    ]
  }]
}
```

KOOK转发系统在转发图片时会自动使用Embed。

### 自定义头像和用户名

每条消息都可以覆盖默认设置：

```json
{
  "content": "消息内容",
  "username": "自定义用户名",
  "avatar_url": "https://example.com/avatar.png"
}
```

KOOK转发系统会自动使用KOOK用户的名称和头像。

---

## 安全建议

### ✅ 最佳实践

1. **定期更换Webhook**: 建议每月更换一次
2. **限制权限**: 只给需要的频道创建Webhook
3. **监控日志**: 定期检查是否有异常调用
4. **备份URL**: 保存Webhook URL到安全的地方

### ⚠️ 安全警告

**不要**:
- ❌ 在公开代码中硬编码Webhook URL
- ❌ 在截图/视频中展示完整URL
- ❌ 分享给不信任的人
- ❌ 在公共频道讨论URL

**如果泄露**:
1. 立即删除Webhook
2. 创建新的Webhook
3. 更新所有使用该URL的地方

---

## 参考资料

- [Discord官方Webhook文档](https://discord.com/developers/docs/resources/webhook)
- [Discord开发者门户](https://discord.com/developers/applications)
- [Embed可视化工具](https://leovoel.github.io/embed-visualizer/)

---

**配置完成！** 🎉

返回 [完整用户手册](./完整用户手册.md)
