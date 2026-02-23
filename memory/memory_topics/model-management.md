# 模型管理 (Model Management)

## 當前配置

| 模型 | 用途 | 設定 |
|------|------|------|
| MiniMax M2.5 | 主要對話 | reasoning: true |
| MiniMax M2.1 | 備用/快速回覆 | reasoning: false |

## API 提供者

- **MiniMax Portal** (主要)
  - API Key: oauth (自動)
  - baseUrl: https://api.minimaxi.com/anthropic

- **Voyage AI** (向量搜尋)
  - API Key: pa-Sewb5EElV2UtKRqJnQnA3z06LbzyNy_ZYtwPq_69Tgl
  - 用於記憶語意搜尋

## qmd 使用方式（2026-02-24 新增）

```bash
# 全文搜尋
qmd search "關鍵詞"

# 讀取檔案
qmd get qmd://memory/2026-02-23.md

# 查看狀態
qmd status

# 更新索引
qmd update
```

## 模型選擇原則

1. **複雜問題** → M2.5 (有 reasoning)
2. **簡單回覆** → M2.1 (快速)
3. **程式開發** → M2.5
4. **翻譯/摘要** → M2.1

## 常見問題

- **當機問題**: tool id not found
- **解決**: 用 `/new` 重置對話

## Token 節省技巧

- 使用 session 而非每次新建
- 配置多個 Agent 各自負責不同任務
- 設定 compactThreshold 控制自動濃縮時機

---

*更新：2026-02-24*
