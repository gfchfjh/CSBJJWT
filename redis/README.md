# Redis安装说明

## 📦 下载Redis

### Windows

1. 访问 https://github.com/tporadowski/redis/releases
2. 下载最新版本的 `Redis-x64-xxx.zip`
3. 解压后，将以下文件复制到此目录：
   - `redis-server.exe`
   - `redis-cli.exe`

### macOS

```bash
# 使用Homebrew安装
brew install redis

# 复制到此目录
cp /usr/local/bin/redis-server .
cp /usr/local/bin/redis-cli .
```

### Linux

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# 或下载源码编译
wget https://download.redis.io/releases/redis-7.0.0.tar.gz
tar xzf redis-7.0.0.tar.gz
cd redis-7.0.0
make

# 复制到此目录
cp src/redis-server ../
cp src/redis-cli ../
```

## 🚀 启动Redis

### Windows
双击运行 `start_redis.bat`

### Linux/macOS
```bash
chmod +x start_redis.sh
./start_redis.sh
```

## ✅ 验证安装

打开新的命令行窗口：

```bash
# Windows
redis-cli.exe ping

# Linux/macOS  
./redis-cli ping
```

如果返回 `PONG`，说明Redis运行正常。

## 📁 当前目录文件

安装完成后，此目录应包含：

```
redis/
├── redis-server.exe (Windows) 或 redis-server (Linux/macOS)
├── redis-cli.exe (Windows) 或 redis-cli (Linux/macOS)
├── redis.conf (配置文件，已包含)
├── start_redis.bat (Windows启动脚本，已包含)
├── start_redis.sh (Linux/macOS启动脚本，已包含)
└── README.md (本文件)
```

## ⚙️ 配置说明

- 监听地址: 127.0.0.1 (仅本地)
- 端口: 6379
- 最大内存: 256MB
- 持久化: 已启用
- 密码: 无（本地使用）

如需修改配置，请编辑 `redis.conf` 文件。
