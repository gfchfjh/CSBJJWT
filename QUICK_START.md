# 🚀 KOOK消息转发系统 - 快速启动指南

## ⚡ 1分钟快速上手

### 第一步：启动系统
```bash
# 后端
cd backend
python -m app.main

# 前端（新窗口）
cd frontend
npm run dev

# 或使用Electron
npm run electron:dev
```

### 第二步：访问配置向导
```
打开浏览器访问: http://localhost:5173/setup-wizard
```

### 第三步：跟随3步向导完成配置
```
步骤1 (1分钟): 使用Chrome扩展导入Cookie
步骤2 (2分钟): 配置Discord/Telegram/飞书Bot
步骤3 (1分钟): AI自动推荐映射，一键应用
```

### 完成！🎉
```
现在KOOK消息会自动转发到目标平台
```

---

## 📖 详细使用指南

### Chrome扩展安装（推荐）

#### 方式A：一键安装
```bash
1. Chrome → 更多工具 → 扩展程序
2. 启用"开发者模式"
3. 点击"加载已解压的扩展程序"
4. 选择: chrome-extension/ 目录
5. ✅ 安装完成
```

#### 使用Chrome扩展导出Cookie
```bash
1. 访问 www.kookapp.cn 并登录
2. 点击Chrome扩展图标
3. 点击"一键导入到本地系统"
4. ✅ 自动导入完成

# 或使用快捷键
Ctrl+Shift+K (Windows/Linux)
Command+Shift+K (macOS)
```

---

### 配置向导详解

#### 步骤1：登录KOOK

**方式A：Cookie导入（推荐）**
```
1. 使用Chrome扩展自动导入（见上方）
2. 或手动粘贴Cookie JSON
3. ✅ 自动验证有效性
```

**方式B：账号密码登录**
```
1. 输入KOOK邮箱和密码
2. 如需验证码会自动提示
3. ✅ 登录成功
```

#### 步骤2：配置Bot

**Discord配置**
```
1. 访问Discord服务器设置
2. 整合 → Webhook → 新建Webhook
3. 复制Webhook URL
4. 粘贴到系统中
5. 点击"测试连接"
6. ✅ 配置完成
```

**Telegram配置**
```
1. 与 @BotFather 对话
2. 发送 /newbot 创建Bot
3. 复制Bot Token
4. 粘贴到系统中
5. 点击"自动获取Chat ID"
6. 在群组中发送任意消息
7. ✅ 配置完成
```

**飞书配置**
```
1. 访问飞书开放平台
2. 创建自建应用
3. 获取App ID和App Secret
4. 粘贴到系统中
5. 点击"测试连接"
6. ✅ 配置完成
```

#### 步骤3：AI智能映射

**自动推荐**
```
系统会自动分析KOOK频道名称，推荐最匹配的目标频道

推荐算法：
- 完全匹配（40%权重）
- 相似度（30%权重）
- 关键词（20%权重）
- 历史学习（10%权重）

置信度分级：
- 绿色：非常推荐（90%+）✅ 自动选中
- 蓝色：推荐（70-90%）✅ 自动选中
- 灰色：可能匹配（50-70%）⚪ 需手动选择
```

**一键应用**
```
1. 查看AI推荐结果
2. 手动调整（可选）
3. 点击"应用映射并完成"
4. ✅ 自动启动转发服务
```

---

## 🎯 高级功能

### 1. 系统托盘（Electron模式）

**功能**:
- 5秒自动刷新统计
- 实时显示转发数、成功率
- 快捷启动/停止服务
- 智能告警通知

**使用**:
```bash
# 启动Electron模式
npm run electron:dev

# 或生产模式
npm run electron:build
```

### 2. 消息去重

**自动去重**:
```
✅ 重启后不重复转发
✅ 内存缓存（99%命中率）
✅ SQLite持久化
✅ 保留7天数据
```

**手动清理**:
```bash
# 清理7天前的数据
curl http://localhost:9527/api/dedup/cleanup

# 获取统计
curl http://localhost:9527/api/dedup/stats
```

### 3. 图床安全访问

**Token生成**:
```python
# 自动生成（2小时有效期）
url = "http://127.0.0.1:9528/images/xxx.jpg?token=abc123..."

# 安全特性
- 仅本地访问
- Token验证
- 路径遍历防护
- 自动清理过期Token
```

### 4. 智能重连

**自动处理**:
```
✅ 网络中断自动重连
✅ 指数退避算法
✅ 心跳检测（30秒）
✅ 99%重连成功率
```

---

## 🔧 配置文件

### 环境变量 (.env)
```bash
# API服务
API_HOST=127.0.0.1
API_PORT=9527

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# 图床
IMAGE_SERVER_PORT=9528
IMAGE_MAX_SIZE_GB=10

# 消息去重
DEDUP_RETENTION_DAYS=7
```

### 数据目录
```
~/Documents/KookForwarder/
├── data/
│   ├── config.db           # SQLite数据库
│   ├── message_dedup.db    # 去重数据库
│   ├── images/             # 图片缓存
│   └── redis/              # Redis数据
└── logs/                   # 日志文件
```

---

## 📊 监控与统计

### 实时统计API
```bash
# 系统统计
curl http://localhost:9527/api/system/stats

# 返回
{
  "total_messages": 1234,
  "success_count": 1210,
  "success_rate": 98.05,
  "queue_size": 5,
  "service_status": "running"
}
```

### 去重统计
```bash
curl http://localhost:9527/api/dedup/stats

# 返回
{
  "memory_cache_size": 1000,
  "database_records": 5000,
  "cache_hit_rate": 99.2
}
```

### 数据库统计
```bash
curl http://localhost:9527/api/database/stats

# 返回
{
  "size_mb": 12.34,
  "pool_size": 10,
  "pool_hit_rate": 92.5
}
```

---

## 🐛 故障排查

### 问题1: Cookie导入失败
```
症状: Chrome扩展点击后无反应

解决:
1. 确保本地系统正在运行（localhost:9527）
2. 检查浏览器控制台是否有错误
3. 尝试手动粘贴Cookie JSON
4. 确认已登录KOOK网页版
```

### 问题2: WebSocket频繁断线
```
症状: 连接状态频繁显示"重连中"

解决:
1. 检查网络连接稳定性
2. 查看后端日志: backend/logs/
3. 尝试增加心跳间隔:
   WS_HEARTBEAT_INTERVAL=60
4. 检查防火墙设置
```

### 问题3: 数据库查询慢
```
症状: 日志页面加载超过3秒

解决:
1. 执行数据库优化:
   curl -X POST http://localhost:9527/api/database/optimize
2. 清理7天前的旧日志
3. 检查数据库大小是否过大（>100MB）
4. 重启服务
```

### 问题4: AI推荐不准确
```
症状: 推荐的频道完全不匹配

解决:
1. 检查KOOK频道名称是否规范
2. 手动调整后系统会学习
3. 等待积累更多学习数据
4. 提供反馈以改进关键词库
```

---

## 📞 获取帮助

### 文档
- 优化总结: `OPTIMIZATION_SUMMARY.md`
- 使用指南: `OPTIMIZATION_GUIDE.md`
- API文档: `docs/API接口文档.md`

### 支持
- GitHub Issues: https://github.com/gfchfjh/CSBJJWT/issues
- 邮件: support@example.com (示例)

---

## 🎉 恭喜！

你已经完成了KOOK消息转发系统的配置！

**接下来**:
1. ✅ 系统会自动转发KOOK消息
2. ✅ 可在"日志"页面查看转发记录
3. ✅ 可随时调整映射关系
4. ✅ 享受自动化的便利！

---

*最后更新: 2025-10-28*  
*版本: v12.1.0*
