# KOOK消息转发系统 - 统一Dockerfile
# 多阶段构建，优化镜像大小

# ============================================
# 阶段1: 前端构建
# ============================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制前端源码
COPY frontend/ ./

# 构建前端
RUN npm run build

# ============================================
# 阶段2: Python运行环境
# ============================================
FROM python:3.11-slim AS runtime

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY backend/requirements.txt ./backend/

# 安装Python依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium && \
    playwright install-deps chromium

# 复制后端代码
COPY backend/ ./backend/

# 复制Redis配置
COPY redis/ ./redis/

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 创建数据目录
RUN mkdir -p /app/data/images /app/data/logs /app/data/redis

# 暴露端口
EXPOSE 9527 9528

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:9527/health || exit 1

# 启动命令
CMD ["python", "-m", "backend.app.main"]
