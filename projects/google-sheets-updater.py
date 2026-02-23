#!/usr/bin/env python3
"""
Google Sheets 更新工具
功能：將爬蟲結果自動更新到 Google Sheets

使用方式：
1. 先執行爬蟲取得 JSON 結果
2. 執行此腳本將結果寫入 Google Sheets

前置需求：
- pip install gspread oauth2client
- 需有 service_account.json 或完成 OAuth 認證
"""

import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==== 配置 ====
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/10PE52Fmv97I9WSmTzdrjimr_A3Q9X8qCsTAGw8MyuAU"
CREDENTIALS_FILE = "~/.openclaw/google-sheets/credentials.json"
CREDENTIALS_EMAIL = "aibotmars@gmail.com"

# ==== Google Sheets 連線 ====
def connect_google_sheets():
    """連線到 Google Sheets"""
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # 使用 OAuth 2.0 認證
    # 如果有 service_account.json，使用以下方式：
    # credentials = ServiceAccountCredentials.from_json_keyfile_name(
    #     CREDENTIALS_FILE, scope)
    
    # 如果使用使用者帳號（aibotmars@gmail.com）
    # 需要先完成 OAuth 認證流程
    gc = gspread.oauth(credentials_filename=CREDENTIALS_FILE)
    
    # 打開試算表
    sh = gc.open_by_url(SPREADSHEET_URL)
    return sh

# ==== 寫入函數 ====
def insert_video_to_sheet(sh, video_data):
    """往上插入新影片資料"""
    # 選擇第一個工作表
    worksheet = sh.sheet1
    
    # 資料格式
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),  # A: 時間戳記
        video_data.get('channel_name', ''),         # B: 頻道名稱
        video_data.get('video_title', ''),           # C: 影片標題
        video_data.get('video_url', ''),             # D: 影片網址
        video_data.get('publish_date', ''),          # E: 發布日期
        video_data.get('summary', ''),               # F: 摘要
        video_data.get('expert_category', ''),       # G: 專家類別
    ]
    
    # 往上插入新列
    worksheet.insert_row(row, 2)  # 第 2 列（標題列在第 1 列）
    
    print(f"✅ 已插入：{row[1]} - {row[2]}")

# ==== 主程式 ====
def main():
    """主程式入口"""
    print("=== Google Sheets 更新工具 ===")
    
    # 測試連線
    try:
        sh = connect_google_sheets()
        print(f"✅ 已連線：{sh.title}")
    except Exception as e:
        print(f"❌ 連線失敗：{e}")
        print("請先完成 OAuth 認證！")
        return
    
    # 測試資料（實際使用時會從爬蟲取得）
    test_data = {
        'channel_name': '測試頻道',
        'video_title': '測試影片',
        'video_url': 'https://youtube.com/watch?v=xxx',
        'publish_date': '2026-02-07',
        'summary': '這是測試摘要',
        'expert_category': '健康'
    }
    
    # 插入測試資料
    insert_video_to_sheet(sh, test_data)

if __name__ == "__main__":
    main()
