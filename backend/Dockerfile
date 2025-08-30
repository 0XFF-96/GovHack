# 使用Python 3.9官方镜像作为基础镜像
FROM python:3.9-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt /app/

# 安装Python依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制项目文件
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/logs /app/media /app/staticfiles

# 收集静态文件
RUN python manage.py collectstatic --noinput || true

# 创建非root用户
RUN addgroup --system django && \
    adduser --system --group django

# 设置文件权限
RUN chown -R django:django /app
USER django

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "govhack_backend.wsgi:application"]