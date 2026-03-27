#!/bin/bash
LOG="$HOME/.openclaw/workspace/knowledge-base/crawler-daily.log"
echo "=== Loop started at $(date) ===" >> "$LOG"
cd "$HOME/.openclaw/workspace/knowledge-base"
while true; do
  python3 crawl_stable.py >> "$LOG" 2>&1
  STATE=$(cat crawl_state.json 2>/dev/null)
  IDX=$(echo "$STATE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('last_channel_index','?'))" 2>/dev/null)
  echo ">>> Round done at $(date). last_channel_index=$IDX" >> "$LOG"
  sleep 3
done
