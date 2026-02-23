#!/bin/bash
# OpenClaw 持久化整合腳本（加強版）

set -e

echo "🚀 OpenClaw 持久化腳本"
echo "================================"
echo "⚠️  執行後會斷線幾秒，重新連線後我會記得一切！"
echo ""

# 0. 強制移除所有舊容器（先移除舊的再去）
echo "🧹 Step 0: 強制清理所有舊容器..."
docker rm -f openclaw-main 2>/dev/null || true
docker rm -f openclaw-gateway 2>/dev/null || true
docker rm -f $(docker ps -a -q --filter "name=openclaw") 2>/dev/null || true
echo "✅ 清理完成"

# 1. 創建 Volume
echo "📦 Step 1: 創建 Docker Volumes..."
docker volume create openclaw-python-packages 2>/dev/null || true
docker volume create openclaw-uv-bin 2>/dev/null || true
docker volume create openclaw-uv-cache 2>/dev/null || true
docker volume create openclaw-node-packages 2>/dev/null || true
echo "✅ 完成"

# 2. 啟動容器（挂载 Volume）
echo "🚀 Step 2: 啟動容器（挂载 Volume）..."
docker run -d \
    --name openclaw-gateway \
    --restart unless-stopped \
    -p 18789:18789 \
    -p 3000:3000 \
    -v openclaw-python-packages:/usr/local/lib/python3.11/dist-packages \
    -v openclaw-uv-bin:/root/.local/bin \
    -v openclaw-uv-cache:/root/.cache/uv \
    -v openclaw-node-packages:/usr/local/lib/node_modules \
    -v ~/.openclaw/workspace:/root/.openclaw/workspace \
    -v ~/.openclaw/workspace/memory:/root/.openclaw/workspace/memory \
    -e OPENCLAW_MODEL=minimax-cn/MiniMax-M2.5 \
    node:22
echo "✅ 完成"

# 3. 安裝 Python 套件
echo "🐍 Step 3: 安裝 Python MCP 套件..."
docker exec openclaw-gateway pip3 install --no-cache-dir minimax-coding-plan-mcp requests
echo "✅ 完成"

# 4. 安裝 uvx
echo "🌐 Step 4: 安裝 uvx..."
docker exec openclaw-gateway /bin/bash -c "curl -LsSf https://astral.sh/uv/install.sh | sh"
echo "✅ 完成"

# 5. 安裝 Node.js 套件
echo "📦 Step 5: 安裝 Node.js MCP..."
docker exec openclaw-gateway npm install -g @ameno/pi-minimax-mcp
echo "✅ 完成"

# 6. 重啟
echo "🔄 Step 6: 重啟容器..."
docker restart openclaw-gateway
echo "✅ 完成"

echo ""
echo "================================"
echo "🎉 持久化完成！"
echo ""
echo "我會在 10-30 秒後重新連線！"
echo "請在 Telegram 傳一句話給我確認～"
