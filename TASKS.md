# TASKS.md - 老闆 Mars 任務清單
*最後更新：2026-03-01*
*這是所有未完成任務的完整清單，由記憶檔整理而來。Planner 每次啟動時請讀這個檔案。*

---

## 🔴 P0 - 最緊急（本週要解決）

### 1. Polymarket 自動交易系統啟動
- **負責：** Trader + Coder
- **狀態：** 🔴 未啟動
- **待做：**
  - [ ] 老闆確認要追蹤哪些市場 ID
  - [ ] 老闆確認資金上限和風險設定
  - [ ] Coder 實作自動下注邏輯
  - [ ] Trader 開始執行（目前只做監控）
- **備註：** 系統架構已有，只差市場設定

### 2. 所有 Sub-Agent 工具確認可用
- **負責：** System-Admin
- **狀態：** 🟡 部分完成
- **待做：**
  - [ ] 確認 youtube-skills 可正常呼叫
  - [ ] 確認 gog (Google Workspace) 可正常呼叫
  - [ ] 確認 bird (X/Twitter) 可正常呼叫
  - [ ] 確認 weather 可正常呼叫
  - [ ] 回報哪些工具有問題

---

## 🟡 P1 - 重要（本月完成）

### 3. 9 位 YouTube 專家知識庫建立
- **負責：** Crawler
- **狀態：** 🟡 Cron 已設定，但不確定是否有在跑
- **專家：** 阿銘師、胡乃文、柏格醫生、周慕姿、松明、Dr. Harvey、初日醫學、泛科學、泛科學院
- **待做：**
  - [ ] Cron 每天 05:00 自動抓字幕（jobs.json 已設定）
  - [ ] 確認 ~/knowledge-base/ 目錄存在
  - [ ] 確認字幕已開始累積
- **備註：** 只抓字幕，不下載影片（硬碟限制）

### 4. Google Sheets 自動更新腳本
- **負責：** Coder
- **狀態：** 🟡 OAuth 完成，腳本未寫
- **待做：**
  - [ ] 寫腳本把 Crawler 的知識庫結果自動填入 Google Sheets
  - [ ] 試算表：https://docs.google.com/spreadsheets/d/10PE52Fmv97I9WSmTzdrjimr_A3Q9X8qCsTAGw8MyuAU
  - [ ] 規則：新資料往上插入
  - [ ] 帳號：aibotmars@gmail.com

### 5. 真相網內容更新
- **負責：** Coder + Crawler
- **狀態：** 🟡 網站已建，內容停滯
- **網址：** https://realtaiwan.github.io/realtaiwan-web/
- **待做：**
  - [ ] Crawler 搜尋最新政治弊案新聞
  - [ ] 整理成文章草稿
  - [ ] Coder 用 realtaiwan token 部署到 GitHub Pages
- **重要：** 身份完全隔離，用 realtaiwan 帳號

### 6. 任務儀表板更新
- **負責：** Coder
- **狀態：** 🟡 網站已建，內容舊了
- **網址：** https://aibotmars-web.github.io/task-dashboard/
- **待做：**
  - [ ] 把這份 TASKS.md 的內容同步到儀表板
  - [ ] 用 aibotmars-web token 部署

---

## 🟢 P2 - 一般（有空做）

### 7. 兒童 AI 繪圖書
- **負責：** Image + Coder
- **狀態：** ⬜ 尚未開始
- **待做：**
  - [ ] 老闆確認主題和風格
  - [ ] Image 用 MiniMax 生成插圖（10-15 張）
  - [ ] Coder 整合成 PDF 或網頁

### 8. 跨境電商（淘寶→蝦皮/亞馬遜）
- **負責：** 待確認
- **狀態：** ⬜ 尚未開始
- **待做：**
  - [ ] 老闆確認具體需求和預算

### 9. App 開發
- **負責：** Coder
- **狀態：** ⬜ 尚未開始
- **待做：**
  - [ ] 老闆確認 App 的功能需求

### 10. SSH 互連救援（Mac ↔ Windows）
- **負責：** System-Admin
- **狀態：** ⬜ 等 Windows 安裝完成
- **待做：**
  - [ ] 老闆在 Windows 安裝 OpenClaw
  - [ ] 設定 Tailscale 互連
  - [ ] 設定 SSH 金鑰

### 11. OpenClaw auto-fix 腳本 macOS 版
- **負責：** Coder
- **狀態：** 🟡 原版是 Linux systemd，需改造
- **待做：**
  - [ ] 改造 exec-fix-v6.sh 為 macOS LaunchAgent 版本

---

## ✅ 已完成（歸檔）

- ✅ Beads (BD) 任務追蹤系統安裝
- ✅ 8 個 Sub-Agent 設定
- ✅ Telegram 群組對應設定
- ✅ GitHub 帳號建立（aibotmars-web, realtaiwan）
- ✅ 任務儀表板網站建立
- ✅ 真相網網站建立
- ✅ Google OAuth 認證（aibotmars@gmail.com）
- ✅ Voyage AI 設定（記憶搜尋）
- ✅ memory-lancedb-pro 安裝
- ✅ 早晨/晚間 cron job 設定
- ✅ Telegram 連線修復（retry 設定）
- ✅ 所有 AGENTS.md 完整重寫（2026-03-01）

---

## 📋 Planner 工作指引

每次啟動時：
1. 讀這個 TASKS.md
2. 選 P0 任務開始推進
3. 分配具體工作給 sub-agent（要說清楚做什麼、怎麼做）
4. 追蹤進度，遇到卡住就記錄原因並標記

給 sub-agent 的指令範例（好的）：
> "Coder，請寫一個 Python 腳本，讀取 ~/knowledge-base/ 下所有今天的 .md 檔，提取標題和重點，用 gog sheets 插入到試算表 [URL] 的第一行。完成後回報結果。"

給 sub-agent 的指令範例（不好的）：
> "幫我做 Google Sheets 整合"
