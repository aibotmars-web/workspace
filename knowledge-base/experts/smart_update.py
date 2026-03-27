#!/usr/bin/env python3
"""
智慧更新知識庫 - 統一使用 kd CLI
kd subtitles 抓現有字幕，kd transcribe 做本地 ASR
不依賴 youtube-transcript-api（IP 被封）或 TranscriptAPI（需付費）
"""

import os
import time
import subprocess
from pathlib import Path

# 確保 PATH 包含 homebrew
os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")

# 專家頻道列表 (頻道名稱: YouTube @username)
CHANNELS = {
    "胡乃文开播": "@Dr.Hu_talk",
    "柏格醫生中文": "@drbergchinese",
    "Dr.HuangAmin": "@Dr.HuangAmin",
    "周慕姿放心說": "@muerstalk",
    "松明讲心理": "@SongMing",
    "超真實商談": "@RealBizChat",
    "Cofit211": "@Cofit211",
    "泛科學": "@PanScitw",
    "泛科學院": "@panscischool",
}

BASE_DIR = Path.home() / ".openclaw/workspace/knowledge-base/experts"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"

MAX_VIDEOS_PER_CHANNEL = 8   # 抓更多部，確保有公開影片
DELAY_BETWEEN_VIDEOS = 3     # 稍微快一點
DELAY_BETWEEN_CHANNELS = 10


def get_channel_videos(channel_username, limit=5):
    """用 yt-dlp 列出頻道最新影片 ID（只列表，不抓內容，不會被 429）"""
    channel = channel_username.replace("@", "")
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s|%(title)s",
        f"https://www.youtube.com/@{channel}/videos",
        "--playlist-end", str(limit),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        videos = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                vid_id, title = line.split("|", 1)
                videos.append((vid_id.strip(), title.strip()))
        return videos
    except FileNotFoundError:
        print("  ⚠️ yt-dlp 未找到，請確認 /opt/homebrew/bin/yt-dlp 存在")
        return []
    except subprocess.TimeoutExpired:
        print("  ⚠️ yt-dlp 逾時")
        return []
    except Exception as e:
        print(f"  ⚠️ 獲取影片失敗: {e}")
        return []


def kd_extract_transcript(video_id):
    """
    用 kd 抓字幕，兩階段：
    1. kd subtitles（快，秒級，抓現成字幕）
    2. kd transcribe（慢，分鐘級，本地 ASR，保證成功）
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    temp_file = Path(f"/tmp/kd_{video_id}.txt")

    # 清理可能的殘留
    temp_file.unlink(missing_ok=True)

    # 階段 1: kd subtitles（快速）
    try:
        result = subprocess.run(
            ["kd", "subtitles", url, "-o", str(temp_file)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if temp_file.exists() and temp_file.stat().st_size > 100:
            text = temp_file.read_text(encoding="utf-8").strip()
            temp_file.unlink(missing_ok=True)
            return text, "subtitles"
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass

    # 階段 2: kd transcribe + mlx-whisper（本地 ASR，不需 API key）
    print("ASR...", end=" ", flush=True)
    temp_file.unlink(missing_ok=True)
    try:
        result = subprocess.run(
            ["kd", "transcribe", url, "--no-subtitles", "--backend", "mlx-whisper", "-o", str(temp_file)],
            capture_output=True,
            text=True,
            timeout=600,  # ASR 可能需要幾分鐘
        )
        if temp_file.exists() and temp_file.stat().st_size > 100:
            text = temp_file.read_text(encoding="utf-8").strip()
            temp_file.unlink(missing_ok=True)
            return text, "ASR"
    except subprocess.TimeoutExpired:
        print("ASR逾時", end=" ", flush=True)
    except Exception as e:
        print(f"ASR錯誤:{e}", end=" ", flush=True)

    # 清理
    temp_file.unlink(missing_ok=True)
    return None, "失敗"


def main():
    print("🚀 知識庫更新（kd CLI）")
    print("=" * 50)

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    stats = {"new": 0, "skip": 0, "fail": 0}

    for name, channel_username in CHANNELS.items():
        print(f"\n📺 {name} ({channel_username})")

        videos = get_channel_videos(channel_username, limit=MAX_VIDEOS_PER_CHANNEL + 2)
        if not videos:
            print("  ⚠️ 無法獲取影片列表")
            continue

        channel_dir = TRANSCRIPTS_DIR / name
        channel_dir.mkdir(exist_ok=True)

        processed = 0
        for vid_id, title in videos:
            if processed >= MAX_VIDEOS_PER_CHANNEL:
                break

            transcript_file = channel_dir / f"{vid_id}.txt"
            if transcript_file.exists():
                stats["skip"] += 1
                continue

            short_title = title[:35] + ("..." if len(title) > 35 else "")
            print(f"  🔄 {short_title} ", end="", flush=True)

            text, method = kd_extract_transcript(vid_id)

            if text and len(text) > 100:
                transcript_file.write_text(text, encoding="utf-8")
                print(f"✅ {method} ({len(text)}字)")
                stats["new"] += 1
                processed += 1
            else:
                print(f"❌ {method}")
                stats["fail"] += 1
                processed += 1

            time.sleep(DELAY_BETWEEN_VIDEOS)

        time.sleep(DELAY_BETWEEN_CHANNELS)

    print(f"\n{'=' * 50}")
    print(f"📊 新增:{stats['new']} 跳過:{stats['skip']} 失敗:{stats['fail']}")
    print("🎉 完成!")


if __name__ == "__main__":
    main()
