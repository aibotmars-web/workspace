#!/usr/bin/env python3
"""
知識庫 LLM 摘要生成器 v2
使用 openclaw agent 呼叫 MiniMax LLM 為專家影片生成結構化摘要
"""

import subprocess
import json
import os
import sys
import re
import uuid
import time
from pathlib import Path
from datetime import datetime

# 設定
WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
EXPERTS_DIR = WORKSPACE / "experts"
SUMMARIES_DIR = WORKSPACE / "summaries"
STATE_FILE = WORKSPACE / "summary_state.json"

# 專家元數據
CHANNEL_META = {
    "Dr.HuangAmin": {"name": "阿銘師x針還傳", "expert": "賴鎮榮醫師（阿銘師）", "area": "中醫針灸、健康養生"},
    "Dr.Hu_talk": {"name": "胡乃文再開", "expert": "胡乃文中醫師", "area": "中醫養生"},
    "drbergchinese": {"name": "柏格醫生中文", "expert": "Dr. Eric Berg", "area": "生酮飲食、健康減重"},
    "muerstalk": {"name": "周慕姿放心說", "expert": "周慕姿心理師", "area": "心理諮商、情緒管理"},
    "SongMing": {"name": "松明講心理", "expert": "松明", "area": "心理學、催眠治療"},
    "DrHarveyTalk": {"name": "Dr. Harvey", "expert": "Dr. Harvey", "area": "健康資訊"},
    "Cofit211": {"name": "初日醫學", "expert": "宋晏仁醫師", "area": "代謝減重、營養醫學"},
    "PanScitw": {"name": "泛科學", "expert": "泛科學編輯團隊", "area": "科學傳播"},
    "panscischool": {"name": "泛科學院", "expert": "泛科學院", "area": "線上課程、科學教育"},
}

MAX_TRANSCRIPT_LEN = 25000
LLM_TIMEOUT = 120  # openclaw agent timeout in seconds


def call_llm_summarize(transcript_text, video_url, channel_id):
    """使用 openclaw agent 叫用 MiniMax LLM 生成摘要"""
    meta = CHANNEL_META.get(channel_id, {})
    expert_name = meta.get("expert", channel_id)
    
    # 裁剪過長文字
    if len(transcript_text) > MAX_TRANSCRIPT_LEN:
        display_text = transcript_text[:MAX_TRANSCRIPT_LEN] + "\n...（內容過長已截斷）"
    else:
        display_text = transcript_text
    
    user_message = f"""你是一個專業的YouTube知識整理助理。請根據以下字幕內容，生成一個結構化的專家知識摘要。

**頻道專家**：{expert_name}（{meta.get('area', '未知領域')}）
**影片網址**：{video_url}

**字幕內容**：
{display_text}

請嚴格按照以下JSON格式輸出，不要有其他文字：
{{
  "title": "影片標題（不超過50字）",
  "expert": "專家名字",
  "topic": "主要主題（5-10字）",
  "summary": "300-500字的繁體中文摘要，包含專家的核心論點",
  "key_points": ["要點1", "要點2", "要點3", "要點4", "要點5"],
  "practical_tips": ["實際建議1", "實際建議2"],
  "source_url": "{video_url}"
}}"""

    session_id = f"kb-summarize-{uuid.uuid4().hex[:8]}"
    
    try:
        result = subprocess.run(
            [
                "openclaw", "agent",
                "--message", user_message,
                "--session-id", session_id,
                "--timeout", str(LLM_TIMEOUT),
                "--json"
            ],
            capture_output=True,
            text=True,
            timeout=LLM_TIMEOUT + 30,
            # 不_override env，讓 subprocess 繼承當前環境
        )
        
        if result.returncode != 0:
            print(f"  ⚠ openclaw agent RC={result.returncode}: {result.stderr[:100]}")
            return None
        
        # 解析 JSON 輸出
        try:
            response_data = json.loads(result.stdout)
            # 從 result.payloads[].text 取得實際回應
            payloads = response_data.get("result", {}).get("payloads", [])
            if not payloads:
                print(f"  ⚠ 無 payloads")
                return None
            
            text_response = payloads[0].get("text", "")
            
            # 去除 markdown code block
            text_response = text_response.strip()
            if text_response.startswith("```"):
                lines = text_response.split("\n")
                text_response = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            
            # 嘗試解析 JSON
            # 去除可能的 bom 或空白
            text_response = text_response.strip()
            summary_data = json.loads(text_response)
            
            return summary_data
            
        except json.JSONDecodeError as e:
            # 嘗試手動提取 JSON
            json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            print(f"  ⚠ JSON 解析失敗: {e}")
            print(f"  📄 回應: {text_response[:300]}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"  ⚠ LLM 回應超時（{LLM_TIMEOUT}秒）")
        return None
    except Exception as e:
        print(f"  ⚠ 例外: {e}")
        return None


def get_all_transcript_files(channel_name):
    """取得某頻道的所有字幕檔"""
    channel_dir = EXPERTS_DIR / channel_name
    if not channel_dir.exists():
        return []
    return list(channel_dir.glob("*.txt"))


def get_summarized_ids(channel_name):
    """取得已生成摘要的影片 ID"""
    summary_dir = SUMMARIES_DIR / channel_name
    if not summary_dir.exists():
        return set()
    return {f.stem for f in summary_dir.glob("*.json")}


def get_video_url(video_id):
    """從影片 ID 建構網址"""
    return f"https://www.youtube.com/watch?v={video_id}"


def main():
    print(f"{'='*60}")
    print(f"📝 知識庫 LLM 摘要生成器 v2 - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 讀取狀態
    state = {}
    if STATE_FILE.exists():
        state = json.load(open(STATE_FILE))
    last_channel_idx = state.get("last_channel_index", 0)
    
    total_new = 0
    total_failed = 0
    
    channels = list(CHANNEL_META.keys())
    
    for i in range(len(channels)):
        idx = (last_channel_idx + i) % len(channels)
        channel_id = channels[idx]
        channel_meta = CHANNEL_META[channel_id]
        
        print(f"\n📺 [{idx+1}/{len(channels)}] {channel_meta['name']}")
        
        # 確保摘要目錄存在
        channel_summary_dir = SUMMARIES_DIR / channel_id
        channel_summary_dir.mkdir(parents=True, exist_ok=True)
        
        # 取得所有字幕檔
        transcript_files = get_all_transcript_files(channel_id)
        
        if not transcript_files:
            print(f"  ⚠ 無字幕檔")
            state["last_channel_index"] = (idx + 1) % len(channels)
            json.dump(state, open(STATE_FILE, "w"))
            continue
        
        # 取得已摘要的
        summarized = get_summarized_ids(channel_id)
        new_transcripts = [f for f in transcript_files if f.stem not in summarized]
        
        if not new_transcripts:
            print(f"  ✅ 全部已摘要 ({len(summarized)} 部)")
            state["last_channel_index"] = (idx + 1) % len(channels)
            json.dump(state, open(STATE_FILE, "w"))
            continue
        
        print(f"  🆕 待摘要: {len(new_transcripts)} 部（已有摘要: {len(summarized)} 部）")
        
        # 只處理前2個新字幕（控制時間）
        to_process = new_transcripts[:2]
        success = 0
        
        for tf in to_process:
            video_id = tf.stem
            video_url = get_video_url(video_id)
            
            print(f"  🔄 {video_id}...", end="", flush=True)
            
            # 讀取字幕
            try:
                transcript_text = tf.read_text(encoding="utf-8").strip()
                if len(transcript_text) < 100:
                    print(f"  ⚠ 字幕太短 ({len(transcript_text)} 字)")
                    total_failed += 1
                    continue
            except Exception as e:
                print(f"  ❌ 讀取失敗: {e}")
                total_failed += 1
                continue
            
            # 生成摘要（最多retry 2次）
            summary = None
            for attempt in range(2):
                summary = call_llm_summarize(transcript_text, video_url, channel_id)
                if summary:
                    break
                if attempt < 1:
                    print(f"  🔄 重試...", end="", flush=True)
                    time.sleep(10)
            
            if summary:
                # 保存摘要
                summary_file = channel_summary_dir / f"{video_id}.json"
                summary["_meta"] = {
                    "channel_id": channel_id,
                    "channel_name": channel_meta["name"],
                    "expert": channel_meta["expert"],
                    "area": channel_meta["area"],
                    "video_id": video_id,
                    "video_url": video_url,
                    "transcript_len": len(transcript_text),
                    "generated_at": datetime.now().isoformat(),
                    "raw_file": str(tf)
                }
                
                with open(summary_file, "w", encoding="utf-8") as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
                
                title_short = summary.get("title", "?")[:30]
                print(f"  ✅ [{summary.get('topic', '?')}] {title_short}")
                success += 1
                total_new += 1
            else:
                print(f"  ❌ 摘要失敗（已重試）")
                total_failed += 1
            
            time.sleep(8)  # 避免太快呼叫 LLM
        
        # 更新進度
        state["last_channel_index"] = (idx + 1) % len(channels)
        state["last_run"] = datetime.now().isoformat()
        json.dump(state, open(STATE_FILE, "w"))
        
        # 每輪只處理一個頻道（避免超時）
        break
    
    print(f"\n{'='*60}")
    print(f"📊 結果: {total_new} 個新摘要成功, {total_failed} 個失敗")
    print(f"✅ 完成! 時間: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    return 0 if total_new > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
