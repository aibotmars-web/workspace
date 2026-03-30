#!/bin/bash
# 知識庫爬蟲 Wrapper - 同時跑字幕版 + ASR 版
LOG="$HOME/.openclaw/workspace/knowledge-base/crawler-daily.log"
cd "$HOME/.openclaw/workspace/knowledge-base"

echo "=== 字幕版 $(date) ===" >> "$LOG"
python3 crawl_subtitles.py >> "$LOG" 2>&1

echo "=== ASR版 $(date) ===" >> "$LOG"
python3 crawl_asr.py >> "$LOG" 2>&1

echo "=== 完成 $(date) ===" >> "$LOG"
