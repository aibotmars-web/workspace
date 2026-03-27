#!/bin/bash
# crawler 爬蟲 v4 - 速率友善版
# 策略: kd subtitles -l zh → 429就等30秒 → 真的會員/不存在才跳過

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

log "🚀 爬蟲 v4 啟動（速率友善版）"

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
    DONE=0 SKIP=0 FAIL=0 RATE_LIMIT=0
    
    while IFS= read -r VIDEO_ID; do
        [ -z "$VIDEO_ID" ] && continue
        ((DONE++))
        OUTPUT="$CHANNEL_DIR/${VIDEO_ID}.txt"
        
        # 跳過已存在的
        if [ -f "$OUTPUT" ] && [ -s "$OUTPUT" ]; then
            ((SKIP++))
            continue
        fi
        
        # ===== kd subtitles =====
        ERR_OUT=$(kd subtitles "https://www.youtube.com/watch?v=$VIDEO_ID" \
            --language zh -o "$OUTPUT" 2>&1)
        RESULT=$?
        
        if [ $RESULT -eq 0 ] && [ -s "$OUTPUT" ]; then
            SIZE=$(wc -c < "$OUTPUT")
            log "✅ [$DONE/$TOTAL] ${SIZE}B $VIDEO_ID"
            sleep 0.5
            continue
        fi
        
        # ===== 讀取錯誤訊息（從輸出檔）=====
        if [ -f "$OUTPUT" ]; then
            ERR_FILE=$(cat "$OUTPUT" 2>/dev/null)
        else
            ERR_FILE=""
        fi
        COMBINED="$ERR_OUT $ERR_FILE"
        
        # 429 Rate Limit → 等30秒重試一次
        if echo "$COMBINED" | grep -qi "429\|too many requests"; then
            rm -f "$OUTPUT"
            log "⏸️  [$DONE/$TOTAL] 429限流，等30秒..."
            sleep 30
            # 重試一次
            kd subtitles "https://www.youtube.com/watch?v=$VIDEO_ID" \
                --language zh -o "$OUTPUT" 2>/dev/null
            if [ -s "$OUTPUT" ]; then
                SIZE=$(wc -c < "$OUTPUT")
                log "✅ [$DONE/$TOTAL] 重試成功 ${SIZE}B $VIDEO_ID"
                sleep 0.5
                continue
            fi
            ((RATE_LIMIT++))
            log "⚠️  [$DONE/$TOTAL] 429仍失敗: $VIDEO_ID"
            sleep 5
            continue
        fi
        
        # 會員限定 → 跳過
        if echo "$COMBINED" | grep -qi "members.only\|join this channel\|會員"; then
            rm -f "$OUTPUT"
            ((FAIL++))
            log "⏭️  [$DONE/$TOTAL] 會員: $VIDEO_ID"
            sleep 1
            continue
        fi
        
        # 影片不存在/私人 → 跳過
        if echo "$COMBINED" | grep -qi "video unavailable\|unavailable\|private\|not available"; then
            rm -f "$OUTPUT"
            ((FAIL++))
            log "⏭️  [$DONE/$TOTAL] 不存在: $VIDEO_ID"
            sleep 0.5
            continue
        fi
        
        # 其他錯誤 → 跳過（不轉錄浪費時間）
        rm -f "$OUTPUT"
        ((FAIL++))
        log "⚠️  [$DONE/$TOTAL] 失敗: $VIDEO_ID"
        sleep 2
        
    done <<< "$VIDEO_LIST"
    
    log "✅ $CHANNEL_NAME 完成 | 成功:$((DONE-SKIP-FAIL-RATE_LIMIT)) 跳過:$SKIP 失敗:$FAIL 限流:$RATE_LIMIT"
done

log "🎉 全部完成！"
