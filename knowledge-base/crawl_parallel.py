#!/usr/bin/env python3
"""
並行爬蟲 - 同時跑多個頻道
用法: python3 crawl_parallel.py [同時跑幾個頻道]
"""
import subprocess
import sys
import random
import os
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
STATE_FILE = WORKSPACE / "crawl_state.json"

os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")

CHANNELS = [
    ("胡乃文开播", "Dr.Hu_talk"),
    ("柏格醫生中文", "drbergchinese"),
    ("Dr.HuangAmin", "Dr.HuangAmin"),
    ("周慕姿放心說", "muerstalk"),
    ("松明讲心理", "SongMing"),
    ("超真實商談", "RealBizChat"),
    ("Cofit211", "Cofit211"),
    ("泛科學", "PanScitw"),
    ("泛科學院", "panscischool"),
]

MAX_CONCURRENT = int(sys.argv[1]) if len(sys.argv) > 1 else 3

def get_channel_videos(channel_username, limit=15):
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s|%(title)s|%(availability)s",
        f"https://www.youtube.com/@{channel_username}/videos",
        "--playlist-end", str(limit * 2),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        videos = []
        skipped = 0
        for line in result.stdout.strip().split("\n"):
            if "|" not in line:
                continue
            parts = line.split("|")
            if len(parts) < 3:
                continue
            vid_id, title, availability = parts[0].strip(), parts[1].strip(), parts[2].strip()
            if availability in ('subscriber_only', 'private') or 'subscriber' in availability.lower():
                skipped += 1
                continue
            videos.append((vid_id, title))
        return videos, skipped
    except Exception:
        return [], 0

def kd_subtitles(video_id, output_file):
    url = f"https://www.youtube.com/watch?v={video_id}"
    import signal
    try:
        proc = subprocess.Popen(
            ["kd", "subtitles", url, "-o", str(output_file)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            preexec_fn=os.setsid
        )
        stdout, stderr = proc.communicate(timeout=45)
        if proc.returncode == 0 and output_file.exists() and output_file.stat().st_size > 100:
            text = output_file.read_text(encoding="utf-8").strip()
            return text
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except:
            pass
    except Exception:
        pass
    return None

def get_crawled_ids(channel_name):
    EXPERTS_DIR = WORKSPACE / "experts"
    channel_dir = EXPERTS_DIR / channel_name
    if not channel_dir.exists():
        return set()
    return {f.stem for f in channel_dir.iterdir() if f.is_file()}

def crawl_channel(name, username, channel_dir):
    """爬一個頻道，回傳成功/失敗數"""
    videos, skipped = get_channel_videos(username, limit=20)
    if not videos:
        return 0, 0, 0
    
    if skipped > 0:
        print(f"  ⏭️  跳過 {skipped} 個會員限定")
    
    total_count = len(videos)
    crawled = get_crawled_ids(name)
    to_fetch = [(v, t) for v, t in videos if v not in crawled]
    
    if not to_fetch:
        print(f"  ✅ 無新影片")
        return 0, 0, total_count
    
    to_fetch = to_fetch[:15]
    success, failed = 0, 0
    
    for vid, title in to_fetch:
        short = title[:30] + ("..." if len(title) > 30 else "")
        print(f"  🔄 {short} ", end="", flush=True)
        
        out_file = channel_dir / f"{vid}.txt"
        text = kd_subtitles(vid, out_file)
        
        if text and len(text) > 100:
            out_file.write_text(text, encoding="utf-8")
            print(f"✅ ({len(text)}字)")
            success += 1
        else:
            print(f"❌")
            failed += 1
        
        import time
        time.sleep(random.uniform(4, 7))
    
    return success, failed, total_count

def main():
    print(f"{'='*60}")
    print(f"🚀 知識庫爬蟲（並行版）- {datetime.now().strftime('%H:%M:%S')}")
    print(f"   同時跑 {MAX_CONCURRENT} 個頻道")
    print(f"{'='*60}")
    
    # 讀取狀態
    import json
    state = json.load(open(STATE_FILE)) if STATE_FILE.exists() else {}
    last_idx = state.get("last_channel_index", 0)
    
    # 找出還有新影片的頻道（最多同時跑 MAX_CONCURRENT 個）
    candidates = []
    for i in range(len(CHANNELS)):
        idx = (last_idx + i) % len(CHANNELS)
        name, username = CHANNELS[idx]
        videos, _ = get_channel_videos(username, limit=20)
        if videos:
            crawled = get_crawled_ids(name)
            new = [v for v, t in videos if v not in crawled]
            if new:
                candidates.append((idx, name, username, len(new)))
    
    # 取前 MAX_CONCURRENT 個
    selected = candidates[:MAX_CONCURRENT]
    
    if not selected:
        print("⚠️ 所有頻道都沒有新影片")
        return
    
    print(f"\n📺 這輪選擇: {[n for _, n, _, _ in selected]}\n")
    
    # 建立目錄
    EXPERTS_DIR = WORKSPACE / "experts"
    for _, name, _, _ in selected:
        (EXPERTS_DIR / name).mkdir(parents=True, exist_ok=True)
    
    # 並行爬取
    import concurrent.futures
    
    def crawl_one(args):
        idx, name, username, new_count = args
        EXPERTS_DIR = WORKSPACE / "experts"
        return idx, name, crawl_channel(name, username, EXPERTS_DIR / name)
    
    total_success = 0
    total_failed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = [executor.submit(crawl_one, s) for s in selected]
        for f in concurrent.futures.as_completed(futures):
            idx, name, (success, failed, total) = f.result()
            crawled_total = len(get_crawled_ids(name))
            pct = int(crawled_total / total * 100) if total > 0 else 0
            print(f"\n📊 {name}: {success}✅ {failed}❌ | 進度 {crawled_total}/{total} ({pct}%)")
            total_success += success
            total_failed += failed
    
    # 更新狀態
    new_last_idx = (selected[-1][0] + 1) % len(CHANNELS) if selected else last_idx
    state["last_channel_index"] = new_last_idx
    state["last_run"] = datetime.now().isoformat()
    json.dump(state, open(STATE_FILE, "w"))
    
    print(f"\n{'='*60}")
    print(f"✅ 完成! 成功:{total_success} 失敗:{total_failed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
