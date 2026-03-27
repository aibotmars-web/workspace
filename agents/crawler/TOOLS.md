# 工具清單 - Crawler

## 可直接使用的工具

| 工具 | 用法 | 何時用 |
|------|------|--------|
| `web_search` | `web_search("關鍵字")` | 搜尋網頁資料 |
| `web_fetch` | `web_fetch("https://...")` | 抓取特定網頁 |
| `memory_recall` | `memory_recall("關鍵字")` | 搜尋過去記憶 |
| `memory_store` | `memory_store("內容", category, importance)` | 存入長期記憶 |
| `exec` | `exec("bash命令")` | 執行系統指令 |
| `read` | `read("檔案路徑")` | 讀取檔案 |
| `write` | `write("路徑", "內容")` | 寫入檔案 |

---

## YouTube 字幕抓取（唯一方法：kd CLI）

### 方法 1: kd subtitles（快速，抓現成字幕）
```bash
exec("kd subtitles 'https://www.youtube.com/watch?v=VIDEO_ID' -o /tmp/output.txt")
```

### 方法 2: kd transcribe（本地 ASR，保證成功，3-10 分鐘）
```bash
exec("kd transcribe 'https://www.youtube.com/watch?v=VIDEO_ID' --no-subtitles --backend mlx-whisper -o /tmp/output.txt")
```

### 列出頻道影片（用 yt-dlp，安全不會被封）
```bash
exec("yt-dlp --flat-playlist --print '%(id)s|%(title)s' 'https://www.youtube.com/@CHANNEL/videos' --playlist-end 3")
```

---

## 9 位專家知識蒸餾

**不要自己手動抓，直接執行腳本：**
```bash
exec("cd ~/.openclaw/workspace/knowledge-base/experts && python3 smart_update.py 2>&1")
```

腳本會自動：yt-dlp 列表 → kd subtitles 抓字幕 → kd transcribe 備援 ASR

| 專家 | YouTube @ | 目錄 |
|------|-----------|------|
| 胡乃文开播 | @Dr.Hu_talk | transcripts/胡乃文开播/ |
| 柏格醫生中文 | @drbergchinese | transcripts/柏格醫生中文/ |
| Dr.HuangAmin | @Dr.HuangAmin | transcripts/Dr.HuangAmin/ |
| 周慕姿放心說 | @muerstalk | transcripts/周慕姿放心說/ |
| 松明讲心理 | @SongMing | transcripts/松明讲心理/ |
| 超真實商談 | @RealBizChat | transcripts/超真實商談/ |
| Cofit211 | @Cofit211 | transcripts/Cofit211/ |
| 泛科學 | @PanScitw | transcripts/泛科學/ |
| 泛科學院 | @panscischool | transcripts/泛科學院/ |

---

## 網頁爬蟲 (agent-browser)

```bash
agent-browser open "https://..."       # 開啟網頁
agent-browser snapshot -i              # 列出互動元素
agent-browser get text @e1             # 取得元素文字
agent-browser screenshot               # 截圖
agent-browser close                    # 關閉
```

---

## Agent 協作工具

| 工具 | 用法 |
|------|------|
| `sessions_send` | 發訊息給其他 Agent |
| `sessions_list` | 查看活躍 sessions |

---

## ⚠️ 禁止（會失敗的做法）

| 禁止 | 原因 |
|------|------|
| `youtube-transcript-api` Python | IP 被 YouTube 封鎖 |
| `youtube-skills` | 不存在的 skill 名稱 |
| `yt-dlp` 抓字幕 | 會 429 限流（列表可以用） |
| `TranscriptAPI.com` | 帳戶無付費方案 |
| OpenAI API | 沒有 key |
| 下載影片檔案 | 只抓字幕，硬碟空間有限 |
| 編造工具名 | 查此清單確認 |
