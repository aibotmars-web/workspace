#!/usr/bin/env python3
"""
Google OAuth 認證腳本
引導老闆完成登入流程
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

CREDS_FILE = "agent/client_secrets.json"
TOKEN_FILE = "agent/token.json"

def main():
    print("=" * 60)
    print("Google OAuth 認證")
    print("=" * 60)
    print()
    print("即將打開瀏覽器進行 Google 登入...")
    print("請用您的 Google 帳號登入並授權")
    print()
    
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if creds and creds.valid:
            print("✓ 已經完成認證！")
            print(f"Token 過期時間: {creds.expiry}")
            return
    
    if not os.path.exists(CREDS_FILE):
        print(f"錯誤: 找不到 {CREDS_FILE}")
        print("請先設定 client_secrets.json")
        return
    
    # 啟動 OAuth 流程
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
    
    print("正在啟動認證流程...")
    print("請在瀏覽器中完成登入")
    print()
    
    creds = flow.run_local_server(port=8080)
    
    # 保存 token
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    print("✓ 認證成功！")
    print(f"Token 已保存到: {TOKEN_FILE}")
    print(f"過期時間: {creds.expiry}")

if __name__ == "__main__":
    main()
