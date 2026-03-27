#!/usr/bin/env python3
"""
YouTube 专家字幕慢慢抓 - 安全版
每次请求等待 15 秒，避免被 IP 封禁
"""
import os
import time
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi

OUTPUT_DIR = "/Users/marsbot/knowledge-base"

# 频道列表（只抓有中文字幕的）
CHANNELS = [
    ("泛科學", "UCuHHKbwC0TWjeqxbqdO-N_g"),
    ("Dr. Harvey", "UC36FfchJRvraEqWGb4MUdDA"),
]

WAIT_SECONDS = 15  # 每次请求等待15秒（安全）
BATCH_WAIT = 60   # 每批（10个）后等待60秒

def get_channel_videos(channel_id, limit=10):
    """获取频道视频列表"""
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
    filepath = f"{OUTPUT_DIR}/{name}/{video_id}.txt"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 频道: {name}\n")
        f.write(f"# 视频: {title}\n")
        f.write(f"# ID: {video_id}\n")
        f.write(f"# 语言: {transcript.language_code}\n")
        f.write(f"# 抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        
        for snippet in transcript.snippets:
            ts = time.strftime('%H:%M:%S', time.gmtime(snippet.start))
            f.write(f"[{ts}] {snippet.text}\n")
    
    return filepath

def main():
    print("=" * 60)
    print("YouTube 字幕慢慢抓 - 安全版")
    print(f"每次等待: {WAIT_SECONDS}秒, 每批等待: {BATCH_WAIT}秒")
    print("=" * 60)
    
    total_success = 0
    total_fail = 0
    
    for name, cid in CHANNELS:
        print(f"\n📺 频道: {name}")
        print("-" * 40)
        
        videos = get_channel_videos(cid, 10)
        print(f"  获取到 {len(videos)} 个视频")
        
        for i, video in enumerate(videos):
            vid = video['id']
            title = video['title'][:30]
            
            print(f"  [{i+1}/10] {vid}: {title}...", end=" ")
            
            transcript = fetch_transcript(vid)
            
            if transcript:
                save_transcript(name, vid, video['title'], transcript)
                print(f"✅ ({len(transcript.snippets)} 条)")
                total_success += 1
            else:
                print("⚠️ 无字幕")
                total_fail += 1
            
            # 每批后等待
            if (i + 1) % 10 == 0 and i < len(videos) - 1:
                print(f"  💤 批次结束，等待 {BATCH_WAIT} 秒...")
                time.sleep(BATCH_WAIT)
            else:
                print(f"  💤 等待 {WAIT_SECONDS} 秒...")
                time.sleep(WAIT_SECONDS)
    
    print("\n" + "=" * 60)
    print(f"🎉 完成! 成功: {total_success}, 失败: {total_fail}")
    print("=" * 60)

if __name__ == "__main__":
    main()
