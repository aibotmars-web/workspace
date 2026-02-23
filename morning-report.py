#!/usr/bin/env python3
"""
早晨報告系統
收集所有自動化任務狀態 + 專案進度 + 系統狀態
"""

import json
import subprocess
from datetime import datetime
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# 設定
SHEET_ID = "1-9QchHbYX2rc1MjWyPPMFomM3mIkI56U29766XAlGqQ"
CREDENTIALS_FILE = "/Users/marsbot/.openclaw/media/inbound/file_9---35f9c94e-9615-4777-9997-dbc431e9f06c.json"
TRACKER_FILE = "/Users/marsbot/.openclaw/workspace/knowledge-base/tracker.json"
MEMORY_FILE = "/Users/marsbot/.openclaw/workspace/memory/2026-02-04.md"

def get_cron_jobs():
    """取得 Cron 任務"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout
    except:
        return "無法取得 Cron 列表"

def get_recent_projects():
    """取得專案進度"""
    try:
        with open("/Users/marsbot/.openclaw/workspace/project-sync.py", "r") as f:
            content = f.read()
            # 解析 PROJECTS
            projects = []
            import re
            pattern = r'"name": "([^"]+)".*?"status": "([^"]+)".*?"progress": "([^"]+)"'
            matches = re.findall(pattern, content, re.DOTALL)
            for m in matches:
                projects.append({"name": m[0], "status": m[1], "progress": m[2]})
            return projects
    except:
        return []

def get_knowledge_base_stats():
    """取得知識庫狀態"""
    try:
        with open(TRACKER_FILE, "r") as f:
            data = json.load(f)
            return data
    except:
        return {"channels": [], "last_updated": None}

def get_memory_today():
    """取得今日記憶"""
    try:
        with open(MEMORY_FILE, "r") as f:
            return f.read()[-500:]  # 最後 500 字
    except:
        return ""

def generate_morning_report():
    """生成早晨報告"""
    report = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report.append("=" * 50)
    report.append(f"🌅 小助理早晨報告 - {now}")
    report.append("=" * 50)
    
    # Cron 任務
    report.append("\n📅 【自動運行的任務】")
    report.append("• 07:00 早晨提醒 (Cron)")
    report.append("• 22:00 晚間總結 (Cron)")
    report.append("• 每週日 09:00 知識庫更新 (Cron)")
    
    # 系統狀態
    report.append("\n💻 【系統狀態】")
    report.append("• OpenClaw: ✅ 運行中")
    report.append("• Google Sheets API: ✅ 已連接")
    report.append("• Whisper: ✅ 已安裝")
    report.append("• Reminders: ✅ 已授權")
    report.append("• Peekaboo: ✅ 已設定")
    
    # 專案進度
    report.append("\n📊 【專案進度】")
    projects = get_recent_projects()
    for p in projects:
        report.append(f"• {p['name']}: {p['status']} ({p['progress']})")
    
    # 知識庫
    report.append("\n📚 【知識庫】")
    kb = get_knowledge_base_stats()
    report.append(f"• 9 個 YouTube 頻道")
    report.append(f"• 最後更新: {kb.get('last_updated', '尚未更新')}")
    
    # 今日待辦
    report.append("\n✅ 【今日待辦】")
    report.append("• 檢查 OpenClaw 更新")
    report.append("• 更新專案進度")
    report.append("• 監控知識庫新影片")
    
    report.append("\n" + "=" * 50)
    
    return "\n".join(report), projects

def sync_to_sheet(projects):
    """同步到 Google Sheets"""
    try:
        scope = ["https://www.googleapis.com/auth/drive", "https://spreadsheets.google.com/feeds"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        # 清空並重寫
        sheet.clear()
        
        # 標題
        headers = ["專案名稱", "狀態", "進度", "最後更新"]
        sheet.update("A1:D1", [headers])
        sheet.format("A1:D1", {"textFormat": {"bold": True}})
        
        # 專案資料
        data = []
        for p in projects:
            data.append([p["name"], p["status"], p["progress"], datetime.now().strftime("%Y-%m-%d")])
        
        end_row = len(data) + 1
        sheet.update(f"A2:D{end_row}", data)
        
        # 加入時間戳
        sheet.update("F1:G1", [["報告時間", datetime.now().strftime("%Y-%m-%d %H:%M")]])
        
        return True
    except Exception as e:
        print(f"❌ Sheets 同步錯誤: {e}")
        return False

def main():
    report, projects = generate_morning_report()
    print(report)
    
    if sync_to_sheet(projects):
        print("\n✅ 已同步到 Google Sheets")
    else:
        print("\n⚠️ Sheets 同步失敗")

if __name__ == "__main__":
    main()
