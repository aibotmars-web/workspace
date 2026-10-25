#!/usr/bin/env python3
"""
知識庫統一狀態管理器 (KB Unified State Manager)
所有爬蟲和 sub-agent 都必須使用這個腳本來讀寫進度

用法:
  python3 kb-state-manager.py read              # 讀取目前進度
  python3 kb-state-manager.py update <channel> <count>  # 更新已爬數量
  python3 kb-state-manager.py report            # 生成進度報告
  python3 kb-state-manager.py check             # 檢查問題
  python3 kb-state-manager.py sync_from_crawl  # ⭐ 從 crawl_state.json 同步（即時資料源）
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"
STATE_FILE = WORKSPACE / "kb-unified-state.json"
PROGRESS_CSV = WORKSPACE / "kb-progress.csv"

def load_state():
    """讀取統一狀態檔"""
    if not STATE_FILE.exists():
        print(f"❌ 錯誤: {STATE_FILE} 不存在！")
        sys.exit(1)
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    """寫入統一狀態檔"""
    state["_meta"] = {
        "last_modified": datetime.now().isoformat(),
        "last_modified_by": os.environ.get("USER", "unknown")
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def cmd_read():
    """顯示目前進度"""
    state = load_state()
    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║       🧠 知識庫統一進度 ({state.get('_meta',{}).get('last_modified','N/A')[:10]})     ║")
    print(f"╚══════════════════════════════════════════════════════════╝")
    print()
    
    total_crawled = 0
    total_videos = 0
    total_summaries = 0
    
    print(f"{'頻道':<18} {'顯示名稱':<14} {'已爬':<6} {'總數':<6} {'進度':<8} {'摘要':<6} {'上次爬取'}")
    print("-" * 90)
    
    for channel_id, info in state.get("channels", {}).items():
        crawled = info.get("crawled_count", 0)
        total = info.get("total_videos", 0)
        summaries = info.get("summary_count", 0)
        last = info.get("last_crawled", "N/A")[:10] if info.get("last_crawled") else "N/A"
        display = info.get("display_name", channel_id)
        
        pct = f"{crawled/total*100:.0f}%" if total > 0 else "-"
        
        print(f"{channel_id:<18} {display:<14} {crawled:<6} {total:<6} {pct:<8} {summaries:<6} {last}")
        
        total_crawled += crawled
        total_videos += total
        total_summaries += summaries
    
    print("-" * 90)
    overall_pct = f"{total_crawled/total_videos*100:.0f}%" if total_videos > 0 else "-"
    print(f"{'總計':<18} {'':<14} {total_crawled:<6} {total_videos:<6} {overall_pct:<8} {total_summaries}")
    print()

def cmd_update(channel_id, crawled_count):
    """更新頻道的已爬數量"""
    state = load_state()
    
    if channel_id not in state.get("channels", {}):
        print(f"❌ 錯誤: 頻道 '{channel_id}' 不存在")
        print(f"可用頻道: {', '.join(state.get('channels', {}).keys())}")
        sys.exit(1)
    
    state["channels"][channel_id]["crawled_count"] = int(crawled_count)
    state["channels"][channel_id]["last_crawled"] = datetime.now().isoformat()
    state["last_run"] = datetime.now().isoformat()
    
    save_state(state)
    print(f"✅ 已更新 {channel_id}: 已爬 {crawled_count} 部")

def cmd_update_ids(channel_id, video_ids_list):
    """更新頻道已爬的影片 ID 清單（用於去重）"""
    state = load_state()
    
    if channel_id not in state.get("channels", {}):
        print(f"❌ 錯誤: 頻道 '{channel_id}' 不存在")
        sys.exit(1)
    
    ids = json.loads(video_ids_list) if isinstance(video_ids_list, str) else video_ids_list
    
    state["channels"][channel_id]["crawled_ids"] = ids
    state["channels"][channel_id]["crawled_count"] = len(ids)
    state["channels"][channel_id]["last_crawled"] = datetime.now().isoformat()
    state["last_run"] = datetime.now().isoformat()
    
    save_state(state)
    print(f"✅ 已更新 {channel_id}: 已爬 {len(ids)} 部 (ID清單)")

def cmd_summary_update(channel_id, summary_count):
    """更新頻道的摘要數量"""
    state = load_state()
    
    if channel_id not in state.get("channels", {}):
        print(f"❌ 錯誤: 頻道 '{channel_id}' 不存在")
        sys.exit(1)
    
    state["channels"][channel_id]["summary_count"] = int(summary_count)
    state["channels"][channel_id]["last_summary"] = datetime.now().isoformat()
    state["last_summary_run"] = datetime.now().isoformat()
    
    save_state(state)
    print(f"✅ 已更新 {channel_id}: 摘要 {summary_count} 筆")

def cmd_report():
    """生成 CSV 進度報告"""
    state = load_state()
    
    csv_lines = ["頻道,YouTube總數,已爬,進度%,摘要數,上次爬取,狀態,備註"]
    
    for channel_id, info in state.get("channels", {}).items():
        crawled = info.get("crawled_count", 0)
        total = info.get("total_videos", 0)
        summaries = info.get("summary_count", 0)
        last = info.get("last_crawled", "N/A")[:10] if info.get("last_crawled") else "N/A"
        status = info.get("status", "unknown")
        note = info.get("note", "")
        pct = f"{crawled/total*100:.0f}%" if total > 0 else "0%"
        
        csv_lines.append(f"{channel_id},{total},{crawled},{pct},{summaries},{last},{status},{note}")
    
    with open(PROGRESS_CSV, "w") as f:
        f.write("\n".join(csv_lines))
    
    print(f"✅ 進度報告已生成: {PROGRESS_CSV}")
    print()
    for line in csv_lines:
        print(line)

def cmd_check():
    """檢查知識庫問題"""
    state = load_state()
    
    print("━━━ 問題檢查 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    issues = []
    
    # 檢查停滯的頻道
    now = datetime.now()
    for channel_id, info in state.get("channels", {}).items():
        last_crawled = info.get("last_crawled")
        if last_crawled:
            try:
                last_date = datetime.fromisoformat(last_crawled.replace("Z", ""))
                days_ago = (now - last_date).days
                if days_ago > 7:
                    issues.append(f"⚠️  {channel_id}: 已停止 {days_ago} 天（上次: {last_crawled[:10]}）")
            except:
                pass
    
    # 檢查摘要落後
    for channel_id, info in state.get("channels", {}).items():
        crawled = info.get("crawled_count", 0)
        summaries = info.get("summary_count", 0)
        if summaries < crawled * 0.5 and crawled > 10:
            pct = summaries/crawled*100 if crawled > 0 else 0
            issues.append(f"⚠️  {channel_id}: 摘要落後 {summaries}/{crawled} ({pct:.0f}%)")
    
    # 檢查超真實商談
    if "超真實商談" in state.get("superseded_channels", {}):
        issues.append(f"⚠️  超真實商談 已停用（已合併至 RealBizChat）")
    
    # 檢查落後的頻道
    for channel_id, info in state.get("channels", {}).items():
        crawled = info.get("crawled_count", 0)
        total = info.get("total_videos", 0)
        if total > 0 and crawled/total < 0.3:
            issues.append(f"📍 {channel_id}: 進度落後 {crawled}/{total} ({crawled/total*100:.0f}%)")
    
    if not issues:
        print("✅ 沒有發現重大問題")
    else:
        for issue in issues:
            print(issue)
    
    print()
    
    # 顯示統一路徑
    print("━━━ 統一檔案路徑 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📁 統一狀態檔: {STATE_FILE}")
    print(f"📊 進度報告: {PROGRESS_CSV}")
    print(f"📁 專家資料: {WORKSPACE}/experts/")
    print(f"📁 摘要資料: {WORKSPACE}/summaries/")
    print()
    
    # 顯示 summary 落後最多的頻道
    print("━━━ 摘要加速優先順序 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    summary_list = []
    for channel_id, info in state.get("channels", {}).items():
        crawled = info.get("crawled_count", 0)
        summaries = info.get("summary_count", 0)
        if summaries < crawled:
            summary_list.append((channel_id, summaries, crawled, crawled - summaries))
    
    summary_list.sort(key=lambda x: x[3], reverse=True)
    for channel_id, summaries, crawled, backlog in summary_list[:5]:
        print(f"  {channel_id}: {summaries} 摘要 / {crawled} 已爬 (落後 {backlog})")

def cmd_sync_from_crawl():
    """從 crawl_state.json（即時、活的）同步進度到 kb-unified-state.json + kb-progress.csv
    
    用法：python3 kb-state-manager.py sync_from_crawl
    
    為什麼要這個？
    - kb-unified-state.json 由舊版爬蟲寫，2026-05 之後就沒再更新（殭屍）
    - crawl_state.json 是 crawl_stable.py（新版）寫的，每輪 04:00/15:00 即時更新
    - 每日報告原本讀 kb-progress.csv（從殭屍 JSON 生成），結果每天回報一模一樣的「停滯 N 天」
    - 這個指令把活的 crawl_state.json 同步給舊報表，讓報表準確
    """
    crawl_state_file = WORKSPACE / "crawl_state.json"
    if not crawl_state_file.exists():
        print(f"❌ crawl_state.json 不存在：{crawl_state_file}")
        sys.exit(1)
    
    crawl_state = json.load(open(crawl_state_file))
    crawl_channels = crawl_state.get("channels", {})
    
    # 1. 更新統一狀態檔
    unified_state_file = WORKSPACE / "kb-unified-state.json"
    if unified_state_file.exists():
        unified = json.load(open(unified_state_file))
    else:
        unified = {"channels": {}}
    
    unified.setdefault("channels", {})
    now_iso = datetime.now().isoformat()
    
    # 建立 display_name → username 的反向索引
    # 解決「中文 key 與英文 username key 並存」的雙胞胎問題
    # 例如：crawl_state 用「松明讲心理」，但統一狀態早就用 SongMing 為 key
    display_to_username = {}
    for ukey, uinfo in unified["channels"].items():
        dn = uinfo.get("display_name", "")
        if dn and ukey not in display_to_username.values():
            display_to_username[dn] = ukey

    # 從 crawl_stable.py 引入完整 CHANNELS（含 display_name 與 username 對應）
    try:
        from crawl_stable import CHANNELS as CRAWL_CHANNELS
        name_to_username = {name: username for name, username in CRAWL_CHANNELS}
    except Exception:
        name_to_username = {}

    synced = 0
    for ch_name, info in crawl_channels.items():
        ch_id = ch_name  # CHANNELS 列表中（name, username）name 已經是資料夾名
        ch_info = unified["channels"].setdefault(ch_id, {})
        ch_info["total_videos"] = info.get("total", 0)
        ch_info["crawled_count"] = info.get("crawled", 0)
        ch_info["last_crawled"] = info.get("last_updated", now_iso)
        ch_info["display_name"] = ch_name
        ch_info["status"] = "active"
        synced += 1

        # 同時更新對應的英文 username key（如果存在），避免 CSV 顯示的英文 key 永遠停在 5 月
        # 優先順序：1) crawl_stable 的 CHANNELS 對應 2) display_name 反查
        username_key = name_to_username.get(ch_name) or display_to_username.get(ch_name)
        if username_key and username_key != ch_id:
            u_info = unified["channels"].setdefault(username_key, {})
            u_info["total_videos"] = info.get("total", 0)
            u_info["crawled_count"] = info.get("crawled", 0)
            u_info["last_crawled"] = info.get("last_updated", now_iso)
            u_info["display_name"] = ch_name
            u_info["status"] = "active"
            synced += 1
    
    save_state(unified)
    
    # 2. 重新生成 CSV（用統一狀態的 cmd_report）
    cmd_report()
    
    print(f"✅ 已從 crawl_state.json 同步 {synced} 個頻道")
    print(f"   統一狀態: {STATE_FILE}")
    print(f"   進度報告: {PROGRESS_CSV}")


def cmd_sync_experts():
    """同步專家目錄中的實際檔案數量到狀態檔"""
    state = load_state()
    experts_dir = WORKSPACE / "experts"
    summaries_dir = WORKSPACE / "summaries"
    
    for channel_id in state.get("channels", {}):
        channel_dir = experts_dir / channel_id
        
        # 計算實際檔案數
        if channel_dir.exists():
            video_ids = set()
            for f in channel_dir.iterdir():
                if f.is_file():
                    name = f.stem
                    # 去掉語言後綴
                    if "." in name:
                        name = name.rsplit(".", 1)[0]
                    if len(name) > 5:
                        video_ids.add(name)
            
            actual_count = len(video_ids)
            state["channels"][channel_id]["crawled_count"] = actual_count
        
        # 計算摘要數
        summary_dir = summaries_dir / channel_id
        if summary_dir.exists():
            summary_count = len(list(summary_dir.glob("*.json")))
            state["channels"][channel_id]["summary_count"] = summary_count
    
    save_state(state)
    print("✅ 已同步專家目錄的實際數量到統一狀態檔")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "read":
        cmd_read()
    elif cmd == "update" and len(sys.argv) >= 4:
        cmd_update(sys.argv[2], sys.argv[3])
    elif cmd == "update_ids" and len(sys.argv) >= 4:
        cmd_update_ids(sys.argv[2], json.loads(sys.argv[3]) if sys.argv[3].startswith("[") else sys.argv[3])
    elif cmd == "summary_update" and len(sys.argv) >= 4:
        cmd_summary_update(sys.argv[2], sys.argv[3])
    elif cmd == "report":
        cmd_report()
    elif cmd == "check":
        cmd_check()
    elif cmd == "sync":
        cmd_sync_experts()
    elif cmd == "sync_from_crawl":
        cmd_sync_from_crawl()
    else:
        print(f"未知指令: {cmd}")
        print(__doc__)
        sys.exit(1)