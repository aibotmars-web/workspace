#!/usr/bin/env python3
"""
語音轉文字工具
使用 OpenAI Whisper 本地轉錄
"""

import subprocess
import sys

def transcribe(audio_path, model="medium", output_format="txt"):
    """轉錄音頻檔案"""
    cmd = [
        "whisper",
        audio_path,
        "--model", model,
        "--output_format", output_format,
        "--output_dir", "/Users/marsbot/.openclaw/workspace/transcripts"
    ]
    
    print(f"🚀 開始轉錄: {audio_path}")
    print(f"📊 使用模型: {model}")
    
    subprocess.run(cmd)
    
    # 讀取結果
    txt_path = audio_path.replace(".ogg", ".txt").replace(".m4a", ".txt")
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
            print(f"\n✅ 轉錄完成！")
            print(f"📝 內容：")
            print(text)
            return text
    except:
        print(f"❌ 無法讀取轉錄結果")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        transcribe(audio_file)
    else:
        print("使用方法: python3 transcribe.py <音頻檔案>")
        print("範例: python3 transcribe.py audio.ogg")
