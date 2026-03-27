#!/bin/bash
# 使用浏览器获取 YouTube 字幕

OUTPUT_DIR="$HOME/.openclaw/workspace/knowledge-base/experts/transcripts"

# 频道列表
CHANNELS=(
    "胡乃文开播|https://www.youtube.com/@Dr.Hu_talk"
    "柏格醫生中文|https://www.youtube.com/@drbergchinese"
    "Dr.HuangAmin|https://www.youtube.com/@Dr.HuangAmin"
    "周慕姿放心說|https://www.youtube.com/@muerstalk"
    "松明讲心理|https://www.youtube.com/@SongMing"
    "超真實商談|https://www.youtube.com/@RealBizChat"
    "Cofit211|https://www.youtube.com/@Cofit211"
    "泛科學|https://www.youtube.com/@PanScitw"
    "泛科學院|https://www.youtube.com/@panscischool"
)

echo "开始抓取字幕..."
echo "输出目录: $OUTPUT_DIR"

# 使用 yt-dlp 获取频道视频列表（只需要ID，不需要访问YouTube）
for entry in "${CHANNELS[@]}"; do
    channel_name="${entry%%|*}"
    channel_url="${entry##*|}"
    channel_dir="$OUTPUT_DIR/$channel_name"
    
    echo ""
    echo "📺 频道: $channel_name"
    
    # 获取最近6个视频ID
    video_ids=$(yt-dlp --get-id "$channel_url" --playlist-end 6 2>/dev/null)
    
    count=0
    for vid in $video_ids; do
        output_file="$channel_dir/${vid}.txt"
        
        if [ -f "$output_file" ]; then
            echo "  ✓ $vid (已存在)"
            continue
        fi
        
        echo "  → $vid"
        
        # 调用 Python 脚本获取字幕
        python3 -c "
import sys
import subprocess
import re

vid = '$vid'
output = '$output_file'

# 使用 yt-dlp 获取字幕（不需要访问视频页面）
result = subprocess.run([
    'yt-dlp', 
    '--write-subs', '--write-auto-subs',
    '--sub-lang', 'zh-TW,zh-CN,zh',
    '--skip-download',
    '--output', output + '.%(ext)s',
    'https://www.youtube.com/watch?v=' + vid
], capture_output=True, text=True)

# 检查是否有字幕文件生成
import os
for ext in ['vtt', 'srt', 'ttml']:
    f = f'{output}.{ext}'
    if os.path.exists(f):
        # 转换为纯文本
        with open(f, 'r', encoding='utf-8') as file:
            text = file.read()
        # 移除 HTML 标签和时间戳
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->.*', '', text)
        text = re.sub(r'^\s*$', '', text, flags=re.MULTILINE)
        with open(output, 'w', encoding='utf-8') as file:
            file.write(text)
        os.remove(f)
        print('ok')
        sys.exit(0)
print('fail')
"
        
        if [ -f "${output}.vtt" ]; then
            # 转换 VTT 为纯文本
            sed -i '' 's/<[^>]*>//g' "${output}.vtt" 2>/dev/null
            mv "${output}.vtt" "$output_file" 2>/dev/null || true
        fi
        
        if [ -s "$output_file" ]; then
            echo "    ✓ 成功"
        else
            echo "    ✗ 失败"
            rm -f "$output_file"
        fi
        
        sleep 1
        count=$((count + 1))
        if [ $count -ge 6 ]; then
            break
        fi
    done
    
    echo "  完成 $count 个视频"
    sleep 2
done

echo ""
echo "========== 统计 =========="
find "$OUTPUT_DIR" -name "*.txt" -type f | wc -l
echo "字幕文件总数"
ls -la "$OUTPUT_DIR"/
