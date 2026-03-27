#!/usr/bin/env python3
"""
9位健康医学专家YouTube字幕抓取
"""
import os
import time
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi

OUTPUT_DIR = "/Users/marsbot/.openclaw/workspace/knowledge-base/experts/transcripts"

# 正确的频道ID (2026-03-06 更新)
CHANNELS = [
    ("胡乃文开播", "UCYUHZk66njfU1VFwSviXPGQ"),
    ("柏格醫生中文", "UCUXi5mmqbvIithAs9AaxEtw"),
    ("Dr.HuangAmin", "UCRYM7X1WTLZeFHf4uuqkYCQ"),
    ("周慕姿放心說", "UCIhaNRLn4OQDWZJiVvdhl5A"),
    ("松明讲心理", "UCHNDk7584Q5g7RQCAFj7RFA"),
    ("DrHarveyTalk", "UC36FfchJRvraEqWGb4MUdDA"),
    ("Cofit211", "UCQBl-anQy5LactionN4q7J_w"),
    ("泛科學", "UCuHHKbwC0TWjeqxbqdO-N_g"),
    ("泛科學院", "UCJkl5K3K3KbzR3OQ"),
]

def get_channel_videos(channel_id, limit=10):
    """获取频道视频"""
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
    """抓取字幕"""
    api = YouTubeTranscriptApi()
    for lang in ['zh-TW', 'zh-Hant', 'zh', 'en']:
        try:
            transcript = api.fetch(video_id, languages=[lang])
            return transcript
        except:
            continue
    return None

def save_transcript(name, video_id, transcript):
    """保存字幕"""
    channel_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(channel_dir, exist_ok=True)
    filepath = os.path.join(channel_dir, f"{video_id}.txt")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for snippet in transcript.snippets:
            f.write(f"{snippet.text}\n")
    return len(transcript.snippets)

def main():
    print("=" * 50)
    print("9位专家字幕抓取")
    print("=" * 50)
    
    total_ok = 0
    total_skip = 0
    
    for name, cid in CHANNELS:
        print(f"\n📺 {name}")
        videos = get_channel_videos(cid, 5)
        
        if not videos:
            print(f"  ❌ 无法获取视频")
            continue
            
        print(f"  获取到 {len(videos)} 个视频")
        
        for vid in videos:
            transcript = get_transcript(vid)
            if transcript:
                count = save_transcript(name, vid, transcript)
                print(f"  ✅ {vid} ({count}条)")
                total_ok += 1
            else:
                print(f"  ⚠️ {vid} 无字幕")
                total_skip += 1
            time.sleep(2)  # 避免太快
    
    print(f"\n完成! 成功: {total_ok}, 无字幕: {total_skip}")

if __name__ == "__main__":
    main()
