# 完整对话记忆摘要 (2026-02-01 到 02-22)

## 关于老闆 (Mars/L)
- 姓名：林嘉俊 (mars)
- 生日：1979年4月2日
- 出生地：台中
- 居住：台中市西屯区西屯路二段126巷48号4楼402室
- 女友：品洁（1979年10月20日生）
- 宠物：两只白色苏格兰折耳猫（bibi、林建成）

## 系统配置
- 电脑：Mac mini M4, 16GB RAM, 256GB SSD
- 模型：MiniMax M2.5 CN（Coding Plan）
- 订阅开始：2025/1/29，年费290 RMB
- Telegram：chat ID 1073451144 (username: @mlnl68), @Ai_bibi_bot
- **重要：發送訊息時必須使用數字 chat ID `1073451144`，不要用 @mlnl68**

## Sub-Agents 配置
| Agent | Chat ID |
|-------|---------|
| Planner | -5002017265 |
| Assistant | -5111933995 |
| Coder | -5205007678 |
| Crawler | -5277218620 |
| Image | -5267145726 |
| Assistant-Work | -5107483605 |
| System-Admin | -5268796547 |
| Trader | -5168109367 |

## 专案
1. 真相网 - 政治弊案揭露网站
2. 九位专家知识库 - 健康/心理/投资
3. Polymarket 自动交易
4. YouTube 内容频道
5. 儿童 AI 绘本书
6. IG Carousel 自動發文 - 加密/金融/創業新聞 → AI 改寫 → 10 張圖卡 → IG 自動發文
   - 開發工具：Claude Code（設計決策在 Claude Code session history）
   - 執行工具：OPENCLAW scheduled task (`auto-post-crypto`，每天 09:01，7 步驟 agent 流程)
   - OPENCLAW Skill：`ig-carousel`（draft/publish/preview/history）
   - 關鍵檔案：`scripts/social-media/content_pipeline.py`、`make_card.py`
   - IG 帳號：@money.showtime (crypto/finance)、@bossmaker.lab (startup)
   - 狀態：Pipeline v3 + ig-carousel skill，draft/publish-last 分離防重複
   - 2026-03-19：顏色固定、佐證配文修復、understand_image 圖片檢查、humanizer 去 AI 味
   - 2026-03-19 v2：AI 封面（fal-ai FLUX schnell，漫畫/普普/賽博龐克風格）、3 選 1 封面候選、走勢圖智慧時間軸、人物藝術風格、--select-cover N

## 重要原则
- 不要自动更新系统（会当机）
- 遇到技术问题直接处理，不用问老闆
- 3小时原则：未回答问题要主动追问
- 不要下载大档案（256GB硬盘限制）
- 只抓字幕，不要下载影片
- 记忆要自动保存（每10句话）

## 常发生的问题
- tool id not found 当机问题
- 记忆会归零
- 需要经常备份

## 已安装的 Skills
- apple-reminders
- ClawVault
- auto-updater
- capability-evolver
- ui-ux-pro-max
- superdesign
- polymarket
- youtube-watcher
- healthcheck
- system-monitor
- SkillGuard

## 🔐 川普密码 (Trump Code)
- **位置**: ~/trump-code/
- **GitHub**: https://github.com/sstklen/trump-code
- **Dashboard**: https://trumpcode.washinmura.jp
- **运行方式**:
  ```bash
  cd ~/trump-code && source venv/bin/activate
  python trump_code_cli.py <指令>
  ```
- **指令**:
  - `signals` - 今日信号
  - `report` - 完整日报
  - `json` - 全部 JSON
  - `models` - 模型排行
  - `predict` - 预测方向
- **注意**: 数据最后更新是 2026-03-15，需要运行 daily_pipeline.py 更新

---
*2026-02-22 汇入完成*

---

# 更新摘要 (2026-02-23 到 2026-03-06)

## 2026-02-23 to 02-25 系統維護
- Docker 清理（刪除閒置容器，省 30GB）
- Voyage API 設定完成（Tier 1 解鎖）
- QMD 向量嵌入完成
- 教訓：改設定前必須先展示給老闆看，不能自作主張

## 2026-02-27 to 03-03 已知問題
- Telegram sendMessage 偶發 HttpError（網路波動，非系統問題）
- Chrome extension relay 無連接 tab（已知問題）
- Docker daemon 未運行（Mar 2 發現，影響 Docker 相關服務）
- TranscriptAPI 無 active paid plan（crawler 爬蟲失敗，知識庫為空）

## 2026-03-04 to 03-05 重大系統修復（Mars + Claude 協作）

### 問題診斷
- Telegram 完全不回應訊息（3 個複合問題）

### 修復內容
1. **Config 衝突**：刪除 `~/openclaw.json`（與 `~/.openclaw/openclaw.json` 衝突）
2. **IPv6 卡住**：在 `openclaw.json` 加入 `network.autoSelectFamily: false`
3. **groupPolicy 錯誤**：從 `allowlist` 改為 `open`
4. **OpenClaw 升級**：2026.2.26 → **2026.3.1**

### Subagent 提示詞全面優化
5. **建立 8 個 TOOLS.md**（之前完全不存在，是幻覺的根本原因！）
6. **重寫 8 個 AGENTS.md**（加入反幻覺規則 + 協作指令 + USER.md 關鍵資訊）
7. **重寫主 SOUL.md**（342 行 → 72 行，前置反幻覺規則）
8. **啟用 Agent-to-Agent 協作**（openclaw.json 加入 tools.agentToAgent）
9. **建立 8 個 subagent memory/MEMORY.md**（長期記憶摘要，各 agent 專屬）
10. **更新 8 個 AGENTS.md**（加入啟動時手動讀取記憶指令）

### 重要發現
- Subagent 使用 `minimal` 提示模式：只注入 AGENTS.md + TOOLS.md
- USER.md / MEMORY.md / SOUL.md **不會**注入給 subagent
- Subagent 需要在 AGENTS.md 中明確 `read("memory/MEMORY.md")` 才能讀到記憶
- EverMemOS (Docker-based) 已永久離線（2026-02-20 誤刪）

## 系統更新記錄

### 2026-03-25 重大更新
- **OpenClaw**：2026.3.13 → 2026.3.23-2
- **模型**：M2.5 → M2.7（已確認 Starter Plan 支援）
- **GitHub Monitor**：每日 09:00 自動檢查新版
- **LanceDB PRO**：64MB，1273個資料檔案，正常運行

### SecretRef 進化（2026.3.22）
從「手改 JSON」→ CLI 互動式引導（configure/plan/apply），從 spec-driven 變成 workflow-driven，成熟度大幅提升。

---

## 系統目前狀態（2026-03-25 更新）
- OpenClaw: **2026.3.1** ✅
- Gateway: 運行中 ✅
- Node: 運行中 ✅
- Telegram: 修復後正常 ✅
- LanceDB PRO: ✅ 運行中（主記憶引擎，Jina embedding）
- QMD: ✅ 可用（/opt/homebrew/bin/qmd）
- EverMemOS (Docker): 已停用（不再使用）
- TranscriptAPI: ❌ 需要充值
- 記憶空白期：2026-03-04 到 03-05（Telegram 故障期間，cron 任務無法正常執行）

## 重要提醒
- 每次 /new 前必須先濃縮到 memory/YYYY-MM-DD.md
- 記憶不會自動同步到 subagent，需要在各 subagent 目錄的 MEMORY.md 手動維護

## 2026-03-18 Claude Code 系統優化（Mars + Claude Code 協作）

### 修復
1. **memory-lancedb-pro**：`npm install openai` 修復 `Cannot find module 'openai'`
2. **content_pipeline.py call_ai()**：JSON 解析修復（跳過 `[plugins]...` 前綴行）
3. **Pillow deprecation**：`getdata()` 改為相容寫法

### OPENCLAW 知識同步
4. **所有 ClawHub skills 更新**：11 個 skills 更新到最新版
5. **8 個 agent TOOLS.md 重建**：從 19 行骨架 → 40-80 行完整工具文件
6. **SKILLS.md 更新**：51/62 → 64/77，新增社群&研究分類
7. **知識橋梁建立**：Claude Code IG pipeline 專案知識寫入 assistant-work/memory/MEMORY.md

### 重要發現
- Claude Code session 與 OPENCLAW 完全隔離，知識不互通
- 需要手動將 Claude Code 的設計決策同步到 OPENCLAW MEMORY.md
- AGENTS.md 只記錄「怎麼執行」，MEMORY.md 要記錄「為什麼這樣設計」

---
*2026-03-18 更新*

## 2026-03-21 記憶系統優化

### 自動濃縮設定
- **腳本位置**: `~/.openclaw/scripts/memory-consolidate.sh`
- **Cron 任務**: 每天 23:59 自動執行
- **功能**: 自動濃縮當天對話到 memory/YYYY-MM-DD.md

### 記憶引擎架構
- **儲存**: LanceDB PRO（plugin 形式，自動儲存 + smart extraction）
- **搜尋**: qmd（語意搜尋）
- **流程**: 
  1. 對話 → LanceDB PRO（自動儲存）
  2. 搜尋 → qmd
  3. 每日 23:59 → 濃縮到 memory/YYYY-MM-DD.md

### 防止失憶要點
- 每次對話開始應自動讀取 MEMORY.md + 昨日記憶
- 長期記憶寫入 MEMORY.md（手動更新）
- 每日記憶在 memory/YYYY-MM-DD.md（自動產生）

---
*2026-03-21 更新*

## 系統知識庫
- **位置**：`~/.openclaw/workspace/knowledge-base/openclaw-system-knowledge.md`
- **內容**：OpenClaw 架構、Memory 系統、Multi-Agent、SecretRef、Cron、LanceDB PRO 完整功能
- **用途**：遇到相關問題時主動引用，主動建議更好的做法

---
*2026-03-25 知識庫建立*

## 🚫 重要：永久禁止使用 TranscriptAPI (2026-03-29)

Mars 已明確禁止使用 TranscriptAPI 選項。**說過很多次不要用，但我不斷失憶重複試錯。**

### 永久規則
- ❌ **絕對禁止**：TranscriptAPI、youtube-transcript-api、任何需要 API key 的 YouTube 轉字幕服務
- ❌ 不要再嘗試 TranscriptAPI plan/upgrade/付費方案
- ❌ 不要問可不可以試 API
- ❌ **已刪除 `youtube-skills` skill**（會引導錯誤方法，已於 2026-03-29 移除）

### ✅ 唯一正確方法
- **kd CLI**（已安裝在 `/opt/homebrew/bin/kd`）
- 用法：
  ```bash
  # 抓現有字幕（快，幾秒）
  kd subtitles "URL" -o output.txt
  
  # 本地 ASR 轉錄（慢但保証成功，3-10 分鐘）
  kd transcribe "URL" --backend mlx-whisper -o output.md
  ```
- 特點：本地 ASR，不需要 API key，不會被 IP 封鎖

### 為什麼我會忘記
- MEMORY.md 之前沒有清楚記錄這個禁令
- 每次對話都是全新上下文，沒有持久化這個教訓

### 防止未來再犯
把這個事實寫入所有相關記憶位置，確保再也不會嘗試 TranscriptAPI。

## Deer Flow 安裝（2026-03-31）

### 狀態
- ✅ 已啟動（手動啟動，關機後需重啟）
- 🌐 http://localhost:3000

### 啟動方式
```bash
cd ~/deer-flow
export $(cat .env | xargs)  # MINIMAX_API_KEY
(cd backend && nohup uv run langgraph dev --no-browser --allow-blocking > logs/langgraph.log 2>&1 &)
sleep 10
(cd backend && PYTHONPATH=. nohup uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001 > ../logs/gateway.log 2>&1 &)
sleep 10
(cd frontend && nohup pnpm run dev > ../logs/frontend.log 2>&1 &)
nginx -c $(pwd)/docker/nginx/nginx.local.conf -p $(pwd)
```

### MiniMax API Key
- 位置：`~/.zshrc` + `~/deer-flow/.env`
- 模型：MiniMax-M2.1（config.yaml 已設定為預設）
- endpoint: https://api.minimaxi.com/v1

### 開機自動啟動
尚未設定（需要 macOS launchd 或 systemd）
