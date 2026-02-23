#!/bin/bash
# MiniMax Coding Plan MCP 啟動腳本

export MINIMAX_API_KEY="sk-cp-zBE1lcRUibZCRRYCuwSJv_HIpvekBW0YsZTEL17h1giYy2KqDOwJ4QoaBtuExUmuE8NQWOHz-P1dtBAF3jKkBrKEs3336Gpr0e6L-wRlMROa4-3V-dwc5Ws"

echo "🚀 啟動 MiniMax Coding Plan MCP 伺服器..."
echo "================================"
echo ""

# 檢查 uvx
if ! command -v uvx &> /dev/null; then
    echo "📦 安裝 uvx..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ uvx 就緒"
echo ""
echo "🌐 啟動 MCP 伺服器..."
echo "   按 Ctrl+C 停止"
echo ""

# 前台運行 MCP 伺服器
uvx minimax-coding-plan-mcp
