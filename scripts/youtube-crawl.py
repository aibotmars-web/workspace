#!/usr/bin/env python3
"""
YouTube 字幕抓取脚本 - 慢慢抓取避免被挡
"""
import time
import os
from youtube_transcript_api import YouTubeTranscriptApi

# 9位专家频道列表
CHANNELS = {
    "阿銘師": "UC9CqM2LF7m1RFNdpAv4L9qA",
    "胡乃文": "UCYUHZk66njfU1VFwSviXPGQ",
    "柏格醫生": "UCUXi5mmqbvIithAs9AaxEtw",  # 需要确认
    "周慕姿": None,  # 需要确认
    "松明": "UCHNDk7584Q5g7RQCAFj7RFA",  # 需要从@SongMing找
    "Dr. Harvey": "UC36FfchJRvraEqWGb4MUdDA",
    "初日醫學": "UCzOblez4o3mZEkpOeFZdHWQ",
    "泛科學": "UCuHHKbwC0TWjeqxbqdO-N_g",
    "泛科學院": None,  # 需要找
}

OUTPUT_DIR = os.path.expanduser("~/knowledge-base")

def get_channel_videos(channel_id):
    """获取频道的最新视频"""
    # 这里用简化方法 - 手动维护视频列表或者用yt-dlp
    # 暂时返回空列表，需要另外处理
    return []

def fetch_transcript(video_id, languages=['zh-TW', 'zh-Hant', 'zh', 'en']):
    """抓取字幕，带重试"""
    api = YouTubeTranscriptApi()
    
    for lang in languages:
        try:
            transcript = api.fetch(video_id=video_id, languages=[lang])
            print(f"  ✓ 成功: 语言={transcript.language_code}")
            return transcript
        except Exception as e:
            continue
    
    print(f"  ✗ 失败: {str(e)[:50]}")
    return None

def save_transcript(name, video_id, transcript):
    """保存字幕到文件"""
    os.makedirs(f"{OUTPUT_DIR}/{name}", exist_ok=True)
    
    filename = f"{OUTPUT_DIR}/{name}/{video_id}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {name} - {video_id}\n")
        f.write(f"# Language: {transcript.language_code}\n")
        f.write(f"#抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        
        for snippet in transcript.snippets:
            timestamp = time.strftime('%H:%M:%S', time.gmtime(snippet.start))
            f.write(f"[{timestamp}] {snippet.text}\n")
    
    print(f"  ✓ 已保存: {filename}")

def test_single_video():
    """测试抓取单个视频"""
    test_videos = [
        ("阿銘師", "twtbftW9kQY"),  # 这个视频我们之前测试过
    ]
    
    for name, video_id in test_videos:
        print(f"\n测试 {name}: {video_id}")
        transcript = fetch_transcript(video_id)
        if transcript:
            # 显示前3条
            print("  前3条字幕:")
            for snippet in transcript.snippets[:3]:
                print(f"    {snippet.start}: {snippet.text}")
        
        # 每次请求后等待
        time.sleep(2)

if __name__ == "__main__":
    print("YouTube 字幕抓取测试...")
    test_single_video()
