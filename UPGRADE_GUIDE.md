# KOOK消息转发系统 - 升级指南

## 📦 v1.4.0 → v1.4.1 升级指南

### ⚠️ 升级前准备

1. **备份数据**（重要！）
   ```bash
   # 备份数据库
   cp ~/Documents/KookForwarder/data/config.db ~/Documents/KookForwarder/data/config.db.backup
   
   # 备份Redis数据（如果使用内置Redis）
   cp -r ~/Documents/KookForwarder/data/redis ~/Documents/KookForwarder/data/redis.backup
   ```

2. **记录当前配置**
   - 导出所有账号信息
   - 导出Bot配置
   - 导出频道映射关系

---

### 🚀 升级步骤

#### 方式一：自动升级（推荐）

```bash
# 1. 进入项目目录
cd /path/to/CSBJJWT

# 2. 停止服务
./stop.sh  # Linux/macOS
# 或
stop.bat   # Windows

# 3. 拉取最新代码
git pull origin main

# 4. 运行升级脚本
./upgrade.sh  # Linux/macOS
# 或
upgrade.bat   # Windows

# 5. 重启服务
./start.sh  # Linux/macOS
# 或
start.bat   # Windows
```

#### 方式二：手动升级

```bash
# 1. 停止服务
# 关闭所有KOOK Forwarder窗口

# 2. 更新代码
cd /path/to/CSBJJWT
git pull origin main

# 3. 更新后端依赖
cd backend
pip install -r requirements.txt --upgrade

# 4. 更新前端依赖
cd ../frontend
npm install

# 5. 重新构建前端（如果使用打包版本）
npm run build

# 6. 重启服务
cd ..
./start.sh  # Linux/macOS
# 或
start.bat   # Windows
```

---

### 🔧 数据库迁移

**v1.4.1无需数据库迁移**，但为了支持新功能，会自动创建审计日志目录：

```
~/Documents/KookForwarder/data/logs/audit/
```

如果升级后发现问题，请检查目录权限：

```bash
# Linux/macOS
chmod -R 755 ~/Documents/KookForwarder/data/logs

# 检查是否有写入权限
ls -la ~/Documents/KookForwarder/data/logs
```

---

### ✅ 验证升级

升级完成后，请验证以下功能：

#### 1. 检查版本号
```bash
# 启动应用后，查看关于页面
# 应该显示：v1.4.1
```

#### 2. 测试核心功能
- [ ] 登录现有账号
- [ ] 查看频道映射
- [ ] 发送测试消息
- [ ] 查看实时日志
- [ ] 检查统计数据

#### 3. 检查新功能
- [ ] 访问 `/api/audit/stats` 查看审计日志统计
- [ ] 在配置页查找"观看视频教程"按钮
- [ ] 尝试发送特殊字符消息，验证安全检查

#### 4. 检查日志
```bash
# 查看应用日志
tail -f ~/Documents/KookForwarder/data/logs/app_*.log

# 查看错误日志
tail -f ~/Documents/KookForwarder/data/logs/error_*.log

# 查看审计日志
tail -f ~/Documents/KookForwarder/data/logs/audit/audit_*.log
```

---

### 🐛 常见升级问题

#### 问题1：依赖安装失败

**症状**：`pip install` 或 `npm install` 报错

**解决**：
```bash
# Python依赖问题
cd backend
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Node依赖问题
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 问题2：数据库锁定

**症状**：`database is locked` 错误

**解决**：
```bash
# 确保所有进程已停止
ps aux | grep python | grep kook
# 如果有进程运行，终止它们
kill -9 <PID>

# 重启服务
./start.sh
```

#### 问题3：Redis连接失败

**症状**：`Cannot connect to Redis` 错误

**解决**：
```bash
# 检查Redis是否运行
redis-cli ping  # 应返回 PONG

# 如果未运行，启动Redis
# Linux/macOS
redis-server

# Windows
cd redis
redis-server.exe redis.conf

# 或使用内置Redis管理器（v1.4.0+）
# 它会自动启动Redis
```

#### 问题4：前端页面空白

**症状**：升级后前端页面无法加载

**解决**：
```bash
# 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete

# 重新构建前端
cd frontend
npm run build

# 或使用开发模式
npm run dev
```

#### 问题5：审计日志无权限

**症状**：`Permission denied` 写入审计日志

**解决**：
```bash
# 创建审计日志目录并设置权限
mkdir -p ~/Documents/KookForwarder/data/logs/audit
chmod -R 755 ~/Documents/KookForwarder/data/logs

# 检查目录所有者
ls -la ~/Documents/KookForwarder/data/logs
```

---

### 📝 配置更新

#### 新增配置项

v1.4.1引入以下新配置（可选）：

```python
# backend/app/config.py

# 审计日志设置
AUDIT_LOG_ENABLED = True  # 是否启用审计日志
AUDIT_LOG_RETENTION_DAYS = 90  # 审计日志保留天数

# 消息验证设置
MESSAGE_VALIDATION_ENABLED = True  # 是否启用消息验证
SPAM_CHECK_ENABLED = True  # 是否检查垃圾消息

# 视频教程设置
VIDEO_TUTORIAL_ENABLED = True  # 是否显示视频教程按钮
```

如需自定义，创建`.env`文件：

```bash
# .env
AUDIT_LOG_ENABLED=true
AUDIT_LOG_RETENTION_DAYS=90
MESSAGE_VALIDATION_ENABLED=true
SPAM_CHECK_ENABLED=true
VIDEO_TUTORIAL_ENABLED=true
```

---

### 🔄 回滚指南

如果升级后遇到严重问题，可以回滚到v1.4.0：

```bash
# 1. 停止服务
./stop.sh

# 2. 回滚代码
git checkout v1.4.0

# 3. 恢复依赖
cd backend
pip install -r requirements.txt
cd ../frontend
npm install

# 4. 恢复数据库（如果需要）
cp ~/Documents/KookForwarder/data/config.db.backup \
   ~/Documents/KookForwarder/data/config.db

# 5. 重启服务
cd ..
./start.sh
```

---

### 📞 获取帮助

如果升级过程中遇到问题：

1. **查看日志**
   ```bash
   tail -f ~/Documents/KookForwarder/data/logs/error_*.log
   ```

2. **查看文档**
   - [完整用户手册](docs/完整用户手册.md)
   - [开发指南](docs/开发指南.md)
   - [常见问题](docs/FAQ.md)

3. **提交Issue**
   - GitHub Issues: https://github.com/gfchfjh/CSBJJWT/issues
   - 包含错误日志和系统信息

4. **社区支持**
   - KOOK官方服务器
   - Discord开发者群组

---

### ✨ 新功能使用指南

#### 1. 查看审计日志

通过API查看审计日志：

```bash
# 获取最近100条审计日志
curl http://localhost:9527/api/audit/logs?limit=100

# 获取登录事件
curl http://localhost:9527/api/audit/logs?event_type=LOGIN

# 获取统计信息
curl http://localhost:9527/api/audit/stats?days=7
```

或在前端页面（v1.5.0将添加UI）：
- 访问"高级功能" → "审计日志"

#### 2. 使用视频教程

在任何配置页面，查找"📺 观看视频教程"按钮：

- **账号管理页** → Cookie获取教程
- **机器人配置页** → Discord/Telegram/飞书教程
- **频道映射页** → 智能映射教程
- **过滤规则页** → 过滤规则教程

#### 3. 测试消息验证

发送以下测试消息，验证安全检查：

```
# 测试XSS防护
<script>alert('test')</script>

# 测试垃圾检测
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

# 正常消息（应通过）
这是一条正常的测试消息
```

---

### 🎉 升级成功！

恭喜完成升级！v1.4.1带来了更好的安全性和用户体验。

**接下来可以**：
1. 探索新功能（审计日志、视频教程）
2. 查看改进文档了解更多细节
3. 参与社区反馈和建议

**感谢使用KOOK消息转发系统！**

---

*最后更新: 2025-10-18*  
*版本: v1.4.1*
