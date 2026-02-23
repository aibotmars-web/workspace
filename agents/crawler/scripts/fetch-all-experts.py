#!/usr/bin/env python3
"""
YT 專家字幕批量下載腳本
使用 youtube-transcript-api 和 requests 獲取頻道影片
"""

import os
import sys
import json
import time
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
import requests

# 專家頻道配置
CHANNELS = {
    "阿銘師x銭還傳": "UC9CqM2LF7m1RFNdpAv4L9qA",
    "胡乃文開講": "UCwLjzp5s2kPCsdTa3oWgkkA",
    "柏格醫生": "UC9CqM2LF7m1RFNdpAv4L9qA",  # 待確認
    "周慕姿放心說": "UCmuerstalk",
    "松明講心理": "UCsongming",
    "Dr.Harvey": "UCdharvey",
    "初日醫學": "UCcofit211",
    "泛科學": "UCcBRuj-2Tp-3T3Q1lvE7q8Q",
    "泛科學院": "UCpanscischoo",
}

def get_channel_videos(channel_id, max_videos=10):
    """使用 YouTube API 獲取頻道影片列表"""
    # 使用 oEmbed API 獲取頻道資訊
    url = f"https://www.youtube.com/channel/{channel_id}/videos"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # 從 HTML 中提取影片 ID
            import re
            video_ids = re.findall(r'"videoId":"([^"]+)"', response.text)
            return list(set(video_ids))[:max_videos]
    except Exception as e:
        print(f"  警告: 無法獲取頻道影片列表: {e}")

    return []

def format_timestamp(seconds):
    """將秒數轉換為時間戳格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def download_subtitle(video_id, output_dir, expert_name):
    """下載影片字幕"""
    try:
        yta = YouTubeTranscriptApi()
        transcript_list = yta.list(video_id)

        # 嘗試不同語言
        languages = ['zh-Hant', 'zh-TW', 'zh-HK', 'zh-Hans', 'zh-CN', 'en']
        transcript = None
        used_lang = None

        for lang in languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                used_lang = lang
                break
            except:
                continue

        if not transcript:
            return False, "No transcript"

        # 獲取字幕內容
        transcript_data = transcript.fetch()

        # 保存為 txt 格式
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{video_id}.txt")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"影片 ID: {video_id}\n")
            f.write(f"專家: {expert_name}\n")
            f.write(f"語言: {used_lang}\n")
            f.write(f"下載時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 50 + "\n\n")

            for entry in transcript_data:
                start = format_timestamp(entry['start'])
                duration = format_timestamp(entry['duration'])
                text = entry['text']
                f.write(f"[{start}] ({duration}s)\n{text}\n\n")

        return True, used_lang

    except Exception as e:
        return False, str(e)

def main():
    base_dir = "subtitles/yt-experts"
    log_dir = "logs"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"yt-experts-{datetime.now().strftime('%Y-%m-%d')}.log")

    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"YT 專家字幕爬取任務\n")
        log.write(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write("=" * 60 + "\n\n")

        total = len(CHANNELS)
        current = 0
        success_count = 0
        subtitle_count = 0

        for expert_name, channel_id in CHANNELS.items():
            current += 1
            print(f"[{current}/{total}] 處理: {expert_name}")

            output_dir = os.path.join(base_dir, expert_name)

            # 獲取影片列表
            video_ids = get_channel_videos(channel_id, max_videos=5)
            print(f"  發現 {len(video_ids)} 部影片")

            if not video_ids:
                # 使用測試影片 ID
                video_ids = ["example1", "example2"]

            for video_id in video_ids:
                if video_id == "example1":
                    continue  # 跳過測試 ID

                success, result = download_subtitle(video_id, output_dir, expert_name)

                if success:
                    print(f"    ✓ {video_id} ({result})")
                    subtitle_count += 1
                    log.write(f"✓ {expert_name}: {video_id} ({result})\n")
                else:
                    print(f"    ✗ {video_id} - {result}")
                    log.write(f"✗ {expert_name}: {video_id} - {result}\n")

                time.sleep(1)  # 避免請求過快

            success_count += 1
            log.write("\n")

        log.write("=" * 60 + "\n")
        log.write(f"完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"處理頻道: {success_count}/{total}\n")
        log.write(f"下載字幕: {subtitle_count} 部\n")
        log.write(f"輸出目錄: {base_dir}\n")

    print(f"\n完成! 結果已保存到: {log_file}")

if __name__ == "__main__":
    main()
