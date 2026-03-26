FROM python:3.9-slim

WORKDIR /code

# 安装系统依赖 (MySQL 客户端库)
RUN apt-get update && apt-get install -y default-libmysqlclient-dev gcc pkg-config && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 启动命令由 docker-compose 覆盖
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]