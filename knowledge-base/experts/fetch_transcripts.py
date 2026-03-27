#!/usr/bin/env python3
"""
批量抓取 YouTube 频道影片字幕
"""

import json
import os
import time
from youtube_transcript_api import YouTubeTranscriptApi

# 频道列表 (名称, URL/ID)
CHANNELS = [
    ("胡乃文开播", "UCYUHZk66njfU1VFwSviXPGQ"),
    ("柏格醫生中文", "UCUXi5mmqbvIithAs9AaxEtw"),
    ("Dr.HuangAmin", "UCW-wK8J5MmN0l4I4S4x3IBA"),
    ("周慕姿放心說", "UCmJqB3KqK5ZlE禽KbzR3OQ"),
    ("松明讲心理", "UCkY5aS9J5QK3KbzR3OQ"),
    ("DrHarveyTalk", "UCZgk7G3K5K3KbzR3OQ"),
    ("Cofit211", "UCGk5K3K5K3KbzR3OQ"),
    ("泛科學", "UCuP7mT4K5K3KbzR3OQ"),
    ("泛科學院", "UCJkl5K3K3KbzR3OQ"),
]

OUTPUT_DIR = "/Users/marsbot/.openclaw/workspace/knowledge-base/experts/transcripts"

def get_channel_videos(channel_id_or_url, limit=10):
    """用 yt-dlp 获取频道最新影片"""
    import subprocess
    cmd = [
        "yt-dlp", "--flat-playlist", 
        "--print", "%(id)s",
        f"https://www.youtube.com/channel/{channel_id_or_url}/videos"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        videos = result.stdout.strip().split('\n')[:limit]
        return videos
    except Exception as e:
        print(f"获取视频失败: {e}")
        return []

def get_transcript(video_id):
    """抓取字幕"""
    api = YouTubeTranscriptApi()
    for lang in ['zh-TW', 'zh', 'en']:
        try:
            transcript = api.fetch(video_id, languages=[lang])
            text = ' '.join([t.text for t in transcript])
            return text, lang
        except:
            continue
    return None, None

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    api = YouTubeTranscriptApi()
    
    for name, channel_id in CHANNELS:
        print(f"\n=== 处理频道: {name} ===")
        
        # 获取视频列表
        videos = get_channel_videos(channel_id, limit=5)
        if not videos:
            print(f"  无法获取视频列表")
            continue
            
        print(f"  获取到 {len(videos)} 个视频")
        
        channel_dir = os.path.join(OUTPUT_DIR, name)
        os.makedirs(channel_dir, exist_ok=True)
        
        for i, video_id in enumerate(videos):
            print(f"  [{i+1}] 抓取 {video_id}...", end=" ")
            transcript, lang = get_transcript(video_id)
            
            if transcript:
                # 保存字幕
                filepath = os.path.join(channel_dir, f"{video_id}.txt")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                print(f"OK! ({len(transcript)} 字, {lang})")
            else:
                print("无字幕")
            
            time.sleep(1)  # 避免请求太快
    
    print("\n完成!")

if __name__ == "__main__":
    main()
