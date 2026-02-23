#!/usr/bin/env python3
"""
YT 專家字幕爬取腳本
使用 youtube-transcript-api (無需 OAuth)
"""

import os
import sys
import json
import datetime
from youtube_transcript_api import YouTubeTranscriptApi

# 專家頻道配置 (需要手動獲取影片 ID)
CHANNELS = {
    "阿銘師x銭還傳": {
        "channel_name": "@Dr.HuangAmin",
        "videos": []  # 稍後填入
    },
    "胡乃文開講": {
        "channel_name": "@Dr.Hu_talk",
        "videos": []
    },
    "柏格醫生": {
        "channel_name": "@drbergchinese",
        "videos": []
    },
    "周慕姿放心說": {
        "channel_name": "@muerstalk",
        "videos": []
    },
    "松明講心理": {
        "channel_name": "@SongMing",
        "videos": []
    },
    "Dr.Harvey": {
        "channel_name": "@DrHarveyTalk",
        "videos": []
    },
    "初日醫學": {
        "channel_name": "@Cofit211",
        "videos": []
    },
    "泛科學": {
        "channel_name": "@PanScitw",
        "videos": []
    },
    "泛科學院": {
        "channel_name": "@panscischoo",
        "videos": []
    }
}

def get_video_id(url):
    """從 URL 提取影片 ID"""
    from urllib.parse import urlparse, parse_qs
    
    if not url:
        return None
    
    query = urlparse(url)
    
    if query.hostname == 'youtu.be':
        return query.path[1:]
    
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            params = parse_qs(query.query)
            if 'v' in params:
                return params['v'][0]
        if query.path.startswith('/embed/'):
            return query.path.split('/')[2]
        if query.path.startswith('/v/'):
            return query.path.split('/')[2]
    
    # 如果直接傳入 ID
    if len(url) == 11:
        return url
    
    return None

def format_timestamp(seconds):
    """將秒數轉換為時間戳格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def download_subtitle(video_id, output_dir, expert_name, video_title=""):
    """下載影片字幕"""
    try:
        yta = YouTubeTranscriptApi()
        
        # 嘗試不同語言
        languages = ['zh-Hant', 'zh-TW', 'zh-HK', 'zh-CN', 'zh-Hans', 'en']
        transcript = None
        used_lang = None
        
        transcript_list = yta.list_transcripts(video_id)
        
        for lang in languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                used_lang = lang
                break
            except:
                continue
        
        if not transcript:
            return False, "No transcript available"
        
        # 獲取字幕內容
        transcript_data = transcript.fetch()
        
        # 保存為 txt 格式
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{video_id}.txt")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"影片 ID: {video_id}\n")
            f.write(f"專家: {expert_name}\n")
            f.write(f"頻道: {CHANNELS[expert_name]['channel_name']}\n")
            f.write(f"標題: {video_title}\n")
            f.write(f"語言: {used_lang}\n")
            f.write(f"下載時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 60 + "\n\n")
            
            for entry in transcript_data:
                start = format_timestamp(entry['start'])
                duration = format_timestamp(entry['duration'])
                text = entry['text']
                f.write(f"[{start}] ({duration}s)\n{text}\n\n")
        
        return True, used_lang
    
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("YT 專家字幕爬取任務")
    print(f"開始時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    base_dir = "subtitles/yt-experts"
    os.makedirs(base_dir, exist_ok=True)
    
    # 測試影片 ID - 從頻道獲取
    test_videos = [
        # 泛科學 (Science)
        "5p8fkvP6g4M",  # 測試影片
    ]
    
    total = len(CHANNELS)
    current = 0
    total_subtitles = 0
    
    # 遍歷所有頻道
    for expert_name, config in CHANNELS.items():
        current += 1
        channel_name = config['channel_name']
        
        print(f"[{current}/{total}] {expert_name} ({channel_name})")
        
        # 這裡需要手動輸入影片 ID
        # 實際使用時，應該從頻道頁面獲取
        
        # 測試：嘗試下載一個測試影片
        expert_dir = os.path.join(base_dir, expert_name)
        os.makedirs(expert_dir, exist_ok=True)
        
        # 如果有影片 ID 列表
        for video_id in config['videos']:
            if not video_id:
                continue
                
            success, result = download_subtitle(video_id, expert_dir, expert_name)
            
            if success:
                print(f"  ✓ {video_id} ({result})")
                total_subtitles += 1
            else:
                print(f"  ✗ {video_id} - {result}")
        
        print()
    
    print("=" * 60)
    print("完成!")
    print(f"總計下載: {total_subtitles} 個字幕")
    print(f"輸出目錄: {base_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
