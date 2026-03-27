#!/usr/bin/env python3
"""
用瀏覽器取得頻道影片列表 + kd 抓字幕
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

# 頻道列表（從 stats 讀取 URL）
def load_channels():
    stats = json.load(open(STATS_FILE))
    return {
        ch: info["url"] 
        for ch, info in stats.get("channels", {}).items()
    }

CHANNELS = [
    ("SongMing", "https://www.youtube.com/@SongMing/videos"),
    ("PanScitw", "https://www.youtube.com/@PanScitw/videos"),
    ("DrHarveyTalk", "https://www.youtube.com/@DrHarveyTalk/videos"),
    ("Cofit211", "https://www.youtube.com/@Cofit211/videos"),
    ("Dr.Hu_talk", "https://www.youtube.com/@Dr.Hu_talk/videos"),
    ("drbergchinese", "https://www.youtube.com/@drbergchinese/videos"),
    ("muerstalk", "https://www.youtube.com/@muerstalk/videos"),
    ("panscischool", "https://www.youtube.com/@panscischool/videos"),
    ("Dr.HuangAmin", "https://www.youtube.com/@Dr.HuangAmin/videos"),
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
            # 去掉語言後綴
            for lang in ['.en', '.zh-TW', '.zh-CN']:
                if lang in name:
                    name = name.replace(lang, '')
            ids.add(name)
    return ids


def get_channel_videos_browser(channel_url, limit=20):
    """用瀏覽器取得頻道影片 ID"""
    try:
        # 打開頻道頁面
        subprocess.run(
            ["agent-browser", "open", channel_url, "--timeout", "30000"],
            capture_output=True, timeout=40
        )
        time.sleep(3)
        
        # 滾動頁面載入更多影片
        for _ in range(3):
            subprocess.run(
                ["agent-browser", "scroll", "2000"],
                capture_output=True, timeout=10
            )
            time.sleep(1)
        
        # 取得 snapshot
        result = subprocess.run(
            ["agent-browser", "snapshot", "-c", "--timeout", "15000"],
            capture_output=True, text=True, timeout=20
        )
        output = result.stdout
        
        # 解析 video IDs
        # 格式: /watch?v=VIDEO_ID
        video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', output)
        
        # 去重
        video_ids = list(dict.fromkeys(video_ids))[:limit]
        
        return video_ids
        
    except Exception as e:
        print(f"    ⚠ 瀏覽器取得失敗: {e}")
        return []


def crawl_video(vid, channel_dir):
    """用 kd 抓單個影片字幕"""
    output_file = channel_dir / f"{vid}.txt"
    
    if output_file.exists() and output_file.stat().st_size > 100:
        return "skipped"
    
    # 隨機延遲
    time.sleep(random.uniform(2, 5))
    
    try:
        result = subprocess.run(
            ["kd", "subtitles", f"https://www.youtube.com/watch?v={vid}", "-o", str(output_file)],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and output_file.exists():
            return "success"
    except:
        pass
    
    # 刪除失敗的檔案
    if output_file.exists():
        output_file.unlink()
    return "failed"


def crawl_channel(channel_name, channel_url, limit=10):
    """爬取一個頻道"""
    channel_dir = EXPERTS_DIR / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"  🔍 取得影片列表...")
    video_ids = get_channel_videos_browser(channel_url, limit=limit)
    
    if not video_ids:
        print(f"  ⚠ 無法取得影片")
        return {"success": 0, "failed": 0, "skipped": 0}
    
    print(f"  📺 找到 {len(video_ids)} 個影片")
    
    # 取得已抓取的
    crawled = get_crawled_videos(channel_name)
    print(f"  📊 已抓取: {len(crawled)} 個")
    
    success = 0
    failed = 0
    skipped = 0
    
    for vid in video_ids:
        if vid in crawled:
            skipped += 1
            continue
        
        print(f"  → {vid}", end="", flush=True)
        result = crawl_video(vid, channel_dir)
        
        if result == "success":
            success += 1
            print(" ✓")
        elif result == "skipped":
            skipped += 1
        else:
            failed += 1
            print(" ✗")
    
    return {"success": success, "failed": failed, "skipped": skipped}


def main():
    print(f"{'='*60}")
    print(f"🚀 知識庫爬蟲 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 讀取狀態
    state_file = WORKSPACE / "crawl_state.json"
    if state_file.exists():
        state = json.load(open(state_file))
        last_index = state.get("last_channel_index", 0)
    else:
        last_index = 0
    
    # 選擇頻道
    channel_name, channel_url = CHANNELS[last_index % len(CHANNELS)]
    print(f"📺 頻道: {channel_name}")
    
    # 爬取
    result = crawl_channel(channel_name, channel_url, limit=10)
    
    print()
    print(f"✅ 成功: {result['success']}, ❌ 失敗: {result['failed']}, ⏭️ 跳過: {result['skipped']}")
    
    # 更新狀態
    next_index = (last_index + 1) % len(CHANNELS)
    state = {
        "last_channel_index": next_index,
        "last_run": datetime.now().isoformat(),
        "last_channel": channel_name,
        "last_result": result,
    }
    json.dump(state, open(state_file, "w"))
    
    # 關閉瀏覽器
    subprocess.run(["agent-browser", "close"], capture_output=True)
    
    print(f"⏰ 下次: {CHANNELS[next_index][0]}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
