#!/usr/bin/env python3
"""
YouTube 专家字幕慢慢抓 - 随机等待版
随机等待 10-25 秒，避免被检测
"""
import os
import time
import random
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi

OUTPUT_DIR = "/Users/marsbot/knowledge-base"

CHANNELS = [
    ("泛科學", "UCuHHKbwC0TWjeqxbqdO-N_g"),
    ("Dr. Harvey", "UC36FfchJRvraEqWGb4MUdDA"),
]

def random_wait():
    """随机等待 10-25 秒"""
    wait = random.randint(10, 25)
    print(f"  💤 随机等待 {wait} 秒...")
    time.sleep(wait)

def get_channel_videos(channel_id, limit=10):
    cmd = ["yt-dlp", "--flat-playlist", "--print", "%(id)s|%(title)s", 
           f"https://www.youtube.com/channel/{channel_id}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        videos = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                vid, title = line.split('|', 1)
                videos.append({'id': vid, 'title': title})
                if len(videos) >= limit:
                    break
        return videos
    except Exception as e:
        print(f"  获取失败: {e}")
        return []

def fetch_transcript(video_id):
    api = YouTubeTranscriptApi()
    for lang in ['zh-TW', 'zh-Hant', 'zh', 'en']:
        try:
            return api.fetch(video_id=video_id, languages=[lang])
        except:
            continue
    return None

def save_transcript(name, video_id, title, transcript):
    os.makedirs(f"{OUTPUT_DIR}/{name}", exist_ok=True)
    filepath = f"{OUTPUT_DIR}/{name}/{video_id}.txt"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 频道: {name}\n# 视频: {title}\n# ID: {video_id}\n")
        f.write(f"# 语言: {transcript.language_code}\n")
        f.write(f"# 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        for snippet in transcript.snippets:
            ts = time.strftime('%H:%M:%S', time.gmtime(snippet.start))
            f.write(f"[{ts}] {snippet.text}\n")
    return filepath

def main():
    print("=" * 60)
    print("YouTube 字幕随机等待版")
    print("每次随机等待: 10-25 秒")
    print("=" * 60)
    
    success = fail = 0
    
    for name, cid in CHANNELS:
        print(f"\n📺 {name}")
        videos = get_channel_videos(cid, 10)
        
        for i, video in enumerate(videos):
            print(f"  [{i+1}/10] {video['id']}: {video['title'][:25]}...", end=" ")
            
            transcript = fetch_transcript(video['id'])
            if transcript:
                save_transcript(name, video['id'], video['title'], transcript)
                print(f"✅ ({len(transcript.snippets)}条)")
                success += 1
            else:
                print("⚠️")
                fail += 1
            
            random_wait()
    
    print(f"\n🎉 完成! 成功: {success}, 失败: {fail}")

if __name__ == "__main__":
    main()
