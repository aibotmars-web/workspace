#!/usr/bin/env python3
"""
專家頻道爬蟲狀態顯示
使用 channel_stats.json 來顯示完整的進度報告
"""

import json
import os
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
STATS_FILE = WORKSPACE / "channel_stats.json"
OUTPUT_DIR = WORKSPACE / "experts" / "transcripts"


def get_actual_crawled(channel_name):
    """從實際目錄統計已抓取的影片數"""
    channel_dir = OUTPUT_DIR / channel_name
    if not channel_dir.exists():
        return 0
    
    count = 0
    for f in channel_dir.glob("*.txt"):
        if f.stat().st_size > 100:
            count += 1
    return count


def load_stats():
    """載入 channel_stats.json"""
    if STATS_FILE.exists():
        with open(STATS_FILE) as f:
            return json.load(f)
    return {"channels": {}}


def save_stats(stats):
    """儲存 stats"""
    stats["last_updated"] = datetime.now().isoformat()
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def main():
    print(f"{'='*70}")
    print(f"📊 專家頻道爬蟲狀態追蹤")
    print(f"{'='*70}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    stats = load_stats()
    channels = stats.get("channels", {})
    
    # 顯示表頭
    print(f"{'頻道':<20} {'總計':<8} {'已抓':<8} {'鎖定':<8} {'待抓':<8} {'進度':<10}")
    print("-" * 70)
    
    total_all = 0
    crawled_all = 0
    locked_all = 0
    
    # 讀取實際目錄中的頻道
    if OUTPUT_DIR.exists():
        actual_dirs = {d.name for d in OUTPUT_DIR.iterdir() if d.is_dir()}
    else:
        actual_dirs = set()
    
    # 合併 stats 中的頻道和實際目錄
    all_channels = set(channels.keys()) | actual_dirs
    
    for channel in sorted(all_channels):
        # 從 stats 讀取
        ch_stats = channels.get(channel, {})
        total = ch_stats.get("total", 0)
        locked_list = ch_stats.get("locked", [])
        locked = len(locked_list) if locked_list else 0
        
        # 從實際目錄統計已抓取
        crawled = get_actual_crawled(channel)
        
        # 計算待抓
        remaining = max(0, total - crawled - locked)
        
        # 計算進度
        if total > 0:
            progress = f"{crawled/total*100:.1f}%"
        else:
            progress = "-"
        
        print(f"{channel:<20} {total:<8} {crawled:<8} {locked:<8} {remaining:<8} {progress:<10}")
        
        total_all += total
        crawled_all += crawled
        locked_all += locked
    
    print("-" * 70)
    remaining_all = max(0, total_all - crawled_all - locked_all)
    if total_all > 0:
        overall = f"{crawled_all/total_all*100:.1f}%"
    else:
        overall = "-"
    print(f"{'總計':<20} {total_all:<8} {crawled_all:<8} {locked_all:<8} {remaining_all:<8} {overall:<10}")
    print(f"{'='*70}")
    
    # 顯示鎖定的頻道（如果有）
    if locked_all > 0:
        print()
        print("🔒 鎖定的影片:")
        for channel, ch_stats in channels.items():
            locked_list = ch_stats.get("locked", [])
            if locked_list:
                print(f"  {channel}: {len(locked_list)} 支")
                for vid in locked_list[:5]:
                    print(f"    - {vid}")
                if len(locked_list) > 5:
                    print(f"    ... 還有 {len(locked_list)-5} 支")


if __name__ == "__main__":
    main()
