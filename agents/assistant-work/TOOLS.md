# 工具清單 - Assistant-Work

## 可直接使用的工具

| 工具 | 用法 | 何時用 |
|------|------|--------|
| `web_search` | `web_search("關鍵字")` | 找熱門話題、競品分析 |
| `web_fetch` | `web_fetch("https://...")` | 抓取參考內容 |
| `memory_recall` | `memory_recall("關鍵字")` | 搜尋過去記憶 |
| `exec` | `exec("bash命令")` | 執行系統指令 |
| `read` | `read("檔案路徑")` | 讀取檔案 |
| `write` | `write("路徑", "內容")` | 寫入檔案 |

## X/Twitter (xurl skill)

```bash
xurl post "推文內容 #hashtag"    # 發推文
xurl search "關鍵字" --count 20  # 搜尋推文
xurl timeline --count 10        # 時間軸
xurl like <tweet_id>            # 按讚
xurl reply <tweet_id> "回覆"     # 回覆
```

## 瀏覽器自動化 (agent-browser — 社群平台網頁版)

```bash
# IG、抖音、Twitch、YouTube 網頁版操作
agent-browser open "https://www.instagram.com"
agent-browser snapshot -i              # 取得互動元素清單
agent-browser click @e1                # 點擊元素
agent-browser fill @e2 "文字"          # 填寫輸入框
agent-browser find text "發布" click   # 語義點擊按鈕
agent-browser screenshot               # 截圖
agent-browser state save ig-auth.json  # 儲存 IG 登入狀態
agent-browser state load ig-auth.json  # 下次直接載入已登入狀態
agent-browser close

# 常用平台 URL
# IG:    https://www.instagram.com
# 抖音:  https://www.tiktok.com
# Twitch: https://www.twitch.tv
# YouTube: https://studio.youtube.com
```

## macOS 畫面截圖 (peekaboo)

```bash
peekaboo image screen                  # 截取整個 Mac 畫面
peekaboo list apps                     # 列出開啟的 App
```

> 規則：操作**社群平台網站**用 agent-browser；截取 Mac 畫面用 peekaboo

## WhatsApp (wacli skill)

```bash
wacli send --to "電話號碼" "訊息"
wacli list
```

## IG Carousel 自動發文（ig-carousel skill）

> ⚠️ **所有 IG 發文都用 `ig-carousel` skill**，不要直接跑 python 腳本

```bash
# ── 推薦流程（9 步驟）：Draft → 選封面 → Publish ──────────

# Step 1: 生成草稿 + 3 張 AI 封面候選
ig-carousel draft crypto

# Step 2: 預覽最新草稿
ig-carousel preview crypto

# Step 3: understand_image 看 3 張封面候選
#   cover_candidate_1.jpg / cover_candidate_2.jpg / cover_candidate_3.jpg

# Step 4: 通知老闆選封面
#   sessions_send(-5107483605, "📸 封面候選已生成，請選 1/2/3")

# Step 5: 套用選中的封面（N=1/2/3）
ig-carousel select-cover crypto 2

# Step 6-7: humanizer 去 AI 味 + Hook 優化（改寫 caption.txt）

# Step 8: 發布
ig-carousel publish crypto

# Step 9: memory_store 記錄

# ── 直接發文（跳過選封面，不推薦）────────────────────────
ig-carousel post crypto
ig-carousel post finance
ig-carousel post startup

# ── 查看發文歷史 ──────────────────────────────────────────
ig-carousel history
```

### 封面候選位置
草稿產出在 `~/.openclaw/workspace/agents/assistant-work/cards/<channel>_<timestamp>/`
- `cover_candidate_1.jpg` ~ `cover_candidate_3.jpg`：3 張 AI 封面候選
- `caption.txt`：文案
- `article_meta.json`：文章 metadata

### 手動發圖（不經 pipeline）
```bash
exec("python3 ~/.openclaw/workspace/scripts/social-media/ig_post.py --images /tmp/s1.jpg /tmp/s2.jpg --caption '文案'")
```

### 帳號設定

| 頻道 | IG 帳號 | 風格 | Config |
|------|---------|------|--------|
| crypto | @money.showtime | 黑金財經（abmedia_io） | ig_config.json |
| finance | @money.showtime | 黑金財經（abmedia_io） | ig_config.json |
| startup | ⚠️ 待設定新帳號 | 極簡（the_insight_circle） | startup_ig_config.json |

### 新創業帳號設定步驟（老闆操作）
1. 在 IG 上建立新帳號
2. 填入帳號資料：`~/.openclaw/workspace/scripts/social-media/startup_ig_config.json`
3. 修改 `content_pipeline.py` 第 31 行，把 `startup` 的 ig_config 改成 `startup_ig_config.json`

## Agent 協作工具

| 工具 | 用法 |
|------|------|
| `sessions_send` | 發訊息給其他 Agent |
| `sessions_list` | 查看活躍 sessions |

## ⚠️ 禁止

- 不要在非工作時間（14:00-23:00以外）發布內容
- 不要使用 OpenAI API
- 不要編造不存在的工具名稱
