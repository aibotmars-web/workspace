#!/usr/bin/env python3
"""
YT 專家知識庫檢索系統 v2
直接搜尋字幕檔案，找到相關專家觀點
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import re

# 設定
DATA_DIR = Path("/Users/marsbot/.openclaw/workspace/agents/assistant/yt_data")
CAPTIONS_DIR = DATA_DIR / "captions"

# 專家頻道資訊（影片 ID 前綴對照）
CHANNEL_VIDEOS = {
    "阿銘師": {"prefix": "rFwmOcWHQUc", "name": "阿銘師x銭還傳", "field": "中醫食療、經絡"},
    "胡乃文": {"prefix": "akWTuJ0ZbtE", "name": "胡乃文開講", "field": "傳統中醫、養生"},
    "柏格醫生": {"prefix": "mUlz3x_S_tM", "name": "柏格醫生", "field": "生酮、功能醫學"},
    "周慕姿": {"prefix": "GFKi57nXY4s", "name": "周慕姿放心說", "field": "心理諮商"},
    "松明": {"prefix": "D6GUlHyUY80", "name": "松明講心理", "field": "心理控制"},
    "初日": {"prefix": "otGGiNPA8ek", "name": "初日醫學", "field": "代謝、減重"},
    "泛科學": {"prefix": "ECn_dlgkR1g", "name": "泛科學", "field": "科學科普"},
    "泛科學院": {"prefix": "svDbThRvByk", "name": "泛科學院", "field": "AI工具"},
}

def get_expert_from_video(video_id: str) -> Dict:
    """根據影片 ID 判斷是哪個專家"""
    # 簡單匹配：檢查字幕目錄中同 ID 的影片標題
    for ext in ['.zh.vtt', '.zh-Hant.vtt', '.zh-Hans.vtt', '.en.vtt']:
        caption_file = CAPTIONS_DIR / f"{video_id}{ext}"
        if caption_file.exists():
            return {"id": video_id, "source": "captions"}
    return None

def extract_video_id_from_file(filename: str) -> str:
    """從檔名提取影片 ID"""
    return filename.split('.')[0]

def search_in_captions(query: str) -> List[Dict]:
    """在字幕中搜尋關鍵字"""
    results = []
    keywords = query.lower().split()
    
    for caption_file in sorted(CAPTIONS_DIR.glob("*.vtt")):
        video_id = extract_video_id_from_file(caption_file.name)
        
        try:
            with open(caption_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查是否包含關鍵字
            content_lower = content.lower()
            matched_keywords = [k for k in keywords if k in content_lower]
            
            if matched_keywords:
                # 提取相關段落
                snippets = extract_snippets(content, keywords)
                
                # 嘗試從標題檔案取得影片標題
                title = get_video_title(video_id)
                
                # 判斷專家
                expert = identify_expert(video_id)
                
                results.append({
                    'video_id': video_id,
                    'expert': expert['name'] if expert else "未知",
                    'field': expert['field'] if expert else "",
                    'title': title,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'snippets': snippets[:2],
                    'matched_keywords': matched_keywords,
                    'score': len(matched_keywords)
                })
                
        except Exception:
            continue
    
    # 按分數排序
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:10]

def extract_snippets(content: str, keywords: List[str], max_len: int = 200) -> List[str]:
    """提取包含關鍵字的段落"""
    snippets = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for keyword in keywords:
            if keyword in line_lower and len(line.strip()) > 10:
                # 提取上下文
                start = max(0, i - 3)
                end = min(len(lines), i + 3)
                text_parts = []
                for j in range(start, end):
                    l = lines[j].strip()
                    if l and not '-->' in l and not l.isdigit() and 'WEBVTT' not in l:
                        text_parts.append(l)
                if text_parts:
                    snippet = ' '.join(text_parts)[:max_len]
                    if snippet not in snippets:
                        snippets.append(snippet)
                break
    
    return snippets

def get_video_title(video_id: str) -> str:
    """取得影片標題"""
    # 嘗試從標題檔案讀取
    title_file = CAPTIONS_DIR / f"{video_id}.title.txt"
    if title_file.exists():
        with open(title_file, 'r') as f:
            return f.read().strip()
    return f"影片 {video_id}"

def identify_expert(video_id: str) -> Optional[Dict]:
    """識別影片屬於哪個專家"""
    # 簡單方法：檢查已知的影片 ID
    known_ids = {
        'rFwmOcWHQUc': {"name": "阿銘師x銭還傳", "field": "中醫食療"},
        'tAVIf0bPUVM': {"name": "阿銘師x銭還傳", "field": "中醫食療"},
        'wD9NiMi1AKg': {"name": "阿銘師x銭還傳", "field": "身心學"},
        'akWTuJ0ZbtE': {"name": "胡乃文開講", "field": "中醫養生"},
        'O_UeOYi92M4': {"name": "胡乃文開講", "field": "中醫養生"},
        'SvEEh1X09Fs': {"name": "胡乃文開講", "field": "中醫養生"},
        'D6GUlHyUY80': {"name": "松明講心理", "field": "心理"},
        'GFKi57nXY4s': {"name": "周慕姿放心說", "field": "心理諮商"},
        'ECn_dlgkR1g': {"name": "泛科學", "field": "科學"},
        'svDbThRvByk': {"name": "泛科學院", "field": "AI"},
    }
    
    return known_ids.get(video_id)

def search_youtube_title(query: str) -> List[Dict]:
    """在已知影片標題中搜尋"""
    results = []
    keywords = query.lower().split()
    
    # 已知的影片標題（從爬蟲結果來的）
    known_videos = [
        {"id": "rFwmOcWHQUc", "expert": "阿銘師", "title": "轉頭就痛！頸因性頭痛，真正的原因在手部！？"},
        {"id": "akWTuJ0ZbtE", "expert": "胡乃文", "title": "濕冷＋強風吹增猝死率！手腳冰冷恐是心肌梗塞前兆！"},
        {"id": "O_UeOYi92M4", "expert": "胡乃文", "title": "60歲婦人吃香蕉昏倒中毒！注意！3種情況不能吃香蕉"},
        {"id": "D6GUlHyUY80", "expert": "松明", "title": "消除你的創傷只需要記住兩兩個字！"},
        {"id": "GFKi57nXY4s", "expert": "周慕姿", "title": "別再用四個字母解釋痛苦，MBTI 的下一步是看懂「局」"},
        {"id": "ECn_dlgkR1g", "expert": "泛科學", "title": "Breaking News! The Violent Savior of Overheated Oceans"},
        {"id": "svDbThRvByk", "expert": "泛科學院", "title": "2026 Best AI Subscription Guide"},
    ]
    
    for video in known_videos:
        title_lower = video['title'].lower()
        if any(k in title_lower for k in keywords):
            results.append({
                'video_id': video['id'],
                'expert': video['expert'],
                'title': video['title'],
                'url': f"https://www.youtube.com/watch?v={video['id']}",
                'snippets': [],
                'matched_keywords': [k for k in keywords if k in title_lower],
                'score': sum(1 for k in keywords if k in title_lower)
            })
    
    return sorted(results, key=lambda x: x['score'], reverse=True)

def search(query: str) -> Dict:
    """主搜尋函數"""
    # 1. 搜尋已知影片標題
    title_results = search_youtube_title(query)
    
    # 2. 搜尋字幕內容
    caption_results = search_in_captions(query)
    
    # 3. 合併結果（去重）
    seen_ids = set()
    all_results = []
    
    for r in title_results:
        if r['video_id'] not in seen_ids:
            seen_ids.add(r['video_id'])
            all_results.append(r)
    
    for r in caption_results:
        if r['video_id'] not in seen_ids:
            seen_ids.add(r['video_id'])
            all_results.append(r)
    
    # 重新排序
    all_results.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'query': query,
        'timestamp': datetime.now().isoformat(),
        'total_results': len(all_results),
        'results': all_results[:5]
    }

def format_response(result: Dict) -> str:
    """格式化回應"""
    if not result['results']:
        return f"❌ 找不到「{result['query']}」相關內容"
    
    lines = []
    lines.append(f"🔍 搜尋：{result['query']}")
    lines.append(f"📊 找到 {result['total_results']} 個相關影片\n")
    
    for i, r in enumerate(result['results'], 1):
        lines.append("─"*50)
        lines.append(f"### {i}. 【{r['expert']}】")
        lines.append(f"**{r['title']}**")
        lines.append(f"📎 {r['url']}")
        
        if r['snippets']:
            lines.append("\n💡 專家說：")
            for s in r['snippets'][:1]:
                lines.append(f"> {s[:150]}...")
        
        lines.append("")
    
    return '\n'.join(lines)

def main():
    import sys
    
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        result = search(query)
        print(format_response(result))
    else:
        print("用法：python3 search_experts.py <搜尋關鍵字>")
        print("\n範例：")
        print("  python3 search_experts.py 失眠")
        print("  python3 search_experts.py 減肥 糖尿病")
        print("  python3 search_experts.py AI")

if __name__ == "__main__":
    main()
