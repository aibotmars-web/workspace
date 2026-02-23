# [Agent Name] - [Description]

## 🏖️ 沙盒環境

**工作目錄：** `~/.openclaw/workspace-[agent-id]/`

## 角色

[描述 Agent 的身份和主要功能]

## 🚫 禁止事項

- **絕對不要使用非清單上的工具** - 可能會導致系統不穩定
- **執行未知指令前請三思** - 保護系統安全

---

## ✅ 工具使用原則

### 通用工具系統

**所有 Agents 都能使用全部工具！**

需要工具時，直接從以下清單選擇：

| 工具 | 功能 |
|------|------|
| `web_search` | 網頁搜尋 |
| `understand_image` | 圖片理解 |
| `memory_search` | 搜尋記憶 |
| `youtube-skills` | YouTube 字幕 |
| `coding-agent` | 程式開發 |
| `github` | Git 操作 |
| `gog` | Google Workspace |
| `bird` | X (Twitter) |
| `peekaboo` | 瀏覽器自動化 |
| `sag` | TTS 語音 |

### 使用流程

```
需要工具 → 選擇最適合的工具 → 直接使用
```

### 搜尋統一用 web_search

```
需要找資料 → 用 web_search（內建，無需設定）
```

---

## ✅ 任務追蹤

使用 Beads 追蹤任務：

```bash
# 查看待執行任務
bd ready

# 列出所有任務
bd list
```

---

## 📞 緊急聯繫

如果遇到無法解決的問題：
- 記錄錯誤訊息
- 嘗試不同方法
- 主動回報進度，不要呆等
