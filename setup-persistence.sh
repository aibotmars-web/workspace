#!/bin/bash
# OpenClaw 持久化腳本（方案 A）

set -e

echo "🚀 開始持久化設定..."
echo "================================"
echo ""

# 1. 創建 Docker Volume
echo "📦 Step 1: 創建 Docker Volumes..."
docker volume create openclaw-python-packages
docker volume create openclaw-uv-bin
docker volume create openclaw-uv-cache
docker volume create openclaw-node-packages

echo "✅ Volumes 創建完成！"
echo ""

# 2. 停止目前容器
echo "🛑 Step 2: 停止目前容器..."
docker stop openclaw-main || true
docker rm openclaw-main || true

echo "✅ 容器已停止並移除"
echo ""

# 3. 啟動新容器（挂载 Volume）
echo "🚀 Step 3: 啟動新容器（使用 Volume）..."
docker run -d \
    --name openclaw-main \
    --restart unless-stopped \
    -p 18789:18789 \
    -v openclaw-python-packages:/usr/local/lib/python3.11/dist-packages \
    -v openclaw-uv-bin:/root/.local/bin \
    -v openclaw-uv-cache:/root/.cache/uv \
    -v openclaw-node-packages:/usr/local/lib/node_modules \
    -v $(pwd)/workspace:/root/.openclaw/workspace \
    -v $(pwd)/memory:/root/.openclaw/workspace/memory \
    -e OPENCLAW_MODEL=minimax-cn/MiniMax-M2.5 \
    docker-openclaw:latest

echo "✅ 新容器已啟動！"
echo ""

# 4. 重新安裝套件到 Volume
echo "📦 Step 4: 安裝 Python MCP 套件到 Volume..."
docker exec openclaw-main pip3 install --no-cache-dir minimax-coding-plan-mcp requests

echo "✅ Python 套件安裝完成"
echo ""

# 5. 安裝 uvx
echo "🌐 Step 5: 安裝 uvx..."
docker exec openclaw-main /bin/bash -c "curl -LsSf https://astral.sh/uv/install.sh | sh"

echo "✅ uvx 安裝完成"
echo ""

# 6. 安裝 Node.js MCP
echo "📦 Step 6: 安裝 Node.js MCP..."
docker exec openclaw-main npm install -g @ameno/pi-minimax-mcp

echo "✅ Node.js 套件安裝完成"
echo ""

# 7. 重啟容器
echo "🔄 Step 7: 重啟容器..."
docker restart openclaw-main

echo "✅ 容器已重啟！"
echo ""

echo "================================"
echo "🎉 持久化完成！"
echo ""
echo "驗證方式："
echo "  docker exec openclaw-main pip3 list | grep minimax"
echo "  docker exec openclaw-main /root/.local/bin/uvx --version"
echo ""
echo "查看日誌："
echo "  docker logs -f openclaw-main"
