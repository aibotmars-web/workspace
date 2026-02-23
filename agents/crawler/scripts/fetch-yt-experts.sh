#!/bin/bash
# YT 專家字幕爬取腳本
# 使用 yt-dlp 批量下載字幕

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 專家頻道列表（使用平行陣列）
EXPERT_NAMES=(
    "阿銘師x銭還傳"
    "胡乃文開講"
    "柏格醫生"
    "周慕姿放心說"
    "松明講心理"
    "Dr.Harvey"
    "初日醫學"
    "泛科學"
    "泛科學院"
)

CHANNEL_URLS=(
    "https://www.youtube.com/@Dr.HuangAmin"
    "https://www.youtube.com/@Dr.Hu_talk"
    "https://www.youtube.com/@drbergchinese"
    "https://www.youtube.com/@muerstalk"
    "https://www.youtube.com/@SongMing"
    "https://www.youtube.com/@DrHarveyTalk"
    "https://www.youtube.com/@Cofit211"
    "https://www.youtube.com/@PanScitw"
    "https://www.youtube.com/@panscischoo"
)

LOG_FILE="logs/yt-experts-$(date +%Y-%m-%d).log"
OUTPUT_DIR="subtitles/yt-experts"

mkdir -p "$OUTPUT_DIR" "logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================"
log "YT 專家字幕爬取任務開始"
log "========================================"

TOTAL_CHANNELS=${#EXPERT_NAMES[@]}
CURRENT=0
SUCCESS_COUNT=0
SUBTITLE_COUNT=0
NO_SUBTITLE_COUNT=0

for i in "${!EXPERT_NAMES[@]}"; do
    EXPERT_NAME="${EXPERT_NAMES[$i]}"
    CHANNEL_URL="${CHANNEL_URLS[$i]}"
    CURRENT=$((CURRENT + 1))

    log ""
    log "[$CURRENT/$TOTAL_CHANNELS] 處理: $EXPERT_NAME"
    log "  頻道: $CHANNEL_URL"

    # 獲取頻道最新 10 部影片
    VIDEO_LIST_FILE="$OUTPUT_DIR/${i}_${EXPERT_NAME}_videos.txt"

    yt-dlp --js-runtimes node --get-id "$CHANNEL_URL" 2>/dev/null | head -10 > "$VIDEO_LIST_FILE"

    VIDEO_COUNT=$(wc -l < "$VIDEO_LIST_FILE")
    log "  發現影片數: $VIDEO_COUNT"

    mkdir -p "$OUTPUT_DIR/$EXPERT_NAME"

    # 處理每個影片
    while IFS= read -r VIDEO_ID; do
        if [ -z "$VIDEO_ID" ]; then
            continue
        fi

        VIDEO_URL="https://www.youtube.com/watch?v=$VIDEO_ID"
        SUBTITLE_FILE="$OUTPUT_DIR/$EXPERT_NAME/${VIDEO_ID}.txt"

        # 檢查是否有字幕
        SUBS=$(yt-dlp --js-runtimes node --list-subs "$VIDEO_URL" 2>&1 | grep -c "automatic captions\|subtitles" || true)

        if [ "$SUBS" -gt "0" ]; then
            log "    下載字幕: $VIDEO_ID"
            yt-dlp --js-runtimes node --write-subs --sub-lang zh-Hant,zh-CN,en --skip-download \
                -o "$SUBTITLE_FILE" "$VIDEO_URL" 2>/dev/null

            if [ -f "${SUBTITLE_FILE%.*}.zh-Hant.vtt" ] || [ -f "${SUBTITLE_FILE%.*}.zh-TW.vtt" ]; then
                SUBTITLE_COUNT=$((SUBTITLE_COUNT + 1))
                log "    ✓ 字幕下載成功"
            elif [ -f "${SUBTITLE_FILE%.*}.en.vtt" ]; then
                SUBTITLE_COUNT=$((SUBTITLE_COUNT + 1))
                log "    ✓ 英文字幕下載成功"
            fi
        else
            NO_SUBTITLE_COUNT=$((NO_SUBTITLE_COUNT + 1))
        fi

    done < "$VIDEO_LIST_FILE"

    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

done

log ""
log "========================================"
log "爬取完成!"
log "========================================"
log "處理頻道數: $SUCCESS_COUNT/$TOTAL_CHANNELS"
log "有字幕影片: $SUBTITLE_COUNT 部"
log "無字幕影片: $NO_SUBTITLE_COUNT 部"
log "輸出目錄: $OUTPUT_DIR"
