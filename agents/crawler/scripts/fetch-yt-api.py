#!/usr/bin/env python3
"""
YT 專家字幕爬取腳本
使用 Google OAuth + YouTube Data API
"""

import os
import json
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 專家頻道配置
CHANNELS = {
    "阿銘師x銭還傳": {
        "channel_id": "UC9CqM2LF7m1RFNdpAv4L9qA",
        "playlist_id": "UU9CqM2LF7m1RFNdpAv4L9qA"  # 上傳影片播放清單
    },
    "胡乃文開講": {
        "channel_id": "UCwLjzp5s2kPCsdTa3oWgkkA",
        "playlist_id": "UUwLjzp5s2kPCsdTa3oWgkkA"
    },
    "柏格醫生": {
        "channel_id": "UC8-Th3bY9b2a1c1a1c1a1c1",
        "playlist_id": "UU8-Th3bY9b2a1c1a1c1a1c1"
    },
    "周慕姿放心說": {
        "channel_id": "UCmuerstalk",
        "playlist_id": "UUmuerstalk"
    },
    "松明講心理": {
        "channel_id": "UCsongming",
        "playlist_id": "UUsongming"
    },
    "Dr.Harvey": {
        "channel_id": "UCdharvey",
        "playlist_id": "UUdharvey"
    },
    "初日醫學": {
        "channel_id": "UCCofit211",
        "playlist_id": "UUCofit211"
    },
    "泛科學": {
        "channel_id": "UCcBRuj-2Tp-3T3Q1lvE7q8Q",
        "playlist_id": "UUcBRuj-2Tp-3T3Q1lvE7q8Q"
    },
    "泛科學院": {
        "channel_id": "UCpanscischoo",
        "playlist_id": "UUpanscischoo"
    }
}

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

TOKEN_FILE = "agent/token.json"
CREDS_FILE = "agent/client_secrets.json"

def get_youtube_service():
    """建立 YouTube API 服務"""
    creds = None
    
    # 載入現有 token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # 如果沒有有效憑證，嘗試 OAuth 流程
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 檢查是否有 client_config
            if os.path.exists(CREDS_FILE):
                flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
                creds = flow.run_local_server(port=8080)
        
        # 保存憑證
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('youtube', 'v3', credentials=creds)

def get_channel_uploads(youtube, channel_id, max_results=10):
    """獲取頻道上傳影片"""
    try:
        # 從頻道 ID 取得上傳播放清單 ID
        response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        
        if 'items' in response and len(response['items']) > 0:
            playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # 獲取播放清單中的影片
            videos_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=max_results
            ).execute()
            
            videos = []
            for item in videos_response.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                title = item['snippet']['title']
                published_at = item['snippet']['publishedAt']
                videos.append({
                    'id': video_id,
                    'title': title,
                    'published_at': published_at
                })
            
            return videos
        
    except HttpError as e:
        print(f"  錯誤: {e}")
    
    return []

def get_video_subtitles(youtube, video_id):
    """獲取影片字幕"""
    try:
        # 嘗試獲取字幕追蹤清單
        caption_response = youtube.captions().list(
            part='snippet',
            videoId=video_id
        ).execute()
        
        captions = []
        for item in caption_response.get('items', []):
            captions.append({
                'id': item['id'],
                'language': item['snippet']['language'],
                'name': item['snippet'].get('name', '')
            })
        
        return captions
    
    except HttpError as e:
        if e.resp.status != 403:  # 字幕不可用是正常的
            print(f"  字幕錯誤: {e}")
    
    return []

def download_caption(youtube, caption_id, output_path):
    """下載字幕"""
    try:
        from googleapiclient.http import MediaIoBaseDownload
        import io
        
        request = youtube.captions().download(
            id=caption_id,
            tfmt='srt'  # SRT 格式
        )
        
        fh = io.FileIO(output_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        return True
    
    except Exception as e:
        print(f"  下載錯誤: {e}")
        return False

def main():
    print("=" * 60)
    print("YT 專家字幕爬取任務")
    print(f"開始時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    base_dir = "subtitles/yt-experts"
    os.makedirs(base_dir, exist_ok=True)
    
    try:
        youtube = get_youtube_service()
        print("✓ YouTube API 連線成功\n")
        
        total = len(CHANNELS)
        current = 0
        total_subtitles = 0
        
        for expert_name, config in CHANNELS.items():
            current += 1
            channel_id = config['channel_id']
            
            print(f"[{current}/{total}] {expert_name}")
            
            # 獲取影片列表
            videos = get_channel_uploads(youtube, channel_id, max_results=5)
            print(f"  發現 {len(videos)} 部影片")
            
            expert_dir = os.path.join(base_dir, expert_name)
            os.makedirs(expert_dir, exist_ok=True)
            
            subtitle_count = 0
            
            for video in videos:
                video_id = video['id']
                video_title = video['title']
                
                # 獲取字幕
                captions = get_video_subtitles(youtube, video_id)
                
                if captions:
                    print(f"    📝 {video_id}: {video_title[:30]}...")
                    
                    for cap in captions:
                        if cap['language'] in ['zh-TW', 'zh-Hant', 'zh-Hans', 'en']:
                            output_file = os.path.join(expert_dir, f"{video_id}_{cap['language']}.srt")
                            
                            if download_caption(youtube, cap['id'], output_file):
                                print(f"      ✓ {cap['language']} 字幕下載成功")
                                subtitle_count += 1
                                total_subtitles += 1
                                break
                else:
                    print(f"    ✗ {video_id}: 無字幕")
            
            print()
        
        print("=" * 60)
        print("完成!")
        print(f"總計下載: {total_subtitles} 個字幕")
        print(f"輸出目錄: {base_dir}")
        print("=" * 60)
        
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
