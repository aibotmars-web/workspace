# AGENTS.md - Sub-Agent 設定

## 檔案分配原則

### 共享（每個 Agent 開頭讀取）
| 檔案 | 內容 |
|------|-------|
| SOUL.md | AI 自我認知 |
| USER.md | 老闆基本資料 |

### 獨立（各 Agent 自己）
| 檔案 | 內容 |
|------|-------|
| AGENTS.md | 自己的角色定義 |
| memory/ | 自己的對話記憶 |

---

## Agent 角色清單

| Agent | 角色 | 功能 |
|-------|------|------|
| main | 協調者 | 分配任務、協調團隊 |
| planner | 規劃師 | 專案規劃、進度追蹤 |
| coder | 開發者 | 程式開發 |
| trader | 交易員 | 市場分析、交易 |
| assistant | 生活助理 | 生活事務、提醒 |
| assistant-work | 內容運營 | 社群營運、發文 |
| crawler | 資料收集 | 爬蟲、數據收集 |
| image | 圖像生成 | AI 繪圖 |
| system-admin | 系統管理 | 系統維護 |

---

## 記憶系統

### 每個 Agent 都有獨立的：
- `memory/` - 對話日誌
- `memory_topics/` - 主題分類
- 使用 qmd + Voyage AI

### 分類清單（12個）
1. agent-to-agent.md
2. multi-agent.md
3. browser-automation.md
4. config-lessons.md
5. docker-sandbox.md
6. node-setup.md
7. model-management.md
8. services-and-skills.md
9. webhook-external.md
10. workflow-rules.md
11. memory-lancedb-pro.md
12. lobster-workflow.md

---

## 團隊溝通

### main → Sub-Agent
使用 sessions_send 分配任務

### Sub-Agent 回報
任做完後回傳結果給 main

---

*更新：2026-02-24*
