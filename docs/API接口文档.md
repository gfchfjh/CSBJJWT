# KOOK消息转发系统 - API接口文档

**版本**: v1.11.0  
**基础URL**: `http://localhost:9527`  
**协议**: HTTP/1.1  
**编码**: UTF-8  

---

## 🔐 认证

所有API请求需要在Header中携带API Token（如果启用）:

\`\`\`http
X-API-Token: your_api_token_here
\`\`\`

**获取Token**:
1. 在\`.env\`文件中设置\`API_TOKEN\`
2. 或通过登录接口获取

---

## 📋 API索引

- [账号管理API](#账号管理api)
- [Bot配置API](#bot配置api)
- [频道映射API](#频道映射api)
- [日志查询API](#日志查询api)
- [系统控制API](#系统控制api)
- [认证API](#认证api)
- [备份API](#备份api)
- [智能映射API](#智能映射api)
- [健康检查API](#健康检查api)
- [更新检查API](#更新检查api)
- [WebSocket API](#websocket-api)

---

## 账号管理API

### 1. 获取所有账号

\`\`\`http
GET /api/accounts
\`\`\`

**响应示例**:
\`\`\`json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "email": "user@example.com",
      "status": "online",
      "last_active": "2025-10-19T15:30:00",
      "created_at": "2025-10-01T10:00:00"
    }
  ]
}
\`\`\`

### 2. 添加账号

\`\`\`http
POST /api/accounts
Content-Type: application/json

{
  "email": "user@example.com",
  "cookie": "[{\"name\":\"token\",\"value\":\"xxx\",\"domain\":\".kookapp.cn\"}]"
}
\`\`\`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | KOOK账号邮箱 |
| cookie | string | 否 | Cookie JSON字符串 |
| password | string | 否 | 账号密码 |

**响应示例**:
\`\`\`json
{
  "success": true,
  "message": "账号添加成功",
  "account_id": 2
}
\`\`\`

### 3. 删除账号

\`\`\`http
DELETE /api/accounts/{account_id}
\`\`\`

**响应**: 204 No Content

### 4. 启动抓取器

\`\`\`http
POST /api/accounts/{account_id}/start
\`\`\`

**响应示例**:
\`\`\`json
{
  "success": true,
  "message": "抓取器启动成功"
}
\`\`\`

### 5. 停止抓取器

\`\`\`http
POST /api/accounts/{account_id}/stop
\`\`\`

### 6. 获取服务器列表

\`\`\`http
GET /api/accounts/{account_id}/servers
\`\`\`

**响应示例**:
\`\`\`json
{
  "success": true,
  "servers": [
    {
      "id": "1234567890",
      "name": "游戏公会",
      "icon": "https://..."
    }
  ]
}
\`\`\`

### 7. 获取频道列表

\`\`\`http
GET /api/accounts/{account_id}/channels?server_id=1234567890
\`\`\`

**响应示例**:
\`\`\`json
{
  "success": true,
  "channels": [
    {
      "id": "9876543210",
      "name": "公告频道",
      "type": "text",
      "server_id": "1234567890"
    }
  ]
}
\`\`\`

---

## Bot配置API

### 1. 获取Bot列表

\`\`\`http
GET /api/bots?platform=discord
\`\`\`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| platform | string | 否 | 平台过滤 (discord/telegram/feishu) |

**响应示例**:
\`\`\`json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "platform": "discord",
      "name": "游戏公告Bot",
      "config": {
        "webhook_url": "https://discord.com/api/webhooks/..."
      },
      "status": "active",
      "created_at": "2025-10-01T10:00:00"
    }
  ]
}
\`\`\`

### 2. 添加Discord Bot

\`\`\`http
POST /api/bots
Content-Type: application/json

{
  "platform": "discord",
  "name": "测试Discord Bot",
  "config": {
    "webhook_url": "https://discord.com/api/webhooks/123456/abc..."
  }
}
\`\`\`

### 3. 添加Telegram Bot

\`\`\`http
POST /api/bots
Content-Type: application/json

{
  "platform": "telegram",
  "name": "测试Telegram Bot",
  "config": {
    "bot_token": "123456:ABC-DEF...",
    "chat_id": "-1001234567890"
  }
}
\`\`\`

### 4. 添加飞书Bot

\`\`\`http
POST /api/bots
Content-Type: application/json

{
  "platform": "feishu",
  "name": "测试飞书Bot",
  "config": {
    "app_id": "cli_abc123",
    "app_secret": "secret_xyz789"
  }
}
\`\`\`

### 5. 测试Bot连接

\`\`\`http
POST /api/bots/{bot_id}/test
\`\`\`

**响应示例**:
\`\`\`json
{
  "success": true,
  "message": "测试消息发送成功",
  "latency_ms": 234
}
\`\`\`

### 6. 删除Bot

\`\`\`http
DELETE /api/bots/{bot_id}
\`\`\`

---

## 频道映射API

### 1. 获取映射列表

\`\`\`http
GET /api/mappings
\`\`\`

**响应示例**:
\`\`\`json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "kook_server_id": "1234567890",
      "kook_channel_id": "9876543210",
      "kook_channel_name": "公告频道",
      "target_platform": "discord",
      "target_bot_id": 1,
      "target_channel_id": "discord_channel_123",
      "enabled": 1
    }
  ]
}
\`\`\`

### 2. 添加映射

\`\`\`http
POST /api/mappings
Content-Type: application/json

{
  "kook_server_id": "1234567890",
  "kook_channel_id": "9876543210",
  "kook_channel_name": "公告频道",
  "target_platform": "discord",
  "target_bot_id": 1,
  "target_channel_id": "discord_channel_123"
}
\`\`\`

### 3. 批量添加映射

\`\`\`http
POST /api/mappings/batch
Content-Type: application/json

{
  "mappings": [
    {...},
    {...}
  ]
}
\`\`\`

### 4. 更新映射

\`\`\`http
PUT /api/mappings/{mapping_id}
Content-Type: application/json

{
  "enabled": 0
}
\`\`\`

### 5. 删除映射

\`\`\`http
DELETE /api/mappings/{mapping_id}
\`\`\`

### 6. 导出映射配置

\`\`\`http
GET /api/mappings/export
\`\`\`

**响应示例**:
\`\`\`json
{
  "version": "1.0",
  "export_time": "2025-10-19T15:30:00",
  "mappings": [...]
}
\`\`\`

### 7. 导入映射配置

\`\`\`http
POST /api/mappings/import
Content-Type: application/json

{
  "mappings": [...]
}
\`\`\`

---

## 日志查询API

### 1. 获取消息日志

\`\`\`http
GET /api/logs?limit=100&status=success&platform=discord
\`\`\`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | integer | 否 | 返回数量，默认100 |
| status | string | 否 | 状态过滤 (success/failed/pending) |
| platform | string | 否 | 平台过滤 (discord/telegram/feishu) |
| channel_id | string | 否 | 频道ID过滤 |

**响应示例**:
\`\`\`json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "kook_message_id": "msg_123",
      "kook_channel_id": "channel_456",
      "content": "测试消息",
      "message_type": "text",
      "sender_name": "用户A",
      "target_platform": "discord",
      "target_channel": "discord_ch_789",
      "status": "success",
      "error_message": null,
      "latency_ms": 1234,
      "created_at": "2025-10-19T15:30:00"
    }
  ],
  "total": 1234,
  "page": 1
}
\`\`\`

### 2. 获取统计信息

\`\`\`http
GET /api/logs/stats?period=today
\`\`\`

**查询参数**:
- \`period\`: today/week/month

**响应示例**:
\`\`\`json
{
  "total": 1234,
  "success": 1200,
  "failed": 34,
  "success_rate": 97.2,
  "avg_latency_ms": 1234,
  "by_platform": {
    "discord": 600,
    "telegram": 400,
    "feishu": 234
  }
}
\`\`\`

### 3. 清除旧日志

\`\`\`http
POST /api/logs/clear?days=30
\`\`\`

---

## 系统控制API

### 1. 获取系统状态

\`\`\`http
GET /api/system/status
\`\`\`

**响应示例**:
\`\`\`json
{
  "service_running": true,
  "redis_connected": true,
  "queue_size": 5,
  "account_count": 2,
  "active_accounts": 2,
  "bot_count": 3,
  "mapping_count": 6,
  "uptime_seconds": 3600,
  "version": "1.8.1"
}
\`\`\`

### 2. 启动服务

\`\`\`http
POST /api/system/start
\`\`\`

### 3. 停止服务

\`\`\`http
POST /api/system/stop
\`\`\`

### 4. 重启服务

\`\`\`http
POST /api/system/restart
\`\`\`

### 5. 获取缓存统计

\`\`\`http
GET /api/cache/stats
\`\`\`

**响应示例** (v1.8.0):
\`\`\`json
{
  "cache_size": 1234,
  "hit_rate": 0.85,
  "miss_rate": 0.15,
  "total_hits": 5000,
  "total_misses": 882
}
\`\`\`

---

## 认证API

### 1. 登录

\`\`\`http
POST /api/auth/login
Content-Type: application/json

{
  "password": "your_password"
}
\`\`\`

**响应示例**:
\`\`\`json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 2592000
}
\`\`\`

### 2. 验证Token

\`\`\`http
POST /api/auth/verify
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
\`\`\`

### 3. 修改密码

\`\`\`http
POST /api/auth/change-password
Content-Type: application/json

{
  "old_password": "old_pass",
  "new_password": "new_pass"
}
\`\`\`

---

## 备份API

### 1. 创建备份

\`\`\`http
POST /api/backup/create
\`\`\`

**响应示例**:
\`\`\`json
{
  "success": true,
  "backup_id": "backup_20251019_153000",
  "backup_path": "/path/to/backup.zip",
  "size_mb": 2.5
}
\`\`\`

### 2. 获取备份列表

\`\`\`http
GET /api/backup/list
\`\`\`

### 3. 恢复备份

\`\`\`http
POST /api/backup/restore
Content-Type: application/json

{
  "backup_id": "backup_20251019_153000"
}
\`\`\`

---

## 智能映射API

### 1. 获取KOOK服务器列表

\`\`\`http
GET /api/smart-mapping/kook-servers?account_id=1
\`\`\`

### 2. 获取KOOK频道列表

\`\`\`http
GET /api/smart-mapping/kook-channels?account_id=1&server_id=1234567890
\`\`\`

### 3. 自动匹配频道

\`\`\`http
POST /api/smart-mapping/auto-match
Content-Type: application/json

{
  "account_id": 1,
  "platform": "discord"
}
\`\`\`

---

## 健康检查API

### 1. 基础健康检查

\`\`\`http
GET /health
\`\`\`

**响应**: \`{"status": "healthy"}\`

### 2. 详细健康检查

\`\`\`http
GET /api/health/check
\`\`\`

**响应示例**:
\`\`\`json
{
  "status": "healthy",
  "components": {
    "redis": {"status": "up", "latency_ms": 5},
    "database": {"status": "up"},
    "worker": {"status": "running"},
    "scrapers": {"total": 2, "active": 2}
  },
  "timestamp": "2025-10-19T15:30:00"
}
\`\`\`

---

## 更新检查API

### 1. 检查更新

\`\`\`http
GET /api/updates/check
\`\`\`

**响应示例**:
\`\`\`json
{
  "current_version": "1.8.1",
  "latest_version": "1.8.2",
  "update_available": true,
  "release_notes": "...",
  "download_url": "https://..."
}
\`\`\`

---

## WebSocket API

### 连接WebSocket

\`\`\`javascript
const ws = new WebSocket('ws://localhost:9527/ws');

ws.onopen = () => {
  console.log('WebSocket连接成功');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data);
  
  // 消息类型
  if (data.type === 'log') {
    // 实时日志
    console.log('日志:', data.data);
  } else if (data.type === 'status') {
    // 状态更新
    console.log('状态:', data.data);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket错误:', error);
};

ws.onclose = () => {
  console.log('WebSocket连接关闭');
};
\`\`\`

**推送消息格式**:
\`\`\`json
{
  "type": "log",
  "data": {
    "message_id": "msg_123",
    "status": "success",
    "content": "测试消息",
    "latency_ms": 1200,
    "platform": "discord",
    "timestamp": "2025-10-19T15:30:00"
  }
}
\`\`\`

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 422 | 验证失败 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

**错误响应格式**:
\`\`\`json
{
  "success": false,
  "error_code": "INVALID_COOKIE",
  "error_message": "Cookie格式无效",
  "solution": "请检查Cookie格式是否为有效的JSON数组",
  "timestamp": "2025-10-19T15:30:00"
}
\`\`\`

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19  
**对应代码版本**: v1.8.1
