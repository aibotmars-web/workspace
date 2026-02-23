# BD 任務管理系統指南

所有 Sub-Agents 必須使用 BD 追蹤任務。

## 常用命令

```bash
# 列出所有任務
bd list

# 查看待辦任務
bd ready

# 建立新任務
bd create "任務名稱" -d "描述" -p 優先級

# 更新任務狀態
bd update <id> --status in_progress
bd update <id> --status done
bd update <id> --status blocked

# 查看任務詳情
bd show <id>

# 關閉任務
bd close <id>
```

## 狀態說明

| 狀態 | 說明 |
|------|------|
| `todo` | 待處理 |
| `in_progress` | 進行中 |
| `blocked` | 被阻塞 |
| `done` | 已完成 |

## 優先級

| 等級 | 說明 |
|------|------|
| P0 | 緊急/重要 |
| P1 | 高優先 |
| P2 | 中優先 |
| P3 | 低優先 |

## 工作流程

1. **收到任務** → 用 `bd create` 建立
2. **開始執行** → 用 `bd update --status in_progress`
3. **完成** → 用 `bd update --status done`
4. **關閉** → 用 `bd close <id>`

---

*所有任務必須透過 BD 追蹤！*
