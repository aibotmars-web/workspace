#!/bin/bash
# 知識庫爬蟲 wrapper - 確保爬完後同步到統一狀態
# 用法: bash kb-crawl-wrapper.sh

WORKSPACE="$HOME/.openclaw/workspace/knowledge-base"
STATE_MGR="$WORKSPACE/kb-state-manager.py"
LOG_FILE="$WORKSPACE/kb-crawl.log"

echo "━━━ 知識庫爬蟲 $(date '+%Y-%m-%d %H:%M:%S') ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# 知識庫爬蟲時間預算：避開 OpenClaw health-monitor 15 分鐘 gateway 重啟週期
# （如需完整跑請手動執行此 wrapper，環境變數會被忽略）
export KB_TIME_BUDGET_MIN=${KB_TIME_BUDGET_MIN:-60}

# Step 1: 執行爬蟲
echo "🚀 執行爬蟲..."
cd "$WORKSPACE"
python3 crawl_stable.py >> "$LOG_FILE" 2>&1
CRAWL_EXIT=$?

echo "✅ 爬蟲完成 (exit: $CRAWL_EXIT)"

# Step 2: 同步到統一狀態
echo "🔄 同步到統一狀態..."
python3 "$STATE_MGR" sync >> "$LOG_FILE" 2>&1

# Step 2b: 從活的 crawl_state.json 補齊（修正 kb-unified-state.json 自 5 月起的殭屍狀態）
echo "🔄 從 crawl_state.json 補齊（即時資料）..."
python3 "$STATE_MGR" sync_from_crawl >> "$LOG_FILE" 2>&1

# Step 3: 生成進度報告
echo "📊 生成進度報告..."
python3 "$STATE_MGR" report >> "$LOG_FILE" 2>&1

# Step 4: 顯示摘要
echo ""
echo "━━━ 爬蟲後進度 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 "$STATE_MGR" read

echo ""
echo "✅ 完成！進度已同步到 kb-unified-state.json"
echo "📝 日誌: $LOG_FILE"