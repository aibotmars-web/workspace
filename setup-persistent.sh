#!/bin/bash
# Complete EverMemOS + Qwen3-Embedding Persistent Setup
# All services will be persistent across container restarts

set -e

echo "🚀 開始創建持久化架構..."
echo "================================"

# 1. Create Docker volumes
echo "📦 Step 1: 創建 Docker volumes..."
docker volume create huggingface-cache 2>/dev/null || echo "Volume already exists"
docker volume create evermemos-data 2>/dev/null || echo "Volume already exists"
docker volume create mongodb-data 2>/dev/null || echo "Volume already exists"
docker volume create elasticsearch-data 2>/dev/null || echo "Volume already exists"
docker volume create redis-data 2>/dev/null || echo "Volume already exists"
docker volume create milvus-data 2>/dev/null || echo "Volume already exists"

echo "✅ Volumes created!"

# 2. Pre-download model to volume
echo ""
echo "📥 Step 2: 下載模型到 volume（預載入）..."
docker run --rm \
    -v huggingface-cache:/root/.cache/huggingface \
    python:3.11-slim \
    bash -c "pip install --no-cache-dir transformers && \
        python -c \"from transformers import AutoTokenizer, AutoModel; \
        m = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-0.6B'); \
        m = AutoModel.from_pretrained('Qwen/Qwen3-Embedding-0.6B'); \
        print('Model downloaded!')\""

echo "✅ 模型預載入完成！"

# 3. Create persistent docker-compose
echo ""
echo "📝 Step 3: 創建 docker-compose 配置..."
cat > /root/.openclaw/docker-compose.persistent.yml << 'EOF'
version: '3.8'

services:
  # ===============================
  # Qwen3-Embedding-0.6B (Persistent)
  # ===============================
  embedding-server:
    build:
      context: ./embedding-server
      dockerfile: Dockerfile.persistent
    container_name: evermemos-embedding
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - MODEL_NAME=Qwen/Qwen3-Embedding-0.6B
      - DEVICE=cpu
    volumes:
      - huggingface-cache:/root/.cache/huggingface
    networks:
      - evermemos-network
    deploy:
      resources:
        limits:
          memory: 4G

  # ===============================
  # EverMemOS Core Services
  # ===============================
  mongodb:
    image: mongo:7.0
    container_name: evermemos-mongodb
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: memsys123
    ports:
      - "27017:27017"
    volumes:
      - mongodb-data:/data/db
    networks:
      - evermemos-network

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: evermemos-elasticsearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ports:
      - "19200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - evermemos-network

  redis:
    image: redis:7.2-alpine
    container_name: evermemos-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - evermemos-network

  milvus-standalone:
    image: milvusdb/milvus:v2.5.2
    container_name: evermemos-milvus
    restart: unless-stopped
    command: ["milvus", "run", "standalone"]
    environment:
      - ETCD_ENDPOINTS=milvus-etcd:2479
      - MINIO_ADDRESS=milvus-minio:9000
    ports:
      - "19530:19530"
    volumes:
      - milvus-data:/var/lib/milvus
    networks:
      - evermemos-network
    depends_on:
      - milvus-etcd
      - milvus-minio

  milvus-etcd:
    image: quay.io/coreos/etcd:v3.5.5
    container_name: evermemos-milvus-etcd
    restart: unless-stopped
    volumes:
      - milvus-etcd-data:/etcd
    networks:
      - evermemos-network

  milvus-minio:
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    container_name: evermemos-milvus-minio
    restart: unless-stopped
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    command: minio server /minio_data --console-address ":9001"
    volumes:
      - milvus-minio-data:/minio_data
    networks:
      - evermemos-network

  # ===============================
  # EverMemOS API (Persistent)
  # ===============================
  evermemos-api:
    build:
      context: ./evermemos
      dockerfile: Dockerfile
    container_name: evermemos-api
    restart: unless-stopped
    ports:
      - "1995:1995"
    environment:
      - LLM_PROVIDER=openai
      - LLM_BASE_URL=${LLM_BASE_URL:-http://host.docker.internal:8001/v1}
      - LLM_API_KEY=${LLM_API_KEY}
      - VECTORIZE_PROVIDER=vllm
      - VECTORIZE_BASE_URL=http://embedding-server:8000/v1
      - VECTORIZE_API_KEY=EMPTY
      - VECTORIZE_MODEL=Qwen/Qwen3-Embedding-0.6B
      - REDIS_HOST=redis
      - MONGODB_HOST=mongodb
      - ES_HOSTS=http://elasticsearch:19200
      - MILVUS_HOST=milvus-standalone
    volumes:
      - evermemos-data:/app/data
    networks:
      - evermemos-network
    depends_on:
      - mongodb
      - elasticsearch
      - redis
      - milvus-standalone
      - embedding-server

networks:
  evermemos-network:
    driver: bridge

volumes:
  huggingface-cache:
    driver: local
  evermemos-data:
    driver: local
  mongodb-data:
    driver: local
  elasticsearch_data:
    driver: local
  redis-data:
    driver: local
  milvus-data:
    driver: local
  milvus-etcd-data:
    driver: local
  milvus-minio-data:
    driver: local
EOF

echo "✅ docker-compose.yml created!"

# 4. Create persistent Dockerfile for embedding server
echo ""
echo "🐳 Step 4: 創建 Embedding Server Dockerfile..."
cat > /root/.openclaw/embedding-server/Dockerfile.persistent << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY server.py .

# Pre-download model during build (so it's baked into the image)
ENV MODEL_NAME="Qwen/Qwen3-Embedding-0.6B"
RUN python -c "from transformers import AutoTokenizer, AutoModel; \
    AutoTokenizer.from_pretrained('$MODEL_NAME'); \
    AutoModel.from_pretrained('$MODEL_NAME'); \
    print('Model baked into image!')"

EXPOSE 8000

CMD ["python", "server.py"]
EOF

echo "✅ Dockerfile.persistent created!"

echo ""
echo "================================"
echo "🎉 持久化設置完成！"
echo ""
echo "接下來的步驟："
echo "1. 啟動所有服務："
echo "   cd /root/.openclaw && docker-compose -f docker-compose.persistent.yml up -d"
echo ""
echo "2. 查看日誌："
echo "   docker-compose -f docker-compose.persistent.yml logs -f"
echo ""
echo "3. 測試 embedding 服務："
echo "   curl http://localhost:8000/health"
