#!/bin/bash
# crawler 爬蟲 v5 - 429時自動切換轉錄
# 策略: 字幕 → 429就轉錄 → 真的會員/不存在才跳過

DEST="/Users/marsbot/.openclaw/workspace/agents/crawler/subtitles/downloads"
LOG="/Users/marsbot/.openclaw/workspace/agents/crawler/subtitles/crawl.log"
PROGRESS="/Users/marsbot/.openclaw/workspace/agents/crawler/subtitles/PROGRESS_REALTIME.txt"
mkdir -p "$DEST"

log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"; }

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

log "🚀 爬蟲 v5 啟動（429自動轉錄版）"

for entry in "${CHANNELS[@]}"; do
    CHANNEL_ID="${entry%%|*}"
    CHANNEL_NAME="${entry#*|}"
    CHANNEL_DIR="$DEST/$CHANNEL_NAME"
    mkdir -p "$CHANNEL_DIR"
    
    log ""
    log "📺 $CHANNEL_NAME"
    
    VIDEO_LIST=$(yt-dlp --flat-playlist --print "%(id)s" \
        "https://www.youtube.com/channel/$CHANNEL_ID/videos" 2>/dev/null)
    [ -z "$VIDEO_LIST" ] && VIDEO_LIST=$(yt-dlp --flat-playlist --print "%(id)s" \
        "https://www.youtube.com/$CHANNEL_ID/videos" 2>/dev/null)
    
    [ -z "$VIDEO_LIST" ] && { log "⚠️ 無法取得 $CHANNEL_NAME 影片清單"; continue; }
    
    TOTAL=$(echo "$VIDEO_LIST" | wc -l | tr -d ' ')
    DONE=0 SUB=0 TRANS=0 SKIP=0 FAIL=0
    
    while IFS= read -r VIDEO_ID; do
        [ -z "$VIDEO_ID" ] && continue
        ((DONE++))
        OUTPUT="$CHANNEL_DIR/${VIDEO_ID}.txt"
        
        # 跳過已存在的
        if [ -f "$OUTPUT" ] && [ -s "$OUTPUT" ]; then
            ((SKIP++))
            continue
        fi
        
        # ===== 嘗試字幕（快）=====
        ERR_OUT=$(kd subtitles "https://www.youtube.com/watch?v=$VIDEO_ID" \
            --language zh -o "$OUTPUT" 2>&1)
        RESULT=$?
        
        if [ $RESULT -eq 0 ] && [ -s "$OUTPUT" ]; then
            SIZE=$(wc -c < "$OUTPUT")
            ((SUB++))
            log "✅ [$DONE/$TOTAL] 字幕: $VIDEO_ID (${SIZE}B)"
            sleep 1
            continue
        fi
        
        # 讀取錯誤訊息
        [ -f "$OUTPUT" ] && ERR_FILE=$(cat "$OUTPUT" 2>/dev/null) || ERR_FILE=""
        COMBINED="$ERR_OUT $ERR_FILE"
        
        # ===== 會員限定 → 跳過 =====
        if echo "$COMBINED" | grep -qi "members.only\|join this channel\|會員"; then
            rm -f "$OUTPUT"
            ((FAIL++))
            log "⏭️  [$DONE/$TOTAL] 會員: $VIDEO_ID"
            sleep 0.5
            continue
        fi
        
        # ===== 429限流 / 無字幕 → 轉錄（利用時間）=====
        if echo "$COMBINED" | grep -qi "429\|too many\|no subtitles\|unavailable\|private\|not available\|video unavailable"; then
            rm -f "$OUTPUT"
            log "🔄 [$DONE/$TOTAL] 限流/無字幕，改用轉錄: $VIDEO_ID"
            kd transcribe "https://www.youtube.com/watch?v=$VIDEO_ID" \
                --no-subtitles --backend mlx-whisper -o "$OUTPUT" 2>/dev/null
            if [ -f "$OUTPUT" ] && [ -s "$OUTPUT" ]; then
                SIZE=$(wc -c < "$OUTPUT")
                ((TRANS++))
                log "✅ [$DONE/$TOTAL] 轉錄: $VIDEO_ID (${SIZE}B)"
            else
                rm -f "$OUTPUT"
                ((FAIL++))
                log "⚠️  [$DONE/$TOTAL] 失敗: $VIDEO_ID"
            fi
            sleep 1
            continue
        fi
        
        # ===== 其他錯誤 → 跳過 =====
        rm -f "$OUTPUT"
        ((FAIL++))
        log "⚠️  [$DONE/$TOTAL] 失敗: $VIDEO_ID"
        sleep 2
        
    done <<< "$VIDEO_LIST"
    
    log "✅ $CHANNEL_NAME 完成 | 字幕:$SUB 轉錄:$TRANS 跳過:$SKIP 失敗:$FAIL"
done

log "🎉 全部完成！"
