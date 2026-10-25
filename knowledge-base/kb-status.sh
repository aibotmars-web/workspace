#!/bin/bash
# 知識庫狀態儀表板 v2
# 使用統一的 kb-state-manager.py 讀取進度
# 用法: bash kb-status.sh

WORKSPACE="$HOME/.openclaw/workspace/knowledge-base"
STATE_MGR="$WORKSPACE/kb-state-manager.py"
STATE_FILE="$WORKSPACE/kb-unified-state.json"
PROGRESS_CSV="$WORKSPACE/kb-progress.csv"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       🧠 知識庫爬蟲進度儀表板 $(date '+%Y-%m-%d %H:%M')        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 檢查必要檔案
if [ ! -f "$STATE_MGR" ]; then
    echo "❌ 錯誤: $STATE_MGR 不存在"
    exit 1
fi

if [ ! -f "$STATE_FILE" ]; then
    echo "❌ 錯誤: $STATE_FILE 不存在"
    exit 1
fi

# 同步實際檔案數量（從專家目錄）
python3 "$STATE_MGR" sync 2>/dev/null

# 顯示進度
python3 "$STATE_MGR" read

# 檢查問題
echo "━━━ 問題檢查 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 "$STATE_MGR" check | grep -E "⚠️|📍"

echo ""
echo "━━━ 統一檔案路徑 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 統一狀態檔: $STATE_FILE"
echo "📊 進度報告: $PROGRESS_CSV"
echo ""
echo "💡 所有 sub-agent 必須使用 kb-state-manager.py 讀寫進度"