#!/bin/bash
# 完整知识库工作流：爬取 → 蒸馏 → 存入知识库
# 1. 爬取 YouTube 字幕
# 2. 用 kd 转换为结构化知识
# 3. 加入 QMD 向量知识库

BASE_DIR="/Users/marsbot/.openclaw/workspace/knowledge-base"
EXPERT_DIR="$BASE_DIR/experts"
LOG_FILE="$BASE_DIR/kd-workflow.log"

echo "=== 知识库工作流 $(date '+%Y-%m-%d %H:%M:%S') ===" | tee -a $LOG_FILE

# 频道列表
CHANNELS=(
  "Dr.Hu_talk:胡乃文開示"
  "drbergchinese:柏格醫生中文"
  "muerstalk:周慕姿放心說"
  "Cofit211:初日醫學"
  "panscischool:泛科學院"
)

# Step 1: 爬取字幕 (跳过已存在的)
echo "[1/3] 爬取字幕..." | tee -a $LOG_FILE
/Users/marsbot/.openclaw/workspace/knowledge-base/crawl-daily.sh >> $LOG_FILE 2>&1

# Step 2: VTT 转文字 + kd 处理
echo "[2/3] 转换字幕..." | tee -a $LOG_FILE

for ch in "${CHANNELS[@]}"; do
  ch_id="${ch%%:*}"
  ch_name="${ch##*:}"
  
  expert_dir="$EXPERT_DIR/$ch_id"
  if [ ! -d "$expert_dir" ]; then
    continue
  fi
  
  # 找最新未处理的影片
  for vtt in $(ls -t "$expert_dir"/*.vtt 2>/dev/null | head -5); do
    video_id=$(basename "$vtt" | sed 's/\..*//')
    md_file="$expert_dir/${video_id}.md"
    
    # 如果还没转换过
    if [ ! -f "$md_file" ]; then
      echo "  → 处理: $video_id" | tee -a $LOG_FILE
      
      # 用 kd 提取字幕
      kd subtitles "https://www.youtube.com/watch?v=$video_id" \
        --output "$md_file" 2>> $LOG_FILE
      
      # 如果 kd 失败，用简单转换
      if [ $? -ne 0 ] || [ ! -f "$md_file" ]; then
        python3 -c "
import re
try:
  with open('$vtt', 'r') as f:
    content = f.read()
  lines = [re.sub(r'<[^>]+>', '', l).strip() 
           for l in content.split('\n') 
           if '-->' not in l and l.strip() and 'WEBVTT' not in l]
  text = ' '.join(lines)
  with open('$md_file', 'w') as f:
    f.write('# $video_id\n\n')
    f.write(text)
except: pass
"
      fi
    fi
  done
done

# Step 3: 更新 QMD 知识库
echo "[3/3] 更新 QMD..." | tee -a $LOG_FILE
qmd collection remove youtube-experts 2>/dev/null
qmd collection add "$EXPERT_DIR" --name "youtube-experts" 2>&1 | tee -a $LOG_FILE
qmd embed 2>&1 | tee -a $LOG_FILE

echo "=== 完成! ===" | tee -a $LOG_FILE
qmd status | tee -a $LOG_FILE
