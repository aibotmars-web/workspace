# HANDOFF.md - Cowork → OpenClaw 交接文件
*建立時間：2026-04-03 12:00*
*目的：把所有 Cowork/Claude Desktop session 的工作成果、待辦事項完整交給 OpenClaw 繼續執行。*

---

## 一、Cowork Session 完成的所有工作

### 🔧 系統層修復

| 日期 | 項目 | 詳細 |
|------|------|------|
| 2026-03-18 | `memory-lancedb-pro` 修復 | `npm install openai` 修復 Cannot find module 'openai' |
| 2026-03-18 | content_pipeline.py JSON 修復 | 跳過 `[plugins]...` 前綴行，解決 JSON 解析失敗 |
| 2026-03-18 | Pillow deprecation 修復 | `getdata()` 改為相容寫法 |
| 2026-03-25 | OpenClaw 升級 | 2026.3.13 → 2026.3.23-2 |
| 2026-03-25 | Model 升級 | M2.5 → M2.7（Starter Plan 支援） |
| 2026-03-29 | TranscriptAPI 永久停用 | 改用 kd CLI（/opt/homebrew/bin/kd） |
| 2026-03-31 | LanceDB PRO autoRecallLimit 修復 | 3→10 條記憶，修改 memory-lancedb-pro/index.ts + openclaw.json |
| 2026-03-31 | embedding config 修復 | provider 從 `"voyage"` 改為 `"openai-compatible"`，補足 baseURL 和 apiKey |
| 2026-03-31 | extractMinImportance schema 修復 | 加入到 openclaw.plugin.json schema，解決 config 驗證錯誤 |
| 2026-03-31 | 33 個 workspace/skills symlink | 建立到 ~/.openclaw/skills/，解決 subagent 找不到 skill 問題 |
| 2026-04-01 | SKILL.md 路徑修復 | ig-carousel 和 agent-browser SKILL.md symlink 修復 |
| 2026-04-03 | exec-approvals.json 修正 | 加入 security=full ask=off，同步 v2026.4.2 YOLO mode |

### 🖼️ IG Carousel Pipeline 修復與優化

| 日期 | 項目 | 詳細 |
|------|------|------|
| 2026-03-19 | 顏色固定 | Carousel 卡片顏色穩定，不再每次不同 |
| 2026-03-19 | 佐證配文修復 | 數據來源標注正確 |
| 2026-03-19 | understand_image 圖片檢查 | 發布前確認圖片品質 |
| 2026-03-19 | humanizer 去 AI 味 | 文字更像人類寫的 |
| 2026-03-19 | AI 封面 | fal-ai FLUX schnell，漫畫/普普/賽博龐克 3 種風格，3 選 1 |
| 2026-03-19 | 走勢圖智慧時間軸 | 自動選擇最佳時間範圍 |
| 2026-03-19 | `--select-cover N` 參數 | 老闆可指定選哪個封面 |
| 2026-03-31 | 防重複鎖 | `.{channel}_pipeline.lock` 30 分鐘內防重複執行 |
| 2026-03-31 | 內容品質閘門 | what < 150 字直接放棄不發文 |
| 2026-03-31 | 清理失敗草稿 | 刪除 3 個無 caption.txt 的 3/31 草稿 |
| 2026-04-01 | `--reuse-existing` 修復 | publish 不再重新生成圖片（老闆看到的草稿 = 實際發布） |
| 2026-04-01 | 審核流程更新 | 草稿圖片 → Telegram → 老闆說「可以」→ 直接發布 |

**IG 帳號：** @money.showtime (crypto/finance)、@bossmaker.lab (startup)

### 🧠 記憶與知識系統

| 日期 | 項目 | 詳細 |
|------|------|------|
| 2026-03-18 | ClawHub skills 更新 | 11 個 skills 更新到最新版 |
| 2026-03-18 | 8 個 agent TOOLS.md 重建 | 從 19 行骨架 → 40-80 行完整工具文件 |
| 2026-03-18 | SKILLS.md 更新 | 51/62 → 64/77，新增社群&研究分類 |
| 2026-03-18 | 知識橋梁建立 | Claude Code IG pipeline 設計決策寫入 assistant-work/memory/MEMORY.md |
| 2026-03-21 | 記憶系統優化 | 自動濃縮腳本（~/.openclaw/scripts/memory-consolidate.sh，每天 23:59） |
| 2026-03-25 | 系統知識庫建立 | ~/.openclaw/workspace/knowledge-base/openclaw-system-knowledge.md |
| 2026-03-29 | YouTube 正確抓字幕方法固化 | 所有相關 MEMORY.md 都加入 kd CLI 禁止 TranscriptAPI 規則 |

### 🔬 DeerFlow 深度研究工具

| 日期 | 項目 | 詳細 |
|------|------|------|
| 2026-03-31 | DeerFlow 安裝 | ~/deer-flow，MiniMax-M2.1 |
| 2026-03-31 | MiniMax API 整合 | ~/.zshrc + ~/deer-flow/.env 設定 MINIMAX_API_KEY |
| 2026-03-31 | 啟動腳本記錄 | 見 MEMORY.md 啟動方式區段 |
| 待完成 | 開機自動啟動 | 尚未設定 macOS LaunchAgent |

**DeerFlow 用途：** 需要深度研究的任務（競品分析、市場調查、技術比較）可用 DeerFlow 代替簡單 web_search

---

## 二、目前系統狀態（2026-04-03）

### 服務狀態
| 服務 | 狀態 | 備註 |
|------|------|------|
| OpenClaw | ✅ v2026.4.2（剛發布，需執行 `openclaw doctor --fix`） | |
| Gateway | ✅ 正常運行 | PID 存在 |
| Telegram | ✅ 正常 | IPv4 only 模式 |
| LanceDB PRO | ✅ 正常（autoRecallLimit=10）| schema mismatch 待確認 |
| MiniMax API | ⚠️ 不穩定 | 3/31 大量 timeout，觀察中 |
| DeerFlow | ⚠️ 需手動啟動 | 關機後不自動啟動 |
| YouTube 爬蟲（字幕抓取） | ✅ 正常（cron 每天 04:00）| |
| YouTube 爬蟲（LLM 總結） | ❌ 超時失敗 | 15 天無新摘要 |
| IG Carousel cron | ✅ 正常（12:00 每日）| |
| Google Sheets updater | ⚠️ 缺 credentials | dry-run 成功 |

### 關鍵檔案位置
| 用途 | 路徑 |
|------|------|
| 主任務清單 | `~/.openclaw/workspace/TASKS.md` |
| 主記憶摘要 | `~/.openclaw/workspace/MEMORY.md` |
| 每日記憶 | `~/.openclaw/workspace/memory/YYYY-MM-DD.md` |
| IG Pipeline | `~/.openclaw/workspace/scripts/social-media/content_pipeline.py` |
| ig-carousel skill | `~/.openclaw/workspace/skills/ig-carousel/` |
| Polymarket bot | `~/.openclaw/workspace/projects/polymarket-bot.py` |
| Google Sheets updater | `~/.openclaw/workspace/projects/google-sheets-updater.py` |
| 知識庫爬蟲 | `~/.openclaw/workspace/projects/yt-expert-crawler.py` |
| kd CLI（YouTube字幕）| `/opt/homebrew/bin/kd` |
| 真相網草稿 | `~/.openclaw/workspace/realtaiwan-drafts/` |
| 真相網 Source | `~/.openclaw/workspace/truth-net/` |
| 真相網部署腳本 | `~/.openclaw/workspace/realtaiwan-drafts/deploy.sh` |
| DeerFlow | `~/deer-flow/` |
| 系統知識庫 | `~/.openclaw/workspace/knowledge-base/openclaw-system-knowledge.md` |

---

## 三、待辦事項優先清單（OpenClaw 接手執行）

### 🔴 立即執行（不需老闆確認）

1. **OpenClaw v2026.4.2 升級**
   ```bash
   openclaw doctor --fix
   ```
   然後重啟 Gateway，確認 LanceDB PRO schema 驗證通過

2. **YouTube LLM 總結超時修復**
   - 讀取 `~/.openclaw/workspace/projects/yt-expert-crawler.py`
   - 找 summarize/LLM 呼叫步驟
   - 增加 timeout 到 120 秒 + 3 次 retry
   - 用阿銘師頻道測試

3. **真相網內容更新**
   - 搜尋 2026-04 台灣政治新聞
   - 寫 2-3 篇草稿到 `realtaiwan-drafts/articles/`
   - 執行 `deploy.sh` 部署

4. **Task Dashboard 同步**
   - Clone task-dashboard repo
   - 把這份 TASKS.md 轉成 HTML
   - Push 部署

### 🟡 等待老闆確認才能執行

1. **Polymarket 市場 ID 和資金設定**（問老闆要追蹤哪些市場）
2. **Google Sheets credentials**（老闆需用 gog 設定）
3. **兒童繪本主題確認**
4. **App 功能需求確認**
5. **Windows OpenClaw 安裝**

---

## 四、重要注意事項（OpenClaw 必讀）

### ⚠️ 永久禁止
- ❌ **TranscriptAPI**（youtube-transcript-api、任何需要 API key 的 YouTube 轉字幕服務）
- ✅ 只能用 `kd subtitles "URL"` 或 `kd transcribe "URL" --backend mlx-whisper`

### ⚠️ 系統限制
- Mac mini M4，256GB SSD（已有 ~72GB 可用）→ 不要下載大檔案
- 不要下載影片，只抓字幕

### ⚠️ 身份隔離
- 真相網操作：只能用 realtaiwan 帳號（git config user.email realtaiwan@proton.me）
- Task Dashboard：用 aibotmars-web token
- 絕對不能混用帳號

### ⚠️ MiniMax API 穩定性
- 3/31 發生大量 timeout（930 秒後放棄）
- 目前策略：timeout → 直接放棄，不重試（老闆確認接受）
- 觀察 4 月是否持續發生

### ⚠️ Claude Code vs OpenClaw 知識隔離
- Claude Code session（Cowork）的設計決策**不會自動同步**到 OpenClaw
- 需要手動把重要設計決策寫入 OpenClaw 的 MEMORY.md 或相關 agent memory
- 這份 HANDOFF.md 是橋接的方式

---

## 五、auto-task-runner-001 指引

### Cron Job 設定（應已存在）
- 每 2 小時執行一次
- 啟動 Planner，讓 Planner 讀取 TASKS.md 並推進可自主執行的任務

### 每次執行流程
1. 讀取 `~/.openclaw/workspace/TASKS.md`
2. 讀取 `~/.openclaw/workspace/HANDOFF.md`（本文件）
3. 選擇可自主執行的 P0 任務
4. 分配給對應 sub-agent 執行
5. 更新 TASKS.md 中的 checkbox 狀態
6. 回報結果到 Telegram

### 本次最優先任務順序
1. 任務 1：`openclaw doctor --fix`
2. 任務 2：YouTube LLM 超時修復
3. 任務 4：真相網更新
4. 任務 5：Task Dashboard 同步

---

*建立者：Claude Code (Cowork session)*
*接收者：OpenClaw / auto-task-runner-001*
*下次更新：完成一個任務後更新 TASKS.md 的 checkbox 狀態*
