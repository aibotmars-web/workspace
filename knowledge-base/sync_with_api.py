#!/usr/bin/env python3
"""
YouTube 專家知識庫同步工具
使用 YouTube Data API v3
"""

import os
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# API 設定
API_KEY = "AQ.Ab8RN6LvAy8t_I_wSyhaBlCJWg3iPXXOgJuyQB0iB0HtQ_oWCQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# 頻道清單（對照 Google Sheets）
CHANNELS = [
    {"name": "阿銘師x針還傳", "account": "@Dr.HuangAmin", "category": "中醫食療"},
    {"name": "胡乃文開講", "account": "@Dr.Hu_talk", "category": "傳統中醫"},
    {"name": "柏格醫生中文", "account": "@drbergchinese", "category": "功能醫學"},
    {"name": "周慕姿放心說", "account": "@muerstalk", "category": "心理諮商"},
    {"name": "松明講心理", "account": "@SongMing", "category": "行為心理"},
    {"name": "Dr. Harvey不廢話", "account": "@DrHarveyTalk", "category": "商業顧問"},
    {"name": "初日醫學", "account": "@Cofit211", "category": "代謝減重"},
    {"name": "泛科學 PanSci", "account": "@PanScitw", "category": "科學科普"},
    {"name": "泛科學院", "account": "@panscischool", "category": "AI工具"},
]

DB_PATH = "/Users/marsbot/.openclaw/workspace/knowledge-base/tracker.json"

def get_youtube_service():
    """建立 YouTube API 服務"""
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def get_channel_id(youtube, account):
    """取得頻道 ID"""
    try:
        # 移除 @ 符號
        username = account.replace("@", "")
        search_response = youtube.search().list(
            part="id",
            q=username,
            type="channel",
            maxResults=1
        ).execute()
        
        if search_response.get("items"):
            return search_response["items"][0]["id"]["channelId"]
    except HttpError as e:
        print(f"Error searching channel {account}: {e}")
    return None

def get_channel_stats(youtube, channel_id):
    """取得頻道統計"""
    try:
        response = youtube.channels().list(
            part="statistics,snippet,contentDetails",
            id=channel_id
        ).execute()
        
        if response.get("items"):
            item = response["items"][0]
            return {
                "title": item["snippet"]["title"],
                "total_videos": int(item["statistics"]["videoCount"]),
                "subscriber_count": item["statistics"].get("subscriberCount", "N/A"),
                "upload_playlist": item["contentDetails"]["relatedPlaylists"]["uploads"],
                "last_updated": datetime.now().isoformat()
            }
    except HttpError as e:
        print(f"Error getting channel stats: {e}")
    return None

def get_latest_videos(youtube, upload_playlist_id, max_results=10):
    """取得最新影片清單"""
    try:
        response = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=upload_playlist_id,
            maxResults=max_results
        ).execute()
        
        videos = []
        for item in response.get("items", []):
            video_id = item["contentDetails"]["videoId"]
            snippet = item["snippet"]
            videos.append({
                "video_id": video_id,
                "title": snippet["title"],
                "published_at": snippet["publishedAt"],
                "thumbnail": snippet["thumbnails"]["default"]["url"]
            })
        return videos
    except HttpError as e:
        print(f"Error getting playlist items: {e}")
    return []

def get_video_transcript(video_id):
    """取得影片字幕"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh-Hant', 'zh', 'en'])
        text = ' '.join([t['text'] for t in transcript])
        return text[:10000]  # 限制長度
    except Exception as e:
        print(f"  無法取得字幕: {e}")
        return None

def main():
    """主程式"""
    print("=" * 60)
    print("YouTube 專家知識庫同步工具")
    print("=" * 60)
    
    # 建立 API 服務
    youtube = get_youtube_service()
    
    # 讀取現有資料庫
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    total_new = 0
    
    for i, channel in enumerate(CHANNELS, 1):
        print(f"\n[{i}/{len(CHANNELS)}] 處理: {channel['name']} ({channel['account']})")
        
        # 取得頻道 ID
        channel_id = get_channel_id(youtube, channel["account"])
        if not channel_id:
            print(f"  ❌ 無法找到頻道: {channel['account']}")
            continue
        
        # 取得頻道統計
        stats = get_channel_stats(youtube, channel_id)
        if not stats:
            print(f"  ❌ 無法取得統計資料")
            continue
        
        print(f"  ✅ 頻道: {stats['title']}")
        print(f"  📹 總影片數: {stats['total_videos']}")
        print(f"  👥 訂閱數: {stats['subscriber_count']}")
        
        # 取得最新影片
        latest_videos = get_latest_videos(youtube, stats['upload_playlist'], max_results=10)
        print(f"  🆕 最新影片數: {len(latest_videos)}")
        
        # 取得字幕（只取最新的 3 部）
        for j, video in enumerate(latest_videos[:3]):
            print(f"    [{j+1}] {video['title'][:40]}...")
            transcript = get_video_transcript(video['video_id'])
            if transcript:
                print(f"        ✅ 字幕長度: {len(transcript)} 字元")
            else:
                print(f"        ❌ 無字幕")
        
        # 更新資料庫
        for ch in db['channels']:
            if ch['account'] == channel['account']:
                ch['total_videos'] = stats['total_videos']
                ch['last_checked'] = stats['last_updated']
                ch['channel_id'] = channel_id
                break
        
        total_new += len(latest_videos)
    
    # 儲存資料庫
    db['last_updated'] = datetime.now().isoformat()
    db['update_log'].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "action": "sync_with_api",
        "channels_updated": len(CHANNELS),
        "videos_found": total_new,
        "api_key_set": True
    })
    
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"同步完成！")
    print(f"更新頻道數: {len(CHANNELS)}")
    print(f"發現影片數: {total_new}")
    print(f"資料庫: {DB_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()
