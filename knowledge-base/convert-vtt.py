#!/usr/bin/env python3
"""
將 YouTube 字幕 (vtt) 轉換為文字並加入 QMD 知識庫
"""

import os
import re
from pathlib import Path

VTT_DIR = "/Users/marsbot/.openclaw/workspace/knowledge-base/experts"
QMD_DIR = "/Users/marsbot/.cache/qmd/documents"

def parse_vtt(vtt_path):
    """解析 VTT 字幕檔案，回傳文字"""
    try:
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除 VTT 標籤和時間戳
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            # 跳過時間戳標籤
            if '-->' in line:
                continue
            # 跳過 WEBVTT 標籤
            if line.strip().startswith('WEBVTT'):
                continue
            # 跳過空白行
            if line.strip() == '':
                continue
            # 移除標籤如 <c>、</c> 等
            clean_line = re.sub(r'<[^>]+>', '', line)
            if clean_line.strip():
                text_lines.append(clean_line.strip())
        
        return ' '.join(text_lines)
    except Exception as e:
        print(f"Error parsing {vtt_path}: {e}")
        return None

def get_channel_name(channel_dir):
    """從目錄名稱對應頻道名稱"""
    channel_map = {
        "Dr.Hu_talk": "胡乃文開示",
        "drbergchinese": "柏格醫生中文", 
        "muerstalk": "周慕姿放心說",
        "Cofit211": "初日醫學",
        "panscischool": "泛科學院",
        "Dr.HuangAmin": "阿銘師x針還傳",
        "SongMing": "松明講心理",
        "PanScitw": "泛科學",
        "DrHarveyTalk": "Dr.Harvey不廢話"
    }
    return channel_map.get(channel_dir, channel_dir)

def main():
    print("=== VTT 字幕轉文字 ===\n")
    
    total = 0
    converted = 0
    
    # 遍歷每個頻道目錄
    channel_dirs = [d for d in Path(VTT_DIR).iterdir() if d.is_dir() and d.name not in ['summaries', 'transcripts']]
    
    for channel_dir in channel_dirs:
        channel_name = get_channel_name(channel_dir.name)
        vtt_files = list(channel_dir.glob("*.vtt"))
        
        if not vtt_files:
            continue
            
        print(f"📺 {channel_name}: {len(vtt_files)} 個字幕")
        
        for vtt_file in vtt_files:
            # 產生文字檔案名稱
            txt_file = vtt_file.with_suffix('.txt')
            
            # 避免重複：如果 txt 已存在且內容較新，跳過
            if txt_file.exists() and txt_file.stat().st_mtime > vtt_file.stat().st_mtime:
                continue
                
            # 解析 VTT
            text = parse_vtt(vtt_file)
            if text and len(text) > 50:  # 至少50個字
                # 寫入文字檔
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(f"頻道: {channel_name}\n")
                    f.write(f"影片ID: {vtt_file.stem}\n")
                    f.write(f"來源: {vtt_file.name}\n")
                    f.write("="*50 + "\n\n")
                    f.write(text)
                converted += 1
                print(f"  ✓ {vtt_file.name} -> {txt_file.name}")
            
            total += 1
    
    print(f"\n=== 完成 ===")
    print(f"總字幕: {total}")
    print(f"已轉換: {converted}")
    print(f"\n文字檔位置: {VTT_DIR}")
    print(f"下一步: 用 'qmd add' 將文字檔加入知識庫")

if __name__ == "__main__":
    main()
