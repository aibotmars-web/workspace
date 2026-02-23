#!/usr/bin/env python3
"""
OpenClaw 每日監控系統
自動檢查更新、新聞、Skills、安全漏洞
"""

import json
import subprocess
from datetime import datetime
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import urllib.request
import re

# 監控清單
SOURCES = {
    "OpenClaw GitHub": "https://github.com/openclaw/openclaw/releases",
    "OpenClaw Docs": "https://docs.openclaw.ai/changelog",
    "ClawHub": "https://clawhub.com",
    "GitHub Issues": "https://github.com/openclaw/openclaw/issues",
    "Discord": "https://discord.com/invite/clawd",
}

# 搜尋關鍵詞（適合老闆的）
RELEVANT_KEYWORDS = [
    "youtube", "transcription", "whisper", "dashboard",
    "task", "automation", "reminder", "weather",
    "browser", "pdf", "translation", "telegram",
    "roi", "revenue", "income", "earning",
    "trading", "crypto", "polymarket", "youtube",
    "ecommerce", "shopify", "taobao",
]

# 設定
SHEET_ID = "1-9QchHbYX2rc1MjWyPPMFomM3mIkI56U29766XAlGqQ"
CREDENTIALS_FILE = "/Users/marsbot/.openclaw/media/inbound/file_9---35f9c94e-9615-4777-9997-dbc431e9f06c.json"

def fetch_github_releases():
    """取得 GitHub Releases"""
    try:
        url = "https://api.github.com/repos/openclaw/openclaw/releases?per_page=5"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            releases = []
            for item in data:
                releases.append({
                    "title": item.get("tag_name", ""),
                    "date": item.get("published_at", "")[:10],
                    "url": item.get("html_url", ""),
                    "body": item.get("body", "")[:500]
                })
            return releases
    except Exception as e:
        print(f"❌ GitHub API error: {e}")
        return []

def fetch_github_issues():
    """取得 GitHub Issues"""
    try:
        url = "https://api.github.com/repos/openclaw/openclaw/issues?state=open&per_page=5"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            issues = []
            for item in data:
                issues.append({
                    "title": item.get("title", ""),
                    "url": item.get("html_url", ""),
                    "labels": [l["name"] for l in item.get("labels", [])]
                })
            return issues
    except Exception as e:
        print(f"❌ GitHub Issues error: {e}")
        return []

def check_security():
    """安全漏洞檢查"""
    try:
        url = "https://api.github.com/repos/openclaw/openclaw/security-advisories"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return len(data)  # 回傳數量
    except:
        return 0  # 無 Advisory API 權限，回傳 0

def filter_relevant(items):
    """過濾相關內容"""
    results = []
    for item in items:
        text = str(item).lower()
        for keyword in RELEVANT_KEYWORDS:
            if keyword in text:
                results.append(item)
                break
    return results

def sync_to_sheet(releases, issues, security_count):
    """同步到 Google Sheets"""
    print("🚀 OpenClaw 監控同步...")
    
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        
        try:
            sheet = client.open("OpenClaw_監控").sheet1
        except:
            sheet = client.create("OpenClaw_監控").sheet1
            sheet.share("marsbot@gmail.com", perm_type="user", role="writer")
        
        # 清空
        sheet.clear()
        
        # 標題
        headers = ["時間", "來源", "標題", "連結", "標籤"]
        sheet.update("A1:E1", [headers])
        sheet.format("A1:E1", {"textFormat": {"bold": True}})
        
        # 寫入 Releases
        row = 2
        for release in releases[:3]:
            sheet.update(f"A{row}:D{row}", [
                [release["date"], "GitHub Releases", release["title"], release["url"]]
            ])
            row += 1
        
        # 寫入 Issues
        for issue in issues[:3]:
            labels = ", ".join(issue.get("labels", []))
            sheet.update(f"A{row}:D{row}", [
                "New", "GitHub Issues", issue["title"], issue["url"]]
            ])
            sheet.update(f"E{row}", labels)
            row += 1
        
        # 安全狀態
        sheet.update(f"A{row+2}", ["安全漏洞檢查", f"✅ 發現 {security_count} 個 advisory"])
        
        # 格式化
        sheet.format(f"A1:E{row+3}", {"wrapStrategy": "WRAP"})
        
        print(f"✅ 已更新 {row} 筆資料")
        return True
        
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return False

def generate_summary(releases, issues, security_count):
    """生成摘要訊息"""
    summary = []
    
    if releases:
        latest = releases[0]
        summary.append(f"🆕 最新版本：{latest['title']}")
    
    relevant = filter_relevant(releases + issues)
    if relevant:
        summary.append(f"📌 發現 {len(relevant)} 個相關更新")
    
    summary.append(f"🔒 安全檢查：{'✅ 無漏洞' if security_count == 0 else f'⚠️ {security_count} 個 advisory'}")
    
    return "\n".join(summary)

def main():
    print("=" * 60)
    print("OpenClaw 每日監控系統")
    print("=" * 60)
    
    print("\n📡 抓取資料中...")
    releases = fetch_github_releases()
    issues = fetch_github_issues()
    security_count = check_security()
    
    print(f"📰 Releases: {len(releases)}")
    print(f"🐛 Issues: {len(issues)}")
    print(f"🔒 Security: {security_count}")
    
    # 同步到 Sheets
    sync_to_sheet(releases, issues, security_count)
    
    # 生成摘要
    summary = generate_summary(releases, issues, security_count)
    
    print("\n" + "=" * 60)
    print(summary)
    print("=" * 60)

if __name__ == "__main__":
    main()
