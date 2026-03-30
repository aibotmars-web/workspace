#!/usr/bin/env python3
"""
知識庫爬蟲 Wrapper - Cron 觸發這個檔案
實際執行 crawl_subtitles.py + crawl_asr.py
"""
import subprocess, os, sys
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "knowledge-base"

# 字幕版（快速）
print("🚀 字幕頻道爬蟲...")
r1 = subprocess.run(["python3", "crawl_subtitles.py"], cwd=WORKSPACE, capture_output=True, text=True)
print(r1.stdout[-500:] if r1.stdout else "")
if r1.returncode != 0:
    print("字幕版錯誤:", r1.stderr[-200:] if r1.stderr else "")

# ASR版（慢速，每次只處理 2 部）
print("\n🎤 ASR 轉錄爬蟲...")
r2 = subprocess.run(["python3", "crawl_asr.py"], cwd=WORKSPACE, capture_output=True, text=True, timeout=600)
print(r2.stdout[-500:] if r2.stdout else "")
if r2.returncode != 0:
    print("ASR版錯誤:", r2.stderr[-200:] if r2.stderr else "")

print("\n✅ 完成!")
