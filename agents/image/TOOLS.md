# TOOLS.md - Image 工具清單

## 可用工具

| 工具 | 用法 | 說明 |
|------|------|------|
| `exec` | `exec("bash命令")` | 執行系統指令 |
| `understand_image` | `understand_image("圖片路徑")` | AI 圖片分析 |
| `web_search` | `web_search("設計靈感 關鍵字")` | 搜尋參考圖 |
| `web_fetch` | `web_fetch("https://...")` | 下載圖片/素材 |
| `read` | `read("檔案路徑")` | 讀取檔案 |
| `write` | `write("路徑", "內容")` | 寫入檔案 |
| `memory_recall` | `memory_recall("設計")` | 搜尋過去的設計紀錄 |

## 🎨 圖片工具

```bash
# MiniMax 圖片生成（透過 API）
# 使用 OpenClaw 內建 image generation tool

# macOS 截圖
peekaboo image screen
peekaboo image window "應用名"

# 圖片分析
understand_image("圖片路徑或URL")

# 去除浮水印
watermark-remover "圖片路徑"

# 影片截圖
video-frames "影片路徑" --count 10
```

## 📸 IG Carousel 圖片生成

```bash
# 用 ig-carousel skill（推薦）
exec("ig-carousel draft crypto")     # 生成草稿（含圖片）
exec("ig-carousel preview crypto")   # 預覽

# 直接跑圖片生成（進階）
exec("cd ~/.openclaw/workspace/scripts/social-media && python3 make_card.py")

# 圖片品質檢查
understand_image("生成的圖片路徑")
```

**make_card.py 功能：** 1080x1080 圖片、文字排版、漸層背景、走勢圖、algorithmic-art 背景

## 🎤 語音合成

```bash
# ElevenLabs TTS
sag speak "文字" --voice "zh-TW"

# GIF 搜尋
gifgrep search "關鍵字"
```

## 完整 Skills 清單

參考：`~/.openclaw/workspace/SKILLS.md`

## ⚠️ 禁止

- 不要生成不當內容
- 不要使用版權圖片未經授權
- 不要使用 OpenAI API
