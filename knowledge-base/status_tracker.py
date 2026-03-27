#!/usr/bin/env python3
"""
專家頻道爬蟲狀態追蹤系統
- 即時取得頻道總影片數
- 追蹤已抓取 / 待抓取 / 鎖定影片
- 避免重複抓取
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
STATS_FILE = WORKSPACE / "channel_stats.json"
OUTPUT_DIR = WORKSPACE / "experts" / "transcripts"

# 頻道設定
CHANNELS = {
    "Dr.Hu_talk": "UCvVY1c7-r8G0eL6K",
    "drbergchinese": "UCg1m-GdGC",
    "Dr.HuangAmin": "UCwSZ",
    "muerstalk": "UCl",
    "SongMiming": "UCX",
    "Cofit211": "UCx",
    "PanScitw": "UC2",
    "panscischool": "UC3",
    "DrHarveyTalk": "UCx",
}

# 頻道名稱與 URL 對照
CHANNEL_URLS = {
    "Dr.Hu_talk": "https://www.youtube.com/@Dr.Hu_talk",
    "drbergchinese": "https://www.youtube.com/@drbergchinese",
    "Dr.HuangAmin": "https://www.youtube.com/@Dr.HuangAmin",
    "muerstalk": "https://www.youtube.com/@muerstalk",
    "SongMing": "https://www.youtube.com/@SongMing",
    "Cofit211": "https://www.youtube.com/@Cofit211",
    "PanScitw": "https://www.youtube.com/@PanScitw",
    "panscischool": "https://www.youtube.com/@panscischool",
    "DrHarveyTalk": "https://www.youtube.com/@DrHarveyTalk",
}


def get_channel_total(channel_url):
    """用 yt-dlp 獲取頻道總影片數（只取 ID 不下載）"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--get-id", "--playlist-end", "500", channel_url],
            capture_output=True,
            text=True,
            timeout=60,
        )
        videos = [v.strip() for v in result.stdout.strip().split("\n") if v.strip()]
        return len(videos), videos
    except Exception as e:
        print(f"    ⚠ 無法獲取總數: {e}")
        return 0, []


def get_crawled_videos(channel_name):
    """取得已抓取的影片 ID 列表"""
    channel_dir = OUTPUT_DIR / channel_name
    if not channel_dir.exists():
        return set()
    
    crawled = set()
    for f in channel_dir.glob("*.txt"):
        if f.stat().st_size > 100:
            # 從檔名取得 video ID
            crawled.add(f.stem)
    return crawled


def load_stats():
    """載入現有統計"""
    if STATS_FILE.exists():
        with open(STATS_FILE) as f:
            return json.load(f)
    return {}


def save_stats(stats):
    """儲存統計"""
    stats["last_updated"] = datetime.now().isoformat()
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def main(refresh=False):
    print(f"{'='*70}")
    print(f"📊 專家頻道爬蟲狀態追蹤")
    print(f"{'='*70}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    stats = load_stats()
    
    # 讀取頻道目錄
    if OUTPUT_DIR.exists():
        existing_dirs = {d.name for d in OUTPUT_DIR.iterdir() if d.is_dir()}
    else:
        existing_dirs = set()
    
    all_channels = set(CHANNEL_URLS.keys()) | existing_dirs
    
    print(f"{'頻道':<20} {'總計':<8} {'已抓':<8} {'鎖定':<8} {'待抓':<8} {'進度':<10}")
    print("-" * 70)
    
    total_all = 0
    crawled_all = 0
    locked_all = 0
    
    for channel_name in sorted(all_channels):
        # 取得頻道 URL
        channel_url = CHANNEL_URLS.get(channel_name)
        if not channel_url:
            # 從專家目錄猜測 URL
            channel_url = f"https://www.youtube.com/@{channel_name}"
        
        # 取得已抓取影片
        crawled_videos = get_crawled_videos(channel_name)
        crawled_count = len(crawled_videos)
        
        # 檢查是否需要刷新總數
        need_refresh = refresh or channel_name not in stats
        
        if need_refresh and channel_url:
            print(f"{channel_name:<20} ", end="", flush=True)
            # 從已抓取的推斷總數（如果頻道還沒抓完）
            total, all_videos = get_channel_total(channel_url)
            
            # 對比已抓取，找出鎖定的影片
            locked = set()
            for vid in all_videos:
                if vid not in crawled_videos:
                    # 檢查是否真的存在（可能被鎖）
                    # 這裡我們標記為"待抓"
                    pass
            
            # 從 stats 讀取鎖定列表
            locked_list = stats.get(channel_name, {}).get("locked", [])
            locked = set(locked_list)
            
            stats[channel_name] = {
                "total": total,
                "crawled": list(crawled_videos),
                "locked": locked_list,
                "last_checked": datetime.now().isoformat(),
            }
            
            print(f"\r{channel_name:<20} {total:<8} {crawled_count:<8} {len(locked):<8}", end="")
        else:
            # 使用現有統計
            channel_stats = stats.get(channel_name, {})
            total = channel_stats.get("total", 0)
            locked_list = channel_stats.get("locked", [])
            
            print(f"{channel_name:<20} {total:<8} {crawled_count:<8} {len(locked_list):<8}", end="")
        
        # 計算待抓
        remaining = max(0, stats.get(channel_name, {}).get("total", 0) - crawled_count - len(stats.get(channel_name, {}).get("locked", [])))
        progress = f"{crawled_count/max(total,1)*100:.1f}%"
        
        print(f" {remaining:<8} {progress:<10}")
        
        total_all += stats.get(channel_name, {}).get("total", 0)
        crawled_all += crawled_count
        locked_all += len(stats.get(channel_name, {}).get("locked", []))
    
    print("-" * 70)
    overall = f"{crawled_all/max(total_all,1)*100:.1f}%"
    print(f"{'總計':<20} {total_all:<8} {crawled_all:<8} {locked_all:<8} {max(0,total_all-crawled_all-locked_all):<8} {overall:<10}")
    print(f"{'='*70}")
    
    # 儲存更新後的統計
    save_stats(stats)
    print(f"✅ 狀態已更新: {STATS_FILE}")


if __name__ == "__main__":
    import sys
    refresh = "--refresh" in sys.argv or "-r" in sys.argv
    main(refresh=refresh)
