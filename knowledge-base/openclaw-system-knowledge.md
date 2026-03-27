# OpenClaw 系統架構知識庫

*建立時間：2026-03-25*
*最後更新：2026-03-25*

---

## 1. 系統架構（Gateway Architecture）

### 核心元件

| 元件 | 說明 |
|------|------|
| **Gateway** | 單一長期運行的守護進程，掌控所有訊息介面（Telegram, WhatsApp, Discord等） |
| **Clients** | macOS App / CLI / Web Admin，透過 WebSocket 連接到 Gateway |
| **Nodes** | macOS / iOS / Android / headless 節點，透過 WebSocket 連接 |
| **Canvas Host** | Gateway HTTP 伺服器提供 `/__openclaw__/canvas/` 和 `/__openclaw__/a2ui/` |

### WebSocket 協議

- 傳輸：WebSocket，text frames + JSON payloads
- 首幀**必須**是 `connect`
- 請求：`{type:"req", id, method, params}` → `{type:"res", id, ok, payload|error}`
- 事件：`{type:"event", event, payload, seq?, stateVersion?}`
- 冪等鑰匙：對有副作用的方法（`send`, `agent`）需要冪等鑰匙

### 連線生命週期

```
Client → Gateway: req:connect
Gateway → Client: res (ok)
Gateway → Client: event:presence
Gateway → Client: event:tick
Client → Gateway: req:agent
Gateway → Client: res:agent (ack)
Gateway → Client: event:agent (streaming)
Gateway → Client: res:agent (final)
```

---

## 2. Memory 系統

### 記憶檔案架構

OpenClaw 的記憶是**純 Markdown，放在 agent workspace**。檔案是真理來源。

| 檔案 | 用途 |
|------|------|
| `memory/YYYY-MM-DD.md` | 每日日誌（append-only），開啟時讀取今天和昨天 |
| `MEMORY.md` | 精選長期記憶，僅在主對話載入 |

### 記憶工具

- `memory_search` — 對索引片段進行語意搜尋
- `memory_get` — 讀取特定 Markdown 檔案/行範圍
- 兩個工具都會優雅降級：檔案不存在時返回空文字而不是拋出錯誤

### 自動記憶刷新（Pre-compaction Ping）

當 session **接近自動精簡**時，OpenClaw 觸發一個**靜默的 agentic turn**，提醒 model 在上下文被精簡**之前**寫入持久記憶。

```json5
{
  compaction: {
    reserveTokensFloor: 20000,
    memoryFlush: {
      enabled: true,
      softThresholdTokens: 4000,
      prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply NO_REPLY if nothing.",
    },
  },
}
```

---

## 3. Multi-Agent 多代理系統

### 什麼是一個 Agent？

一個 **agent** 是一個完整作用域的大脑，有自己的：

- **Workspace**（檔案、AGENTS.md/SOUL.md/USER.md、局部筆記、人物設定規則）
- **State directory**（`agentDir`）- auth profiles、model registry、per-agent 設定
- **Session store**（聊天歷史 + 路由狀態）放在 `~/.openclaw/agents/<agentId>/sessions`

### 路徑對照

| 項目 | 路徑 |
|------|------|
| Config | `~/.openclaw/openclaw.json` |
| State dir | `~/.openclaw` |
| Workspace | `~/.openclaw/workspace` |
| Agent dir | `~/.openclaw/agents/<agentId>/agent` |
| Sessions | `~/.openclaw/agents/<agentId>/sessions` |

### 路由規則（Message → Agent 映射）

Bindings 是**確定的**且**最具體者獲勝**：

1. `peer` 匹配（精確 DM/group/channel id）
2. `parentPeer` 匹配（thread 繼承）
3. `guildId + roles`（Discord role 路由）
4. `guildId`（Discord）
5. `teamId`（Slack）
6. `accountId` 匹配
7. channel-level 匹配
8. fallback 到預設 agent

### Agent 隔離

- Auth profiles 是 **per-agent** 的
- 不要跨 agent 重用 `agentDir`（會造成 auth/session 衝突）
- 如果要共用 creds，複製 `auth-profiles.json` 到其他 agent 的 `agentDir`

---

## 4. SecretRef & 設定管理

### 核心概念

**SecretRef** 讓你用 `{provider, id}` 引用敏感資料，而不是把明文寫進 `openclaw.json`。

### CLI 工作流（configure → plan → apply）

```bash
# 1. 審計
openclaw secrets audit --check

# 2. 互動式設定
openclaw secrets configure

# 3. 預覽計劃
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run

# 4. 執行計劃
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json

# 5. 重新載入運行時快照
openclaw secrets reload
```

### 2026.3.22 SecretRef 重大改進

| 以前 | 現在 |
|------|------|
| 手改 JSON + 看 source code | `secrets configure` 互動式引導 |
| 只能自己摸索 spec | `plan` → `apply` 完整流程 |
| 懂的人才能用 | 一般使用者也能上手 |
| "spec-driven" | **"workflow-driven"** |

**這是成熟度的關鍵跳躍**：從「學習工具」變成「使用工具」。

---

## 5. Cron 系統

### 基本用法

```bash
# 添加 cron job
openclaw cron add \
  --name "my-job" \
  --cron "0 9 * * *" \
  --agent main \
  --session isolated \
  --message "要做什麼" \
  --announce \
  --channel telegram \
  --to 1073451144

# 列出所有 cron jobs
openclaw cron list

# 立即執行
openclaw cron run <job-id>

# 禁用/啟用
openclaw cron disable <job-id>
openclaw cron enable <job-id>
```

### 選項說明

| 選項 | 說明 |
|------|------|
| `--cron` | cron 表達式（5-field 或 6-field） |
| `--every` | 持續時間（如 `10m`, `1h`） |
| `--at` | 一次性執行（ISO 時間或 `+duration`） |
| `--agent` | 使用的 agent |
| `--session isolated` | 在隔離 session 執行 |
| `--announce` | 執行後通知 |
| `--light-context` | 輕量級啟動上下文 |
| `--delete-after-run` | 一次性 job 成功後刪除 |

### 進階用法

```bash
# 輕量級 morning brief
openclaw cron add \
  --name "lightweight-morning" \
  --cron "0 7 * * *" \
  --session isolated \
  --message "Summarize overnight updates." \
  --light-context \
  --no-deliver

# 編輯 delivery 設定
openclaw cron edit <job-id> \
  --announce --channel telegram --to "123456789"
```

### 重試策略

連續錯誤後使用指數退避重試（30s → 1m → 5m → 15m → 60m），下次成功後恢復正常排程。

---

## 6. LanceDB PRO 完整功能

### 核心架構

```
index.ts (Entry Point)
├── store.ts (LanceDB 儲存層)
├── embedder.ts (嵌入抽象層)
├── retriever.ts (混合檢索引擎)
├── scopes.ts (多作用域訪問控制)
├── tools.ts (Agent API)
├── noise-filter.ts (噪音過濾)
├── adaptive-retrieval.ts (自適應檢索)
├── smart-extractor.ts (LLM 6類別提取)
├── decay-engine.ts (Weibull 衰減模型)
└── tier-manager.ts (三層管理)
```

### 混合檢索

```
Query → embedQuery() ─┐
                       ├─→ Hybrid Fusion → Rerank → Lifecycle Decay → Filter
Query → BM25 FTS ─────┘
```

- **Vector Search** — 透過 LanceDB ANN（cosine distance）的語意相似性
- **BM25 Full-Text Search** — 透過 LanceDB FTS index 的精確關鍵詞匹配
- **Hybrid Fusion** — 向量分數為基礎，BM25 命中獲得加權提升
- **Cross-Encoder Reranking** — Jina/SiliconFlow/Voyage AI/Pinecone

### Smart Extraction（v1.1.0）

LLM 驅動的 6 類別提取：

| 類別 | 說明 |
|------|------|
| `profile` | 身份/背景資料 |
| `preferences` | 偏好設定 |
| `entities` | 實體（人/事/物）|
| `events` | 事件記錄 |
| `cases` | 案例/問題 |
| `patterns` | 模式/規律 |

### 記憶生命週期（v1.1.0）

- **Weibull Decay Engine**: composite score = recency + frequency + intrinsic value
- **三層管理**: `Peripheral ↔ Working ↔ Core`
- **訪問強化**: 頻繁召回的記憶衰減更慢（間隔重複風格）
- **重要性調製半衰期**: 重要的記憶衰減更慢

### 多作用域隔離

內建作用域：`global`, `agent:<id>`, `custom:<name>`, `project:<id>`, `user:<id>`

### 自動捕獲 & 自動召回

- **Auto-Capture**（`agent_end`）: 從對話中提取 preference/fact/decision/entity，每 turn 最多 3 條
- **Auto-Recall**（`before_agent_start`）: 注入 `<relevant-memories>` 上下文（最多 3 條）

### 配置示例

```json
{
  "plugins": {
    "entries": {
      "memory-lancedb-pro": {
        "enabled": true,
        "config": {
          "embedding": {
            "provider": "openai-compatible",
            "apiKey": "${JINA_API_KEY}",
            "model": "jina-embeddings-v5-text-small",
            "baseURL": "https://api.jina.ai/v1",
            "dimensions": 1024
          },
          "autoCapture": true,
          "autoRecall": true,
          "retrieval": {
            "mode": "hybrid",
            "vectorWeight": 0.7,
            "bm25Weight": 0.3,
            "rerank": "cross-encoder",
            "candidatePoolSize": 50,
            "recencyWeight": 0.25
          },
          "smartExtraction": true,
          "extractMinMessages": 2,
          "extractMaxChars": 8000
        }
      }
    }
  }
}
```

### CLI 命令

```bash
openclaw memory-pro list [--scope global] [--category fact] [--limit 20]
openclaw memory-pro search "query" [--scope global] [--limit 10]
openclaw memory-pro stats
openclaw memory-pro delete <id>
openclaw memory-pro export [--scope global] [--output memories.json]
openclaw memory-pro import memories.json [--scope global]
openclaw memory-pro upgrade [--dry-run]
```

---

## 7. 關鍵配置路徑

### 主要設定檔

| 檔案 | 用途 |
|------|------|
| `~/.openclaw/openclaw.json` | 主配置 |
| `~/.openclaw/agents/<agentId>/sessions/` | Session 儲存 |
| `~/.openclaw/memory/lancedb-pro/` | LanceDB PRO 資料庫 |
| `~/.openclaw/credentials/` | 認證凭據 |

### agents.defaults.model

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "minimax-portal/MiniMax-M2.7",
        "fallbacks": ["minimax-portal/MiniMax-M2.1"]
      }
    }
  }
}
```

### 當前配置（2026-03-25）

| 項目 | 值 |
|------|-----|
| 主模型 | `minimax-portal/MiniMax-M2.7` |
| Fallback | `minimax-portal/MiniMax-M2.1` |
| Memory backend | LanceDB PRO |
| Memory scopes | global, agent:main, agent:coder, agent:trader, agent:system-admin |
| 嵌入 | Jina v5-text-small (1024 dimensions) |
| 檢索模式 | hybrid (vector 70% + BM25 30%) |

---

## 8. 常見工作流

### 添加新 Agent

```bash
openclaw agents add <agent-name>
# 設定 workspace、SOUL.md、AGENTS.md
# 設定 bindings 路由
openclaw gateway restart
```

### 設定 Cron 監控

```bash
# 添加每日 GitHub Monitor
openclaw cron add \
  --name "github-monitor" \
  --cron "0 9 * * *" \
  --agent main \
  --session isolated \
  --message "執行 GitHub 監控腳本..." \
  --announce \
  --channel telegram \
  --to 1073451144
```

### 更新 OpenClaw

```bash
# 預覽更新
openclaw update --dry-run

# 執行更新
openclaw update --yes

# 更新完成後自動重啟
```

### 管理 Secrets

```bash
# 審計當前狀態
openclaw secrets audit --check

# 互動式設定
openclaw secrets configure

# 重新載入
openclaw secrets reload
```

---

## 9. 故障排除

| 問題 | 解決方案 |
|------|----------|
| JSON 格式錯誤 | `cat ~/.openclaw/openclaw.json \| python3 -m json.tool > /dev/null` |
| Memory plugin 不工作 | 檢查 `plugins.slots.memory` 設定 |
| Gateway 無法啟動 | `openclaw doctor` 診斷 |
| 認證問題 | `openclaw secrets audit --check` |
| Cron 不執行 | `openclaw cron runs <job-id>` 查看日誌 |

---

## 10. 重要連結

- 文檔：`/opt/homebrew/lib/node_modules/openclaw/docs/`
- 線上文檔：https://docs.openclaw.ai
- GitHub：https://github.com/openclaw/openclaw
- ClawHub：https://clawhub.com

---

*本文件由小助理自動生成，用於系統性理解 OpenClaw 架構和功能*
