#!/bin/bash
# kd 爬蟲腳本 - 直接用 shell 迴圈
# 每個頻道抓 3 部影片

BASE_DIR="$HOME/.openclaw/workspace/knowledge-base/experts"
LOG_FILE="$BASE_DIR/kd-crawl-$(date +%Y-%m-%d).log"

CHANNELS=(
    "胡乃文开播|@Dr.Hu_talk"
    "柏格醫生中文|@drbergchinese"
    "Dr.HuangAmin|@Dr.HuangAmin"
    "周慕姿放心說|@muerstalk"
    "松明讲心理|@SongMing"
    "超真實商談|@RealBizChat"
    "Cofit211|@Cofit211"
    "泛科學|@PanScitw"
    "泛科學院|@panscischool"
)

echo "========================================"
echo "kd 知識庫爬蟲 $(date)"
echo "========================================" | tee -a "$LOG_FILE"

for entry in "${CHANNELS[@]}"; do
    channel_name="${entry%%|*}"
    channel_username="${entry##*|}"
    
    echo "" | tee -a "$LOG_FILE"
    echo "📺 頻道: $channel_name ($channel_username)" | tee -a "$LOG_FILE"
    
    # 獲取影片 ID
    channel="${channel_username#@}"
    video_ids=$(yt-dlp --flat-playlist --print "%(id)s" "https://www.youtube.com/@$channel/videos" --playlist-end 3 2>/dev/null)
    
    count=0
    for vid in $video_ids; do
        output_file="$BASE_DIR/transcripts/$channel_name/${vid}.txt"
        
        if [ -f "$output_file" ]; then
            echo "  ⏭️  跳過: $vid (已有)" | tee -a "$LOG_FILE"
            continue
        fi
        
        echo "  🔄 抓取: $vid" | tee -a "$LOG_FILE"
        
        # 用 kd 轉錄（3 分鐘 timeout）
        # 先檢查是否為會員影片
        if ! yt-dlp --skip-download --list-subs "https://www.youtube.com/watch?v=$vid" 2>&1 | grep -q "HTTP Error 404"; then
            timeout 180 kd process "https://www.youtube.com/watch?v=$vid" \
                --no-summary --no-subtitles --transcriber mlx-whisper \
                -o "$output_file" 2>/dev/null
        else
            echo "  🔒 會員影片跳过" | tee -a "$LOG_FILE"
            continue
        fi
        
        if [ -s "$output_file" ]; then
            size=$(wc -c < "$output_file")
            echo "  ✅ 成功 ($size bytes)" | tee -a "$LOG_FILE"
        else
            echo "  ❌ 失敗" | tee -a "$LOG_FILE"
            rm -f "$output_file"
        fi
        
        count=$((count + 1))
        [ $count -ge 3 ] && break
        sleep 5
    done
    
    sleep 10
done

echo "" | tee -a "$LOG_FILE"
echo "🎉 完成 $(date)" | tee -a "$LOG_FILE"
