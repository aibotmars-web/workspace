#!/bin/bash
# YouTube 專家知識庫爬蟲 Daemon
# 每小時執行一次（20部/輪），持續運行
# 使用 nohup ./crawl-daily.sh & 啟動

BASE_DIR="/Users/marsbot/.openclaw/workspace/knowledge-base/experts"
LOG_FILE="$BASE_DIR/crawler-cron.log"
PID_FILE="/tmp/crawl-daemon.pid"

# 防止重複啟動
if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "[$(date)] 爬蟲 Daemon 已在運行 (PID $(cat "$PID_FILE"))" >> "$LOG_FILE"
    exit 0
fi

echo $$ > "$PID_FILE"

echo "============================================================"
echo "YouTube 專家知識庫爬蟲 Daemon 啟動 $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

while true; do
    echo ""
    echo "============================================================"
    echo "爬蟲循環 $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================================"
    
    cd "$BASE_DIR"
    # 爬 top3pct 頻道
    bash crawl_top3pct.sh >> "$LOG_FILE" 2>&1
    echo "--- kd_crawl $(date)" >> "$LOG_FILE" 2>&1
    # 爬其他頻道
    bash kd_crawl.sh >> "$LOG_FILE" 2>&1
    
    echo "完成，等待 1 小時..."
    sleep 3600
done
