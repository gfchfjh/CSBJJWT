# KOOK消息转发系统 - API接口文档

**版本**: v12.1.0 深度优化版  
**最后更新**: 2025-10-28  
**基础URL**: `http://localhost:15678`

---

## 📋 目录

1. [认证](#认证)
2. [v12.1.0新增API](#v121新增api)
3. [账号管理](#账号管理)
4. [Bot配置](#bot配置)
5. [频道映射](#频道映射)
6. [AI映射学习](#ai映射学习)
7. [消息去重](#消息去重)
8. [WebSocket管理](#websocket管理)
9. [消息日志](#消息日志)
10. [系统控制](#系统控制)
11. [环境检测](#环境检测)
12. [数据库优化](#数据库优化)
13. [图床服务](#图床服务)
14. [系统托盘](#系统托盘)

---

## 认证

所有API请求需要在Header中携带Token：

```http
X-API-Token: your_api_token_here
```

### 获取Token

```http
POST /api/auth/token
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

**响应**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

---

## v12.1.0新增API

### 消息去重API

#### 检查消息是否重复

```http
POST /api/v1/deduplicator/check
Content-Type: application/json

{
  "message_id": "msg_123456",
  "channel_id": "ch_789"
}
```

**响应**:
```json
{
  "is_duplicate": false,
  "message_id": "msg_123456"
}
```

#### 获取去重统计

```http
GET /api/v1/deduplicator/stats
```

**响应**:
```json
{
  "cache_size": 12450,
  "db_total": 45678,
  "cache_hit_rate": 0.99,
  "oldest_timestamp": "2025-10-21T10:30:00Z",
  "newest_timestamp": "2025-10-28T15:45:00Z"
}
```

### WebSocket管理API

#### 获取连接状态

```http
GET /api/v1/websocket/status
```

**响应**:
```json
{
  "status": "connected",
  "reconnect_count": 2,
  "last_heartbeat": "2025-10-28T15:45:30Z",
  "connected_at": "2025-10-28T10:00:00Z",
  "uptime_seconds": 20730
}
```

#### 手动触发重连

```http
POST /api/v1/websocket/reconnect
```

**响应**:
```json
{
  "success": true,
  "message": "重连成功",
  "new_status": "connected"
}
```

### AI映射学习API

#### 记录用户选择（学习）

```http
POST /api/v1/smart-mapping/learn
Content-Type: application/json

{
  "kook_channel": "游戏讨论",
  "target_channel": "gaming",
  "accepted": true
}
```

**响应**:
```json
{
  "success": true,
  "message": "学习记录已保存"
}
```

#### 获取智能推荐（4维评分）

```http
POST /api/v1/smart-mapping/recommend
Content-Type: application/json

{
  "kook_channel": "游戏讨论",
  "target_channels": ["gaming", "game-chat", "general"]
}
```

**响应**:
```json
{
  "recommendations": [
    {
      "target_channel": "gaming",
      "score": 0.92,
      "breakdown": {
        "exact_match": 0.0,
        "similarity": 0.85,
        "keyword_match": 1.0,
        "historical": 0.75
      }
    },
    {
      "target_channel": "game-chat",
      "score": 0.78,
      "breakdown": {
        "exact_match": 0.0,
        "similarity": 0.72,
        "keyword_match": 0.8,
        "historical": 0.6
      }
    }
  ]
}
```

### 安全图床API

#### 生成访问Token

```http
POST /api/v1/images/token
Content-Type: application/json

{
  "image_path": "images/msg_123456.png"
}
```

**响应**:
```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "url": "http://localhost:15679/image?token=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6&path=images/msg_123456.png",
  "expires_at": "2025-10-28T17:45:00Z"
}
```

#### 访问图片（需Token）

```http
GET /image?token=<TOKEN>&path=<PATH>
```

**安全验证**:
- ✅ Token验证（256位）
- ✅ IP白名单（127.0.0.1/::1/localhost）
- ✅ 路径遍历防护（检测../、~、/etc/）

### 系统托盘API

#### 获取托盘统计数据

```http
GET /api/v1/tray/stats
```

**响应**:
```json
{
  "total_forwarded": 1234,
  "success_rate": 0.985,
  "queue_size": 5,
  "service_status": "running"
}
```

---

## v11.0.0及之前API

### 环境检测API

#### 并发检测所有环境

```http
GET /api/environment/check
```

**响应**:
```json
{
  "elapsed": 8.5,
  "all_passed": true,
  "python": {
    "name": "Python版本",
    "passed": true,
    "current": "3.11.5",
    "required": "3.11+",
    "message": "✅ Python 3.11.5 符合要求"
  },
  "chromium": {
    "name": "Chromium浏览器",
    "passed": true,
    "message": "✅ Chromium 120.0.6099.109 已安装且可用"
  },
  "redis": {
    "name": "Redis服务",
    "passed": true,
    "message": "✅ Redis 6.2.14 运行正常"
  },
  "network": {
    "name": "网络连接",
    "passed": true,
    "success_count": 3,
    "total_count": 3,
    "message": "✅ 网络正常 (3/3可达)"
  },
  "ports": {
    "name": "端口可用性",
    "passed": true,
    "ports": [9527, 6379, 9528],
    "message": "✅ 所有端口可用"
  },
  "disk": {
    "name": "磁盘空间",
    "passed": true,
    "free_gb": 50.5,
    "required_gb": 5,
    "message": "✅ 磁盘空间充足 (50.50GB可用)"
  }
}
```

#### 自动修复环境问题

```http
POST /api/environment/fix/{check_name}
```

**路径参数**:
- `check_name`: `chromium` | `redis` | `ports`

**响应**:
```json
{
  "success": true,
  "message": "✅ Chromium安装成功"
}
```

#### 获取系统信息

```http
GET /api/environment/system-info
```

**响应**:
```json
{
  "os": "Windows",
  "os_version": "10.0.19045",
  "architecture": "AMD64",
  "python_version": "3.11.5",
  "hostname": "DESKTOP-XXX",
  "processor": "Intel64 Family 6 Model 158 Stepping 10, GenuineIntel"
}
```

---

### AI映射学习API

#### 获取AI推荐

```http
POST /api/mapping-learning/recommend
Content-Type: application/json

{
  "kook_channel": {
    "id": "123456",
    "name": "公告频道"
  },
  "target_channels": [
    {"id": "111", "name": "announcements", "platform": "discord"},
    {"id": "222", "name": "公告群", "platform": "telegram"},
    {"id": "333", "name": "通知群", "platform": "feishu"}
  ]
}
```

**响应**:
```json
[
  {
    "target_channel": {
      "id": "111",
      "name": "announcements",
      "platform": "discord"
    },
    "confidence": 0.95,
    "reason": "完全匹配 | 翻译匹配"
  },
  {
    "target_channel": {
      "id": "222",
      "name": "公告群",
      "platform": "telegram"
    },
    "confidence": 0.90,
    "reason": "完全匹配"
  }
]
```

#### 记录映射选择

```http
POST /api/mapping-learning/record
Content-Type: application/json

{
  "kook_channel_id": "123456",
  "target_channel_id": "111"
}
```

**响应**:
```json
{
  "success": true,
  "message": "已记录"
}
```

#### 获取学习统计

```http
GET /api/mapping-learning/stats
```

**响应**:
```json
{
  "total_mappings_learned": 50,
  "total_uses": 235,
  "most_used_mapping": {
    "kook_channel_id": "123456",
    "target_channel_id": "111",
    "use_count": 45
  },
  "translation_table_size": 15
}
```

#### 获取/更新翻译表

```http
GET /api/mapping-learning/translation-table
```

```http
POST /api/mapping-learning/translation-table
Content-Type: application/json

{
  "新词": ["new", "word"],
  "自定义": ["custom", "my-word"]
}
```

---

### 数据库优化API

#### 执行所有优化

```http
POST /api/database/optimize
```

**响应**:
```json
{
  "archive": {
    "success": true,
    "archived_count": 1234,
    "message": "已归档1234条日志"
  },
  "vacuum": {
    "success": true,
    "size_before_bytes": 104857600,
    "size_after_bytes": 73400320,
    "saved_bytes": 31457280,
    "saved_percent": 30.0,
    "message": "节省30.00 MB (30.0%)"
  },
  "analyze": {
    "success": true,
    "message": "分析完成"
  },
  "integrity": {
    "success": true,
    "result": "ok",
    "message": "数据库完整性正常"
  },
  "elapsed": 15.5
}
```

#### 归档旧日志

```http
POST /api/database/archive
```

#### VACUUM压缩

```http
POST /api/database/vacuum
```

#### 获取数据库信息

```http
GET /api/database/info
```

**响应**:
```json
{
  "path": "/path/to/config.db",
  "size_bytes": 104857600,
  "size_formatted": "100.00 MB",
  "modified_at": "2025-10-28T10:00:00",
  "total_records": 10000,
  "tables": {
    "message_logs": 8500,
    "accounts": 5,
    "bot_configs": 3,
    "channel_mappings": 15
  }
}
```

---

### 通知系统API

#### 发送通知

```http
POST /api/notifications/send
Content-Type: application/json

{
  "notification_type": "success",
  "title": "操作成功",
  "body": "配置已保存",
  "action": "/settings"
}
```

**通知类型**:
- `success`: 成功通知
- `warning`: 警告通知
- `error`: 错误通知
- `info`: 信息通知

#### 获取通知历史

```http
GET /api/notifications/history?limit=100&notification_type=warning
```

#### 清空通知历史

```http
DELETE /api/notifications/history
```

#### 获取通知统计

```http
GET /api/notifications/stats
```

**响应**:
```json
{
  "total": 1000,
  "success": 800,
  "warning": 150,
  "error": 50,
  "info": 0,
  "suppressed": 25,
  "history_count": 100,
  "quiet_time_enabled": true,
  "quiet_start": "22:00",
  "quiet_end": "08:00"
}
```

#### 获取/更新通知设置

```http
GET /api/notifications/settings
```

```http
POST /api/notifications/settings
Content-Type: application/json

{
  "enable_warning": true,
  "enable_error": true,
  "quiet_start": "22:00",
  "quiet_end": "08:00",
  "enable_quiet_time": true
}
```

---

### 图床服务API

#### 获取图片（需要Token）

```http
GET http://localhost:9528/images/{filename}?token={token}
```

**安全特性**:
- 32字节URL安全Token
- 2小时有效期
- Token与文件名绑定
- 仅允许本地访问
- 防止路径遍历攻击

#### 上传图片

```http
POST http://localhost:9528/api/images/upload
Content-Type: multipart/form-data

file: <binary>
```

**响应**:
```json
{
  "url": "http://localhost:9528/images/abc123.jpg?token=xyz...",
  "filename": "abc123.jpg",
  "token": "xyz...",
  "expires_in": 7200,
  "size": 1048576
}
```

#### 获取图床统计

```http
GET http://localhost:9528/api/images/stats
```

**响应**:
```json
{
  "total_tokens": 150,
  "expired_tokens": 20,
  "active_tokens": 130,
  "total_images": 500,
  "total_size_mb": 250.5,
  "max_size_gb": 10,
  "cleanup_days": 7
}
```

#### 撤销Token

```http
POST http://localhost:9528/api/images/token/revoke
Content-Type: application/json

{
  "token": "xyz..."
}
```

---

## 账号管理

### 获取所有账号

```http
GET /api/accounts
```

**响应**:
```json
[
  {
    "id": 1,
    "username": "user123",
    "status": "online",
    "cookie_expires_at": "2025-11-28T00:00:00",
    "last_active": "2025-10-28T10:00:00",
    "message_count": 1234
  }
]
```

### 添加账号

```http
POST /api/accounts
Content-Type: application/json

{
  "username": "user123",
  "cookies": [...],
  "password": "encrypted_password"
}
```

### 更新账号

```http
PUT /api/accounts/{account_id}
Content-Type: application/json

{
  "cookies": [...]
}
```

### 删除账号

```http
DELETE /api/accounts/{account_id}
```

### 测试账号连接

```http
POST /api/accounts/{account_id}/test
```

**响应**:
```json
{
  "success": true,
  "message": "连接成功",
  "latency_ms": 150
}
```

---

## Bot配置

### 获取所有Bot

```http
GET /api/bots
```

### 添加Bot

```http
POST /api/bots
Content-Type: application/json

{
  "name": "Discord Bot 1",
  "platform": "discord",
  "config": {
    "webhook_url": "https://discord.com/api/webhooks/..."
  }
}
```

### 更新Bot

```http
PUT /api/bots/{bot_id}
```

### 删除Bot

```http
DELETE /api/bots/{bot_id}
```

### 测试Bot连接

```http
POST /api/bots/{bot_id}/test
```

---

## 频道映射

### 获取所有映射

```http
GET /api/mappings
```

### 创建映射

```http
POST /api/mappings
Content-Type: application/json

{
  "kook_channel_id": "123456",
  "kook_channel_name": "公告频道",
  "target_platform": "discord",
  "target_channel_id": "789012",
  "target_channel_name": "announcements",
  "bot_id": 1
}
```

### 批量创建映射

```http
POST /api/mappings/batch
Content-Type: application/json

{
  "mappings": [
    {
      "kook_channel_id": "123456",
      "target_channel_id": "789012",
      "bot_id": 1
    },
    ...
  ]
}
```

### 更新映射

```http
PUT /api/mappings/{mapping_id}
```

### 删除映射

```http
DELETE /api/mappings/{mapping_id}
```

---

## 消息日志

### 获取日志

```http
GET /api/logs?page=1&page_size=50&status=success&start_date=2025-10-01&end_date=2025-10-28
```

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认50）
- `status`: 状态过滤（success/failed/pending）
- `start_date`: 开始日期
- `end_date`: 结束日期
- `kook_channel_id`: KOOK频道ID
- `target_platform`: 目标平台

**响应**:
```json
{
  "total": 1000,
  "page": 1,
  "page_size": 50,
  "logs": [
    {
      "id": 1,
      "kook_message_id": "msg123",
      "content": "测试消息",
      "sender_name": "用户A",
      "status": "success",
      "latency_ms": 150,
      "created_at": "2025-10-28T10:00:00"
    }
  ]
}
```

### 获取统计信息

```http
GET /api/logs/stats?period=today
```

**响应**:
```json
{
  "total_messages": 1000,
  "success_count": 950,
  "failed_count": 50,
  "success_rate": 0.95,
  "avg_latency_ms": 150,
  "platforms": {
    "discord": 400,
    "telegram": 350,
    "feishu": 200
  }
}
```

---

## 系统控制

### 启动服务

```http
POST /api/system/start
```

### 停止服务

```http
POST /api/system/stop
```

### 重启服务

```http
POST /api/system/restart
```

### 获取系统状态

```http
GET /api/system/status
```

**响应**:
```json
{
  "running": true,
  "uptime_seconds": 3600,
  "version": "11.0.0",
  "accounts_online": 5,
  "total_accounts": 5,
  "queue_size": 10,
  "today_messages": 1000,
  "success_rate": 0.95
}
```

### 测试转发

```http
POST /api/system/test-forward
Content-Type: application/json

{
  "message": "测试消息",
  "mapping_id": 1
}
```

### 清空队列

```http
POST /api/system/clear-queue
```

---

## WebSocket

### 连接

```
ws://localhost:9527/ws
```

### 实时消息

**服务器推送事件**:

```json
{
  "type": "message_forwarded",
  "data": {
    "message_id": "msg123",
    "status": "success",
    "latency_ms": 150
  }
}
```

```json
{
  "type": "account_status",
  "data": {
    "account_id": 1,
    "status": "online"
  }
}
```

```json
{
  "type": "system_notification",
  "data": {
    "title": "账号掉线",
    "body": "账号user123已掉线",
    "level": "warning"
  }
}
```

---

## 错误响应

所有API错误响应格式：

```json
{
  "detail": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-10-28T10:00:00"
}
```

**常见错误码**:
- `AUTH_FAILED`: 认证失败
- `NOT_FOUND`: 资源不存在
- `VALIDATION_ERROR`: 参数验证失败
- `INTERNAL_ERROR`: 内部错误
- `RATE_LIMIT_EXCEEDED`: 请求频率超限

**HTTP状态码**:
- `200`: 成功
- `400`: 参数错误
- `401`: 未认证
- `403`: 无权限
- `404`: 不存在
- `500`: 服务器错误

---

## 速率限制

- 默认限制：100请求/分钟
- WebSocket连接：5个/客户端
- 文件上传：10MB/文件

---

## 示例代码

### Python

```python
import requests

# 获取Token
response = requests.post(
    'http://localhost:9527/api/auth/token',
    json={'username': 'admin', 'password': 'password'}
)
token = response.json()['token']

# 使用Token
headers = {'X-API-Token': token}
response = requests.get(
    'http://localhost:9527/api/accounts',
    headers=headers
)
accounts = response.json()
```

### JavaScript

```javascript
// 获取Token
const response = await fetch('http://localhost:9527/api/auth/token', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'password'})
});
const {token} = await response.json();

// 使用Token
const accounts = await fetch('http://localhost:9527/api/accounts', {
  headers: {'X-API-Token': token}
}).then(r => r.json());
```

---

<div align="center">
  <p><strong>v11.0.0 API Documentation</strong></p>
  <p>Made with ❤️ by KOOK Forwarder Team</p>
</div>
