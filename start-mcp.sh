#!/bin/bash
# MiniMax Coding Plan MCP 啟動腳本
# 網頁搜尋 + 圖片理解

set -e

echo "🚀 啟動 MiniMax Coding Plan MCP..."
echo "================================"

# API Key（從你的 openclaw.json 取得）
API_KEY="sk-cp-zBE1lcRUibZCRRYCuwSJv_HIpvekBW0YsZTEL17h1giYy2KqDOwJ4QoaBtuExUmuE8NQWOHz-P1dtBAF3jKkBrKEs3336Gpr0e6L-wRlMROa4-3V-dwc5Ws"

# 驗證 uvx
if ! command -v uvx &> /dev/null; then
    echo "📦 安裝 uvx..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ uvx 已就緒"

# 啟動 MCP 伺服器（前台運行）
echo "🌐 啟動 MCP 伺服器..."
echo "   按 Ctrl+C 停止"
echo ""

uvx minimax-coding-plan --api-key "$API_KEY"
