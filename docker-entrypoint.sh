#!/bin/bash
# OpenClaw Persistent Entry Point

set -e

echo "🚀 啟動 OpenClaw..."
echo "✅ 所有套件已預裝（Python MCP, uvx, Node.js MCP）"

# 啟動 MCP 伺服器（在背景）
export MINIMAX_API_KEY="${MINIMAX_API_KEY:-sk-cp-zBE1lcRUibZCRRYCuwSJv_HIpvekBW0YsZTEL17h1giYy2KqDOwJ4QoaBtuExUmuE8NQWOHz-P1dtBAF3jKkBrKEs3336Gpr0e6L-wRlMROa4-3V-dwc5Ws}"
export MINIMAX_API_HOST="${MINIMAX_API_HOST:-https://api.minimaxi.com}"

echo "🌐 啟動 MiniMax MCP 伺服器..."
nohup /root/.local/bin/uvx minimax-coding-plan-mcp > /var/log/mcp.log 2>&1 &

# 等待 MCP 啟動
sleep 5

# 啟動 OpenClaw
echo "🐙 啟動 OpenClaw Gateway..."
exec /usr/local/bin/node /usr/local/lib/node_modules/openclaw/openclaw.mjs gateway
