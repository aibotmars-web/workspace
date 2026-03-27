#!/usr/bin/env python3
"""
YT 專家頻道爬蟲 v4.1
使用 Google API 或 yt-dlp 備用
顯示影片總數與進度百分比
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Google API (可選)
try:
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

import yt_dlp

# 專家頻道列表
CHANNELS = {
    "Dr.HuangAmin": {"name": "阿銘師x銭還傳", "url": "https://www.youtube.com/@Dr.HuangAmin"},
    "Dr.Hu_talk": {"name": "胡乃文開講", "url": "https://www.youtube.com/@Dr.Hu_talk"},
    "drbergchinese": {"name": "柏格醫生", "url": "https://www.youtube.com/@drbergchinese"},
    "muerstalk": {"name": "周慕姿放心說", "url": "https://www.youtube.com/@muerstalk"},
    "SongMing": {"name": "松明講心理", "url": "https://www.youtube.com/@SongMing"},
    "DrHarveyTalk": {"name": "Dr. Harvey", "url": "https://www.youtube.com/@DrHarveyTalk"},
    "Cofit211": {"name": "初日醫學", "url": "https://www.youtube.com/@Cofit211"},
    "PanScitw": {"name": "泛科學", "url": "https://www.youtube.com/@PanScitw"},
    "panscischool": {"name": "泛科學院", "url": "https://www.youtube.com/@panscischool"}
}

OUTPUT_DIR = Path("/Users/marsbot/.openclaw/workspace/agents/assistant")
DATA_DIR = OUTPUT_DIR / "yt_data"
DATA_DIR.mkdir(exist_ok=True)

def get_youtube_service():
    """建立 YouTube API 服務"""
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        print("⚠️ 未設定 YOUTUBE_API_KEY，將使用 yt-dlp")
        return None
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        return youtube
    except Exception as e:
        print(f"❌ API 連線失敗: {e}")
        return None

def get_channel_stats_google(youtube, channel_id):
    """用 Google API 取得頻道統計"""
    try:
        response = youtube.channels().list(
            part='statistics,snippet', id=channel_id
        ).execute()
        if 'items' in response and len(response['items']) > 0:
            item = response['items'][0]
            stats = item.get('statistics', {})
            return {
                'title': item['snippet']['title'],
                'subscriber_count': stats.get('subscriberCount', '0'),
                'video_count': stats.get('videoCount', '0')
            }
    except Exception as e:
        pass
    return None

def get_channel_stats_ydlp(channel_url):
    """用 yt-dlp 取得頻道統計"""
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            return {
                'title': info.get('title', ''),
                'subscriber_count': str(info.get('subscriber_count', 0)),
                'video_count': str(info.get('playlist_count', 0))
            }
    except Exception as e:
        return None

def get_channel_videos_google(youtube, channel_id, max_results=15):
    """用 Google API 取得影片列表"""
    try:
        response = youtube.channels().list(
            part='contentDetails', id=channel_id
        ).execute()
        if 'items' not in response or len(response['items']) == 0:
            return []
        
        uploads_playlist = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        videos_response = youtube.playlistItems().list(
            part='snippet', playlistId=uploads_playlist, maxResults=max_results
        ).execute()
        
        videos = []
        for item in videos_response.get('items', []):
            snippet = item['snippet']
            if 'shorts' in snippet.get('title', '').lower():
                continue
            videos.append({
                'id': snippet['resourceId']['videoId'],
                'title': snippet['title'],
                'url': f"https://www.youtube.com/watch?v={snippet['resourceId']['videoId']}"
            })
        return videos
    except Exception:
        return []

def get_channel_videos_ydlp(channel_url, max_results=15):
    """用 yt-dlp 取得影片列表（只取公開影片）"""
    try:
        ydl_opts = {
            'quiet': True, 'no_warnings': True, 
            'extract_flat': 'in_playlist', 
            'playlistend': max_results * 3,
            'get': ['id', 'title', 'duration', 'availability']
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            
            videos = []
            if 'entries' in info:
                for entry in info['entries']:
                    if not entry or not entry.get('id'):
                        continue
                    
                    # 跳過 Shorts
                    title = entry.get('title', '').lower()
                    if 'shorts' in title:
                        continue
                    
                    # 檢查是否為公開影片（availability 為空或 "NA" 表示公開）
                    availability = entry.get('availability', '')
                    is_subscriber_only = (
                        availability == 'subscriber_only' or
                        'subscriber_only' in str(availability).lower() or
                        'private' in str(availability).lower()
                    )
                    if is_subscriber_only:
                        continue  # 跳過會員限定影片
                    
                    duration = entry.get('duration', 0) or 0
                    if duration and duration < 60:
                        continue
                    videos.append({
                        'id': entry['id'],
                        'title': entry['title'],
                        'url': f"https://www.youtube.com/watch?v={entry['id']}",
                        'duration': duration,
                        'availability': availability
                    })
            return videos[:max_results]
    except Exception:
        return []

def print_progress_bar(current, total, prefix='', suffix='', length=25):
    """顯示進度條"""
    if total == 0:
        return
    percent = 100 * current / total
    filled = int(length * current // total)
    bar = '█' * filled + '░' * (length - filled)
    print(f'\r{prefix} │{bar}│ {percent:5.1f}% {suffix}', end='', flush=True)
    if current == total:
        print()

def crawl_channel(channel_id, youtube):
    """爬取單一頻道"""
    channel_info = CHANNELS[channel_id]
    print(f"\n{'─'*60}")
    print(f"🔍 {channel_info['name']}")
    print(f"{'─'*60}")
    
    # 取得頻道統計
    stats = None
    if youtube:
        stats = get_channel_stats_google(youtube, channel_id)
    
    if not stats:
        stats = get_channel_stats_ydlp(channel_info['url'])
    
    if stats:
        sub_count = int(stats.get('subscriber_count', 0))
        vid_count = int(stats.get('video_count', 0))
        print(f"📺 訂閱：{sub_count:,} | 影片總數：{vid_count:,}")
    else:
        print("⚠️ 無法取得頻道統計")
    
    # 取得影片列表
    videos = []
    if youtube:
        videos = get_channel_videos_google(youtube, channel_id)
    
    if not videos:
        videos = get_channel_videos_ydlp(channel_info['url'])
    
    print(f"📹 取得 {len(videos)} 部最新長影片\n")
    
    if not videos:
        return None
    
    results = {
        "channel_id": channel_id,
        "channel_name": channel_info['name'],
        "url": channel_info['url'],
        "crawl_time": datetime.now().isoformat(),
        "total_channel_videos": int(stats['video_count']) if stats else 0,
        "videos": []
    }
    
    # 顯示進度爬取
    for i, video in enumerate(videos, 1):
        duration = video.get('duration', 0)
        dur_str = f"{duration//60}分鐘" if duration else ""
        title_short = video['title'][:18] + "..." if len(video['title']) > 18 else video['title']
        print_progress_bar(i, len(videos), suffix=f"{title_short} {dur_str}")
        
        results["videos"].append({
            "id": video['id'],
            "title": video['title'],
            "url": video['url'],
            "duration": video.get('duration', 0),
            "has_transcript": None
        })
    
    return results

def generate_report(all_results, all_stats):
    """生成更新日誌"""
    total_videos = sum(int(s['video_count']) if s else 0 for s in all_stats.values())
    
    report = f"""# YT 專家更新日誌

## {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

---

## 📊 頻道總覽

"""
    for channel_id, stats in all_stats.items():
        if stats:
            name = CHANNELS[channel_id]['name']
            sub = int(stats.get('subscriber_count', 0))
            vid = int(stats.get('video_count', 0))
            report += f"### {name}\n"
            report += f"- 訂閱數：{sub:,}\n- 影片總數：{vid:,}\n\n"
    
    report += f"""
---

## 📈 更新統計

- **監控頻道：** {len(all_results)} 個
- **頻道影片總數：** {total_videos:,} 部
- **本次更新：** {sum(len(r['videos']) if r else 0 for r in all_results)} 部
- **更新時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🎬 今日更新影片

"""
    
    for result in all_results:
        if not result:
            continue
        report += f"### 【{result['channel_name']}】\n"
        for video in result['videos']:
            dur = video.get('duration', 0)
            dur_str = f"{dur//60}分鐘" if dur else ""
            report += f"- **{video['title']}**\n"
            report += f"  - 📎 {video['url']}\n"
            report += f"  - ⏱️ {dur_str}\n\n"
    
    return report

def main():
    print("🚀 YT 專家頻道爬蟲 v4.1")
    print("="*60)
    
    # 建立 API 服務
    youtube = get_youtube_service() if GOOGLE_API_AVAILABLE else None
    
    all_results = []
    all_stats = {}
    
    total_channels = len(CHANNELS)
    
    for i, channel_id in enumerate(CHANNELS.keys(), 1):
        print(f"\n[{i}/{total_channels}] 處理中...")
        
        # 取得統計
        if youtube:
            stats = get_channel_stats_google(youtube, channel_id)
        else:
            stats = get_channel_stats_ydlp(CHANNELS[channel_id]['url'])
        all_stats[channel_id] = stats
        
        # 爬取影片
        result = crawl_channel(channel_id, youtube)
        if result:
            all_results.append(result)
    
    if not all_results:
        print("\n⚠️ 沒有爬取到任何影片")
        return
    
    # 儲存 JSON
    json_file = DATA_DIR / "experts_latest.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "crawl_time": datetime.now().isoformat(),
            "channels": all_results,
            "stats": all_stats
        }, f, ensure_ascii=False, indent=2)
    print(f"\n💾 資料已儲存: {json_file}")
    
    # 報告
    report = generate_report(all_results, all_stats)
    log_file = DATA_DIR / "yt-updates.log"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📝 更新日誌: {log_file}")
    
    # 摘要
    total_videos = sum(int(s['video_count']) if s else 0 for s in all_stats.values())
    print(f"\n✅ 爬取完成！")
    print(f"   頻道數：{len(all_results)}")
    print(f"   頻道影片總數：{total_videos:,}")
    print(f"   今日更新：{sum(len(r['videos']) for r in all_results)}")

if __name__ == "__main__":
    main()
