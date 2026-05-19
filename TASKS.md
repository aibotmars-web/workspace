# TASKS.md - 老闆 Mars 任務清單
*最後更新：2026-05-16 14:00（Auto-Task-Runner 例行檢查）*
*這是所有未完成任務的完整清單，涵蓋 OpenClaw + Cowork session 所有待辦。*
*🤖 Auto-Task-Runner（auto-task-runner-001）每 2 小時自動推進本清單，跳過標有「需老闆確認」的任務。*
*🛠️ 工作流程：gstack sprint（Think → Plan → Build → Review → Test → Ship）+ DeerFlow 深度研究*
*📦 工具：/office-hours（規劃）、/review（程式碼審查）、/qa（品質確認）、/ship（部署）、DeerFlow（深度研究，http://localhost:8001）*

---

## 🔴 P0 - 最緊急（本週要解決）

### 1. OpenClaw 版本管理
- **負責：** System-Admin（🤖 Auto可自主執行）
- **狀態：** ✅ 目前版本 v2026.5.7（2026-05-09）
- **版本歷史：**
  - v2026.4.2 → 完成遷移（2026-04-04）
  - v2026.5.7 → 系統自動升級（2026-05-09）
- **說明：** 系統已從 v2026.4.2 升至 v2026.5.7，共經過 4 個 minor 版本（5.3→5.4→5.5→5.6→5.7）。v2026.5.7 重點：ClawHub publish 修復、Discord target parse 修復、cron status JSON 增強、Codex/OpenAI model 新增。
- **已驗證：** openclaw --version 回傳 2026.5.7 (eeef486)，Gateway 正常運行

### 2. YouTube 知識庫 LLM 總結超時修復
- **負責：** Coder（🤖 Auto可自主執行）
- **狀態：** ✅ 已修復（2026-04-04）
- **根本原因：** `crawl_stable.py` 只下載字幕，沒有內建 LLM 摘要流程
- **修復方案：** 
  - 新建 `summarize_transcripts.py`：使用 `openclaw agent --session-id` 叫用 MiniMax LLM 生成結構化 JSON 摘要
  - 每輪處理 1 個頻道、2 部新影片，控制 LLM 呼叫時間
  - 加入 retry 邏輯（最多 2 次）
  - 更新 `crawler-knowledge-001` cron job 加入摘要步驟
- **已驗證：** 成功生成 6 個摘要（Dr.HuangAmin x2, Dr.Hu_talk x2, drbergchinese x2）
- **待做：**
  - [x] 建立 `summarize_transcripts.py`（2026-04-04）
  - [x] 更新 `crawler-knowledge-001` cron job（2026-04-04）
  - [x] 測試驗證（2026-04-04，已生成首批摘要）
  - [ ] ⚠️ 持續積累：cron job 每週期會自動生成 2+ 個新摘要

### 3. Polymarket 自動交易系統啟動
- **負責：** Trader + Coder
- **狀態：** 🔴 等待老闆確認
- **待做：**
  - [ ] ⚠️ 需老闆確認：要追蹤哪些市場 ID（目前 polymarket-bot.py 裡是佔位符 `0x1234...`）
  - [ ] ⚠️ 需老闆確認：每次下注上限（目前設定 $10/次）、止損設定（-0.3%）
  - [ ] 確認後：Coder 填入實際市場 ID 到 `~/.openclaw/workspace/projects/polymarket-bot.py`
  - [ ] Trader 開始執行（目前只做監控）
- **🤖 Auto跳過：** 前兩項需老闆輸入

---

## 🟡 P1 - 重要（本月完成）

### 4. 真相網（RealTaiwan）內容更新
- **負責：** Crawler + Coder（🤖 Auto可自主執行）
- **狀態：** ✅ 已完成（2026-04-07），新增文章（2026-05-10）
- **網址：** https://realtaiwan.github.io/realtaiwan-web/
- **草稿目錄：** `~/.openclaw/workspace/realtaiwan-drafts/`
- **Source：** `~/.openclaw/workspace/truth-net/`
- **已完成：**
  - [x] ✅ 新增 3 篇 HTML 文章（2026-04-07）：柯文哲與沈慶京17次密會、黃國昌選擇性失憶、柯文哲一審判決
  - [x] ✅ deploy.sh 執行成功（2026-04-07 18:10）：已推送 GitHub
  - [x] ✅ 新文章草稿 markdown 已提交 drafts repo
  - [x] ✅ 新增文章（2026-05-10）：柯文哲條款闖關（立院司委會審查）
- **身份安全：** 完全隔離，只能用 realtaiwan 帳號，絕對不能用 mars/aibotmars 帳號
- **身份安全：** 完全隔離，只能用 realtaiwan 帳號，絕對不能用 mars/aibotmars 帳號
- **Auto 指令範例：**
  > "Crawler，用 web_search 搜尋『柯文哲審判最新進展 2026』、『黃國昌弊案 2026』、『台灣政治新聞 2026-04』。整理出 2 篇 300-500 字文章，存到 ~/.openclaw/workspace/realtaiwan-drafts/articles/20260403-柯文哲.md（日期要對）。格式：## 標題、## 背景、## 關鍵事件、## 來源。完成後通知 Coder 執行 deploy.sh。"

### 5. 任務儀表板更新（Task Dashboard Sync）
- **負責：** Coder（🤖 Auto可自主執行）
- **狀態：** ✅ 已同步（2026-05-09）
- **網址：** https://aibotmars-web.github.io/task-dashboard/
- **待做：**
  - [x] Clone repo + 讀取 TASKS.md + 更新 index.html（用 gh auth 推送）
  - [x] 格式：P0/P1/P2 分區，狀態彩色標籤（done/in_progress/blocked/pending）
  - [x] ✅ 已推送並驗證（2026-04-04 18:07）：https://aibotmars-web.github.io/task-dashboard/
- **Auto 指令範例：**
  > "Coder，讀取 `~/.openclaw/workspace/TASKS.md`，clone `github.com/aibotmars-web/task-dashboard`，更新 index.html 反映最新任務狀態（P0/P1/P2 分區，彩色狀態標籤），push 部署，回報 URL。"

### 6. Google Sheets 自動更新腳本
- **負責：** Coder（🤖 Auto可自主執行，但 credentials 需老闆設定）
- **狀態：** 🟡 腳本已就緒，缺少 Google credentials
- **試算表：** https://docs.google.com/spreadsheets/d/10PE52Fmv97I9WSmTzdrjimr_A3Q9X8qCsTAGw8MyuAU
- **腳本位置：** `~/.openclaw/workspace/projects/google-sheets-updater.py` 和 `~/.openclaw/workspace/scripts/sheets-updater.py`
- **待做：**
  - [ ] ⚠️ 需老闆確認：用 gog 設定 Google service account credentials 到 `~/.openclaw/google-sheets/credentials.json`
  - [ ] 確認 credentials 後：`python3 ~/.openclaw/workspace/scripts/sheets-updater.py`（移除 --dry-run）
  - [ ] 設定每日 cron 自動執行（建議 09:30，早晨報告之後）
- **🤖 Auto跳過：** credentials 設定需老闆操作 gog

### 7. 所有 Sub-Agent 工具確認可用
- **負責：** System-Admin（🤖 Auto可自主執行）
- **狀態:** 🟡 檢測完成（2026-04-04）
- **工具確認結果：**
  - [x] **weather** ✅ 完全正常（wttr.in 回應 +21°C Taipei）
  - [x] **kd CLI** ✅ 完全正常（成功下載字幕，Rick Roll 測試通過）
  - [x] **gog** ⚠️ 已安裝 v0.9.0，但 OAuth token 過期（`invalid_grant`），需老闆執行 `gog auth login` 重新認證
  - [x] **bird** ⚠️ 已安裝 v0.8.0，但 Twitter cookies 未設定（Safari/Chrome/Firefox 皆無登入 cookies），需老闆在瀏覽器登入 X 並設定 cookie source
- **待做：**
  - [ ] 老闆重新認證 gog：`gog auth login`
  - [ ] 老闆設定 bird Twitter cookies：在 Safari/Chrome 登入 X，並確認 cookie 路徑

---

## 🔵 P1.5 - IG Carousel 維護（持續進行）

### 8. IG Carousel 每日發文流程
- **負責：** Assistant-Work（cron 自動，12:00 每日）
- **狀態：** 🟢 基本正常，2026-04-01 成功發布
- **已修復（Cowork session 完成）：**
  - ✅ `--reuse-existing` 防止 publish 重新生成圖片
  - ✅ 防重複鎖（30分鐘 `.lock` 檔）
  - ✅ 內容品質閘門（<150 字不發文）
  - ✅ AI 封面（fal-ai FLUX schnell，3 種風格候選）
  - ✅ autoRecallLimit 修復（3→10 條記憶注入）
  - ✅ JSON 解析修復（跳過 `[plugins]...` 前綴）
- **目前流程：**
  1. 12:00 cron → 生成草稿 → 圖片傳送 Telegram → 通知老闆
  2. 老闆回覆「可以」→ `ig-carousel publish`（--reuse-existing）
  3. 發布成功 → 回報結果
- **待觀察：**
  - [ ] MiniMax API 是否還有超時問題（3/31 事件後）
  - [ ] 確認 @money.showtime 和 @bossmaker.lab 兩個帳號都正常

---

## 🟢 P2 - 一般（有空做）

### 9. DeerFlow 開機自動啟動
- **負責：** System-Admin（🤖 Auto可自主執行）
- **狀態：** ✅ 已完成（2026-04-04）
- **安裝位置：** `~/deer-flow/`
- **網址：** http://localhost:3000（frontend），http://localhost:8001（backend）
- **已完成：**
  - [x] 建立 LaunchAgent plist（`~/Library/LaunchAgents/com.deerflow.startup.plist`）
  - [x] 建立 wrapper script（`~/deer-flow/scripts/launchd-start.sh`）
  - [x] 測試開機自動啟動（launchctl load 成功，PID 71721）
  - [x] 確認啟動後 http://localhost:3000 可訪問（DeerFlow 目前在線）
- **開機流程：** LaunchAgent → launchd-start.sh → start-daemon.sh → langgraph + uvicorn + frontend + nginx

### 10. OpenClaw auto-fix 腳本 macOS 版
- **負責：** Coder（🤖 Auto可自主執行）
- **狀態:** ✅ 已完成（2026-04-07）
- **問題：** 舊版 script 依賴 `timeout` 命令（macOS 不存在），導致每 5 分鐘 false positive 並觸發錯誤的重啟迴圈
- **修復：**
  - 重寫 `exec-fix-v6.sh`：移除 `timeout` 依賴，改用 `curl --connect-timeout` 和直接命令執行
  - 更新 `ai.openclaw.exec-monitor.plist`：PATH 加入 `/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin`
  - 清空錯誤日誌，重新載入 LaunchAgent
  - 驗證：✅ Shell / Node.js / Gateway HTTP 全部正常

### 11. 兒童 AI 繪圖書
- **負責：** Image + Coder
- **狀態：** ⬜ 尚未開始
- **待做：**
  - [ ] ⚠️ 需老闆確認：主題和風格
  - [ ] Image 用 MiniMax 生成插圖（10-15 張）（等老闆確認後）
  - [ ] Coder 整合成 PDF 或網頁（等老闆確認後）

### 12. 跨境電商（淘寶→蝦皮/亞馬遜）
- **負責：** 待確認
- **狀態：** ⬜ 尚未開始
- **待做：**
  - [ ] ⚠️ 需老闆確認：具體需求和預算

### 13. App 開發
- **負責：** Coder
- **狀態：** ⬜ 尚未開始
- **待做：**
  - [ ] ⚠️ 需老闆確認：App 的功能需求

### 14. SSH 互連救援（Mac ↔ Windows）
- **負責：** System-Admin
- **狀態：** ⬜ 等 Windows 安裝完成
- **待做：**
  - [ ] ⚠️ 需老闆確認：在 Windows 安裝 OpenClaw
  - [ ] 設定 Tailscale 互連（等老闆完成 Windows 安裝）
  - [ ] 設定 SSH 金鑰

---

## ✅ 已完成（歸檔）

### Cowork Sessions 完成項目（2026-03 ~ 04）
- ✅ **LanceDB PRO autoRecallLimit 修復**（3→10 條記憶，2026-03-31）
- ✅ **memory-lancedb-pro embedding config 修復**（voyage → openai-compatible，2026-03-31）
- ✅ **33 個 workspace/skills symlink**（建立到 ~/.openclaw/skills/，2026-03-31）
- ✅ **IG Carousel --reuse-existing**（publish 不再重新生成圖片，2026-04-01）
- ✅ **IG Pipeline 防重複鎖**（30分鐘 lock 檔，2026-03-31）
- ✅ **IG 內容品質閘門**（<150 字不發文，2026-03-31）
- ✅ **IG AI 封面**（fal-ai FLUX schnell，漫畫/普普/賽博龐克 3 選 1，2026-03-19）
- ✅ **content_pipeline.py JSON 解析修復**（跳過 [plugins] 前綴，2026-03-18）
- ✅ **Pillow deprecation 修復**（getdata() 相容寫法，2026-03-18）
- ✅ **exec-approvals.json 修正**（security=full ask=off，2026-04-03）
- ✅ **DeerFlow 安裝**（~/deer-flow，MiniMax-M2.1，2026-03-31）
- ✅ **OpenClaw 升級** 2026.3.13 → 2026.3.23-2（2026-03-25）
- ✅ **model 升級** M2.5 → M2.7（2026-03-25）
- ✅ **SKILL.md 路徑 symlink 修復**（ig-carousel、agent-browser，2026-04-01）

### 更早完成項目
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
- ✅ TranscriptAPI 永久停用（改用 kd CLI，2026-03-29）
- ✅ kd CLI 安裝（/opt/homebrew/bin/kd，本地 ASR）
- ✅ 8 個 TOOLS.md 建立（解決幻覺問題，2026-03-05）
- ✅ Agent-to-Agent 協作啟用（openclaw.json，2026-03-05）

---

## 📋 Auto-Task-Runner 工作指引

### auto-task-runner-001 執行規則
每 2 小時自動執行，依照以下優先順序：

**可自主執行（不需確認）：**
1. P0 任務 1（OpenClaw 升級）→ 執行 `openclaw doctor --fix`
2. P0 任務 2（YouTube LLM 修復）→ 診斷並修復超時問題
3. P1 任務 4（真相網更新）→ 搜尋新聞 → 寫草稿 → 部署
4. P1 任務 5（Task Dashboard 同步）→ 把 TASKS.md 轉成 HTML → push
5. P1 任務 7（工具確認）→ 逐一測試並回報
6. P2 任務 9（DeerFlow 開機啟動）→ 建立 LaunchAgent plist

**需老闆確認，跳過：**
- 任務 3（Polymarket 市場 ID 和資金設定）
- 任務 6（Google Sheets credentials）
- 任務 11/12/13（兒童繪本、電商、App）
- 任務 14（Windows 安裝）

### Planner 每次啟動時
1. 讀這個 TASKS.md
2. 優先處理 P0 可自主執行的任務
3. 分配具體工作給 sub-agent（說清楚做什麼、怎麼做、用哪個工具）
4. 追蹤進度，卡住就記錄原因並標記

### 給 sub-agent 的指令範例（好的）
> "Coder，請讀取 `~/.openclaw/workspace/projects/yt-expert-crawler.py`，找出 summarize 函數，把 timeout 從當前值改為 120 秒，加入 3 次 retry（每次等 10 秒），測試阿銘師頻道最新字幕能否生成摘要，回報結果。"

### 給 sub-agent 的指令範例（不好的）
> "幫我修 YouTube 爬蟲"

---

## 📋 Auto-Task-Runner 執行紀錄

### 2026-05-11 08:02（本次執行）
### 2026-05-15 14:04（Auto-Task-Runner 例行檢查）
- 系統狀態：OpenClaw v2026.5.7 ✅ / DeerFlow healthy ✅ / 爬蟲正常 ✅
- 所有可自主執行任務均已完成（P0/P1/P2 ✅）
- 僅存等待老闆確認項目（Polymarket、Google credentials、兒童繪本、電商、App）
- gateway.err.log 485KB（正常，<500KB）
- 回報：無需自主行動，系統正常運行
- 系統狀態檢查完畢
- 所有可自主執行的任務均已完成（P0/P1/P2 ✅）
- 僅存等待老闆確認的項目（Polymarket、Google credentials、兒童繪本、電商、App）
- 回報：無需自主行動，系統正常運行

### 2026-05-16 16:00（Auto-Task-Runner 例行檢查）
- 系統狀態：OpenClaw v2026.5.7 ✅ / DeerFlow 🔄 已重新啟動（離線後自動修復）✅ / 爬蟲 Daemon PID 正常 ✅
- 所有可自主執行任務均已完成（P0/P1/P2 ✅）
- 僅存等待老闆確認項目（Polymarket、Google credentials、兒童繪本、電商、App）
- 今日執行：DeerFlow 離線 → 自動重啟 → 健康檢查通過 ✅
- 回報：無需自主行動，系統正常運行


### 2026-05-18 16:00（Auto-Task-Runner 例行檢查）
- **系統狀態：** OpenClaw v2026.5.7 ✅ / DeerFlow healthy ✅ / 爬蟲 Daemon 正常運行 ✅
- **所有可自主執行任務均已完成（P0/P1/P2 ✅）**
- **僅存等待老闆確認項目**（Polymarket、Google credentials、兒童繪本、電商、App）
- **⚠️ 持續監控：** MiniMax LLM timeout 問題（凌晨時段）
- **回報：** 無需自主行動，系統正常運行

### 2026-05-19 18:00（Auto-Task-Runner 例行檢查）
- **系統狀態：** OpenClaw v2026.5.7 ✅ / DeerFlow healthy ✅
- **爬蟲 Daemon：** 正在處理（kd process 運行中，PID 12284）
- **所有可自主執行任務均已完成（P0/P1/P2 ✅）**
- **僅存等待老闆確認項目**（Polymarket、Google credentials、兒童繪本、電商、App）
- **⚠️ 持續監控：** MiniMax LLM timeout 問題（凌晨時段）
- **回報：** 無需自主行動，系統正常運行
