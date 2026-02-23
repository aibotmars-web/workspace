#!/bin/bash
echo "🚀 開始安裝與同步..."

# 切換到正確目錄
cd "$(dirname "$0")"

# 安裝依賴
echo "📦 安裝 google-api-python-client..."
pip3 install google-api-python-client

# 執行同步
echo "🔄 執行知識庫同步..."
python3 sync_with_api.py

echo "✅ 完成！按 Enter 關閉..."
read
