FROM python:3.11-slim

WORKDIR /app

# 从官方镜像复制 uv 二进制
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uvx /usr/local/bin/uvx

# 安装依赖（显式传入 pyproject.toml，可选 uv.lock 用于可复现构建）
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev

# 复制应用代码
COPY app/ app/

# 预建目录
RUN mkdir -p audio dbdata

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
