#!/bin/bash
# crawler 全面爬蟲 - 8個專家頻道字幕
# kd CLI 本地抓取，不需 API key

DEST="/Users/marsbot/.openclaw/workspace/agents/crawler/subtitles/downloads"
LOG="/Users/marsbot/.openclaw/workspace/agents/crawler/subtitles/crawl.log"
mkdir -p "$DEST"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"
}

# 頻道清單
CHANNELS=(
    "UCYUHZk66njfU1VFwSviXPGQ|胡乃文開獎"
    "UCUXi5mmqbvIithAs9AaxEtw|柏格醫生"
    "UCIhaNRLn4OQDWZJiVvdhl5A|周慕姿放心說"
    "UCHNDk7584Q5g7RQCAFj7RFA|松明講心理"
    "UCzOblez4o3mZEkpOeFZdHWQ|初日醫學"
    "UCuHHKbwC0TWjeqxbqdO-N_g|泛科學"
    "@panscischool|泛科學院"
    "UC97oYK3XMf9RLtkc0lO8C-Q|健康旦DrHarvey"
)

for entry in "${CHANNELS[@]}"; do
    CHANNEL_ID="${entry%%|*}"
    CHANNEL_NAME="${entry#*|}"
    CHANNEL_DIR="$DEST/$CHANNEL_NAME"
    mkdir -p "$CHANNEL_DIR"
    
    log "=========================================="
    log "開始抓取：$CHANNEL_NAME"
    log "=========================================="
    
    # 取得影片清單
    VIDEO_LIST=$(yt-dlp --flat-playlist --print "%(id)s" \
        "https://www.youtube.com/channel/$CHANNEL_ID/videos" \
        2>/dev/null)
    
    if [ -z "$VIDEO_LIST" ]; then
        VIDEO_LIST=$(yt-dlp --flat-playlist --print "%(id)s" \
            "https://www.youtube.com/$CHANNEL_ID/videos" \
            2>/dev/null)
    fi
    
    if [ -z "$VIDEO_LIST" ]; then
        log "⚠️ 無法取得 $CHANNEL_NAME 的影片清單，跳過"
        continue
    fi
    
    COUNT=$(echo "$VIDEO_LIST" | wc -l)
    log "📺 $CHANNEL_NAME: 找到 $COUNT 部影片"
    
    i=0
    while IFS= read -r VIDEO_ID; do
        [ -z "$VIDEO_ID" ] && continue
        ((i++))
        
        OUTPUT_FILE="$CHANNEL_DIR/${VIDEO_ID}.txt"
        
        if [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
            continue
        fi
        
        # kd抓字幕
        ERR=$(kd subtitles "https://www.youtube.com/watch?v=$VIDEO_ID" \
            -o "$OUTPUT_FILE" --no-thumbnail --no-timestamps 2>&1)
        RESULT=$?
        
        if [ $RESULT -eq 0 ] && [ -s "$OUTPUT_FILE" ]; then
            SIZE=$(wc -c < "$OUTPUT_FILE")
            if [ "$SIZE" -gt 100 ]; then
                log "✅  [$i/$COUNT] 字幕: $VIDEO_ID (${SIZE}B)"
                continue
            fi
        fi
        
        # 檢查是否會員限定
        if echo "$ERR" | grep -qi "members-only\|join this channel\|member.only\|會員"; then
            rm -f "$OUTPUT_FILE"
            log "⏭️  [$i/$COUNT] 會員限定，跳過: $VIDEO_ID"
            continue
        fi
        
        # 嘗試轉錄
        rm -f "$OUTPUT_FILE"
        ERR2=$(kd transcribe "https://www.youtube.com/watch?v=$VIDEO_ID" \
            --no-subtitles --backend mlx-whisper -o "$OUTPUT_FILE" 2>&1)
        RESULT2=$?
        
        if [ $RESULT2 -eq 0 ] && [ -s "$OUTPUT_FILE" ]; then
            SIZE=$(wc -c < "$OUTPUT_FILE")
            log "✅  [$i/$COUNT] 轉錄: $VIDEO_ID (${SIZE}B)"
        else
            rm -f "$OUTPUT_FILE"
            if echo "$ERR2" | grep -qi "members-only\|join this channel"; then
                log "⏭️  [$i/$COUNT] 會員限定(轉錄): $VIDEO_ID"
            else
                log "⚠️  [$i/$COUNT] 失敗: $VIDEO_ID"
            fi
        fi
        
    done <<< "$VIDEO_LIST"
    log "✅ $CHANNEL_NAME 完成"
    log ""
done

log "🎉 全部頻道抓取完成！"
find "$DEST" -name "*.txt" -exec wc -c {} + 2>/dev/null | tail -1
