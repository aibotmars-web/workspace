#!/usr/bin/env python3
"""
知識庫同步腳本
每日執行，更新頻道資訊與影片清單
"""

import json
import subprocess
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import os

# 讀取追蹤資料庫
DB_PATH = "/Users/marsbot/.openclaw/workspace/knowledge-base/tracker.json"
SUMMARIES_DIR = "/Users/marsbot/.openclaw/workspace/knowledge-base/experts/summaries"

def load_db():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_video_id(url):
    """從 URL 提取影片 ID"""
    parsed = urlparse(url)
    if parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    if parsed.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [None])[0]
        if '/shorts/' in parsed.path:
            return parsed.path.split('/')[-1]
    return None

def get_channel_videos(url, limit=10):
    """取得頻道最新影片"""
    try:
        # 使用 yt-dlp 取得影片清單
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "%(url)s", url],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            videos = result.stdout.strip().split('\n')
            return [v for v in videos if v][:limit]
    except Exception as e:
        print(f"Error getting videos: {e}")
    return []

def get_video_info(url):
    """取得影片資訊"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--print", "%(title)s|||%(upload_date)s", "--playlist-items", "1", url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split('|||')
            return {
                "title": parts[0] if parts else "Unknown",
                "date": parts[1] if len(parts) > 1 else None
            }
    except:
        pass
    return {"title": "Unknown", "date": None}

def get_transcript(video_url):
    """取得字幕"""
    video_id = extract_video_id(video_url)
    if not video_id:
        return None
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh-Hant', 'zh', 'en'])
        text = ' '.join([t['text'] for t in transcript])
        return text[:5000]  # 限制長度
    except Exception as e:
        print(f"  無法取得字幕: {e}")
        return None

def sync_channel(channel):
    """同步單一頻道"""
    print(f"\n處理: {channel['name']} ({channel['account']})")
    
    # 取得影片清單
    videos = get_channel_videos(channel['url'], limit=20)
    total = len(videos)
    
    print(f"  發現 {total} 部影片")
    
    # 更新總數
    channel['total_videos'] = total
    channel['last_checked'] = datetime.now().strftime("%Y-%m-%d")
    
    # 檢查新影片
    new_count = 0
    for video_url in videos[:5]:  # 只檢查最新的 5 部
        video_id = extract_video_id(video_url)
        exists = any(v.get('video_id') == video_id for v in channel['videos'])
        
        if not exists:
            info = get_video_info(video_url)
            transcript = get_transcript(video_url)
            
            video_entry = {
                "video_id": video_id,
                "url": video_url,
                "title": info['title'],
                "date": info['date'],
                "transcript": transcript,
                "processed": False
            }
            channel['videos'].insert(0, video_entry)
            new_count += 1
            print(f"  新增: {info['title'][:50]}...")
    
    print(f"  新增 {new_count} 部新影片")
    return new_count

def main():
    print("=" * 50)
    print("知識庫同步程式")
    print("=" * 50)
    
    db = load_db()
    total_new = 0
    
    for channel in db['channels']:
        new = sync_channel(channel)
        total_new += new
    
    # 記錄更新
    db['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db['update_log'].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "action": "sync",
        "channels_updated": len(db['channels']),
        "videos_added": total_new
    })
    
    save_db(db)
    
    print("\n" + "=" * 50)
    print(f"同步完成！新增 {total_new} 部影片")
    print(f"資料庫: {DB_PATH}")
    print("=" * 50)

if __name__ == "__main__":
    main()
