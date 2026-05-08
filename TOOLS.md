# 統一工具清單 - 全體 Agents 共享

## 可直接使用的工具

| 工具 | 用法 | 何時用 |
|------|------|--------|
| `web_search` | `web_search("關鍵字")` | 搜尋資料、查詢資訊 |
| `web_fetch` | `web_fetch("https://...")` | 抓取特定網頁內容 |
| `understand_image` | `understand_image("圖片路徑", "描述")` | 分析圖片 |
| `memory_recall` | `memory_recall("關鍵字")` | 搜尋過去記憶（支援 scope、category 篩選） |
| `memory_store` | `memory_store("要記住的內容", category, importance)` | 存入長期記憶（category: preference/fact/decision/entity） |
| `memory_stats` | `memory_stats()` | 查看記憶統計（數量、分類、scope） |
| `exec` | `exec("bash命令")` | 執行系統指令 |
| `read` | `read("檔案路徑")` | 讀取檔案 |
| `write` | `write("路徑", "內容")` | 寫入檔案 |

## Agent 協作工具

| 工具 | 功能 |
|------|------|
| `sessions_send` | 發訊息給其他 Agent |
| `sessions_list` | 查看活躍 sessions |
| `sessions_spawn` | 啟動新的 Agent session |

## 🧠 gstack / DeerFlow / AutoResearch

| Skill | 路徑 | 指令 | 說明 |
|-------|------|------|------|
| `gstack/office-hours` | `~/.openclaw/skills/gstack/office-hours` | `openclaw skill run office-hours '任務'` | Think & Plan，任務前必做 |
| `gstack/review` | `~/.openclaw/skills/gstack/review` | `openclaw skill run review '程式碼'` | 程式碼審查 |
| `gstack/qa` | `~/.openclaw/skills/gstack/qa` | `openclaw skill run qa '說明'` | 品質確認測試 |
| `gstack/ship` | `~/.openclaw/skills/gstack/ship` | `openclaw skill run ship '說明'` | 部署（ship 前先跑 review + qa） |
| `gstack/cso` | `~/.openclaw/skills/gstack/cso` | `openclaw skill run cso '問題'` | 安全審查 |
| `gstack/design-shotgun` | `~/.openclaw/skills/gstack/design-shotgun` | `openclaw skill run design-shotgun '需求'` | 多版設計方案 |
| `gstack/canary` | `~/.openclaw/skills/gstack/canary` | `openclaw skill run canary '功能'` | Canary 驗證 |
| `claude-to-deerflow` | `~/.openclaw/skills/claude-to-deerflow/` | `bash ~/.openclaw/skills/claude-to-deerflow/scripts/chat.sh '問題'` | DeerFlow 深度研究（先 curl http://localhost:8001/health 確認） |
| `autoresearch` | `~/.openclaw/skills/autoresearch/` | 見 coder/TOOLS.md | ML 實驗優化（val_bpb 越低越好） |

---

## 已安裝 Skills

| Skill | 功能 | 主要使用者 |
|-------|------|-----------|
| `youtube-full` | YouTube 搜尋、字幕、頻道、播放清單（需 TRANSCRIPT_API_KEY） | crawler |
| `coding-agent` | 程式開發（Claude Code / Codex） | coder |
| `github` | Git 版本控制（gh CLI） | coder |
| `gog` | Google 行事曆、Gmail、Drive | assistant |
| `xurl` | X (Twitter) 發文、搜尋、回覆 | assistant-work |
| `x-research` | X/Twitter 深度研究、監控帳號 | assistant-work |
| `peekaboo` | macOS 原生 App UI 自動化 | assistant-work |
| `agent-browser` | 網頁瀏覽、填表、爬蟲（Chromium） | all |
| `wacli` | WhatsApp 操作 | assistant-work |
| `sag` | ElevenLabs 語音合成 | image |
| `apple-reminders` | Apple 提醒事項 | assistant |
| `things-mac` | Things 3 待辦 | assistant |
| `weather` | 天氣查詢（wttr.in / Open-Meteo，免 API key） | assistant |
| `healthcheck` | 系統安全檢查、硬體狀態 | system-admin |
| `session-logs` | 搜尋自己的歷史對話記錄 | all |
| `self-improvement` | 錯誤學習、自我改進記錄 | all |
| `humanizer` | 去除 AI 味文字 | all |
| `deep-research-pro` | 多來源深度研究（免 API key） | all |
| `summarize` | 摘要網頁、影片、檔案 | all |
| `watermark-remover` | 去除圖片/影片浮水印 | image |
| `nano-pdf` | PDF 編輯 | all |

## YouTube 字幕抓取方法（crawler 專用）

**唯一方法：用 kd CLI（本地 ASR，不需 API key，不會被 IP 封鎖）**

```bash
# 方法 1: 抓現有字幕（快，幾秒完成）
kd subtitles "https://www.youtube.com/watch?v=VIDEO_ID" -o output.txt

# 方法 2: 本地 ASR 轉錄（慢但保證成功，3-10 分鐘/影片）
kd transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --no-subtitles --backend mlx-whisper -o output.txt

# 方法 3: 完整處理（轉錄 + AI 摘要）
kd process "https://www.youtube.com/watch?v=VIDEO_ID" --no-summary -o output.md
```

**重要規則：**
- 不要用 `youtube-transcript-api` Python 庫（IP 被 YouTube 封鎖）
- 不要用 `yt-dlp` 抓字幕（會 429 限流）
- 用 `yt-dlp --flat-playlist --print "%(id)s|%(title)s"` 只列出影片 ID 是安全的
- `kd` 已安裝在 `/opt/homebrew/bin/kd`

## ⚠️ 常見錯誤（避免幻覺）

| 錯誤用法 | 正確做法 |
|----------|---------|
| `youtube-skills` | 不存在！用 `youtube-full` 或 `kd` CLI |
| `bird` | 不存在！用 `xurl` |
| `memory_search` | 已改名為 `memory_recall` |
| `memory_get` | 已不存在，用 `memory_recall` 替代 |
| `apply_patch` | 不存在！用 `write` 或 `edit` |
| `weather "台中"` | `exec("curl -s 'wttr.in/Taichung?format=3&lang=zh-tw'")` |
| `polymarket` CLI | 不存在！用 `web_search` 查 Polymarket |
| OpenAI API | 不要用（沒有 key） |
| `youtube-transcript-api` | 不要用（IP 被封鎖），用 `kd` CLI |
| 編造工具名 | 查此清單確認 |
| 猜測 API URL | 先 `web_search` 確認 |

## 使用原則

1. **直接使用** — 不需問老闆，根據需求直接調用
2. **查清單** — 不確定工具是否存在時回來看
3. **用 `sessions_send` 協作** — 需要其他 Agent 幫忙時
4. **遇到錯誤** — 用 `self-improvement` skill 記錄，避免重複犯錯
