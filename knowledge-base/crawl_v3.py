#!/usr/bin/env python3
"""
知識庫爬蟲 - 輪流抓取每個頻道
每次每個頻道抓 3-5 個，分散風險
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

# 嘗試找 DrHarveyTalk 的 URL
try:
    stats = json.load(open(STATS_FILE))
    if "DrHarveyTalk" in stats.get("channels", {}):
        url = stats["channels"]["DrHarveyTalk"].get("url", "")
        if url:
            CHANNELS.append(("DrHarveyTalk", url))
except:
    pass


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


def get_channel_videos_browser(channel_url, limit=30):
    """用瀏覽器取得頻道影片 ID"""
    try:
        subprocess.run(
            ["agent-browser", "open", channel_url, "--timeout", "30000"],
            capture_output=True, timeout=40
        )
        time.sleep(3)
        
        # 滾動頁面
        for _ in range(5):
            subprocess.run(
                ["agent-browser", "scroll", "3000"],
                capture_output=True, timeout=10
            )
            time.sleep(0.5)
        
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
    
    time.sleep(random.uniform(2, 4))
    
    try:
        result = subprocess.run(
            ["kd", "subtitles", f"https://www.youtube.com/watch?v={vid}", "-o", str(output_file)],
            capture_output=True, text=True, timeout=60
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
    print(f"🚀 知識庫爬蟲 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    total_success = 0
    total_failed = 0
    total_skipped = 0
    
    # 讀取狀態
    state_file = WORKSPACE / "crawl_state.json"
    if state_file.exists():
        state = json.load(open(state_file))
        last_index = state.get("last_channel_index", 0)
    else:
        last_index = 0
    
    # 輪流抓每個頻道（每次每個抓 3 個）
    videos_per_channel = 3
    
    for i in range(len(CHANNELS)):
        idx = (last_index + i) % len(CHANNELS)
        channel_name, channel_url = CHANNELS[idx]
        
        print(f"\n📺 [{i+1}/{len(CHANNELS)}] {channel_name}")
        
        channel_dir = EXPERTS_DIR / channel_name
        channel_dir.mkdir(parents=True, exist_ok=True)
        
        # 取得影片列表
        video_ids = get_channel_videos_browser(channel_url, limit=30)
        
        if not video_ids:
            print(f"  ⚠ 無法取得影片")
            continue
        
        print(f"  🔍 找到 {len(video_ids)} 個影片")
        
        # 取得已抓取的
        crawled = get_crawled_videos(channel_name)
        print(f"  📊 已抓: {len(crawled)}")
        
        # 過濾未抓取的
        to_fetch = [v for v in video_ids if v not in crawled][:videos_per_channel]
        
        if not to_fetch:
            print(f"  ✅ 全部已抓")
            continue
        
        print(f"  🎯 待抓: {len(to_fetch)} 個")
        
        success = 0
        failed = 0
        
        for vid in to_fetch:
            print(f"  → {vid}", end="", flush=True)
            result = crawl_video(vid, channel_dir)
            
            if result == "success":
                success += 1
                print(" ✓")
            else:
                failed += 1
                print(" ✗")
        
        total_success += success
        total_failed += failed
        
        print(f"  📈 本次: 成功 {success}, 失敗 {failed}")
        
        # 短暫休息
        time.sleep(random.uniform(1, 2))
    
    # 更新狀態
    next_index = (last_index + len(CHANNELS)) % len(CHANNELS)
    state = {
        "last_channel_index": next_index,
        "last_run": datetime.now().isoformat(),
        "last_result": {
            "success": total_success,
            "failed": total_failed,
        }
    }
    json.dump(state, open(state_file, "w"))
    
    # 關閉瀏覽器
    subprocess.run(["agent-browser", "close"], capture_output=True)
    
    print(f"\n{'='*60}")
    print(f"✅ 完成!")
    print(f"   成功: {total_success}, 失敗: {total_failed}")
    print(f"   下次從頻道 {CHANNELS[next_index][0]} 開始")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
