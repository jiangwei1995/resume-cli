FROM python:3.12-slim

WORKDIR /app

# 先装依赖，利用镜像层缓存
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

ENTRYPOINT ["resume-cli"]
CMD ["--help"]
