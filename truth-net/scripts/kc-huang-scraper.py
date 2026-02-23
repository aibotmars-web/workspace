#!/usr/bin/env python3
"""
黃國昌 YouTube 頻道爬蟲
真相網專用 - 每日爬取影片字幕與進度追蹤

使用方法: python3 kc-huang-scraper.py
"""

import json
import os
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

# 黃國昌頻道 ID
CHANNEL_ID = "UC-wlAMJl7k_b5kO1-9Bf2gQ"
BASE_URL = "https://www.youtube.com/watch?v="

def get_video_id_from_url(url):
    """從 YouTube URL 提取影片 ID"""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return url

def get_transcript(video_id):
    """取得影片字幕"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh-Hant', 'zh-TW', 'zh', 'en'])
        full_text = ""
        for item in transcript:
            full_text += item['text'] + "\n"
        return full_text
    except Exception as e:
        return f"無法取得字幕: {e}"

def scrape_channel_videos():
    """
    爬取黃國昌頻道所有影片
    注意: 需要登入才能取得完整列表，這裡使用替代方案
    """
    # 黃國昌近期熱門影片 (需要從其他來源取得完整列表)
    # 可用來源: Nitter, Invidious, 或手動維護列表

    videos = [
        {
            "title": "超思雞蛋弊案完整分析",
            "video_id": "EB858NtJWr0",
            "date": "2024-06-27",
            "category": "農業弊案",
            "status": "待爬取"
        },
        {
            "title": "台鹽綠能掏空8.6億",
            "video_id": "cPYpXZ9yFK0",
            "date": "2024-",
            "category": "能源弊案",
            "status": "待爬取"
        },
        # ... 更多影片待補
    ]

    return videos

def update_progress(video_id, status, details=""):
    """更新影片進度"""
    progress_file = "data/progress.json"
    progress = {}

    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)

    progress[video_id] = {
        "status": status,
        "details": details,
        "updated_at": datetime.now().isoformat()
    }

    with open(progress_file, 'w') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def save_video_data(video):
    """儲存影片資料"""
    data_dir = "data/cases"
    os.makedirs(data_dir, exist_ok=True)

    filename = f"{video['video_id']}.json"
    filepath = os.path.join(data_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(video, f, ensure_ascii=False, indent=2)

def main():
    print("=" * 50)
    print("黃國昌 YouTube 爬蟲 - 真相網")
    print("=" * 50)
    print(f"頻道: https://www.youtube.com/@KC-Huang")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 爬取影片列表
    videos = scrape_channel_videos()
    print(f"\n找到 {len(videos)} 部影片\n")

    for video in videos:
        print(f"處理中: {video['title']}")
        video_id = video['video_id']

        # 嘗試取得字幕
        transcript = get_transcript(video_id)
        video['transcript'] = transcript[:5000] if len(transcript) > 5000 else transcript
        video['transcript_length'] = len(transcript)

        # 更新狀態
        if "無法取得" not in transcript:
            video['status'] = "已完成"
            print(f"  ✅ 字幕取得成功 ({len(transcript)} 字)")
        else:
            video['status'] = "待手動處理"
            print(f"  ⚠️ {transcript[:100]}")

        # 儲存資料
        save_video_data(video)

    # 更新進度報告
    print("\n" + "=" * 50)
    print("進度報告")
    print("=" * 50)
    completed = sum(1 for v in videos if v['status'] == "已完成")
    print(f"已完成: {completed}/{len(videos)}")
    print(f"待處理: {len(videos) - completed}/{len(videos)}")

    # 生成 HTML 報告
    generate_html_report(videos)

def generate_html_report(videos):
    """生成 HTML 進度報告"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>黃國昌影片爬取進度 - 真相網</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .video {{ padding: 10px; border: 1px solid #ddd; margin: 5px 0; }}
        .done {{ background: #d4edda; }}
        .pending {{ background: #fff3cd; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>📊 黃國昌影片爬取進度</h1>
    <p>更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>影片總數: {len(videos)} | 已完成: {sum(1 for v in videos if v['status']=='已完成')}</p>
    <hr>
"""

    for video in videos:
        status_class = "done" if video['status'] == "已完成" else "pending"
        html += f"""
        <div class="video {status_class}">
            <strong>{video['title']}</strong><br>
            📁 {video['category']} | 📅 {video['date']}<br>
            🔗 https://www.youtube.com/watch?v={video['video_id']}<br>
            狀態: {video['status']}
        </div>
"""

    html += "</body></html>"

    with open("progress.html", 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n📄 進度報告已儲存: progress.html")

if __name__ == "__main__":
    main()
