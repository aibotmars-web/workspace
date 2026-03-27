#!/bin/bash
# crawler 快速爬蟲 v3 - 8個專家頻道字幕
# 策略: kd subtitles -l zh (快 ~1秒) → 無字幕才轉錄 → 會員果斷跳過

DEST="/Users/marsbot/.openclaw/workspace/agents/crawler/subtitles/downloads"
LOG="/Users/marsbot/.openclaw/workspace/agents/crawler/subtitles/crawl.log"
PROGRESS="/Users/marsbot/.openclaw/workspace/agents/crawler/subtitles/PROGRESS_REALTIME.txt"
mkdir -p "$DEST"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"
}

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

log "=========================================="
log "🚀 快速爬蟲 v3 啟動 (修正會員偵測)"
log "=========================================="

for entry in "${CHANNELS[@]}"; do
    CHANNEL_ID="${entry%%|*}"
    CHANNEL_NAME="${entry#*|}"
    CHANNEL_DIR="$DEST/$CHANNEL_NAME"
    mkdir -p "$CHANNEL_DIR"
    
    log ""
    log "📺 $CHANNEL_NAME"
    log "-------------------------------------------"
    
    VIDEO_LIST=$(yt-dlp --flat-playlist --print "%(id)s" \
        "https://www.youtube.com/channel/$CHANNEL_ID/videos" 2>/dev/null)
    [ -z "$VIDEO_LIST" ] && VIDEO_LIST=$(yt-dlp --flat-playlist --print "%(id)s" \
        "https://www.youtube.com/$CHANNEL_ID/videos" 2>/dev/null)
    
    [ -z "$VIDEO_LIST" ] && { log "⚠️ 無法取得 $CHANNEL_NAME 影片清單"; continue; }
    
    TOTAL=$(echo "$VIDEO_LIST" | wc -l | tr -d ' ')
    DONE=0 SKIP=0 FAIL=0
    SUB_OK=0 TR_OK=0
    
    while IFS= read -r VIDEO_ID; do
        [ -z "$VIDEO_ID" ] && continue
        ((DONE++))
        OUTPUT="$CHANNEL_DIR/${VIDEO_ID}.txt"
        
        # 跳過已存在的
        if [ -f "$OUTPUT" ] && [ -s "$OUTPUT" ]; then
            ((SKIP++))
            continue
        fi
        
        # ===== 策略1: kd subtitles zh (快) =====
        ERR_OUT=$(kd subtitles "https://www.youtube.com/watch?v=$VIDEO_ID" \
            --language zh -o "$OUTPUT" 2>&1)
        RESULT=$?
        
        if [ $RESULT -eq 0 ] && [ -s "$OUTPUT" ]; then
            SIZE=$(wc -c < "$OUTPUT")
            ((SUB_OK++))
            log "✅ [$DONE/$TOTAL] 字幕(${SIZE}B): $VIDEO_ID"
            echo "$CHANNEL_NAME|$VIDEO_ID|字幕|$(date '+%H:%M:%S')" >> "$PROGRESS"
            continue
        fi
        
        # ===== 策略2: 會員限定 → 跳過 =====
        # 檢查錯誤訊息內容（不在檔案裡，在 stderr）
        if echo "$ERR_OUT" | grep -qi "members.only\|join this channel\|會員\|no subtitles.*this video"; then
            rm -f "$OUTPUT"
            ((FAIL++))
            log "⏭️  [$DONE/$TOTAL] 會員: $VIDEO_ID"
            continue
        fi
        
        # ===== 策略3: 真的沒有字幕 → 轉錄（慢）=====
        rm -f "$OUTPUT"
        kd transcribe "https://www.youtube.com/watch?v=$VIDEO_ID" \
            --no-subtitles --backend mlx-whisper -o "$OUTPUT" 2>/dev/null
        
        if [ -f "$OUTPUT" ] && [ -s "$OUTPUT" ]; then
            SIZE=$(wc -c < "$OUTPUT")
            ((TR_OK++))
            log "✅ [$DONE/$TOTAL] 轉錄(${SIZE}B): $VIDEO_ID"
            echo "$CHANNEL_NAME|$VIDEO_ID|轉錄|$(date '+%H:%M:%S')" >> "$PROGRESS"
        else
            rm -f "$OUTPUT"
            ((FAIL++))
            log "⚠️  [$DONE/$TOTAL] 失敗: $VIDEO_ID"
        fi
        
    done <<< "$VIDEO_LIST"
    
    log "✅ $CHANNEL_NAME 完成 | 字幕:$SUB_OK 轉錄:$TR_OK 跳過:$SKIP 失敗:$FAIL"
done

log ""
log "=========================================="
log "🎉 全部完成！"
log "=========================================="
