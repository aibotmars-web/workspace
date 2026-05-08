# Learnings

Append structured entries:
- LRN-YYYYMMDD-XXX for corrections / best practices / knowledge gaps
- Include summary, details, suggested action, metadata, and status

## 2026-04-07 - 知識庫爬蟲工作流（Mars 確認版）
**來源**：Mars 直接指示
**格式**：回報進度用 (已抓/總數/進度%)
**工具**：只用 kd CLI（kd subtitles / kd transcribe --backend mlx-whisper）
**追蹤**：~/knowledge-base/爬蟲進度追蹤.csv
**注意**：
1. 頻道影片總數要翻到最後一頁確認
2. 會員影片無法抓取，需記錄在追蹤表
3. 避免重複抓取相同內容
4. 持續抓取不停止
