#!/usr/bin/env python3
"""
黃國昌 YouTube 爬蟲腳本
影片來源：https://www.youtube.com/@KC-Huang
重點弊案：超思雞蛋、台鹽綠能、聯合再生、88會館、imb詐騙案
生成 HTML 進度報告
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import yt_dlp
except ImportError:
    print("請安裝 yt-dlp: pip install yt-dlp")
    sys.exit(1)

# 配置
CHANNEL_URL = "https://www.youtube.com/@KC-Huang"
OUTPUT_DIR = Path("/Users/marsbot/.openclaw/workspace/kc_huang_crawler")
DATA_DIR = OUTPUT_DIR / "data"
REPORTS_DIR = OUTPUT_DIR / "reports"
HTML_REPORT = REPORTS_DIR / "progress.html"

# 重點關鍵字
KEYWORDS = {
    "超思雞蛋": ["超思", "雞蛋", "蛋價", "進口蛋"],
    "台鹽綠能": ["台鹽", "綠能", "光電", "綠電"],
    "聯合再生": ["聯合再生", "再生能源", "太陽光電"],
    "88會館": ["88會館", "會館", "郭哲敏"],
    "imb詐騙": ["imb", "imB", "詐騙", "吸金", "假投資"]
}

# 狀態追蹤
crawl_state = {
    "start_time": None,
    "last_update": None,
    "total_videos": 0,
    "processed_videos": 0,
    "failed_videos": 0,
    "videos_with_captions": 0,
    "relevant_videos": 0,
    "videos": [],
    "status": "initializing",
    "errors": []
}


def setup_directories():
    """建立必要目錄"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"目錄已建立: {OUTPUT_DIR}")


def get_channel_videos() -> List[Dict]:
    """取得頻道所有影片列表"""
    print("正在取得頻道影片列表...")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'dump_single_json': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            channel_info = ydl.extract_info(CHANNEL_URL, download=False)
            
            videos = []
            if 'entries' in channel_info:
                for entry in channel_info['entries']:
                    if entry and entry.get('id'):
                        videos.append({
                            'id': entry['id'],
                            'title': entry.get('title', ''),
                            'url': f"https://www.youtube.com/watch?v={entry['id']}",
                            'duration': entry.get('duration', 0),
                            'upload_date': entry.get('upload_date', ''),
                            'view_count': entry.get('view_count', 0),
                            'thumbnail': entry.get('thumbnail', ''),
                        })
            
            print(f"找到 {len(videos)} 部影片")
            return videos
            
    except Exception as e:
        print(f"取得影片列表失敗: {e}")
        crawl_state["errors"].append(f"取得影片列表失敗: {str(e)}")
        return []


def check_captions_available(video_url: str) -> bool:
    """檢查影片是否有字幕"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': False,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return 'subtitles' in info and len(info['subtitles']) > 0
            
    except Exception:
        return False


def get_video_details(video_id: str) -> Optional[Dict]:
    """取得單一影片詳細資訊"""
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'writesubtitles': False,
        'skip_download': True,
        'getdescription': True,
        'getduration': True,
        'getviewcount': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # 提取字幕
            subtitles = {}
            if 'subtitles' in info:
                for lang, subs in info['subtitles'].items():
                    if lang in ['zh-Hant', 'zh-Hans', 'zh', 'en']:
                        subtitles[lang] = [s['url'] for s in subs[:1]]
            
            # 自動產生字幕
            auto_subtitles = {}
            if 'automatic_captions' in info:
                for lang, subs in info['automatic_captions'].items():
                    if lang in ['zh-Hant', 'zh-Hans', 'zh']:
                        auto_subtitles[lang] = [s['url'] for s in subs[:1]]
            
            return {
                'id': video_id,
                'title': info.get('title', ''),
                'description': info.get('description', ''),
                'url': video_url,
                'duration': info.get('duration', 0),
                'upload_date': info.get('upload_date', ''),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'subtitles': subtitles,
                'auto_subtitles': auto_subtitles,
                'has_captions': len(subtitles) > 0 or len(auto_subtitles) > 0,
                'thumbnail': info.get('thumbnail', ''),
            }
            
    except Exception as e:
        print(f"  取得影片 {video_id} 詳細資訊失敗: {e}")
        crawl_state["errors"].append(f"影片 {video_id}: {str(e)}")
        return None


def analyze_video_relevance(video: Dict) -> Dict[str, bool]:
    """分析影片與弊案的關聯性"""
    title = video.get('title', '').lower()
    description = video.get('description', '').lower() if video.get('description') else ''
    
    relevance = {}
    
    for case_name, keywords in KEYWORDS.items():
        relevance[case_name] = False
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title or keyword_lower in description:
                relevance[case_name] = True
                break
    
    return relevance


def extract_captions(video_id: str, languages: List[str] = ['zh-Hant', 'zh-Hans', 'zh']) -> Dict[str, str]:
    """擷取影片字幕"""
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'writeautomaticsub': True,
        'subtitleslangs': languages,
        'outtmpl': str(DATA_DIR / f"{video_id}.%(ext)s"),
    }
    
    captions = {}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # 讀取已下載的字幕檔案
        for lang in languages:
            subtitle_file = DATA_DIR / f"{video_id}.{lang}.vtt"
            if subtitle_file.exists():
                with open(subtitle_file, 'r', encoding='utf-8') as f:
                    captions[lang] = f.read()
        
    except Exception as e:
        print(f"    擷取字幕失敗: {e}")
        crawl_state["errors"].append(f"字幕擷取 {video_id}: {str(e)}")
    
    return captions


def generate_html_report():
    """生成 HTML 進度報告"""
    elapsed_time = ""
    if crawl_state["start_time"]:
        elapsed = datetime.now() - crawl_state["start_time"]
        elapsed_time = str(elapsed).split('.')[0]
    
    relevant_cases = {}
    for case_name in KEYWORDS.keys():
        relevant_cases[case_name] = [
            v for v in crawl_state["videos"]
            if v.get('relevance', {}).get(case_name, False)
        ]
    
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>黃國昌 YouTube 爬蟲進度報告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', 'Microsoft JhengHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .header h1 {{
            color: #333;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-card .label {{
            color: #666;
            margin-top: 5px;
        }}
        .progress-section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .progress-bar-container {{
            background: #eee;
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin: 15px 0;
        }}
        .progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        .cases-section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .case-card {{
            border: 1px solid #eee;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
        }}
        .case-card h3 {{
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .case-card .count {{
            background: #667eea;
            color: white;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.8em;
        }}
        .video-list {{
            max-height: 300px;
            overflow-y: auto;
        }}
        .video-item {{
            padding: 10px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .video-item:last-child {{
            border-bottom: none;
        }}
        .video-item a {{
            color: #667eea;
            text-decoration: none;
        }}
        .video-item a:hover {{
            text-decoration: underline;
        }}
        .status-badge {{
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
        }}
        .status-completed {{ background: #d4edda; color: #155724; }}
        .status-failed {{ background: #f8d7da; color: #721c24; }}
        .status-pending {{ background: #fff3cd; color: #856404; }}
        .videos-section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .video-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        .video-card {{
            border: 1px solid #eee;
            border-radius: 10px;
            overflow: hidden;
        }}
        .video-card img {{
            width: 100%;
            height: 180px;
            object-fit: cover;
        }}
        .video-card .content {{
            padding: 15px;
        }}
        .video-card h4 {{
            font-size: 1em;
            margin-bottom: 10px;
            color: #333;
        }}
        .video-card .meta {{
            font-size: 0.85em;
            color: #666;
            margin-bottom: 10px;
        }}
        .video-card .badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }}
        .badge {{
            background: #e9ecef;
            color: #495057;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.75em;
        }}
        .badge.relevant {{
            background: #cce5ff;
            color: #004085;
        }}
        .errors-section {{
            background: #f8d7da;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }}
        .errors-section h3 {{
            color: #721c24;
            margin-bottom: 15px;
        }}
        .error-item {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            color: #721c24;
        }}
        .timestamp {{
            text-align: right;
            color: #999;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📺 黃國昌 YouTube 爬蟲進度報告</h1>
            <p>頻道：{CHANNEL_URL}</p>
            <p>更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p class="timestamp">耗時：{elapsed_time}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="number">{crawl_state["total_videos"]}</div>
                <div class="label">總影片數</div>
            </div>
            <div class="stat-card">
                <div class="number">{crawl_state["processed_videos"]}</div>
                <div class="label">已處理</div>
            </div>
            <div class="stat-card">
                <div class="number">{crawl_state["videos_with_captions"]}</div>
                <div class="label">有字幕</div>
            </div>
            <div class="stat-card">
                <div class="number">{crawl_state["relevant_videos"]}</div>
                <div class="label">相關影片</div>
            </div>
            <div class="stat-card">
                <div class="number">{crawl_state["failed_videos"]}</div>
                <div class="label">失敗</div>
            </div>
        </div>
        
        <div class="progress-section">
            <h2>📊 爬取進度</h2>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {min(100, (crawl_state["processed_videos"] / max(1, crawl_state["total_videos"]) * 100)):.1f}%">
                    {crawl_state["processed_videos"]} / {crawl_state["total_videos"]} ({min(100, (crawl_state["processed_videos"] / max(1, crawl_state["total_videos"]) * 100)):.1f}%)
                </div>
            </div>
            <p>狀態：<span class="status-badge status-{crawl_state["status"]}">{crawl_state["status"]}</span></p>
        </div>
"""
    
    # 重點弊案區塊
    html += """
        <div class="cases-section">
            <h2>🔍 重點弊案相關影片</h2>
"""
    
    for case_name, videos in relevant_cases.items():
        html += f"""
            <div class="case-card">
                <h3>{case_name} <span class="count">{len(videos)} 部影片</span></h3>
                <div class="video-list">
"""
        for video in videos[:10]:  # 只顯示前10部
            upload_date = video.get('upload_date', '')
            if upload_date:
                upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
            html += f"""
                    <div class="video-item">
                        <a href="{video['url']}" target="_blank">{video['title'][:60]}...</a>
                        <span>{upload_date}</span>
                    </div>
"""
        if len(videos) > 10:
            html += f"""                    <div class="video-item">... 還有 {len(videos) - 10} 部影片</div>"""
        html += """                </div>
            </div>
"""
    
    html += """        </div>
"""
    
    # 錯誤區塊
    if crawl_state["errors"]:
        html += """
        <div class="errors-section">
            <h2>⚠️ 錯誤記錄</h2>
"""
        for error in crawl_state["errors"][-20:]:  # 只顯示最近20筆
            html += f"""            <div class="error-item">{error}</div>
"""
        html += """        </div>
"""
    
    # 影片列表區塊
    html += """
        <div class="videos-section">
            <h2>📋 所有已處理影片</h2>
            <div class="video-grid">
"""
    
    for video in crawl_state["videos"][:50]:  # 只顯示前50部
        badges = []
        if video.get('has_captions'):
            badges.append("✅ 字幕")
        if video.get('relevance'):
            for case, is_relevant in video['relevance'].items():
                if is_relevant:
                    badges.append(f"📌 {case}")
        
        upload_date = video.get('upload_date', '')
        if upload_date:
            upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
        
        html += f"""
                <div class="video-card">
                    <img src="{video.get('thumbnail', '')}" alt="{video['title'][:30]}">
                    <div class="content">
                        <h4>{video['title'][:50]}{'...' if len(video.get('title', '')) > 50 else ''}</h4>
                        <div class="meta">
                            <p>📅 {upload_date}</p>
                            <p>👁️ {video.get('view_count', 0):,} 次觀看</p>
                        </div>
                        <div class="badges">
                            {''.join([f'<span class="badge">{b}</span>' for b in badges[:3]])}
                        </div>
                    </div>
                </div>
"""
    
    html += """            </div>
        </div>
    </div>
</body>
</html>"""
    
    # 寫入檔案
    with open(HTML_REPORT, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"進度報告已更新: {HTML_REPORT}")


def save_data():
    """儲存爬取資料"""
    data_file = DATA_DIR / "crawl_state.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(crawl_state, f, ensure_ascii=False, indent=2)
    print(f"資料已儲存: {data_file}")


def run_crawler():
    """執行爬蟲主程式"""
    crawl_state["start_time"] = datetime.now()
    crawl_state["status"] = "running"
    
    setup_directories()
    
    # 步驟1：取得頻道影片列表
    videos = get_channel_videos()
    crawl_state["total_videos"] = len(videos)
    crawl_state["status"] = "fetching_details"
    generate_html_report()
    
    if not videos:
        print("無法取得影片列表，結束爬蟲")
        crawl_state["status"] = "failed"
        generate_html_report()
        return
    
    # 步驟2：處理每部影片
    print(f"\n開始處理 {len(videos)} 部影片...")
    
    for i, video_info in enumerate(videos):
        video_id = video_info['id']
        print(f"處理中 [{i+1}/{len(videos)}]: {video_info['title'][:50]}...")
        
        # 取得詳細資訊
        details = get_video_details(video_id)
        
        if details:
            # 分析關聯性
            relevance = analyze_video_relevance(details)
            details['relevance'] = relevance
            
            # 檢查是否有相關影片
            if any(relevance.values()):
                crawl_state["relevant_videos"] += 1
            
            # 檢查字幕
            if details.get('has_captions'):
                crawl_state["videos_with_captions"] += 1
            
            crawl_state["processed_videos"] += 1
            
            # 如果有字幕且有關聯，下載字幕
            if details.get('has_captions') and any(relevance.values()):
                print(f"  正在擷取字幕...")
                captions = extract_captions(video_id)
                details['captions'] = captions
            
            crawl_state["videos"].append(details)
        else:
            crawl_state["failed_videos"] += 1
        
        # 每10部影片更新一次報告
        if (i + 1) % 10 == 0:
            generate_html_report()
            save_data()
        
        # 避免請求過快
        time.sleep(1)
    
    # 步驟3：完成
    crawl_state["status"] = "completed"
    crawl_state["last_update"] = datetime.now().isoformat()
    
    generate_html_report()
    save_data()
    
    print(f"\n✅ 爬蟲完成!")
    print(f"總影片數: {crawl_state['total_videos']}")
    print(f"已處理: {crawl_state['processed_videos']}")
    print(f"有字幕: {crawl_state['videos_with_captions']}")
    print(f"相關影片: {crawl_state['relevant_videos']}")
    print(f"失敗: {crawl_state['failed_videos']}")
    print(f"\n進度報告: {HTML_REPORT}")


if __name__ == "__main__":
    run_crawler()
