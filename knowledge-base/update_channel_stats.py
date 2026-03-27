#!/usr/bin/env python3
"""
用瀏覽器自動更新頻道總影片數
"""

import subprocess
import re
import time
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
STATS_FILE = WORKSPACE / "channel_stats.json"

CHANNELS = {
    "Dr.Hu_talk": "https://www.youtube.com/@Dr.Hu_talk/videos",
    "drbergchinese": "https://www.youtube.com/@drbergchinese/videos",
    "muerstalk": "https://www.youtube.com/@muerstalk/videos",
    "panscischool": "https://www.youtube.com/@panscischool/videos",
    "Cofit211": "https://www.youtube.com/@Cofit211/videos",
    "PanScitw": "https://www.youtube.com/@PanScitw/videos",
    "Dr.HuangAmin": "https://www.youtube.com/@Dr.HuangAmin/videos",
    "DrHarveyTalk": "https://www.youtube.com/@DrHarveyTalk/videos",
    "SongMing": "https://www.youtube.com/@SongMing/videos",
}


def run_browser(cmd):
    """執行瀏覽器命令"""
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result.stdout + result.stderr


def get_video_count(channel_url):
    """用瀏覽器抓取頻道總影片數"""
    # 打開頻道頁面
    run_browser(["agent-browser", "open", channel_url, "--timeout", "30000"])
    time.sleep(3)  # 等頁面載入
    
    # 截圖取得文字
    output = run_browser(["agent-browser", "snapshot", "-c", "--timeout", "15000"])
    
    # 解析 "XXX 部影片" 或 "X videos"
    patterns = [
        r'(\d[\d,]*(?:\.\d+)?[萬千]?)\s*部\s*影片',
        r'(\d[\d,]*(?:\.\d+)?[萬千]?)\s*videos',
        r'(\d[\d,]+)\s*videos',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            text = match.group(1)
            # 轉換萬->10000
            if '萬' in text:
                return int(float(text.replace('萬', '')) * 10000)
            elif '千' in text:
                return int(float(text.replace('千', '')) * 1000)
            else:
                return int(text.replace(',', ''))
    
    # 如果沒找到，回傳 0
    return 0


def main():
    print(f"{'='*60}")
    print(f"🔄 更新頻道總影片數")
    print(f"{'='*60}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 載入現有 stats
    if STATS_FILE.exists():
        with open(STATS_FILE) as f:
            stats = json.load(f)
    else:
        stats = {"channels": {}}
    
    for channel, url in CHANNELS.items():
        print(f"📺 {channel}...", end=" ", flush=True)
        
        try:
            total = get_video_count(url)
            if total > 0:
                if channel not in stats["channels"]:
                    stats["channels"][channel] = {}
                stats["channels"][channel]["total"] = total
                stats["channels"][channel]["last_checked"] = datetime.now().strftime("%Y-%m-%d")
                print(f"{total} 部")
            else:
                print("無法取得")
        except Exception as e:
            print(f"錯誤: {e}")
        
        time.sleep(2)  # 避免太頻繁
    
    # 關閉瀏覽器
    run_browser(["agent-browser", "close"])
    
    # 儲存
    stats["last_updated"] = datetime.now().isoformat()
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"✅ 已更新 {STATS_FILE}")


if __name__ == "__main__":
    main()
