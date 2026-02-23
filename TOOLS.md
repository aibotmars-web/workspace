# 統一工具清單 - 全體 Agents 共享

## ⚡ 使用說明

所有 Sub-Agents 都能使用以下工具，**需要時直接調用**：

---

## 🔧 可用工具清單

### 1. 內建工具（無需設定）

| 工具 | 功能 | 使用時機 |
|------|------|---------|
| `web_search` | 網頁搜尋 | 找資料、查詢資訊時 |
| `understand_image` | 圖片理解 | 看到截圖、圖片、需要分析視覺內容時 |
| `memory_search` | 搜尋記憶 | 需要回想過去討論過的內容時 |
| `memory_get` | 讀取記憶 | 需要讀取特定記憶檔案時 |

### 2. 已安裝 Skills

| 工具 | 功能 | 使用時機 |
|------|------|---------|
| `youtube-skills` | YouTube 搜尋、字幕抓取 | 需要 YouTube 相關功能時 |
| `transcriptapi` | YouTube 字幕 | 需要抓取影片字幕時 |
| `coding-agent` | 程式開發 | 需要寫程式、開發專案時 |
| `github` | Git 操作 | 需要 Git 版本控制時 |
| `gog` | Google Workspace | 需要操作 Google 行事曆、郵件時 |
| `bird` | X (Twitter) | 需要發推文、操作 X 時 |
| `peekaboo` | 瀏覽器自動化 | 需要自動化網頁操作時 |
| `wacli` | WhatsApp | 需要操作 WhatsApp 時 |
| `sag` | ElevenLabs TTS | 需要文字轉語音時 |
| `weather` | 天氣查詢 | 需要查詢天氣時 |
| `things-mac` | Things 3 | 需要管理待辦事項時 |
| `apple-reminders` | Apple 提醒事項 | 需要設定提醒時 |

### 3. 系統工具

| 工具 | 功能 | 使用時機 |
|------|------|---------|
| `exec` | 執行命令 | 需要在系統上執行指令時 |
| `read` | 讀取檔案 | 需要讀取檔案內容時 |
| `write` | 寫入檔案 | 需要儲存資料到檔案時 |
| `Browser` | 瀏覽器控制 | 需要自動化瀏覽器操作時 |

---

## ✅ 使用原則

### 什麼時候該用什麼工具？

```
需要找資料 → web_search
看到圖片 → understand_image  
需要回想過去 → memory_search
需要寫程式 → coding-agent
需要 Git 操作 → github
需要自動化網頁 → peekaboo / Browser
需要發社群 → bird / wacli
需要語音 → sag
```

### 重要提醒

1. **直接使用** - 不需要問老闆，根據需求直接調用
2. **選對工具** - 用錯工具會浪費時間
3. **查詢清單** - 不確定時回來看這份清單

---

## 📝 更新紀錄

2026-02-20: 優化為通用工具系統，所有 Agents 都能使用全部工具
