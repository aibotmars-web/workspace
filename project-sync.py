#!/usr/bin/env python3
"""
專案儀表板同步程式
自動更新 Google Sheets
"""

import json
from datetime import datetime
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# 設定
SHEET_ID = "1-9QchHbYX2rc1MjWyPPMFomM3mIkI56U29766XAlGqQ"
CREDENTIALS_FILE = "/Users/marsbot/.openclaw/media/inbound/file_9---35f9c94e-9615-4777-9997-dbc431e9f06c.json"

# 專案資料（之後可擴充）
PROJECTS = [
    {
        "name": "真相網",
        "category": "資訊",
        "status": "🔴 未開始",
        "progress": "0%",
        "today_progress": "",
        "next_step": "規劃平台功能",
        "notes": "AI 新聞平台"
    },
    {
        "name": "OpenClaw 每日監控",
        "category": "資訊",
        "status": "✅ 已建立腳本",
        "progress": "100%",
        "today_progress": "建立監控系統",
        "next_step": "設定 Sheet ID",
        "notes": "自動檢查更新/安全/Skills"
    },
    {
        "name": "YouTube 內容頻道",
        "category": "賺錢",
        "status": "🔴 未開始",
        "progress": "0%",
        "today_progress": "",
        "next_step": "選擇方向",
        "notes": ""
    },
    {
        "name": "Polymarket 自動交易",
        "category": "賺錢",
        "status": "🔴 未開始",
        "progress": "0%",
        "today_progress": "",
        "next_step": "研究 API",
        "notes": ""
    },
    {
        "name": "兒童 AI 繪圖書",
        "category": "賺錢",
        "status": "🔴 未開始",
        "progress": "0%",
        "today_progress": "",
        "next_step": "找繪圖工具",
        "notes": ""
    },
    {
        "name": "9 頻道知識庫",
        "category": "知識",
        "status": "🔴 進行中",
        "progress": "10%",
        "today_progress": "建立追蹤腳本",
        "next_step": "修復字幕抓取",
        "notes": "yt-dlp 需要 deno runtime"
    },
]

def sync_to_sheet():
    """同步到 Google Sheets"""
    print("🚀 專案儀表板同步...")
    
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        
        # 建立或開啟 Sheet
        try:
            sheet = client.open("專案儀表板").sheet1
        except:
            sheet = client.create("專案儀表板").sheet1
            sheet.share("marsbot@gmail.com", perm_type="user", role="writer")
        
        # 標題
        headers = ["專案名稱", "類別", "狀態", "進度", "今日進步", "下一步", "筆記", "最後更新"]
        sheet.update("A1:H1", [headers])
        sheet.format("A1:H1", {"textFormat": {"bold": True}})
        
        # 更新資料
        data = []
        for p in PROJECTS:
            row = [
                p["name"],
                p["category"],
                p["status"],
                p["progress"],
                p["today_progress"],
                p["next_step"],
                p["notes"],
                datetime.now().strftime("%Y-%m-%d")
            ]
            data.append(row)
        
        end_row = len(PROJECTS) + 1
        sheet.update(f"A2:H{end_row}", data)
        
        print(f"✅ 已更新 {len(PROJECTS)} 個專案")
        return True
        
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return False

if __name__ == "__main__":
    sync_to_sheet()
