#!/usr/bin/env python3
"""
MiniMax Coding Plan 用量查詢工具
"""
import requests
import json
import sys

API_KEY = "sk-cp-zBE1lcRUibZCRRYCuwSJv_HIpvekBW0YsZTEL17h1giYy2KqDOwJ4QoaBtuExUmuE8NQWOHz-P1dtBAF3jKkBrKEs3336Gpr0e6L-wRlMROa4-3V-dwc5Ws"

# 嘗試多個 API 端點
endpoints = [
    ("https://api.minimaxi.com/v1/usage", {"model": "abab6.5s-chat"}),
    ("https://platform.minimaxi.com/v1/usage", {"model": "abab6.5s-chat"}),
    ("https://www.minimaxi.com/v1/usage", {"model": "abab6.5s-chat"}),
]

print("🔍 查詢 MiniMax Coding Plan 用量...\n")

for url, data in endpoints:
    try:
        resp = requests.post(url, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }, json=data, timeout=10)
        
        if resp.status_code != 404:
            print(f"✅ 端點: {url}")
            print(f"狀態: {resp.status_code}")
            print(f"回應: {resp.text[:500]}")
            print()
    except Exception as e:
        print(f"❌ {url}: {e}")

print("=" * 50)
print("如果以上都失敗，請手動訪問：")
print("https://platform.minimaxi.com/user-center/payment/coding-plan")
