#!/usr/bin/env python3
"""
ASR 轉錄爬蟲（慢速版）
用 kd transcribe (mlx-whisper) 處理沒有字幕的頻道
每次只處理 2 部影片，避免卡太久
"""
import subprocess, time, random, json, os, signal
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
EXPERTS_DIR = WORKSPACE / "experts"
STATE_FILE = WORKSPACE / "crawl_asr_state.json"

os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")

# 無字幕、需要 ASR 的頻道
CHANNELS = [
    ("柏格醫生中文", "drbergchinese"),
    ("胡乃文开播", "Dr.Hu_talk"),
    ("Dr.HuangAmin", "Dr.HuangAmin"),
]

VIDEOS_PER_ROUND = 20  # 每次轉錄 20 部（狀態會保存，cron 多次觸發會持續累積）


def get_channel_videos(channel_username, limit=15):
    cmd = ["yt-dlp", "--flat-playlist", "--print", "%(id)s|%(title)s|%(availability)s",
           f"https://www.youtube.com/@{channel_username}/videos", "--playlist-end", str(limit * 2)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        videos, skipped = [], 0
        for line in result.stdout.strip().split("\n"):
            if "|" not in line: continue
            parts = line.split("|")
            if len(parts) < 3: continue
            vid_id, title, avail = parts[0].strip(), parts[1].strip(), parts[2].strip()
            if avail in ('subscriber_only', 'private') or 'subscriber' in avail.lower():
                skipped += 1; continue
            videos.append((vid_id, title))
        return videos, skipped
    except:
        return [], 0


def kd_transcribe(video_id, output_file):
    """用 mlx_whisper 直接轉錄（繞過 kd CLI 的 hang 問題）"""
    import shutil
    url = f"https://www.youtube.com/watch?v={video_id}"
    audio_path = f"/tmp/asr_{video_id}.mp3"
    
    # 下載音頻
    try:
        r = subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "5",
             "-o", audio_path, url],
            capture_output=True, text=True, timeout=60
        )
        if not os.path.exists(audio_path):
            return None
    except:
        return None
    
    # 用 mlx_whisper 轉錄
    try:
        from mlx_whisper import transcribe
        result = transcribe(audio=audio_path, language="zh")
        text = result.get("text", "").strip()
        # 清理
        os.remove(audio_path)
        return text if text else None
    except Exception as e:
        print(f"MLX錯誤:{e}", end=" ")
        try: os.remove(audio_path)
        except: pass
        return None


def get_crawled_ids(name):
    d = EXPERTS_DIR / name
    return {f.stem for f in d.iterdir()} if d.exists() else set()


def main():
    print(f"{'='*60}")
    print(f"🎤 ASR 轉錄爬蟲（慢速版）- {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

    state = json.load(open(STATE_FILE)) if STATE_FILE.exists() else {}
    last_idx = state.get("last_channel_index", 0)

    for i in range(len(CHANNELS)):
        idx = (last_idx + i) % len(CHANNELS)
        name, username = CHANNELS[idx]

        print(f"\n📺 [{idx+1}/{len(CHANNELS)}] {name}（ASR 轉錄）")
        (EXPERTS_DIR / name).mkdir(parents=True, exist_ok=True)

        videos, skipped = get_channel_videos(username, limit=30)
        if not videos:
            print(f"  ⚠ 無法取得影片"); continue
        if skipped > 0: print(f"  ⏭️  跳過 {skipped} 個會員限定")

        crawled = get_crawled_ids(name)
        to_fetch = [(v, t) for v, t in videos if v not in crawled]
        if not to_fetch:
            print(f"  ✅ 無新影片"); continue

        to_fetch = to_fetch[:VIDEOS_PER_ROUND]
        success, failed = 0, 0

        for vid, title in to_fetch:
            short = title[:28] + ("…" if len(title) > 28 else "")
            print(f"  🎤 {short} ", end="", flush=True)
            out = EXPERTS_DIR / name / f"{vid}.txt"
            text = kd_transcribe(vid, out)
            if text and len(text) > 100:
                out.write_text(text, encoding="utf-8")
                print(f"✅ ({len(text)}字)"); success += 1
            else:
                print(f"❌"); failed += 1
            time.sleep(random.uniform(5, 10))

        total = len(videos)
        crawled_now = len(get_crawled_ids(name))
        pct = int(crawled_now / total * 100) if total > 0 else 0
        print(f"  📊 {name}: {success}✅ {failed}❌ | 進度 {crawled_now}/{total} ({pct}%)")

        state["last_channel_index"] = (idx + 1) % len(CHANNELS)
        state["last_run"] = datetime.now().isoformat()
        json.dump(state, open(STATE_FILE, "w"))
        time.sleep(random.uniform(10, 15))
        break

    print(f"\n{'='*60}")
    print(f"✅ 完成! 時間: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
