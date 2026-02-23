#!/bin/bash
echo "🚀 OpenClaw 每日監控系統"
echo "=================================="

cd "$(dirname "$0")"

# 檢查依賴
echo "📦 檢查依賴..."
python3 -c "import gspread" 2>/dev/null || pip3 install gspread

# 執行監控
echo "🔄 執行監控..."
python3 openclaw-monitor.py

echo ""
echo "=================================="
echo "✨ 完成！"
echo ""
echo "此腳本會檢查："
echo "  - GitHub Releases (更新版本)"
echo "  - GitHub Issues (新問題)"
echo "  - Security Advisories (安全漏洞)"
echo "  - ClawHub (新 Skills)"
echo ""
read -p "按 Enter 關閉..."
