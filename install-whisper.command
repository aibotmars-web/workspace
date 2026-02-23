#!/bin/bash
echo "🚀 Whisper 語音轉文字安裝程式"
echo "=================================="

# 檢查是否已安裝
if command -v whisper &> /dev/null; then
    echo "✅ Whisper 已安裝"
    whisper --version
else
    echo "📦 安裝 Whisper..."
    brew install openai-whisper
    echo "✅ Whisper 安裝完成"
fi

echo ""
echo "=================================="
echo "✨ 安裝完成！"
echo ""
echo "使用方法："
echo "whisper <檔案路徑> --model medium --output_format txt"
echo ""
echo "範例："
echo "whisper /Users/marsbot/.openclaw/media/inbound/file_10---e0f69c5b-56c4-40d6-b24d-8ccf1d82ca0a.ogg --model medium --output_format txt"
echo ""
read -p "按 Enter 關閉..."
