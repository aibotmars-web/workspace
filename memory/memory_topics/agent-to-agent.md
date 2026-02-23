# Agent 與 Agent 溝通 (Agent-to-Agent)

## 現有 Agents

| Agent | Chat ID | 功能 |
|-------|---------|------|
| main | Telegram | 小助理 |
| planner | -5002017265 | 項目規劃 |
| assistant | -5111933995 | 生活小秘 |
| coder | -5205007678 | 程式開發 |
| crawler | -5277218620 | 資料收集 |
| image | -5267145726 | 圖像生成 |
| assistant-work | -5107483605 | 內容運營 |
| system-admin | -5268796547 | 系統管理 |
| trader | -5168109367 | 交易監控 |

## 溝通原則

### Planner 溝通
- 每小時檢查進度一次
- 只回報給 Planner，不要一直敲老闆
- 老闆沒回時不要再次敲
- 超過24小時沒回覆再敲

### Session 管理
- 使用 `sessions_send` 跨 Agent 發訊息
- 使用 `sessions_spawn` 創建子任務
- 使用 `subagents` 管理子 Agent 生命週期

## 訊息傳遞

```
主 Agent → sessions_send → 子 Agent
         ↓
    子 Agent 完成後回傳結果
```

---

*更新：2026-02-23*
