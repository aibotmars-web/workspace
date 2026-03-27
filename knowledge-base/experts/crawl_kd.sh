#!/bin/bash
# 用 kd 全面爬取知識庫

CHANNELS=(
  "Dr.Hu_talk:https://www.youtube.com/@Dr.Hu_talk/videos"
  "Dr.HuangAmin:https://www.youtube.com/@Dr.HuangAmin/videos"
  "muerstalk:https://www.youtube.com/@muerstalk/videos"
  "SongMing:https://www.youtube.com/@SongMing/videos"
  "DrHarveyTalk:https://www.youtube.com/@DrHarveyTalk/videos"
  "Cofit211:https://www.youtube.com/@Cofit211/videos"
  "PanScitw:https://www.youtube.com/@PanScitw/videos"
  "panscischool:https://www.youtube.com/@panscischool/videos"
)

LOG_FILE="kd-crawl-$(date +%Y-%m-%d).log"

echo "=== 開始全面爬取 $(date) ===" | tee -a "$LOG_FILE"

for ch in "${CHANNELS[@]}"; do
  IFS=':' read -r name url <<< "$ch"
  echo "" | tee -a "$LOG_FILE"
  echo "=== 抓取 $name ===" | tee -a "$LOG_FILE"
  
  # 獲取最新3個影片
  videos=$(yt-dlp "$url" --playlist-end 3 --print "%(id)s" 2>/dev/null)
  
  for vid in $videos; do
    echo "  - $vid" | tee -a "$LOG_FILE"
    cd "$name"
    kd transcribe "https://www.youtube.com/watch?v=$vid" --backend mlx-whisper --output "${vid}.md" 2>&1 | tail -3
    cd ..
    sleep 5
  done
  
  sleep 10
done

echo "=== 爬取完成 $(date) ===" | tee -a "$LOG_FILE"
