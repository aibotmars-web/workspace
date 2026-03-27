# TOOLS.md - Planner 工具清單

## 可用工具

| 工具 | 用法 | 說明 |
|------|------|------|
| `exec` | `exec("bash命令")` | 執行系統指令 |
| `web_search` | `web_search("關鍵字")` | 搜尋資料做規劃 |
| `web_fetch` | `web_fetch("https://...")` | 抓取文件 |
| `read` | `read("檔案路徑")` | 讀取專案檔案 |
| `write` | `write("路徑", "內容")` | 寫入規劃文件 |
| `memory_recall` | `memory_recall("專案名")` | 搜尋過去專案紀錄 |
| `memory_store` | `memory_store("決策", ...)` | 儲存重要決策 |
| `sessions_send` | `sessions_send("agent:id", "任務")` | 派發任務給專屬 Agent |

## 📋 任務管理

```bash
# 進度追蹤（bd 工具）
bd list
bd add "任務描述"
bd update "任務ID" --status done

# Telegram 通知
sessions_send("agent:main", "任務完成報告")
```

## 🔬 規劃研究

| Skill | 用途 |
|-------|------|
| `deep-research-pro` | 多來源深度研究（不需 API Key） |
| `Polymarket` | 預測市場賠率（風險評估） |
| `trend-watcher` | GitHub 新工具趨勢追蹤 |
| `ontology` | 結構化知識圖譜（專案關係管理） |

## Agent 派工

```bash
# 派任務給 Coder
sessions_send("agent:main:coder", "修復 content_pipeline.py 的 JSON 解析")

# 派任務給 Crawler
sessions_send("agent:main:crawler", "研究最新 IG 演算法趨勢")

# 派任務給 Image
sessions_send("agent:main:image", "設計新的 Carousel 模板")
```

## 完整 Skills 清單

參考：`~/.openclaw/workspace/SKILLS.md`
