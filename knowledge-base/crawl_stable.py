#!/usr/bin/env python3
"""
知識庫爬蟲 - 修正版（2026-03-29）
修復問題：
1. @username/videos 只爬第一頁，導致 total 永遠只有 30-40 部
2. 改用 uploads playlist，可以分頁拿到真正的總數

邏輯：
1. 從頻道抓 uploads playlist ID
2. 用 playlist_count 取得真正總影片數
3. 用 uploads playlist 抓所有影片（分頁）
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
    ("超真實商談", "RealBizChat"),      # 115 部
    ("泛科學院", "panscischool"),       # 141 部
    ("周慕姿放心說", "muerstalk"),      # 175 部
    ("Dr.HuangAmin", "Dr.HuangAmin"),  # 220 部
    ("Cofit211", "Cofit211"),          # 313 部
    ("胡乃文开播", "Dr.Hu_talk"),       # 331 部
    ("松明讲心理", "SongMing"),         # 491 部
    ("泛科學", "PanScitw"),             # 543 部
    ("top3pct", "top3pct"),            # 210 部（2026-07-07 自退役的 kd_crawl daemon 收編）
]

VIDEOS_PER_CHANNEL = 15       # 每輪每頻道處理的數量
MAX_TRANSCRIBE_PER_RUN = 8    # 每輪最多本地轉錄數（時間預算是主要限制，這是保險）
MAX_FAILS_PER_VIDEO = 3       # 同一部影片失敗幾次後不再重試
# 時間預算：跑滿為止（可跨多頻道），可用環境變數覆寫方便測試
# 時間預算（分鐘）—— 預設 60 分鐘讓一次能多跑幾個頻道
# 可用 KB_TIME_BUDGET_MIN 環境變數覆寫（單輪跑多久）。原本預設 20 太短，九個頻道輪不完。
TIME_BUDGET_MIN = float(os.environ.get("KB_TIME_BUDGET_MIN", "60"))
_RUN_DEADLINE = None  # main() 開跑時設定


def time_left():
    """回傳本輪剩餘秒數"""
    return _RUN_DEADLINE - time.monotonic() if _RUN_DEADLINE else 0


def is_members_only_title(title):
    """列表階段的 availability 有時漏標會員影片，用標題再擋一層"""
    t = title.lower()
    return "member" in t or "會員限定" in title or "會員專屬" in title


def get_playlist_info(channel_username):
    """從頻道頁面抓 uploads playlist ID 和真正總數（用 --playlist-end 500 數行數）"""
    try:
        # 先抓 playlist ID
        cmd1 = [
            "yt-dlp", "--flat-playlist", "--print", "%(playlist_id)s",
            f"https://www.youtube.com/@{channel_username}",
            "--playlist-end", "1",
        ]
        r1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=60)
        playlist_id = None
        for line in r1.stdout.strip().split('\n'):
            pid = line.strip()
            # UC... = uploads, UU... = liked videos, LL... = liked videos alt
            if pid.startswith(("UC", "UU", "LL")):
                playlist_id = pid
                break
        if not playlist_id:
            return None, 0

        # 抓所有公開影片數量（--playlist-end 5000 覆盖所有頻道）
        cmd2 = [
            "yt-dlp", "--flat-playlist",
            "--print", "%(id)s|%(availability)s",
            f"https://www.youtube.com/@{channel_username}/videos",
            "--playlist-end", "5000",
        ]
        r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=120)
        total = 0
        for line in r2.stdout.strip().split('\n'):
            if '|' not in line:
                continue
            parts = line.split('|')
            if len(parts) < 2:
                continue
            avail = parts[1].strip()
            if avail in ('subscriber_only', 'private') or 'subscriber' in avail.lower():
                continue
            total += 1

        playlist_url = f"https://www.youtube.com/@{channel_username}/videos"
        return playlist_url, total
    except Exception as e:
        print(f"  ⚠ 取得 playlist 失敗: {e}")
        return None, 0


def get_channel_videos(playlist_url, limit=5000):
    """從 uploads playlist 抓影片，含 availability 過濾"""
    cmd = [
        "yt-dlp", "--flat-playlist",
        "--print", "%(id)s|%(title)s|%(availability)s",
        playlist_url,
        "--playlist-end", str(limit),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
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


WHISPER_MODEL = "mlx-community/whisper-large-v3-mlx"  # 本地已快取，中文品質最佳
ERROR_LOG = WORKSPACE / "kb-crawl-errors.log"


def _log_fail(video_id, reason):
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} {video_id} {reason}\n")


def kd_transcribe(video_id, output_file):
    """yt-dlp 下載音訊 + mlx-whisper 本地轉錄，6 分鐘總超時。

    音訊由 yt-dlp 直接下載（自帶簽名/標頭處理），不再用 `-g` 取 URL 丟給
    ffmpeg——那條路現在會被 YouTube 403。失敗原因寫入 kb-crawl-errors.log。
    """
    import threading
    result_holder = [None]
    audio_file = output_file.with_suffix(".m4a")

    def _do():
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            r1 = subprocess.run(
                ["yt-dlp", "-f", "ba/b", "--no-playlist", "-o", str(audio_file), url],
                capture_output=True, text=True, timeout=180,
            )
            if r1.returncode != 0 or not audio_file.exists():
                _log_fail(video_id, f"yt-dlp音訊下載失敗: {r1.stderr.strip()[-300:]}")
                return

            import mlx_whisper
            result = mlx_whisper.transcribe(
                str(audio_file), path_or_hf_repo=WHISPER_MODEL, language="zh",
            )
            text = result.get("text", "").strip()
            if text:
                result_holder[0] = text
            else:
                _log_fail(video_id, "whisper轉錄結果為空")
        except Exception as e:
            _log_fail(video_id, f"{type(e).__name__}: {str(e)[:300]}")
        finally:
            if audio_file.exists():
                try:
                    audio_file.unlink()
                except:
                    pass

    t = threading.Thread(target=_do)
    t.daemon = True
    t.start()
    t.join(timeout=360)
    if t.is_alive():
        _log_fail(video_id, "轉錄超時(360s)")
        result_holder[0] = None
    return result_holder[0]


def get_crawled_ids(channel_name):
    channel_dir = EXPERTS_DIR / channel_name
    if not channel_dir.exists():
        return set()
    return {f.stem for f in channel_dir.iterdir() if f.is_file()}


def main():
    global _RUN_DEADLINE
    _RUN_DEADLINE = time.monotonic() + TIME_BUDGET_MIN * 60

    print(f"{'='*60}")
    print(f"🚀 知識庫爬蟲（修正版）- {datetime.now().strftime('%H:%M:%S')}"
          f"（時間預算 {TIME_BUDGET_MIN:.0f} 分鐘）")
    print(f"{'='*60}")

    state = json.load(open(STATE_FILE)) if STATE_FILE.exists() else {}
    last_idx = state.get("last_channel_index", 0)

    for i in range(len(CHANNELS)):
        if time_left() < 180:
            print(f"\n⏰ 時間預算用完，本輪結束（下輪從 index {state.get('last_channel_index', 0)} 續跑）")
            break

        idx = (last_idx + i) % len(CHANNELS)
        name, username = CHANNELS[idx]

        print(f"\n📺 [{idx+1}/{len(CHANNELS)}] {name}")

        channel_dir = EXPERTS_DIR / name
        channel_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: 取得 uploads playlist URL 和總數
        print(f"  🔍 抓 playlist URL...")
        playlist_url, true_total = get_playlist_info(username)
        
        if not playlist_url:
            cerrs = state.setdefault("channel_errors", {})
            cerrs[name] = cerrs.get(name, 0) + 1
            print(f"  ⚠ 無法取得 playlist（連續第 {cerrs[name]} 次）")
            if cerrs[name] >= 3:
                print(f"  🚨 頻道 @{username} 連續 {cerrs[name]} 次解析失敗——"
                      f"handle 可能已改名或頻道關閉，請人工確認新網址並更新 CHANNELS 清單")
            state["last_channel_index"] = (idx + 1) % len(CHANNELS)
            json.dump(state, open(STATE_FILE, "w"))
            continue
        state.setdefault("channel_errors", {}).pop(name, None)

        print(f"  📊 真正總數: {true_total} 部（已排除會員限定）")

        # Step 2: 抓所有公開影片（從 uploads playlist）
        print(f"  📋 抓公開影片列表...")
        videos = get_channel_videos(playlist_url)
        if not videos:
            print(f"  ⚠ 無法取得影片列表")
            state["last_channel_index"] = (idx + 1) % len(CHANNELS)
            json.dump(state, open(STATE_FILE, "w"))
            continue

        total_count = len(videos)
        print(f"  📋 抓到 {total_count} 部公開影片")

        crawled = get_crawled_ids(name)
        fails = state.setdefault("failed_videos", {})
        skipped_fails = sum(1 for v, _ in videos if fails.get(v, 0) >= MAX_FAILS_PER_VIDEO)
        skipped_members = sum(1 for _, t in videos if is_members_only_title(t))
        to_fetch = [(v, t) for v, t in videos
                    if v not in crawled
                    and fails.get(v, 0) < MAX_FAILS_PER_VIDEO
                    and not is_members_only_title(t)]
        if skipped_fails:
            print(f"  ⏭️  略過 {skipped_fails} 部連續失敗 ≥{MAX_FAILS_PER_VIDEO} 次的影片（記錄在 failed_videos）")
        if skipped_members:
            print(f"  ⏭️  略過 {skipped_members} 部標題含會員限定的影片")

        if not to_fetch:
            print(f"  ✅ 無新影片")
        else:
            to_fetch = to_fetch[:VIDEOS_PER_CHANNEL]
            success, failed = 0, 0
            transcribed = 0

            for vid, title in to_fetch:
                if time_left() < 60:
                    print(f"  ⏰ 時間預算用完，剩餘影片下輪處理")
                    break

                short = title[:28] + ("..." if len(title) > 28 else "")
                print(f"  🔄 {short} ", end="", flush=True)

                try:
                    out_file = channel_dir / f"{vid}.txt"
                    text = kd_subtitles(vid, out_file)

                    if text and len(text) > 100:
                        out_file.write_text(text, encoding="utf-8")
                        print(f"✅ ({len(text)}字)")
                        success += 1
                    elif transcribed >= MAX_TRANSCRIBE_PER_RUN or time_left() < 300:
                        # 不算失敗，下輪再轉錄——控制單輪執行時間
                        print(f"⏭️  無字幕，本輪轉錄額度/時間已滿，下輪處理")
                    else:
                        print(f"📝 無字幕，轉錄... ", end="", flush=True)
                        transcribed += 1
                        text2 = kd_transcribe(vid, out_file)
                        if text2 and len(text2) > 100:
                            out_file.write_text(text2, encoding="utf-8")
                            print(f"🎤 ({len(text2)}字)")
                            success += 1
                            fails.pop(vid, None)
                        else:
                            fails[vid] = fails.get(vid, 0) + 1
                            print(f"❌ (第{fails[vid]}次，詳見 kb-crawl-errors.log)")
                            failed += 1
                except Exception as e:
                    # 單部影片任何意外都不擋整輪
                    fails[vid] = fails.get(vid, 0) + 1
                    _log_fail(vid, f"意外錯誤 {type(e).__name__}: {str(e)[:200]}")
                    print(f"❌ 意外錯誤 (第{fails[vid]}次)")
                    failed += 1

                time.sleep(random.uniform(4, 7))

            crawled_total = len(get_crawled_ids(name))
            pct = int(crawled_total / total_count * 100) if total_count > 0 else 0
            print(f"  📊 {name}: {success}✅ {failed}❌")
            print(f"  📊 進度: {crawled_total}/{total_count} ({pct}%)")

        # 寫入狀態
        state["last_channel_index"] = (idx + 1) % len(CHANNELS)
        state["last_run"] = datetime.now().isoformat()
        
        if "channels" not in state:
            state["channels"] = {}
        state["channels"][name] = {
            "total": total_count,
            "crawled": len(get_crawled_ids(name)),
            "last_updated": datetime.now().isoformat()
        }
        json.dump(state, open(STATE_FILE, "w"))

        # 時間還夠就繼續下一個頻道（時間預算制取代原本的一輪一頻道）
        time.sleep(random.uniform(8, 12))

    print(f"\n{'='*60}")
    print(f"✅ 完成! 時間: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
