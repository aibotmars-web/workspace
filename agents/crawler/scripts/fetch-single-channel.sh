#!/bin/bash
# YT 專家字幕爬取腳本 - 優化版
# 每次只處理一個頻道，更可靠

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

EXPERT_NAME="$1"
CHANNEL_URL="$2"

OUTPUT_DIR="subtitles/yt-experts/$EXPERT_NAME"
LOG_FILE="logs/yt-experts-$(date +%Y-%m-%d).log"

mkdir -p "$OUTPUT_DIR" "logs"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 處理: $EXPERT_NAME" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 頻道: $CHANNEL_URL" | tee -a "$LOG_FILE"

# 獲取最新 5 部影片
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 獲取影片清單..." | tee -a "$LOG_FILE"
yt-dlp --js-runtimes node --get-id "$CHANNEL_URL" 2>/dev/null | head -5 > "/tmp/${EXPERT_NAME}_videos.txt"

SUBTITLE_COUNT=0
while IFS= read -r VIDEO_ID; do
    if [ -z "$VIDEO_ID" ]; then
        continue
    fi

    VIDEO_URL="https://www.youtube.com/watch?v=$VIDEO_ID"
    SUBTITLE_FILE="$OUTPUT_DIR/${VIDEO_ID}.txt"

    # 嘗試下載字幕
    yt-dlp --js-runtimes node --write-subs --sub-lang zh-Hant,zh-CN,en --skip-download \
        -o "$SUBTITLE_FILE" "$VIDEO_URL" 2>/dev/null

    if [ -f "${SUBTITLE_FILE%.*}.zh-Hant.vtt" ] || [ -f "${SUBTITLE_FILE%.*}.zh-TW.vtt" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ $EXPERT_NAME: $VIDEO_ID (中文字幕)" | tee -a "$LOG_FILE"
        SUBTITLE_COUNT=$((SUBTITLE_COUNT + 1))
    elif [ -f "${SUBTITLE_FILE%.*}.en.vtt" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ $EXPERT_NAME: $VIDEO_ID (英文字幕)" | tee -a "$LOG_FILE"
        SUBTITLE_COUNT=$((SUBTITLE_COUNT + 1))
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ $EXPERT_NAME: $VIDEO_ID (無字幕)" | tee -a "$LOG_FILE"
    fi

done < "/tmp/${EXPERT_NAME}_videos.txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成: $EXPERT_NAME - 獲取 $SUBTITLE_COUNT 個字幕" | tee -a "$LOG_FILE"
