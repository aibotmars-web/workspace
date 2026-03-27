#!/usr/bin/env python3
"""
YouTube 专家字幕慢慢抓 - 避免被 rate limit
每抓一个视频休息 3-5 秒
"""
import os
import time
import subprocess
import json
from youtube_transcript_api import YouTubeTranscriptApi

# 频道配置
CHANNELS = {
    "阿銘師": "UC9CqM2LF7m1RFNdpAv4L9qA",
    "胡乃文": "UCYUHZk66njfU1VFwSviXPGQ",
    "柏格醫生": "UCUXi5mmqbvIithAs9AaxEtw",
    "周慕姿": "UCqE8X0c0iKV7yGnWq0g8bCw",  # 假设
    "松明": "UCHNDk7584Q5g7RQCAFj7RFA",
    "Dr. Harvey": "UC36FfchJRvraEqWGb4MUdDA",
    "初日醫學": "UCzOblez4o3mZEkpOeFZdHWQ",
    "泛科學": "UCuHHKbwC0TWjeqxbqdO-N_g",
    "泛科學院": "UC1lA4IY9Z6u12hT6vKHgQ7Q",
}

OUTPUT_DIR = os.path.expanduser("~/knowledge-base")
MAX_VIDEOS_PER_CHANNEL = 10  # 每个频道最多抓10个
WAIT_SECONDS = 3  # 每次请求等待秒数

def get_channel_videos(channel_id, limit=10):
    """用 yt-dlp 获取频道最新视频"""
    cmd = [
        "yt-dlp", "--flat-playlist", 
        "--print", "%(id)s|%(title)s",
        f"https://www.youtube.com/channel/{channel_id}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        videos = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                vid, title = line.split('|', 1)
                videos.append({'id': vid, 'title': title})
                if len(videos) >= limit:
                    break
        return videos
    except Exception as e:
        print(f"  获取视频失败: {e}")
        return []

def fetch_transcript(video_id):
    """抓取字幕"""
    api = YouTubeTranscriptApi()
    languages = ['zh-TW', 'zh-Hant', 'zh', 'en']
    
    for lang in languages:
        try:
            transcript = api.fetch(video_id=video_id, languages=[lang])
            return transcript
        except Exception as e:
            continue
    
    return None

def save_transcript(name, video_id, title, transcript):
    """保存字幕"""
    os.makedirs(f"{OUTPUT_DIR}/{name}", exist_ok=True)
    
    filename = f"{OUTPUT_DIR}/{name}/{video_id}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 频道: {name}\n")
        f.write(f"# 视频: {title}\n")
        f.write(f"# ID: {video_id}\n")
        f.write(f"# 语言: {transcript.language_code}\n")
        f.write(f"# 抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        
        for snippet in transcript.snippets:
            ts = time.strftime('%H:%M:%S', time.gmtime(snippet.start))
            f.write(f"[{ts}] {snippet.text}\n")
    
    return filename

def main():
    print("=" * 60)
    print("YouTube 专家字幕慢慢抓")
    print("=" * 60)
    
    total_videos = 0
    success_count = 0
    
    for name, channel_id in CHANNELS.items():
        print(f"\n📺 处理频道: {name}")
        print("-" * 40)
        
        # 获取视频列表
        videos = get_channel_videos(channel_id, MAX_VIDEOS_PER_CHANNEL)
        print(f"  获取到 {len(videos)} 个视频")
        
        for i, video in enumerate(videos):
            video_id = video['id']
            title = video['title']
            print(f"  [{i+1}/{len(videos)}] {video_id}: {title[:30]}...")
            
            # 抓字幕
            transcript = fetch_transcript(video_id)
            
            if transcript:
                filename = save_transcript(name, video_id, title, transcript)
                print(f"    ✅ 成功! ({len(transcript.snippets)} 条字幕)")
                success_count += 1
            else:
                print(f"    ⚠️ 无字幕或失败")
            
            total_videos += 1
            
            # 慢慢等待，避免被挡
            print(f"    💤 等待 {WAIT_SECONDS} 秒...")
            time.sleep(WAIT_SECONDS)
    
    print("\n" + "=" * 60)
    print(f"完成! 总计: {total_videos} 视频, 成功: {success_count}")
    print(f"保存位置: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
