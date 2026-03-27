#!/bin/bash
# 快速頻道狀態顯示（使用已知的頻道數據）
# 由 cron 每天更新一次總數

WORKSPACE="$HOME/.openclaw/workspace/knowledge-base"
STATS_FILE="$WORKSPACE/channel_stats.json"
OUTPUT_DIR="$WORKSPACE/experts/transcripts"

# 讀取統計
get_stat() {
    local channel=$1
    local key=$2
    grep -o "\"$channel\"[^}]*\"$key\"[^,]*" "$STATS_FILE" 2>/dev/null | grep -o '[0-9]\+' | head -1
}

echo "======================================================================"
echo "📊 專家頻道爬蟲狀態"
echo "======================================================================"
echo "時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 從目錄統計已抓取
echo "頻道                   總計    已抓    鎖定    待抓    進度"
echo "----------------------------------------------------------------------"

total_all=0
crawled_all=0
locked_all=0

for dir in "$OUTPUT_DIR"/*/; do
    [ -d "$dir" ] || continue
    channel=$(basename "$dir")
    
    # 統計已抓取
    crawled=$(find "$dir" -name "*.txt" -type f -size +100c 2>/dev/null | wc -l | tr -d ' ')
    
    # 嘗試從 stats json 讀取總數
    if [ -f "$STATS_FILE" ]; then
        total=$(python3 -c "import json; d=json.load(open('$STATS_FILE')); print(d.get('$channel',{}).get('total',0))" 2>/dev/null)
        locked=$(python3 -c "import json; d=json.load(open('$STATS_FILE')); print(len(d.get('$channel',{}).get('locked',[])))" 2>/dev/null)
    else
        total=0
        locked=0
    fi
    
    # 如果沒有總數，顯示 ?
    if [ "$total" = "0" ] || [ -z "$total" ]; then
        total_str="?"
        progress="-"
        remaining="?"
    else
        total_str=$total
        remaining=$((total - crawled - locked))
        if [ $remaining -lt 0 ]; then remaining=0; fi
        progress=$(python3 -c "print(f'{$crawled/$total*100:.1f}%')" 2>/dev/null || echo "-")
    fi
    
    printf "%-20s %-8s %-8s %-8s %-8s %-10s\n" "$channel" "$total_str" "$crawled" "$locked" "$remaining" "$progress"
    
    total_all=$((total_all + ${total:-0}))
    crawled_all=$((crawled_all + crawled))
    locked_all=$((locked_all + locked))
done

echo "----------------------------------------------------------------------"
remaining_all=$((total_all - crawled_all - locked_all))
if [ $remaining_all -lt 0 ]; then remaining_all=0; fi
overall=$(python3 -c "print(f'{$crawled_all/$total_all*100:.1f}%')" 2>/dev/null || echo "-")
printf "%-20s %-8s %-8s %-8s %-8s %-10s\n" "總計" "$total_all" "$crawled_all" "$locked_all" "$remaining_all" "$overall"
echo "======================================================================"
echo ""
echo "💡 提示: 用 --refresh 更新頻道總數"
