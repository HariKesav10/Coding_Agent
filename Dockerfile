FROM python:3.11-slim
LABEL authors="HariKesav"

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    curl \
    && rm-rf /var/lib/apt-get/lists/*

RUN pip install --no-cache-dir numpy pandas pytest requests

WORKDIR /sandbox

ENTRYPOINT ["top", "-b"]