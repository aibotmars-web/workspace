#!/bin/bash
# 使用 npx 啟動 MiniMax Coding Plan MCP

API_KEY="sk-cp-zBE1lcRUibZCRRYCuwSJv_HIpvekBW0YsZTEL17h1giYy2KqDOwJ4QoaBtuExUmuE8NQWOHz-P1dtBAF3jKkBrKEs3336Gpr0e6L-wRlMROa4-3V-dwc5Ws"

echo "🚀 啟動 MiniMax Coding Plan MCP..."
echo "使用 npx 運行..."
echo "API Key: ${API_KEY:0:20}..."
echo ""

npx -y minimax-coding-plan --api-key "$API_KEY"
