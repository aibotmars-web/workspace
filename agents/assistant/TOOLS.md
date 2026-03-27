# TOOLS.md - Assistant 工具清單

## 可用工具

| 工具 | 用法 | 說明 |
|------|------|------|
| `exec` | `exec("bash命令")` | 執行系統指令 |
| `web_search` | `web_search("關鍵字")` | 搜尋網頁 |
| `read` / `write` | 讀寫檔案 | 檔案操作 |
| `memory_recall` / `memory_store` | 記憶管理 | 搜尋/儲存長期記憶 |

## 📅 Google Workspace

```bash
gog calendar events --today              # 今日行程
gog calendar events --days 7             # 未來 7 天
gog gmail search 'is:unread' --limit 10  # 未讀郵件
```

## 📝 筆記 & 任務

| Skill | 指令 | 說明 |
|-------|------|------|
| `apple-notes` | `memo list` / `memo new "標題" "內容"` | Apple Notes |
| `apple-reminders` | `remindctl list` / `remindctl add "內容"` | ⚠️ 用 remindctl |
| `things-mac` | `things list today` / `things add "任務"` | Things 3 |
| `obsidian` | `obsidian-cli search "關鍵字"` | Obsidian |

## 🌤️ 日常資訊

```bash
exec("curl -s 'wttr.in/Taichung?format=3&lang=zh-tw'")  # 天氣
imsg send "+886..." "訊息"                                 # iMessage
polymarket search "事件"                                    # 預測市場
```

## 完整 Skills 清單

參考：`~/.openclaw/workspace/SKILLS.md`

