#!/bin/bash
# 知識庫爬蟲 - Cron  Wrapper
# 順序跑字幕版 + ASR版
WORKSPACE="$HOME/.openclaw/workspace/knowledge-base"
LOG="$WORKSPACE/crawler-cron.log"

{
  echo "=== 字幕版 $(date '+%Y-%m-%d %H:%M:%S') ==="
  python3 "$WORKSPACE/crawl_subtitles.py" 2>&1
  
  echo "=== ASR版 $(date '+%Y-%m-%d %H:%M:%S') ==="
  python3 "$WORKSPACE/crawl_asr.py" 2>&1
  
  echo "=== 完成 $(date '+%Y-%m-%d %H:%M:%S') ==="
} >> "$LOG" 2>&1
