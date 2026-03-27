#!/bin/bash
# YouTube 字幕爬取脚本
# 处理限流和错误

OUTPUT_DIR="$HOME/.openclaw/workspace/knowledge-base/experts/transcripts"
MAX_PER_CHANNEL=6
MAX_RETRIES=3
WAIT_ON_ERROR=30

# 频道列表 (频道名 -> URL)
CHANNELS=(
    "胡乃文开播|https://www.youtube.com/@Dr.Hu_talk"
    "柏格醫生中文|https://www.youtube.com/@drbergchinese"
    "Dr.HuangAmin|https://www.youtube.com/@Dr.HuangAmin"
    "周慕姿放心說|https://www.youtube.com/@muerstalk"
    "松明讲心理|https://www.youtube.com/@SongMing"
    "DrHarveyTalk|https://www.youtube.com/@DrHarveyTalk"
    "Cofit211|https://www.youtube.com/@Cofit211"
    "泛科學|https://www.youtube.com/@PanScitw"
    "泛科學院|https://www.youtube.com/@panscischool"
)

log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

get_transcript() {
    local video_id=$1
    local output_file=$2
    local retry=0
    
    while [ $retry -lt $MAX_RETRIES ]; do
        # 尝试获取字幕 - 优先中文
        yt-dlp "https://www.youtube.com/watch?v=$video_id" \
            --write-subs --write-auto-subs \
            --sub-lang "zh-TW,zh-CN,zh,en" \
            --skip-download \
            --output "$output_file.%(ext)s" \
            --quiet 2>&1
        
        if [ $? -eq 0 ]; then
            # 找到并转换字幕文件
            for ext in vtt srt; do
                sub_file="$output_file.$ext"
                if [ -f "$sub_file" ]; then
                    # 转换为纯文本
                    sed 's/<[^>]*>//g' "$sub_file" > "$output_file.txt" 2>/dev/null
                    if [ -s "$output_file.txt" ]; then
                        rm -f "$sub_file"
                        return 0
                    fi
                fi
            done
        fi
        
        # 检查是否被限流
        if yt-dlp "https://www.youtube.com/watch?v=$video_id" --skip-download --quiet 2>&1 | grep -qi "429\|rate\|too many"; then
            log "⚠️ 检测到限流，等待 ${WAIT_ON_ERROR}s..."
            sleep $WAIT_ON_ERROR
            retry=$((retry + 1))
            continue
        fi
        
        break
    done
    
    return 1
}

# 主循环
total=0
success=0

for entry in "${CHANNELS[@]}"; do
    channel_name="${entry%%|*}"
    channel_url="${entry##*|}"
    channel_dir="$OUTPUT_DIR/$channel_name"
    
    log "📺 处理频道: $channel_name"
    
    # 获取视频列表
    video_ids=$(yt-dlp --get-id "$channel_url" --playlist-end $MAX_PER_CHANNEL 2>/dev/null)
    
    count=0
    for vid in $video_ids; do
        total=$((total + 1))
        output_file="$channel_dir/$vid"
        
        log "  → 抓取 $vid..."
        
        if get_transcript "$vid" "$output_file"; then
            success=$((success + 1))
            log "    ✓ 成功"
        else
            log "    ✗ 失败"
        fi
        
        # 每次抓取后短暂等待，避免太快被限流
        sleep 2
        
        count=$((count + 1))
        if [ $count -ge $MAX_PER_CHANNEL ]; then
            break
        fi
    done
    
    log "  完成 $count 个视频"
    # 频道间等待
    sleep 5
done

log "========================================"
log "完成！总计: $total, 成功: $success"
log "保存位置: $OUTPUT_DIR"
