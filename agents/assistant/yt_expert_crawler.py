#!/usr/bin/env python3
"""
YT 專家頻道爬蟲 v3
使用 yt-dlp 下載字幕（包含自動字幕）
"""

import sys
import json
import time
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import yt_dlp

# 專家頻道列表
CHANNELS = {
    "Dr.HuangAmin": {"name": "阿銘師x銭還傳", "url": "https://www.youtube.com/@Dr.HuangAmin/videos"},
    "Dr.Hu_talk": {"name": "胡乃文開講", "url": "https://www.youtube.com/@Dr.Hu_talk/videos"},
    "drbergchinese": {"name": "柏格醫生", "url": "https://www.youtube.com/@drbergchinese/videos"},
    "muerstalk": {"name": "周慕姿放心說", "url": "https://www.youtube.com/@muerstalk/videos"},
    "SongMing": {"name": "松明講心理", "url": "https://www.youtube.com/@SongMing/videos"},
    "DrHarveyTalk": {"name": "Dr. Harvey", "url": "https://www.youtube.com/@DrHarveyTalk/videos"},
    "Cofit211": {"name": "初日醫學", "url": "https://www.youtube.com/@Cofit211/videos"},
    "PanScitw": {"name": "泛科學", "url": "https://www.youtube.com/@PanScitw/videos"},
    "panscischool": {"name": "泛科學院", "url": "https://www.youtube.com/@panscischool/videos"}
}

OUTPUT_DIR = Path("/Users/marsbot/.openclaw/workspace/agents/assistant")
DATA_DIR = OUTPUT_DIR / "yt_data"
CAPTIONS_DIR = DATA_DIR / "captions"
CAPTIONS_DIR.mkdir(parents=True, exist_ok=True)

def get_channel_videos(channel_url, limit=15):
    """取得頻道最新長影片列表"""
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'playlistend': limit * 2}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            videos = []
            if 'entries' in info:
                for entry in info['entries']:
                    if entry and entry.get('id'):
                        title = entry.get('title', '').lower()
                        if 'shorts' in title: continue
                        duration = entry.get('duration', 0) or 0
                        if duration and duration < 60: continue
                        videos.append({'id': entry['id'], 'title': entry.get('title', ''), 'url': f"https://www.youtube.com/watch?v={entry['id']}", 'duration': duration})
            return videos[:limit]
    except Exception as e:
        print(f"  ⚠️ 取得影片失敗: {e}")
        return []

def download_caption(video_id, video_url):
    """下載字幕"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['zh-Hant', 'zh-Hans', 'zh', 'en'],
        'outtmpl': str(CAPTIONS_DIR / f"{video_id}.%(ext)s"),
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # 讀取下載的字幕
        for ext in ['vtt', 'srt', 'txt']:
            temp_file = CAPTIONS_DIR / f"{video_id}.{ext}"
            if temp_file.exists():
                with open(temp_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                text = clean_caption(content)
                if len(text) > 50:
                    return text
                temp_file.unlink()
        return None
    except Exception as e:
        return None

def clean_caption(content):
    """清理字幕檔案，提取純文字"""
    lines = content.split('\n')
    text_lines = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('-->') or line.replace('.', '').replace(':', '').isdigit():
            continue
        if '<' in line and '>' in line:
            continue
        text_lines.append(line)
    return ' '.join(text_lines)

def summarize_text(text, max_length=500):
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def crawl_channel(channel_id):
    channel_info = CHANNELS[channel_id]
    print(f"\n{'='*50}")
    print(f"🔍 爬取: {channel_info['name']}")
    print(f"{'='*50}")
    
    videos = get_channel_videos(channel_info['url'], limit=15)
    if not videos:
        print(f"  ⚠️ 沒有找到長影片")
        return None
    
    results = {
        "channel_id": channel_id,
        "channel_name": channel_info['name'],
        "url": channel_info['url'],
        "crawl_time": datetime.now().isoformat(),
        "videos": []
    }
    
    for video in videos:
        video_id = video['id']
        duration_str = f"{video.get('duration', 0)//60}分鐘" if video.get('duration') else "?"
        print(f"  📹 {video['title'][:35]}... ({duration_str})")
        
        transcript = download_caption(video_id, video['url'])
        
        video_result = {
            "id": video_id,
            "title": video['title'],
            "url": video['url'],
            "duration": video.get('duration', 0),
            "has_transcript": transcript is not None and len(transcript) > 50,
            "transcript_preview": summarize_text(transcript) if transcript else None,
        }
        
        results["videos"].append(video_result)
        
        if transcript and len(transcript) > 50:
            print(f"     ✅ 有字幕 ({len(transcript)} 字)")
        else:
            print(f"     ❌ 無字幕")
        
        time.sleep(0.3)
    
    return results

def generate_report(all_results):
    report = f"""# YT 專家更新日誌

## {datetime.now().strftime('%Y年%m月%d日')}

### 📊 今日統計
- 爬取頻道數：{len([r for r in all_results if r])} 個
- 更新影片數：{sum(len(r['videos']) if r else 0 for r in all_results)} 部
- 有字幕影片：{sum(sum(1 for v in r['videos'] if v.get('has_transcript')) for r in all_results if r)} 部

"""
    for result in all_results:
        if not result: continue
        report += f"#### {result['channel_name']}\n"
        for video in result['videos']:
            duration_str = f"{video.get('duration', 0)//60}分鐘" if video.get('duration') else "?"
            report += f"""- **標題**：{video['title']}
- **連結**：{video['url']}
- **時長**：{duration_str}
- **字幕狀態**：{'✅ 有' if video['has_transcript'] else '❌ 無'}

"""
    return report

def main():
    print("🚀 開始爬取 YT 專家頻道...")
    all_results = []
    for channel_id in CHANNELS:
        try:
            result = crawl_channel(channel_id)
            if result:
                all_results.append(result)
        except Exception as e:
            print(f"❌ 爬取失敗: {e}")
    
    if not all_results:
        print("\n⚠️ 沒有爬取到任何影片")
        return
    
    json_file = DATA_DIR / "experts_latest.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 資料已儲存: {json_file}")
    
    report = generate_report(all_results)
    log_file = DATA_DIR / "yt-updates.log"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📝 更新日誌: {log_file}")
    
    total_videos = sum(len(r['videos']) for r in all_results)
    videos_with_transcript = sum(sum(1 for v in r['videos'] if v.get('has_transcript')) for r in all_results)
    print(f"\n✅ 爬取完成！")
    print(f"   爬取頻道：{len(all_results)}")
    print(f"   總長影片數：{total_videos}")
    print(f"   有字幕：{videos_with_transcript}")

if __name__ == "__main__":
    main()
