#!/usr/bin/env python3
"""
查詢 YouTube 頻道影片數量
使用 yt-dlp --dump-json
"""

import subprocess
import json

channels = {
    "Dr.HuangAmin": "https://www.youtube.com/@Dr.HuangAmin",
    "Dr.Hu_talk": "https://www.youtube.com/@Dr.Hu_talk",
    "drbergchinese": "https://www.youtube.com/@drbergchinese",
    "muerstalk": "https://www.youtube.com/@muerstalk",
    "SongMing": "https://www.youtube.com/@SongMing",
    "DrHarveyTalk": "https://www.youtube.com/@DrHarveyTalk",
    "Cofit211": "https://www.youtube.com/@Cofit211",
    "PanScitw": "https://www.youtube.com/@PanScitw",
    "panscischool": "https://www.youtube.com/@panscischool"
}

def get_video_count(url):
    """使用 yt-dlp 取得頻道資訊"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--playlist-items", "1-1", url],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            return data.get('channel_count', 'N/A')
    except Exception as e:
        print(f"Error: {e}")
    return "Error"

print("查詢中...")
for name, url in channels.items():
    count = get_video_count(url)
    print(f"{name}: {count}")
