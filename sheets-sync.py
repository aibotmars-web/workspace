#!/usr/bin/env python3
"""
Google Sheets 自動同步腳本
使用 uv 執行
"""

import subprocess
import sys

# 確保使用 uv 執行
def run_with_uv(script_path):
    cmd = ["uv", "run", "--with", "gspread", "python", script_path]
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "sheets-sync-internal.py")
    
    # 讀取資料
    INCOME_DATA = [
        ["月份", "日期", "存入", "結餘", "備註"],
        ["2026/01", "01/21", 1, 66694, "藍新科技轉帳"],
        ["2026/01", "01/19", 26530, 79413, "勞保就保給付"],
        ["2026/01", "01/15", 10000, 55883, "統一數網貨款"],
        ["2026/01", "01/15", 47, 45883, "SHOPEE 代付轉"],
        ["2026/01", "01/12", 29996, 30587, "SHOPEE 代付轉"],
        ["2026/01", "01/08", 10000, 10464, "機車款"],
        ["2026/01", "01/05", 270, 19274, "SHOPEE 代付轉"],
        ["2026/01", "01/02", 468, 35049, "蘭芳園"],
        ["2025/12", "12/23", 26530, 57970, "勞保就保給付"],
        ["2025/12", "12/05", 8521, 75155, "薪資"],
        ["2025/12", "12/05", 4385, 66634, "FEDI"],
        ["2025/12", "12/26", 2650, 49368, ""],
        ["2025/12", "12/18", 1500, 46530, "握推椅"],
        ["2025/11", "11/14", 1653, 87662, "茂揚林嘉俊代"],
        ["2025/11", "11/12", 10000, 76009, "行政院發年金"],
        ["2025/11", "11/06", 3802, 97731, "茂揚林嘉俊代"],
        ["2025/11", "11/05", 20529, 93929, "薪資"],
        ["2025/11", "11/05", 17000, 73400, ""],
        ["2025/11", "11/04", 44800, 90415, ""],
    ]
    
    print("🚀 開始同步...")
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # 設定
        SHEET_ID = "1-blha8M8QCY1eX63iHtaxFXRhCnm-GqMAFwKkac2Mfc"
        CREDENTIALS_FILE = "/Users/marsbot/.openclaw/media/inbound/file_9---35f9c94e-9615-4777-9997-dbc431e9f06c.json"
        
        # 連線
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
        client = gspread.authorize(creds)
        
        # 打開 Sheet
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        # 清空並寫入
        sheet.clear()
        sheet.update("A1:E20", INCOME_DATA)
        
        # 格式化標題
        sheet.format("A1:E1", {"textFormat": {"bold": True}})
        
        print("✅ 同步完成！")
        
    except ImportError:
        print("❌ gspread 未安裝，使用 uv 執行：")
        print("uv run --with gspread python3 /Users/marsbot/.openclaw/workspace/sheets-sync.py")
    except Exception as e:
        print(f"❌ 錯誤：{e}")
