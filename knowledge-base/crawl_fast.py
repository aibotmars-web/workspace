#!/usr/bin/env python3
"""
知識庫爬蟲 - 高速版
每次每個頻道抓 10 個，更快覆蓋
"""

import subprocess
import time
import random
import json
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
STATS_FILE = WORKSPACE / "channel_stats.json"
EXPERTS_DIR = WORKSPACE / "experts"

# 頻道列表
CHANNELS = [
    ("Dr.Hu_talk", "https://www.youtube.com/@Dr.Hu_talk/videos"),
    ("drbergchinese", "https://www.youtube.com/@drbergchinese/videos"),
    ("muerstalk", "https://www.youtube.com/@muerstalk/videos"),
    ("panscischool", "https://www.youtube.com/@panscischool/videos"),
    ("Cofit211", "https://www.youtube.com/@Cofit211/videos"),
    ("PanScitw", "https://www.youtube.com/@PanScitw/videos"),
    ("Dr.HuangAmin", "https://www.youtube.com/@Dr.HuangAmin/videos"),
    ("SongMing", "https://www.youtube.com/@SongMing/videos"),
]


def get_crawled_videos(dir_name):
    """取得已抓取的 video IDs"""
    channel_dir = EXPERTS_DIR / dir_name
    if not channel_dir.exists():
        return set()
    
    ids = set()
    for f in channel_dir.iterdir():
        if f.is_file() and f.suffix in ['.txt', '.md']:
            name = f.stem
            for lang in ['.en', '.zh-TW', '.zh-CN']:
                if lang in name:
                    name = name.replace(lang, '')
            ids.add(name)
    return ids


def get_channel_videos_browser(channel_url, limit=50):
    """用瀏覽器取得頻道影片 ID"""
    try:
        subprocess.run(
            ["agent-browser", "open", channel_url, "--timeout", "30000"],
            capture_output=True, timeout=40
        )
        time.sleep(2)
        
        # 滾動頁面載入更多
        for _ in range(8):
            subprocess.run(
                ["agent-browser", "scroll", "3000"],
                capture_output=True, timeout=10
            )
            time.sleep(0.3)
        
        result = subprocess.run(
            ["agent-browser", "snapshot", "-c", "--timeout", "15000"],
            capture_output=True, text=True, timeout=20
        )
        
        video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', result.stdout)
        video_ids = list(dict.fromkeys(video_ids))[:limit]
        return video_ids
        
    except Exception as e:
        return []


def crawl_video(vid, channel_dir):
    """用 kd 抓字幕"""
    output_file = channel_dir / f"{vid}.txt"
    
    if output_file.exists() and output_file.stat().st_size > 100:
        return "skipped"
    
    time.sleep(random.uniform(1, 2))  # 更快間隔
    
    try:
        result = subprocess.run(
            ["kd", "subtitles", f"https://www.youtube.com/watch?v={vid}", "-o", str(output_file)],
            capture_output=True, text=True, timeout=45
        )
        if result.returncode == 0 and output_file.exists():
            return "success"
    except:
        pass
    
    if output_file.exists():
        output_file.unlink()
    return "failed"


def main():
    print(f"{'='*60}")
    print(f"🚀 知識庫爬蟲(高速版) - {datetime.now().strftime('%H:%M:%S')}")
    
    total_success = 0
    total_failed = 0
    
    # 讀取狀態
    state_file = WORKSPACE / "crawl_state.json"
    last_index = 0
    if state_file.exists():
        state = json.load(open(state_file))
        last_index = state.get("last_channel_index", 0)
    
    videos_per_channel = 10  # 增加到 10 個
    
    for i in range(len(CHANNELS)):
        idx = (last_index + i) % len(CHANNELS)
        channel_name, channel_url = CHANNELS[idx]
        
        print(f"\n📺 [{i+1}/{len(CHANNELS)}] {channel_name}")
        
        channel_dir = EXPERTS_DIR / channel_name
        channel_dir.mkdir(parents=True, exist_ok=True)
        
        video_ids = get_channel_videos_browser(channel_url, limit=50)
        
        if not video_ids:
            print(f"  ⚠ 無法取得")
            continue
        
        crawled = get_crawled_videos(channel_name)
        to_fetch = [v for v in video_ids if v not in crawled][:videos_per_channel]
        
        if not to_fetch:
            print(f"  ✅ 已完成")
            continue
        
        print(f"  🎯 抓 {len(to_fetch)} 個...")
        
        success = 0
        failed = 0
        
        for vid in to_fetch:
            result = crawl_video(vid, channel_dir)
            if result == "success":
                success += 1
                print(f"  ✓", end="", flush=True)
            else:
                failed += 1
                print(f"  ✗", end="", flush=True)
        
        total_success += success
        total_failed += failed
        
        print(f" ({success}/{len(to_fetch)})")
        
        time.sleep(random.uniform(0.5, 1))
    
    # 更新狀態
    next_index = (last_index + len(CHANNELS)) % len(CHANNELS)
    json.dump({
        "last_channel_index": next_index,
        "last_run": datetime.now().isoformat(),
    }, open(state_file, "w"))
    
    subprocess.run(["agent-browser", "close"], capture_output=True)
    
    print(f"\n{'='*60}")
    print(f"✅ 成功: {total_success}, 失敗: {total_failed}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
