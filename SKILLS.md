# Skills 完整清單

> 更新時間：2026-03-18 | 目前狀態：64/77 ready
> 每個 skill 的詳細用法在 `openclaw skills info <skill>` 查詢
> Skills 更新：`npx clawhub update --all --force`

---

## 🌐 網頁 & 搜尋

| Skill | 用法 | 說明 |
|-------|------|------|
| `web_search` | `web_search("關鍵字")` | 搜尋網頁 |
| `web_fetch` | `web_fetch("https://...")` | 抓取特定網頁 |
| `tavily` | `tavily search "關鍵字"` | 即時搜尋（需 TAVILY_API_KEY） |
| `blogwatcher` | `blogwatcher monitor "url"` | 監控 RSS/Blog 更新 |
| `deep-research-pro` | `deep-research-pro "問題"` | 深度多來源研究 |

## 🤖 瀏覽器自動化 (agent-browser)

比 peekaboo 更強大的全功能瀏覽器控制：

```bash
agent-browser open "https://..."            # 開啟網頁
agent-browser snapshot -i                   # 取得互動元素清單（含 ref）
agent-browser click @e1                     # 點擊元素（用 snapshot 取得 ref）
agent-browser fill @e2 "文字"               # 填寫輸入框
agent-browser screenshot                    # 截圖
agent-browser screenshot --full page.png    # 全頁截圖存檔
agent-browser pdf output.pdf               # 輸出 PDF
agent-browser get title                     # 取得頁面標題
agent-browser get text @e1                  # 取得元素文字
agent-browser find text "登入" click        # 語義搜尋元素並點擊
agent-browser state save auth.json         # 儲存 Cookie/登入狀態
agent-browser state load auth.json         # 載入已儲存的登入狀態
agent-browser record start demo.webm       # 錄製操作影片
agent-browser record stop
agent-browser close                         # 關閉瀏覽器
```

**常用流程：**
```bash
# 1. 開啟 → 2. 取元素 → 3. 操作 → 4. 確認
agent-browser open "https://example.com"
agent-browser snapshot -i    # 看到 ref 如 @e1, @e2, @e3
agent-browser fill @e1 "帳號"
agent-browser fill @e2 "密碼"
agent-browser click @e3      # 登入按鈕
```

---

## 📅 Google Workspace (gog)

```bash
gog calendar events --today              # 今日行程
gog calendar events --days 7             # 未來 7 天
gog gmail search 'is:unread' --limit 10  # 未讀郵件
gog gmail search '關鍵字' --limit 5      # 搜尋郵件
gog drive list                           # Google Drive
gog drive upload "檔案路徑"              # 上傳檔案
```

---

## 📝 筆記 & 任務

| Skill | 指令 | 說明 |
|-------|------|------|
| `apple-notes` | `memo list / memo new "標題" "內容"` | Apple Notes |
| `apple-reminders` | `remindctl list / remindctl add "內容"` | ⚠️ 用 remindctl，不是 apple-reminders |
| `things-mac` | `things list / things add "任務"` | Things 3 |
| `obsidian` | `obsidian-cli search "關鍵字"` | Obsidian Vault |
| `bear-notes` | `grizzly list / grizzly new "標題"` | Bear Notes |

---

## 🎥 YouTube (youtube-full)

```bash
# ⚠️ 需要 TRANSCRIPT_API_KEY（目前額度用完，用 youtube-transcript-api Python 替代）
youtube-full search "關鍵字" --limit 10
youtube-full transcript "VIDEO_ID"
youtube-full channel "CHANNEL_ID" --limit 5

# 免費替代方案（Python）：
python3 -c "
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
transcript = api.fetch('VIDEO_ID')
print([s.text for s in transcript])
"

# YouTube RSS（不需 API Key）：
curl -s 'https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID'
```

---

## 📸 圖片 & 影片

| Skill | 用法 | 說明 |
|-------|------|------|
| `camsnap` | `camsnap capture` | 攝影機截圖 |
| `peekaboo` | `peekaboo screenshot` | macOS UI 截圖/自動化 |
| `video-frames` | `video-frames "影片路徑"` | 截取影片幀 |
| `watermark-remover` | `watermark-remover "圖片路徑"` | 去除浮水印 |
| `songsee` | `songsee "音頻路徑"` | 音頻分析頻譜圖 |
| `gifgrep` | `gifgrep search "關鍵字"` | GIF 搜尋下載 |
| `nano-pdf` | `nano-pdf edit "PDF路徑"` | PDF 自然語言編輯 |

---

## 🔊 語音 & 音樂

| Skill | 用法 | 說明 |
|-------|------|------|
| `sag` | `sag speak "文字" --voice "zh-TW"` | ElevenLabs TTS |
| `openai-whisper` | `whisper "音頻檔"` | 本地語音轉文字（離線） |
| `voice-call` | 透過 OpenClaw | 語音通話（需設定） |
| `spotify-player` | `spogo play "歌名"` | Spotify 播放 |
| `sonoscli` | `sonos play / sonos volume 50` | Sonos 喇叭控制 |
| `blucli` | `blu play / blu volume` | BluOS 音響控制 |

---

## 💻 程式開發

| Skill | 用法 | 說明 |
|-------|------|------|
| `coding-agent` | `coding-agent "任務描述"` | 委派複雜開發任務給 Codex/Claude Code |
| `github` | `gh issue list / gh pr create` | GitHub Issues/PRs |
| `gh-issues` | `gh-issues owner/repo` | 批次修 GitHub issues |
| `skill-creator` | `skill-creator create "名稱"` | 建立/改善 skill |
| `tmux` | `tmux new-session -d` | Terminal session 管理 |

---

## 📨 通訊 & 訊息

| Skill | 用法 | 說明 |
|-------|------|------|
| `imsg` | `imsg send "電話" "訊息"` | iMessage/SMS |
| `wacli` | `wacli send "電話" "訊息"` | WhatsApp |
| `xurl` | `xurl post "推文"` | X (Twitter) API |
| `himalaya` | `himalaya list / himalaya send` | IMAP/SMTP 郵件 |
| `session-logs` | `session-logs search "關鍵字"` | 搜尋對話歷史紀錄 |

---

## 🌤️ 資訊 & 實用

| Skill | 用法 | 說明 |
|-------|------|------|
| `weather` | `exec("curl -s 'wttr.in/Taichung?format=3&lang=zh-tw'")` | ⚠️ 用 curl，不是 weather 命令 |
| `Polymarket` | `polymarket search "事件"` | 預測市場賠率 |
| `oracle` | `oracle "問題" --engine claude` | AI 問答 bundler |
| `gemini` | `gemini "問題"` | Google Gemini AI |
| `ordercli` | `ordercli orders` | Foodora 訂單查詢 |
| `content-watcher` | 監控 RSS + AI 摘要 | 自動內容監控 |
| `rss-ai-reader` | RSS 訂閱 + AI 摘要 | RSS 閱讀器 |

---

## 🏠 智慧家居

| Skill | 用法 | 說明 |
|-------|------|------|
| `openhue` | `openhue list / openhue scene "名稱"` | Philips Hue 燈控 |
| `eightctl` | `eightctl status / eightctl temp` | Eight Sleep 床墊 |

---

## 🔧 系統 & 維護

| Skill | 用法 | 說明 |
|-------|------|------|
| `healthcheck` | `healthcheck run` | 系統安全掃描 |
| `openclaw-auto-updater` | `openclaw-auto-updater check` | 自動更新排程 |
| `clawhub` | `npx clawhub search "關鍵字"` | 搜尋/安裝新 skills |
| `mcporter` | `mcporter list` | MCP 伺服器管理 |
| `1password` | `op item get "名稱"` | 1Password 密碼管理 |
| `model-usage` | `codexbar cost --model current` | AI 使用量/費用 |

---

## 📊 社群 & 內容成長

| Skill | 用法 | 說明 |
|-------|------|------|
| `ig-carousel` | `ig-carousel post crypto` | IG Carousel 自動發文（RSS→AI改寫→去AI味→Hook優化→10張圖→發文） |
| `tiktok-growth` | 內容策略 + 腳本生成 | TikTok 成長策略、Hook 公式、90天計劃 |
| `x-research` | `x-research search "關鍵字"` | X/Twitter 研究（TwitterAPI.io，需 TWITTERAPI_KEY） |
| `humanizer` | `humanizer score "文字"` | 偵測 AI 痕跡、改寫成自然人話 |
| `content-watcher` | `content-watcher add "RSS url"` | 監控 RSS + AI 摘要 |

## 🔬 研究 & 分析

| Skill | 用法 | 說明 |
|-------|------|------|
| `deep-research-pro` | 多來源深度研究 | 不需 API Key，DuckDuckGo + 合成報告 |
| `brave-search` | `brave-search "關鍵字"` | Brave Search API（需 BRAVE_API_KEY） |
| `tavily` | `tavily search "關鍵字"` | AI 最佳化搜尋（需 TAVILY_API_KEY） |
| `Polymarket` | `polymarket search "事件"` | 預測市場即時賠率（免費） |
| `evomap-tools` | AI Agent 進化市場 | 發佈/取得 Capsule |

## 🔁 自我進化

| Skill | 用法 | 說明 |
|-------|------|------|
| `self-improvement` | 自動觸發（錯誤/糾正時） | 記錄錯誤、學習、功能需求到 `.learnings/` |
| `proactive-agent` | 自動觸發（任務前） | 主動規劃、記憶歷史、減少重複詢問 |
| `find-skills` | `find-skills "我要做 XX"` | 自動搜尋並安裝合適的 skill |
| `skill-vetter` | `skill-vetter "skill名稱"` | 安裝前安全審計 |
| `capability-evolver` | `/evolve` | 分析歷史紀錄自我進化 |
| `confucius-debug` | 自動觸發（遇錯時） | 6800+ issue 知識庫即時修復（需 CONFUCIUS_LOBSTER_ID） |
| `trend-watcher` | 監控 GitHub trending | 追蹤新工具和技術趨勢 |

## 🧠 記憶 & 知識

| Skill | 用法 | 說明 |
|-------|------|------|
| `memory_search` | `memory_search("關鍵字")` | 搜尋長期記憶 |
| `memory_get` | `memory_get("qmd://memory/...")` | 讀取特定記憶 |
| `ontology` | `ontology create person "名字"` | 結構化知識圖譜 |

---

## ❌ 目前不可用（需要 API Key）

| Skill | 需要 |
|-------|------|
| `discord` | Discord bot token |
| `slack` | Slack workspace |
| `notion` | NOTION_API_KEY |
| `trello` | TRELLO_API_KEY |
| `openai-image-gen` | OPENAI_API_KEY |
| `openai-whisper-api` | OPENAI_API_KEY |
| `nano-banana-pro` | GEMINI_API_KEY |
| `goplaces` | GOOGLE_PLACES_API_KEY |
| `sherpa-onnx-tts` | 本地模型路徑設定 |
| `confucius-debug` | CONFUCIUS_LOBSTER_ID |
| `bluebubbles` | BlueBubbles App |
| `polyclaw` | POLYCLAW_PRIVATE_KEY |
| `twitter-openclaw` | TWITTER_BEARER_TOKEN |
