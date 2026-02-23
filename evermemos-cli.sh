#!/bin/bash
# EverMemOS CLI - 透過 docker exec 調用 EverMemOS API

CONTAINER="evermemos"
PORT=1995
API_BASE="http://localhost:$PORT/api/v1"

# 測試健康狀態
if [ "$1" = "health" ]; then
    docker exec $CONTAINER curl -s "http://localhost:$PORT/health"
    exit $?
fi

# 儲存記憶
if [ "$1" = "store" ]; then
    CONTENT="$2"
    SENDER="${3:-system}"
    MSG_ID="${4:-msg-$(date +%s)}"
    
    docker exec $CONTAINER curl -s -X POST "$API_BASE/memories" \
        -H "Content-Type: application/json" \
        -d "{
            \"content\": \"$CONTENT\",
            \"message_id\": \"$MSG_ID\",
            \"sender\": \"$SENDER\",
            \"create_time\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
        }"
    exit $?
fi

# 搜尋記憶
if [ "$1" = "search" ]; then
    QUERY="$2"
    USER="${3:-system}"
    
    docker exec $CONTAINER curl -s "$API_BASE/memories/search?query=$QUERY&user_id=$USER"
    exit $?
fi

# 讀取記憶
if [ "$1" = "fetch" ]; then
    USER="${2:-system}"
    
    docker exec $CONTAINER curl -s "$API_BASE/memories?user_id=$USER"
    exit $?
fi

echo "EverMemOS CLI - 記憶系統"
echo "=========================="
echo ""
echo "用法:"
echo "  $0 health                    - 檢查服務狀態"
echo "  $0 store <內容> [發送者] [ID] - 儲存記憶"
echo "  $0 search <關鍵字> [用戶]      - 搜尋記憶"
echo "  $0 fetch [用戶]              - 讀取記憶"
echo ""
echo "範例:"
echo "  $0 health"
echo "  $0 store 'Mars是我的老闆' system"
echo "  $0 search Mars system"
echo "  $0 fetch system"
