#!/usr/bin/env python3
"""
快速檢查頻道爬蟲狀態
顯示：頻道總共幾支 / 已抓取幾支 / 進度%
"""

import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
OUTPUT_DIR = WORKSPACE / "experts" / "transcripts"

# 頻道列表（名稱 -> ID）
CHANNELS = {
    "Dr.Hu_talk": "UCvVY1c7-r8GwV0g……",
    "drbergchinese": "UCg1……",
    "Dr.HuangAmin": "UC……",
    "muerstalk": "UC……",
    "SongMing": "UC……",
    "Cofit211": "UC……",
    "PanScitw": "UC……",
    "panscischool": "UC……",
}

def get_crawled_count(channel_name):
    """統計已抓取的檔案數"""
    channel_dir = OUTPUT_DIR / channel_name
    if not channel_dir.exists():
        return 0
    txt_files = list(channel_dir.glob("*.txt"))
    return len([f for f in txt_files if f.stat().st_size > 100])


def get_channel_total(channel_url, limit=200):
    """獲取頻道總影片數"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--get-id", "--playlist-end", str(limit), channel_url],
            capture_output=True,
            text=True,
            timeout=30,
        )
        videos = [v.strip() for v in result.stdout.strip().split("\n") if v.strip()]
        return len(videos)
    except:
        return 0


def main():
    print(f"{'='*60}")
    print(f"📊 專家知識庫爬蟲狀態")
    print(f"{'='*60}")
    print(f"查詢時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 從目錄讀取已知的頻道
    if OUTPUT_DIR.exists():
        dirs = [d for d in OUTPUT_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]
        channel_names = sorted([d.name for d in dirs])
    else:
        channel_names = list(CHANNELS.keys())
    
    # 統計
    print(f"{'頻道':<20} {'總計':<10} {'已抓':<10} {'進度':<10} {'狀態':<10}")
    print("-" * 65)
    
    total_all = 0
    crawled_all = 0
    
    for channel_name in channel_names:
        crawled = get_crawled_count(channel_name)
        
        # 嘗試從 log 找到上次抓取的總數
        log_file = WORKSPACE / "kd-crawl-latest.log"
        total = "?"
        status = "未知"
        
        if crawled == 0:
            status = "未開始"
        elif crawled < 50:
            status = "進行中"
        else:
            status = "已完成"
        
        # 嘗試從 crawler-cron.log 讀取總數
        cron_log = WORKSPACE / "crawler-cron.log"
        if cron_log.exists():
            with open(cron_log) as f:
                content = f.read()
                if channel_name in content:
                    # 找到該頻道的記錄
                    lines = content.split('\n')
                    for line in lines:
                        if channel_name in line and '抓取' in line:
                            # 解析數量
                            import re
                            match = re.search(r'(\d+)/(\d+)', line)
                            if match:
                                crawled, total = int(match.group(1)), int(match.group(2))
        
        print(f"{channel_name:<20} {str(total):<10} {crawled:<10} {'-':<10} {status:<10}")
        total_all += int(total) if total != "?" else 0
        crawled_all += crawled
    
    print("-" * 65)
    overall = f"{crawled_all/total_all*100:.1f}%" if total_all > 0 else "N/A"
    print(f"{'總計':<20} {total_all:<10} {crawled_all:<10} {overall:<10}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
