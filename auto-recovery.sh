#!/bin/bash
# auto-recovery.sh - 自動恢復腳本
# 用途：檢測 exec 錯誤，保存對話，協助恢復

RECOVERY_FILE="/Users/marsbot/.openclaw/workspace/memory/$(date +%Y-%m-%d)-recovery.md"
SESSION_FILE="/Users/marsbot/.openclaw/workspace/transcripts/latest.jsonl"

# 檢查是否有 exec EAGAIN 錯誤
check_exec_status() {
    if [ -f /tmp/exec_error ]; then
        cat /tmp/exec_error
        return 1
    fi
    return 0
}

# 保存當前對話狀態
save_recovery_state() {
    echo "# 恢復點 - $(date '+%Y-%m-%d %H:%M:%S')" > "$RECOVERY_FILE"
    echo "" >> "$RECOVERY_FILE"
    echo "## 最後任務" >> "$RECOVERY_FILE"
    echo "- truthnet repo 已創建: https://github.com/realtaiwan/truthnet" >> "$RECOVERY_FILE"
    echo "- 下一步: clone 並 push 程式碼" >> "$RECOVERY_FILE"
    echo "" >> "$RECOVERY_FILE"
    echo "## 執行中的命令" >> "$RECOVERY_FILE"
    echo "待恢復: git clone && push truthnet" >> "$RECOVERY_FILE"
    echo "" >> "$RECOVERY_FILE"
    echo "## MEMORY.md 狀態" >> "$RECOVERY_FILE"
    echo "✅ 長期記憶完整" >> "$RECOVERY_FILE"
    echo "✅ GitHub PAT: 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" >> "$RECOVERY_FILE"
    echo "✅ 10 個弊案資料已記錄" >> "$RECOVERY_FILE"
    echo "## 待辦" >> "$RECOVERY_FILE"
    echo "1. clone https://github.com/realtaiwan/truthnet" >> "$RECOVERY_FILE"
    echo "2. 創建 truthnet 程式碼結構" >> "$RECOVERY_FILE"
    echo "3. git add . && git commit -m 'Initial truthnet structure'" >> "$RECOVERY_FILE"
    echo "4. git push" >> "$RECOVERY_FILE"
    echo "" >> "$RECOVERY_FILE"
    echo "---" >> "$RECOVERY_FILE"
    echo "*恢復時間: $(date '+%Y-%m-%d %H:%M:%S')*" >> "$RECOVERY_FILE"
    echo "✅ 已保存"
}

# 主程式
main() {
    echo "🔍 檢查 exec 狀態..."
    
    if check_exec_status; then
        echo "✅ Exec 正常"
        exit 0
    else
        echo "⚠️ 檢測到錯誤，執行恢復..."
        save_recovery_state
        echo ""
        echo "========================================"
        echo "📋 恢復步驟："
        echo "1. 執行 /new 重新開始對話"
        echo "2. 告訴小助理：'truthnet 恢復'"
        echo "3. 小助理會讀取 $RECOVERY_FILE"
        echo "========================================"
        exit 1
    fi
}

main "$@"
