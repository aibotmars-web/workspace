#!/usr/bin/env python3
"""
YouTube 知識庫同步系統
自動抓取字幕 + AI 生成摘要
"""

import json
import subprocess
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# 設定
DB_PATH = "/Users/marsbot/.openclaw/workspace/knowledge-base/tracker.json"
SUMMARIES_DIR = "/Users/marsbot/.openclaw/workspace/knowledge-base/summaries"

# 頻道清單（9 個專家）
CHANNELS = [
    {"name": "阿銘師x針還傳", "account": "@Dr.HuangAmin"},
    {"name": "胡乃文開講", "account": "@Dr.Hu_talk"},
    {"name": "柏格醫生中文", "account": "@drbergchinese"},
    {"name": "周慕姿放心說", "account": "@muerstalk"},
    {"name": "松明講心理", "account": "@SongMing"},
    {"name": "Dr. Harvey不廢話", "account": "@DrHarveyTalk"},
    {"name": "初日醫學", "account": "@Cofit211"},
    {"name": "泛科學 PanSci", "account": "@PanScitw"},
    {"name": "泛科學院", "account": "@panscischool"},
]

def extract_video_id(url):
    """從 URL 提取影片 ID"""
    parsed = urlparse(url)
    if parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    if parsed.path == '/watch':
        return parse_qs(parsed.query).get('v', [None])[0]
    return None

def get_video_info(url):
    """取得影片標題和日期"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--print", "%(title)s|||%(upload_date)s", url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split('|||')
            return {"title": parts[0], "date": parts[1] if len(parts) > 1 else None}
    except:
        pass
    return {"title": None, "date": None}

def get_transcript(video_url):
    """取得字幕"""
    video_id = extract_video_id(video_url)
    if not video_id:
        return None
    try:
        transcript = YouTubeTranscriptApi().get_transcript(video_id, languages=['zh-Hant', 'zh', 'en'])
        text = ' '.join([t['text'] for t in transcript])
        return text[:15000]  # 限制長度
    except Exception as e:
        print(f"  無法取得字幕: {e}")
        return None

def generate_summary(text):
    """生成 AI 摘要（預留）"""
    # 這裡可以串接 AI API 生成摘要
    # 暫時返回前 500 字
    return text[:500] + "..."

def main():
    print("=" * 60)
    print("YouTube 知識庫同步系統（字幕 + 摘要）")
    print("=" * 60)
    
    import os
    os.makedirs(SUMMARIES_DIR, exist_ok=True)
    
    # 讀取資料庫
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except:
        db = {"channels": [], "update_log": []}
    
    total_new = 0
    
    for channel in CHANNELS:
        print(f"\n[{CHANNELS.index(channel)+1}/{len(CHANNELS)}] 處理: {channel['name']} ({channel['account']})")
        
        # 使用 yt-dlp 取得頻道影片
        try:
            result = subprocess.run(
                ["yt-dlp", "--flat-playlist", "--print", "%(url)s", f"https://www.youtube.com/{channel['account']}"],
                capture_output=True, text=True, timeout=60
            )
            videos = [v for v in result.stdout.strip().split('\n') if v][:10]  # 最新 10 部
        except Exception as e:
            print(f"  ❌ 取得影片失敗: {e}")
            continue
        
        print(f"  📹 發現 {len(videos)} 部影片")
        
        new_count = 0
        for video_url in videos:
            video_id = extract_video_id(video_url)
            info = get_video_info(video_url)
            transcript = get_transcript(video_url)
            
            if transcript:
                summary = generate_summary(transcript)
                filename = f"{channel['account'].replace('@', '')}_{video_id}.json"
                filepath = f"{SUMMARIES_DIR}/{filename}"
                
                data = {
                    "channel": channel['name'],
                    "account": channel['account'],
                    "video_id": video_id,
                    "title": info['title'],
                    "url": video_url,
                    "date": info['date'],
                    "transcript": transcript,
                    "summary": summary,
                    "created_at": datetime.now().isoformat()
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"    ✅ {info['title'][:40]}...")
                new_count += 1
            else:
                print(f"    ❌ 無字幕")
        
        print(f"  ➕ 新增 {new_count} 部")
        total_new += new_count
    
    # 更新資料庫
    db['last_updated'] = datetime.now().isoformat()
    db['update_log'].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "action": "sync_with_summaries",
        "channels_updated": len(CHANNELS),
        "videos_processed": total_new
    })
    
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ 完成！處理 {total_new} 部影片")
    print(f"📁 儲存位置: {SUMMARIES_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
