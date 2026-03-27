#!/usr/bin/env python3
"""
快速爬蟲腳本 - 每次只抓一個頻道
"""

import subprocess
import time
import random
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
STATS_FILE = WORKSPACE / "channel_stats.json"
EXPERTS_DIR = WORKSPACE / "experts"

# 頻道列表（按進度排序：從最低的開始）
CHANNELS = [
    "SongMing",           # 0.1%
    "PanScitw",           # 0.7%
    "DrHarveyTalk",       # 3.3%
    "Cofit211",           # 4.3%
    "Dr.Hu_talk",         # 5.4%
    "drbergchinese",      # 1.6%
    "muerstalk",          # 12.7%
    "panscischool",       # 11.9%
    "Dr.HuangAmin",       # 1.8%
]


def get_unique_videos(dir_name):
    """取得已抓取的 unique video IDs"""
    channel_dir = EXPERTS_DIR / dir_name
    if not channel_dir.exists():
        return set()
    
    video_ids = set()
    for f in channel_dir.iterdir():
        if f.is_file() and f.suffix in ['.txt', '.md', '.vtt']:
            name = f.stem
            # 去掉語言後綴
            if '.en' in name:
                name = name.replace('.en', '')
            elif '.zh-TW' in name:
                name = name.replace('.zh-TW', '')
            video_ids.add(name)
    return video_ids


def get_channel_videos(channel_url, limit=50):
    """獲取頻道影片列表"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--get-id", "--playlist-end", str(limit), channel_url],
            capture_output=True,
            text=True,
            timeout=30,
        )
        videos = [v.strip() for v in result.stdout.strip().split("\n") if v.strip()]
        return videos
    except:
        return []


def crawl_channel(channel_name, limit=10):
    """爬取一個頻道的最新影片"""
    channel_dir = EXPERTS_DIR / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    
    # 從 stats 讀取 URL
    stats = json.load(open(STATS_FILE)) if STATS_FILE.exists() else {"channels": {}}
    ch_info = stats.get("channels", {}).get(channel_name, {})
    channel_url = ch_info.get("url", f"https://www.youtube.com/@{channel_name}/videos")
    
    # 取得已抓取的
    crawled = get_unique_videos(channel_name)
    
    # 取得頻道影片
    videos = get_channel_videos(channel_url, limit=limit)
    
    success = 0
    failed = 0
    skipped = 0
    
    for vid in videos:
        if vid in crawled:
            skipped += 1
            continue
        
        output_file = channel_dir / f"{vid}.txt"
        
        # 隨機延遲
        time.sleep(random.uniform(2, 5))
        
        # 用 kd subtitles
        try:
            result = subprocess.run(
                ["kd", "subtitles", f"https://www.youtube.com/watch?v={vid}", "-o", str(output_file)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0 and output_file.exists():
                success += 1
            else:
                failed += 1
        except:
            failed += 1
    
    return {"success": success, "failed": failed, "skipped": skipped}


def main():
    print(f"🚀 開始爬蟲 - {datetime.now().strftime('%H:%M:%S')}")
    
    # 讀取上次執行的頻道
    state_file = WORKSPACE / "crawl_state.json"
    if state_file.exists():
        state = json.load(open(state_file))
        last_index = state.get("last_channel_index", 0)
    else:
        last_index = 0
    
    # 選擇下一個頻道（循環）
    channel = CHANNELS[last_index % len(CHANNELS)]
    print(f"📺 爬取頻道: {channel}")
    
    # 執行爬蟲（每次只抓 10 個）
    result = crawl_channel(channel, limit=10)
    
    print(f"✅ 成功: {result['success']}, ❌ 失敗: {result['failed']}, ⏭️ 跳過: {result['skipped']}")
    
    # 更新狀態
    next_index = (last_index + 1) % len(CHANNELS)
    state = {
        "last_channel_index": next_index,
        "last_run": datetime.now().isoformat(),
        "last_channel": channel,
        "last_result": result,
    }
    json.dump(state, open(state_file, "w"))
    
    print(f"⏰ 下次將爬取: {CHANNELS[next_index]}")
    print(f"✅ 完成 - {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
