#!/usr/bin/env python3
"""
YT 專家字幕下載腳本
使用 youtube-transcript-api 獲取字幕
"""

import os
import sys
import json
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    """從 URL 提取影片 ID"""
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path.startswith('/embed/'):
            return query.path.split('/')[2]
        if query.path.startswith('/v/'):
            return query.path.split('/')[2]
    return None

def format_timestamp(seconds):
    """將秒數轉換為時間戳格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def save_subtitle(video_id, output_path, expert_name):
    """下載並保存字幕"""
    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)

        # 嘗試中文繁體
        try:
            transcript = transcript_list.find_transcript(['zh-Hant', 'zh-TW', 'zh-HK'])
            lang = 'zh-Hant'
        except:
            try:
                transcript = transcript_list.find_transcript(['zh-Hans', 'zh-CN'])
                lang = 'zh-CN'
            except:
                try:
                    transcript = transcript_list.find_transcript(['en'])
                    lang = 'en'
                except:
                    return None, "No transcript available"

        # 獲取字幕內容
        transcript_data = transcript.fetch()

        # 保存為 txt 格式
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"影片 ID: {video_id}\n")
            f.write(f"專家: {expert_name}\n")
            f.write(f"語言: {lang}\n")
            f.write(f"下載時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 50 + "\n\n")

            for entry in transcript_data:
                start = format_timestamp(entry['start'])
                duration = format_timestamp(entry['duration'])
                text = entry['text']
                f.write(f"[{start}] ({duration}s)\n{text}\n\n")

        return output_path, lang

    except Exception as e:
        return None, str(e)

def main():
    if len(sys.argv) < 3:
        print("用法: python3 fetch-subtitle.py <expert_name> <video_url> [output_dir]")
        sys.exit(1)

    expert_name = sys.argv[1]
    video_url = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else f"subtitles/yt-experts/{expert_name}"

    video_id = get_video_id(video_url)
    if not video_id:
        print(f"❌ 無法解析影片 URL: {video_url}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{video_id}.txt")

    path, result = save_subtitle(video_id, output_path, expert_name)

    if path:
        print(f"✅ {expert_name}: {video_id} ({result}) → {path}")
    else:
        print(f"❌ {expert_name}: {video_id} - {result}")

if __name__ == "__main__":
    main()
