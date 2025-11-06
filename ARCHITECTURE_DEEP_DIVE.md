# KOOK消息转发系统 - 深度架构文档

**文档版本**: 2.0  
**系统版本**: v18.0.3  
**更新日期**: 2025-11-06

---

## 📐 系统架构概览

### 1. 三层架构设计

```
┌──────────────────────────────────────────────────────────┐
│                    表示层 (Presentation)                  │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Electron   │  │  Vue 3 前端  │  │ Chrome扩展   │     │
│  │ 主进程     │  │  (用户界面)  │  │  (Cookie)    │     │
│  └────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────▼─────────────────────────────────┐
│                    业务逻辑层 (Business)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  API层   │ │ 处理器   │ │ 转发器   │ │ 插件系统 │   │
│  │ (150+端点│ │ (消息)   │ │ (5平台)  │ │ (扩展)   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│                    数据层 (Data)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ SQLite   │ │  Redis   │ │  KOOK    │ │  文件    │   │
│  │ (配置)   │ │ (队列)   │ │ (消息)   │ │ (图片)   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 2. 进程架构

```
┌─────────────────────────────────────────────────────┐
│            Electron 主进程 (Node.js)                │
│  - 窗口管理                                         │
│  - 托盘图标                                         │
│  - IPC通信                                          │
│  - 子进程管理                                       │
└────────┬──────────────────┬─────────────────────────┘
         │                  │
    ┌────▼────┐        ┌────▼────┐
    │ Redis   │        │ Backend │
    │ Process │        │ Process │
    │ (6379)  │        │ (9527)  │
    └─────────┘        └────┬────┘
                            │
                    ┌───────┴────────┐
                    │                │
            ┌───────▼──────┐ ┌──────▼──────┐
            │ Playwright   │ │  Worker     │
            │ Browser      │ │  Tasks      │
            └──────────────┘ └─────────────┘
```

---

## 🔄 数据流分析

### 1. 消息处理完整流程

```
┌──────────┐
│ KOOK服务器│
└─────┬────┘
      │ WebSocket
      │
┌─────▼────────────────────────────────────────────────┐
│ 1. 消息采集 (KookScraper)                            │
│    - Playwright浏览器                                 │
│    - WebSocket监听                                    │
│    - 消息解析                                         │
└─────┬────────────────────────────────────────────────┘
      │
┌─────▼────────────────────────────────────────────────┐
│ 2. 消息入队 (RedisQueue)                             │
│    - 序列化 (JSON)                                    │
│    - Redis RPUSH                                      │
│    - 本地Fallback (可选)                              │
└─────┬────────────────────────────────────────────────┘
      │
┌─────▼────────────────────────────────────────────────┐
│ 3. 消息出队 (MessageWorker)                          │
│    - Redis BLPOP (批量10条)                           │
│    - 反序列化                                         │
│    - 任务分发                                         │
└─────┬────────────────────────────────────────────────┘
      │
┌─────▼────────────────────────────────────────────────┐
│ 4. 消息处理 (MessageProcessor)                       │
│    ├─ 去重检查 (Redis Hash)                          │
│    ├─ 过滤规则 (FilterEngine)                        │
│    ├─ 格式转换 (Formatter)                           │
│    ├─ 媒体处理 (ImageProcessor/VideoProcessor)      │
│    └─ 插件钩子 (PluginSystem)                        │
└─────┬────────────────────────────────────────────────┘
      │
┌─────▼────────────────────────────────────────────────┐
│ 5. 映射查询 (Database)                               │
│    - 查询channel_mappings表                          │
│    - 获取目标平台和Bot配置                           │
│    - 返回映射列表                                    │
└─────┬────────────────────────────────────────────────┘
      │
┌─────▼────────────────────────────────────────────────┐
│ 6. 消息转发 (Forwarders)                             │
│    ├─ Discord (DiscordForwarder)                     │
│    ├─ Telegram (TelegramForwarder)                   │
│    ├─ 飞书 (FeishuForwarder)                         │
│    ├─ 企业微信 (WeChatWorkForwarder)                 │
│    └─ 钉钉 (DingTalkForwarder)                       │
└─────┬────────────────────────────────────────────────┘
      │
┌─────▼────────────────────────────────────────────────┐
│ 7. 结果处理                                          │
│    ├─ 成功: 记录日志 (message_logs)                  │
│    ├─ 失败: 加入重试队列 (failed_messages)           │
│    └─ 指标: 更新统计 (Metrics)                       │
└──────────────────────────────────────────────────────┘
```

### 2. 用户操作流程

```
┌──────────┐
│ 用户操作 │
└─────┬────┘
      │
┌─────▼──────────────────────────────────────┐
│ 前端操作 (Vue 3)                            │
│  - 表单输入                                  │
│  - 按钮点击                                  │
│  - 页面导航                                  │
└─────┬──────────────────────────────────────┘
      │ HTTP Request
      │ (axios)
┌─────▼──────────────────────────────────────┐
│ API路由 (FastAPI)                           │
│  - 认证检查                                  │
│  - 参数验证                                  │
│  - 路由分发                                  │
└─────┬──────────────────────────────────────┘
      │
┌─────▼──────────────────────────────────────┐
│ 业务逻辑                                    │
│  - 数据处理                                  │
│  - 业务规则                                  │
│  - 外部调用                                  │
└─────┬──────────────────────────────────────┘
      │
┌─────▼──────────────────────────────────────┐
│ 数据持久化                                  │
│  - SQLite写入                                │
│  - Redis缓存                                 │
│  - 文件存储                                  │
└─────┬──────────────────────────────────────┘
      │ HTTP Response
      │ (JSON)
┌─────▼──────────────────────────────────────┐
│ 前端响应                                    │
│  - 数据更新                                  │
│  - UI刷新                                    │
│  - 提示反馈                                  │
└─────────────────────────────────────────────┘
```

---

## 🗄️ 数据模型详解

### 1. 核心数据表

#### accounts (账号表)

```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,          -- KOOK账号邮箱
    password_encrypted TEXT,              -- 加密后的密码
    cookie TEXT,                         -- Cookie JSON
    status TEXT DEFAULT 'offline',       -- online/offline/error
    last_active TIMESTAMP,               -- 最后活跃时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_accounts_email ON accounts(email);
CREATE INDEX idx_accounts_status ON accounts(status);
```

**数据关系**: 1个账号 → N个Scraper实例

#### bot_configs (机器人配置表)

```sql
CREATE TABLE bot_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,              -- discord/telegram/feishu/wechatwork/dingtalk
    name TEXT NOT NULL,                  -- Bot名称
    config TEXT NOT NULL,                -- 配置JSON
    status TEXT DEFAULT 'active',        -- active/inactive
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**配置JSON结构**:
```json
{
  "discord": {
    "webhook_url": "https://discord.com/api/webhooks/...",
    "username": "KOOK转发",
    "avatar_url": "..."
  },
  "telegram": {
    "bot_token": "123456:ABC-DEF...",
    "chat_id": "-100123456789"
  },
  "feishu": {
    "app_id": "cli_xxx",
    "app_secret": "xxx",
    "webhook_url": "..."
  }
}
```

#### channel_mappings (频道映射表)

```sql
CREATE TABLE channel_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kook_server_id TEXT NOT NULL,        -- KOOK服务器ID
    kook_channel_id TEXT NOT NULL,       -- KOOK频道ID
    kook_channel_name TEXT NOT NULL,     -- KOOK频道名称
    target_platform TEXT NOT NULL,       -- 目标平台
    target_bot_id INTEGER NOT NULL,      -- 目标Bot ID
    target_channel_id TEXT NOT NULL,     -- 目标频道ID
    enabled INTEGER DEFAULT 1,           -- 启用状态
    FOREIGN KEY (target_bot_id) REFERENCES bot_configs(id)
);

-- 性能索引
CREATE INDEX idx_channel_mappings_kook_channel 
ON channel_mappings(kook_channel_id, enabled);

CREATE INDEX idx_mapping_bot_platform 
ON channel_mappings(target_bot_id, target_platform);
```

**映射查询优化**:
```python
# 单频道查询 (O(1))
mappings = db.execute(
    "SELECT * FROM channel_mappings WHERE kook_channel_id = ? AND enabled = 1",
    (channel_id,)
).fetchall()
```

#### message_logs (消息日志表)

```sql
CREATE TABLE message_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kook_message_id TEXT NOT NULL UNIQUE,  -- KOOK消息ID
    kook_channel_id TEXT NOT NULL,         -- KOOK频道ID
    content TEXT,                          -- 消息内容
    message_type TEXT,                     -- text/image/video/file
    sender_name TEXT,                      -- 发送者
    target_platform TEXT,                  -- 目标平台
    target_channel TEXT,                   -- 目标频道
    status TEXT,                           -- success/failed/pending
    error_message TEXT,                    -- 错误信息
    latency_ms INTEGER,                    -- 延迟(毫秒)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 查询索引
CREATE INDEX idx_message_logs_kook_id ON message_logs(kook_message_id);
CREATE INDEX idx_message_logs_status ON message_logs(status);
CREATE INDEX idx_message_logs_created ON message_logs(created_at DESC);

-- 复合索引
CREATE INDEX idx_logs_channel_status 
ON message_logs(kook_channel_id, status, created_at DESC);
```

**查询性能**:
- 单消息查询: O(1) (唯一索引)
- 状态查询: O(log n) (B-Tree索引)
- 时间范围查询: O(log n + k)

### 2. Redis数据结构

#### 消息队列

```redis
# 主队列
LIST kook_messages
  - JSON序列化的消息对象
  - RPUSH入队, BLPOP出队
  - 支持批量出队

# 失败重试队列
LIST retry_messages
  - 失败消息暂存
  - 指数退避重试

# 死信队列
LIST dead_letter_messages
  - 多次失败的消息
  - 人工介入处理
```

#### 消息去重

```redis
# 去重哈希表
HASH message_dedup
  key: kook_message_id
  value: timestamp
  TTL: 86400秒 (24小时)

# 快速判断
EXISTS message_dedup:{message_id}
```

#### 速率限制

```redis
# Token Bucket算法
STRING rate_limit:discord:{webhook_id}
  value: current_tokens
  TTL: 动态计算

# Sliding Window算法
ZSET rate_limit:telegram:{bot_id}
  member: timestamp
  score: timestamp
```

---

## 🔌 API接口详解

### 1. 认证相关API

#### POST /api/auth/login
```python
# 登录认证
Request:
{
  "password": "用户密码"
}

Response:
{
  "token": "JWT Token",
  "expires_in": 86400,
  "user_info": {...}
}
```

#### POST /api/auth/set-password
```python
# 设置主密码 (首次运行)
Request:
{
  "password": "新密码",
  "confirm_password": "确认密码"
}

Response:
{
  "success": true,
  "message": "密码设置成功"
}
```

### 2. 账号管理API

#### GET /api/accounts
```python
# 获取账号列表
Response:
[
  {
    "id": 1,
    "email": "user@example.com",
    "status": "online",
    "last_active": "2025-11-06T10:30:00",
    "created_at": "2025-11-01T08:00:00"
  }
]
```

#### POST /api/accounts
```python
# 添加账号
Request:
{
  "email": "user@example.com",
  "password": "密码" (可选),
  "cookie": "Cookie JSON" (可选)
}

Response:
{
  "id": 1,
  "email": "user@example.com",
  "status": "offline"
}
```

#### POST /api/accounts/{id}/start
```python
# 启动账号监听
Response:
{
  "success": true,
  "scraper_id": "scraper_1",
  "status": "starting"
}
```

### 3. 机器人配置API

#### GET /api/bots
```python
# 获取Bot列表
Response:
[
  {
    "id": 1,
    "platform": "discord",
    "name": "Discord Bot 1",
    "config": {
      "webhook_url": "https://..."
    },
    "status": "active"
  }
]
```

#### POST /api/bots
```python
# 添加Bot配置
Request:
{
  "platform": "discord",
  "name": "My Discord Bot",
  "config": {
    "webhook_url": "https://discord.com/api/webhooks/..."
  }
}
```

#### POST /api/bots/{id}/test
```python
# 测试Bot连接
Response:
{
  "success": true,
  "message": "测试消息发送成功",
  "latency_ms": 230
}
```

### 4. 频道映射API

#### GET /api/mappings
```python
# 获取映射列表
Response:
[
  {
    "id": 1,
    "kook_server_id": "123456",
    "kook_channel_id": "789012",
    "kook_channel_name": "#公告",
    "target_platform": "discord",
    "target_bot_id": 1,
    "target_channel_id": "987654321",
    "enabled": true
  }
]
```

#### POST /api/mappings
```python
# 创建映射
Request:
{
  "kook_server_id": "123456",
  "kook_channel_id": "789012",
  "kook_channel_name": "#公告",
  "target_platform": "discord",
  "target_bot_id": 1,
  "target_channel_id": "987654321"
}
```

#### POST /api/mappings/batch
```python
# 批量创建映射
Request:
{
  "mappings": [
    {...},
    {...}
  ]
}

Response:
{
  "success": 15,
  "failed": 2,
  "total": 17
}
```

### 5. 实时日志API

#### GET /api/logs
```python
# 获取消息日志
Query Parameters:
- limit: 100 (默认)
- status: success/failed
- start_time: ISO时间
- end_time: ISO时间

Response:
[
  {
    "id": 1,
    "kook_message_id": "msg_123",
    "content": "测试消息",
    "message_type": "text",
    "status": "success",
    "latency_ms": 230,
    "created_at": "2025-11-06T10:30:00"
  }
]
```

#### WebSocket /api/ws/logs
```python
# 实时日志推送
Connect: ws://localhost:9527/api/ws/logs

Receive:
{
  "type": "log",
  "data": {
    "message_id": "msg_123",
    "status": "success",
    "content": "...",
    "timestamp": "2025-11-06T10:30:00"
  }
}
```

### 6. 系统状态API

#### GET /api/system/stats
```python
# 获取系统统计
Response:
{
  "accounts": {
    "total": 3,
    "online": 2,
    "offline": 1
  },
  "messages": {
    "total": 12345,
    "success": 12100,
    "failed": 245,
    "success_rate": 0.98
  },
  "queue": {
    "size": 10,
    "processing": 2
  },
  "uptime": 86400
}
```

#### GET /api/health
```python
# 健康检查
Response:
{
  "status": "healthy",
  "components": {
    "redis": "ok",
    "database": "ok",
    "scrapers": "ok"
  },
  "timestamp": "2025-11-06T10:30:00"
}
```

---

## 🔐 安全架构

### 1. 认证授权

```
┌──────────────────────────────────────┐
│          认证流程                     │
└────────────┬─────────────────────────┘
             │
    ┌────────▼────────┐
    │ 用户输入密码     │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ bcrypt验证      │
    │ (数据库哈希)     │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ 生成JWT Token   │
    │ (24小时有效)    │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ 返回Token       │
    │ (localStorage)  │
    └─────────────────┘
```

### 2. 密码安全

```python
# 密码复杂度要求
PASSWORD_REQUIREMENTS = {
    "min_length": 8,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digit": True,
    "require_special": True,
    "forbidden_patterns": [
        # 禁止常见弱密码
        "12345678", "password", "admin123", ...
    ],
    "forbidden_sequences": [
        # 禁止连续字符
        "abc", "123", "aaa", ...
    ]
}

# 密码存储
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt)

# 密码验证
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

### 3. API认证

```python
# 中间件认证
class APIAuthMiddleware:
    async def __call__(self, request: Request, call_next):
        # 公开路径跳过
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)
        
        # 检查Token
        token = request.headers.get('X-API-Token')
        if not token or not verify_token(token):
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized"}
            )
        
        return await call_next(request)
```

### 4. 数据加密

```python
# Cookie加密存储
from cryptography.fernet import Fernet

class CookieEncryption:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
    
    def encrypt(self, cookie: dict) -> str:
        """加密Cookie"""
        cookie_json = json.dumps(cookie)
        encrypted = self.cipher.encrypt(cookie_json.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted: str) -> dict:
        """解密Cookie"""
        decrypted = self.cipher.decrypt(encrypted.encode())
        return json.loads(decrypted.decode())
```

---

## ⚡ 性能优化策略

### 1. 数据库优化

```python
# 1. 批量插入
def batch_insert_messages(messages: List[dict]):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO message_logs (...)
            VALUES (?, ?, ?, ...)
        """, [(msg['id'], msg['content'], ...) for msg in messages])

# 2. 索引优化
# 复合索引: 频道ID + 状态 + 时间
CREATE INDEX idx_logs_channel_status 
ON message_logs(kook_channel_id, status, created_at DESC);

# 3. 查询优化
# 使用索引覆盖
SELECT id, status, created_at 
FROM message_logs 
WHERE kook_channel_id = ? AND status = 'success'
ORDER BY created_at DESC
LIMIT 100;
```

### 2. Redis优化

```python
# 1. 批量出队 (+30%吞吐)
async def dequeue_batch(count: int = 10):
    messages = []
    
    # 首条阻塞等待
    first = await redis.blpop('kook_messages', timeout=5)
    if first:
        messages.append(json.loads(first[1]))
        
        # 后续非阻塞快速取出
        for _ in range(count - 1):
            msg = await redis.lpop('kook_messages')
            if msg:
                messages.append(json.loads(msg))
            else:
                break
    
    return messages

# 2. Pipeline批量操作
pipe = redis.pipeline()
for key, value in items:
    pipe.set(key, value)
await pipe.execute()

# 3. 连接池
redis_pool = aioredis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=20,
    decode_responses=True
)
```

### 3. 并发优化

```python
# 1. asyncio并发处理
async def process_messages_concurrent(messages: List[dict]):
    tasks = [process_message(msg) for msg in messages]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# 2. 限制并发数
from asyncio import Semaphore

semaphore = Semaphore(10)  # 最多10个并发

async def limited_process(message: dict):
    async with semaphore:
        return await process_message(message)

# 3. 连接池
class DiscordForwarderPool:
    def __init__(self, webhook_urls: List[str]):
        self.forwarders = [
            DiscordForwarder() 
            for _ in webhook_urls
        ]
        self.current_index = 0
    
    def get_next(self) -> DiscordForwarder:
        """轮询获取转发器"""
        forwarder = self.forwarders[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.forwarders)
        return forwarder
```

### 4. 缓存策略

```python
# 1. 映射缓存
class MappingCache:
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    async def get_mappings(self, channel_id: str):
        # 检查缓存
        if channel_id in self.cache:
            cached, timestamp = self.cache[channel_id]
            if time.time() - timestamp < self.ttl:
                return cached
        
        # 查询数据库
        mappings = db.get_channel_mappings(channel_id)
        self.cache[channel_id] = (mappings, time.time())
        return mappings

# 2. Bot配置缓存
@lru_cache(maxsize=100)
def get_bot_config(bot_id: int) -> dict:
    return db.get_bot_config(bot_id)
```

---

## 🔧 可扩展性设计

### 1. 插件系统架构

```python
# 插件接口
class PluginBase(ABC):
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        pass
    
    async def on_load(self):
        """插件加载"""
        pass
    
    async def on_unload(self):
        """插件卸载"""
        pass

# 钩子系统
class PluginManager:
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register_hook(self, hook_name: str, callback: Callable):
        """注册钩子"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    async def call_hook(self, hook_name: str, *args, **kwargs):
        """调用钩子"""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                await callback(*args, **kwargs)

# 使用示例
class MyPlugin(PluginBase):
    async def on_load(self):
        plugin_manager.register_hook(
            'before_message_forward',
            self.on_before_forward
        )
    
    async def on_before_forward(self, message: dict):
        # 自定义处理逻辑
        message['content'] = f"[插件] {message['content']}"
```

### 2. 平台扩展

```python
# 转发器接口
class ForwarderBase(ABC):
    @abstractmethod
    async def send_message(self, content: str, **kwargs) -> bool:
        """发送文本消息"""
        pass
    
    @abstractmethod
    async def send_image(self, image_url: str, **kwargs) -> bool:
        """发送图片消息"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> tuple[bool, str]:
        """测试连接"""
        pass

# 新平台实现
class SlackForwarder(ForwarderBase):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_message(self, content: str, **kwargs) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url,
                json={"text": content}
            ) as resp:
                return resp.status == 200
```

### 3. 数据库迁移

```python
# 版本管理
DATABASE_VERSION = 3

def migrate_database():
    current_version = db.get_config('db_version') or 0
    
    if current_version < 1:
        # 迁移到版本1
        migrate_to_v1()
    
    if current_version < 2:
        # 迁移到版本2
        migrate_to_v2()
    
    if current_version < 3:
        # 迁移到版本3
        migrate_to_v3()
    
    db.set_config('db_version', str(DATABASE_VERSION))

def migrate_to_v3():
    """添加新字段"""
    with db.get_connection() as conn:
        conn.execute("""
            ALTER TABLE accounts 
            ADD COLUMN avatar_url TEXT
        """)
```

---

## 📊 监控与运维

### 1. 健康检查

```python
class HealthChecker:
    async def check_all(self) -> dict:
        """全面健康检查"""
        results = {
            "redis": await self.check_redis(),
            "database": await self.check_database(),
            "scrapers": await self.check_scrapers(),
            "queue": await self.check_queue()
        }
        
        overall = all(r['status'] == 'ok' for r in results.values())
        
        return {
            "status": "healthy" if overall else "unhealthy",
            "components": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def check_redis(self) -> dict:
        """检查Redis"""
        try:
            await redis_queue.redis.ping()
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

### 2. 性能指标

```python
class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
    
    def record_message_processed(self, platform: str, status: str):
        """记录消息处理"""
        key = f"message.{platform}.{status}"
        self.counters[key] += 1
    
    @contextmanager
    def measure_time(self, operation: str):
        """测量耗时"""
        start = time.time()
        yield
        duration = time.time() - start
        self.timers[operation].append(duration)
    
    def get_summary(self) -> dict:
        """获取统计摘要"""
        return {
            "counters": dict(self.counters),
            "timers": {
                k: {
                    "count": len(v),
                    "avg": sum(v) / len(v) if v else 0,
                    "min": min(v) if v else 0,
                    "max": max(v) if v else 0
                }
                for k, v in self.timers.items()
            }
        }
```

### 3. 日志管理

```python
# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] %(message)s"
        },
        "detailed": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
            "level": "DEBUG"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"]
    }
}
```

---

## 🚀 部署架构

### 1. 开发环境

```
开发机器
├── Python 3.12 (venv)
├── Node.js 18
├── Redis (本地)
├── Chrome/Chromium
└── VS Code / PyCharm
```

### 2. 生产环境

```
Electron应用
├── 嵌入式Redis
├── 嵌入式后端 (PyInstaller)
├── 前端资源 (Vite打包)
└── Playwright浏览器
```

### 3. Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  kook-forwarder:
    build: .
    ports:
      - "9527:9527"
      - "5173:5173"
    volumes:
      - ./data:/app/data
    environment:
      - REDIS_HOST=redis
      - API_PORT=9527
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

---

**文档维护**: 请在每次重大架构变更后更新此文档  
**版本控制**: 文档版本应与系统版本同步更新

