# OpenClaw GitHub Update - 2026-05-19

## Latest Release: v2026.5.18

### ⚠️ 版本落後
- 目前系統版本: v2026.5.7
- 最新版本: v2026.5.18
- **落後 11 個版本**，建議更新

### 主要新功能
1. **Mac app 大改版** - Settings 頁面重新設計，統一的卡片佈局、更乾淨的許可/語音/skills/cron/exec/debug 分頁
2. **新 Skills** - meme-maker skill、Python pdb 除錯 skill、node inspector 技能
3. **CLI 新插件工具** - `defineToolPlugin` + `openclaw plugins build/validate/init` 命令
4. **Browser** - 快照中顯示待處理對話框，可回答 `browser dialog --dialog-id`
5. **Android** - Talk Mode 改用 realtime Gateway relay 語音 session
6. **Gateway 效能** - 重啟準備延遲大幅降低

### 重要修復
- Telegram: 論壇主題交付、HTTP 421 Misdirected Request 處理、隔離長輪詢穩定性
- Codex app-server: 多個修復包括 native code mode、thread 清理、OAuth 狀態
- GitHub Copilot: 修復 `invalid_request_body` 錯誤
- Mac app: SwiftUI Settings 崩潰問題修復
- 圖片處理: Sharp 安裝失敗時有完整 fallback 方案
- 記憶系統: sqlite-vec 與 semantic vector 區分修復
- 非常多 QA-Lab 測試改進

### 修補數量
- Changes: ~20 項新功能
- Fixes: ~100+ 項修復

*Generated: 2026-05-19 09:02*
