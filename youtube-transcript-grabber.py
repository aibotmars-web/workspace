#!/usr/bin/env python3
"""
抓取 YouTube 頻道影片字幕
只抓文字，不下載影片
"""

import sys
import json
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    """從 URL 提取影片 ID"""
    parsed = urlparse(url)
    if parsed.hostname in ['youtu.be']:
        return parsed.path[1:]
    if parsed.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [None])[0]
        if parsed.path.startswith('/embed/'):
            return parsed.path.split('/')[-1]
        if parsed.path.startswith('/v/'):
            return parsed.path.split('/')[-1]
    return None

def get_transcript(video_id, language='zh-Hant'):
    """取得字幕"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        text = ' '.join([t['text'] for t in transcript])
        return text
    except Exception as e:
        print(f"無法取得字幕: {e}")
        return None

# 測試
test_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
video_id = extract_video_id(test_video)
print(f"測試影片 ID: {video_id}")

# 實際頻道列表（從 MEMORY.md 來的）
channels = {
    "Dr.HuangAmin": "阿銘師x針還傳",
    "Dr.Hu_talk": "胡乃文開講",
    "drbergchinese": "柏格醫生中文",
    "muerstalk": "周慕姿放心說",
    "SongMing": "松明講心理",
    "DrHarveyTalk": "Dr. Harvey不廢話",
    "Cofit211": "初日醫學",
    "PanScitw": "泛科學",
    "panscischool": "泛科學院"
}

print(f"載入了 {len(channels)} 個頻道設定")
