#!/usr/bin/env python3
"""Detect text overlap in slide images - measures text block fill ratio."""
from PIL import Image
import numpy as np

def analyze_slide(img_path):
    """
    Analyze slide for potential text overlap by measuring how much
    of the slide area is occupied by high-detail (text) content.
    """
    img = Image.open(img_path).convert('RGB')
    arr = np.array(img)
    h, w = arr.shape[:2]
    
    # Divide into horizontal bands (each slide has distinct sections)
    # Typical slide layout: header zone (top 20%), text zone (20-75%), footer zone (bottom 25%)
    bands = {
        'header': (0, int(h*0.20)),
        'text_main': (int(h*0.20), int(h*0.75)),
        'text_footer': (int(h*0.75), h)
    }
    
    results = {}
    for name, (y1, y2) in bands.items():
        band = arr[y1:y2]
        gray = np.mean(band, axis=2)
        
        # Calculate variance per column - high variance = text present
        col_var = np.var(gray, axis=0)  # variance across rows for each column
        
        # Find columns with significant content
        content_cols = np.where(col_var > 50)[0]
        
        if len(content_cols) > 0:
            # Check if content spans the full width (might indicate text wrapping issues)
            content_span = content_cols[-1] - content_cols[0] if len(content_cols) > 0 else 0
            fill_ratio = len(content_cols) / w
            
            results[name] = {
                'fill_ratio': round(fill_ratio, 2),
                'content_span': content_span,
                'w': w,
                'has_content': len(content_cols) > w * 0.1
        }
    
    # Also check for extremely dense regions (potential overlap indicator)
    gray_full = np.mean(arr, axis=2)
    row_variance = np.var(gray_full, axis=1)
    max_row_var = np.max(row_variance)
    
    return results, max_row_var

def check_slide(img_path):
    """Check if slide looks healthy or has potential issues."""
    bands, max_var = analyze_slide(img_path)
    
    issues = []
    
    # Check text_main zone - if fill ratio is very high, text might be too dense
    if 'text_main' in bands:
        fm = bands['text_main']
        if fm['fill_ratio'] > 0.85:
            issues.append(f"⚠️ 主內容區填充率過高 ({fm['fill_ratio']})，可能有文字擠壓")
        if fm['content_span'] == fm['w'] - 1:
            issues.append(f"⚠️ 文字撐滿全寬，可能有溢出問題")
    
    # Check footer zone - if almost full, text might be overflowing
    if 'text_footer' in bands:
        ff = bands['text_footer']
        if ff['fill_ratio'] > 0.7 and ff['has_content']:
            issues.append(f"⚠️ 頁腳區域有內容 ({ff['fill_ratio']})，可能是文字溢出")
    
    # High max variance could indicate sharp text edges (good) or chaotic overlap (bad)
    # We want high variance in header/text zones but not chaotic patterns
    
    if not issues:
        status = "✅ 正常"
    else:
        status = "❌ 有問題"
    
    return status, issues, bands

if __name__ == '__main__':
    from pathlib import Path
    
    card_dir = Path('/Users/marsbot/.openclaw/workspace/agents/assistant-work/cards/crypto_20260330_123729')
    slides = sorted(card_dir.glob('crypto_20260330_123729_s*.jpg'))
    
    print(f"分析 {len(slides)} 張幻燈片...\n")
    
    problem_slides = []
    
    for slide in slides:
        status, issues, bands = check_slide(str(slide))
        print(f"{Path(slide).name}: {status}")
        if issues:
            for issue in issues:
                print(f"  {issue}")
            problem_slides.append(Path(slide).name)
        # Show band fill ratios
        for band, data in bands.items():
            print(f"  {band}: fill={data['fill_ratio']}, span={data['content_span']}")
        print()
    
    if problem_slides:
        print(f"\n🚨 有問題的幻燈片: {', '.join(problem_slides)}")
    else:
        print("\n✅ 所有幻燈片看起來正常")
