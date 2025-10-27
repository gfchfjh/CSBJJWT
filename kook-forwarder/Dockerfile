# KOOK消息转发系统 - Docker镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（包括编译工具，用于构建psutil等库）
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-6 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxshmfence1 \
    redis-server \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制后端代码
COPY backend/ ./backend/

# 安装Python依赖（分步执行以便调试）
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN cd backend && playwright install chromium

# 安装Playwright系统依赖
RUN cd backend && playwright install-deps chromium || true

# 创建数据目录
RUN mkdir -p /data/logs /data/images /data/db

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=9527 \
    REDIS_HOST=127.0.0.1 \
    REDIS_PORT=6379 \
    DATA_DIR=/data

# 暴露端口
EXPOSE 9527

# 复制启动脚本
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:9527/health || exit 1

# 启动应用
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "-m", "backend.app.main"]
