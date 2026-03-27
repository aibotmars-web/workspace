#!/bin/bash
# 每日 YouTube 專家知識庫爬蟲 - 增加數量版
# 爬取每個頻道最新 20 部影片的字幕

BASE_DIR="/Users/marsbot/.openclaw/workspace/knowledge-base"
EXPERT_DIR="$BASE_DIR/experts"
LOG_FILE="$BASE_DIR/crawler-full.log"

# 專家頻道列表
CHANNELS=(
  "Dr.HuangAmin|阿銘師x針還傳"
  "Dr.Hu_talk|胡乃文開示"
  "drbergchinese|柏格醫生中文"
  "muerstalk|周慕姿放心說"
  "SongMing|松明講心理"
  "DrHarveyTalk|Dr.Harvey不廢話"
  "Cofit211|初日醫學"
  "PanScitw|泛科學"
  "panscischool|泛科學院"
)

MAX_VIDEOS=50  # 增加到50部

echo "============================================================" | tee -a $LOG_FILE
echo "YouTube 專家知識庫爬蟲 (多量版) $(date '+%Y-%m-%d %H:%M:%S')" | tee -a $LOG_FILE
echo "每頻道抓取: $MAX_VIDEOS 部" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE

# 確保專家目錄存在
mkdir -p "$EXPERT_DIR"

TOTAL_SUBTITLES=0

for ch in "${CHANNELS[@]}"; do
  CHANNEL_ID="${ch%%|*}"
  CHANNEL_NAME="${ch##*|}"
  
  echo "" | tee -a $LOG_FILE
  echo "[$CHANNEL_NAME] 抓取中..." | tee -a $LOG_FILE
  
  # 建立專家目錄
  EXPERT_SUB_DIR="$EXPERT_DIR/$CHANNEL_ID"
  mkdir -p "$EXPERT_SUB_DIR"
  
  cd "$EXPERT_SUB_DIR"
  
  # 抓取最新 $MAX_VIDEOS 部影片
  yt-dlp --flat-playlist --print "%(title)s|%(id)s" \
    "https://www.youtube.com/@${CHANNEL_ID}/videos" 2>/dev/null | head -$MAX_VIDEOS | while read line; do
    
    VIDEO_TITLE="${line%%|*}"
    VIDEO_ID="${line##*|}"
    
    # 如果字幕檔案不存在，才抓取
    if [ ! -f "${VIDEO_ID}.zh-TW.vtt" ] && [ ! -f "${VIDEO_ID}.en.vtt" ]; then
      echo "  → 抓取: ${VIDEO_TITLE:0:50}..."
      yt-dlp --skip-download --write-subs --write-auto-subs --sub-lang zh-TW,zh-CN,en \
        -o "%(id)s" "https://www.youtube.com/watch?v=${VIDEO_ID}" 2>> $LOG_FILE
      
      # 計算有抓到字幕的數量
      if [ -f "${VIDEO_ID}.zh-TW.vtt" ] || [ -f "${VIDEO_ID}.en.vtt" ]; then
        TOTAL_SUBTITLES=$((TOTAL_SUBTITLES + 1))
      fi
    else
      echo "  ✓ 已存在: ${VIDEO_TITLE:0:50}..."
    fi
  done
  
  CHANNEL_COUNT=$(ls -1 *.vtt 2>/dev/null | wc -l | tr -d ' ')
  echo "[$CHANNEL_NAME] 完成 (共 $CHANNEL_COUNT 個字幕)" | tee -a $LOG_FILE
done

echo "" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE
echo "爬蟲完成 $(date '+%Y-%m-%d %H:%M:%S')" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE
