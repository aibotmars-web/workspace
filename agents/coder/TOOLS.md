# TOOLS.md - Coder 工具清單

## 可用工具

| 工具 | 用法 | 說明 |
|------|------|------|
| `exec` | `exec("bash命令")` | 執行系統指令（主要工具） |
| `read` | `read("檔案路徑")` | 讀取檔案 |
| `write` | `write("路徑", "內容")` | 寫入檔案 |
| `web_search` | `web_search("關鍵字")` | 查技術文件 |
| `web_fetch` | `web_fetch("https://...")` | 抓取 API 文件 |
| `memory_recall` | `memory_recall("關鍵字")` | 搜尋過去的技術筆記 |
| `memory_store` | `memory_store("內容", ...)` | 儲存技術解法 |

## 開發工具

```bash
# Git
exec("git status && git log --oneline -10")
exec("git diff HEAD~1")

# Python
exec("python3 script.py")
exec("pip3 install 套件")

# Node.js
exec("node script.js")
exec("npm install 套件")
```

## 🐙 GitHub

```bash
gh issue list --repo owner/repo
gh pr create --title "修復" --body "說明"
gh-issues owner/repo --label bug --limit 5
```

## 🧩 開發 Skills

| Skill | 用途 |
|-------|------|
| `coding-agent` | 委派複雜任務給 Claude Code/Codex |
| `github` / `gh-issues` | GitHub 操作 |
| `skill-creator` | 建立/改善 OpenClaw skills |
| `tmux` | Terminal session 管理 |
| `confucius-debug` | 6800+ 已知問題即時修復 |
| `agent-browser` | 瀏覽器自動化（調試 Web UI） |

## 完整 Skills 清單

參考：`~/.openclaw/workspace/SKILLS.md`

## ⚠️ 禁止

- 不要修改 `~/.openclaw/openclaw.json`（系統設定）
- 不要 `rm -rf`，用 `trash` 代替
- 不要自動 push 到 main branch
