#!/bin/bash
echo "🚀 YouTube 知識庫同步（字幕 + AI 摘要）"
echo "=================================="

cd "$(dirname "$0")"

# 檢查依賴
echo "📦 檢查依賴..."
python3 -c "import youtube_transcript_api" 2>/dev/null || pip3 install youtube-transcript-api
python3 -c "import yt_dlp" 2>/dev/null || pip3 install yt-dlp

# 執行同步
echo "🔄 執行同步..."
python3 knowledge-base/sync-with-summaries.py

echo ""
echo "=================================="
echo "✨ 完成！"
read -p "按 Enter 關閉..."
