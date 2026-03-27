#!/usr/bin/env python3
"""
知識庫爬蟲 - 簡化版
只用 kd subtitles（快），會員專屬影片直接跳過
每輪只處理 1 個頻道，斷點續傳
"""

import subprocess
import time
import random
import json
import os
import signal
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
EXPERTS_DIR = WORKSPACE / "experts"
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

VIDEOS_PER_CHANNEL = 15


def get_channel_videos(channel_username, limit=15):
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s|%(title)s|%(availability)s",
        f"https://www.youtube.com/@{channel_username}/videos",
        "--playlist-end", str(limit * 2),  # 多抓一些再過濾
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
            
            # 跳過會員限定、私人影片
            if availability in ('subscriber_only', 'private') or 'subscriber' in availability.lower():
                skipped += 1
                continue
            
            videos.append((vid_id, title))
        
        if skipped > 0:
            print(f"  ⏭️  跳過 {skipped} 個會員限定/私人影片")
        return videos
    except Exception as e:
        print(f"  ⚠ yt-dlp 失敗: {e}")
        return []


def kd_subtitles(video_id, output_file):
    """用 kd subtitles 抓字幕，嚴格 45 秒超時"""
    url = f"https://www.youtube.com/watch?v={video_id}"
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
    except (subprocess.TimeoutExpired, Exception):
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    return None


def kd_transcribe(video_id, output_file):
    """用 kd transcribe（mlx-whisper）轉錄，適合沒有字幕的影片，嚴格 5 分鐘超時"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        proc = subprocess.Popen(
            ["kd", "transcribe", url, "--no-subtitles", "--backend", "mlx-whisper", "-o", str(output_file)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            preexec_fn=os.setsid
        )
        stdout, stderr = proc.communicate(timeout=300)
        if proc.returncode == 0 and output_file.exists() and output_file.stat().st_size > 100:
            text = output_file.read_text(encoding="utf-8").strip()
            return text
    except (subprocess.TimeoutExpired, Exception):
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    return None


def get_crawled_ids(channel_name):
    channel_dir = EXPERTS_DIR / channel_name
    if not channel_dir.exists():
        return set()
    return {f.stem for f in channel_dir.iterdir() if f.is_file()}


def main():
    print(f"{'='*60}")
    print(f"🚀 知識庫爬蟲（kd subtitles 專用）- {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

    state = json.load(open(STATE_FILE)) if STATE_FILE.exists() else {}
    last_idx = state.get("last_channel_index", 0)

    # 只處理一個頻道，狀態寫入下次從下一個繼續
    for i in range(len(CHANNELS)):
        idx = (last_idx + i) % len(CHANNELS)
        name, username = CHANNELS[idx]

        print(f"\n📺 [{idx+1}/{len(CHANNELS)}] {name}")

        channel_dir = EXPERTS_DIR / name
        channel_dir.mkdir(parents=True, exist_ok=True)

        videos = get_channel_videos(username, limit=20)
        if not videos:
            print(f"  ⚠ 無法取得影片列表")
            continue

        total_count = len(videos)
        crawled = get_crawled_ids(name)
        to_fetch = [(v, t) for v, t in videos if v not in crawled]

        if not to_fetch:
            print(f"  ✅ 無新影片")
            continue

        to_fetch = to_fetch[:VIDEOS_PER_CHANNEL]
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
                # 沒有字幕 → 嘗試 ASR 轉錄
                print(f"📝 無字幕，嘗試轉錄... ", end="", flush=True)
                text2 = kd_transcribe(vid, out_file)
                if text2 and len(text2) > 100:
                    out_file.write_text(text2, encoding="utf-8")
                    print(f"🎤 ({len(text2)}字)")
                    success += 1
                else:
                    print(f"❌")
                    failed += 1

            time.sleep(random.uniform(4, 7))

        crawled_total = len(get_crawled_ids(name))
        pct = int(crawled_total / total_count * 100) if total_count > 0 else 0
        print(f"  📊 {name}: {success}✅ {failed}❌")
        print(f"  📊 進度: {crawled_total}/{total_count} ({pct}%)")
        print(f"  📊 總計: 成功:{success} 失敗:{failed}")

        # 寫入狀態
        state["last_channel_index"] = (idx + 1) % len(CHANNELS)
        state["last_run"] = datetime.now().isoformat()
        
        # 更新頻道總數和進度
        if "channels" not in state:
            state["channels"] = {}
        crawled_now = len([v for v, t in videos if v in get_crawled_ids(name) or (v, t) in to_fetch[:success]])
        state["channels"][name] = {
            "total": total_count,
            "crawled": len(get_crawled_ids(name)) + success,
            "last_updated": datetime.now().isoformat()
        }
        json.dump(state, open(STATE_FILE, "w"))

        # 每頻道休息後退出，下次 cron 從下一個頻道繼續
        time.sleep(random.uniform(8, 12))
        break

    print(f"\n{'='*60}")
    print(f"✅ 完成! 時間: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
