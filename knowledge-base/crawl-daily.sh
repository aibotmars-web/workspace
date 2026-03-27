#!/bin/bash
# 每日 YouTube 專家知識庫爬蟲
# 每天爬 ~50 部影片字幕 (9頻道 x 6部)

BASE_DIR="/Users/marsbot/.openclaw/workspace/knowledge-base/experts"
LOG_FILE="$BASE_DIR/crawler-cron.log"

echo "============================================================"
echo "YouTube 專家知識庫爬蟲 $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

cd "$BASE_DIR"
python3 smart_update.py >> "$LOG_FILE" 2>&1

echo ""
echo "爬蟲完成 $(date '+%Y-%m-%d %H:%M:%S')"
