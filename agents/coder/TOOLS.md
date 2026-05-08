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

## 🧠 gstack Skills（工程流程）

gstack 是 OpenClaw 的工程協作套件，位於 `~/.openclaw/skills/gstack/`。

| Skill | 指令 | 說明 | 何時用 |
|-------|------|------|--------|
| `office-hours` | `openclaw skill run office-hours '任務說明'` | Think & Plan：開始任務前確認方向、技術評估 | **新任務必做**，避免走錯方向 |
| `review` | `openclaw skill run review '程式碼路徑或內容'` | Code Review：找 CRITICAL/HIGH 問題 | **每次寫完程式碼後必做** |
| `qa` | `openclaw skill run qa '專案名稱 + 功能說明'` | 品質確認：UI/API/整合測試 | Web 專案 ship 前必做 |
| `ship` | `openclaw skill run ship '專案名稱 + 說明'` | 部署：通過 review + qa 後執行 | 正式部署流程 |
| `cso` | `openclaw skill run cso '問題描述'` | Chief Security Officer 安全審查 | 有 auth/API key/用戶資料時用 |
| `design-shotgun` | `openclaw skill run design-shotgun '設計需求'` | 快速生成多版設計方案（散彈槍法） | 需要 UI/UX 方案時 |
| `canary` | `openclaw skill run canary '要驗證的功能'` | Canary 測試：小範圍驗證再全量 | 高風險變更上線前 |

**gstack 工程流程**：office-hours → Build → review → qa → ship

---

## 🦌 DeerFlow 深度研究

DeerFlow 是本地 AI 研究框架，用於需要多步驟資料收集和分析的任務。

**路徑**：`~/.openclaw/skills/claude-to-deerflow/`

```bash
# 1. 先確認 DeerFlow 是否在線
exec("curl -s http://localhost:8001/health")
# 回傳 {"status":"healthy"} 代表正常

# 2. 發送研究任務
exec("bash ~/.openclaw/skills/claude-to-deerflow/scripts/chat.sh '研究問題'")
```

**何時用**：
- 需要蒐集大量網路資料（競品分析、技術調查）
- 多步驟研究任務（需要搜尋→整合→分析）
- 老闆交辦的深度研究報告

**注意**：DeerFlow 無法連線時直接跳過，用 `web_search` 替代

---

## 🔬 AutoResearch（ML 實驗）

AutoResearch 是自動化機器學習實驗框架，用於隔夜 ML 訓練優化。

**路徑**：`~/.openclaw/skills/autoresearch/`，實驗程式碼在 `~/.openclaw/workspace/autoresearch/`

```bash
# 準備資料
exec("~/.openclaw/workspace/skills/autoresearch/scripts/ar-prepare.sh")

# 啟動 session（tag 格式 mmdd，如 apr3）
exec("~/.openclaw/workspace/skills/autoresearch/scripts/ar-start.sh <tag>")

# 訓練（固定 5 分鐘/輪）
exec("cd ~/.openclaw/workspace/autoresearch && ~/.local/bin/uv run train.py")

# 查看結果
exec("~/.openclaw/workspace/skills/autoresearch/scripts/ar-results.sh")
```

**目標**：讓 `val_bpb`（validation bits per byte）越低越好
**注意**：不要修改 `prepare.py`，只改 `train.py`

---

## 完整 Skills 清單

參考：`~/.openclaw/workspace/SKILLS.md`

## ⚠️ 禁止

- 不要修改 `~/.openclaw/openclaw.json`（系統設定）
- 不要 `rm -rf`，用 `trash` 代替
- 不要自動 push 到 main branch
