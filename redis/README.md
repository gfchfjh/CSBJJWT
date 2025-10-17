# Redis 服务说明

KOOK消息转发系统使用Redis作为消息队列中间件，确保消息的可靠传递和持久化。

## 安装方式

### Windows

1. **自动安装（推荐）**
   - 运行 `start.bat`，系统会自动检测并尝试启动Redis
   - 如果未找到Redis，会提供下载链接

2. **手动安装**
   - 下载预编译版本：https://github.com/tporadowski/redis/releases
   - 下载 `Redis-x64-x.x.x.zip`
   - 解压到本目录（`redis/`文件夹下）
   - 确保 `redis-server.exe` 在此目录中

### Linux

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**CentOS/RHEL:**
```bash
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

### macOS

```bash
brew install redis
brew services start redis
```

## 验证安装

检查Redis是否运行：

**Windows:**
```cmd
netstat -ano | findstr :6379
```

**Linux/macOS:**
```bash
redis-cli ping
```

如果返回 `PONG`，说明Redis正常运行。

## 配置文件

- `redis.conf` - Redis配置文件
- 默认端口：6379
- 默认绑定：127.0.0.1（仅本地访问）
- 最大内存：256MB
- 持久化：RDB快照模式

## 常见问题

### 1. 端口被占用
如果端口6379已被占用，可以：
- 停止其他Redis实例
- 或修改配置文件中的端口号

### 2. 启动失败
- 检查是否有权限问题
- 查看日志文件了解详细错误
- 尝试手动运行：`redis-server redis.conf`

### 3. 无需Redis运行？
系统会在Redis不可用时自动使用内存队列作为降级方案，但：
- ⚠️ 性能较低
- ⚠️ 程序崩溃会丢失未处理的消息
- ⚠️ 不支持消息持久化

**建议生产环境必须使用Redis！**

## 性能优化

对于大流量场景，可以调整以下配置：

1. **增加最大内存**
   ```
   maxmemory 512mb  # 或更大
   ```

2. **启用AOF持久化**（更安全但性能略低）
   ```
   appendonly yes
   ```

3. **调整保存策略**
   ```
   save 900 1     # 15分钟内至少1个key变化
   save 300 10    # 5分钟内至少10个key变化
   save 60 10000  # 1分钟内至少10000个key变化
   ```

## 监控

查看Redis状态：
```bash
redis-cli info
redis-cli info stats
redis-cli info memory
```

## 清理数据

如需清空Redis数据：
```bash
redis-cli FLUSHALL
```

⚠️ **注意：这将删除所有数据，包括未处理的消息队列！**

## 安全建议

1. **设置密码**（生产环境）
   - 编辑 `redis.conf`
   - 取消注释并设置：`requirepass yourStrongPassword123`
   - 在应用配置中添加密码

2. **仅绑定本地**
   - 保持 `bind 127.0.0.1`
   - 不要暴露到公网

3. **防火墙规则**
   - 仅允许本地访问6379端口

## 技术支持

如遇到问题，请查看：
- 主项目README.md
- 提交Issue：https://github.com/gfchfjh/CSBJJWT/issues
