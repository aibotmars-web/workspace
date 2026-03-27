#!/usr/bin/env python3
"""
專家頻道爬蟲狀態顯示 v3
計算每個頻道的 unique video ID（避免重複計算）
"""

import json
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
STATS_FILE = WORKSPACE / "channel_stats.json"
EXPERTS_DIR = WORKSPACE / "experts"

# 頻道對照表（stats.json key -> 實際目錄名稱）
CHANNEL_MAP = {
    "Dr.Hu_talk": "Dr.Hu_talk",
    "drbergchinese": "drbergchinese",
    "muerstalk": "muerstalk",
    "panscischool": "panscischool",
    "Cofit211": "Cofit211",
    "PanScitw": "PanScitw",
    "Dr.HuangAmin": "Dr.HuangAmin",
    "DrHarveyTalk": "DrHarveyTalk",
    "SongMing": "SongMing",
}


def get_unique_videos(dir_name):
    """取得頻道的 unique video ID 數量"""
    channel_dir = EXPERTS_DIR / dir_name
    if not channel_dir.exists():
        return 0
    
    video_ids = set()
    for f in channel_dir.iterdir():
        if f.is_file():
            # 檔名格式: VIDEO_ID.ext 或 VIDEO_ID.lang.ext
            # 例如: 4Dz5AvemNQ8.en.vtt, BjLItKMNh_w.zh-TW.md
            name = f.stem  # 去掉附檔名
            # 去掉語言後綴 (.en, .zh-TW 等)
            match = re.match(r'^([a-zA-Z0-9_-]+)', name)
            if match:
                video_ids.add(match.group(1))
    
    return len(video_ids)


def get_crawled_videos(dir_name):
    """取得已抓取的影片 ID 集合"""
    channel_dir = EXPERTS_DIR / dir_name
    if not channel_dir.exists():
        return set()
    
    video_ids = set()
    for f in channel_dir.iterdir():
        if f.is_file():
            name = f.stem
            match = re.match(r'^([a-zA-Z0-9_-]+)', name)
            if match:
                video_ids.add(match.group(1))
    
    return video_ids


def load_stats():
    """載入 channel_stats.json"""
    if STATS_FILE.exists():
        with open(STATS_FILE) as f:
            return json.load(f)
    return {"channels": {}}


def main():
    print(f"{'='*72}")
    print(f"📊 專家頻道爬蟲狀態追蹤")
    print(f"{'='*72}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    stats = load_stats()
    channels = stats.get("channels", {})
    
    # 表頭
    print(f"{'頻道':<18} {'顯示名稱':<14} {'總計':<8} {'已抓':<8} {'鎖定':<8} {'待抓':<8} {'進度':<10}")
    print("-" * 80)
    
    total_all = 0
    crawled_all = 0
    locked_all = 0
    
    for stats_key, dir_name in CHANNEL_MAP.items():
        ch_stats = channels.get(stats_key, {})
        
        # 從 stats 讀取
        total = ch_stats.get("total", 0)
        display_name = ch_stats.get("display_name", dir_name)
        locked_list = ch_stats.get("locked", [])
        locked = len(locked_list) if locked_list else 0
        
        # 從實際目錄統計已抓取（unique videos）
        crawled = get_unique_videos(dir_name)
        
        # 計算待抓
        remaining = max(0, total - crawled - locked)
        
        # 計算進度
        if total > 0:
            progress = f"{crawled/total*100:.1f}%"
        else:
            progress = "-"
        
        print(f"{dir_name:<18} {display_name:<14} {total:<8} {crawled:<8} {locked:<8} {remaining:<8} {progress:<10}")
        
        total_all += total
        crawled_all += crawled
        locked_all += locked
    
    print("-" * 80)
    remaining_all = max(0, total_all - crawled_all - locked_all)
    if total_all > 0:
        overall = f"{crawled_all/total_all*100:.1f}%"
    else:
        overall = "-"
    print(f"{'總計':<18} {'':<14} {total_all:<8} {crawled_all:<8} {locked_all:<8} {remaining_all:<8} {overall:<10}")
    print(f"{'='*72}")
    
    # 顯示鎖定的影片
    print()
    locked_videos = []
    for stats_key, dir_name in CHANNEL_MAP.items():
        ch_stats = channels.get(stats_key, {})
        locked_list = ch_stats.get("locked", [])
        if locked_list:
            for vid in locked_list:
                locked_videos.append((dir_name, vid))
    
    if locked_videos:
        print("🔒 鎖定的影片:")
        for dir_name, vid in locked_videos[:10]:
            print(f"  [{dir_name}] {vid}")
        if len(locked_videos) > 10:
            print(f"  ... 還有 {len(locked_videos)-10} 支")
    else:
        print("🔒 鎖定的影片: 無")
    
    print()
    print("💡 使用方式:")
    print("   python3 show_status.py          # 顯示狀態")
    print("   python3 show_status.py --refresh # 更新頻道總數")


if __name__ == "__main__":
    import sys
    main()
