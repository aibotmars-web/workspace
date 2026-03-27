#!/usr/bin/env python3
"""
YouTube 字幕慢速抓取 - 间隔30秒避免被封
"""
import os
import time
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi

OUTPUT_DIR = "/Users/marsbot/.openclaw/workspace/knowledge-base/experts/transcripts"

# 频道列表
CHANNELS = [
    ("阿銘師", "UC9CqM2LF7m1RFNdpAv4L9qA"),
    ("胡乃文开播", "UCYUHZk66njfU1VFwSviXPGQ"),
    ("柏格醫生中文", "UCUXi5mmqbvIithAs9AaxEtw"),
    ("周慕姿放心說", "UCIhaNRLn4OQDWZJiVvdhl5A"),
    ("松明讲心理", "UCHNDk7584Q5g7RQCAFj7RFA"),
    ("DrHarveyTalk", "UC36FfchJRvraEqWGb4MUdDA"),
    ("初日醫學", "UCzOblez4o3mZEkpOeFZdHWQ"),
    ("泛科學", "UCuHHKbwC0TWjeqxbqdO-N_g"),
    ("泛科學院", "UCJkl5K3K3KbzR3OQ"),
]

WAIT_VIDEO = 30  # 每个视频等待30秒
WAIT_CHANNEL = 60  # 每个频道等待60秒

def get_channel_videos(channel_id, limit=10):
    cmd = ["yt-dlp", "--flat-playlist", "--print", "%(id)s", 
           f"https://www.youtube.com/channel/{channel_id}/videos"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        videos = [v.strip() for v in result.stdout.strip().split('\n') if v.strip()]
        return videos[:limit]
    except Exception as e:
        print(f"  获取失败: {e}")
        return []

def get_transcript(video_id):
    api = YouTubeTranscriptApi()
    for lang in ['zh-TW', 'zh-Hant', 'zh', 'en']:
        try:
            transcript = api.fetch(video_id, languages=[lang])
            return transcript
        except:
            continue
    return None

def save_transcript(name, video_id, transcript):
    channel_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(channel_dir, exist_ok=True)
    filepath = os.path.join(channel_dir, f"{video_id}.txt")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for snippet in transcript.snippets:
            f.write(f"{snippet.text}\n")
    return len(transcript.snippets)

def main():
    print("=" * 60)
    print("慢速抓取开始 - 间隔30秒")
    print("=" * 60)
    
    total_ok = 0
    total_skip = 0
    
    for name, cid in CHANNELS:
        print(f"\n📺 {name}")
        videos = get_channel_videos(cid, 10)
        
        if not videos:
            print(f"  ❌ 获取失败")
            time.sleep(WAIT_CHANNEL)
            continue
            
        print(f"  获取到 {len(videos)} 个视频")
        
        for i, vid in enumerate(videos):
            print(f"  [{i+1}] {vid}...", end=" ", flush=True)
            transcript = get_transcript(vid)
            
            if transcript:
                count = save_transcript(name, vid, transcript)
                print(f"✅ ({count}条)")
                total_ok += 1
            else:
                print("⚠️ 无字幕")
                total_skip += 1
            
            print(f"  💤 等待{WAIT_VIDEO}秒...")
            time.sleep(WAIT_VIDEO)
        
        print(f"  💤 频道结束，等待{WAIT_CHANNEL}秒...")
        time.sleep(WAIT_CHANNEL)
    
    print(f"\n完成! 成功: {total_ok}, 无字幕: {total_skip}")

if __name__ == "__main__":
    main()
