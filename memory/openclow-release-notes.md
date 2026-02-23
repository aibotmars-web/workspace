# OpenClaw Release Notes 摘要

## 版本：2026.2.21 (2026-02-21)

### 新功能
- Gemini 3.1 支持
- Telegram/Discord 串流預覽模式
- Discord 語音頻道支援
- iOS Watch 伴侶應用
- 裝置配對管理

### 安全更新
- 防止 prompt injection 攻擊
- Webhook 路徑安全強化
- 檔案上傳路徑檢查
- ACP 安全加固

### 記憶系統
- Voyage AI 向量搜尋支援
- 支援 qmd 本地搜尋
- session-memory 在 /new 和 /reset 時觸發

---

## 重要設定

### 啟用 Voyage AI
```json
"models": {
  "providers": {
    "voyage": {
      "apiKey": "your-key"
    }
  }
},
"memorySearch": {
  "provider": "voyage"
}
```

### 啟用 qmd
```json
"memory": {
  "backend": "qmd"
}
```

---

## 常見問題

### 當機處理
- 執行 `openclaw doctor` 診斷
- 執行 `openclaw gateway restart`
- 檢查日誌：`tail ~/.openclaw/logs/gateway.log`

---

*更新：2026-02-23*
