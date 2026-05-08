#!/bin/bash
# kd 爬蟲腳本 v3 - 含錯誤自動繼續
# 每個頻道抓 3 部影片，錯誤不中斷

set +e  # 不要因為錯誤而退出

BASE_DIR="$HOME/.openclaw/workspace/knowledge-base/experts"
LOG_FILE="$BASE_DIR/kd-crawl-$(date +%Y-%m-%d).log"
PROGRESS_FILE="$BASE_DIR/progress.json"
CSV_FILE="$BASE_DIR/progress.csv"
CACHE_FILE="$BASE_DIR/youtube_cache.txt"

# 錯誤計數
ERROR_COUNT=0
SUCCESS_COUNT=0

# 頻道對照表
CHANNELS=(
    "胡乃文开播|@Dr.Hu_talk|Dr.Hu_talk"
    "柏格醫生中文|@drbergchinese|drbergchinese"
    "Dr.HuangAmin|@Dr.HuangAmin|Dr.HuangAmin"
    "周慕姿放心說|@muerstalk|muerstalk"
    "松明讲心理|@SongMing|SongMing"
    "超真實商談|@RealBizChat|超真實商圈"
    "Cofit211|@Cofit211|Cofit211"
    "泛科學|@PanScitw|PanScitw"
    "泛科學院|@panscischool|panscischool"
    "top3pct|@top3pct|top3pct"
)

get_youtube_total() {
    local username="$1"
    
    # 先看快取
    local cached=$(grep "^${username}|" "$CACHE_FILE" 2>/dev/null | cut -d'|' -f2)
    if [ -n "$cached" ] && [ "$cached" -gt 0 ] 2>/dev/null; then
        echo "$cached"
        return
    fi
    
    # 用 --playlist-end 500 自動翻下一頁抓正確總數
    local count=$(timeout 25 yt-dlp --flat-playlist --print '%(id)s' "https://www.youtube.com${username}/videos" --playlist-end 500 2>/dev/null | wc -l | tr -d ' ')
    
    if [ -n "$count" ] && [ "$count" -gt 0 ] 2>/dev/null; then
        echo "$count"
    else
        echo "0"
    fi
}

get_crawled_count() {
    local dir_name="$1"
    local count=0
    [ -d "$BASE_DIR/transcripts/$dir_name" ] && count=$((count + $(ls "$BASE_DIR/transcripts/$dir_name"/*.txt 2>/dev/null | wc -l | tr -d ' ')))
    [ -d "$BASE_DIR/transcripts/$dir_name" ] && count=$((count + $(ls "$BASE_DIR/transcripts/$dir_name"/*.md 2>/dev/null | wc -l | tr -d ' ')))
    [ -d "$BASE_DIR/$dir_name" ] && count=$((count + $(ls "$BASE_DIR/$dir_name"/*.md 2>/dev/null | wc -l | tr -d ' ')))
    [ -d "$BASE_DIR/$dir_name" ] && count=$((count + $(ls "$BASE_DIR/$dir_name"/*.txt 2>/dev/null | wc -l | tr -d ' ')))
    echo "$count"
}

generate_json() {
    echo "{" > "$PROGRESS_FILE"
    echo '  "updated": "'$(date -Iseconds)'",' >> "$PROGRESS_FILE"
    echo '  "channels": [' >> "$PROGRESS_FILE"
    local first=1
    for entry in "${CHANNELS[@]}"; do
        channel_name="${entry%%|*}"
        rest="${entry#*|}"
        channel_username="${rest%%|*}"
        dir_name="${rest##*|}"
        youtube_total=$(get_youtube_total "$channel_username")
        crawled=$(get_crawled_count "$dir_name")
        progress=0
        [ "$youtube_total" -gt 0 ] 2>/dev/null && progress=$((crawled * 100 / youtube_total))
        [ $first -eq 0 ] && echo "," >> "$PROGRESS_FILE"
        first=0
        printf '    {"name":"%s","youtube":%s,"crawled":%s,"progress":%s}' "$channel_name" "$youtube_total" "$crawled" "$progress" >> "$PROGRESS_FILE"
    done
    echo "" >> "$PROGRESS_FILE"
    echo "  ]," >> "$PROGRESS_FILE"
    local total_yt=0; local total_cr=0
    for entry in "${CHANNELS[@]}"; do
        rest="${entry#*|}"
        channel_username="${rest%%|*}"
        dir_name="${rest##*|}"
        total_yt=$((total_yt + $(get_youtube_total "$channel_username")))
        total_cr=$((total_cr + $(get_crawled_count "$dir_name")))
    done
    echo '  "summary": {"total_youtube":'$total_yt',"total_crawled":'$total_cr'}' >> "$PROGRESS_FILE"
    echo "}" >> "$PROGRESS_FILE"
}

generate_csv() {
    echo "頻道,YouTube總數,已爬,進度%" > "$CSV_FILE"
    for entry in "${CHANNELS[@]}"; do
        channel_name="${entry%%|*}"
        rest="${entry#*|}"
        channel_username="${rest%%|*}"
        dir_name="${rest##*|}"
        youtube_total=$(get_youtube_total "$channel_username")
        crawled=$(get_crawled_count "$dir_name")
        progress=0
        [ "$youtube_total" -gt 0 ] 2>/dev/null && progress=$((crawled * 100 / youtube_total))
        echo "$channel_name,$youtube_total,$crawled,$progress%" >> "$CSV_FILE"
    done
}

show_progress() {
    echo "📊 知識庫爬蟲進度"
    echo "========================"
    generate_csv
    cat "$CSV_FILE"
    echo ""
}

# ===== 爬蟲核心（含錯誤自動繼續）=====
crawl_video() {
    local vid="$1"
    local output_file="$2"
    local channel_name="$3"
    
    echo "  🔄 抓取: $vid" | tee -a "$LOG_FILE"
    
    # 檢查是否為會員影片
    if timeout 15 yt-dlp --skip-download --list-subs "https://www.youtube.com/watch?v=$vid" 2>&1 | grep -q "HTTP Error 404"; then
        echo "  🔒 會員影片跳过" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # 嘗試抓字幕
    local sub_exists=$(timeout 15 yt-dlp --skip-download --list-subs "https://www.youtube.com/watch?v=$vid" 2>&1 | grep -cE "(zh-Hant|zh-CN|en) \[exists\]" || echo 0)
    
    if [ "$sub_exists" -gt 0 ]; then
        # 有字幕，用 kd subtitles
        timeout 90 kd subtitles "https://www.youtube.com/watch?v=$vid" -o "$output_file" 2>&1 | tee -a "$LOG_FILE"
    else
        # 無字幕，用 ASR
        timeout 300 kd process "https://www.youtube.com/watch?v=$vid" --no-summary --no-subtitles --transcriber mlx-whisper -o "$output_file" 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # 檢查結果
    if [ -s "$output_file" ]; then
        size=$(wc -c < "$output_file")
        if [ "$size" -gt 100 ]; then
            echo "  ✅ 成功 ($size bytes)" | tee -a "$LOG_FILE"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            return 0
        fi
    fi
    
    # 失敗
    echo "  ⚠️ 失敗/空檔案，继续下一個" | tee -a "$LOG_FILE"
    rm -f "$output_file"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    return 1
}

# ===== 主程式 =====
case "${1:-crawl}" in
    progress|status)
        show_progress
        ;;
    crawl)
        echo "========================================"
        echo "kd 知識庫爬蟲 v3 $(date)"
        echo "錯誤自動繼續模式" | tee -a "$LOG_FILE"
        echo "========================================" | tee -a "$LOG_FILE"
        
        generate_json; generate_csv
        echo "📊 起始進度已記錄" | tee -a "$LOG_FILE"
        
        for entry in "${CHANNELS[@]}"; do
            channel_name="${entry%%|*}"
            rest="${entry#*|}"
            channel_username="${rest%%|*}"
            dir_name="${rest##*|}"
            
            echo "" | tee -a "$LOG_FILE"
            echo "📺 頻道: $channel_name ($channel_username)" | tee -a "$LOG_FILE"
            
            # 獲取影片 ID（最多 5 個）
            channel="${channel_username#@}"
            video_ids=$(timeout 25 yt-dlp --flat-playlist --print "%(id)s" "https://www.youtube.com/@$channel/videos" --playlist-end 5 2>/dev/null)
            
            [ -z "$video_ids" ] && echo "  ❌ 無法獲取影片列表，跳過" | tee -a "$LOG_FILE" && continue
            
            count=0
            for vid in $video_ids; do
                # 檢查是否已爬過
                output_file=""
                for check_dir in "$BASE_DIR/$dir_name" "$BASE_DIR/transcripts/$channel_name"; do
                    if [ ! -f "$check_dir/${vid}.txt" ] && [ ! -f "$check_dir/${vid}.md" ]; then
                        output_file="$check_dir/${vid}.txt"
                        mkdir -p "$(dirname "$output_file")"
                        break
                    fi
                done
                
                if [ -z "$output_file" ]; then
                    echo "  ⏭️  $vid 已有" | tee -a "$LOG_FILE"
                    continue
                fi
                
                # 抓取（錯誤不中斷）
                crawl_video "$vid" "$output_file" "$channel_name" || true
                
                count=$((count + 1))
                [ $count -ge 3 ] && break
                
                # 每次間隔
                sleep 3
            done
            
            # 每個頻道爬完更新進度
            generate_json; generate_csv
            
            # 頻道間間隔
            sleep 8
        done
        
        echo "" | tee -a "$LOG_FILE"
        echo "🎉 完成 $(date)" | tee -a "$LOG_FILE"
        echo "成功: $SUCCESS_COUNT | 錯誤: $ERROR_COUNT" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo "📈 最終進度：" | tee -a "$LOG_FILE"
        cat "$CSV_FILE" | tee -a "$LOG_FILE"
        ;;
    *)
        echo "用法: $0 [crawl|progress]"
        ;;
esac