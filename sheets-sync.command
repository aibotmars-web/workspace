#!/bin/bash
echo "🚀 Google Sheets 同步工具"
echo "========================"

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python3"
    exit 1
fi

# 安裝 gspread
echo "📦 安裝 gspread..."
pip3 install gspread

# 執行同步
echo "🔄 執行同步..."
cd "$(dirname "$0")"
python3 sheets-sync.py

echo ""
echo "========================"
echo "✨ 完成！"
read -p "按 Enter 關閉..."
