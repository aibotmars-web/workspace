#!/usr/bin/env python3
"""
YT 知識庫 + Google Sheets 整合程式
功能：
1. 從 YouTube 專家頻道抓取最新影片
2. 生成摘要
3. 自動更新到 Google Sheets

頻道清單：
- @Dr.HuangAmin - 阿銘師x針還傳 (健康)
- @Dr.Hu_talk - 胡乃⽂開講 - 名醫談養⽣ (健康)
- @drbergchinese - 柏格醫⽣中⽂ (健康)
- @muerstalk - 周慕姿放⼼說 (心理)
- @SongMing - 松明講⼼理 (心理)
- @DrHarveyTalk - Dr. Harvey (健康)
- @Cofit211 - 初⽇醫學 - 宋晏仁醫師 (健康)
- @PanScitw - 泛科學 (科學)
- @panscischool - 泛科學院 (科學)

使用方式：
python3 yt-expert-crawler.py
"""

import json
import subprocess
import sys
from datetime import datetime

# ==== 配置 ====
CHANNEL_CONFIG = {
    "Dr.HuangAmin": {
        "channel_id": "UCxxxx",  # 待填入實際 ID
        "name": "阿銘師x針還傳",
        "category": "健康"
    },
    "Dr.Hu_talk": {
        "channel_id": "UCyyyy",  # 待填入實際 ID
        "name": "胡乃文開講",
        "category": "健康"
    },
    "drbergchinese": {
        "channel_id": "UCzzzz",
        "name": "柏格醫生中文",
        "category": "健康"
    },
    # ... 其他頻道
}

# ==== YouTube 抓取函數 ====
def get_channel_videos(channel_id, max_results=5):
    """使用 yt-dlp 抓取頻道最新影片"""
    cmd = [
        "yt-dlp",
        "--playlist-end", str(max_results),
        "--dump-json",
        f"https://www.youtube.com/channel/{channel_id}/videos"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    video = json.loads(line)
                    videos.append({
                        'title': video.get('title', ''),
                        'url': video.get('webpage_url', ''),
                        'upload_date': video.get('upload_date', ''),
                        'duration': video.get('duration', 0),
                        'view_count': video.get('view_count', 0),
                        'description': video.get('description', '')[:500]
                    })
            return videos
        else:
            print(f"❌ yt-dlp 錯誤：{result.stderr}")
            return []
            
    except Exception as e:
        print(f"❌ 執行錯誤：{e}")
        return []

# ==== 影片摘要（待整合 LLM）====
def generate_video_summary(video_info):
    """生成影片摘要"""
    # TODO: 整合 LLM API（如 MiniMax）
    title = video_info['title']
    desc = video_info.get('description', '')[:300]
    
    summary = {
        'headline': title,
        'key_topics': ['待使用 AI 生成'],
        'expert_opinion': '待生成',
        'relevance_score': 0.7
    }
    
    return summary

# ==== 資料整合 ====
def process_channel(channel_name, config):
    """處理單一頻道"""
    print(f"\n📺 處理頻道：{config['name']}")
    
    videos = get_channel_videos(config['channel_id'], max_results=3)
    
    processed = []
    for video in videos:
        summary = generate_video_summary(video)
        
        processed.append({
            'channel_name': config['name'],
            'category': config['category'],
            'video_title': video['title'],
            'video_url': video['url'],
            'publish_date': video['upload_date'],
            'summary': summary,
            'collected_at': datetime.now().isoformat()
        })
    
    return processed

# ==== 寫入 Google Sheets ====
def write_to_google_sheets(data_list):
    """寫入 Google Sheets"""
    # TODO: 整合 google-sheets-updater.py
    print(f"\n💾 準備寫入 {len(data_list)} 筆資料到 Google Sheets")
    
    for item in data_list:
        print(f"   📌 {item['channel_name']} - {item['video_title'][:30]}...")
    
    return True

# ==== 主程式 ====
def main():
    """主程式"""
    print("=== YT 知識庫 + Google Sheets 整合程式 ===")
    print(f"頻道數量：{len(CHANNEL_CONFIG)}")
    print("-" * 50)
    
    all_results = []
    
    for channel_name, config in CHANNEL_CONFIG.items():
        results = process_channel(channel_name, config)
        all_results.extend(results)
    
    # 寫入 Google Sheets
    print("\n" + "=" * 50)
    write_to_google_sheets(all_results)
    
    print("\n✅ 完成！")
    return all_results

if __name__ == "__main__":
    main()
